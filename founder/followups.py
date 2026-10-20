"""Follow-ups: requests made of the founder that nobody has handled, and
promises the founder made that are still open.

Two directions, because a founder drops both:
  asks      someone asked you for something (an email, a slack mention, a PR
            review request) and you have not answered or the work is not done
  promises  you told someone you would do something ('I will send the data room
            access by Mar 10') and nothing since says you did

The model reads the candidate sentence and pulls out what was asked and the
deadline in the sender's words. Everything that decides whether a follow-up is
open is plain code: replies in the same thread, a later state on an issue the
message names, a PR that merged, and deadlines parsed against the message's own
date, so 'by Friday' sent on a Friday means that day
"""
import re
from datetime import datetime, timedelta, timezone

from . import config, llm

ASK_RE = re.compile(r"\b(can you|could you|would you|can u|could u|please|pls|plz|need you|need this|any update|"
                    r"any updates|any chance|wondering if|would you mind|lmk (?:when|by|once)|"
                    r"let me know (?:when|by|once))\b|\?", re.I)
# closers that look like asks or promises and are neither. real mail is full of
# them, and without this every status email became a follow-up
BOILERPLATE_RE = re.compile(
    r'no action needed|let me know if you (?:want|have|need|would like)|follow up if nothing changes|'
    r'for visibility|recommend we ship|rolling forward|if we cannot reproduce', re.I)
PROMISE_RE = re.compile(r"\b(i will|i'll|ill send|will send|will get|will update|will share|let me get|on it|"
                        r"early next week|by (?:mon|tue|wed|thu|fri)\w*|by eod|by tomorrow|by tmrw|"
                        r"sending (?:it )?(?:over )?(?:tmrw|tomorrow|tonight|today))\b", re.I)
WEEKDAYS = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
# how people write them. 'thurs' and 'weds' are everywhere, and a bare 'mon' would also match 'month'
WEEKDAY_FORMS = {'monday': ('monday', 'mon'), 'tuesday': ('tuesday', 'tues', 'tue'),
                 'wednesday': ('wednesday', 'weds', 'wed'), 'thursday': ('thursday', 'thurs', 'thur', 'thu'),
                 'friday': ('friday', 'fri'), 'saturday': ('saturday', 'sat'), 'sunday': ('sunday', 'sun')}
