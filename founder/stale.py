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
           number, a relative date such as 'next Friday' resolved against when it
           was written, a different month or quarter) or say, about the same
           thing, that it is delayed, on hold or dropped with no value at all
           ('pushed the timeline back for now'). That last case is the one place
           the model reads a sentence, because similarity to example sentences
           could not tell 'pushed back' from 'on track' (see soft_change)
  ask      the model only confirms the newer item is about the same thing

The filter does the real work. A 3B model asked 'is this record outdated' says
yes to nearly everything, so it flagged 60 routine issues. Asked 'is this about
the same subject' it is useful, and the concrete-value test, which is plain
code, decides whether the two disagree
"""
import calendar
import math
import re
from datetime import datetime, timedelta

from . import dates, llm
from .extract import HEDGE_RE, HINT_RE, NOVELTY_FLOOR, SPECIFIC_DF, _cosine

RECORD_KINDS = ('doc', 'deal', 'issue')
RELATED_COSINE = 0.64        # a newer item this close to the record may be about it
ENTITY_COSINE = 0.58         # lower bar when they share a specific person or company
CHANGE_LIKE = 0.60           # gate score of a newer item that reads like a change. lowered from 0.68 once the typed-value and shared-word tests existed: the gate had been the main brake, and it dropped real updates scoring 0.64
MAX_NEWER = 4                # items shown to the model per record
MIN_GAP_HOURS = 0            # newer means strictly later. it was one hour, to keep the same edit (an email and its slack post) from reading as an update. replaying ingest with 0 on the sample data changed no stale record and no check, and a real correction can land minutes after the page it corrects, so the hour could only cost a miss
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

MONEY_RE = re.compile(r'\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmM]?\b')
DATE_RE = re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}\b', re.I)
ISO_RE = re.compile(r'\b(\d{4})-(\d{2})-(\d{2})\b')
SLASH_RE = re.compile(r'\b(\d{1,2})/(\d{1,2})\b')
PERCENT_RE = re.compile(r'\b(\d+(?:\.\d+)?)\s?(?:%|percent)')
DURATION_RE = re.compile(r'\b(\d+)\s?-?\s?(yrs?|years?|mos?|months?|wks?|weeks?)\b', re.I)
UNIT = {'y': 'year', 'm': 'month', 'w': 'week'}
MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
# a status change with no number in it. 'accepted another offer' makes a hiring
# page stale though neither says a date
STATUS_CHANGE_RE = re.compile(
    r'accepted another offer|closing the loop|on hold|hold .{0,20}offer|no longer|withdrawn|called off', re.I)


WEEKDAYS = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
WEEKDAY_RE = re.compile(r'\b(next|this)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tues?|thu(?:rs?)?|fri)\b', re.I)
IN_RE = re.compile(r'\bin (\d+|a|one|two|three|four|five|six) (day|week)s?\b', re.I)
NUMBER_WORDS = {'a': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
MONTH_ONLY_RE = re.compile(r'\b(?:to|until|till|in|by|during|end of|early|late|mid|beginning of)\s+(?:the\s+)?'
                           r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b(?!\.?\s*\d)', re.I)
QUARTER_RE = re.compile(r'\bq([1-4])\b', re.I)


def relative_phrases(text, base):
    """(phrase, date) for each word like 'tomorrow' or 'next Friday', resolved against when the text was written"""
    low = text.lower()
    out = []
    for m in re.finditer(r'\btomorrow\b|\btmrw\b', low):
        out.append((m.group(0), base + timedelta(days=1)))
    for m in WEEKDAY_RE.finditer(low):
        word = m.group(2)
        target = next(n for n, name in enumerate(WEEKDAYS) if name.startswith(word[:3]))
        if m.group(1) == 'next':
            # the following calendar week, which is what 'next Friday' means whichever day it is said
            out.append((m.group(0).strip(), base - timedelta(days=base.weekday()) + timedelta(days=7 + target)))
        else:
            out.append((m.group(0).strip(), base + timedelta(days=(target - base.weekday()) % 7 or 7)))
    for m in IN_RE.finditer(low):
        n = int(m.group(1)) if m.group(1).isdigit() else NUMBER_WORDS[m.group(1)]
        out.append((m.group(0), base + timedelta(days=n * (7 if m.group(2) == 'week' else 1))))
    for m in re.finditer(r'\bend of (?:the )?month\b|\beom\b', low):
        out.append((m.group(0), base.replace(day=calendar.monthrange(base.year, base.month)[1])))
    for m in re.finditer(r'\bend of (?:the )?week\b|\beow\b', low):
        out.append((m.group(0), base - timedelta(days=base.weekday()) + timedelta(days=4)))
    return out


def relative_dates(text, base):
    """Dates that words like 'tomorrow' and 'next Friday' stand for, resolved against when the text
    was written. Returns day values ('mar 20') and month values ('month apr')"""
    days = {f'{MONTHS[d.month - 1]} {d.day}' for _, d in relative_phrases(text, base)}
    months = {f'month {MONTHS[base.month % 12]}'} if re.search(r'\bnext month\b', text.lower()) else set()
    return days, months


def concrete_values(text, base=None):
    """The dates, prices and amounts in a text, normalised so '2026-03-31' and
    'Mar 31' compare equal. Issue ids, PR numbers and invoice numbers are not
    values and never appear here. With base (when the text was written) words like
    'next Friday' become dates too, and a bare month or quarter ('pushed to April',
    'now Q3') becomes a month or quarter value"""
    vals = {re.sub(r'[\s,]', '', m.group(0).lower()) for m in MONEY_RE.finditer(text)}
    for m in DATE_RE.finditer(text):
        month, _, day = m.group(0).lower().replace('.', '').partition(' ')
        vals.add(f'{month[:3]} {int(day.strip())}')
    for y, mo, d in ISO_RE.findall(text):
        vals.add(f'{MONTHS[int(mo) - 1]} {int(d)}')
    # terms of a deal: '15%' and '2 yr' are values as much as a date is
    vals |= {f'{p}%' for p in PERCENT_RE.findall(text)}
    vals |= {f'{n} {UNIT[u[0].lower()]}' for n, u in DURATION_RE.findall(text)}
    for a, b in SLASH_RE.findall(text):
        found = dates.month_day(int(a), int(b))
        if found:
            vals.add(f'{MONTHS[found[0] - 1]} {found[1]}')
    if base is not None:
        days, months = relative_dates(text, base)
        vals |= days | months
        vals |= {f'month {m.lower()[:3]}' for m in MONTH_ONLY_RE.findall(text)}
        vals |= {f'quarter q{q}' for q in QUARTER_RE.findall(text)}
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


def _typed(values):
    """Group values by what they measure: a date, an amount, a percentage, a duration"""
    out = {}
    for v in values:
        kind = ('percent' if v.endswith('%') else 'money' if v.startswith('$') else
                'month' if v.startswith('month ') else 'quarter' if v.startswith('quarter ') else
                'duration' if v.split()[-1] in ('year', 'month', 'week') else 'date')
        out.setdefault(kind, set()).add(v)
    return out


SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+|\n|;')


def _label_words(text):
    """Words that say what a sentence is about, without its values"""
    return {w for w in WORD_RE.findall(text.lower())} - GENERIC - {'date', 'target', 'expected', 'status'}


def _quarter(month):
    return f'quarter q{MONTHS.index(month) // 3 + 1}'


def typed_values(text, base=None):
    """concrete_values grouped by what they measure. A date also says which month and quarter it falls
    in, so a bare 'moved to April' or 'now Q3' can be compared with a record that says 'Mar 31'"""
    typed = _typed(concrete_values(text, base))
    months = {f"month {d.split()[0]}" for d in typed.get('date', ())} | typed.get('month', set())
    if months:
        typed['month'] = months
        typed.setdefault('quarter', set()).update(_quarter(m.split()[1]) for m in months)
    return typed


def word_weight(word, df):
    """What a shared word is worth: a rare one ('beta', 'timeline') names a plan, a common one does not"""
    return 1.0 / (1.0 + math.log(max(1, df.get(word, 1))))


def conflict_strength(record_text, newer_text, record_title='', newer_title='', record_base=None, newer_base=None, df=None):
    """How strongly the newer text contradicts the record, 0 for not at all. A
    different value of the thing the record states a value of. Three tests, all code:
      1. same kind of value: another date where the record has a date, another
         price where it has a price, another month or quarter. a date in the newer
         text means nothing to a record that has none
      2. the new value sits in a sentence about the same thing: for dates the
         two sentences must share a word ('close' and 'close', 'cutover' and
         'cutover'). an email that says 'reproduce by Mar 13' shares nothing with a
         deal's 'expected close date' and no longer marks it stale
      3. the record's title may supply the shared word, since 'Initech renewal
         terms' and 'initech renewal is 2 yr at 15%' are about the same renewal
         though no sentence of the record repeats a word
    record_base and newer_base are when each text was written. With them 'next Friday' and
    'tomorrow' are dates, which is how a change worded in relative terms is caught.
    A status change with no number ('accepted another offer') also counts, weakly.
    The strength is the number of subject words the new value's sentence shares
    with the record, which ranks the real update above a template email that
    happens to mention the same company. With df (how many items use each word) the words are
    weighted by how rare they are, so the strength is on the same scale as a soft change's overlap"""
    old, new = typed_values(record_text, record_base), typed_values(newer_text, newer_base)
    best = 0.0
    for kind in new:
        if kind not in old or not new[kind] - old[kind]:
            continue
        fresh = new[kind] - old[kind]
        new_labels = set().union(*[_label_words(x) for x in SENTENCE_SPLIT.split(newer_text)
                                   if typed_values(x, newer_base).get(kind, set()) & fresh] or [set()])
        old_labels = set().union(*[_label_words(x) for x in SENTENCE_SPLIT.split(record_text)
                                   if kind in typed_values(x, record_base)] or [set()])
        # the record's own title says what it is about, so its words count on the record
        # side. the newer title does not count: a template email titled 'Initech renewal #45'
        # is about latency, whatever its subject line says
        common = new_labels & (old_labels | _label_words(record_title))
        shared = sum(word_weight(w, df) for w in common) if df is not None else len(common)
        if shared:
            best = max(best, float(shared))
    if best:
        return best
    return STATUS_STRENGTH if STATUS_CHANGE_RE.search(newer_text) else 0.0


