"""A search glossary built from the mailbox itself, in place of a hand-written synonym list.

A one-word question ('sso', 'investors', 'billing') gives a text search almost nothing, and the
words a mailbox uses for a thing ('okta', 'login', 'term sheet') depend on the company. Writing
them into the source ties the code to one company. Asking an embedding model for the nearest
words does not work either: single words embed badly ('sso' lands nearest 'https' and 'security'
and 'runway' nearest 'routine'). So the work is split:

  candidates   code gathers, for each word the inbox uses, the words nearest to it in embedding
               space and the words that appear in the same items. Both lists are noisy and both
               come from this inbox, so every candidate is a word that can match something
  choose       the model reads one word and its candidates and lists up to six words that an
               email about the same thing would use: candidates that fit, and common words it
               knows that the candidates missed (single sign-on is also login and okta). Code keeps
               only words the inbox contains, so a guess that matches nothing costs nothing

The result is stored as data (the glossary table) and rebuilt at ingest, so a new company, a new
product name or a new nickname for a project is picked up on the next run with no code change
"""
import json
import re

import numpy as np

from . import config, llm

MIN_DF = 3                # a word in fewer items than this has no pattern to learn
MAX_DF = 150              # one in more says nothing about a topic
MAX_TERMS = 400           # words that get an entry, most used first
POOL_EMBED = 12           # embedding neighbours offered to the model per word
POOL_COOCCUR = 12         # co-occurring words offered per word
KEEP = 6
MAX_RELATED_DF = 40       # a related word in more items than this blurs a search instead of focusing it
BATCH = 10
MEMO_OVERLAP = 0.7        # a remembered entry is reused while this much of its candidate list is unchanged
SIM_DIGITS = 3            # similarities are rounded before ranking, so embedding noise cannot reorder near-ties

SCHEMA = {'type': 'object',
          'properties': {'entries': {'type': 'array', 'items': {
              'type': 'object',
              'properties': {'term': {'type': 'string'}, 'related': {'type': 'array', 'items': {'type': 'string'}}},
              'required': ['term', 'related']}}},
          'required': ['entries']}
SYSTEM = (
    'You build a search glossary for one mailbox. Reply with JSON only.\n'
    'For each TERM you get CANDIDATES, words that appear near it in this mailbox. List up to 6 other '
    'words that an email or message about the same thing would also use: synonyms, the tools, vendors or '
    'products involved, the kinds of people involved, close variants. Prefer candidates that fit. Add a '
    'common word you know when the candidates miss the point (for example an invoice also involves billing, '
    'payment and receipt). One lowercase word each. List none when the term is a general word with no '
    'particular topic.')


def _words(text):
    return set(re.findall(r'[a-z]{3,}', text.lower()))


def candidates(items, vocab, stop):
    """term -> candidate words, from embeddings and from co-occurrence"""
    # ties on the count break by word. the counts come out of a set, whose order changes between runs, and the
    # cut at MAX_TERMS fell on a different word each time
    terms = [w for w, n in sorted(vocab.items(), key=lambda kv: (-kv[1], kv[0]))
             if MIN_DF <= n <= MAX_DF and len(w) >= 3 and w not in stop][:MAX_TERMS]
    usable = {w for w, n in vocab.items() if 2 <= n <= MAX_DF * 2 and len(w) >= 3 and w not in stop}
    index = {}
    for item in items:
        if item['state'] != 'current':
            continue
        for word in _words(f"{item['title']} {item['body']}") & usable:
            index.setdefault(word, set()).add(item['id'])
    pool = sorted(usable)
    vectors = np.array(llm.embed(pool, kind='query'), dtype=np.float32)
    vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)
    where = {w: n for n, w in enumerate(pool)}
    out = {}
    for term in terms:
        if term not in where:
            continue
        # a stable sort on rounded scores: the embedder's last-digit noise reordered near-ties between two
        # ingests of the same data, which changed the candidate list and so the prompt
        near = np.argsort(-np.round(vectors @ vectors[where[term]], SIM_DIGITS), kind='stable')
        by_embedding = [pool[i] for i in near if pool[i] != term][:POOL_EMBED]
        mine = index.get(term, set())
        together = sorted(((len(mine & ids) / len(mine | ids), w) for w, ids in index.items() if w != term and mine & ids),
                          reverse=True)
        by_items = [w for _, w in together[:POOL_COOCCUR]]
        out[term] = list(dict.fromkeys(by_embedding + by_items))
    return out


def _memo_path():
    return config.STATE_DIR / 'glossary_memo.json'


def _load_memo():
    try:
        return json.loads(_memo_path().read_text())
    except (OSError, ValueError):
        return {}       # no memo yet, or one that does not parse: every term is asked again


def _save_memo(memo):
    try:
        config.STATE_DIR.mkdir(parents=True, exist_ok=True)
        _memo_path().write_text(json.dumps(memo))
    except OSError:
        pass            # the memo only saves calls


def _unchanged(old, new):
    old, new = set(old), set(new)
    return bool(old | new) and len(old & new) / len(old | new) >= MEMO_OVERLAP


def choose(pool, vocab):
    """term -> related words the model gave that the inbox contains. The model's answer for a word is
    remembered by word, next to its candidate list. The prompt cache keys on the whole batch, so one word
    whose candidates moved re-asked its nine neighbours: 33 of 35 batches missed on unchanged data. A
    remembered word is asked again only when its candidates changed by more than MEMO_OVERLAP allows, which
    is how a daily ingest pays for the words new mail touched and for nothing else"""
    memo = _load_memo()
    raw = {t: memo[t]['related'] for t in pool if t in memo and _unchanged(memo[t]['pool'], pool[t])}
    todo = [t for t in pool if t not in raw]
    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        prompt = '\n\n'.join(f"TERM {t}\nCANDIDATES: {', '.join(pool[t])}" for t in batch)
        result = llm.chat(SYSTEM, prompt, schema=SCHEMA, cache=True, max_tokens=800, role='extract')
        parsed = llm.parse_json(result['text'], None) or {}
        for entry in parsed.get('entries', []):
            term = str(entry.get('term', '')).lower()
            if term in batch and term not in raw:
                raw[term] = [str(w).lower().strip() for w in entry.get('related', [])]
        if parsed.get('entries'):
            # a word the model left out of an answer that otherwise parsed has nothing to relate. without an
            # empty entry it was asked again on every ingest
            for term in batch:
                raw.setdefault(term, [])
                memo[term] = {'pool': pool[term], 'related': raw[term]}
        _save_memo(memo)
    glossary = {}
    for term, related in raw.items():
        kept = [w for w in dict.fromkeys(related) if w != term and 1 <= vocab.get(w, 0) <= MAX_RELATED_DF and w.isalpha()][:KEEP]
        if kept:
            glossary[term] = kept
    return glossary


def build(items, vocab, stop):
    return choose(candidates(items, vocab, stop), vocab)


def write(conn, glossary):
    conn.executemany('INSERT OR REPLACE INTO glossary VALUES (?,?)', [(t, ' '.join(w)) for t, w in glossary.items()])
    conn.commit()
