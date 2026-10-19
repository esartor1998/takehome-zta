"""Source adapters: raw api-shaped rows -> one shared item shape.

An item is a plain dict with these keys:
  id         stable, human-readable, and what answers cite (gmail:<id>, ...)
  source     gmail | calendar | slack | linear
  kind       email | event | message | issue
  thread_key groups items that belong to one conversation or record
  ts         when it happened (iso, utc). events use their start time
  title, body, quoted
  author     person id or None, plus author_how for how we resolved it
  people     person ids involved (recipients, attendees, assignee)
  status     event status or issue state, else ''
  start, end for events
  flags      list of data-quality problems we noticed and handled
"""
import base64
import json
import re
from datetime import datetime, timedelta, timezone

from . import config

CHANNELS = {'C01ENG': '#eng', 'C02PROD': '#product', 'C03GEN': '#general',
            'C04INC': '#incidents', 'C05DES': '#design', 'C06RAND': '#random'}

# a reply quote starts at 'On Mar 6, Priya wrote:' or 'Priya wrote:' and
# everything after it is the quoted tail. we cut there and keep the tail
# separately so we can still tell what a reply was answering
QUOTE_START_RE = re.compile(r'^(?:On .+?,? )?[A-Z][\w. ]+ wrote:\s*$', re.M)
ACME_RE = re.compile(r'\bACME-\d+\b')


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_iso(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def split_quote(body):
    match = QUOTE_START_RE.search(body)
    if not match:
        return body.strip(), ''
    return body[:match.start()].strip(), body[match.start():].strip()


def _read_jsonl(path):
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def gmail_items(raw_dir, ident):
    items = []
    for row in _read_jsonl(raw_dir / 'gmail_messages.jsonl'):
        headers = {h['name']: h['value'] for h in row['payload']['headers']}
        padded = row['payload']['body']['data'] + '=' * (-len(row['payload']['body']['data']) % 4)
        body, quoted = split_quote(base64.urlsafe_b64decode(padded).decode(errors='ignore'))
        ts = datetime.fromtimestamp(int(row['internalDate']) / 1000, tz=timezone.utc)

        author, how = ident.from_email(headers.get('From', ''))
        # a role address or an unknown sender is identified by the signature
        sig = ident.from_signature(body)
        if author is None and sig:
            author, how = sig, 'signature'
        recipients = [r for r in (ident.from_email(a)[0] for a in headers.get('To', '').split(','))
                      if r]
        subject = headers.get('Subject', '')
        items.append({
            'id': f"gmail:{row['id']}", 'source': 'gmail', 'kind': 'email',
            'thread_key': f"gmail:{row['threadId']}", 'ts': _iso(ts),
            'title': subject, 'body': body, 'quoted': quoted,
            'author': author, 'author_how': how, 'people': sorted(set(recipients)),
            'status': '', 'start': '', 'end': '', 'flags': [],
            'meta': {'from': headers.get('From', ''), 'to': headers.get('To', ''),
                     'unread': 'UNREAD' in row.get('labelIds', [])},
        })
    return items


def calendar_items(raw_dir, ident):
    items = []
    for row in _read_jsonl(raw_dir / 'calendar_events.jsonl'):
        start = _parse_iso(row['start']['dateTime'])
        end = _parse_iso(row['end']['dateTime'])
        flags = []
        if end <= start:
            # filler events draw start and end hours independently. an event
            # that ends before it starts would vanish from every time filter,
            # so we assume an hour and say so
            end = start + timedelta(hours=1)
            flags.append('end_before_start_assumed_1h')
        attendees = [ident.from_email(a['email'])[0] for a in row.get('attendees', [])]
        responses = {ident.from_email(a['email'])[0]: a['responseStatus']
                     for a in row.get('attendees', [])}
        organizer = ident.from_email(row['organizer']['email'])[0]
        note = row.get('description', '')
        items.append({
            'id': f"calendar:{row['id']}", 'source': 'calendar', 'kind': 'event',
            'thread_key': f"calendar:{row.get('recurringEventId') or row['id']}",
            'ts': _iso(start), 'title': row['summary'], 'body': note, 'quoted': '',
            'author': organizer, 'author_how': 'directory',
            'people': sorted({a for a in attendees if a}),
            'status': row['status'], 'start': _iso(start), 'end': _iso(end), 'flags': flags,
            'meta': {'responses': responses, 'recurring': row.get('recurringEventId', '')},
        })
    return items


def slack_items(raw_dir, ident):
    items = []
    rows = _read_jsonl(raw_dir / 'slack_messages.jsonl')
    parents = {(r['channel_id'], r['ts']): r for r in rows}
    for row in rows:
        ts = datetime.fromtimestamp(float(row['ts']), tz=timezone.utc)
        channel = CHANNELS.get(row['channel_id'], row['channel_id'])
        thread = row.get('thread_ts')
        flags = []
        if thread and (row['channel_id'], thread) in parents and thread > row['ts']:
            # generator draws reply times independently of the parent. a reply
            # cannot precede its parent, so we flag it instead of trusting ts
            flags.append('reply_before_parent')
        items.append({
            'id': f"slack:{row['channel_id']}:{row['ts']}", 'source': 'slack', 'kind': 'message',
            'thread_key': f"slack:{row['channel_id']}:{thread or row['ts']}",
            'ts': _iso(ts), 'title': channel, 'body': row['text'], 'quoted': '',
            'author': ident.from_slack(row['user']), 'author_how': 'directory',
            'people': [], 'status': '', 'start': '', 'end': '', 'flags': flags,
            'meta': {'channel': channel, 'edited': bool(row.get('edited')),
                     'reactions': sum(r['count'] for r in row.get('reactions', []))},
        })
    return items


def linear_items(raw_dir, ident):
    items = []
    for row in _read_jsonl(raw_dir / 'linear_issues.jsonl'):
        assignee = ident.from_linear(row['assignee']['id']) if row.get('assignee') else None
        updated = _parse_iso(row['updatedAt'])
        items.append({
            # the snapshot time is in the id because several records share one
            # identifier (an audit export). dedupe marks all but the latest
            'id': f"linear:{row['identifier']}@{updated.strftime('%Y%m%dT%H%M')}",
            'source': 'linear', 'kind': 'issue',
            'thread_key': f"linear:{row['identifier']}", 'ts': _iso(updated),
            'title': row['title'], 'body': row['description'], 'quoted': '',
            'author': assignee, 'author_how': 'directory',
            'people': [assignee] if assignee else [],
            'status': row['state']['name'], 'start': '', 'end': '', 'flags': [],
            'meta': {'identifier': row['identifier'], 'priority': row.get('priority'),
                     'labels': [n['name'] for n in row['labels']['nodes']],
                     'created': row['createdAt']},
        })
    return items


def normalize_all(raw_dir, ident):
    items = (gmail_items(raw_dir, ident) + calendar_items(raw_dir, ident)
             + slack_items(raw_dir, ident) + linear_items(raw_dir, ident))
    now = _iso(config.NOW)
    for item in items:
        # filler timestamps run up to 23h past the fixed clock. an item from
        # the future cannot exist yet, so we quarantine it instead of let it
        # show up as 'latest'. events are the exception: scheduled ones are
        # supposed to be in the future
        if item['kind'] != 'event' and item['ts'] > now:
            item['flags'].append('after_now')
    return items
