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
import html
import json
import re
from datetime import datetime, timedelta, timezone

from . import config
from .identity import parse_addresses

CHANNELS = {'C01ENG': '#eng', 'C02PROD': '#product', 'C03GEN': '#general',
            'C04INC': '#incidents', 'C05DES': '#design', 'C06RAND': '#random',
            'C07FUND': '#fundraising', 'C08HIRE': '#hiring'}
MENTION_RE = re.compile(r'<@(U[A-Z0-9]+)>')

# where the quoted tail of a reply begins, by the client that wrote it:
#   gmail:   'On Tue, Mar 3, 2026 at 3:00 PM Alex <a@x> wrote:' (wrapped or not)
#   short:   'Priya wrote:' (what the first layer of the dataset uses)
#   outlook: a 'From: ... Sent: ...' header block
#   forward: '---------- Forwarded message ---------'
# everything after the marker is the quoted tail. we cut there and keep the tail
# separately, so every later reply in a thread does not match the old decision
QUOTE_STARTS = (
    ('reply', re.compile(r'^On [^\n]{5,160}?(?:\n[^\n]{0,120})?wrote:\s*$', re.M)),
    ('reply', re.compile(r'^(?:On .+?,? )?[A-Z][\w. ]+ wrote:\s*$', re.M)),
    ('reply', re.compile(r'^From: .+\n(?:Sent|Date): ', re.M)),
    ('forward', re.compile(r'^-{3,}\s*Forwarded message\s*-{3,}', re.M)),
)
QUOTED_LINE_RE = re.compile(r'^>', re.M)
HEADER_LINE_RE = re.compile(r'^(?:On .+?,? )?[A-Z][\w. ]+ wrote:\s*$|^On .{5,160}$|^[A-Za-z][\w. ]{0,40}.* wrote:\s*$')
ACME_RE = re.compile(r'\bACME-\d+\b')
AUTOMATED_HEADERS = ('Auto-Submitted', 'List-Unsubscribe')
AUTO_REPLY_SUBJECT_RE = re.compile(r'^\s*(automatic reply|auto-?reply|out of office|undeliverable|delivery status)', re.I)


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_iso(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def split_quote(body):
    """Returns (own text, quoted tail, 'reply' | 'forward' | '').

    Three styles of reply: the header then a quoted block (top posting), a
    quoted block with the writer's answers between its lines (inline), and
    quoted lines with no header at all. Cutting at the first marker is right
    for the first and throws away every answer in the other two, so the lines of
    the tail that are not quoted are kept as the writer's own words"""
    cut, kind = None, ''
    for label, pattern in QUOTE_STARTS:
        match = pattern.search(body)
        if match and (cut is None or match.start() < cut):
            cut, kind = match.start(), label
    if cut is None:
        if not QUOTED_LINE_RE.search(body):
            return body.strip(), '', ''
        own = [l for l in body.splitlines() if not l.startswith('>')]
        return '\n'.join(own).strip(), '\n'.join(l for l in body.splitlines() if l.startswith('>')), 'reply'
    own, tail = body[:cut].strip(), body[cut:].strip()
    if kind == 'reply' and QUOTED_LINE_RE.search(tail):
        inline = [l for l in tail.splitlines()
                  if l.strip() and not l.startswith('>') and not HEADER_LINE_RE.match(l.strip())]
        if inline:
            own = (own + '\n' + '\n'.join(inline)).strip()
    return own, tail, kind


def html_to_text(markup):
    """Enough html handling for mail bodies: paragraph and line breaks become
    newlines, tags are dropped, entities are decoded"""
    text = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>', '\n', markup)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\n{3,}', '\n\n', html.unescape(text)).strip()


def _decode(data):
    return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4)).decode(errors='ignore')


def mail_text(payload):
    """The readable body of a gmail payload. Real messages are often multipart
    with a text part and an html twin, or html only. Prefer the text part"""
    parts = payload.get('parts')
    if parts:
        plain = [p for p in parts if p.get('mimeType') == 'text/plain' and p.get('body', {}).get('data')]
        if plain:
            return _decode(plain[0]['body']['data'])
        rich = [p for p in parts if p.get('mimeType') == 'text/html' and p.get('body', {}).get('data')]
        return html_to_text(_decode(rich[0]['body']['data'])) if rich else ''
    data = payload.get('body', {}).get('data', '')
    if not data:
        return ''
    text = _decode(data)
    return html_to_text(text) if payload.get('mimeType') == 'text/html' else text