SOFT_SCHEMA = {'type': 'object', 'properties': {'changed': {'type': 'boolean'}}, 'required': ['changed']}
SOFT_SYSTEM = (
    'You compare one SENTENCE from a newer message with a RECORD. Reply with JSON only.\n'
    'changed = true when the sentence says that what the record states (a plan, date, deadline, '
    'status or decision) was delayed, moved, put on hold, dropped, reversed or otherwise changed, '
    'even when it gives no new date.\n'
    'changed = false when the sentence asks or suggests, says nothing changed, repeats the record, '
    'only discusses a possible change, or is about a different thing.\n'
    'Examples\n'
    'RECORD: Launch is Apr 3. SENTENCE: We pushed the launch back for now. -> true\n'
    'RECORD: Launch is Apr 3. SENTENCE: The launch is on track. -> false\n'
    'RECORD: Launch is Apr 3. SENTENCE: Should we push the launch? -> false\n'
    'RECORD: Launch is Apr 3. SENTENCE: Standup moved to 3pm. -> false\n'
    'RECORD: Interviews run Mar 9 to Mar 13. SENTENCE: We paused interviews until the budget is approved. -> true')
SOFT_MAX_SENTENCES = 2
SOFT_MAX_ITEMS = 3          # newer items the model reads per record
SOFT_MIN_SHARED = 2         # subject words a sentence must share with the record. one is often incidental
STATUS_STRENGTH = 0.25      # a status change with no value ('accepted another offer'), the weakest evidence there is


