"""Hybrid retrieval: several cheap pulls fused with reciprocal rank fusion.

Pulls, each returning ranked item ids:
  fts        sqlite fts5 bm25 over title, body and participant names
  vector     chroma nearest neighbours on the query embedding
  structured intent-driven sql: today's meetings, blocked issues, decisions,
             unanswered asks. exact questions get exact answers here, since
             embeddings are weak on dates and status
  person     items written by or sent to a person named in the question

Time is resolved against the fixed clock in config.NOW, never the machine's.
"""
import json
import re
from datetime import timedelta

from . import config, llm, store

RRF_K = 60            # standard rrf damping constant
PULL_WEIGHTS = {'structured': 3.0, 'fts': 1.0, 'vector': 1.0, 'person': 0.7}
FTS_LIMIT = 30
VECTOR_LIMIT = 30
STOP = frozenset('what which who whom when where how why is are was were do does did the a an '
                 'of to in on at for and or my me i we our about from with this that these those '
                 'have has had any all across any there been be it its show tell give summarize '
                 'summarise should know before next'.split())

INTENTS = {
    'meetings': r'\b(meeting|calendar|schedule|sync|on today|call|standup|invite|upcoming)\b',
    'blocked': r'\b(block|blocked|blocker|blockers|stuck)\b',
    'decisions': r'\b(decision|decisions|decided|current|plan|date|ship|auth|authentication|'
                 r'freeze|roadmap|reversed|changed)\b',
    'followups': r'\b(follow.?ups?|missing|waiting|unanswered|owe|reply|respond)\b',
    'focus': r'\b(focus|priorit\w+|important|urgent|today)\b',
}


def _day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def time_window(question):
    """Return (start, end) datetimes for words like today, or None."""
    q = question.lower()
    today = _day_start(config.NOW)
    if 'tomorrow' in q:
        return today + timedelta(days=1), today + timedelta(days=2)
    if 'yesterday' in q:
        return today - timedelta(days=1), today
    if 'last week' in q:
        return config.WEEK_START - timedelta(days=7), config.WEEK_START
    if 'this week' in q:
        return config.WEEK_START, config.NOW
    if re.search(r'\b(recent|recently|lately)\b', q):
        return config.NOW - timedelta(days=7), config.NOW
    if re.search(r'\b(today|tonight|this morning|this afternoon)\b', q):
        return today, today + timedelta(days=1)
    return None


def detect_intents(question):
    q = question.lower()
    return {name for name, pattern in INTENTS.items() if re.search(pattern, q)}


def _iso(dt):
    return config.iso(dt)


def mentioned_people(conn, question):
    """Person ids named in the question. 'I', 'my' and 'me' mean the founder.

    A bare first name that two people share ('Alex') matches both, and we say
    so in the context header instead of guessing which one was meant"""
    q = question.lower()
    found = set()
    if re.search(r'\b(i|my|me|mine)\b', q):
        found.add(config.FOUNDER_PERSON_ID)
    for row in conn.execute('SELECT id, name, slack_handle, linear_name FROM people'):
        parts = row['name'].lower().replace('.', '').split()
        if row['name'].lower() in q or (len(parts) > 1 and f'{parts[0]} {parts[-1]}' in q):
            found.add(row['id'])
        elif re.search(rf"\b{re.escape(parts[0])}\b", q) and \
                sum(1 for r in conn.execute('SELECT name FROM people')
                    if r['name'].lower().split()[0] == parts[0]) == 1:
            found.add(row['id'])
        elif row['linear_name'] and re.search(rf"\b{re.escape(row['linear_name'])}\b", q):
            found.add(row['id'])
    return found


# ---- pulls ---------------------------------------------------------------

def _terms(question):
    words = re.findall(r"[A-Za-z0-9][\w'-]*", question)
    return [w for w in words if w.lower() not in STOP and len(w) > 1]


def pull_fts(conn, question, window):
    terms = _terms(question)
    if not terms:
        return []
    query = ' OR '.join('"' + t.replace('"', '') + '"' for t in terms)
    sql = ("SELECT i.id FROM items_fts f JOIN items i ON i.rowid = f.rowid "
           "WHERE items_fts MATCH ? AND i.state = 'current' AND i.ts <= ? ")
    args = [query, _iso(config.NOW)]
    if window and window[1] <= config.NOW + timedelta(days=0):
        sql += 'AND i.ts >= ? AND i.ts < ? '
        args += [_iso(window[0]), _iso(window[1])]
    sql += 'ORDER BY bm25(items_fts, 4.0, 1.0, 2.0) LIMIT ?'
    return [r['id'] for r in conn.execute(sql, args + [FTS_LIMIT])]


def pull_vector(conn, question, window):
    vec = llm.embed([question], kind='query')[0]
    res = store.vector_collection().query(
        query_embeddings=[vec], n_results=VECTOR_LIMIT, where={'state': 'current'})
    ids = res['ids'][0]
    if not ids:
        return []
    marks = ','.join('?' * len(ids))
    rows = {r['id']: r for r in conn.execute(
        f'SELECT id, ts, kind FROM items WHERE id IN ({marks})', ids)}
    out = []
    for item_id in ids:
        row = rows[item_id]
        if row['kind'] != 'event' and row['ts'] > _iso(config.NOW):
            continue
        if window and window[1] <= config.NOW and not (_iso(window[0]) <= row['ts'] < _iso(window[1])):
            continue
        out.append(item_id)
    return out


