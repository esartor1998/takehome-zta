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

from . import config, llm
from .names import NameSense

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
    ('followups', r"\b(waiting on me|owe|promised?|promises|follow.?ups?|unanswered|overdue|past due|slipp(?:ed|ing)|haven.?t (?:replied|answered|responded)|"
                  r"need(?:s)? (?:a |my )?(?:reply|response|answer)|who.?s waiting|what am i missing|anything i.?m missing)\b"),
    ('focus', r"\b(urgent|priorit\w+|focus|on fire|needs? (?:my )?attention|most important|first thing|"
              r"what should i (?:do|work)|where do i start)\b"),
    ('decisions', r"\b(decisions?|decided|what was decided|what did we decide)\b"),
    ('prep', r"(\b(before|prep(?:are)? for|ready for|going into|heading into)\b.{0,40}\b(call|meeting|sync|check.?in|chat)\b|"
             r"\bnext (meeting|call)\b|\bmeeting prep\b)"),
    ('catchup', r"\b(catch me up|catch up|what did i miss|what.?s new|any updates|^\s*updates?\??\s*$|brief me|"
                r"recap|what happened|going on|how.?s everything|overview|summar(?:y|ize|ise) (?:my|the|everything|all))\b"),
    ('blocked', r"\b(block(?:ed|ers?)?|stuck|stalled)\b"),
    ('schedule', r"(\bon today\b|\bon tomorrow\b|\bmy day\b|\bagenda\b|\bcalendar\b|\bschedule\b|\bmeetings?\b|"
                 r"\bwhat do i have\b|\bam i free\b|\bwhat.?s on\b|\bwhats on\b|\bany(?:thing)? (?:calls|meetings)\b)"),
)

OVERVIEW_WORDS = frozenset('story deal status update updates news happening going issues issue problems problem about info '
                           'summary overview situation anything account customer'.split())
DECISION_WORDS = frozenset('decision decisions decided decide made make recently were was lately'.split())

# a role word is the crm status of some contacts ('investor', 'candidate', 'recruiter'), read from the people
# table. customers are companies and are asked about by name or as a digest, so they are not a role here
NOT_ROLES = frozenset({'customer'})


@dataclass
class Plan:
    kind: str
    people: list = field(default_factory=list)       # person ids the question names
    ambiguous: dict = field(default_factory=dict)    # alias -> candidate ids, when one name fits several
    start: object = None
    end: object = None
    day_label: str = ''
    expansions: list = field(default_factory=list)   # spellings the inbox holds for a word of the question
    related: list = field(default_factory=list)      # words the glossary built at ingest relates to the question's words
    terms: list = field(default_factory=list)        # topic words left after filler is removed
    group: str = ''                                   # 'investors' when the question names a role, not a person
    fixes: dict = field(default_factory=dict)         # typos corrected in the question, word -> word
    org_people: list = field(default_factory=list)    # the contacts of a company the question names
    orgs: list = field(default_factory=list)          # the company names themselves
    mine: bool = False                                # 'I', 'my', 'me' in the question


_vocab_cache = {}
_glossary_cache = {}


def glossary(conn):
    """term -> words this inbox uses alongside it, built at ingest (glossary.py)"""
    key = conn.execute('PRAGMA database_list').fetchone()[2]
    if key not in _glossary_cache:
        try:
            _glossary_cache[key] = {r['term']: r['related'].split() for r in conn.execute('SELECT term, related FROM glossary')}
        except Exception:
            _glossary_cache[key] = {}
    return _glossary_cache[key]


def vocabulary(conn):
    """Every word in the indexed text with the number of items it appears in,
    read from the fts index. It is what a typo is corrected against, so a
    misspelling of 'northwind' becomes 'northwind' because that is a word this
    inbox contains"""
    key = conn.execute('PRAGMA database_list').fetchone()[2]
    if key not in _vocab_cache:
        try:
            _vocab_cache[key] = {r['term']: r['doc'] for r in conn.execute('SELECT term, doc FROM vocab')}
            # words a founder types that the inbox may never contain
            for word in QUESTION_WORDS:
                _vocab_cache[key].setdefault(word, 50)
        except Exception:
            _vocab_cache[key] = {}
    return _vocab_cache[key]


