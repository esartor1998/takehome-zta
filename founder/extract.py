"""Decision extraction at ingest, and deterministic resolution of conflicts.

The llama 3B model reads each candidate item once and labels it. We do not let
it decide what is current. That is plain code over the labels, because a small
model asked 'which of these is the latest decision' gets it wrong often enough
to matter, and because code is testable.

  1. gate        a cheap regex picks items that sound like decisions, plus all
                 snapshots of any linear issue those items point at
  2. label       the model returns kind, value and the value it retracts
  3. validate    values must be copied from the text, rules override the kind
                 when the wording is unambiguous ('reverting', 'corrected')
  4. resolve     per topic: latest decision-bearing event is current, anything
                 whose value was explicitly retracted is stale even if newer
"""
import json
import re

from . import llm
from .normalize import ACME_RE

# deliberately narrow. 'ship', 'now' and plain 'moved' appear in filler and
# would send hundreds of items to the model for nothing
HINT_RE = re.compile(
    r'\b(decision|decided|reversing|reverting|reopening|new plan|correction|corrected|'
    r'confirmed:|rescheduled|moving .{0,40} from|\(was )', re.I)

DECISION_KINDS = ('decision', 'reversal', 'correction')

SCHEMA = {
    'type': 'object',
    'properties': {
        'kind': {'type': 'string',
                 'enum': ['decision', 'reversal', 'correction', 'restatement', 'none']},
        'value': {'type': 'string'},
        'retracts': {'type': 'string'},
    },
    'required': ['kind', 'value', 'retracts'],
}

SYSTEM = (
    'You label one work message or record. Reply with JSON only.\n'
    'kind: decision = a new choice was made. reversal = an earlier choice is undone '
    'or changed. correction = a wrong fact or date in an earlier message is fixed. '
    'restatement = repeats a choice with no change. none = no decision.\n'
    'value: the choice or fact, copied from the text, under 12 words.\n'
    'retracts: the old value this replaces, copied from the text, or an empty string.')

RETRACT_PATTERNS = (
    re.compile(r'corrected from ([^)\n.]+)', re.I),
    re.compile(r',? not ([A-Z][a-z]{2} \d+|[^.\n]+?)(?:[.\n]|$)', re.I),
    re.compile(r'\(was ([^)]+)\)', re.I),
)
RULE_KINDS = (
    (re.compile(r'\b(revers\w+|revert\w+|reopen\w+|new plan)\b', re.I), 'reversal'),
    (re.compile(r'\b(correction|corrected)\b', re.I), 'correction'),
    (re.compile(r'\bdecision\b', re.I), 'decision'),
)


def _norm(text):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 +]', ' ', text.lower())).strip()


def _rule_retracts(text):
    for pattern in RETRACT_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return ''


def _rule_kind(text):
    for pattern, kind in RULE_KINDS:
        if pattern.search(text):
            return kind
    return ''


def candidates(items):
    """Items worth sending to the model, as described in the module header"""
    live = [i for i in items if i['state'] != 'quarantined']
    hinted = [i for i in live if i['source'] != 'calendar'
              and HINT_RE.search(i['title'] + ' ' + i['body'])]
    # a linear snapshot joins when a hinted item references its identifier, or
    # shares a topic with one (the roadmap email thread and its issue have no
    # explicit id in common, only a matching title)
    refs = {r for i in hinted for r in ACME_RE.findall(i['title'] + ' ' + i['body'])}
    topics = {i['topic'] for i in hinted}
    linear = [i for i in live if i['source'] == 'linear'
              and (i['meta']['identifier'] in refs or i['topic'] in topics)]
    # an issue that is hinted by its own text joins with its other snapshots
    own = {i['meta']['identifier'] for i in hinted if i['source'] == 'linear'}
    linear += [i for i in live if i['source'] == 'linear'
               and i['meta']['identifier'] in own and i not in linear]
    seen, out = set(), []
    for item in hinted + linear:
        if item['id'] not in seen:
            seen.add(item['id'])
            out.append(item)
    return out