def pull_person(conn, people):
    if not people:
        return []
    marks = ','.join('?' * len(people))
    rows = conn.execute(
        f"SELECT id FROM items WHERE state='current' AND ts <= ? AND author IN ({marks}) "
        'ORDER BY ts DESC LIMIT 20', [_iso(config.NOW), *people])
    return [r['id'] for r in rows]


def meeting_prep(conn, event_id):
    """Items a founder wants open before a meeting: everything linked to the
    event by title (the reschedule email and slack post), then the last two
    weeks of messages that mention the meeting's name"""
    event = conn.execute('SELECT title FROM items WHERE id=?', (event_id,)).fetchone()
    linked = [r['b'] if r['a'] == event_id else r['a'] for r in conn.execute(
        "SELECT a, b FROM links WHERE (a=? OR b=?) AND reason='title'", (event_id, event_id))]
    words = ' OR '.join(f'"{w}"' for w in re.findall(r'[A-Za-z]{4,}', event['title']))
    recent = []
    if words:
        recent = [r['id'] for r in conn.execute(
            "SELECT i.id FROM items_fts f JOIN items i ON i.rowid=f.rowid WHERE items_fts MATCH ? "
            "AND i.state='current' AND i.kind IN ('email','message') AND i.ts <= ? AND i.ts >= ? "
            'ORDER BY bm25(items_fts) LIMIT 6',
            (words, _iso(config.NOW), _iso(config.NOW - timedelta(days=14))))]
    return [i for i in linked if i != event_id] + recent


def pull_structured(conn, question, intents, window, people):
    ids = []
    now = _iso(config.NOW)
    founder = config.FOUNDER_PERSON_ID

    if 'meetings' in intents or 'focus' in intents:
        lo, hi = window or (_day_start(config.NOW), _day_start(config.NOW) + timedelta(days=1))
        if re.search(r'\b(next|before|upcoming)\b', question.lower()) and not window:
            lo, hi = config.NOW, config.NOW + timedelta(days=1)
        events = [r['id'] for r in conn.execute(
            "SELECT id, people FROM items WHERE kind='event' AND start >= ? AND start < ? "
            'ORDER BY start', (_iso(lo), _iso(hi))) if founder in json.loads(r['people'])]
        # cancelled events stay in so the reschedule trail is visible, the
        # renderer labels them. we also pull the twin of any event: same title
        # on another day with status cancelled
        ids += events
        for event_id in events:
            ids += [r['id'] for r in conn.execute(
                "SELECT t.id FROM items e JOIN items t ON t.title = e.title AND t.id != e.id "
                "AND t.kind='event' AND t.status='cancelled' AND t.people = e.people "
                'WHERE e.id = ?', (event_id,))]
        if re.search(r'\b(next|before|prep|upcoming)\b', question.lower()) and events:
            ids += meeting_prep(conn, events[0])

    if 'blocked' in intents:
        rows = conn.execute(
            "SELECT id FROM items WHERE source='linear' AND state='current' AND status='Blocked' "
            'ORDER BY json_extract(meta, "$.priority") IS NULL, json_extract(meta, "$.priority"), ts DESC '
            'LIMIT 15')
        ids += [r['id'] for r in rows]

    if 'decisions' in intents:
        # current decisions first, newest first. topics whose current state
        # came from a retraction rank higher: those are the ones people miss
        rows = conn.execute(
            "SELECT item_id FROM decisions WHERE status IN ('current','stale') "
            "ORDER BY (status='stale') DESC, ts DESC LIMIT 12")
        ids += [r['item_id'] for r in rows]

    if 'followups' in intents:
        ids += [r['id'] for r in conn.execute(
            "SELECT id FROM items WHERE kind='email' AND state='current' AND ts <= ? "
            "AND (body LIKE '%follow up%' OR body LIKE '%by EOD%' OR body LIKE '%?%') "
            'ORDER BY ts DESC LIMIT 15', (now,))]

    seen = set()
    return [i for i in ids if not (i in seen or seen.add(i))]


# ---- fusion ----------------------------------------------------------------

def fuse(pulls):
    scores = {}
    for name, ranked in pulls.items():
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + PULL_WEIGHTS[name] / (RRF_K + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def retrieve(conn, question, k=10):
    window = time_window(question)
    intents = detect_intents(question)
    people = mentioned_people(conn, question)
    pulls = {
        'fts': pull_fts(conn, question, window),
        'vector': pull_vector(conn, question, window),
        'person': pull_person(conn, people - {config.FOUNDER_PERSON_ID}),
        'structured': pull_structured(conn, question, intents, window, people),
    }
    ranked = fuse(pulls)

    # one slot per duplicate group. the canonical copy represents the group and
    # lists where else it was posted, so a repost does not eat the budget
    chosen, groups = [], set()
    for item_id in ranked:
        row = conn.execute('SELECT dup_group FROM items WHERE id=?', (item_id,)).fetchone()
        if row['dup_group']:
            if row['dup_group'] in groups:
                continue
            groups.add(row['dup_group'])
        chosen.append(item_id)
        # when exact structured hits exist the vector and fts tail is mostly
        # noise ('rerunning CI' for a meeting question), so we keep a short tail
        if len(chosen) >= (min(k, len(pulls['structured']) + 3) if pulls['structured'] else k):
            break
    return {'ids': chosen, 'intents': sorted(intents), 'people': sorted(people),
            'window': window, 'pulls': {n: len(v) for n, v in pulls.items()}}
