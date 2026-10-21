"""Ingest pipeline: raw exports -> identity -> normalise -> dedupe -> topics ->
decisions -> sqlite + chroma. Run as `founder ingest`"""
import subprocess
import sys
import time

import numpy as np

from . import config, dates, dedupe, extract, followups, glossary, llm, retrieve, route, stale, store
from .identity import IdentityResolver, format_report, resolution_report
from .normalize import normalize_all


def ensure_raw_data():
    """data/ is gitignored (it is a symlink on the dev rig), so a fresh clone
    regenerates it from the seeded script"""
    if (config.RAW_DIR / 'gmail_messages.jsonl').exists():
        return
    print('raw data missing, running synthetic_data_generator.py')
    subprocess.run([sys.executable, 'synthetic_data_generator.py'], cwd=config.ROOT, check=True)


def embed_text(item, ident):
    """What we embed: a readable line with who and when, then the content.
    Names in the text are what let 'what did Daniel say' find his email even
    when it was sent from a personal address"""
    author = ident.name(item['author']) if item['author'] else 'unknown sender'
    day = item['ts'][:10]
    head = {'email': f"Email from {author} on {day}, subject: {item['title']}",
            'event': f"Calendar event ({item['status']}) {item['title']} on {day}",
            'message': f"Slack {item['title']} message from {author} on {day}",
            'issue': f"Linear issue {item['meta'].get('identifier', '')} ({item['status']}) "
                     f"assigned to {author}, {item['title']}",
            'pr': f"GitHub pull request ({item['status']}) by {author}, {item['title']}",
            'comment': f"GitHub comment from {author} on {item['title']}",
            'doc': f"Notion page edited {day} by {author}, {item['title']}",
            'deal': f"CRM deal ({item['status']}), {item['title']}",
            'note': f"CRM note on {day}, {item['title']}"}[item['kind']]
    text = f"{head}\n{item['body']}"
    if 'forwarded' in item['flags']:
        # the forwarded message is what the email is about. it is embedded with the note, and stays out of the body
        text += f"\nForwarded message: {item['quoted'][:800]}"
    return text.strip()


def novelty_scores(items, plain):
    """How unlike the rest of the corpus each item is: one minus its mean
    similarity to its three nearest neighbours in other conversations. Template
    mail ('Quick update on this, X owns the next step') has near-identical
    neighbours and scores close to zero. a bespoke message about a deal has none.
    It decides which of a person's fifty messages are worth a line when someone asks
    what they have been saying"""
    ids = [i['id'] for i in items]
    matrix = np.array([plain[i] for i in ids], dtype=np.float32)
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-9)
    sims = matrix @ matrix.T
    threads = np.array([i['thread_key'] for i in items])
    out = {}
    for n, item in enumerate(items):
        row = np.where(threads == item['thread_key'], -1.0, sims[n])
        out[item['id']] = float(1.0 - np.sort(row)[-3:].mean())
    return out


def run(skip_decisions=False):
    started = time.time()
    ensure_raw_data()
    ident = IdentityResolver(config.RAW_DIR, embed=llm.embed)
    items = normalize_all(config.RAW_DIR, ident)
    print(f'{ident.learn_nicknames(items)} nicknames learned from the mail')
    print(f'{ident.link_mentions(items)} items mention a person by first name')
    for line in format_report(resolution_report(items)):
        print(line)
    order = dates.detect_slash_order(f"{i['title']} {i['body']}" for i in items)
    dates.set_slash_order(order)
    for item in items:
        item['embed_text'] = embed_text(item, ident)
        # machine mail and bot posts are indexed but not 'current': they repeat
        # what the real sources say and would crowd out the people in retrieval
        item['state'] = ('quarantined' if 'after_now' in item['flags']
                         else 'automated' if {'automated', 'bot'} & set(item['flags']) else 'current')
        item.update(superseded_by=None, dup_group=None, topic=None)

    print(f'embedding {len(items)} items with {config.EMBED_MODEL}')
    vectors = dict(zip((i['id'] for i in items), llm.embed([i['embed_text'] for i in items])))

    dedupe.collapse_linear_snapshots(items)
    dupe_pairs = dedupe.find_cross_source_dupes(items, vectors) + dedupe.find_duplicate_events(items)
    by_id = {i['id']: i for i in items}
    for first, second in dupe_pairs:
        # the earlier post is canonical. both stay searchable and citable
        group = by_id[first]['dup_group'] or first
        by_id[first]['dup_group'] = by_id[second]['dup_group'] = group

    topics, links = dedupe.build_topics(items, dupe_pairs)
    for topic_id, members in topics.items():
        for member in members:
            by_id[member]['topic'] = topic_id

    # header-free vectors for comparing items with each other. the retrieval
    # vectors start with 'Email from X on date', which dominates short texts
    plain = dict(zip((i['id'] for i in items),
                     llm.embed([f"{i['title']}. {i['body']}"[:600] for i in items], kind='query')))
    for item_id, value in novelty_scores(items, plain).items():
        by_id[item_id]['novelty'] = value
    decisions, stale_rows, follow_rows = [], [], []
    pool = extract.scoring_pool(items)
    scores = extract.gate_scores(pool, vectors)
    for item_id, value in scores.items():
        by_id[item_id]['gate'] = value
    if not skip_decisions:
        entities = extract.entity_map(items, ident)
        decisions = extract.extract_decisions(items, topics, ident, vectors, scores, entities, plain, resolve_now=False)
        stale_rows = stale.find_stale(items, plain, scores, entities, ident)
        # a stale record is evidence of a change of plan, so it feeds back into the decision history
        decisions = extract.merge_stale(decisions, stale_rows, items)
        extract.resolve(decisions)
        extract.mark_stale(decisions, stale_rows)
        stale_rows = stale_rows + extract.retraction_rows(decisions, stale_rows)
        print(f'{len(stale_rows)} records still state an outdated plan')
        follow_rows = followups.find_followups(items, ident)
        print(f'{len(follow_rows)} follow-ups ({sum(r["status"] == "open" for r in follow_rows)} open)')

    conn = store.reset()
    store.write_items(conn, items, ident.people)
    conn.execute("INSERT OR REPLACE INTO settings VALUES ('slash_order', ?)", (order,))
    vocab = {r['term']: r['doc'] for r in conn.execute('SELECT term, doc FROM vocab ORDER BY term')}
    terms = glossary.build(items, vocab, retrieve.STOP | route.FILLER)
    glossary.write(conn, terms)
    print(f'{len(terms)} words have related words in the search glossary')
    conn.executemany('INSERT INTO links VALUES (?,?,?)', links)
    extract.write_decisions(conn, decisions)
    stale.write_stale(conn, stale_rows)
    followups.write_followups(conn, follow_rows)
    conn.commit()
    store.write_vectors(store.reset_vectors(), items, vectors)

    print(f'{len(items)} items, {len(dupe_pairs)} cross-source dupes, '
          f'{sum(len(m) > 1 for m in topics.values())} multi-item topics, '
          f'{len(decisions)} decision events, {time.time() - started:.1f}s')
    return {'items': items, 'dupe_pairs': dupe_pairs, 'topics': topics, 'decisions': decisions}
