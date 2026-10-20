"""Second layer of synthetic data: breadth and variance.

The first layer (synthetic_data_generator.py) plants the required cases. This
layer exists because real inboxes are not like that: they have vendors and
newsletters, forwarded and html-only mail, outsiders with two addresses, two
people called Daniel, calendars in other timezones, PRs and docs and CRM deals
that disagree with each other, and requests nobody answered.

It runs after every draw from the first layer, on its own seeded generator, so
ids and content from the first layer do not change. expand() appends to the
raw lists it is given and returns the rows for three new sources: github,
notion and crm, plus their directory exports and an answer key fragment.

Every planted fact below is written into the answer key, because the eval
questions and the benchmark checks are built from it.
"""
import base64
import json
import random
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
X = random.Random(20260317)     # content choices for this layer


def D(month, day, hour=0, minute=0):
    return datetime(2026, month, day, hour, minute, tzinfo=UTC)


def _iso(dt):
    return dt.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def _local_iso(dt, offset_hours):
    """An iso string in another timezone, like a real calendar returns"""
    tz = timezone(timedelta(hours=offset_hours))
    return dt.astimezone(tz).isoformat()


# ---- people outside the company ---------------------------------------------

EXTERNALS = [
    # id, name, work email, other email, org, title, role
    ('X1', 'Daniel Foster', 'd.foster@globex.example', 'danf.photo@gmail.example', 'Globex', 'VP Engineering', 'customer'),
    ('X2', 'Mei Tanaka', 'mei.tanaka@initech.example', None, 'Initech', 'Procurement lead', 'customer'),
    ('X3', 'Jordan Pryce', 'jordan@northwindvc.example', None, 'Northwind Ventures', 'Partner', 'investor'),
    ('X4', 'Caroline Ades', 'caroline@blueharbor.example', None, 'Blue Harbor Capital', 'Principal', 'investor'),
    ('X5', 'Sam Okafor', 'sam.okafor@hooli.example', None, 'Hooli', 'Head of Data', 'customer'),
    ('X6', 'Taylor Brooks', 'taylor.brooks@mailbox.example', None, '', 'Candidate, Senior Backend', 'candidate'),
    ('X7', 'Lena Ortiz', 'lena@talentbridge.example', None, 'TalentBridge', 'Recruiter', 'recruiter'),
]
EXT = {e[0]: dict(id=e[0], name=e[1], email=e[2], alt=e[3], org=e[4], title=e[5], role=e[6])
       for e in EXTERNALS}

GITHUB_LOGINS = {'P1': 'alexchen', 'P2': 'priyan', 'P3': 'mwebb-dev', 'P4': 'sofiar',
                 'P5': 'dkim-eng', 'P6': 'amorgan', 'P7': 'hpark', 'P8': 'ohaddad', 'P9': 'rliu'}

# senders that are machines, not people. a real adapter would key off the
# List-Unsubscribe and Auto-Submitted headers, which we also set
AUTOMATED = {
    'github': ('GitHub', 'notifications@github.example'),
    'linear': ('Linear', 'no-reply@linear.example'),
    'calendar': ('Google Calendar', 'calendar-notification@google.example'),
    'paymint': ('Paymint Billing', 'billing@paymint.example'),
    'news': ('SaaS Weekly', 'news@saasweekly.example'),
    'cloud': ('CloudHost', 'receipts@cloudhost.example'),
}


# ---- human noise ------------------------------------------------------------
# real mail and chat are typed in a hurry. these operators touch only the words a
# person chose: casing, shorthand, a dropped final period, the odd typo, a mobile
# signature. dates, amounts, ids, addresses and the words that carry a decision
# are protected, because a typo in 'Mar 22' would make the question unanswerable
# for a person as well, and that would test nothing
import re as _re
PROTECT = _re.compile(r"(ACME-\d+|#\d+|\$\s?\d[\d,.]*\s?[kKmM]?|\b\d[\d:/.,-]*\b|"
                      r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d+|"
                      r"[\w.+-]+@[\w.-]+|https?://\S+|<@U\w+>|\b[A-Z][a-z]+\b)")
CUE_WORDS = frozenset('decision decided correction corrected reverting reversing reopening cancelled canceled '
                      'rescheduled moved confirmed approved accepted closing cutover freeze ship'.split())
ABBREVIATIONS = {'please': 'pls', 'thanks': 'thx', 'tomorrow': 'tmrw', 'because': 'bc', 'about': 'abt',
                 'before': 'bfr', 'weekend': 'wknd', 'meeting': 'mtg', 'customer': 'cust', 'review': 'rev'}
NOISE_SKIP_THREADS = {'thread_auth_001', 'thread_roadmap_001', 'thread_meeting_001', 'thread_billing_001',
                      'thread_ooo_001'}
NOISE_SKIP_SLACK = ('ACME-142', 'Roadmap:', 'Weekly Product Sync', 'billing migration is blocked on my side',
                    'Confirmed: OAuth')
SIGNOFFS = ('\n\nSent from my iPhone', '\n\nsent from my phone, excuse typos', '\n\nSent from Outlook for Android')
DISCLAIMER = ('\n\nThis message may contain confidential information. If you are not the intended recipient, '
              'please delete it and notify the sender.')


def _typo(word, rng):
    kind = rng.choice(('swap', 'drop', 'double'))
    i = rng.randrange(1, len(word) - 1)
    if kind == 'swap':
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if kind == 'drop':
        return word[:i] + word[i + 1:]
    return word[:i] + word[i] + word[i:]


def humanise(text, rng, typo_rate=0.010, abbr_rate=0.5, external=False):
    """One message, typed in a hurry. Deterministic for a given rng state"""
    out, last = [], 0
    for match in PROTECT.finditer(text):
        chunk = text[last:match.start()]
        out.append(_edit_chunk(chunk, rng, typo_rate, abbr_rate))
        out.append(match.group(0))
        last = match.end()
    out.append(_edit_chunk(text[last:], rng, typo_rate, abbr_rate))
    text = ''.join(out)
    roll = rng.random()
    if roll < 0.20 and text[:1].isupper() and not text.startswith(('Hi ', 'Hello')):
        text = text[0].lower() + text[1:]                 # no capital, typed on a phone
    if rng.random() < 0.20:
        text = _re.sub(r'[.]\s*$', '', text)               # last full stop dropped
    if rng.random() < 0.08:
        text += rng.choice(SIGNOFFS)
    elif external and rng.random() < 0.10:
        text += DISCLAIMER
    return text


