"""Morning brief: no question asked. Deterministic sections do the finding,
the model only picks and phrases the top focus items.

Why not let the model read everything and 'write a brief': a 3B model skims,
misses the one stale record, and its output is not testable. Here every
section is a query we can assert on, and the model is limited to ranking a
short list of facts we already verified."""
import re
from datetime import timedelta

from . import answer, config, llm, store

WINDOW_DAYS = 7           # 'recent' for decisions and customer issues
ASK_WINDOW_DAYS = 14      # how far back an unanswered ask still counts
CUSTOMERS = ('Globex', 'Initech', 'Hooli', 'Umbrella', 'Stark', 'Wayne')
CUSTOMER_ISSUE_RE = re.compile(r'\b(reported|flake|escalat\w+|issue|bug|outage)\b', re.I)
ASK_RE = re.compile(r'\b(please|can you|could you|need you)\b|\?', re.I)

FOCUS_SYSTEM = (
    f"You write the top of a morning brief for the founder, Alex Chen. Time: "
    f"{config.NOW.strftime('%A %Y-%m-%d %H:%M')} UTC.\n"
    'You get numbered facts, already ranked. Write one action line per fact, in the '
    'same order and numbering. Say what to do and why it matters now. End each line '
    'with its own fact number, like [2]. Use only the words and numbers in the fact. '
    'Do not combine facts.')


def _iso(dt):
    return config.iso(dt)


def _names(conn):
    return {r['id']: r['name'] for r in conn.execute('SELECT id, name FROM people')}


def _hhmm(text):
    return text[11:16]


def _topic_label(conn, topic):
    """A readable name for a decision topic: the linear title if the topic has
    an issue, else the earliest email subject without its Re: prefix"""
    row = conn.execute(
        "SELECT title FROM items WHERE topic=? AND source='linear' ORDER BY ts LIMIT 1", (topic,)).fetchone()
    if not row:
        row = conn.execute(
            "SELECT title FROM items WHERE topic=? AND kind='email' ORDER BY ts LIMIT 1", (topic,)).fetchone()
    return re.sub(r'^(re:\s*)+', '', row['title'], flags=re.I) if row else 'plan'


PRIORITY_NAMES = {0: 'no priority', 1: 'urgent', 2: 'high', 3: 'medium', 4: 'low'}


def _rank(item):
    """linear uses 0 for 'no priority', which would sort above urgent"""
    return item['meta'].get('priority') or 5


def _clean_title(item):
    return re.sub(r'\s*\(ACME-\d+\)$', '', item['title'])


def todays_schedule(conn, names):
    day = config.NOW.replace(hour=0, minute=0, second=0)
    rows = conn.execute(
        "SELECT * FROM items WHERE kind='event' AND start >= ? AND start < ? ORDER BY start",
        (_iso(day), _iso(day + timedelta(days=1))))
    out = []
    for row in rows:
        item = store.row_to_item(row)
        if config.FOUNDER_PERSON_ID not in item['people'] or item['status'] == 'cancelled':
            continue
        upcoming = item['start'] >= _iso(config.NOW)
        response = item['meta']['responses'].get(config.FOUNDER_PERSON_ID, '')
        notes = []
        if item['body']:
            notes.append(item['body'][0].lower() + item['body'][1:])
        if response in ('needsAction', 'declined'):
            notes.append('you have not accepted' if response == 'needsAction' else 'you declined')
        if 'end_before_start_assumed_1h' in item['flags']:
            notes.append('end time in the calendar data is invalid, assumed 1h')
        out.append({'item': item, 'upcoming': upcoming, 'notes': notes,
                    'attendees': [names[p] for p in item['people'] if p != config.FOUNDER_PERSON_ID]})
    return out


def recent_decisions(conn):
    """Topics whose plan changed this week, with what replaced what, plus any
    record that still carries a retracted value"""
    since = _iso(config.NOW - timedelta(days=WINDOW_DAYS + 7))
    topics = [r['topic'] for r in conn.execute(
        "SELECT topic FROM decisions WHERE kind IN ('reversal','correction') AND ts >= ? "
        'GROUP BY topic', (since,))]
    out = []
    for topic in topics:
        rows = [dict(r) for r in conn.execute(
            'SELECT * FROM decisions WHERE topic=? ORDER BY ts', (topic,))]
        current = [r for r in rows if r['status'] == 'current']
        if not current:
            continue
        out.append({'label': _topic_label(conn, topic), 'current': current[-1], 'history': [r for r in rows if r['status'] == 'superseded'],
                    'stale': [r for r in rows if r['status'] == 'stale']})
    return out


