"""Identity resolution: map every address, handle and name to one person id.

Sources of truth, in the order we trust them:
  1. the directory exports: contacts and slack and linear and github and
     notion users for the team, crm contacts for customers and investors
  2. a display name that matches one person (a second address for someone, like
     'Daniel F. <danf.photo@gmail.example>' matching Daniel Foster)
  3. a unique handle match ('dkim.work@gmail.com' against linear handle 'dkim')
  4. a signature in the body ('-- Daniel', or a full name block)

Every resolution records how it was made, so a wrong merge can be traced. We
never merge on first name alone: 'Alex Chen' and 'Alex C. Morgan' are two
people, and 'Daniel Kim' and 'Daniel Foster' are two more. A bare first name in
a question is different: it matches every person who has it, and the caller
decides what to do with the ambiguity
"""
import json
import re
from collections import Counter
from dataclasses import dataclass, field

from .names import NameSense

SIGNATURE_RE = re.compile(r'(?:^|\s)(?:--|—|-)\s*([A-Z][a-z]+)\s*$')

# how a message opens ('Hi Becky,') and how it closes ('-- Dan'). names people call each
# other, which is where nicknames are learned
SALUTATION_RE = re.compile(r'^\W*(?:hi|hey|hello|dear|yo)\s+([A-Za-z]+)\b', re.I)

# a sender is a machine when the local part says so or a bulk header is set
AUTOMATED_LOCAL_RE = re.compile(r'^(no-?reply|notifications?|newsletter|news|billing|receipts?|'
                                r'calendar-notification|alerts?|support|mailer)', re.I)


@dataclass
class Person:
    id: str
    name: str
    work_email: str = ''
    emails: set = field(default_factory=set)
    slack_id: str = ''
    slack_handle: str = ''
    linear_id: str = ''
    linear_name: str = ''
    github_login: str = ''
    notion_id: str = ''
    org: str = ''
    title: str = ''
    role: str = ''           # customer, investor, candidate and so on, for outsiders
    external: bool = False
    nicknames: set = field(default_factory=set)   # learned from the mail (see learn_nicknames), never listed by hand

    @property
    def first(self):
        return self.name.split()[0].lower()

    def aliases(self, nicknames=True):
        """Lowercase names this person goes by in chat. nicknames=False leaves out the learned ones, for
        uses where a nickname that is also a plain word ('mark', 'bill') would link unrelated text"""
        parts = self.name.lower().replace('.', '').split()
        out = {self.name.lower(), parts[0]}
        if nicknames:
            out |= self.nicknames
        if len(parts) > 1:
            out.add(parts[0][0] + parts[-1][0])           # initials like 'dk'
            out.add(f'{parts[0]} {parts[-1]}')
        if self.slack_handle:
            out.add(self.slack_handle.lstrip('@').lower())
        if self.linear_name:
            out.add(self.linear_name.lower())
        return out


def parse_addresses(header):
    """[(display name, address)] from a To, Cc or From header. The stdlib
    parser needs quoted display names and misreads 'ADES, Caroline <x@y>' as two
    addresses. Real exports are not always quoted, so we split on the '>' that
    closes each address instead"""
    out = []
    for chunk in re.split(r'(?<=>)\s*,\s*', (header or '').strip()):
        if '<' in chunk and '>' in chunk:
            display = chunk[:chunk.index('<')].strip().strip('"').strip()
            out.append((display, chunk[chunk.index('<') + 1:chunk.index('>')].strip()))
        else:
            out += [('', a.strip()) for a in chunk.split(',') if '@' in a]
    return out


def resolution_report(items, top=5):
    """How well the people in the export were placed, so a gap shows up at ingest and not as a wrong answer.
    Senders that matched no one, mailboxes shared by a team, and calendar guests that no directory knows
    all drop out of later stages quietly: they have no person id to count, link or ask about"""
    mail = [i for i in items if i['kind'] == 'email']
    how = Counter(i['author_how'] for i in mail)
    unresolved = Counter(i['meta'].get('from', '') for i in mail if i['author_how'] == 'unresolved')
    unknown = Counter(a for i in items if i['kind'] == 'event' for a in i['meta'].get('unknown_attendees', []))
    return {'senders': dict(how), 'unresolved_senders': unresolved.most_common(top),
            'unknown_guests': unknown.most_common(top), 'unknown_guest_total': sum(unknown.values())}


def format_report(report):
    lines = ['senders by how they were placed: ' + ', '.join(f'{n} {k}' for k, n in sorted(report['senders'].items(), key=lambda kv: -kv[1]))]
    if report['unresolved_senders']:
        lines.append('senders no rule could place: ' + '; '.join(f'{a or "(blank)"} x{n}' for a, n in report['unresolved_senders']))
    if report['unknown_guests']:
        lines.append(f"calendar guests in no directory ({report['unknown_guest_total']}): " + '; '.join(f'{a} x{n}' for a, n in report['unknown_guests']))
    return lines


