"""Stale records: a doc, deal or issue that still states a plan newer messages
have changed.

This is record-centric on purpose. Grouping every message into decision topics
and then asking which records disagree with the winner needs the grouping to be
right first, and a slack line like 'Jordan says they cannot close before May 15,
updating the plan' shares no words with the Notion page it updates. Going the
other way is easier: for each record, find the newer items about the same thing
and ask the model one narrow question, is this record now out of date.

  find     newer items close in meaning or sharing a specific person or company
  filter   at least one of them has to read like a change of plan, and has to
           carry a concrete value the record lacks (a different date, price or
           number) or a status change ('accepted another offer', 'on hold')
  ask      the model only confirms the newer item is about the same thing

The filter does the real work. A 3B model asked 'is this record outdated' says
yes to nearly everything, so it flagged 60 routine issues. Asked 'is this about
the same subject' it is useful, and the concrete-value test, which is plain
code, decides whether the two disagree
"""
import re

from . import llm
from .extract import SPECIFIC_DF, _cosine

RECORD_KINDS = ('doc', 'deal', 'issue')
RELATED_COSINE = 0.64        # a newer item this close to the record may be about it
ENTITY_COSINE = 0.58         # lower bar when they share a specific person or company
CHANGE_LIKE = 0.68           # gate score of a newer item that reads like a change
MAX_NEWER = 4                # items shown to the model per record
MIN_GAP_HOURS = 1            # newer means at least this much later, not the same edit
NEWER_KINDS = ('email', 'message', 'doc', 'note', 'issue')

SCHEMA = {'type': 'object',
          'properties': {'same_subject': {'type': 'boolean'}, 'newer_item': {'type': 'integer'},
                         'current_fact': {'type': 'string'}},
          'required': ['same_subject', 'newer_item', 'current_fact']}
SYSTEM = (
    'You match a RECORD to NEWER items. Reply with JSON only.\n'
    'same_subject = true when one NEWER item is about the same specific thing the record is '
    'about (the same plan, deal, price, date, hire or issue). false when they only share a '
    'general topic or a person.\n'
    'newer_item: the number of that item, or 0.\n'
    'current_fact: what that item says about the thing, in under 12 words, copied from it, '
    'or an empty string.')

MONEY_RE = re.compile(r'\$\s?\d[\d,.]*\s?[kKmM]?\b')
DATE_RE = re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}\b', re.I)
ISO_RE = re.compile(r'\b(\d{4})-(\d{2})-(\d{2})\b')
MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
# a status change with no number in it. 'accepted another offer' makes a hiring
# page stale though neither says a date
STATUS_CHANGE_RE = re.compile(
    r'accepted another offer|closing the loop|on hold|hold .{0,20}offer|no longer|withdrawn|called off', re.I)


def concrete_values(text):
    """The dates, prices and amounts in a text, normalised so '2026-03-31' and
    'Mar 31' compare equal. Issue ids, PR numbers and invoice numbers are not
    values and never appear here"""
    vals = {re.sub(r'[\s,]', '', m.group(0).lower()) for m in MONEY_RE.finditer(text)}
    for m in DATE_RE.finditer(text):
        month, _, day = m.group(0).lower().replace('.', '').partition(' ')
        vals.add(f'{month[:3]} {int(day.strip())}')
    for y, mo, d in ISO_RE.findall(text):
        vals.add(f'{MONTHS[int(mo) - 1]} {int(d)}')
    return vals


WORD_RE = re.compile(r'[a-z]{4,}')
GENERIC = frozenset('this that with from have will they them their there were been about would could '
                    'should after before still also when what which other into over only than then '
                    'just like some more most very much many make made need needs please thanks '
                    'thank hello team update notes draft heads attendees owner action'.split())
MIN_SHARED_WORDS = 2
# notes of a meeting that happened are history, not a record of current state, so a
# later change does not make them wrong. they were being flagged as stale
HISTORICAL_RE = re.compile(r'meeting notes|notes[: ]|minutes|postmortem|retro(?:spective)?\b', re.I)


def shared_words(a, b):
    return (set(WORD_RE.findall(a.lower())) & set(WORD_RE.findall(b.lower()))) - GENERIC