def _read_jsonl(path):
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def gmail_items(raw_dir, ident):
    items = []
    for row in _read_jsonl(raw_dir / 'gmail_messages.jsonl'):
        headers = {h['name']: h['value'] for h in row['payload']['headers']}
        body, quoted, quote_kind = split_quote(mail_text(row['payload']))
        ts = datetime.fromtimestamp(int(row['internalDate']) / 1000, tz=timezone.utc)
        automated = any(h in headers for h in AUTOMATED_HEADERS) or bool(AUTO_REPLY_SUBJECT_RE.match(headers.get('Subject', '')))

        author, how = ident.from_email(headers.get('From', ''), automated=automated)
        # a role address or an unknown sender is identified by the signature
        sig = ident.from_signature(body)
        if author is None and sig and how not in ('automated',):
            author, how = sig, 'signature'
        recipients = ident.recipients(headers.get('To', ''), headers.get('Cc', ''))
        parsed_from = parse_addresses(headers.get('From', ''))
        sender_name = (parsed_from[0][0] if parsed_from and parsed_from[0][0] else headers.get('From', ''))
        flags = ['automated'] if automated or how == 'automated' else []
        if quote_kind == 'forward':
            flags.append('forwarded')
        items.append({
            'id': f"gmail:{row['id']}", 'source': 'gmail', 'kind': 'email',
            'thread_key': f"gmail:{row['threadId']}", 'ts': _iso(ts),
            'title': headers.get('Subject', ''), 'body': body, 'quoted': quoted,
            'author': author, 'author_how': how, 'people': recipients,
            'status': '', 'start': '', 'end': '', 'flags': flags,
            'meta': {'from': headers.get('From', ''), 'from_name': sender_name,
                     'to': headers.get('To', ''), 'cc': headers.get('Cc', ''),
                     'unread': 'UNREAD' in row.get('labelIds', []),
                     'labels': row.get('labelIds', [])},
        })
    return items


def _when(block):
    """A calendar start or end: a dateTime with any offset, or an all-day date.
    Returns (utc datetime, original string, all_day)"""
    if 'dateTime' in block:
        return _parse_iso(block['dateTime']), block['dateTime'], False
    return datetime.fromisoformat(block['date']).replace(tzinfo=timezone.utc), block['date'], True


