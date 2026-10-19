"""Identity resolution: map every address, handle and name to one person id.

Sources of truth, in the order we trust them:
  1. the slack, linear and contacts directory exports (exact id or email match)
  2. a unique handle match, like linear 'dkim' matching 'dkim.work@gmail.com'
  3. a signature in the body ('-- Daniel') when the sender is unknown

Every resolution records how it was made, so a wrong merge can be traced.
We never merge on first name alone: 'Alex Chen' and 'Alex C. Morgan' are two
people and a first-name rule folds them together
"""
import json
import re
from dataclasses import dataclass, field

SIGNATURE_RE = re.compile(r'(?:^|\s)(?:--|\u2014|-)\s*([A-Z][a-z]+)\s*$')


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


class IdentityResolver:
    def __init__(self, raw_dir):
        self.people = {}
        self.by_email = {}
        self.by_slack = {}
        self.by_linear = {}
        self.by_handle = {}
        self.shared_inboxes = set()
        self._load(raw_dir)
        self.company_domain = self._company_domain()

    def _load(self, raw_dir):
        contacts = json.loads((raw_dir / 'contacts.json').read_text())
        slack = json.loads((raw_dir / 'slack_users.json').read_text())
        linear = json.loads((raw_dir / 'linear_users.json').read_text())

        # contacts anchor the person list. ids are assigned in file order so
        # they stay stable across runs
        for conn in contacts['connections']:
            pid = conn['resourceName'].split('/')[-1]
            emails = [e['value'].lower() for e in conn['emailAddresses']]
            person = Person(id=pid, name=conn['names'][0]['displayName'],
                            work_email=emails[0], emails=set(emails))
            self.people[pid] = person
            for email in emails:
                self.by_email[email] = pid

        for member in slack['members']:
            pid = self.by_email.get(member['profile']['email'].lower())
            if not pid:
                continue
            self.people[pid].slack_id = member['id']
            self.people[pid].slack_handle = '@' + member['name']
            self.by_slack[member['id']] = pid

        for node in linear['nodes']:
            pid = self.by_email.get(node['email'].lower())
            if not pid:
                continue
            self.people[pid].linear_id = node['id']
            self.people[pid].linear_name = node['name']
            self.by_linear[node['id']] = pid
            self.by_linear[node['name']] = pid
            self.by_handle[node['name'].lower()] = pid

    def _company_domain(self):
        domains = [e.split('@')[1] for e in self.by_email if e in
                   {p.work_email for p in self.people.values()}]
        return max(set(domains), key=domains.count)

    def register_shared_inbox(self, address):
        self.shared_inboxes.add(address.lower())

    # ---- lookups ------------------------------------------------------

    def from_email(self, address):
        """Return (person id or None, how). Display names are stripped first"""
        match = re.search(r'[\w.+-]+@[\w.-]+', address or '')
        if not match:
            return None, 'none'
        email = match.group(0).lower()
        if email in self.shared_inboxes:
            return None, 'shared_inbox'
        if email in self.by_email:
            return self.by_email[email], 'directory'
        # an unknown mailbox on our own domain is a role address (eng-team@),
        # not a person, and the signature inside it is who wrote
        if email.endswith('@' + self.company_domain):
            self.shared_inboxes.add(email)
            return None, 'shared_inbox'
        return self._by_handle_prefix(email)

    def _by_handle_prefix(self, email):
        # 'dkim.work@gmail.com' -> local part starts with the linear handle
        # 'dkim'. we need exactly one hit, otherwise we leave it unresolved
        local = re.split(r'[.+_-]', email.split('@')[0])[0]
        hits = {pid for handle, pid in self.by_handle.items()
                if local == handle or (len(handle) >= 4 and email.split('@')[0].startswith(handle))}
        if len(hits) == 1:
            return hits.pop(), 'handle_match'
        return None, 'unresolved'

    def from_signature(self, body):
        """Resolve by a trailing '-- Name' when the first name is unambiguous"""
        match = SIGNATURE_RE.search(body.strip())
        if not match:
            return None
        first = match.group(1).lower()
        hits = [p.id for p in self.people.values() if p.name.split()[0].lower() == first]
        return hits[0] if len(hits) == 1 else None

    def from_slack(self, user_id):
        return self.by_slack.get(user_id)

    def from_linear(self, user_id):
        return self.by_linear.get(user_id)

    def name(self, pid):
        return self.people[pid].name if pid in self.people else pid
