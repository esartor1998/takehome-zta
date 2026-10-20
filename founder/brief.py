"""Morning brief: no question asked. Deterministic sections do the finding,
the model only picks and phrases the top focus items.

Why not let the model read everything and 'write a brief': a 3B model skims,
misses the one stale record, and its output is not testable. Here every
section is a query we can assert on, and the model is limited to phrasing a
short list of facts we already verified. The same facts answer the open
questions in answer.py ('anything urgent', 'what am I missing'), so the brief
and the question path cannot disagree about what matters"""
import json
import re
from datetime import datetime, timedelta

from . import answer, config, llm, store

WINDOW_DAYS = 7           # 'recent' for decisions and customer issues
ISSUE_WINDOW_DAYS = 14    # how far back repeated customer reports are counted
CUSTOMERS = ('Globex', 'Initech', 'Hooli', 'Umbrella', 'Stark', 'Wayne')
FOCUS_COUNT = 3
SOON_DAYS = 2             # a deadline this close raises an ask's score

# what kind of problem a message describes, by its own words. two reports are
# the same issue only if they have the same company and the same kind
ISSUE_TYPES = (
    ('timeout', re.compile(r'time[ds]? ?out|504|too slow', re.I)),
    ('login loop', re.compile(r'redirect loop|login loop|loops?\b|stuck in a redirect', re.I)),
    ('invoice', re.compile(r'invoice|seat count|billing error', re.I)),
    ('flake', re.compile(r'flake|flaky', re.I)),
    ('outage', re.compile(r'outage|down for|incident', re.I)),
)

FOCUS_SYSTEM = (
    f"You write the top of a morning brief for the founder, Alex Chen. Time: "
    f"{config.NOW.strftime('%A %Y-%m-%d %H:%M')} UTC.\n"
    'You get numbered facts, already ranked. Write one action line per fact, in the '
    'same order and numbering. Say what to do and why it matters now. End each line '
    'with its own fact number, like [2]. Use only the words and numbers in the fact. '
    'Do not combine facts.')

PRIORITY_NAMES = {0: 'no priority', 1: 'urgent', 2: 'high', 3: 'medium', 4: 'low'}


def _iso(dt):
    return config.iso(dt)