def candidate_sentences(record, new):
    """Sentences of a newer item that talk about the record: they share two subject words with it, and are
    not questions or hedges. A change of plan that carries no value is judged one sentence at a time"""
    subject = _label_words(f"{record['title']} {record['body']}")
    out = []
    for sentence in SENTENCE_SPLIT.split(new['body']):
        sentence = sentence.strip()
        if len(sentence.split()) >= 3 and not HEDGE_RE.search(sentence) and len(subject & _label_words(sentence)) >= SOFT_MIN_SHARED:
            out.append(sentence)
    return out[:SOFT_MAX_SENTENCES]


def soft_change(record, new):
    """The sentence of a newer item that says the record's plan was delayed, held or dropped without
    giving a value, or ''. Code picks the sentences (same subject, not a hedge, not meeting notes) and
    the model answers one yes or no per sentence. Similarity to example sentences could not do this:
    'the launch is on track' and 'we are holding off until Q3' scored alike"""
    if HISTORICAL_RE.search(new['title']):
        return ''
    for sentence in candidate_sentences(record, new):
        result = llm.chat(SOFT_SYSTEM, f"RECORD: {record['title']}. {record['body'][:200]}\nSENTENCE: {sentence}",
                          schema=SOFT_SCHEMA, cache=True, max_tokens=60, role='extract')
        if (llm.parse_json(result['text'], None) or {}).get('changed') is True:
            return sentence
    return ''