def calendar_items(raw_dir, ident):
    items = []
    for row in _read_jsonl(raw_dir / 'calendar_events.jsonl'):
        start, start_local, all_day = _when(row['start'])
        end, _, _ = _when(row['end'])
        flags = []
        if all_day:
            flags.append('all_day')
        if end <= start:
            # filler events draw start and end hours independently. an event
            # that ends before it starts would vanish from every time filter,
            # so we assume an hour and say so
            end = start + timedelta(hours=1)
            flags.append('end_before_start_assumed_1h')
        attendees = [ident.from_email(a['email'])[0] for a in row.get('attendees', [])]
        responses = {ident.from_email(a['email'])[0]: a['responseStatus']
                     for a in row.get('attendees', []) if ident.from_email(a['email'])[0]}
        organizer = ident.from_email(row['organizer']['email'])[0]
        note = row.get('description', '')
        items.append({
            'id': f"calendar:{row['id']}", 'source': 'calendar', 'kind': 'event',
            'thread_key': f"calendar:{row.get('recurringEventId') or row['id']}",
            'ts': _iso(start), 'title': row['summary'], 'body': note, 'quoted': '',
            'author': organizer, 'author_how': 'directory',
            'people': sorted({a for a in attendees if a}),
            'status': row['status'], 'start': _iso(start), 'end': _iso(end), 'flags': flags,
            'meta': {'responses': responses, 'recurring': row.get('recurringEventId', ''),
                     'time_zone': row['start'].get('timeZone', ''), 'start_local': start_local,
                     'location': row.get('location', '')},
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
        # '<@U01ALEXCHEN>' is unreadable to the model and to full text search
        # we replace it with the name so 'asked Alex' and the mention agree
        text = MENTION_RE.sub(lambda m: '@' + ident.name(ident.from_slack(m.group(1)) or m.group(1)),
                              row['text'])
        if row.get('bot_id'):
            flags.append('bot')
        items.append({
            'id': f"slack:{row['channel_id']}:{row['ts']}", 'source': 'slack', 'kind': 'message',
            'thread_key': f"slack:{row['channel_id']}:{thread or row['ts']}",
            'ts': _iso(ts), 'title': channel, 'body': text, 'quoted': '',
            'author': ident.from_slack(row['user']) if row.get('user') else None,
            'author_how': 'bot' if row.get('bot_id') else 'directory',
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


def github_items(raw_dir, ident):
    items = []
    path = raw_dir / 'github_pulls.jsonl'
    if not path.exists():
        return items
    for row in _read_jsonl(path):
        repo = row['repo']
        if row['type'] == 'pull_request':
            status = 'merged' if row['merged_at'] else ('open' if row['state'] == 'open' else 'closed without merging')
            reviewers = [ident.from_github(r['login']) for r in row['requested_reviewers']]
            items.append({
                'id': f"github:{repo}#{row['number']}", 'source': 'github', 'kind': 'pr',
                'thread_key': f"github:{repo}#{row['number']}", 'ts': row['updated_at'],
                'title': row['title'], 'body': row['body'], 'quoted': '',
                'author': ident.from_github(row['user']['login']), 'author_how': 'directory',
                'people': sorted({r for r in reviewers if r}), 'status': status, 'start': '', 'end': '',
                'flags': [], 'meta': {'repo': repo, 'number': row['number'], 'created': row['created_at'],
                                      'merged_at': row['merged_at'], 'url': row['html_url'],
                                      'labels': [l['name'] for l in row['labels']]}})
        else:
            items.append({
                'id': f"github:{repo}#{row['pull_number']}:c{row['id']}", 'source': 'github', 'kind': 'comment',
                'thread_key': f"github:{repo}#{row['pull_number']}", 'ts': row['created_at'],
                'title': f"comment on PR #{row['pull_number']}", 'body': row['body'], 'quoted': '',
                'author': ident.from_github(row['user']['login']), 'author_how': 'directory',
                'people': [], 'status': '', 'start': '', 'end': '', 'flags': [],
                'meta': {'repo': repo, 'number': row['pull_number']}})
    return items


def notion_items(raw_dir, ident):
    items = []
    path = raw_dir / 'notion_pages.jsonl'
    if not path.exists():
        return items
    for row in _read_jsonl(path):
        title = ''.join(t['plain_text'] for t in row['properties']['title']['title'])
        items.append({
            'id': f"notion:{row['id']}", 'source': 'notion', 'kind': 'doc',
            'thread_key': f"notion:{row['id']}", 'ts': row['last_edited_time'], 'title': title,
            'body': '\n'.join(b['text'] for b in row['blocks']), 'quoted': '',
            'author': ident.from_notion(row['last_edited_by']['id']), 'author_how': 'directory',
            'people': [], 'status': '', 'start': '', 'end': '', 'flags': [],
            'meta': {'created': row['created_time'], 'url': row['url']}})
    return items


def crm_items(raw_dir, ident):
    items, deals = [], {}
    path = raw_dir / 'crm_deals.jsonl'
    if not path.exists():
        return items
    rows = _read_jsonl(path)
    for row in rows:
        if row['type'] != 'deal':
            continue
        props = row['properties']
        deals[row['id']] = props['dealname']
        contacts = row['associations']['contacts']
        owner, _ = ident.from_email(props['hubspot_owner_email'])
        amount = f"${int(float(props['amount'])):,}" if props.get('amount') else 'no amount'
        items.append({
            'id': f"crm:deal:{row['id']}", 'source': 'crm', 'kind': 'deal',
            'thread_key': f"crm:deal:{row['id']}", 'ts': props['hs_lastmodifieddate'],
            'title': props['dealname'],
            'body': (f"Deal stage: {props['dealstage']}. Amount: {amount}. Expected close date: "
                     f"{props['closedate'][:10]}. Type: {props['dealtype']}. {props.get('description', '')}").strip(),
            'quoted': '', 'author': owner, 'author_how': 'directory',
            'people': sorted(c for c in contacts if c in ident.people), 'status': props['dealstage'],
            'start': '', 'end': '', 'flags': [],
            'meta': {'amount': props.get('amount'), 'close_date': props['closedate'],
                     'deal_type': props['dealtype']}})
    for row in rows:
        if row['type'] != 'note':
            continue
        props = row['properties']
        deal_id = row['associations']['deals'][0]
        owner, _ = ident.from_email(props['hubspot_owner_email'])
        items.append({
            'id': f"crm:note:{row['id']}", 'source': 'crm', 'kind': 'note',
            'thread_key': f'crm:deal:{deal_id}', 'ts': props['hs_timestamp'],
            'title': f"CRM note on {deals.get(deal_id, 'a deal')}", 'body': props['hs_note_body'],
            'quoted': '', 'author': owner, 'author_how': 'directory', 'people': [], 'status': '',
            'start': '', 'end': '', 'flags': [], 'meta': {'deal_id': deal_id}})
    return items


def normalize_all(raw_dir, ident):
    items = (gmail_items(raw_dir, ident) + calendar_items(raw_dir, ident)
             + slack_items(raw_dir, ident) + linear_items(raw_dir, ident)
             + github_items(raw_dir, ident) + notion_items(raw_dir, ident) + crm_items(raw_dir, ident))
    now = _iso(config.NOW)
    for item in items:
        # filler timestamps run up to 23h past the fixed clock. an item from
        # the future cannot exist yet, so we quarantine it instead of letting it
        # show up as 'latest'. events are the exception: scheduled ones are
        # supposed to be in the future
        if item['kind'] != 'event' and item['ts'] > now:
            item['flags'].append('after_now')
    return items