SLASH_DATE_RE = re.compile(r'\b(\d{1,2})/(\d{1,2})\b')
ORDINAL_RE = re.compile(r'\b(?:the )?(\d{1,2})(?:st|nd|rd|th)\b')
MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
DATE_RE = re.compile(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\b', re.I)
MAX_AGE_DAYS = 30         # older than this and a still-open ask is probably dead

SCHEMA = {'type': 'object',
          'properties': {'is_request': {'type': 'boolean'}, 'what': {'type': 'string'},
                         'due': {'type': 'string'}},
          'required': ['is_request', 'what', 'due']}
SYSTEM = (
    'You read one message. Reply with JSON only.\n'
    'is_request = true when the author asks the reader (or promises, if the message is a '
    'promise) to do a specific thing. Greetings, thanks and status updates are false.\n'
    'what: the thing, copied from the message, under 15 words.\n'
    'due: the deadline in the author\'s words, copied from the message (like "by Friday" or '
    '"before Tuesday\'s partner meeting"), or an empty string.')


def parse_due(text, base):
    """A date for a deadline phrase, resolved against when the message was
    sent. Handles prose dates (Mar 20), slash dates (3/20), ordinals (the 20th),
    weekdays and their short forms, tomorrow and tmrw, end of day, week and month.
    Returns an iso date string or ''"""
    low = text.lower()
    match = DATE_RE.search(low)
    if match:
        month = MONTHS.index(match.group(1)[:3]) + 1
        return datetime(base.year, month, int(match.group(2))).strftime('%Y-%m-%d')
    match = SLASH_DATE_RE.search(low)
    if match and 1 <= int(match.group(1)) <= 12 and 1 <= int(match.group(2)) <= 31:
        return datetime(base.year, int(match.group(1)), int(match.group(2))).strftime('%Y-%m-%d')
    match = ORDINAL_RE.search(low)
    if match and 1 <= int(match.group(1)) <= 31:
        day = int(match.group(1))
        month, year = (base.month, base.year) if day >= base.day else ((base.month % 12) + 1, base.year + (base.month == 12))
        try:
            return datetime(year, month, day).strftime('%Y-%m-%d')
        except ValueError:
            pass
    if re.search(r'\b(tomorrow|tmrw|tmr)\b', low):
        return (base + timedelta(days=1)).strftime('%Y-%m-%d')
    if re.search(r'\b(eod|today|end of day|tonight)\b', low):
        return base.strftime('%Y-%m-%d')
    if re.search(r'\b(eow|end of (?:the )?week)\b', low):
        return (base + timedelta(days=(4 - base.weekday()) % 7)).strftime('%Y-%m-%d')
    for name, forms in WEEKDAY_FORMS.items():
        if any(re.search(rf'\b{form}\b', low) for form in forms):
            ahead = (WEEKDAYS.index(name) - base.weekday()) % 7
            return (base + timedelta(days=ahead)).strftime('%Y-%m-%d')
    if re.search(r'early next week|next week', low):
        return (base + timedelta(days=(7 - base.weekday()) % 7 or 7)).strftime('%Y-%m-%d')
    return ''


def _due(due_phrase, body, base):
    """The model's phrase if it gave one, else a 'by' or 'before' phrase in the body"""
    if due_phrase:
        return parse_due(due_phrase, base)
    match = re.search(r'\b(?:by|before)\b[^.?!\n]*', body, re.I)
    return parse_due(match.group(0), base) if match else ''


ACK_ONLY_RE = re.compile(r"^\W*(ok(ay)?|ack|\+1|thanks?|thx|ty|sgtm|lgtm|got it|noted|on it|will do|looks good|nice|same here)\W*$", re.I)
MIN_REPLY_WORDS = 8


def substantive(item):
    """A reply that answers something. 'ack' and '+1' from a teammate in the
    thread do not close an ask made of the founder"""
    return len(item['body'].split()) >= MIN_REPLY_WORDS and not ACK_ONLY_RE.match(item['body'].strip())


def evidence_index(items):
    """Cheap proof that an ask was done without a reply: an issue the message
    names that moved to Done afterwards, or a request to decline an invite for a
    meeting that is now cancelled"""
    done = {i['meta']['identifier']: i for i in items
            if i['source'] == 'linear' and i['state'] == 'current' and i['status'] == 'Done'}
    cancelled = {i['title'].lower(): i for i in items if i['kind'] == 'event' and i['status'] == 'cancelled'}

    def handled_by(item):
        for ref in set(re.findall(r'\bACME-\d+\b', item['body'])):
            if ref in done and done[ref]['ts'] > item['ts']:
                return done[ref]['id']
        if re.search(r'decline the old invite', item['body'], re.I):
            for title, event in cancelled.items():
                if title in item['title'].lower():
                    return event['id']
        return None
    return handled_by


def _ts(item):
    return datetime.fromisoformat(item['ts'].replace('Z', '+00:00'))


def _label(item, text):
    result = llm.chat(SYSTEM, f"from: {item['author']}\nmessage: {text[:500]}", schema=SCHEMA,
                      cache=True, max_tokens=80, role='extract')
    parsed = llm.parse_json(result['text'], None) or {}
    what = parsed.get('what', '').strip()
    low = text.lower()
    # copied text only. a paraphrased task or deadline cannot be parsed or shown honestly
    if what and re.sub(r'\W+', ' ', what.lower()) not in re.sub(r'\W+', ' ', low):
        what = ''
    due = parsed.get('due', '').strip()
    if due and re.sub(r'\W+', ' ', due.lower()) not in re.sub(r'\W+', ' ', low):
        due = ''
    if not what:
        sentence = next((s for s in re.split(r'(?<=[.!?])\s+|\n', text) if ASK_RE.search(s) or PROMISE_RE.search(s)), text)
        what = sentence.strip()[:120]
    return what, due


def find_followups(items, ident):
    """Returns rows for the followups table"""
    handled_by = evidence_index(items)
    founder = config.FOUNDER_PERSON_ID
    founder_name = ident.people[founder].name
    now = config.NOW
    live = [i for i in items if i['state'] == 'current']
    by_thread = {}
    for item in live:
        by_thread.setdefault(item['thread_key'], []).append(item)
    rows = []

    # ---- asks
    for item in live:
        if item['author'] in (None, founder) or item['author'] == '' or _ts(item) < now - timedelta(days=MAX_AGE_DAYS):
            continue
        if item['kind'] == 'pr':
            if founder in item['people'] and item['status'] == 'open':
                rows.append({'item_id': item['id'], 'kind': 'ask', 'who': item['author'], 'whom': founder,
                             'what': f"review {item['meta']['repo']} PR #{item['meta']['number']}: {item['title']}",
                             'due': '', 'status': 'open', 'evidence': '', 'ts': item['ts']})
            continue
        addressed = founder in item['people'] if item['kind'] == 'email' else (
            item['kind'] == 'message' and f'@{founder_name}' in item['body'])
        if not addressed or not ASK_RE.search(item['body']) or 'automated' in item['flags'] \
                or BOILERPLATE_RE.search(item['body']):
            continue
        what, due = _label(item, item['body'])
        later = [m for m in by_thread[item['thread_key']] if m['ts'] > item['ts'] and m['author'] not in (None, item['author'])]
        later_mine = [m for m in later if m['author'] == founder]
        # a teammate answering a thread the founder was copied on closes the ask
        # as well: it was answered, by someone other than the founder
        later_team = [m for m in later if not ident.people[m['author']].external and substantive(m)] if item['kind'] == 'email' else []
        evidence = (later_mine or later_team)[0]['id'] if (later_mine or later_team) else (handled_by(item) or '')
        status = 'replied' if (later_mine or later_team) else ('handled' if evidence else 'open')
        rows.append({'item_id': item['id'], 'kind': 'ask', 'who': item['author'], 'whom': founder,
                     'what': what, 'due': _due(due, item['body'], _ts(item)), 'status': status, 'evidence': evidence, 'ts': item['ts']})

    # ---- promises: only the founder's latest message in each thread counts. an
    # earlier promise was either kept or replaced by a later one
    for thread, group in by_thread.items():
        mine = sorted((m for m in group if m['author'] == founder and m['kind'] in ('email', 'message')),
                      key=lambda m: m['ts'])
        if not mine or _ts(mine[-1]) < now - timedelta(days=MAX_AGE_DAYS):
            continue
        last = mine[-1]
        if not PROMISE_RE.search(last['body']) or BOILERPLATE_RE.search(last['body']):
            continue
        what, due = _label(last, last['body'])
        theirs = [m for m in group if m['author'] not in (None, founder) and m['ts'] > last['ts']]
        recipients = [p for p in last['people'] if p != founder] or ([theirs[0]['author']] if theirs else [])
        rows.append({'item_id': last['id'], 'kind': 'promise', 'who': founder,
                     'whom': ','.join(recipients), 'what': what, 'due': parse_due(due or last['body'], _ts(last)),
                     'status': 'open', 'evidence': '', 'ts': last['ts']})
    return rows


def write_followups(conn, rows):
    for r in rows:
        conn.execute('INSERT INTO followups VALUES (?,?,?,?,?,?,?,?,?)',
                     (r['item_id'], r['kind'], r['who'], r['whom'], r['what'], r['due'], r['status'],
                      r['evidence'], r['ts']))


def is_overdue(row):
    return bool(row['due']) and row['due'] < config.NOW.strftime('%Y-%m-%d') and row['status'] == 'open'