def disagrees(record_text, newer_text):
    """True when the newer text states a value the record does not, and the
    record states some value of its own, or the newer text is a status change"""
    old, new = concrete_values(record_text), concrete_values(newer_text)
    if old and new and not new <= old:
        return True
    return bool(STATUS_CHANGE_RE.search(newer_text))


def find_stale(items, vectors, scores, entities):
    """vectors must be header-free embeddings of title and body. the ones used for
    retrieval start with 'Email from X on date', which makes unrelated items look alike"""
    from datetime import datetime, timedelta
    by_id = {i['id']: i for i in items}
    live = [i for i in items if i['state'] == 'current']
    records = [i for i in live if i['kind'] in RECORD_KINDS and not HISTORICAL_RE.search(i['title'])]
    out = []
    for rec in records:
        floor = datetime.fromisoformat(rec['ts'].replace('Z', '+00:00')) + timedelta(hours=MIN_GAP_HOURS)
        related = []
        for new in live:
            if new['kind'] not in NEWER_KINDS or new['id'] == rec['id'] or new['thread_key'] == rec['thread_key']:
                continue
            if datetime.fromisoformat(new['ts'].replace('Z', '+00:00')) < floor:
                continue
            cos = _cosine(vectors[rec['id']], vectors[new['id']])
            shared = entities.get(rec['id'], set()) & entities.get(new['id'], set())
            # close in meaning, or sharing a specific person or company, and in
            # both cases sharing at least two plain words. the words test keeps a
            # meeting-notes doc from being matched to a customer email by tone
            if (cos >= RELATED_COSINE or (shared and cos >= ENTITY_COSINE)) and \
                    (shared or len(shared_words(f"{rec['title']} {rec['body']}", f"{new['title']} {new['body']}")) >= MIN_SHARED_WORDS):
                related.append((cos, new))
        related = [(c, n) for c, n in related if scores.get(n['id'], 0) >= CHANGE_LIKE
                   and disagrees(f"{rec['title']}. {rec['body']}", f"{n['title']}. {n['body']}")]
        if not related:
            continue
        related = sorted(related, key=lambda t: -t[0])[:MAX_NEWER]
        newer = [n for _, n in related]
        numbered = '\n'.join(f"[{k}] ({n['ts'][:10]}) {n['title']}. {n['body'][:200]}" for k, n in enumerate(newer, 1))
        prompt = (f"RECORD ({rec['kind']}, last edited {rec['ts'][:10]}): {rec['title']}. {rec['body'][:300]}\n"
                  f'NEWER items:\n{numbered}')
        result = llm.chat(SYSTEM, prompt, schema=SCHEMA, cache=True, max_tokens=60, role='extract')
        parsed = llm.parse_json(result['text'], None)
        # the model picks which newer item shows the change. we do not let it veto:
        # the filters above already require a conflicting value, and a 3B model
        # answering 'same subject' false dropped a real stale plan
        k = (parsed or {}).get('newer_item', 0)
        if not 1 <= k <= len(newer):
            k = 1     # the closest item by similarity
        out.append({'item_id': rec['id'], 'newer_id': newer[k - 1]['id'],
                    'current_fact': _fact_sentence(newer[k - 1], rec, parsed.get('current_fact', '')),
                    'why': f"newer {newer[k - 1]['source']} item from {newer[k - 1]['ts'][:10]} changes this"})
    return out


def _fact_sentence(newer, rec, said):
    """What the newer item says that the record does not: the model's phrase if it
    is a copy, else the sentence holding the value the record lacks"""
    text = f"{newer['title']}. {newer['body']}"
    said = said.strip()
    if said and re.sub(r'\W+', ' ', said.lower()) in re.sub(r'\W+', ' ', text.lower()):
        return said
    missing = concrete_values(text) - concrete_values(f"{rec['title']}. {rec['body']}")
    for sentence in re.split(r'(?<=[.!?])\s+|\n', newer['body']):
        if missing & concrete_values(sentence):
            return sentence.strip()[:140]
    return newer['body'].split('\n')[0][:140]


def write_stale(conn, rows):
    for r in rows:
        conn.execute('INSERT OR REPLACE INTO stale_records VALUES (?,?,?,?)',
                     (r['item_id'], r['newer_id'], r['current_fact'], r['why']))