def disagrees(record_text, newer_text, record_title='', newer_title=''):
    return conflict_strength(record_text, newer_text, record_title, newer_title) > 0


def subject_overlap(record, new, df):
    """How well the best candidate sentence of a newer item matches a record, counting rare shared words for
    more than common ones. 'beta' and 'timeline' name a plan, 'design' appears in every other record"""
    subject = _label_words(f"{record['title']} {record['body']}")
    best = 0.0
    for sentence in candidate_sentences(record, new):
        best = max(best, sum(1.0 / (1.0 + math.log(max(1, df.get(w, 1)))) for w in subject & _label_words(sentence)))
    return best


def find_stale(items, vectors, scores, entities, ident=None):
    """vectors must be header-free embeddings of title and body. the ones used for
    retrieval start with 'Email from X on date', which makes unrelated items look alike"""
    live = [i for i in items if i['state'] == 'current']
    records = [i for i in live if i['kind'] in RECORD_KINDS and not HISTORICAL_RE.search(i['title'])]
    df = {}
    for item in live:
        for word in set(WORD_RE.findall(f"{item['title']} {item['body']}".lower())):
            df[word] = df.get(word, 0) + 1
    prepared, soft_scores = [], {}
    for rec in records:
        floor = datetime.fromisoformat(rec['ts'].replace('Z', '+00:00')) + timedelta(hours=MIN_GAP_HOURS)
        related = []
        for new in live:
            if new['kind'] not in NEWER_KINDS or new['id'] == rec['id'] or new['thread_key'] == rec['thread_key']:
                continue
            if datetime.fromisoformat(new['ts'].replace('Z', '+00:00')) <= floor:
                continue
            # template mail ('Customer escalation #46: we are blocked on review until Mar 02') is nearly identical to
            # other mail and is not an update to anything, whatever date it carries. the same test that keeps it
            # out of decision labelling applies here
            if new.get('novelty', 1.0) < NOVELTY_FLOOR and not HINT_RE.search(new['title'] + ' ' + new['body']):
                continue
            cos = _cosine(vectors[rec['id']], vectors[new['id']])
            shared = entities.get(rec['id'], set()) & entities.get(new['id'], set())
            # close in meaning, or sharing a specific person or company, and in
            # both cases sharing at least two plain words. the words test keeps a
            # meeting-notes doc from being matched to a customer email by tone
            if (cos >= RELATED_COSINE or (shared and cos >= ENTITY_COSINE)) and \
                    (shared or len(shared_words(f"{rec['title']} {rec['body']}", f"{new['title']} {new['body']}")) >= MIN_SHARED_WORDS):
                related.append((cos, new))
        # a deal belongs to a counterparty: an update only counts if it names that company or
        # its contact, by name in the text (entity links are too coarse for a customer every email mentions). without this, one investor's email marked another investor's deal stale
        if rec['kind'] == 'deal' and ident is not None:
            parties = {w for pid in rec['people'] for w in re.findall(r'[a-z]{4,}', f'{ident.people[pid].name} {ident.people[pid].org}'.lower())}
            related = [(c, n) for c, n in related if parties & set(re.findall(r'[a-z]{4,}', f"{n['title']} {n['body']}".lower()))]
        rec_base = datetime.fromisoformat(rec['ts'].replace('Z', '+00:00'))
        strength = {n['id']: conflict_strength(rec['body'], n['body'], rec['title'], n['title'], rec_base,
                                               datetime.fromisoformat(n['ts'].replace('Z', '+00:00')), df) for _, n in related}
        # a plan can slip without a new date only if it had a time to slip from
        timed = set(typed_values(rec['body'], rec_base)) & {'date', 'month', 'quarter', 'duration'}
        eligible = [t for t in related if scores.get(t[1]['id'], 0) >= CHANGE_LIKE and strength[t[1]['id']] <= STATUS_STRENGTH] if timed else []
        for _, n in eligible:
            soft_scores[(rec['id'], n['id'])] = subject_overlap(rec, n, df)
        prepared.append((rec, related, strength, eligible))
    # one sentence updates the record it is about, not every record that shares a word with it
    best = {}
    for (_, new_id), score in soft_scores.items():
        best[new_id] = max(best.get(new_id, 0.0), score)
    out = []
    for rec, related, strength, eligible in prepared:
        said = {}
        about = sorted((t for t in eligible if soft_scores[(rec['id'], t[1]['id'])] > 0
                        and soft_scores[(rec['id'], t[1]['id'])] >= best[t[1]['id']] - 1e-9), key=lambda t: -t[0])[:SOFT_MAX_ITEMS]
        for _, n in about:
            # no contradicting value: perhaps it says the plan slipped, without saying to when
            said[n['id']] = soft_change(rec, n)
            if said[n['id']]:
                # on the scale typed conflicts use, so a message that shares the record's rare words
                # outranks a page that shares one ordinary word with it and carries a date
                strength[n['id']] = soft_scores[(rec['id'], n['id'])]
        related = [(c, n) for c, n in related if scores.get(n['id'], 0) >= CHANGE_LIKE and strength[n['id']] > 0]
        if not related:
            continue
        # strongest contradiction first. among equals the newest wins: when two later items both
        # change a date, the older of them is no longer the current word. then closest in meaning
        related = sorted(related, key=lambda t: (-strength[t[1]['id']], _neg_ts(t[1]['ts']), -t[0]))[:MAX_NEWER]
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
        # the model picks which newer item shows the change, but not a weaker one than the
        # best contradiction (a 3b model picked a template email over the real update) and not an
        # older one than the newest of equal strength (it picked the earlier of two date changes)
        if not 1 <= k <= len(newer) or strength[newer[k - 1]['id']] < strength[newer[0]['id']] \
                or newer[k - 1]['ts'] < newer[0]['ts']:
            k = 1
        out.append({'item_id': rec['id'], 'newer_id': newer[k - 1]['id'],
                    'current_fact': _fact_sentence(newer[k - 1], rec, (parsed or {}).get('current_fact', ''), said.get(newer[k - 1]['id'], '')),
                    'why': f"newer {newer[k - 1]['source']} item from {newer[k - 1]['ts'][:10]} changes this"})
    return out


def _neg_ts(ts):
    """A sort key that puts later timestamps first"""
    return -datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()


def _fact_sentence(newer, rec, said, soft=''):
    """What the newer item says that the record does not: the model's phrase if it
    is a copy, else the sentence holding the value the record lacks"""
    text = f"{newer['title']}. {newer['body']}"
    said = said.strip()
    if said and re.sub(r'\W+', ' ', said.lower()) in re.sub(r'\W+', ' ', text.lower()):
        return said
    base = datetime.fromisoformat(newer['ts'].replace('Z', '+00:00'))
    missing = concrete_values(text, base) - concrete_values(f"{rec['title']}. {rec['body']}")
    for sentence in re.split(r'(?<=[.!?])\s+|\n', newer['body']):
        if missing & concrete_values(sentence, base):
            return sentence.strip()[:140]
    return (soft or newer['body'].split('\n')[0])[:140]


def write_stale(conn, rows):
    for r in rows:
        conn.execute('INSERT OR REPLACE INTO stale_records VALUES (?,?,?,?)',
                     (r['item_id'], r['newer_id'], r['current_fact'], r['why']))