def _edit_distance_one(a, b):
    """True when a and b differ by one insertion, deletion, substitution or swap"""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        if len(diff) == 1:
            return True
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    i = 0
    while i < len(short) and short[i] == long_[i]:
        i += 1
    return short[i:] == long_[i + 1:]


MIN_FIX_LENGTH = 4     # shorter words are too easy to turn into other words. four letters is allowed
                       # only when the fix is a word the inbox uses often (see MIN_SHORT_FIX_DOC)
MIN_SHORT_FIX_DOC = 4
QUESTION_WORDS = frozenset("""waiting promised promise follow followups unanswered blocked blockers stuck urgent priority
priorities focus decisions decided meeting meetings calendar schedule agenda summary happened investors customers
emails missing saying talking working anything everything yesterday tomorrow today tonight overdue important
attention update updates caught recap overview""".split()) | FILLER
# shorthand that is not a typo
ABBREVIATIONS = {'tdy': 'today', 'tday': 'today', 'tmrw': 'tomorrow', 'tmr': 'tomorrow', 'tmrrw': 'tomorrow',
                 'yday': 'yesterday', 'mtg': 'meeting', 'mtgs': 'meetings', 'wk': 'week', 'prio': 'priority',
                 'prios': 'priorities', 'eod': 'today', 'abt': 'about', 'w/': 'with', 'pls': 'please'}


def near_words(vocab, word, limit=3):
    """Corpus words one edit away from word, most common first"""
    if len(word) < MIN_FIX_LENGTH:
        return []
    close = [(n, w) for w, n in vocab.items() if _edit_distance_one(word, w)
             and (len(word) > MIN_FIX_LENGTH or n >= MIN_SHORT_FIX_DOC)]
    return [w for n, w in sorted(close, reverse=True)[:limit]]


def fix_typos(q, vocab, keep=()):
    """Replace words the inbox has never seen with the nearest word it has. The
    founder types fast: 'whats daniel sayin', 'anyting from investers'. Words in
    keep are left alone, and a word already in the vocabulary is never touched"""
    fixed = {}

    def swap(match):
        word = match.group(0)
        if len(word) < MIN_FIX_LENGTH or word in vocab or word in FILLER or word in keep or not word.isalpha():
            return word
        close = near_words(vocab, word, 1)
        if close:
            fixed[word] = close[0]
            return close[0]
        return word

    return (re.sub(r"[a-z]+", swap, q) if vocab else q), fixed


def normalise(question):
    q = question.lower().strip()
    q = re.sub(r"\bwhat'?s\b", 'what is', q)
    q = re.sub(r"\bwhos\b", 'who is', q)
    q = re.sub(r"\bhows\b", 'how is', q)
    q = re.sub(r'\s+', ' ', q)
    return re.sub(r"[a-z/]+", lambda m: ABBREVIATIONS.get(m.group(0), m.group(0)), q)


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


RARE_WORD_DOCS = 5      # a word in fewer items than this may be a name the mail never used
_sense_cache = {}


def unseen_nicknames(conn, q, vocab, known):
    """Person ids for words that look like a nickname the inbox has never used ('bex', 'liz'). The
    ones the mail does use were learned at ingest and are already aliases. The same name rules
    apply (names.py), and only rare words are tried, so 'mar' in 'mar 20' is left alone"""
    key = conn.execute('PRAGMA database_list').fetchone()[2]
    if key not in _sense_cache:
        rows = [dict(r) for r in conn.execute('SELECT id, name FROM people')]
        _sense_cache[key] = (NameSense({r['name'].split()[0].lower() for r in rows}, llm.embed), rows)
    sense, rows = _sense_cache[key]
    hits = {}
    for word in dict.fromkeys(re.findall(r'[a-z]{3,}', q)):
        if word in known or word in FILLER or word in QUESTION_WORDS or vocab.get(word, 0) >= RARE_WORD_DOCS:
            continue
        ids = [r['id'] for first in sense.resolve(word) for r in rows
               if r['name'].split()[0].lower() == first and r['id'] != config.FOUNDER_PERSON_ID]
        if ids:
            hits[word] = ids
    return hits


