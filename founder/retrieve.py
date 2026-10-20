"""Hybrid retrieval: several cheap pulls fused with reciprocal rank fusion.

Pulls, each returning ranked item ids:
  fts        sqlite fts5 bm25 over title, body and participant names
  vector     chroma nearest neighbours on the query embedding
  structured intent-driven sql: today's meetings, blocked issues, decisions,
             unanswered asks. exact questions get exact answers here, since
             embeddings are weak on dates and status
  person     items written by or sent to a person named in the question

Time is resolved against the fixed clock in config.NOW, never the machine's
"""
import json
import re
from datetime import timedelta

from . import config, llm, route, store

RRF_K = 60            # standard rrf damping constant
PULL_WEIGHTS = {'structured': 3.0, 'fts': 1.0, 'vector': 1.0, 'person': 1.0, 'window': 1.0}
FTS_LIMIT = 30
VECTOR_LIMIT = 30
STOP = frozenset('what which who whom when where how why is are was were do does did the a an '
                 'of to in on at for and or my me i we our about from with this that these those '
                 'have has had any all across any there been be it its show tell give summarize '
                 'summarise should know before next'.split())

# words that say 'decision question' without naming a topic
GENERIC_DECISION_WORDS = frozenset(
    'decision decisions decided current plan recent recently made date changed change latest '
    'status week today'.split())

INTENTS = {
    'meetings': r'\b(meeting|calendar|schedule|sync|on today|call|standup|invite|upcoming)\b',
    'blocked': r'\b(block|blocked|blocker|blockers|stuck)\b',
    'decisions': r'\b(decision|decisions|decided|plan|ship|auth|authentication|freeze|roadmap|reversed|changed)\b',
    'followups': r'\b(follow.?ups?|missing|waiting|unanswered|owe|reply|respond)\b',
    'cancel': r'\b(cancel\w*|resched\w*|moved|postpone\w*)\b',
    'focus': r'\b(focus|priorit\w+|important|urgent|today)\b',
}


