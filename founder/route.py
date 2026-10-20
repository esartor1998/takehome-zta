"""Understand a vague question before retrieving anything.

Founders do not ask 'what decisions were made in the last seven days'. They ask
'what is on today', 'what is daniel saying', 'anything urgent', 'billing?'. This
turns that into a plan: which kind of answer is wanted, who is meant, and over
what time. It is plain rules on purpose. The rules run before any model call, so
the same question gets the same plan whichever model answers it, and a plan can
be tested without a model at all.

Kinds:
  schedule   what is on the calendar for a day
  followups  what you owe people and what people are waiting on
  focus      what to do first
  catchup    what happened, what changed
  blocked    what is stuck
  person     what someone has been saying or doing
  topic      anything else: search, then answer
"""
import json
import re
from dataclasses import dataclass, field
from datetime import timedelta

from . import config

TWO_LETTER_WORDS = frozenset('am as at be by do go he if in is it me my no of on or so to up us we an ok hi'.split())

# words that carry no topic once the intent is known
FILLER = frozenset("""hey hi hello please pls can could would you tell me give show let us lets
i we my our the a an is are was were be been am do does did to of for on in at with about
what whats who whos how hows where when why any anything something someone going up
saying say says said talking talk doing been new latest lately recent recently now today
tonight tomorrow yesterday week this next last""".split())

# what a question word means. checked in order, first hit wins, so the specific
# forms come before the loose ones
KIND_PATTERNS = (
    ('followups', r"\b(waiting on me|owe|promised?|promises|follow.?ups?|unanswered|haven.?t (?:replied|answered|responded)|"
                  r"need(?:s)? (?:a |my )?(?:reply|response|answer)|who.?s waiting|what am i missing|anything i.?m missing)\b"),
    ('focus', r"\b(urgent|priorit\w+|focus|on fire|needs? (?:my )?attention|most important|first thing|"
              r"what should i (?:do|work)|where do i start)\b"),
    ('decisions', r"\b(decisions?|decided|what was decided|what did we decide)\b"),
    ('catchup', r"\b(catch me up|catch up|what did i miss|what.?s new|any updates?|updates?\??$|brief me|"
                r"recap|what happened|going on|how.?s everything|overview|summar(?:y|ize|ise) (?:my|the|everything|all))\b"),
    ('blocked', r"\b(block(?:ed|ers?)?|stuck|stalled)\b"),
    ('schedule', r"(\bon today\b|\bon tomorrow\b|\bmy day\b|\bagenda\b|\bcalendar\b|\bschedule\b|\bmeetings?\b|"
                 r"\bwhat do i have\b|\bam i free\b|\bwhat.?s on\b|\bwhats on\b|\bany(?:thing)? (?:calls|meetings)\b)"),
)

DECISION_WORDS = frozenset('decision decisions decided decide made make recently were was lately'.split())

# role words and the crm status that marks them
ROLE_WORDS = {'investor': 'investor', 'vc': 'investor', 'candidate': 'candidate', 'recruiter': 'recruiter'}

# one word that stands for a family of words. 'investors' appears nowhere in a
# term sheet email, and embeddings alone are weak on a one-word question
SYNONYMS = {
    'investor': 'investor investors vc fund ventures capital term sheet round seed raise fundraising cap table partner',
    'customer': 'customer customers client escalation renewal contract',
    'hiring': 'hiring hire candidate offer recruiter interview',
    'pricing': 'pricing price seat plan per seat',
    'billing': 'billing invoice payment cutover paymint ledgerly',
    'sso': 'sso okta login redirect auth',
    'roadmap': 'roadmap ship freeze launch release date',
    'runway': 'runway burn cash balance bank',
}


@dataclass
class Plan:
    kind: str
    people: list = field(default_factory=list)       # person ids the question names
    ambiguous: dict = field(default_factory=dict)    # alias -> candidate ids, when one name fits several
    start: object = None
    end: object = None
    day_label: str = ''
    expansions: list = field(default_factory=list)   # extra search words from SYNONYMS
    terms: list = field(default_factory=list)        # topic words left after filler is removed
    group: str = ''                                   # 'investors' when the question names a role, not a person
    mine: bool = False                                # 'I', 'my', 'me' in the question


def normalise(question):
    q = question.lower().strip()
    q = re.sub(r"\bwhat'?s\b", 'what is', q)
    q = re.sub(r"\bwhos\b", 'who is', q)
    q = re.sub(r"\bhows\b", 'how is', q)
    return re.sub(r'\s+', ' ', q)


def day_window(q):
    """(start, end, label) for words like today, or None"""
    today = config.NOW.replace(hour=0, minute=0, second=0, microsecond=0)
    if re.search(r'\btomorrow\b', q):
        return today + timedelta(days=1), today + timedelta(days=2), 'tomorrow'
    if re.search(r'\byesterday\b', q):
        return today - timedelta(days=1), today, 'yesterday'
    if re.search(r'\blast week\b', q):
        return config.WEEK_START - timedelta(days=7), config.WEEK_START, 'last week'
    if re.search(r'\bnext week\b', q):
        return config.WEEK_START + timedelta(days=7), config.WEEK_START + timedelta(days=14), 'next week'
    if re.search(r'\bthis week\b', q):
        return config.WEEK_START, config.NOW, 'this week'
    if re.search(r'\b(today|tonight|this morning|this afternoon)\b', q):
        return today, today + timedelta(days=1), 'today'
    return None