def rows_by_id(rows, pid):
    return next(r for r in rows if r['id'] == pid)


def plan(conn, question):
    q = normalise(question)
    vocab = vocabulary(conn)
    q, fixes = fix_typos(q, vocab)
    window = day_window(q)
    people, ambiguous = match_people(conn, q, question)
    if not people:
        for word, ids in unseen_nicknames(conn, q, vocab, set(fixes.values())).items():
            people += ids
            if len(ids) > 1:
                ambiguous[word] = ids
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
    org_people, orgs = [], []
    if not people:
        for row in conn.execute("SELECT id, org FROM people WHERE org != ''"):
            if any(t == row['org'].lower().split()[0] for t in terms):
                org_people.append(row['id'])
                orgs.append(row['org'].split()[0])
    activity = bool(re.search(r'\b(saying|said|up to|doing|working on|latest from|anything from|hear from)\b', q))

    # a person with nothing else to ask about is a request for their activity
    # 'what is daniel saying', 'anything from priya', 'dan?'
    if kind == 'topic' and org_people and activity:
        kind = 'person'
    elif kind == 'topic' and org_people and all(t in OVERVIEW_WORDS or t in {o.lower() for o in orgs} for t in terms):
        kind = 'company'             # a company name with nothing else to ask is a request for the whole account
    elif kind == 'topic' and not people and not terms and window:
        kind = 'schedule'            # 'tomorrow?' on its own is 'what is on tomorrow'
    elif kind == 'topic' and people and (not terms or window or activity):
        kind = 'person'
    # a role word stands for the people who have it: 'investors' is Jordan and
    # Caroline, 'candidates' is Taylor
    group = ''
    roles = {r['role'] for r in conn.execute("SELECT DISTINCT role FROM people WHERE role != ''")} - NOT_ROLES
    gloss = glossary(conn)
    for role in sorted(roles):
        if not people and any(t.startswith(role) or role in gloss.get(t, ()) for t in terms):
            ids = [r['id'] for r in conn.execute('SELECT id FROM people WHERE role=?', (role,))]
            people, group = ids, role + 's'
            kind = 'person' if kind == 'topic' else kind
    people = people or org_people
    # the corrected spelling is what the inbox holds, so it is searched for alongside what was typed
    expansions, related = list(fixes.values()), []
    for t in terms:
        related += gloss.get(t) or gloss.get(t.rstrip('s'), [])
    # the other direction: the inbox may hold the misspelling. 'northwind' also searches 'northwnd'
    for t in terms:
        if t in vocab:
            expansions += near_words(vocab, t)
    plan_ = Plan(kind=kind, people=people, ambiguous=ambiguous, group=group, expansions=list(dict.fromkeys(expansions)),
                 related=list(dict.fromkeys(related)),
                 terms=terms, mine=mine, fixes=fixes, org_people=org_people, orgs=list(dict.fromkeys(orgs)))
    if window:
        plan_.start, plan_.end, plan_.day_label = window
    elif kind == 'schedule' and people:
        # 'any meetings with investors coming up' looks forward, not at today
        plan_.start, plan_.end, plan_.day_label = config.NOW, config.NOW + timedelta(days=14), 'coming up'
    elif kind == 'schedule':
        today = config.NOW.replace(hour=0, minute=0, second=0, microsecond=0)
        plan_.start, plan_.end, plan_.day_label = today, today + timedelta(days=1), 'today'
    return plan_