def _edit_chunk(chunk, rng, typo_rate, abbr_rate):
    def edit(match):
        word = match.group(0)
        low = word.lower()
        if low in CUE_WORDS:
            return word
        if low in ABBREVIATIONS and rng.random() < abbr_rate:
            return ABBREVIATIONS[low]
        if len(word) >= 5 and word.islower() and rng.random() < typo_rate:
            return _typo(word, rng)
        return word
    return _re.sub(r"[A-Za-z]+", edit, chunk)


def _rewrite_mail(row, fn):
    """Apply fn to the readable text parts of a Gmail row, keeping the encoding"""
    def one(part):
        data = part.get('body', {}).get('data')
        if not data or part.get('mimeType', 'text/plain') != 'text/plain':
            return
        text = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4)).decode()
        part['body']['data'] = base64.urlsafe_b64encode(fn(text).encode()).decode().rstrip('=')
    payload = row['payload']
    if payload.get('parts'):
        for part in payload['parts']:
            one(part)
    else:
        one(payload)
    first = payload['parts'][0] if payload.get('parts') else payload
    data = first.get('body', {}).get('data')
    if data:
        row['snippet'] = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4)).decode()[:120].replace('\n', ' ')


def expand(ctx):
    PEOPLE, hexid = ctx['PEOPLE'], ctx['hex']
    gmail, cal, slack, linear = ctx['gmail_raw'], ctx['cal_raw'], ctx['slack_raw'], ctx['linear_raw']
    random.seed(20260318)       # the first layer's helpers draw from the global rng
    key = {}                    # answer key fragment

    me = PEOPLE['P1']['work']

    def work(pid):
        return PEOPLE[pid]['work']

    # ---- mail helpers -------------------------------------------------------

    def addr(pid_or_ext, style='plain'):
        """An address in one of the header styles real mail uses"""
        if pid_or_ext in PEOPLE:
            name, email = PEOPLE[pid_or_ext]['name'], PEOPLE[pid_or_ext]['work']
        else:
            name, email = EXT[pid_or_ext]['name'], EXT[pid_or_ext]['email']
        first, _, last = name.partition(' ')
        if style == 'name':
            return f'{name} <{email}>'
        if style == 'lastfirst':
            return f'{last.upper()}, {first} <{email}>'
        if style == 'quoted':
            return f'"{name}" <{email}>'
        return email

    def mail(frm, to, subject, body, when, thread, cc=None, style='name', html=False,
             multipart=False, automated=None, labels=None):
        """Append one Gmail users.messages.get (format=full) shaped record"""
        msg_id, headers = hexid(16), [
            {'name': 'From', 'value': frm}, {'name': 'To', 'value': to},
            {'name': 'Subject', 'value': subject},
            {'name': 'Date', 'value': when.strftime('%a, %d %b %Y %H:%M:%S +0000')}]
        if cc:
            headers.append({'name': 'Cc', 'value': cc})
        if automated:
            headers += [{'name': 'Auto-Submitted', 'value': 'auto-generated'},
                        {'name': 'List-Unsubscribe', 'value': '<mailto:unsubscribe@example.invalid>'}]

        def b64(text):
            return base64.urlsafe_b64encode(text.encode()).decode().rstrip('=')

        if html:
            html_body = '<html><body>' + ''.join(
                f'<p>{line}</p>' if line.strip() else '' for line in body.split('\n')) + '</body></html>'
            payload = {'mimeType': 'text/html', 'headers': headers, 'body': {'data': b64(html_body)}}
        elif multipart:
            html_body = '<div>' + '<br>'.join(body.split('\n')) + '</div>'
            payload = {'mimeType': 'multipart/alternative', 'headers': headers, 'body': {'size': 0},
                       'parts': [{'mimeType': 'text/plain', 'body': {'data': b64(body)}},
                                 {'mimeType': 'text/html', 'body': {'data': b64(html_body)}}]}
        else:
            payload = {'mimeType': 'text/plain', 'headers': headers, 'body': {'data': b64(body)}}
        gmail.append({
            'id': msg_id, 'threadId': thread,
            'labelIds': labels or (['INBOX', 'UNREAD'] if random.random() < 0.35 else ['INBOX']),
            'snippet': body[:120].replace('\n', ' '),
            'internalDate': str(int(when.timestamp() * 1000)), 'payload': payload})
        return msg_id

    def quoted(who, when, text, style='gmail'):
        """A quoted tail in the style of the client that wrote it"""
        stamp = when.strftime('%a, %b %-d, %Y at %-I:%M %p')
        if style == 'outlook':
            return (f'\n\nFrom: {who}\nSent: {when.strftime("%A, %B %-d, %Y %-I:%M %p")}\n'
                    f'To: someone\nSubject: Re\n\n{text}')
        if style == 'forward':
            return (f'\n\n---------- Forwarded message ---------\nFrom: {who}\n'
                    f'Date: {stamp}\n\n{text}')
        return f'\n\nOn {stamp} {who} wrote:\n' + '\n'.join('> ' + line for line in text.split('\n'))

    SIG_ALEX = '\n\n--\nAlex Chen\nCEO, Acme Robotics'

    # ---- slack helpers ------------------------------------------------------

    def say(pid, channel, text, when, thread_ts=None, bot=None, reactions=None):
        ts = f'{int(when.timestamp())}.{random.randint(100000, 999999):06d}'
        rec = {'type': 'message', 'channel_id': channel, 'user': PEOPLE[pid]['slack_id'] if pid else None,
               'text': text, 'ts': ts}
        if thread_ts:
            rec['thread_ts'] = thread_ts
        if bot:
            rec['bot_id'] = 'B' + hexid(8).upper()
            rec['username'] = bot
            rec.pop('user')
        if reactions:
            rec['reactions'] = [{'name': n, 'count': c, 'users': []} for n, c in reactions]
        slack.append(rec)
        return rec

    # ---- calendar helpers ---------------------------------------------------

    def event(summary, start, end, people=(), externals=(), status='confirmed', organizer='P1',
              note=None, tz=0, all_day=False, responses=None, location=None, recurring=None, zone=None):
        """Calendar event with an external attendee, another timezone, an
        all-day span or a tentative status, which the first layer has none of"""
        attendees = []
        for pid in people:
            attendees.append({'email': work(pid), 'displayName': PEOPLE[pid]['name'],
                              'responseStatus': (responses or {}).get(pid, 'accepted')})
        for eid in externals:
            attendees.append({'email': EXT[eid]['email'], 'displayName': EXT[eid]['name'],
                              'responseStatus': (responses or {}).get(eid, 'accepted')})
        rec = {'id': hexid(26), 'status': status, 'summary': summary, 'attendees': attendees,
               'organizer': {'email': work(organizer), 'displayName': PEOPLE[organizer]['name']}}
        if all_day:
            rec['start'] = {'date': start.strftime('%Y-%m-%d')}
            rec['end'] = {'date': end.strftime('%Y-%m-%d')}
        else:
            zone = zone or {0: 'UTC', -7: 'America/Los_Angeles', -4: 'America/New_York'}[tz]
            rec['start'] = {'dateTime': _local_iso(start, tz), 'timeZone': zone}
            rec['end'] = {'dateTime': _local_iso(end, tz), 'timeZone': zone}
        if note:
            rec['description'] = note
        if location:
            rec['location'] = location
        if recurring:
            rec['recurringEventId'] = recurring
        cal.append(rec)
        return rec

    # ---- linear helper ------------------------------------------------------

    def issue(identifier, title, desc, state, assignee, updated, created, priority=2, labels=('backend',)):
        linear.append({
            'id': hexid(24), 'identifier': identifier, 'title': title, 'description': desc,
            'state': {'name': state},
            'assignee': {'id': PEOPLE[assignee]['linear_id'], 'name': PEOPLE[assignee]['linear_name']},
            'priority': priority, 'createdAt': _iso(created), 'updatedAt': _iso(updated),
            'labels': {'nodes': [{'name': l} for l in labels]}})

    github, notion, crm = [], [], []

    def pr(number, title, body, author, created, state='open', merged=None, closed=None,
           reviewers=(), repo='acme/api', labels=()):
        """GitHub REST pulls shape, plus the comments we attach as separate rows"""
        row = {'type': 'pull_request', 'number': number, 'title': title, 'body': body,
               'state': 'closed' if (merged or closed) else state,
               'user': {'login': GITHUB_LOGINS[author]}, 'repo': repo,
               'created_at': _iso(created),
               'updated_at': _iso(max(x for x in (created, merged, closed) if x)),
               'merged_at': _iso(merged) if merged else None,
               'closed_at': _iso(merged or closed) if (merged or closed) else None,
               'requested_reviewers': [{'login': GITHUB_LOGINS[r]} for r in reviewers],
               'labels': [{'name': l} for l in labels], 'draft': False,
               'html_url': f'https://github.example/{repo}/pull/{number}'}
        github.append(row)
        return row

    def pr_comment(number, author, body, when, repo='acme/api'):
        github.append({'type': 'issue_comment', 'repo': repo, 'pull_number': number,
                       'user': {'login': GITHUB_LOGINS[author]}, 'body': body,
                       'created_at': _iso(when), 'id': int(hexid(8), 16)})

    def page(title, text, editor, created, edited, parent=''):
        """Notion page shape: title property, plain text blocks, edit times"""
        notion.append({
            'object': 'page', 'id': hexid(32), 'url': f'https://notion.example/{hexid(10)}',
            'created_time': _iso(created), 'last_edited_time': _iso(edited),
            'created_by': {'id': PEOPLE[editor]['notion_id']}, 'last_edited_by': {'id': PEOPLE[editor]['notion_id']},
            'parent': parent, 'properties': {'title': {'title': [{'plain_text': title}]}},
            'blocks': [{'type': 'paragraph', 'text': line} for line in text.split('\n') if line.strip()]})

    def deal(name, amount, stage, close, modified, owner, contact, kind, description=''):
        did = hexid(10)
        crm.append({'type': 'deal', 'id': did, 'properties': {
            'dealname': name, 'amount': str(amount), 'dealstage': stage, 'closedate': _iso(close),
            'createdate': _iso(modified - timedelta(days=30)), 'hs_lastmodifieddate': _iso(modified),
            'dealtype': kind, 'hubspot_owner_email': work(owner), 'description': description},
            'associations': {'contacts': [contact]}})
        return did

    def note(deal_id, body, when, owner):
        crm.append({'type': 'note', 'id': hexid(10), 'properties': {
            'hs_note_body': body, 'hs_timestamp': _iso(when), 'hubspot_owner_email': work(owner)},
            'associations': {'deals': [deal_id]}})

    # notion ids are part of the people directory, not the answer key
    for pid, person in PEOPLE.items():
        person['notion_id'] = 'nu_' + person['slack_id'][1:].lower()

    # ======================================================================
    # scenario 1: fundraising, three records that disagree about the close date
    # ======================================================================
    t0 = 'thread_northwind_001'
    mail(addr('P1', 'name'), addr('X3', 'name'), 'Acme Robotics seed extension - intro',
         'Hi Jordan,\n\nThanks for the intro from Priya. Deck attached. I will send updated cohort '
         'metrics by Friday.' + SIG_ALEX, D(3, 2, 15), t0, cc=work('P2'))
    m2 = mail(addr('X3', 'name'), me, 'Re: Acme Robotics seed extension - intro',
              'Alex, deck is great. Can we do a partner update Tue Mar 17? We would need ARR by cohort '
              'before then. We are at roughly $3M for the extension on a $12M pre.\n\nJordan'
              + quoted('Alex Chen <alex.chen@acmerobotics.com>', D(3, 2, 15),
                       'I will send updated cohort metrics by Friday.'), D(3, 5, 17), t0)
    mail(addr('P1', 'name'), addr('X3', 'name'), 'Re: Acme Robotics seed extension - intro',
         'Sorry Jordan, slipping on the cohort metrics. Will send early next week.' + SIG_ALEX,
         D(3, 6, 20), t0)
    mail(addr('X3', 'name'), me, 'Re: Acme Robotics seed extension - intro',
         'Alex, following up: please send cohort ARR before Tuesday\'s partner meeting. The term sheet '
         'discussion hinges on it. Can you confirm you will get it to us by Monday?\n\nJordan',
         D(3, 13, 16), t0, multipart=True)
    t1 = 'thread_blueharbor_001'
    mail(addr('P1', 'name'), addr('X4', 'name'), 'Blue Harbor x Acme - next steps',
         'Caroline, great chatting. I will send data room access by Mar 10.' + SIG_ALEX, D(2, 24, 18), t1)
    mail(addr('X4', 'name'), me, 'Re: Blue Harbor x Acme - next steps',
         'Thanks Alex, looking forward to data room access.\n\nCaroline Ades | Blue Harbor Capital',
         D(3, 4, 15), t1)
    mail(addr('X4', 'lastfirst'), me, 'Re: Blue Harbor x Acme - next steps',
         'Hi Alex, any update on the data room access? We are keen to keep moving.\n\nCaroline',
         D(3, 12, 14), t1)

    say('P2', 'C07FUND', '<@U01ALEXCHEN> Northwind wants cohort ARR by Mon, can you send? \U0001F64F', D(3, 13, 16, 30))
    say('P2', 'C07FUND', '<@U01ALEXCHEN> can you approve the data room request for Blue Harbor?', D(3, 14, 15))
    say('P2', 'C07FUND', 'Jordan says they cannot close before May 15 because of the partner calendar. '
        'Updating the plan.', D(3, 13, 17), reactions=[('eyes', 2)])
    say('P8', 'C07FUND', 'fwiw ledgerly wants the round closed before we sign anything over 50k', D(3, 11, 19))

    page('Seed extension plan',
         'Target close: Apr 30.\nRaise: $3M extension at $12M pre.\nLead: Northwind Ventures.\n'
         'Backup: Blue Harbor Capital.\nOwner: Priya Nair.', 'P2', D(3, 1, 16), D(3, 12, 16))
    nw = deal('Northwind Ventures - seed extension', 3000000, 'partner meeting', D(3, 31), D(3, 5, 18), 'P1', 'X3',
              'investor', 'Lead candidate for the seed extension')
    bh = deal('Blue Harbor Capital - seed extension', 2000000, 'intro call', D(4, 15), D(2, 24, 18), 'P1', 'X4',
              'investor', 'Backup investor')
    note(nw, 'Jordan: partner update Mar 17, needs ARR by cohort first.', D(3, 5, 18), 'P1')
    note(bh, 'Waiting on data room access from us. No contact since Mar 4.', D(3, 4, 16), 'P1')
    event('Blue Harbor intro call', D(3, 4, 15), D(3, 4, 15, 45), people=('P1', 'P2'), externals=('X4',))
    event('Northwind Ventures partner update', D(3, 17, 15), D(3, 17, 16), people=('P1', 'P2'),
          externals=('X3',), tz=-4, responses={'X3': 'needsAction'})
    key['fundraising'] = {
        'current_close_target': 'May 15 (Slack #fundraising, Mar 13)',
        'stale_records': ['Notion Seed extension plan says Apr 30', 'CRM Northwind deal closedate Mar 31'],
        'owed_by_alex': ['cohort ARR to Jordan Pryce before Tue Mar 17 partner meeting (asked Mar 5 and Mar 13)',
                         'data room access to Caroline Ades promised for Mar 10, asked again Mar 12'],
        'slack_asks_to_alex': ['Mar 13 cohort ARR for Northwind', 'Mar 14 approve Blue Harbor data room request']}

    # ======================================================================
    # scenario 2: Globex SSO keeps coming back, across five sources
    # ======================================================================
    t2 = 'thread_globex_sso_001'
    mail(addr('X1', 'name'), f"{me}, {work('P3')}", 'SSO login loops for our users',
         'Hi Alex, Marcus,\n\nSome of our users get stuck in a redirect loop on SSO login. Started Monday. '
         'Can you take a look?\n\nDaniel Foster\nVP Engineering, Globex', D(3, 3, 16), t2)
    mail(addr('P3', 'name'), addr('X1', 'name'), 'Re: SSO login loops for our users',
         'Daniel, reproduced it, fix is in progress (ACME-431).', D(3, 5, 15), t2, cc=me)
    mail(addr('X1', 'name'), me, 'Re: SSO login loops for our users',
         'Thanks for the fix, looks good on our side.\n\nDaniel', D(3, 10, 18), t2)
    mail('"Daniel F." <danf.photo@gmail.example>', me, 'Re: SSO login loops for our users',
         'It is back. Okta users are looping again. Can you confirm a fix ships before Mar 20? '
         'Our rollout is Mar 23.\n\n- Daniel Foster, Globex', D(3, 12, 17), t2, html=True)
    issue('ACME-431', 'Globex SSO redirect loop', 'Users on Globex SSO get a redirect loop after login.',
          'In Progress', 'P3', D(3, 5, 15), D(3, 3, 17), priority=1, labels=('backend', 'customer'))
    issue('ACME-431', 'Globex SSO redirect loop', 'Fixed in PR 218, waiting on Globex confirmation.',
          'Done', 'P3', D(3, 10, 11), D(3, 3, 17), priority=1, labels=('backend', 'customer'))
    issue('ACME-431', 'Globex SSO redirect loop', 'Recurred for Globex users on Okta. Needs a second fix.',
          'Reopened', 'P3', D(3, 12, 18), D(3, 3, 17), priority=1, labels=('backend', 'customer'))
    say('P3', 'C04INC', 'Globex SSO redirect loop repro\'d, tracking in ACME-431', D(3, 3, 17, 30))
    say('P3', 'C04INC', 'SSO fix merged, PR #218. should be live after deploy', D(3, 10, 11, 30))
    say('P4', 'C04INC', 'globex saying sso loops again \U0001F62C reopening ACME-431', D(3, 12, 18, 15),
        reactions=[('eyes', 3)])
    pr(218, 'fix: SSO redirect loop (ACME-431)', 'Stops the redirect loop by clearing the stale state cookie.',
       'P3', D(3, 6, 10), merged=D(3, 10, 11), reviewers=('P5',), labels=('bugfix', 'customer'))
    pr(231, 'fix: SSO redirect loop for Okta (ACME-431)', 'Second fix for Okta tenants. Review from Alex please.',
       'P3', D(3, 13, 12), reviewers=('P1', 'P5'), labels=('bugfix', 'customer'))
    pr_comment(231, 'P5', 'lgtm on my side, needs Alex for the auth change', D(3, 13, 17))
    event('Globex check-in', D(3, 15, 17, 30), D(3, 15, 18), people=('P1', 'P3'), externals=('X1',),
          tz=-7, location='https://meet.example/globex-checkin',
          note='Customer check-in about SSO and the Mar 23 rollout')
    # hooli: repeating export timeouts
    mail(addr('X5', 'name'), me, 'Export timing out again',
         'Alex, our nightly export timed out again last night. Second time this month.\n\nSam', D(3, 11, 14), 'thread_hooli_001')
    mail(addr('X5', 'quoted'), work('P8'), 'Export timeout',
         'Hi Omar, the export job timed out (504). Can you check?', D(3, 4, 13), 'thread_hooli_002')
    issue('ACME-433', 'Hooli export timeout', 'Exports over 50k rows time out. Blocked by infra change ACME-420.',
          'Blocked', 'P8', D(3, 11, 15), D(3, 4, 15), priority=2, labels=('infra', 'customer'))
    # initech: invoice question, answered
    mail(addr('X2', 'name'), me, 'Invoice INV-2207 question',
         'Hi Alex, INV-2207 shows 40 seats but we bought 35. Could you confirm?\n\nMei Tanaka\nInitech',
         D(3, 9, 15), 'thread_initech_001')
    mail(addr('P1', 'name'), addr('X2', 'name'), 'Re: Invoice INV-2207 question',
         'Hi Mei, you are right, it should be 35 seats. Credit note coming.' + SIG_ALEX, D(3, 10, 16),
         'thread_initech_001')
    key['customers'] = {
        'repeating_issue': 'Globex SSO redirect loop: reported Mar 3, fixed Mar 10 (PR 218), recurred Mar 12 on Okta (ACME-431 reopened, PR 231 open)',
        'open_ask_to_alex': 'Daniel Foster asked Mar 12 for confirmation that the SSO fix ships before Mar 20 (rollout Mar 23)',
        'meeting_today': 'Globex check-in 17:30 UTC today (10:30 PDT) with Daniel Foster',
        'hooli': 'export timeouts twice (Mar 4, Mar 11), ACME-433 blocked by ACME-420',
        'initech': 'invoice INV-2207 seat count, answered by Alex Mar 10'}

    # ======================================================================
    # scenario 3: pricing, a decision changed in a meeting, with stale records
    # ======================================================================
    page('Pricing v3', 'Decision: $49 per seat per month for all customers.\nOwner: Hannah Park.',
         'P7', D(3, 5, 15), D(3, 5, 16))
    say('P7', 'C02PROD', 'thinking $59 for new logos and grandfather existing customers at $49. thoughts?', D(3, 9, 16))
    page('Pricing review notes Mar 11',
         'Attendees: Hannah, Sofia, Priya, Alex.\nDecision: new customers pay $59 per seat, existing customers '
         'stay at $49 (grandfathered).\nOwner: Hannah Park.\nAction: Sofia updates the pricing page.',
         'P7', D(3, 11, 18), D(3, 11, 18))
    mail(addr('P4', 'name'), f"{me}, {work('P7')}, {work('P2')}", 'Pricing page is live',
         'Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.',
         D(3, 13, 19), 'thread_pricing_001', multipart=True)
    issue('ACME-440', 'Update pricing page to $49/seat', 'Change the pricing page to $49 per seat for everyone.',
          'Todo', 'P4', D(3, 6, 15), D(3, 5, 17), priority=3, labels=('frontend',))
    issue('ACME-441', 'Update pricing page to $59/seat for new customers',
          'New customers see $59 per seat, existing stay at $49.', 'Done', 'P4', D(3, 13, 19), D(3, 11, 19),
          priority=2, labels=('frontend',))
    key['pricing'] = {
        'current': '$59 per seat for new customers, $49 for existing customers (grandfathered), decided Mar 11',
        'stale_records': ['Notion Pricing v3 says $49 for all', 'Linear ACME-440 still says $49 for everyone (Todo)']}

    # ======================================================================
    # scenario 4: hiring offer extended, put on hold, candidate gone
    # ======================================================================
    t4 = 'thread_hiring_001'
    mail(addr('P1', 'name'), f"{work('P2')}, {EXT['X7']['email']}", 'Taylor Brooks - offer',
         'Let us extend an offer to Taylor Brooks: $165k plus 0.4%. Lena, please send it over.' + SIG_ALEX,
         D(3, 3, 19), t4)
    mail(addr('P2', 'name'), me, 'Re: Taylor Brooks - offer',
         'Alex, budget freeze until the raise closes. Hold Taylor\'s offer for now.', D(3, 10, 15), t4)
    mail(addr('X7', 'name'), me, 'Re: Taylor Brooks - offer',
         'Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena',
         D(3, 13, 21), t4)
    say('P2', 'C08HIRE', 'holding taylor\'s offer until the raise closes, per budget', D(3, 10, 15, 30))
    page('Hiring - Senior Backend', 'Offer to Taylor Brooks approved at $165k.\nStatus: offer out.',
         'P2', D(3, 3, 20), D(3, 3, 20))
    key['hiring'] = {'current': 'Not hiring Taylor Brooks: offer extended Mar 3, put on hold Mar 10, candidate accepted another offer Mar 13',
                     'stale_records': ['Notion Hiring page says offer out at $165k']}

    # ======================================================================
    # scenario 5: billing cutover date moved, notion still has the old one
    # ======================================================================
    page('Billing migration plan', 'Cutover date: Mar 24.\nVendor: Ledgerly replaces Paymint.\nOwner: Omar Haddad.',
         'P8', D(3, 2, 15), D(3, 2, 15))
    say('P8', 'C01ENG', 'billing cutover moves to Mar 31. daniel is back Mar 16 and we want a week of parallel run',
        D(3, 12, 16))
    mail(addr('P2', 'name'), me, 'FYI billing cutover',
         'Heads up, billing cutover is now Mar 31 (was Mar 24). Omar and Daniel agreed.', D(3, 12, 18),
         'thread_billing_002')
    pr(230, 'billing: webhook retry (ACME-316)', 'Retries failed billing webhooks with backoff.', 'P8',
       D(3, 11, 15), reviewers=('P1',), repo='acme/billing')
    key['billing'] = {'current_cutover': 'Mar 31 (Slack and email Mar 12)',
                      'stale_records': ['Notion Billing migration plan says Mar 24'],
                      'daniel_kim': 'asked Priya to push the migration a week; out of office Mar 10-14, back Mar 16',
                      'review_requested_from_alex': ['acme/billing PR 230 (since Mar 11)', 'acme/api PR 231 (since Mar 13)']}

    # ======================================================================
    # scenario 6: Alex's calendar today and tomorrow, with every messy shape
    # ======================================================================
    event('Standup', D(3, 15, 9, 30), D(3, 15, 9, 45), people=('P1', 'P2', 'P3', 'P4', 'P5'),
          recurring='rec_standup_001')
    event('Investor update prep', D(3, 15, 11), D(3, 15, 11, 45), people=('P1', 'P2'), organizer='P2')
    event('1:1 Marcus', D(3, 15, 15), D(3, 15, 15, 30), people=('P1', 'P3'), status='cancelled', organizer='P3',
          note='Cancelled, Marcus is covering the Globex fix')
    event('Board prep', D(3, 15, 19), D(3, 15, 20), people=('P1', 'P2'), status='tentative', organizer='P2',
          responses={'P1': 'tentative'})
    event('Offsite travel', D(3, 15), D(3, 16), people=('P1', 'P2', 'P3', 'P4', 'P5'), all_day=True,
          note='Flights, see the offsite doc')
    event('Customer escalations review', D(3, 16, 16), D(3, 16, 16, 45), people=('P1', 'P3', 'P4'), organizer='P4',
          tz=0, zone='Europe/London')
    key['calendar'] = {
        'today_for_alex': ['09:30 Standup (done)', '11:00 Investor update prep (done)', '16:00 Weekly Product Sync (moved here from Fri Mar 13)',
                           '17:30 Globex check-in with Daniel Foster', '19:00 Board prep (tentative)', 'all day Offsite travel',
                           '15:00 1:1 Marcus is CANCELLED'],
        'tomorrow_for_alex': ['14:00 Sprint Planning', '16:00 Customer escalations review']}

    # ======================================================================
    # nicknames, a second Daniel, and everyday chatter that refers to people loosely
    # ======================================================================
    say('P3', 'C01ENG', 'dan can you look at the billing webhook retry when you are back?', D(3, 9, 20))
    say('P8', 'C01ENG', 'DK is out till monday so ledgerly questions go to me', D(3, 10, 14))
    say('P2', 'C03GEN', 'danny out thu-fri, ping omar for billing', D(3, 9, 15))
    say('P1', 'C01ENG', 'daniel f from globex is joining the check-in today, be nice \U0001F605', D(3, 15, 12))
    key['people'] = {'daniels': ['Daniel Kim (teammate, @daniel, DK, Dan)', 'Daniel Foster (Globex, customer, also writes from danf.photo@gmail.example)'],
                     'alexes': ['Alex Chen (founder)', 'Alex C. Morgan (a different person)']}

    # ======================================================================
    # github and notion filler, written to look like work and not like the scenarios
    # ======================================================================
    pr_titles = ['chore: bump dependencies', 'refactor: split handler module', 'test: add retry tests',
                 'feat: pagination on list endpoints', 'fix: flaky export test', 'docs: update runbook',
                 'perf: cache warm on boot', 'fix: null check in audit log']
    number = 240
    for _ in range(45):
        author = X.choice([p for p in PEOPLE if p != 'P1'])
        created = D(2, 20) + timedelta(hours=X.randint(0, 24 * 22))
        merged = created + timedelta(hours=X.randint(2, 60)) if X.random() < 0.7 else None
        if merged and merged > ctx['CURRENT_TIME']:
            merged = None
        reviewers = tuple(X.sample([p for p in PEOPLE if p not in (author, 'P1')], 2))
        pr(number, X.choice(pr_titles), 'See the linked issue for context.', author, created, merged=merged,
           reviewers=reviewers, repo=X.choice(['acme/api', 'acme/web', 'acme/billing']))
        if X.random() < 0.4:
            pr_comment(number, X.choice(reviewers), X.choice(['lgtm', 'nit: rename this', 'can you add a test?',
                                                            'approved, ship it']), created + timedelta(hours=3))
        number += 1
    doc_titles = ['Engineering onboarding', 'On-call runbook', 'Q1 OKRs', 'Security review checklist',
                  'Design system notes', 'Data retention policy', 'Release process', 'Postmortem: Feb deploy',
                  'Customer interview notes', 'Hiring rubric', 'Roadmap', 'Meeting notes: weekly sync Mar 6']
    page('Roadmap (Q1)', 'Freeze Mar 10.\nShip Mar 20.\nOwner: Sofia Reyes.', 'P4', D(2, 20, 15), D(3, 1, 15))
    page('Meeting notes: weekly sync Mar 6',
         'Attendees: Alex, Priya, Marcus, Hannah.\nAction: Alex sends cohort ARR to Northwind.\n'
         'Action: Marcus looks at the Globex SSO loop.\nDecision: freeze stays Mar 10.', 'P7', D(3, 6, 17), D(3, 6, 17))
    for title in doc_titles[:10]:
        page(title, 'Draft notes. ' + ' '.join(X.choice(
            ['Owners to confirm.', 'Review next sprint.', 'See the wiki for history.', 'Open questions at the end.',
             'Numbers are approximate.']) for _ in range(4)), X.choice(list(PEOPLE)),
            D(2, 15) + timedelta(hours=X.randint(0, 24 * 25)), D(3, 1) + timedelta(hours=X.randint(0, 24 * 10)))
    key['roadmap_notion'] = 'Notion Roadmap (Q1) still says ship Mar 20, edited Mar 1 before the correction'

    # ======================================================================
    # inbox noise: newsletters, receipts, notifications, forwards, short replies
    # ======================================================================
    news = ['SaaS Weekly #{n}: five metrics founders ignore', 'SaaS Weekly #{n}: the pricing page teardown',
            'SaaS Weekly #{n}: hiring in a downturn']
    for n in range(40):
        when = D(2, 20) + timedelta(hours=X.randint(0, 24 * 23))
        label, sender = AUTOMATED['news']
        mail(f'{label} <{sender}>', me, X.choice(news).format(n=100 + n),
             'This week: benchmarks, a pricing teardown, and three tools we like. Read more on the web. '
             'Unsubscribe at any time.', when, f'thread_news_{n}', automated=True, html=X.random() < 0.6,
             labels=['INBOX', 'CATEGORY_PROMOTIONS'])
    for n in range(14):
        when = D(2, 22) + timedelta(days=2 * n, hours=X.randint(0, 6))
        label, sender = AUTOMATED['cloud']
        mail(f'{label} <{sender}>', me, f'Your CloudHost receipt for February #{n}',
             f'Thanks for your payment of ${X.randint(300, 4000)}.00. Receipt attached. Questions? '
             'Reply to this email.', when, f'thread_receipt_{n}', automated=True)
    for n in range(6):
        label, sender = AUTOMATED['paymint']
        mail(f'{label} <{sender}>', me, f'Paymint invoice INV-{3000 + n}',
             f'Your Paymint invoice is ready. Amount due ${X.randint(900, 2500)}.00. '
             'Your plan renews automatically.', D(2, 25) + timedelta(days=4 * n), f'thread_paymint_{n}', automated=True)
    for p in github:
        if p['type'] == 'pull_request' and p['number'] in (218, 231, 230) or (
                p['type'] == 'pull_request' and X.random() < 0.15):
            label, sender = AUTOMATED['github']
            mail(f'{label} <{sender}>', me, f"[{p['repo']}] {p['title']} (PR #{p['number']})",
                 f"{p['user']['login']} opened a pull request. View it on GitHub.",
                 datetime.fromisoformat(p['created_at'].replace('Z', '+00:00')) + timedelta(minutes=1),
                 f"thread_gh_{p['number']}", automated=True)
    for ident, when in (('ACME-431', D(3, 12, 18, 5)), ('ACME-142', D(3, 14, 22, 5))):
        label, sender = AUTOMATED['linear']
        mail(f'{label} <{sender}>', me, f'{ident} was updated', f'{ident} changed state. Open in Linear.',
             when, f'thread_lin_{ident}', automated=True)
    label, sender = AUTOMATED['calendar']
    for title, when in (('Globex check-in', D(3, 12, 20)), ('Northwind Ventures partner update', D(3, 5, 18, 10)),
                        ('Board prep', D(3, 13, 14))):
        mail(f'{label} <{sender}>', me, f'Invitation: {title}', f'You have been invited to {title}. '
             'Yes, No, Maybe. View all event details.', when, f'thread_invite_{title[:6]}', automated=True)

    # forwarded mail and one-word replies from people
    mail(addr('P2', 'name'), me, 'Fwd: Northwind term sheet template',
         'FYI, standard template from their counsel. Nothing to sign yet.' + quoted(
             'Jordan Pryce <jordan@northwindvc.example>', D(3, 8, 16), 'Attaching our standard term sheet template.',
             style='forward'), D(3, 9, 14), 'thread_fwd_001')
    mail(addr('P3', 'name'), me, 'Re: Globex rollout', 'ok', D(3, 11, 15), 'thread_short_001')
    mail(addr('P4', 'lastfirst'), me, 'Re: pricing', '+1', D(3, 12, 14), 'thread_short_002')
    mail(addr('P5', 'name'), me, 'Re: standup', 'sounds good, thanks!', D(3, 9, 12), 'thread_short_003')
    mail(addr('P7', 'name'), me, 'Re: roadmap review',
         'Alex,\n\nGood sync. A few thoughts:\n- freeze looks fine\n- ship date needs another look after Sofia\'s '
         'correction\n- can we add a risks slide?\n\nThanks,\nHannah' + quoted(
             'Alex Chen <alex.chen@acmerobotics.com>', D(3, 10, 15), 'Sharing the roadmap deck before Thursday.',
             style='outlook'), D(3, 11, 20), 'thread_roadmap_002')

    # ======================================================================
    # extra slack texture: bots, links, typos, emoji, threads
    # ======================================================================
    for n in range(50):
        when = D(2, 22) + timedelta(hours=X.randint(0, 24 * 21))
        if when > ctx['CURRENT_TIME']:
            continue
        who = X.choice([p for p in PEOPLE])
        text = X.choice(['pushed a fix for the flaky test \U0001F64F', 'anyone seen the ci queue? stuck on retries',
                         'lunch?', 'shipping the docs update after standup', 'quick q: who owns the audit log export?',
                         'heads up: deploy at 5pm', 'thx all!', 'reviewing now', 'out for a doctor appt, back at 2',
                         'https://notion.example/runbook has the steps', 'lgtm \U0001F44D', 'ci is red again, looking'])
        say(who, X.choice(['C01ENG', 'C02PROD', 'C03GEN', 'C05DES', 'C06RAND']), text, when)
    for n in range(10):
        when = D(3, 1) + timedelta(hours=X.randint(0, 24 * 14))
        say(None, 'C04INC', f'deploy #{800 + n} finished for acme/api in {X.randint(3, 9)}m', when, bot='deploy-bot')
    # a few more ordinary issues so linear is not all planted
    for n in range(8):
        ident = f'ACME-{450 + n}'
        issue(ident, X.choice(['Cleanup old migrations', 'Add audit log filter', 'Improve error messages',
                               'Speed up CI', 'Document the export API']),
              f'Routine task {ident}.', X.choice(['Todo', 'In Progress', 'Done']),
              X.choice([p for p in PEOPLE if p != 'P1']), D(3, 1) + timedelta(hours=X.randint(0, 24 * 14)),
              D(2, 20), priority=X.choice([0, 3, 4]), labels=(X.choice(['backend', 'frontend', 'infra']),))


    # ======================================================================
    # scenario 7: a renewal whose terms the founder changed with two words
    # ======================================================================
    page('Initech renewal terms', 'Term: 1 year.\nDiscount: 10%.\nOwner: Rebecca Liu.\nStatus: draft sent to legal.',
         'P9', D(3, 3, 16), D(3, 4, 16))
    ren = deal('Initech - renewal', 84000, 'contract sent', D(3, 31), D(3, 4, 17), 'P9', 'X2', 'renewal',
               'Renewal at 1 year, 10 percent discount')
    issue('ACME-460', 'Initech renewal paperwork', 'Prepare 1 year renewal at 10% discount for legal.',
          'Todo', 'P9', D(3, 4, 18), D(3, 4, 17), priority=2, labels=('legal',))
    t7 = 'thread_initech_renew_001'
    mail(addr('X2', 'name'), me, 'renewal q', 'hi alex, legal is asking if we can do 2 yrs w/ 15% off?? lmk\n\nMei',
         D(3, 9, 16), t7)
    mail(addr('P9', 'name'), me, 'Re: renewal q', 'Alex - Initech wants 2yr / 15%. ok by you? need yes/no by thurs so '
         'legal can redline', D(3, 10, 15), t7, cc=work('P2'))
    mail(addr('P1', 'name'), addr('P9', 'name'), 'Re: renewal q', 'ok by me. 2yr 15% fine, go ahead', D(3, 12, 20), t7)
    say('P9', 'C03GEN', 'initech renewal is 2 yr at 15% now, legal redlining', D(3, 13, 15))
    key['initech_renewal'] = {
        'current': '2-year term at 15% discount, approved by Alex on Mar 12 (email), up from 1 year at 10%',
        'stale_records': ['Notion Initech renewal terms (1 year, 10%)', 'CRM Initech renewal deal (1 year, 10%)',
                          'Linear ACME-460 (1 year renewal at 10%)']}

    # ======================================================================
    # scenario 8: a security report promised for tomorrow, with a deadline in slash dates
    # ======================================================================
    t8 = 'thread_hooli_soc2_001'
    mail(addr('X5', 'name'), me, 'SOC 2 report', 'Alex, our security team needs your SOC 2 report before we renew. '
         'can u send by 3/18? thx\n\nSam', D(3, 11, 17), t8)
    mail(addr('P1', 'name'), addr('X5', 'name'), 'Re: SOC 2 report', 'will send the summary tmrw', D(3, 11, 18), t8)
    say('P2', 'C03GEN', 'do we have the soc2 report ready for hooli?', D(3, 12, 15))
    say('P8', 'C03GEN', 'audit report lands 3/20, summary before that is just the pen test exec summary', D(3, 12, 15, 20))
    key['soc2'] = {'ask': 'Sam Okafor (Hooli) wants the SOC 2 report by 3/18 (Mar 18)',
                   'promise': 'Alex told Sam on Mar 11 he would send a summary tomorrow (Mar 12), and nothing shows he did',
                   'fact': 'the audit report lands Mar 20'}

    # ======================================================================
    # scenario 9: an investor update draft answered inline
    # ======================================================================
    t9 = 'thread_investor_update_001'
    mail(addr('P1', 'name'), addr('P2', 'name'), 'Investor update draft', 'draft attached, thoughts?\n\nSection 1: ARR is $1.8M, '
         'up 12% MoM\nSection 2: churn 3%\nSection 3: asks', D(3, 12, 19), t9)
    mail(addr('P2', 'name'), me, 'Re: Investor update draft',
         '\nOn Fri, Mar 13, 2026 at 3:00 PM Alex Chen <alex.chen@acmerobotics.com> wrote:\n'
         '> Section 1: ARR is $1.8M, up 12% MoM\nFine, but say roughly $1.8M, not exact.\n'
         '> Section 2: churn 3%\ncut this slide, Jordan will ask about it live\n'
         '> Section 3: asks\nadd the cohort chart here', D(3, 13, 20), t9)
    key['investor_update'] = {'priya_edits': ['say roughly $1.8M ARR, not exact', 'cut the churn slide',
                                              'add the cohort chart to the asks section']}

    # ======================================================================
    # everyday chatter that could be mistaken for an answer, and duplicates across calendars
    # ======================================================================
    mail(addr('P4', 'name'), me, 'Re: SSO login loops for our users', 'ack', D(3, 12, 18), 'thread_globex_sso_001')
    mail(addr('P2', 'name'), me, 'Re: Northwind term sheet template', '+1', D(3, 9, 15), 'thread_fwd_001')
    for n, when in enumerate((D(3, 10, 14), D(3, 11, 13), D(3, 12, 14), D(3, 13, 13), D(3, 13, 17))):
        target = X.choice(['P2', 'P3', 'P4', 'P7'])
        mail(addr('P5', 'name'), addr(target, 'name'), 'Automatic reply: ' + X.choice(['Standup notes', 'Weekly sync agenda',
             'billing question', 'Re: Deploy checklist']), "I'm out of the office until Mar 16 with limited access. "
             'For billing, contact Priya Nair.', when, f'thread_autoreply_{n}', automated=True)
    event('Northwind <> Acme: partner update', D(3, 17, 15), D(3, 17, 16), people=('P1',), externals=('X3',), tz=-4,
          organizer='P2', responses={'X3': 'accepted'})
    event('sync w/ priya re raise', D(3, 16, 15), D(3, 16, 15, 30), people=('P1', 'P2'), organizer='P2')
    for ident, title, desc, state in (
            ('ACME-470', 'exports r slow again??', 'see slack. same as hooli thing', 'Todo'),
            ('ACME-471', 'fix the thing w/ the audit log', 'priya knows', 'In Progress'),
            ('ACME-472', 'sso cleanup (not the globex one)', 'old okta config', 'Todo'),
            ('ACME-473', 'billing: ledgerly sandbox keys', 'omar has them', 'Done'),
            ('ACME-474', 'docs for api keys??', 'maybe not needed now', 'Todo'),
            ('ACME-475', 'rate limit headers', 'follow up from eng sync', 'In Progress')):
        issue(ident, title, desc, state, X.choice([p for p in PEOPLE if p != 'P1']),
              D(3, 1) + timedelta(hours=X.randint(0, 24 * 14)), D(2, 25), priority=X.choice([0, 3, 4]),
              labels=(X.choice(['backend', 'infra', 'docs']),))
    for text in ('\U0001F44D', 'ty!', 'k', 'lol ok', 'on it', '\U0001F64F', 'same here', 'sgtm', 'nice', 'ack'):
        say(X.choice(list(PEOPLE)), X.choice(['C01ENG', 'C02PROD', 'C03GEN']), text,
            D(3, 5) + timedelta(hours=X.randint(0, 24 * 9)))

    # ======================================================================
    # the noise pass: every message a person typed gets a little human mess
    # ======================================================================
    rng = random.Random(20260319)
    people_emails = {v['work'] for v in PEOPLE.values()}
    for row in gmail:
        headers = {h['name']: h['value'] for h in row['payload']['headers']}
        if row['threadId'] in NOISE_SKIP_THREADS or 'Auto-Submitted' in headers or 'List-Unsubscribe' in headers:
            continue
        if rng.random() < 0.30:
            external = not any(e in headers.get('From', '') for e in people_emails)
            _rewrite_mail(row, lambda text, e=external: humanise(text, rng, external=e))
    for row in slack:
        if row.get('bot_id') or any(k in row['text'] for k in NOISE_SKIP_SLACK) or len(row['text']) < 8:
            continue
        if rng.random() < 0.30:
            row['text'] = humanise(row['text'], rng, typo_rate=0.015)

    contacts = {'results': [
        {'id': e['id'], 'properties': {'firstname': e['name'].split()[0], 'lastname': e['name'].split()[1],
                                        'email': e['email'], 'company': e['org'], 'jobtitle': e['title'],
                                        'hs_lead_status': e['role']}} for e in EXT.values()]}
    return {
        'github': github, 'notion': notion, 'crm': crm,
        'github_users': [{'login': GITHUB_LOGINS[k], 'name': v['name'], 'email': v['work']} for k, v in PEOPLE.items()],
        'notion_users': [{'id': v['notion_id'], 'name': v['name'], 'person': {'email': v['work']}}
                         for v in PEOPLE.values()],
        'crm_contacts': contacts, 'answer_key': key,
        'alt_emails': {e['id']: e['alt'] for e in EXT.values() if e['alt']}}
