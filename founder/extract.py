"""Decision extraction at ingest, and deterministic resolution of conflicts.

The model reads each candidate item once and labels it. We do not let it decide
what is current. That is plain code over the labels, because a small model
asked 'which of these is the latest decision' gets it wrong often enough to
matter, and because code is testable. The one judgement we do hand back to the
model is narrow: does an old record still say what the current decision says.

  1. gate        items that sound like a decision or a change. a regex catches
                 explicit wording, and similarity to prototype sentences catches
                 the rest ('Jordan says they cannot close before May 15,
                 updating the plan' has none of the regex words)
  2. label       the model names what each item is about in two to five words
                 ('pricing', 'seed close date'), which is the grouping key
  3. topics      events join when they share a thread or issue, when their
                 text is close in embedding space, or when they share a specific
                 person or company (a slack message about 'Jordan' belongs with
                 the deal Jordan is the contact on). we embed title and body with
                 no 'who and when' header: with the header, same-topic and
                 cross-topic pairs overlapped completely (0.68 to 0.92 against
                 0.58 to 0.73), without it they nearly separate. groups are
                 built around anchors, items that clearly are a change of plan,
                 because clustering every candidate chained all of them into one
  4. validate    values must be copied from the text, rules override the kind
                 when the wording is unambiguous ('reverting', 'corrected')
  5. resolve     per topic: the last change of plan is the anchor, everything
                 from there on is current, and a record in a tool of record that
                 still states the old plan is flagged stale
"""
import hashlib
import re

from . import llm
from .normalize import ACME_RE

# explicit wording. 'ship', 'now' and plain 'moved' appear in filler and would
# send hundreds of items to the model for nothing
HINT_RE = re.compile(
    r'\b(decision|decided|reversing|reverting|reopening|new plan|correction|corrected|'
    r'confirmed:|rescheduled|moving .{0,40} from|\(was )', re.I)

# what a change of plan sounds like, in the words people actually use. the gate
# takes the items most similar to any of these. wording here is deliberately
# generic: tuning it to the planted cases would make the recall number meaningless
PROTOTYPES = (
    'We decided to go with this option.',
    'Decision: the plan is now this.',
    'The date has moved to a later date.',
    'Correction: it is this value, not the one I said before.',
    'We are reversing the earlier decision.',
    'Updating the plan with the new target.',
    'Putting this on hold until further notice.',
    'They accepted another offer, so we are closing the loop.',
    'The cutover moves to a different date.',
    'New customers pay one price and existing customers keep the old price.',
    'Rescheduled, moved from Friday to another day.',
    'Agreed, the new plan is to do this instead.',
    'Target close date and amount for the deal.',
)
GATE_FRACTION = 0.10      # share of the pool taken by similarity, on top of the regex
GATE_RECORD_FRACTION = 0.25   # tools of record get a wider net, since a stale
                              # record is what we are trying to find in them

DECISION_KINDS = ('decision', 'reversal', 'correction')
RECORD_SOURCES = ('linear', 'notion', 'crm')   # a tool of record can go stale
GATE_KINDS = ('email', 'message', 'doc', 'issue', 'note', 'comment', 'deal')

# similarity cutoffs, measured on this data with title+body embeddings and no
# header: same-topic pairs run 0.62 to 0.86 and cross-topic pairs 0.47 to 0.62
ANCHOR_SCORE = 0.74       # gate score at which an item counts as a real change on its own
MERGE_COSINE = 0.74       # an anchor pair this close merges two groups
ENTITY_COSINE = 0.58      # a pair that shares a specific entity needs only this
GROUP_COSINE = 0.68       # average cosine between anchors of two merging groups
ATTACH_COSINE = 0.70      # a non-anchor joins the anchor group it is this close to
SPECIFIC_DF = 20          # an entity in more items than this links nothing
SCHEMA = {
    'type': 'object',
    'properties': {
        'kind': {'type': 'string',
                 'enum': ['decision', 'reversal', 'correction', 'restatement', 'proposal', 'none']},
        'subject': {'type': 'string'},
        'value': {'type': 'string'},
        'retracts': {'type': 'string'},
    },
    'required': ['kind', 'subject', 'value', 'retracts'],
}