def blocked_for_founder(conn):
    rows = [store.row_to_item(r) for r in conn.execute(
        "SELECT * FROM items WHERE source='linear' AND state='current' AND status='Blocked' "
        'AND author = ? ORDER BY ts DESC', (config.FOUNDER_PERSON_ID,))]
    return sorted(rows, key=_rank)


def unanswered_asks(conn):
    """Inbound requests to the founder with no reply from them in the thread,
    each checked against evidence that it was already handled"""
    since = _iso(config.NOW - timedelta(days=ASK_WINDOW_DAYS))
    rows = conn.execute(
        "SELECT * FROM items WHERE kind='email' AND state='current' AND ts >= ? AND ts <= ? "
        'AND author != ? ORDER BY ts DESC', (since, _iso(config.NOW), config.FOUNDER_PERSON_ID))
    out = []
    for row in rows:
        item = store.row_to_item(row)
        if config.FOUNDER_PERSON_ID not in item['people'] or not ASK_RE.search(item['body']):
            continue
        replied = conn.execute(
            'SELECT 1 FROM items WHERE thread_key=? AND author=? AND ts > ?',
            (item['thread_key'], config.FOUNDER_PERSON_ID, item['ts'])).fetchone()
        if replied:
            continue
        out.append({'item': item, 'handled_by': _handled_by(conn, item)})
    return out


def _handled_by(conn, item):
    """Cheap evidence that an ask was done without a reply. an issue it names
    moved to Done after the ask, or it asked to decline an invite that is now
    cancelled"""
    for ref in set(re.findall(r'\bACME-\d+\b', item['body'])):
        done = conn.execute(
            "SELECT id FROM items WHERE source='linear' AND state='current' "
            "AND json_extract(meta,'$.identifier')=? AND status='Done' AND ts > ?",
            (ref, item['ts'])).fetchone()
        if done:
            return done['id']
    match = re.search(r'decline the old invite', item['body'], re.I)
    if match:
        cancelled = conn.execute(
            "SELECT id FROM items WHERE kind='event' AND status='cancelled' AND ? LIKE '%' || title || '%'",
            (item['title'],)).fetchone()
        if cancelled:
            return cancelled['id']
    return None


def repeated_customer_issues(conn):
    since = _iso(config.NOW - timedelta(days=WINDOW_DAYS))
    out = []
    for customer in CUSTOMERS:
        rows = [store.row_to_item(r) for r in conn.execute(
            "SELECT * FROM items WHERE kind IN ('email','message') AND state='current' "
            'AND ts >= ? AND ts <= ? AND (body LIKE ? OR title LIKE ?)',
            (since, _iso(config.NOW), f'%{customer}%', f'%{customer}%'))]
        issues = [r for r in rows if CUSTOMER_ISSUE_RE.search(r['body'] + ' ' + r['title'])]
        if len(issues) >= 2:
            out.append({'customer': customer, 'items': issues})
    return sorted(out, key=lambda c: -len(c['items']))


def build_facts(conn, names, schedule, decisions, blocked, asks, customers):
    """Scored facts: (score, text, ids). The score is what makes this a brief
    and not a dump. Rough order: a meeting soon, a record you must fix, an ask
    nobody handled, a changed plan, your blocked work, repeating customers."""
    facts = []
    for e in schedule:
        item = e['item']
        if e['upcoming']:
            hours = (_parse(item['start']) - config.NOW).total_seconds() / 3600
            note = f" ({'; '.join(e['notes'])})" if e['notes'] else ''
            facts.append((100 - hours, f"Meeting today {_hhmm(item['start'])} UTC: {item['title']} with "
                          f"{', '.join(e['attendees'])}{note}", [item['id']]))
    for d in decisions:
        text = f"{d['label']}: current plan is '{d['current']['value']}'"
        if d['history']:
            text += f", replacing '{d['history'][-1]['value']}'"
        ids = [d['current']['item_id']]
        score = 60
        for stale in d['stale']:
            text += (f". The record {stale['item_id'].split('@')[0].split(':')[1]} still says "
                     f"'{stale['value']}' and must be updated")
            ids.append(stale['item_id'])
            score = 90
        facts.append((score, text, ids))
    for a in asks:
        if a['handled_by']:
            continue
        sender = names.get(a['item']['author'], 'someone')
        facts.append((80, f"{sender} asked you and nobody has handled it: '{a['item']['body'][:100]}'",
                      [a['item']['id']]))
    for item in blocked:
        facts.append((50 - _rank(item), f"Blocked, owned by you: {item['meta']['identifier']} "
                      f"{_clean_title(item)}", [item['id']]))
    for c in customers[:2]:
        facts.append((30 + len(c['items']), f"{c['customer']} issue mentioned {len(c['items'])} times "
                      f"in {WINDOW_DAYS} days", [i['id'] for i in c['items']][:3]))
    return sorted(facts, key=lambda f: -f[0])