def _day_start(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def time_window(question):
    """Return (start, end) datetimes for words like today, or None"""
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
    # vague words (saying, going on, anything) say nothing about the topic

    words = re.findall(r"[A-Za-z0-9][\w'-]*", question)
    return [w for w in words if w.lower() not in STOP and w.lower() not in route.FILLER and len(w) > 1]


def pull_fts(conn, question, window=None):
    """bm25 over title, body and participant names. With a window it only
    looks inside it, which is how 'this week' gets used: as its own pull,
    not as a hard filter on the others. a hard filter dropped the answer to
    'who was out of office' because the email was dated before the week it
    was about"""
    terms = _terms(question)
    if not terms:
        return []
    query = ' OR '.join('"' + t.replace('"', '') + '"' for t in terms)
    sql = ("SELECT i.id FROM items_fts f JOIN items i ON i.rowid = f.rowid "
           "WHERE items_fts MATCH ? AND i.state = 'current' AND i.ts <= ? ")
    args = [query, _iso(config.NOW)]
    if window:
        sql += 'AND i.ts >= ? AND i.ts < ? '
        args += [_iso(window[0]), _iso(window[1])]
    sql += 'ORDER BY bm25(items_fts, 4.0, 1.0, 2.0) LIMIT ?'
    return [r['id'] for r in conn.execute(sql, args + [FTS_LIMIT])]


def pull_vector(conn, question):
    vec = llm.embed([question], kind='query')[0]
    res = store.vector_collection().query(
        query_embeddings=[vec], n_results=VECTOR_LIMIT, where={'state': 'current'})
    ids = res['ids'][0]
    if not ids:
        return []
    marks = ','.join('?' * len(ids))
    rows = {r['id']: r for r in conn.execute(
        f'SELECT id, ts, kind FROM items WHERE id IN ({marks})', ids)}
    return [i for i in ids if rows[i]['kind'] == 'event' or rows[i]['ts'] <= _iso(config.NOW)]


def pull_person(conn, people, question):
    """Items written by a named person, ranked by how well they match the rest
    of the question. Recency alone buried 'what did Rebecca say about Globex'
    under her newer small talk"""
    if not people:
        return []
    marks = ','.join('?' * len(people))
    name_words = {w.lower() for r in conn.execute(f'SELECT name FROM people WHERE id IN ({marks})',
                                                  list(people)) for w in re.findall(r'\w+', r['name'])}
    terms = [t for t in _terms(question) if t.lower() not in name_words and t.lower() not in
             ('say', 'said', 'says', 'tell', 'told', 'mention', 'mentioned')]
    if terms:
        query = ' OR '.join('"' + t.replace('"', '') + '"' for t in terms)
        rows = conn.execute(
            "SELECT i.id FROM items_fts f JOIN items i ON i.rowid = f.rowid "
            f"WHERE items_fts MATCH ? AND i.state='current' AND i.ts <= ? AND i.author IN ({marks}) "
            'ORDER BY bm25(items_fts, 4.0, 1.0, 0.0) LIMIT 20', [query, _iso(config.NOW), *people])
        ranked = [r['id'] for r in rows]
        if ranked:
            return ranked
    rows = conn.execute(
        f"SELECT id FROM items WHERE state='current' AND ts <= ? AND author IN ({marks}) "
        'ORDER BY ts DESC LIMIT 20', [_iso(config.NOW), *people])
    return [r['id'] for r in rows]


ACTIVITY_DAYS = 14        # how far back 'what is X saying' looks
ACTIVITY_PER_PERSON = 6   # items per person, so an ambiguous name shows each candidate
ACTIVITY_KINDS = ('email', 'message', 'comment', 'pr', 'doc', 'note')


def pull_person_activity(conn, people, days=ACTIVITY_DAYS):
    """Recent things written by a person or about them, newest first, one per
    conversation. Several people (an ambiguous first name) are interleaved so
    each gets a fair share before the cut"""
    since = _iso(config.NOW - timedelta(days=days))
    per_person = []
    for pid in people:
        row = conn.execute('SELECT name FROM people WHERE id=?', (pid,)).fetchone()
        rows = conn.execute(
            "SELECT id, thread_key, author, title, body, ts, novelty FROM items WHERE state='current' AND ts >= ? AND ts <= ? "
            f"AND kind IN ({','.join('?' * len(ACTIVITY_KINDS))}) ORDER BY ts DESC", [since, _iso(config.NOW), *ACTIVITY_KINDS])
        seen, picked = set(), []
        for r in rows:
            # a bare first name in text is not enough: everyone says 'daniel'. the
            # author field or the full name has to agree
            if r['author'] != pid and row['name'].lower() not in f"{r['title']} {r['body']}".lower():
                continue
            if r['thread_key'] in seen:
                continue
            seen.add(r['thread_key'])
            picked.append(r)
        # the most distinctive items, shown newest first. recency alone gave a
        # list of template status mail and buried the one message about a deal
        top = sorted(sorted(picked, key=lambda r: -r['novelty'])[:ACTIVITY_PER_PERSON], key=lambda r: r['ts'], reverse=True)
        per_person.append([r['id'] for r in top])
    out = []
    for group in zip(*[p + [None] * (ACTIVITY_PER_PERSON - len(p)) for p in per_person]) if per_person else []:
        out += [i for i in group if i]
    return out


def pull_named_refs(conn, question):
    """Items the question names outright: an issue id like ACME-440 or a PR like
    'PR #231'. An exact reference is the strongest signal there is"""
    ids = []
    for ident in dict.fromkeys(re.findall(r'\bACME-\d+\b', question, re.I)):
        row = conn.execute("SELECT id FROM items WHERE source='linear' AND state='current' AND "
                           "json_extract(meta,'$.identifier')=? COLLATE NOCASE", (ident,)).fetchone()
        if row:
            ids.append(row['id'])
    for number in dict.fromkeys(re.findall(r'(?:\bPR\b|pull request)\s*#?(\d+)', question, re.I)):
        ids += [r['id'] for r in conn.execute("SELECT id FROM items WHERE kind='pr' AND json_extract(meta,'$.number')=?", (int(number),))]
    return ids


def pull_named_events(conn, question):
    """Meetings named in the question, in every state and on every date. This is
    what lets 'was the Friday sync cancelled' see the cancelled Friday event and
    its confirmed replacement together"""
    q = question.lower()
    titles = [r['title'] for r in conn.execute("SELECT DISTINCT title FROM items WHERE kind='event'")
              if len(r['title'].split()) >= 2 and len(r['title']) >= 8 and r['title'].lower() in q]
    if not titles:
        return []
    marks = ','.join('?' * len(titles))
    rows = [dict(r) for r in conn.execute(
        f"SELECT id, start, status, title FROM items WHERE kind='event' AND title IN ({marks}) "
        "AND start >= ? AND start < ? ORDER BY start",
        [*titles, _iso(config.NOW - timedelta(days=21)), _iso(config.NOW + timedelta(days=14))])]
    day = re.search(r'\b(?:mar(?:ch)?)\s+(\d{1,2})\b', q)
    if not day:
        return [r['id'] for r in rows]
    # a named date means that day's events. if one was cancelled, the next
    # confirmed event with the same title is where it went. without this a
    # question about March 13 returned the standup from March 12 as well, and
    # the model answered about the wrong day
    stamp = f"2026-03-{int(day.group(1)):02d}"
    on_day = [r for r in rows if r['start'].startswith(stamp)]
    extra = []
    for r in on_day:
        if r['status'] == 'cancelled':
            extra += [n['id'] for n in rows if n['title'] == r['title'] and n['status'] == 'confirmed'
                      and n['start'] > r['start']][:1]
    return [r['id'] for r in on_day] + extra or [r['id'] for r in rows]


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


def pull_structured(conn, question, intents, window, people, extras=None):
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
        # 'blocked and mine' means owned by whoever the question names, which
        # is the founder for I/my/me
        owner_sql = f" AND author IN ({','.join('?' * len(people))})" if people else ''
        rows = conn.execute(
            "SELECT id FROM items WHERE source='linear' AND state='current' AND status='Blocked'"
            + owner_sql + ' ORDER BY (author = ?) DESC, (json_extract(meta, "$.priority") = 0), '
            'json_extract(meta, "$.priority"), ts DESC LIMIT 15', sorted(people) + [config.FOUNDER_PERSON_ID])
        ids += [r['id'] for r in rows]

    if 'decisions' in intents:
        # current decisions first. when the question names something specific
        # (auth, ship date) only topics that mention it are kept, otherwise a
        # question about the auth decision also dragged the roadmap in and the
        # model mixed the two. a generic 'what was decided' keeps everything
        rows = conn.execute(
            "SELECT d.item_id, d.status, d.topic, i.title, i.body FROM decisions d JOIN items i ON i.id=d.item_id "
            "WHERE d.status IN ('current','stale') ORDER BY (d.status='stale') DESC, d.ts DESC").fetchall()
        words = {t.lower() for t in _terms(question)} - GENERIC_DECISION_WORDS
        if words:
            # score whole topics, not single items. 'Q1 ship date' matches the
            # auth topic on 'ship' alone and the roadmap topic on 'q1' and
            # 'ship', so only the better-covered topic survives
            topic_words = {}
            for r in rows:
                topic_words.setdefault(r['topic'], set()).update(
                    words & set(re.findall(r'[a-z0-9]+', (r['title'] + ' ' + r['body']).lower())))
            best = max((len(w) for w in topic_words.values()), default=0)
            # nothing matches: the question names something that is not a decision
            # topic ('is ACME-440 up to date'), so the decision pull has nothing to add
            # returning every decision here buried the one item the question named
            keep = {t for t, w in topic_words.items() if len(w) == best} if best else set()
            rows = [r for r in rows if r['topic'] in keep]
        ids += [r['item_id'] for r in rows[:12]]
        if extras is not None:
            extras['decision_topics'] = list(dict.fromkeys(r['topic'] for r in rows[:12]))

    if 'followups' in intents:
        ids += [r['id'] for r in conn.execute(
            "SELECT id FROM items WHERE kind='email' AND state='current' AND ts <= ? "
            "AND (body LIKE '%follow up%' OR body LIKE '%by EOD%' OR body LIKE '%?%') "
            'ORDER BY ts DESC LIMIT 15', (now,))]

    seen = set()
    return [i for i in ids if not (i in seen or seen.add(i))]


# ---- fusion ----------------------------------------------------------------

def fuse(pulls, weights=None):
    weights = {**PULL_WEIGHTS, **(weights or {})}
    scores = {}
    for name, ranked in pulls.items():
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + weights[name] / (RRF_K + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def retrieve(conn, question, k=10, plan=None, disable=None, weights=None):
    """disable names pulls to skip and weights overrides their fusion weights, both
    for the ablation tests. by default they come from the FOUNDER_DISABLE setting"""
    disable = set(config.DISABLED_PULLS if disable is None else disable)
    window = time_window(question)
    intents = detect_intents(question)
    people = mentioned_people(conn, question)
    search_text = question
    if plan:
        # the plan already read the question: who is meant (every Daniel, when only a
        # first name was given), which day, and which words stand for a family of words
        people = set(plan.people) | ({config.FOUNDER_PERSON_ID} if plan.mine else set())
        window = (plan.start, plan.end) if plan.start else window
        search_text = question + ' ' + ' '.join(plan.expansions)
        if plan.kind == 'blocked':
            intents.add('blocked')
    extras = {}
    pulls = {
        'fts': [] if 'fts' in disable else pull_fts(conn, search_text),
        'vector': [] if 'vector' in disable else pull_vector(conn, search_text),
        'window': pull_fts(conn, search_text, window) if window and 'window' not in disable else [],
        'person': [] if 'person' in disable else pull_person(conn, people - {config.FOUNDER_PERSON_ID}, question),
        'structured': [] if 'structured' in disable else pull_structured(conn, question, intents, window, people, extras),
    }
    named = pull_named_events(conn, question) if 'structured' not in disable else []
    refs = pull_named_refs(conn, question) if 'structured' not in disable else []
    pulls['structured'] = list(dict.fromkeys(refs + named + pulls['structured']))
    if plan and plan.kind == 'person' and 'structured' not in disable:
        pulls['structured'] = pull_person_activity(conn, [p for p in plan.people])
    ranked = fuse(pulls, weights)

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
        if len(chosen) >= (min(k, len(pulls['structured']) + (0 if 'blocked' in intents or named or refs or (plan and plan.kind == 'person' and not plan.group) else 3)) if pulls['structured'] else k):
            break
    return {'ids': chosen, 'plan_kind': plan.kind if plan else '', 'decision_topics': extras.get('decision_topics', []), 'intents': sorted(intents), 'people': sorted(people),
            'window': window, 'pulls': {n: len(v) for n, v in pulls.items()}}