def _read(raw_dir, name, default=None):
    try:
        return json.loads((raw_dir / name).read_text())
    except OSError:
        return default


class IdentityResolver:
    def __init__(self, raw_dir, embed=None):
        self.people = {}
        self.by_email = {}
        self.by_slack = {}
        self.by_linear = {}
        self.by_handle = {}
        self.by_github = {}
        self.by_notion = {}
        self.shared_inboxes = set()
        self._load(raw_dir)
        self.company_domain = self._company_domain()
        self.sense = NameSense({p.first for p in self.people.values()}, embed)

    def _add_email(self, pid, email):
        email = email.lower()
        self.people[pid].emails.add(email)
        self.by_email[email] = pid

    def _load(self, raw_dir):
        contacts = _read(raw_dir, 'contacts.json')
        slack = _read(raw_dir, 'slack_users.json')
        linear = _read(raw_dir, 'linear_users.json')

        # contacts anchor the team. ids come from the file so they stay stable
        for conn in contacts['connections']:
            pid = conn['resourceName'].split('/')[-1]
            emails = [e['value'].lower() for e in conn['emailAddresses']]
            self.people[pid] = Person(id=pid, name=conn['names'][0]['displayName'], work_email=emails[0])
            for email in emails:
                self._add_email(pid, email)

        for member in slack['members']:
            pid = self.by_email.get(member['profile']['email'].lower())
            if pid:
                self.people[pid].slack_id = member['id']
                self.people[pid].slack_handle = '@' + member['name']
                self.by_slack[member['id']] = pid

        for node in linear['nodes']:
            pid = self.by_email.get(node['email'].lower())
            if pid:
                self.people[pid].linear_id = node['id']
                self.people[pid].linear_name = node['name']
                self.by_linear[node['id']] = pid
                self.by_linear[node['name']] = pid
                self.by_handle[node['name'].lower()] = pid

        for user in _read(raw_dir, 'github_users.json', []):
            pid = self.by_email.get(user['email'].lower())
            if pid:
                self.people[pid].github_login = user['login']
                self.by_github[user['login']] = pid

        for user in _read(raw_dir, 'notion_users.json', []):
            pid = self.by_email.get(user['person']['email'].lower())
            if pid:
                self.people[pid].notion_id = user['id']
                self.by_notion[user['id']] = pid

        # outside people from the crm. they get ids too, so a customer and an
        # investor can be asked about by name like a teammate
        for contact in (_read(raw_dir, 'crm_contacts.json', {}) or {}).get('results', []):
            props = contact['properties']
            pid = contact['id']
            self.people[pid] = Person(
                id=pid, name=f"{props['firstname']} {props['lastname']}", work_email=props['email'].lower(),
                org=props.get('company', ''), title=props.get('jobtitle', ''), role=props.get('hs_lead_status', ''),
                external=True)
            self._add_email(pid, props['email'])

    def _company_domain(self):
        domains = [p.work_email.split('@')[1] for p in self.people.values() if not p.external]
        return max(set(domains), key=domains.count)

    def register_shared_inbox(self, address):
        self.shared_inboxes.add(address.lower())

    # ---- lookups ------------------------------------------------------

    @staticmethod
    def _name_tokens(display):
        """'KIM, DANIEL' and 'Daniel Kim' and 'Daniel K.' -> ['daniel', 'kim']"""
        display = display.strip().strip('"')
        if ',' in display:
            last, _, first = display.partition(',')
            display = f'{first} {last}'
        parts = re.findall(r"[A-Za-z][A-Za-z'-]*\.?", display)
        return [p.lower().rstrip('.') for p in parts]

    def _by_display_name(self, display):
        """A display name that points at exactly one person. 'Daniel F.' needs
        the last initial to pick Foster over Kim, and a bare first name never
        resolves, since two Daniels exist"""
        tokens = self._name_tokens(display)
        if len(tokens) < 2:
            return None
        first, last = tokens[0], tokens[-1]
        hits = []
        for person in self.people.values():
            parts = person.name.lower().replace('.', '').split()
            # 'Dan F.' is Daniel Foster: a nickname stands for the first name it shortens. the last
            # name or initial has to agree as well, which is what makes a loose first-name test safe
            if (parts[0] == first or parts[0] in self.sense.resolve(first)) and (parts[-1] == last or (len(last) == 1 and parts[-1][0] == last)):
                hits.append(person.id)
        return hits[0] if len(hits) == 1 else None

    def from_email(self, header_value, automated=False):
        """Return (person id or None, how). Accepts a bare address or a full
        'Name <address>' header value, in any of the styles clients produce"""
        parsed = parse_addresses(header_value)
        display, email = parsed[0] if parsed else ('', '')
        email = email.lower()
        if not email:
            return None, 'none'
        if email in self.shared_inboxes:
            return None, 'shared_inbox'
        if email in self.by_email:
            return self.by_email[email], 'directory'
        local = email.split('@')[0]
        if automated or AUTOMATED_LOCAL_RE.match(local):
            return None, 'automated'
        # an unknown mailbox on our own domain is a role address (eng-team@),
        # not a person, and the signature inside it is who wrote
        if email.endswith('@' + self.company_domain):
            self.shared_inboxes.add(email)
            return None, 'shared_inbox'
        if display:
            pid = self._by_display_name(display)
            if pid:
                return pid, 'display_name'
        return self._by_handle_prefix(email)

    def recipients(self, *header_values):
        """Person ids for every address in To and Cc headers. getaddresses
        handles 'LAST, First <x>' where a plain comma split would not"""
        out = []
        for display, email in (a for v in header_values for a in parse_addresses(v)):
            pid, _ = self.from_email(f'{display} <{email}>')
            if pid:
                out.append(pid)
        return sorted(set(out))

    def _by_handle_prefix(self, email):
        # 'dkim.work@gmail.com' -> local part starts with the linear handle
        # 'dkim'. we need exactly one hit, otherwise we leave it unresolved
        local = re.split(r'[.+_-]', email.split('@')[0])[0]
        hits = {pid for handle, pid in self.by_handle.items()
                if local == handle or (len(handle) >= 4 and email.split('@')[0].startswith(handle))}
        if len(hits) == 1:
            return hits.pop(), 'handle_match'
        return None, 'unresolved'

    def from_signature(self, body, thread_people=(), internal_only=False):
        """Resolve by a trailing full name, or by '-- Name' when that first name points at
        one person. A full name wins, so '- Daniel Foster, Globex' is Foster and not either
        Daniel. A first name is looked up among everyone, outsiders included, because customers
        and investors sign with first names too. When it fits several people the writer has to
        be someone in the conversation (thread_people). A role address on our own domain can
        only be a teammate (internal_only), since nobody outside sends from it"""
        tail = '\n'.join(body.strip().splitlines()[-4:]).lower()
        for person in self.people.values():
            if len(person.name.split()) > 1 and person.name.lower() in tail:
                return person.id
        match = SIGNATURE_RE.search(body.strip())
        if not match:
            return None
        first = match.group(1).lower()
        stands = self.sense.resolve(first)
        hits = [p.id for p in self.people.values()
                if (p.first == first or p.first in stands) and not (internal_only and p.external)]
        if len(hits) == 1:
            return hits[0]
        scoped = [h for h in hits if h in thread_people]
        return scoped[0] if len(scoped) == 1 else None

    def learn_nicknames(self, items):
        """Find the names this team and its contacts use for each other, from the mail itself:
        the first word of display names in headers, how messages open ('Hi Becky,') and how
        they close ('-- Dan'). A word is kept as a nickname only if the name rules in
        names.py tie it to a roster first name. Nothing here is listed in advance"""
        seen = set()
        for item in items:
            if item['kind'] != 'email':
                continue
            for header in (item['meta'].get('from', ''), item['meta'].get('to', ''), item['meta'].get('cc', '')):
                for display, _ in parse_addresses(header):
                    tokens = self._name_tokens(display)
                    if tokens:
                        seen.add(tokens[0])
            lines = item['body'].strip().splitlines()
            if lines and (m := SALUTATION_RE.match(lines[0])):
                seen.add(m.group(1).lower())
            if m := SIGNATURE_RE.search(item['body'].strip()):
                seen.add(m.group(1).lower())
        firsts = {p.first for p in self.people.values()}
        learned = 0
        for token in sorted(seen - firsts):
            for first in self.sense.resolve(token):
                for person in self.people.values():
                    if person.first == first:
                        person.nicknames.add(token)
                        learned += 1
        return learned

    def from_slack(self, user_id):
        return self.by_slack.get(user_id)

    def from_linear(self, user_id):
        return self.by_linear.get(user_id)

    def from_github(self, login):
        return self.by_github.get(login)

    def from_notion(self, user_id):
        return self.by_notion.get(user_id)

    def name(self, pid):
        if pid not in self.people:
            return pid
        person = self.people[pid]
        return f'{person.name} ({person.org})' if person.org else person.name

    def match_name(self, text, nicknames=True):
        """Every person a lowercase name or nickname in text could mean. One
        first name can match several people, which is how a question like 'what
        is daniel saying' learns it is ambiguous"""
        text = text.lower()
        hits = []
        for person in self.people.values():
            for alias in person.aliases(nicknames):
                if len(alias) >= 2 and re.search(rf'(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])', text):
                    hits.append(person.id)
                    break
        return hits