def _parse(text):
    from datetime import datetime
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


FOCUS_COUNT = 3


def focus_section(facts):
    """Top facts by score, phrased by the model as action lines. We hand it
    exactly the facts to phrase so it has nothing to rank, and nothing to
    invent a link between: an earlier version given all facts joined two
    unrelated issues in one line"""
    top = facts[:FOCUS_COUNT]
    if not top:
        return '', [], None
    numbered = '\n'.join(f'[{n}] {text}' for n, (_, text, _) in enumerate(top, 1))
    result = llm.chat(FOCUS_SYSTEM, f'Facts:\n{numbered}', max_tokens=260)
    labels = {n: ids for n, (_, _, ids) in enumerate(top, 1)}
    cited = []

    def swap(match):
        nums = [int(n) for n in re.split(r'\s*,\s*', match.group(1))]
        ids = [labels[n][0] for n in nums if n in labels]
        cited.extend(ids)
        return ''.join(f'[{i}]' for i in ids)

    # the model likes to open with 'Here is the morning brief'. we only keep
    # the numbered lines
    lines = [l for l in result['text'].strip().splitlines() if re.match(r'\s*\d+\.', l)]
    return answer.CITE_RE.sub(swap, '\n'.join(lines) or result['text'].strip()), cited, result


def generate(conn):
    names = _names(conn)
    schedule = todays_schedule(conn, names)
    decisions = recent_decisions(conn)
    blocked = blocked_for_founder(conn)
    asks = unanswered_asks(conn)
    customers = repeated_customer_issues(conn)
    facts = build_facts(conn, names, schedule, decisions, blocked, asks, customers)
    focus, cited, llm_result = focus_section(facts)

    lines = [f"# Morning brief, {config.NOW.strftime('%A %B %d, %Y')}",
             f"as of {config.NOW.strftime('%H:%M')} UTC", '']
    if focus:
        lines += ['## Focus today', focus, '']

    lines += ['## Today']
    if not schedule:
        lines.append('- nothing on your calendar')
    for e in schedule:
        item = e['item']
        past = '' if e['upcoming'] else ' (already started)'
        note = f" - {'; '.join(e['notes'])}" if e['notes'] else ''
        lines.append(f"- {_hhmm(item['start'])}-{_hhmm(item['end'])} UTC {item['title']} with "
                     f"{', '.join(e['attendees'])}{past}{note} [{item['id']}]")

    lines += ['', '## Plans that changed']
    if not decisions:
        lines.append('- none this week')
    for d in decisions:
        cur = d['current']
        line = f"- {d['label']}: {cur['value']} (as of {cur['ts'][:10]}) [{cur['item_id']}]"
        if d['history']:
            line += f"; replaced '{d['history'][-1]['value']}' [{d['history'][-1]['item_id']}]"
        lines.append(line)
        for stale in d['stale']:
            lines.append(f"  - out of date: {stale['item_id'].split('@')[0].split(':')[1]} still says "
                         f"'{stale['value']}', update it [{stale['item_id']}]")

    lines += ['', '## Blocked on you']
    lines += [f"- {i['meta']['identifier']} {_clean_title(i)}, {PRIORITY_NAMES.get(i['meta']['priority'], 'no priority')} [{i['id']}]" for i in blocked] or ['- nothing']

    lines += ['', '## Follow-ups']
    if not asks:
        lines.append('- nothing waiting on you')
    for a in asks:
        sender = names.get(a['item']['author'], 'someone')
        tail = (f" - looks handled [{a['handled_by']}]" if a['handled_by'] else ' - no reply yet')
        lines.append(f"- {sender}: {a['item']['body'][:90].replace(chr(10), ' ')}{tail} [{a['item']['id']}]")

    if customers:
        lines += ['', '## Customer issues repeating']
        for c in customers:
            lines.append(f"- {c['customer']}: {len(c['items'])} mentions this week "
                         + ' '.join(f"[{i['id']}]" for i in c['items'][:3]))

    return {'text': '\n'.join(lines) + '\n', 'facts': facts, 'focus_cited': cited,
            'seconds': llm_result['seconds'] if llm_result else 0,
            'prompt_tokens': llm_result['prompt_tokens'] if llm_result else 0,
            'completion_tokens': llm_result['completion_tokens'] if llm_result else 0}