def label(item):
    text = f"{item['title']}\n{item['body']}"
    result = llm.chat(SYSTEM, f"source: {item['source']}\ntext: {text}", schema=SCHEMA,
                      cache=True, max_tokens=120)
    try:
        parsed = json.loads(result['text'])
    except ValueError:
        parsed = {'kind': 'none', 'value': '', 'retracts': ''}
    return parsed


def validate(item, parsed):
    """Apply the rules over the model's label. Returns (event dict, disagreed)"""
    text = f"{item['title']} {item['body']}"
    rule_kind = _rule_kind(text)
    kind = rule_kind or parsed.get('kind', 'none')
    disagreed = bool(rule_kind) and rule_kind != parsed.get('kind')

    # values and retractions must be copied from the text. a value the model
    # paraphrased or invented cannot be matched against other items later
    value = parsed.get('value', '').strip()
    if not value or _norm(value) not in _norm(text):
        value = item['body'].split('\n')[0][:120]
    # the model copies whole sentences or channel names into retracts, which
    # then matches nothing or too much. we only trust its answer when it is a
    # short span from the body with a digit in it (a date, a version, an id)
    retracts = parsed.get('retracts', '').strip()
    if not (retracts and re.search(r'\d', retracts) and len(retracts.split()) <= 4
            and _norm(retracts) in _norm(item['body'])):
        retracts = ''
    retracts = _rule_retracts(text) or retracts

    # a linear record is a statement of the current plan even when its wording
    # carries no decision verb
    if item['source'] == 'linear' and kind in ('none', 'restatement'):
        kind, value = 'decision', item['body']
    return {'kind': kind, 'value': value, 'retracts': retracts}, disagreed


def extract_decisions(items, topics, ident):
    events, disagreements = [], 0
    for item in candidates(items):
        event, disagreed = validate(item, label(item))
        disagreements += disagreed
        if event['kind'] in ('none',):
            continue
        events.append({
            'item_id': item['id'], 'topic': item['topic'], 'kind': event['kind'],
            'value': event['value'], 'retracts': event['retracts'], 'ts': item['ts'],
            'summary': item['body'].split('\n')[0][:160], 'source': item['source'],
            'status': 'current', 'why': '', 'dup_group': item['dup_group'] or item['id'],
        })
    print(f'labelled {len(events)} decision events, rules overrode the model on {disagreements}')
    resolve(events)
    return events


def resolve(events):
    by_topic = {}
    for event in events:
        by_topic.setdefault(event['topic'], []).append(event)
    for group in by_topic.values():
        group.sort(key=lambda e: e['ts'])
        # explicit retractions beat recency. a stale record edited later (a
        # linear issue touched after the correction) still carries the old value
        for correction in (e for e in group if e['retracts']):
            retracted = _norm(correction['retracts'])
            for other in group:
                if other is correction or other['ts'] <= correction['ts']:
                    continue
                if retracted and retracted in _norm(other['value']) and \
                        retracted not in _norm(correction['value']):
                    other['status'] = 'stale'
                    other['why'] = f"value '{correction['retracts']}' was retracted in {correction['item_id']}"
        live = [e for e in group if e['status'] != 'stale' and e['kind'] in DECISION_KINDS]
        if not live:
            continue
        # the anchor is the last event that changed the plan. everything from
        # there on, plus anything duplicating it in another tool, is the
        # current state. earlier events are superseded. records after the
        # anchor (a linear issue closed once the email went out) agree with it
        changers = [e for e in live if e['kind'] in ('reversal', 'correction')]
        anchor = (changers or live)[-1]
        for event in live:
            if event['ts'] >= anchor['ts'] or event['dup_group'] == anchor['dup_group']:
                event['status'] = 'current'
            else:
                event['status'] = 'superseded'
                event['why'] = f"replaced by {anchor['item_id']}"


def write_decisions(conn, events):
    for e in events:
        conn.execute('INSERT OR REPLACE INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?)',
                     (e['item_id'], e['topic'], e['kind'], e['value'], e['retracts'],
                      e['summary'], e['ts'], e['status'], e['why'], e['source']))