def match_people(conn, q, original=''):
    """Person ids named in the question, and which names were ambiguous.

    A bare first name goes to everyone who has it ('daniel' is Daniel Kim and
    Daniel Foster), nicknames and initials count, and the founder is never
    matched by first name since a founder asking about 'alex' means someone else"""
    hits, ambiguous = [], {}
    rows = [dict(r) for r in conn.execute('SELECT id, name, aliases FROM people')]
    by_alias = {}
    for row in rows:
        for alias in json.loads(row['aliases']):
            if len(alias) >= 2:
                by_alias.setdefault(alias, []).append(row['id'])
    for alias, ids in by_alias.items():
        if not re.search(rf'(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])', q):
            continue
        # two letters is an initial pair ('dk'), unless it is also a word ('am')
        if len(alias) == 2 and alias in TWO_LETTER_WORDS:
            continue
        if alias in ('chen',):
            continue
        if config.FOUNDER_PERSON_ID in ids and len(ids) > 1:
            ids = [i for i in ids if i != config.FOUNDER_PERSON_ID]    # 'alex' is not me
        elif ids == [config.FOUNDER_PERSON_ID] and ' ' not in alias:
            continue          # the founder is 'i' and 'me', not their own first name
        if len(ids) > 1:
            ambiguous[alias] = ids
        hits += ids
    # a full name hit beats a first name hit: 'daniel kim' is only Daniel Kim
    full = [r['id'] for r in rows if r['name'].lower() in q]
    if full:
        hits = full + [h for h in hits if h not in full and not any(
            rows_by_id(rows, h)['name'].split()[0].lower() == rows_by_id(rows, f)['name'].split()[0].lower() for f in full)]
        ambiguous = {a: ids for a, ids in ambiguous.items() if not set(ids) & set(full)}
    return list(dict.fromkeys(hits)), ambiguous


def rows_by_id(rows, pid):
    return next(r for r in rows if r['id'] == pid)


def plan(conn, question):
    q = normalise(question)
    window = day_window(q)
    people, ambiguous = match_people(conn, q, question)
    mine = bool(re.search(r"\b(i|my|me|mine|i have|i am)\b", q))
    kind = 'topic'
    for name, pattern in KIND_PATTERNS:
        if re.search(pattern, q):
            kind = name
            break
    # 'which emails relate to upcoming meetings' asks for mail, not the calendar
    if kind == 'schedule' and re.search(r'\bemails?\b|\bmessages?\b', q):
        kind = 'topic'
    words = re.findall(r"[a-z0-9$][a-z0-9'$-]*", q)
    name_words = {w for p in people for w in re.findall(r'[a-z]+', (rows_by_id(
        [dict(r) for r in conn.execute('SELECT id, name FROM people')], p)['name']).lower())}
    alias_words = {a for ids in ambiguous.values() for a in ()} | set(ambiguous)
    terms = [w for w in words if w not in FILLER and w not in name_words and w not in alias_words and len(w) > 1]

    # 'what decisions were made recently' lists decisions. 'what was the original
    # auth decision' is about one topic, and listing every decision answers it badly
    if kind == 'decisions' and any(t not in DECISION_WORDS for t in terms):
        kind = 'topic'
    # a company name stands for the people we know there. 'what is hooli saying'
    # is about Sam Okafor even though his emails never say 'Hooli'. a bare
    # company name stays a topic question, since a company is more than its contacts
    org_people = []
    if not people:
        for row in conn.execute("SELECT id, org FROM people WHERE org != ''"):
            if any(t == row['org'].lower().split()[0] for t in terms):
                org_people.append(row['id'])
    activity = bool(re.search(r'\b(saying|said|up to|doing|working on|latest from|anything from|hear from)\b', q))

    # a person with nothing else to ask about is a request for their activity.
    # 'what is daniel saying', 'anything from priya', 'dan?'
    if kind == 'topic' and org_people and activity:
        kind = 'person'
    elif kind == 'topic' and not people and not terms and window:
        kind = 'schedule'            # 'tomorrow?' on its own is 'what is on tomorrow'
    elif kind == 'topic' and people and (not terms or window or activity):
        kind = 'person'
    # a role word stands for the people who have it: 'investors' is Jordan and
    # Caroline, 'candidates' is Taylor
    group = ''
    for word, role in ROLE_WORDS.items():
        if any(t.startswith(word) for t in terms) and not people:
            ids = [r['id'] for r in conn.execute('SELECT id FROM people WHERE role=?', (role,))]
            if ids:
                people, group = ids, word.rstrip('s') + 's'
                kind = 'person' if kind == 'topic' else kind
    people = people or org_people
    expansions = []
    for key, words_ in SYNONYMS.items():
        if any(t.startswith(key[:5]) for t in terms):
            expansions += words_.split()
    plan_ = Plan(kind=kind, people=people, ambiguous=ambiguous, group=group, expansions=list(dict.fromkeys(expansions)),
                 terms=terms, mine=mine)
    if window:
        plan_.start, plan_.end, plan_.day_label = window
    elif kind == 'schedule' and people:
        # 'any meetings with investors coming up' looks forward, not at today
        plan_.start, plan_.end, plan_.day_label = config.NOW, config.NOW + timedelta(days=14), 'coming up'
    elif kind == 'schedule':
        today = config.NOW.replace(hour=0, minute=0, second=0, microsecond=0)
        plan_.start, plan_.end, plan_.day_label = today, today + timedelta(days=1), 'today'
    return plan_