def _parse(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def _names(conn):
    """Display names, with the company for outsiders: 'Daniel Foster (Globex)'"""
    return {r['id']: (f"{r['name']} ({r['org']})" if r['org'] else r['name'])
            for r in conn.execute('SELECT id, name, org FROM people')}


def _hhmm(text):
    return text[11:16]


def _rank(item):
    """linear uses 0 for 'no priority', which would sort above urgent"""
    return item['meta'].get('priority') or 5


def _clean_title(item):
    return re.sub(r'\s*\(ACME-\d+\)$', '', item['title'])


# ---- the calendar ------------------------------------------------------------

def day_events(conn, names, start, end):
    """The founder's events between start and end in every state, with what a
    person needs to know about each: done or still to come, cancelled,
    tentative, all-day, a time zone other than UTC, outside guests"""
    out, shown = [], set()
    for row in conn.execute("SELECT * FROM items WHERE kind='event' AND start >= ? AND start < ? ORDER BY start",
                            (_iso(start), _iso(end))):
        item = store.row_to_item(row)
        if config.FOUNDER_PERSON_ID not in item['people']:
            continue
        # one meeting on two calendars is one line
        if item['dup_group']:
            if item['dup_group'] in shown:
                continue
            shown.add(item['dup_group'])
        flags = []
        if item['status'] == 'cancelled':
            flags.append('CANCELLED')
        elif item['status'] == 'tentative':
            flags.append('tentative')
        if 'all_day' in item['flags']:
            flags.append('all day')
        response = item['meta']['responses'].get(config.FOUNDER_PERSON_ID, '')
        if response == 'needsAction' and item['status'] == 'confirmed':
            flags.append('you have not accepted')
        elif response == 'declined':
            flags.append('you declined')
        zone = item['meta'].get('time_zone', '')
        local = item['meta'].get('start_local', '')
        if zone and zone != 'UTC' and 'T' in local:
            flags.append(f'{local[11:16]} {zone.split("/")[-1].replace("_", " ")} time')
        if 'end_before_start_assumed_1h' in item['flags']:
            flags.append('end time invalid, assumed 1h')
        past = item['end'] <= _iso(config.NOW) and 'all_day' not in item['flags']
        started = item['start'] <= _iso(config.NOW) < item['end']
        out.append({'item': item, 'flags': flags, 'past': past, 'started': started,
                    'upcoming': not past and not started and item['status'] != 'cancelled',
                    'attendees': [names[p] for p in item['people'] if p != config.FOUNDER_PERSON_ID],
                    'external': [p for p in item['people'] if names[p].endswith(')')]})
    return out


def event_line(e):
    item = e['item']
    when = 'all day' if 'all day' in e['flags'] else f"{_hhmm(item['start'])}-{_hhmm(item['end'])} UTC"
    # a list that spans days needs the date, or 'Tuesday's meeting' reads as today's
    if item['start'][:10] != config.NOW.strftime('%Y-%m-%d'):
        when = f"{_parse(item['start']).strftime('%a %b %-d')} {when}"
    notes = [f for f in e['flags'] if f != 'all day']
    if e['past']:
        notes.append('already happened')
    elif e['started']:
        notes.append('in progress')
    if item['body']:
        notes.append(item['body'][0].lower() + item['body'][1:])
    guests = f" with {', '.join(e['attendees'])}" if e['attendees'] else ''
    return f"{when} {item['title']}{guests}" + (f" ({'; '.join(notes)})" if notes else '')


def meeting_prep(conn, event, names):
    """What to have in your head before a meeting with outsiders: their open
    asks of you, and customer issues for their company that are not closed"""
    notes, ids = [], []
    for pid in event['external']:
        for row in conn.execute("SELECT item_id, what FROM followups WHERE who=? AND kind='ask' AND status='open'",
                                (pid,)):
            notes.append(f"{names[pid]} is waiting on you: {row['what']}")
            ids.append(row['item_id'])
        org = conn.execute('SELECT org FROM people WHERE id=?', (pid,)).fetchone()['org']
        if org:
            for row in conn.execute(
                    "SELECT id, title, status FROM items WHERE source='linear' AND state='current' "
                    "AND status IN ('Reopened','Blocked','In Progress') AND (title LIKE ? OR body LIKE ?) "
                    "ORDER BY ts DESC LIMIT 2", (f'%{org}%', f'%{org}%')):
                notes.append(f"{_clean_title({'title': row['title']})} is {row['status']}")
                ids.append(row['id'])
    return notes, ids


# ---- changes of plan and stale records ----------------------------------------

def recent_decisions(conn):
    """Topics where a decision was made or changed recently, with what it
    replaced. A topic counts if its current decision is recent, so a plain
    decision (pricing, a hiring call) shows up as well as a reversal"""
    since = _iso(config.NOW - timedelta(days=WINDOW_DAYS + 7))
    topics = [r['topic'] for r in conn.execute(
        "SELECT topic FROM decisions WHERE status='current' AND ts >= ? GROUP BY topic", (since,))]
    out = []
    for topic in topics:
        rows = [dict(r) for r in conn.execute('SELECT * FROM decisions WHERE topic=? ORDER BY ts', (topic,))]
        current = [r for r in rows if r['status'] == 'current']
        if not current:
            continue
        norm = lambda text: re.sub(r'\W+', ' ', text.lower()).strip()
        # what it replaced has to differ from what it is now. the same value posted
        # in slack and in email is one decision, not 'Mar 31 replacing Mar 31'
        out.append({'label': store.topic_label(conn, topic), 'current': current[-1],
                    'history': [r for r in rows if r['status'] == 'superseded'
                                and norm(r['value']) != norm(current[-1]['value'])]})
    return out


def stale_records(conn):
    """Records that still state an old plan, from both detectors: a value that
    was explicitly retracted, and a newer item that changes a date or price"""
    out, seen = [], set()
    for r in conn.execute(
            'SELECT s.item_id, s.newer_id, s.current_fact, i.title, i.source, i.body, n.source AS nsource '
            'FROM stale_records s JOIN items i ON i.id=s.item_id JOIN items n ON n.id=s.newer_id '
            'ORDER BY i.ts DESC'):
        seen.add(r['item_id'])
        out.append({'item_id': r['item_id'], 'title': r['title'], 'source': r['source'],
                    'fact': r['current_fact'], 'newer_id': r['newer_id'], 'says': r['body'].replace('\n', ' ')[:80]})
    for r in conn.execute("SELECT d.item_id, d.value, d.why, i.title, i.source FROM decisions d "
                          "JOIN items i ON i.id=d.item_id WHERE d.status='stale'"):
        if r['item_id'] in seen:
            continue
        newer = re.search(r'(?:in|by) ([a-z]+:\S+)\s*$', r['why'])
        out.append({'item_id': r['item_id'], 'title': re.sub(r'\s*\(ACME-\d+\)$', '', r['title']),
                    'source': r['source'], 'fact': r['why'], 'newer_id': newer.group(1) if newer else '',
                    'says': r['value'][:80]})
    return out


def blocked_for_founder(conn):
    rows = [store.row_to_item(r) for r in conn.execute(
        "SELECT * FROM items WHERE source='linear' AND state='current' AND status='Blocked' "
        'AND author = ? ORDER BY ts DESC', (config.FOUNDER_PERSON_ID,))]
    return sorted(rows, key=_rank)


# ---- follow-ups ----------------------------------------------------------------

def followup_rows(conn):
    return [dict(r) for r in conn.execute(
        'SELECT f.*, p.name AS who_name, i.title, i.source FROM followups f JOIN items i ON i.id=f.item_id '
        'LEFT JOIN people p ON p.id=f.who ORDER BY f.ts DESC')]


def _due_bonus(row):
    if not row['due']:
        return 0
    today = config.NOW.strftime('%Y-%m-%d')
    if row['due'] < today:
        return 15
    return 10 if row['due'] <= (config.NOW + timedelta(days=SOON_DAYS)).strftime('%Y-%m-%d') else 0


def followup_text(row, names):
    """One line for a follow-up, with who, what and when it is due"""
    due = f", due {row['due']}" if row['due'] else ''
    overdue = ' (overdue)' if row['due'] and row['due'] < config.NOW.strftime('%Y-%m-%d') and row['status'] == 'open' else ''
    if row['kind'] == 'promise':
        whom = ', '.join(names.get(p, p) for p in row['whom'].split(',') if p) or 'someone'
        return f"You promised {whom}: {row['what']}{due}{overdue}, and it is still open"
    who = names.get(row['who'], 'someone')
    state = {'open': 'nobody has handled it', 'replied': 'already answered', 'handled': 'already handled'}[row['status']]
    return f"{who} asked you: {row['what']}{due}{overdue} ({state})"


# ---- customers -----------------------------------------------------------------

def recurring_customer_issues(conn, names):
    """The same kind of problem reported again by or about the same company.
    Evidence is spread across tools (an email, a slack thread, an issue, a PR),
    so we count distinct days, distinct tools and reports written by the
    customer, not raw mentions: a template that repeats a customer name ten
    times in one tool is not a recurring issue"""
    since = _iso(config.NOW - timedelta(days=ISSUE_WINDOW_DAYS))
    orgs = {r['org']: r['id'] for r in conn.execute("SELECT org, id FROM people WHERE org != '' AND external=1")}
    candidates = {org: org for org in orgs} | {c: c for c in CUSTOMERS}
    clusters = {}
    for row in conn.execute("SELECT * FROM items WHERE state='current' AND ts >= ? AND ts <= ? AND kind IN "
                            "('email','message','issue','pr','comment')", (since, _iso(config.NOW))):
        item = store.row_to_item(row)
        text = f"{item['title']} {item['body']}"
        for org in candidates:
            if not re.search(rf'\b{org}\b', text, re.I) and not (
                    item['author'] and names.get(item['author'], '').endswith(f'({org})')):
                continue
            for label, pattern in ISSUE_TYPES:
                if pattern.search(text):
                    clusters.setdefault((org, label), []).append(item)
    out = []
    for (org, label), items in clusters.items():
        days = {i['ts'][:10] for i in items}
        sources = {i['source'] for i in items}
        outside = [i for i in items if i['author'] and names.get(i['author'], '').endswith(')')]
        reopened = any(i['source'] == 'linear' and i['status'] == 'Reopened' for i in items)
        if len(days) < 2 and not reopened:
            continue
        # template mail from teammates repeats customer names all day. a real
        # recurring problem is reported by the customer, or shows up in more than
        # one tool (an email, an issue, a thread)
        if len(sources) < 2 and len(outside) < 2:
            continue
        score = 2 * len(days) + 3 * len(sources) + 3 * len(outside) + (10 if reopened else 0)
        out.append({'customer': org, 'label': label, 'items': items, 'days': len(days), 'sources': sorted(sources),
                    'reopened': reopened, 'outside': len(outside), 'score': score})
    return sorted(out, key=lambda c: -c['score'])[:4]


# ---- facts -----------------------------------------------------------------------

def build_facts(conn, names):
    """Scored facts as dicts: score, text, ids, cat, handled. The score is what
    makes this a brief and not a dump. Rough order: a meeting soon, a record
    you must fix, an overdue ask or promise, a changed plan, your blocked work,
    repeating customers. Handled items stay in with low scores so a question
    like 'what am I missing' can say they were checked"""
    facts = []

    def add(score, text, ids, cat, handled=False, **extra):
        facts.append({'score': score, 'text': text, 'ids': [i for i in ids if i], 'cat': cat, 'handled': handled, **extra})

    today = config.NOW.replace(hour=0, minute=0, second=0, microsecond=0)
    for e in day_events(conn, names, today, today + timedelta(days=1)):
        item = e['item']
        if e['upcoming']:
            hours = (_parse(item['start']) - config.NOW).total_seconds() / 3600
            notes, ids = meeting_prep(conn, e, names)
            prep = f". Before it: {'; '.join(notes)}" if notes else ''
            # a routine meeting is not a priority. one with outsiders and open business is, and
            # a tentative one is not. these weights put a prepared customer meeting above a weekly sync
            score = 60 - hours + (30 if notes else 0) - (20 if item['status'] == 'tentative' else 0)
            add(score, f"Meeting today: {event_line(e)}{prep}", [item['id']] + ids, 'meeting')
        else:
            add(5, f"Today, earlier or not happening: {event_line(e)}", [item['id']], 'schedule', handled=True)
    for r in stale_records(conn):
        fact = f", but the newer information says: {r['fact']}" if r['fact'] else ''
        add(72, f"{r['title']} ({r['source']}) still says '{r['says']}'{fact}. It is out of date and needs updating",
            [r['item_id'], r['newer_id']], 'stale')
    for d in recent_decisions(conn):
        text = f"{d['label']}: current plan is '{d['current']['value']}'"
        if d['history']:
            text += f", replacing '{d['history'][-1]['value']}'"
        add(25, text + '. Records already reflect this, no action needed', [d['current']['item_id']], 'change', handled=True)
    for row in followup_rows(conn):
        done = row['status'] != 'open'
        base = 70 if row['kind'] == 'ask' else 70
        add(5 if done else base + _due_bonus(row), followup_text(row, names), [row['item_id'], row['evidence']],
            'ask' if row['kind'] == 'ask' else 'promise', handled=done,
            people=[row['who']] + [p for p in row['whom'].split(',') if p],
            overdue=bool(row['due']) and row['due'] < config.NOW.strftime('%Y-%m-%d') and row['status'] == 'open')
    for item in blocked_for_founder(conn):
        add(50 - _rank(item), f"Blocked, owned by you: {item['meta']['identifier']} {_clean_title(item)}", [item['id']], 'blocked')
    for c in recurring_customer_issues(conn, names):
        ids = [i['id'] for i in sorted(c['items'], key=lambda i: i['ts'])][-3:]
        recurred = ', and a fix that was marked done came back' if c['reopened'] else ''
        add(30 + c['score'], f"{c['customer']} {c['label']} reported again: {len(c['items'])} reports on {c['days']} days "
            f"across {', '.join(c['sources'])}{recurred}", ids, 'customer')
    return sorted(facts, key=lambda f: -f['score'])


def prep_facts(conn, plan, question):
    """Everything to have in your head before one meeting. The meeting is the one
    the question names (by a guest, a company or a title word) or else the next one.
    Open asks the guests have made of you, promises you made them, the open issues
    for their company and the pull requests waiting on you that fix those, the
    emails linked to the meeting, and anything that changed about it"""
    names = _names(conn)
    low = question.lower()
    upcoming = [e for e in day_events(conn, names, config.NOW - timedelta(hours=1), config.NOW + timedelta(days=14))
                if e['upcoming'] or e['started']]
    if not upcoming:
        return []
    org_words = {w for pid in plan.people for w in re.findall(r'[a-z]{4,}', names.get(pid, '').lower())}
    word_set = set(re.findall(r'[a-z]{4,}', low)) | org_words

    def relevance(e):
        title = set(re.findall(r'[a-z]{4,}', e['item']['title'].lower()))
        guests = {w for pid in e['item']['people'] for w in re.findall(r'[a-z]{4,}', names.get(pid, '').lower())}
        return len((title | guests) & word_set - GENERIC_QUESTION_WORDS)
    best = max(upcoming, key=lambda e: (relevance(e), -upcoming.index(e)))
    e = best if relevance(best) else upcoming[0]
    item = e['item']
    facts = [{'score': 0, 'text': f'Meeting: {event_line(e)}', 'ids': [item['id']], 'cat': 'prep', 'handled': False}]

    def add(text, *ids):
        facts.append({'score': 0, 'text': text, 'ids': [i for i in ids if i], 'cat': 'prep', 'handled': False})

    guests = [p for p in item['people'] if p != config.FOUNDER_PERSON_ID]
    for row in followup_rows(conn):
        if row['status'] == 'open' and row['kind'] == 'ask' and row['who'] in guests:
            add(followup_text(row, names), row['item_id'])
        if row['status'] == 'open' and row['kind'] == 'promise' and set(row['whom'].split(',')) & set(guests):
            add(followup_text(row, names), row['item_id'])
    notes, ids = meeting_prep(conn, e, names)
    seen_issue = set()
    for note, item_id in zip(notes, ids):
        if 'waiting on you' not in note:
            add(note, item_id)
            seen_issue.add(item_id)
    # pull requests waiting on you that name one of those issues
    for issue_id in list(seen_issue):
        row = conn.execute("SELECT meta FROM items WHERE id=?", (issue_id,)).fetchone()
        ident = (json.loads(row['meta']) if row else {}).get('identifier')
        if ident:
            for pr in conn.execute("SELECT id, title, status, people FROM items WHERE kind='pr' AND status='open' "
                                   "AND (title LIKE ? OR body LIKE ?)", (f'%{ident}%', f'%{ident}%')):
                if config.FOUNDER_PERSON_ID in json.loads(pr['people']):
                    add(f"PR waiting on your review: {pr['title']}", pr['id'])
    for r in conn.execute("SELECT a, b FROM links WHERE (a=? OR b=?) AND reason='title'", (item['id'], item['id'])):
        other = r['b'] if r['a'] == item['id'] else r['a']
        row = conn.execute("SELECT title, ts, source FROM items WHERE id=? AND kind IN ('email','message')", (other,)).fetchone()
        if row:
            add(f"Related {row['source']} ({row['ts'][:10]}): {row['title']}", other)
    return facts


def company_facts(conn, plan):
    """The whole picture of one account: meetings coming up with its people, what they
    are waiting on from you, what you promised them, open issues that name the
    company, the recent mail, the deal, and anything on file that is out of date"""
    names = _names(conn)
    people = list(plan.org_people)
    org = plan.orgs[0] if plan.orgs else 'the company'
    facts = []

    def add(text, *ids):
        facts.append({'score': 0, 'text': text, 'ids': [i for i in ids if i], 'cat': 'company', 'handled': False})

    for e in day_events(conn, names, config.NOW, config.NOW + timedelta(days=14)):
        if (e['upcoming'] or e['started']) and set(e['item']['people']) & set(people):
            add(f"Meeting coming up: {event_line(e)}", e['item']['id'])
    for row in followup_rows(conn):
        if row['status'] == 'open' and (row['who'] in people or set(row['whom'].split(',')) & set(people)):
            add(followup_text(row, names), row['item_id'])
    for r in conn.execute("SELECT id, title, status, ts FROM items WHERE source='linear' AND state='current' AND status != 'Done' "
                          'AND (title LIKE ? OR body LIKE ?) ORDER BY ts DESC LIMIT 4', (f'%{org}%', f'%{org}%')):
        old = conn.execute('SELECT current_fact FROM stale_records WHERE item_id=?', (r['id'],)).fetchone()
        add(f"Open issue: {_clean_title({'title': r['title']})} is {r['status']} (updated {r['ts'][:10]})"
            + (f", out of date: newer information says {old['current_fact']}" if old else ''), r['id'])
    for c in recurring_customer_issues(conn, names):
        if c['customer'].lower() == org.lower():
            ids = [i['id'] for i in sorted(c['items'], key=lambda i: i['ts'])][-2:]
            recurred = ', and a fix that was marked done came back' if c['reopened'] else ''
            add(f"{c['label']} reported again: {len(c['items'])} reports on {c['days']} days across {', '.join(c['sources'])}{recurred}", *ids)
    marks = ','.join('?' * len(people))
    for r in conn.execute(f"SELECT id, title, ts FROM items WHERE kind='email' AND state='current' AND author IN ({marks}) "
                          'ORDER BY ts DESC LIMIT 3', people):
        add(f"Email from them on {r['ts'][:10]}: {r['title']}", r['id'])
    for r in conn.execute("SELECT id, title, status, ts FROM items WHERE kind='deal' AND (title LIKE ? OR body LIKE ?)",
                          (f'%{org}%', f'%{org}%')):
        stale = conn.execute('SELECT current_fact FROM stale_records WHERE item_id=?', (r['id'],)).fetchone()
        add(f"CRM deal '{r['title']}' ({r['status']})" + (f", out of date: newer information says {stale['current_fact']}" if stale else ''), r['id'])
    return facts


GENERIC_QUESTION_WORDS = frozenset('before next call meeting need what know should about with from have'.split())


def collect_facts(conn):
    """All scored facts, without the narrative. Used by the question path"""
    return build_facts(conn, _names(conn))


def schedule_facts(conn, start, end, people=None):
    """One fact per calendar event in the window, in time order. With people,
    only events they are in"""
    names = _names(conn)
    out = []
    for e in day_events(conn, names, start, end):
        item = e['item']
        if people and not set(people) & set(item['people']):
            continue
        notes, ids = (meeting_prep(conn, e, names) if e['upcoming'] else ([], []))
        prep = f". Before it: {'; '.join(notes)}" if notes else ''
        out.append({'score': 0, 'text': event_line(e) + prep, 'ids': [item['id']] + ids, 'cat': 'schedule',
                    'handled': False})
    return out


def blocked_facts(conn, mine_only=False):
    """Every blocked issue, yours first, so a short answer shows what is yours
    and says how many others there are"""
    names = _names(conn)
    rows = [store.row_to_item(r) for r in conn.execute(
        "SELECT * FROM items WHERE source='linear' AND state='current' AND status='Blocked'")]
    mine = sorted((r for r in rows if r['author'] == config.FOUNDER_PERSON_ID), key=_rank)
    others = sorted((r for r in rows if r['author'] != config.FOUNDER_PERSON_ID), key=lambda r: (_rank(r), r['ts']))
    out = []
    for r in mine + ([] if mine_only else others):
        why = re.search(r'blocked by [^.]+', r['body'], re.I)
        owner = 'yours' if r['author'] == config.FOUNDER_PERSON_ID else f"owner {names.get(r['author'], 'unassigned')}"
        out.append({'score': 0, 'text': f"{r['meta']['identifier']} {_clean_title(r)} ({owner}, "
                    f"{PRIORITY_NAMES.get(r['meta']['priority'], 'no priority')}" + (f"; {why.group(0)}" if why else '') + ')',
                    'ids': [r['id']], 'cat': 'blocked', 'handled': False, 'mine': r['author'] == config.FOUNDER_PERSON_ID})
    return out


MEETING_EMAIL_DAYS = 14   # how far back mail counts as being about a meeting
MAX_WORD_DF = 6           # a title word in more emails than this relates nothing


def meeting_email_facts(conn):
    """For each upcoming meeting, the recent emails that relate to it: a reschedule
    email linked by title, or mail from or to an outside guest, or mail sharing a
    distinctive word with the meeting title. Teammate chatter needs the title link
    or a word match, since teammates write to each other about everything"""
    names = _names(conn)
    out = []
    since = _iso(config.NOW - timedelta(days=MEETING_EMAIL_DAYS))
    email_df = {}
    for row in conn.execute("SELECT title, body FROM items WHERE kind='email' AND state='current' AND ts >= ?", (since,)):
        for w in set(re.findall(r'[a-z]{4,}', f"{row['title']} {row['body']}".lower())):
            email_df[w] = email_df.get(w, 0) + 1
    for e in day_events(conn, names, config.NOW, config.NOW + timedelta(days=MEETING_EMAIL_DAYS)):
        if not e['upcoming'] and not e['started']:
            continue
        item = e['item']
        linked = {r['b'] if r['a'] == item['id'] else r['a'] for r in conn.execute(
            "SELECT a, b FROM links WHERE (a=? OR b=?) AND reason='title'", (item['id'], item['id']))}
        # distinctive title words only: 'globex' or 'sync' appear in dozens of emails and
        # relate everything to everything. whole words, so 'board' is not 'dashboard'
        words = [w for w in re.findall(r'[a-z]{4,}', item['title'].lower())
                 if w not in ('meeting', 'review', 'check') and email_df.get(w, 0) <= MAX_WORD_DF]
        guests = [p for p in item['people'] if p != config.FOUNDER_PERSON_ID]
        found = []
        for row in conn.execute("SELECT * FROM items WHERE kind='email' AND state='current' AND ts >= ? AND ts <= ? "
                                'ORDER BY ts DESC', (since, _iso(config.NOW))):
            mail = store.row_to_item(row)
            text = f"{mail['title']} {mail['body']}".lower()
            from_guest = mail['author'] in e['external'] or bool(set(mail['people']) & set(e['external']))
            if mail['id'] in linked or from_guest or any(re.search(rf'\b{w}\b', text) for w in words):
                found.append(mail)
        for mail in found[:3]:
            out.append({'score': 0, 'text': f"Email '{mail['title']}' from {names.get(mail['author'], 'someone')} "
                        f"({mail['ts'][:10]}) relates to {item['title']} on {item['start'][:10]}",
                        'ids': [mail['id'], item['id']], 'cat': 'meeting_email', 'handled': False})
    return out


# ---- narrative --------------------------------------------------------------------

def focus_section(facts):
    """Top facts by score, phrased by the model as action lines. We hand it
    exactly the facts to phrase so it has nothing to rank, and nothing to
    invent a link between: an earlier version given all facts joined two
    unrelated issues in one line"""
    top = [f for f in facts if not f['handled']][:FOCUS_COUNT]
    if not top:
        return '', [], None
    numbered = '\n'.join(f"[{n}] {f['text']}" for n, f in enumerate(top, 1))
    result = llm.chat(FOCUS_SYSTEM, f'Facts:\n{numbered}', max_tokens=260, role='brief')
    labels = {n: f['ids'] for n, f in enumerate(top, 1)}
    cited = []

    def swap(match):
        nums = [int(n) for n in re.split(r'\s*,\s*', match.group(1))]
        ids = [labels[n][0] for n in nums if n in labels]
        cited.extend(ids)
        return ''.join(f'[{i}]' for i in ids)

    # the model likes to open with 'Here is the morning brief'. we only keep
    # the numbered lines
    lines = [l for l in result['text'].strip().splitlines() if re.match(r'\s*\d+\.', l)]
    if len(lines) != len(top):
        # a model that ignored the format (headings, bullets, a title) gets no say:
        # the facts themselves are the numbered lines
        lines = [f"{n}. {f['text']} [{n}]" for n, f in enumerate(top, 1)]
    return answer.CITE_RE.sub(swap, '\n'.join(lines)), cited, result


def generate(conn):
    names = _names(conn)
    facts = build_facts(conn, names)
    focus, cited, llm_result = focus_section(facts)
    today = config.NOW.replace(hour=0, minute=0, second=0, microsecond=0)

    lines = [f"# Morning brief, {config.NOW.strftime('%A %B %d, %Y')}", f"as of {config.NOW.strftime('%H:%M')} UTC", '']
    if focus:
        lines += ['## Focus today', focus, '']

    lines += ['## Today']
    events = day_events(conn, names, today, today + timedelta(days=1))
    if not events:
        lines.append('- nothing on your calendar')
    for e in events:
        notes, ids = meeting_prep(conn, e, names) if e['upcoming'] else ([], [])
        lines.append(f"- {event_line(e)} [{e['item']['id']}]")
        for note, item_id in zip(notes, ids):
            lines.append(f"  - prep: {note} [{item_id}]")

    stale = stale_records(conn)
    changes = recent_decisions(conn)
    lines += ['', '## Plans that changed']
    if not changes and not stale:
        lines.append('- none this week')
    for d in changes:
        cur = d['current']
        line = f"- {d['label']}: {cur['value']} (as of {cur['ts'][:10]}) [{cur['item_id']}]"
        if d['history']:
            line += f"; replaced '{d['history'][-1]['value']}' [{d['history'][-1]['item_id']}]"
        lines.append(line)
    for r in stale:
        fact = f", newer says: {r['fact']}" if r['fact'] else ''
        lines.append(f"  - out of date: {r['title']} ({r['source']}) still says '{r['says']}'{fact}, update it "
                     f"[{r['item_id']}]" + (f" [{r['newer_id']}]" if r['newer_id'] else ''))

    rows = followup_rows(conn)
    open_asks = [r for r in rows if r['kind'] == 'ask' and r['status'] == 'open']
    promises = [r for r in rows if r['kind'] == 'promise' and r['status'] == 'open']
    closed = [r for r in rows if r['kind'] == 'ask' and r['status'] != 'open']
    lines += ['', '## Waiting on you']
    lines += [f"- {followup_text(r, names)} [{r['item_id']}]" for r in sorted(open_asks, key=lambda r: (-_due_bonus(r), r['ts']))] \
        or ['- nothing waiting on you']
    lines += ['', '## You said you would']
    lines += [f"- {followup_text(r, names)} [{r['item_id']}]" for r in promises] or ['- no open promises']
    if closed:
        lines += ['', '## Asked, already handled']
        lines += [f"- {followup_text(r, names)} [{r['item_id']}]" + (f" [{r['evidence']}]" if r['evidence'] else '')
                  for r in closed[:4]]

    blocked = blocked_for_founder(conn)
    lines += ['', '## Blocked on you']
    lines += [f"- {i['meta']['identifier']} {_clean_title(i)}, {PRIORITY_NAMES.get(i['meta']['priority'], 'no priority')} "
              f"[{i['id']}]" for i in blocked] or ['- nothing']

    customers = recurring_customer_issues(conn, names)
    if customers:
        lines += ['', '## Customer issues repeating']
        for c in customers:
            ids = ' '.join(f"[{i['id']}]" for i in sorted(c['items'], key=lambda i: i['ts'])[-3:])
            recurred = ' A fix marked done came back.' if c['reopened'] else ''
            lines.append(f"- {c['customer']}, {c['label']}: {len(c['items'])} reports on {c['days']} days across "
                         f"{', '.join(c['sources'])}.{recurred} {ids}")

    return {'text': '\n'.join(lines) + '\n', 'facts': facts, 'focus_cited': cited,
            'seconds': llm_result['seconds'] if llm_result else 0,
            'prompt_tokens': llm_result['prompt_tokens'] if llm_result else 0,
            'completion_tokens': llm_result['completion_tokens'] if llm_result else 0}