SYSTEM = (
    'You label one work message or record. Reply with JSON only.\n'
    'kind: decision = a new choice was made. reversal = an earlier choice is undone '
    'or changed. correction = a wrong fact or date in an earlier message is fixed. '
    'restatement = repeats a choice with no change. proposal = an idea or question not yet '
    'agreed. none = no decision.\n'
    "subject: two to five words naming what it is about, like 'pricing' or 'ship date'.\n"
    'value: the choice or fact, copied from the text, under 12 words.\n'
    'retracts: the old value this replaces, copied from the text, or an empty string.')

RETRACT_PATTERNS = (
    re.compile(r'corrected from ([^)\n.]+)', re.I),
    re.compile(r',? not ([A-Z][a-z]{2} \d+|[^.\n]+?)(?:[.\n]|$)', re.I),
    re.compile(r'\(was ([^)]+)\)', re.I),
)
# the wording only counts at the start of a sentence. 'ship date needs another
# look after Sofia's correction' mentions a correction without making one, and
# an unanchored version of this rule made that email the current ship date
_START = r'(?:^|[.!?\n]\s*|:\s*)\W*'
RULE_KINDS = (
    (re.compile(_START + r'(revers\w+|revert\w+|reopen\w+|new plan)\b', re.I), 'reversal'),
    (re.compile(_START + r'(correction|corrected)\b', re.I), 'correction'),
    (re.compile(_START + r'decision\b', re.I), 'decision'),
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


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


# ---- gate ------------------------------------------------------------------

def gate_scores(items, vectors):
    """Max cosine to any prototype, per item id. Prototypes are embedded as
    queries, which is what nomic expects for a search against documents"""
    protos = llm.embed(list(PROTOTYPES), kind='query')
    return {i['id']: max(_cosine(vectors[i['id']], p) for p in protos) for i in items}


def scoring_pool(items):
    return [i for i in items if i['state'] == 'current' and i['kind'] in GATE_KINDS]


def candidates(items, scores):
    """Items worth sending to the model, as described in the module header"""
    live = [i for i in items if i['state'] not in ('quarantined', 'automated')]
    pool = scoring_pool(items)

    def top(rows, fraction):
        ranked = sorted(rows, key=lambda i: -scores[i['id']])
        return ranked[:max(1, int(len(ranked) * fraction))]

    people_items = [i for i in pool if i['source'] not in RECORD_SOURCES]
    record_items = [i for i in pool if i['source'] in RECORD_SOURCES]
    hinted = [i for i in live if i['source'] != 'calendar'
              and HINT_RE.search(i['title'] + ' ' + i['body'])]
    chosen = hinted + top(people_items, GATE_FRACTION) + top(record_items, GATE_RECORD_FRACTION)

    # a linear snapshot joins when a chosen item references its identifier, or
    # shares a topic with one (the roadmap email thread and its issue have no
    # explicit id in common, only a matching title). older snapshots of an issue
    # we already chose come along so its history is complete
    refs = {r for i in chosen for r in ACME_RE.findall(i['title'] + ' ' + i['body'])}
    topics = {i['topic'] for i in chosen}
    chosen_idents = {i['meta']['identifier'] for i in chosen if i['source'] == 'linear'}
    linear = [i for i in live if i['source'] == 'linear'
              and (i['meta']['identifier'] in refs or i['topic'] in topics
                   or i['meta']['identifier'] in chosen_idents)]
    seen, out = set(), []
    for item in chosen + linear:
        if item['id'] not in seen:
            seen.add(item['id'])
            out.append(item)
    return out


# ---- label -----------------------------------------------------------------

def label(item):
    text = f"{item['title']}\n{item['body']}"
    result = llm.chat(SYSTEM, f"source: {item['source']}\ntext: {text}", schema=SCHEMA,
                      cache=True, max_tokens=120, role='extract')
    return llm.parse_json(result['text'], {'kind': 'none', 'subject': '', 'value': '', 'retracts': ''})


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
    rule_retracts = _rule_retracts(text)
    retracts = rule_retracts or retracts
    # a message that names the value it replaces ('not Mar 20', 'corrected from
    # Mar 20') is a correction whatever else it says. only the explicit patterns
    # count: the model's own retracts also fired on a plain doc that lists two dates
    if rule_retracts and kind in ('decision', 'restatement', 'none'):
        kind = 'correction'

    # a record in a tool of record states the current plan whether or not its
    # wording carries a decision verb. that is what lets us notice it going stale
    if item['source'] in RECORD_SOURCES and kind in ('none', 'restatement', 'proposal'):
        kind = 'decision'
        value = item['body'].replace('\n', ' ')[:200] if item['source'] != 'crm' else item['body'][:200]
    subject = re.sub(r'[^a-z0-9 ]', ' ', parsed.get('subject', '').lower()).strip()
    if not subject or len(subject.split()) > 6:
        subject = re.sub(r'\s*\(ACME-\d+\)|^(re|fwd?):\s*', '', item['title'].lower()).strip()
    return {'kind': kind, 'subject': subject, 'value': value, 'retracts': retracts}, disagreed


def extract_decisions(items, topics, ident, vectors, scores, entities, plain):
    cands = candidates(items, scores)
    events, disagreements = [], 0
    for item in cands:
        event, disagreed = validate(item, label(item))
        disagreements += disagreed
        if event['kind'] in ('none', 'proposal'):
            continue
        explicit = bool(HINT_RE.search(item['title'] + ' ' + item['body']))
        events.append({
            'item_id': item['id'], 'explicit': explicit, 'structural': item['topic'], 'topic': item['topic'],
            'kind': event['kind'], 'subject': event['subject'], 'value': event['value'],
            'retracts': event['retracts'], 'ts': item['ts'], 'summary': item['body'].split('\n')[0][:160],
            'source': item['source'], 'status': 'current', 'why': '',
            'dup_group': item['dup_group'] or item['id'], 'item_state': item['state'],
            'text': f"{item['title']}. {item['body']}"[:400], 'entities': entities.get(item['id'], set()),
            'anchor': explicit or event['kind'] in ('reversal', 'correction')
                      or scores.get(item['id'], 0) >= ANCHOR_SCORE})
    for e in events:
        e['vec'] = plain[e['item_id']]
    events, merged = group_events(events)
    print(f'gate chose {len(cands)} items, merged {merged} groups, kept {len(events)} decision events '
          f'in {len({e["topic"] for e in events})} topics, rules overrode the model on {disagreements}')
    resolve(events)
    return events


def entity_map(items, ident):
    """Specific people and companies each item mentions or involves. Only
    outsiders count (a teammate's name is everywhere) and only ones that appear
    in few items, so 'Globex', which every customer email mentions, links nothing"""
    orgs = {p.org.lower(): p.id for p in ident.people.values() if p.org}
    found = {}
    for item in items:
        if item['state'] == 'automated':
            continue
        text = f"{item['title']} {item['body']}".lower()
        ents = {pid for pid in ident.match_name(text) if ident.people[pid].external}
        ents |= {f'org:{org}' for org in orgs if re.search(rf'\b{re.escape(org.split()[0])}\b', text)}
        ents |= {p for p in ([item['author']] + item['people']) if p and ident.people[p].external}
        # a company is also its people, so a deal with Jordan and a doc naming Northwind meet
        ents |= {f'org:{ident.people[e].org.lower()}' for e in list(ents) if e in ident.people and ident.people[e].org}
        found[item['id']] = ents
    df = {}
    for ents in found.values():
        for e in ents:
            df[e] = df.get(e, 0) + 1
    return {i: {e for e in ents if df[e] <= SPECIFIC_DF} for i, ents in found.items()}


def group_events(events):
    """Assign each event a decision topic, built around anchors. Returns
    (events kept, number of merges)"""
    if not events:
        return events, 0
    groups = {}
    for e in events:
        groups.setdefault(e['structural'], []).append(e)
    anchored = {k: g for k, g in groups.items() if any(m['anchor'] for m in g)}
    loose = {k: g for k, g in groups.items() if k not in anchored}

    def pair_cos(a, b):
        return _cosine(a['vec'], b['vec'])

    def link(ga, gb, need_anchor):
        """How strongly two groups belong together, or 0. The target side always
        counts only its anchors: matching any member let a pile of near-identical
        routine issues attach to whichever topic happened to contain one of them"""
        best = 0.0
        for x in ga:
            for y in gb:
                if not y['anchor'] or (need_anchor and not x['anchor']):
                    continue
                cos = pair_cos(x, y)
                shared = x['entities'] & y['entities']
                if cos >= MERGE_COSINE or (shared and cos >= ENTITY_COSINE):
                    best = max(best, cos)
        return best

    merged = 0
    while True:
        keys = list(anchored)
        scored = [(link(anchored[a], anchored[b], True), a, b) for n, a in enumerate(keys) for b in keys[n + 1:]]
        scored = [t for t in scored if t[0] > 0]
        # the average over anchors is the brake on chaining: one close pair is
        # not enough to fold two topics together
        scored = [t for t in scored if _avg_cos(anchored[t[1]], anchored[t[2]]) >= GROUP_COSINE]
        if not scored:
            break
        _, a, b = max(scored)
        anchored[a] += anchored.pop(b)
        merged += 1

    # groups with no anchor of their own (a doc, a linear issue, a quiet reply)
    # join the topic they are clearly about, or are dropped
    for members in loose.values():
        best, target = 0.0, None
        for key, group in anchored.items():
            strength = link(members, group, False)
            if strength > best:
                best, target = strength, key
        if target is not None:
            anchored[target] += members

    kept = []
    for members in anchored.values():
        # an anchor by similarity alone, with no group mates and no decision
        # wording, is a routine message and not a decision
        if len(members) == 1 and not (members[0]['explicit'] or members[0]['source'] in RECORD_SOURCES
                                      or members[0]['kind'] in ('reversal', 'correction')):
            continue
        name = 'dt:' + hashlib.sha1(min(m['item_id'] for m in members).encode()).hexdigest()[:10]
        for m in members:
            m['topic'] = name
        kept += members
    return kept, merged


def _avg_cos(ga, gb):
    anchors_a = [x for x in ga if x['anchor']]
    anchors_b = [y for y in gb if y['anchor']]
    sims = [_cosine(x['vec'], y['vec']) for x in anchors_a for y in anchors_b]
    return sum(sims) / len(sims)


def _team_names(ident):
    return {w.lower() for p in ident.people.values() if not p.external for w in re.findall(r'[A-Za-z]+', p.name)}


# ---- resolve ---------------------------------------------------------------

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
        # anchor (a linear issue closed once the email went out) agree with it.
        # which records still state an old plan is a separate pass (stale.py)
        changers = [e for e in live if e['kind'] in ('reversal', 'correction')]
        anchor = (changers or live)[-1]
        for event in live:
            if event['ts'] >= anchor['ts'] or event['dup_group'] == anchor['dup_group']:
                event['status'] = 'current'
                continue
            event['status'] = 'superseded'
            event['why'] = f"replaced by {anchor['item_id']}"


def write_decisions(conn, events):
    for e in events:
        conn.execute('INSERT OR REPLACE INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                     (e['item_id'], e['topic'], e['kind'], e['value'], e['retracts'],
                      e['summary'], e['ts'], e['status'], e['why'], e['source'], e['subject']))
