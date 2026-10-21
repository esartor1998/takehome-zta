"""Question answering: retrieve, render numbered context, answer, verify cites.

The model cites with short numbers like [3]. We map them back to real item ids
in code, because a 3B model copying a 16 character hex id or a slack ts will
mangle it sometimes, and a dropped digit is a citation to nothing
"""
import os
import re
import time
from datetime import datetime

from . import brief, config, llm, retrieve, route, stale, store

BODY_CHARS = 450
CANT_FIND = "I can't find that in the available data."

SYSTEM = f"""You are the founder's assistant. The founder is Alex Chen. Answer using ONLY the numbered context items.

Current time: {config.NOW.strftime('%A %Y-%m-%d %H:%M')} UTC. Resolve today, tomorrow and this week against this time, never against any other date.

Rules:
1. Every sentence that states a fact ends with its citation markers, like [2] or [2][5]. Cite only numbers that appear in the context.
2. Items marked SUPERSEDED, STALE or CANCELLED are history. Never present them as current. Mention them only to explain what changed, and say they are outdated.
3. When items disagree, the item marked CURRENT wins.
4. If the context does not contain the answer, reply exactly: {CANT_FIND}
5. Do not add names, numbers or dates that are not in the context. Say what is missing instead of guessing.
6. For lists, give the identifier, the title and the owner of each entry.
7. Be concise: at most 120 words. Write plain sentences. Do not copy the item headers.

Example
Question: Who owns the billing migration?
Answer: Priya Nair owns the billing migration [2]. Daniel Kim asked to push it by a week [4][5]"""

# extra instruction by detected intent. a bare 'what should I know' makes the
# 3B model refuse, so we say what a good answer to that kind of question covers
MODE_HINTS = {
    'meetings': 'Cover: the meeting title, its time, who attends, and anything that changed '
                '(a reschedule, a cancelled earlier slot) with the reason.',
    'cancel': 'Say whether the event is CANCELLED or CONFIRMED. Quote the calendar note for where '
              'or when it moved. Do not invent a reason.',
    'emails': 'List each email as: sender, subject, date. Give the meeting it relates to.',
    'topic': 'Summarise in three to five sentences: what happened, what is still open, and anything marked '
             'STALE or CANCELLED that someone might still be relying on.',
    'blocked': 'List each blocked issue as: identifier, title, owner.',
    'person': 'Summarise what each person said or did recently, newest first, one line each, with the date. '
              'Cover each person named in the note, separately.',
    'decisions': 'State the current decision first, then what it replaced and who changed it.',
}

# open questions have no single item as the answer. they are answered from the
# same verified facts the morning brief is built from, because retrieval over
# raw items gave 'the PR for the billing migration was merged' (nothing in the
# data says that) for 'what happened this week'. instructions say what a good
# answer to each kind of question covers: a bare 'what should I know' makes a
# 3B model refuse, and 'what is on today' needs a list in time order
DIGESTS = {
    'schedule': (None, 'List every event in time order with its time, who is in it and anything unusual '
                       '(cancelled, tentative, all day, already happened, a different time zone). '
                       'Say what is still to come. If a meeting has a prep note, include it.'),
    'followups': ({'ask', 'promise'}, 'Two parts. First what people are waiting on you for, with the deadline and '
                                      'whether it is overdue. Then what you promised and still have open. Mention '
                                      'asks that are already handled in one short line. If nothing is open, say so.'),
    'focus': (None, 'Give up to 3 priorities, most urgent first, one line each. Skip items marked no action needed.'),
    'catchup': (None, 'Summarise the most important items in one sentence each, most important first. '
                      'Group what changed, what is waiting on you, and what is at risk.'),
    'blocked': (None, 'List the blocked issues, yours first.'),
    'prep': (None, 'List what to know before the meeting, one line each.'),
    'company': (None, 'Summarise the account in a few lines: meetings, what they wait on, open issues, the deal.'),
    'meeting_emails': (None, 'List each email with the meeting it relates to.'),
    'decisions': ({'change'}, 'List each decision with its date, who made it and what it replaced. Newest first.'),
    'customers': ({'customer'}, 'List each customer problem, how many times it was reported, over how many days, '
                                'and whether a fix came back.'),
}
# how many facts a model is shown when it phrases a digest. only the model path has a budget (a local
# model reads 8192 tokens). a list rendered by code has no reason to leave anything out, and a founder
# asking for the docket wants all of it
DIGEST_LIMIT = 8
FOLLOWUP_LIMIT = 12
BLOCKED_LIMIT = 12
PREP_LIMIT = 10
SCHEDULE_LIMIT = 14

# these answers are lists of facts the database already holds. a model adds
# nothing to them and costs seconds, tokens and the occasional wrong line (a
# cancelled meeting called 'superseded', an open ask listed as handled), so
# they are rendered by code. FOUNDER_DIGEST=llm sends them through the model
# anyway, which is how the benchmark compares models on the same facts
CODE_DIGESTS = ('schedule', 'followups', 'customers', 'decisions', 'blocked', 'meeting_emails', 'prep', 'company', 'catchup')

CITE_RE = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')


def _when(iso_text):
    from datetime import datetime
    dt = datetime.fromisoformat(iso_text.replace('Z', '+00:00'))
    return dt.strftime('%a %Y-%m-%d %H:%M UTC')


def render_item(conn, item, label, people_names):
    """One numbered context entry. Ids stay out of the text on purpose: the
    model quotes headers it can see, and the number is all it needs to cite"""
    row = store.row_to_item(item)
    author = people_names.get(row['author'], row['meta'].get('from_name') or 'unknown sender')
    tags = []
    kind = row['kind']
    if kind == 'event':
        tags.append(row['status'].upper())
        attendees = ', '.join(people_names.get(p, p) for p in row['people'])
        if 'all_day' in row['flags']:
            when = f"all day {row['meta'].get('start_local', row['start'])[:10]}"
        else:
            when = f"{_when(row['start'])} to {_when(row['end'])}"
            zone, local = row['meta'].get('time_zone', ''), row['meta'].get('start_local', '')
            if zone and zone != 'UTC' and 'T' in local:
                when += f" ({local[11:16]} local time in {zone})"
        head = f"[{label}] calendar event '{row['title']}', {when}, attendees: {attendees}, organizer: {author}"
    elif kind == 'email':
        head = f"[{label}] email from {author}, {_when(row['ts'])}, subject: {row['title']}"
        if 'forwarded' in row['flags']:
            tags.append('forwarded message')
    elif kind == 'message':
        head = f"[{label}] slack {row['title']} message from {author}, {_when(row['ts'])}"
    elif kind == 'pr':
        head = (f"[{label}] github pull request #{row['meta']['number']} in {row['meta']['repo']} "
                f"({row['status']}) by {author}, updated {_when(row['ts'])}, title: {row['title']}")
        if row['people']:
            tags.append('review requested from ' + ', '.join(people_names.get(p, p) for p in row['people']))
    elif kind == 'comment':
        head = f"[{label}] github comment from {author}, {_when(row['ts'])}, on {row['title']}"
    elif kind == 'doc':
        head = f"[{label}] notion page '{row['title']}', last edited {_when(row['ts'])} by {author}"
    elif kind == 'deal':
        head = f"[{label}] crm deal '{row['title']}' ({row['status']}), last updated {_when(row['ts'])}, owner {author}"
    elif kind == 'note':
        head = f"[{label}] crm note, {_when(row['ts'])}, {row['title']}"
    else:
        head = (f"[{label}] linear issue {row['meta'].get('identifier')} ({row['status']}), "
                f"owner {author}, updated {_when(row['ts'])}, title: {row['title']}")

    decision = conn.execute('SELECT * FROM decisions WHERE item_id=?', (row['id'],)).fetchone()
    newer_info = conn.execute('SELECT s.current_fact, n.ts, n.source FROM stale_records s '
                         'JOIN items n ON n.id = s.newer_id WHERE s.item_id=?', (row['id'],)).fetchone()
    if newer_info:
        newer = f", for example: {newer_info['current_fact']}" if newer_info['current_fact'] else ''
        tags.append(f"STALE: newer information from {newer_info['source']} on {newer_info['ts'][:10]} changes this{newer}. "
                    'this record is NOT up to date')
    elif decision:
        if decision['status'] == 'stale':
            tags.append('STALE: this record still states a value that was corrected later, '
                        'so it is NOT up to date')
        else:
            tags.append(decision['status'].upper())
    if row['state'] == 'automated':
        tags.append('automated message from a system, not a person')
    siblings = [r for r in conn.execute(
        'SELECT source, title FROM items WHERE dup_group=? AND id!=?', (row['dup_group'], row['id']))] \
        if row['dup_group'] else []
    if siblings:
        tags.append('same update also posted in ' + ', '.join(
            f"{r['source']} {r['title']}" for r in siblings))
    if row['flags']:
        tags.append('data issues: ' + ','.join(f for f in row['flags'] if f not in ('all_day', 'forwarded')))
        tags = [t for t in tags if t != 'data issues: ']
    line = head + (f" ({'; '.join(tags)})" if tags else '')
    body = row['body'][:BODY_CHARS]
    # 'next Friday' means a date only against the day it was written, and a model that is left to work it out
    # does it wrong (it called Friday Mar 20 'March 21')
    resolved = stale.relative_phrases(row['body'], datetime.fromisoformat(row['ts'].replace('Z', '+00:00'))) if kind in ('email', 'message') else []
    if resolved:
        body += '\n    dates in this message: ' + '; '.join(f"'{p}' is {d.strftime('%a %b %-d')}" for p, d in resolved)
    if 'forwarded' in row['flags'] and row['quoted']:
        body += f"\n    forwarded message: {row['quoted'][:BODY_CHARS]}"
    if kind == 'event' and body:
        body = f'calendar note: {body}'
    return f"{line}\n    {body}"


def expand_decision_context(conn, ids, topics, limit=3):
    """For retrieved items that belong to a decision topic, make sure the
    current state of that topic is in the context. Otherwise a question that
    matches the old wording retrieves only the superseded side of a reversal"""
    extra = []
    for topic in topics:
        rows = conn.execute(
            "SELECT item_id FROM decisions WHERE topic=? AND status='current' ORDER BY ts DESC",
            (topic,)).fetchall()
        extra += [r['item_id'] for r in rows[:2]]
    return ids + [e for e in dict.fromkeys(extra) if e not in ids][:limit]


def context_block(context, number):
    match = re.search(rf'^\[{number}\] .*?(?=^\[\d+\] |\Z)', context, re.S | re.M)
    return match.group(0) if match else ''


MAX_PREVIOUS_STAGES = 2   # newest first, older history is rarely what was asked
STAGE_GAP_HOURS = 12      # events closer than this belong to one change of plan
SOURCE_RANK = {'linear': 0, 'slack': 1, 'gmail': 2}   # cleanest phrasing first


def _day(ts):
    return datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime('%b %d').replace(' 0', ' ')


def _stages(rows):
    """Group decision events into stages (newest stage first). The email, the
    slack post and the linear edit for one change land minutes apart, and
    listing each separately made the model count them as separate decisions"""
    stages = []
    for row in sorted(rows, key=lambda r: r['ts']):
        t = datetime.fromisoformat(row['ts'].replace('Z', '+00:00'))
        if stages and (t - stages[-1][-1]['_t']).total_seconds() < STAGE_GAP_HOURS * 3600:
            stages[-1].append(dict(row, _t=t))
        else:
            stages.append([dict(row, _t=t)])
    return stages[::-1]


def _pick(stage):
    return min(stage, key=lambda r: SOURCE_RANK.get(r['source'], 3))


def decision_timelines(conn, topics, limit=2):
    """One distilled entry per decision topic among the retrieved items:
    current state first, then what it replaced, then any record still carrying
    a retracted value. Shown raw, a reversal thread made the 3B model answer
    with whichever side it read last. Each entry cites the current item"""
    names = {r['id']: r['name'] for r in conn.execute('SELECT id, name FROM people')}
    out = []
    for topic in topics[:limit]:
        rows = [dict(r) for r in conn.execute(
            'SELECT d.*, i.author FROM decisions d JOIN items i ON i.id=d.item_id '
            'WHERE d.topic=? ORDER BY d.ts DESC', (topic,))]
        current = [r for r in rows if r['status'] == 'current']
        if not current:
            continue
        stages = [[dict(r) for r in current]] + _stages([r for r in rows if r['status'] == 'superseded'])[:MAX_PREVIOUS_STAGES]
        label = store.topic_label(conn, topic)
        for number, stage in enumerate(stages):
            # the phrasing comes from the cleanest source (linear), but who made
            # the call and the item we cite come from a person's own message
            # a linear record's author is its assignee, not the decider
            human = min(stage, key=lambda r: (r['source'] == 'linear', SOURCE_RANK.get(r['source'], 3)))
            status = 'this is the CURRENT decision' if number == 0 else 'this was later replaced'
            verb = {'decision': 'decided', 'reversal': 'reversed it to',
                    'correction': 'corrected it to'}.get(human['kind'], 'decided')
            # a plain sentence relays far better on the 3B model than a labelled
            # field list, which it garbled into 'changed by <wrong person>'
            out.append((f"On {_day(stage[0]['ts'])}, {names.get(human['author'], 'unknown')} {verb}: "
                        f"{_pick(stage)['value']} ({label}; {status})", human['item_id']))
        for r in rows:
            if r['status'] == 'stale':
                out.append((f"The record {r['item_id'].split('@')[0].split(':')[1]} is NOT up to date ({label}). "
                            f"It still says: {r['value']}. The plan was corrected after it was written", r['item_id']))
    return out


THREAD_TOP = 4            # only the best-ranked items get their conversation pulled in
THREAD_EXTRA = 2          # siblings added per conversation
UPDATE_EXTRA = 3          # updates added for stale records in the context


def pull_in_updates(conn, ids):
    """A stale record that made it into the context brings the item that shows it is
    stale. Lexical search finds the old Notion page that says 'Initech renewal terms'
    and misses the one-line reply that changed them"""
    extra = []
    for item_id in ids:
        row = conn.execute('SELECT newer_id FROM stale_records WHERE item_id=?', (item_id,)).fetchone()
        if row and row['newer_id'] not in ids and row['newer_id'] not in extra:
            extra.append(row['newer_id'])
    return ids + extra[:UPDATE_EXTRA]


def expand_threads(conn, ids):
    """The conversation around the best hits. 'ok by me, 2yr 15% fine' shares no
    words with the question about the Initech discount, and the thread it is in does"""
    extra = []
    for item_id in ids[:THREAD_TOP]:
        row = conn.execute('SELECT thread_key, kind FROM items WHERE id=?', (item_id,)).fetchone()
        if not row or row['kind'] not in ('email', 'message'):
            continue
        siblings = conn.execute(
            "SELECT id FROM items WHERE thread_key=? AND id!=? AND state='current' AND kind IN ('email','message') "
            'ORDER BY (author = ?) DESC, ts DESC LIMIT ?',
            (row['thread_key'], item_id, config.FOUNDER_PERSON_ID, THREAD_EXTRA)).fetchall()
        extra += [s['id'] for s in siblings if s['id'] not in ids and s['id'] not in extra]
    return ids + extra


def assemble_ids(conn, found):
    """Everything a model may cite for one question: what retrieval picked, the
    current decisions for its topics, the updates behind any stale record, and the
    conversations around the best hits"""
    ids = expand_decision_context(conn, found['ids'], found['decision_topics'])
    return expand_threads(conn, pull_in_updates(conn, ids))


def build_context(conn, ids, timelines=()):
    names = {r['id']: (f"{r['name']} ({r['org']})" if r['org'] else r['name'])
             for r in conn.execute('SELECT id, name, org FROM people')}
    labels, lines = {}, []
    for text, cite_id in timelines:
        number = len(labels) + 1
        labels[number] = cite_id
        lines.append(f'[{number}] {text}')
    for item_id in ids:
        number = len(labels) + 1
        row = conn.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        labels[number] = item_id
        lines.append(render_item(conn, row, number, names))
    return labels, '\n\n'.join(lines)


def _content_words(text):
    return {w for w in re.findall(r'[a-z0-9]+', CITE_RE.sub('', text).lower())
            if len(w) > 2 and w not in retrieve.STOP}


# a cited item only survives if it supports the sentence about as well as the
# best retrieved item does. the 3B model cited two unrelated linear issues for
# 'Daniel asked to push the billing migration', because they shared his name and
# 'migration'. the email shared six words, the issues three
KEEP_RATIO = 0.7
MIN_SHARED = 2
ADD_MIN_RATIO = 0.5   # share of the sentence the item must cover to be added


def ground_citations(text, blocks, current):
    """Check every citation against the words it is supposed to support.

    blocks: label -> rendered context text for every label
    current: labels that are not STALE, SUPERSEDED or CANCELLED. only these can
    be added to a sentence, so a bare 'ship date is Mar 22' is never pinned on
    the stale record that says Mar 20.
    Returns (text, dropped, added, issues). issues lists every claim whose
    citation could not be made to hold, for the founder and for investigate()"""
    dropped = added = 0
    issues = []
    out_lines = []
    # the dates, prices, percentages and durations each block states. short numbers cannot be
    # compared as words ('20' and '22' are one character apart, and every header carries '2026'
    # and a time), so a claim's values have to appear in the blocks that carry its citations
    values = {n: stale.concrete_values(blocks[n]) for n in blocks}
    for line in text.split('\n'):
        pieces = []
        for sentence in re.split(r'(?<=[.!?])\s+', line):
            words = _content_words(sentence)
            if len(sentence.split()) <= 3 or CANT_FIND.lower().rstrip('.') in sentence.lower() or not words:
                pieces.append(sentence)
                continue
            support = {n: len(words & _content_words(blocks[n])) for n in blocks}
            best = max(support.values(), default=0)
            marks = [int(n) for m in CITE_RE.finditer(sentence) for n in re.split(r'\s*,\s*', m.group(1))]
            kept = [n for n in dict.fromkeys(marks)
                    if n in blocks and support[n] >= MIN_SHARED and support[n] >= KEEP_RATIO * best]
            model_marks = [n for n in dict.fromkeys(marks) if n in blocks]
            dropped += len(model_marks) - len(kept)
            kind = ''
            if not kept:
                cands = [n for n in current if support[n] >= MIN_SHARED
                         and support[n] / len(words) >= ADD_MIN_RATIO]
                if cands:
                    kept = [max(cands, key=lambda n: support[n])]
                    added += 1
                    kind = 'reattributed' if model_marks else ''
                else:
                    kind = 'unsupported' if model_marks else ('uncited' if len(sentence.split()) > 4 else '')
            elif len(kept) < len(model_marks):
                kind = 'partly_unsupported'
            claimed = stale.concrete_values(CITE_RE.sub('', sentence))
            if kept and claimed:
                missing = claimed - set().union(*[values[n] for n in kept])
                if missing:
                    # the value is in another block that also supports the sentence: cite that one too
                    holders = [n for n in current if missing <= values[n] and support[n] >= MIN_SHARED]
                    if holders:
                        kept = kept + [max(holders, key=lambda n: support[n])]
                        added += 1
                    elif not kind:
                        kind = 'value_mismatch'
            # a claim whose other citations held is supported, and a remark about the answer is not a claim
            if kind == 'partly_unsupported' or (kind and not is_claim(sentence)):
                kind = ''
            if kind:
                issues.append({'claim': CITE_RE.sub('', sentence).strip(), 'kind': kind,
                               'model_labels': model_marks, 'labels': list(kept)})
            # markers go before the closing punctuation. after it, the sentence
            # splitter reads them as the start of the next sentence
            bare, tail = re.match(r'(.*?)([.!?]*)\s*$', CITE_RE.sub('', sentence).strip(), re.S).groups()
            pieces.append(bare.rstrip() + ''.join(f' [{n}]' for n in kept) + tail)
        out_lines.append(' '.join(pieces))
    return '\n'.join(out_lines), dropped, added, issues


INVESTIGATE_LIMIT = 4        # claims checked per answer, worst first
INVESTIGATE_SCHEMA = {'type': 'object',
                      'properties': {'verdict': {'type': 'string', 'enum': ['supported', 'partly', 'not_supported']},
                                     'best_source': {'type': 'integer'}, 'reason': {'type': 'string'}},
                      'required': ['verdict', 'best_source', 'reason']}
INVESTIGATE_SYSTEM = (
    'You check one claim against numbered sources. Reply with JSON only.\n'
    'verdict: supported = a source says this. partly = a source says some of it. not_supported = '
    'no source says it.\n'
    'best_source: the number of the source that supports the claim best, or 0 if none does.\n'
    'reason: under 20 words, naming what is missing or wrong.')
META_RE = re.compile(r"^\W*(nothing|no one|none|nobody|there (is|are) no|what('s| is| remains)( still)? (open|outstanding)|"
                     r"note\b|overall|in summary|to summari[sz]e|open question|still open)", re.I)


def is_claim(sentence):
    """A sentence that states something about the data: it has a number, a date, an id or
    a name past the first word, and it is not a remark about the answer itself ('Nothing is
    marked STALE', 'What remains open: ...'). Only claims can be unsupported"""
    if META_RE.match(sentence):
        return False
    return bool(re.search(r'\d|[A-Z]{2,}-\d|(?<!^)(?<=[a-z,;] )[A-Z][a-z]+', sentence.strip()))


ISSUE_ORDER = {'unsupported': 0, 'value_mismatch': 1, 'reattributed': 2, 'partly_unsupported': 3, 'uncited': 4}


def investigate(issues, blocks, labels, ids_by_label=None):
    """Ask the model to look at each claim whose citation did not hold. It reads
    the claim and the sources, says whether any source supports it, and names the
    best one. A supported verdict with a named source repairs the citation. Anything
    else becomes a flag for the founder. Lexical checks found the problems, and
    the model only has to read them, which is a task a small model does well.
    Returns (flags, repairs, usage) with repairs as {claim: label} and usage the
    tokens, cost and projected cost of the checks, which count toward the answer's"""
    flags, repairs = [], {}
    usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'cost': 0.0, 'projected_cost': 0.0}
    for issue in sorted(issues, key=lambda i: ISSUE_ORDER.get(i['kind'], 9))[:INVESTIGATE_LIMIT]:
        shown = list(dict.fromkeys(issue['model_labels'] + issue['labels']))
        if not shown:
            # nothing was cited: show the two sources that share the most words
            words = _content_words(issue['claim'])
            shown = sorted(blocks, key=lambda n: -len(words & _content_words(blocks[n])))[:2]
        sources = '\n\n'.join(blocks[n][:500] for n in shown)
        result = llm.chat(INVESTIGATE_SYSTEM, f"Claim: {issue['claim']}\n\nSources:\n{sources}",
                          schema=INVESTIGATE_SCHEMA, max_tokens=80, role='verify')
        for key in usage:
            usage[key] += result[key] if key in result else 0
        parsed = llm.parse_json(result['text'], None) or {}
        verdict, best = parsed.get('verdict', 'not_supported'), parsed.get('best_source', 0)
        if verdict == 'supported' and best in blocks:
            repairs[issue['claim']] = best
            continue
        flags.append({'claim': issue['claim'], 'kind': issue['kind'], 'verdict': verdict,
                      'reason': parsed.get('reason', '').strip() or 'no source says this',
                      'cited': [ids_by_label[n] for n in issue['model_labels'] if ids_by_label and n in ids_by_label]})
    # claims past the limit are still flagged, only not examined
    for issue in sorted(issues, key=lambda i: ISSUE_ORDER.get(i['kind'], 9))[INVESTIGATE_LIMIT:]:
        flags.append({'claim': issue['claim'], 'kind': issue['kind'], 'verdict': 'not examined',
                      'reason': 'citation did not match the source and was not checked', 'cited': []})
    return flags, repairs, usage


def apply_repairs(text, repairs):
    """Put a repaired citation on its claim"""
    for claim, label in repairs.items():
        text = text.replace(claim, f'{claim} [{label}]', 1) if claim in text else text
    return text


def verify(text, labels):
    """Map [n] to ids, drop markers that point at nothing, and count sentences
    that state something without a valid citation. Returns (text, cited, ungrounded)"""
    cited = []

    def swap(match):
        nums = [int(n) for n in re.split(r'\s*,\s*', match.group(1))]
        valid = [labels[n] for n in nums if n in labels]
        cited.extend(valid)
        return ''.join(f'[{v}]' for v in valid)

    mapped = CITE_RE.sub(swap, text)
    sentences = [s for s in re.split(r'(?<=[.!?])\s+|\n+', mapped) if len(s.split()) > 3]
    ungrounded = [s for s in sentences if not re.search(r'\[[a-z]+:[^\]]+\]', s)]
    return mapped, list(dict.fromkeys(cited)), ungrounded


def _shown(plan, kind, facts, limit):
    """Every fact when code renders the list. A model gets at most limit of them, and plan.total keeps
    the full count so the answer can say how many were left out"""
    plan.total = len(facts)
    if kind in CODE_DIGESTS and os.environ.get('FOUNDER_DIGEST', 'code') == 'code':
        return facts
    return facts[:limit]


def digest_facts(conn, plan, question):
    """(kind, facts, instruction) when the plan calls for a digest, else None"""
    kind = plan.kind
    if kind == 'topic' and re.search(r'\bemails?\b', question, re.I) and re.search(r'\bmeetings?\b', question, re.I):
        kind = 'meeting_emails'
    if re.search(r'\bcustomers?\b.*\b(issues?|problems?|repeat\w*|complain\w*)\b', question, re.I):
        kind = 'customers'
    if kind not in DIGESTS:
        return None
    cats, instruction = DIGESTS[kind]
    if kind == 'company':
        return kind, _shown(plan, kind, brief.company_facts(conn, plan), PREP_LIMIT), instruction
    if kind == 'prep':
        return kind, _shown(plan, kind, brief.prep_facts(conn, plan, question), PREP_LIMIT), instruction
    if kind == 'blocked':
        return kind, _shown(plan, kind, brief.blocked_facts(conn, mine_only=plan.mine), BLOCKED_LIMIT), instruction
    if kind == 'meeting_emails':
        return kind, _shown(plan, kind, brief.meeting_email_facts(conn), DIGEST_LIMIT), instruction
    if kind == 'schedule':
        return kind, _shown(plan, kind, brief.schedule_facts(conn, plan.start, plan.end, plan.people or None), SCHEDULE_LIMIT), instruction
    facts = brief.collect_facts(conn)
    if cats:
        facts = [f for f in facts if f['cat'] in cats]
    elif kind == 'catchup':
        # the digest renders its own sections and limits, so it gets every fact
        return kind, [f for f in facts if f['cat'] != 'schedule'], instruction
    if kind == 'followups':
        # asks with a deadline first, then the rest. facts are already scored
        facts = [f for f in facts if f['cat'] in ('ask', 'promise')]
        # 'what did I promise hooli' is about one company's people, and 'anything overdue'
        # about the late ones
        if plan.people:
            facts = [f for f in facts if set(f.get('people', [])) & set(plan.people)]
        if re.search(r'overdue|past due|late|slipp', question, re.I):
            facts = [f for f in facts if f.get('overdue')]
    if kind == 'focus':
        # the top priorities are phrased from the ranking and the rest of the docket is listed under them
        plan.total = len(facts)
        return kind, facts, instruction
    return kind, _shown(plan, kind, facts, FOLLOWUP_LIMIT if kind == 'followups' else DIGEST_LIMIT), instruction


def ambiguity_note(conn, plan):
    """A bare first name that fits several people. We answer for all of them and
    say which is which, since guessing wrong is worse than a longer answer"""
    parts = []
    for alias, ids in plan.ambiguous.items():
        who = ', '.join(
            (lambda r: f"{r['name']} ({r['org'] or 'teammate'})")(
                conn.execute('SELECT name, org FROM people WHERE id=?', (i,)).fetchone()) for i in ids)
        parts.append(f"'{alias}' could mean {who}")
    return 'Note: ' + '; '.join(parts) + '. Answer for each of them and label which is which.'


def ask(conn, question, k=10):
    started = time.time()
    plan = route.plan(conn, question)
    digest = digest_facts(conn, plan, question)
    if digest:
        return ask_digest(conn, question, digest, started, plan)
    found = retrieve.retrieve(conn, question, k=k, plan=plan)
    intents = list(found['intents'])
    if plan.kind == 'person':
        intents.append('person')
    elif plan.kind == 'topic' and not plan.people:
        intents.append('topic')
    if re.search(r'\bemails?\b', question, re.I) and 'meetings' in intents:
        intents.append('emails')
    hints = ' '.join(MODE_HINTS[i] for i in intents if i in MODE_HINTS)
    if plan.ambiguous:
        hints += ' ' + ambiguity_note(conn, plan)
    ids = assemble_ids(conn, found)
    if re.search(r'\bemails?\b', question, re.I):
        # a question about emails gets emails and the events they relate to,
        # slack chatter in the list was presented as email
        ids = [i for i in ids if i.startswith(('gmail:', 'calendar:'))]
    labels, context = build_context(conn, ids, decision_timelines(conn, found['decision_topics']))
    result = llm.chat(SYSTEM, f'Context items:\n\n{context}\n\nQuestion: {question}\n{hints}', max_tokens=300)
    blocks = {n: context_block(context, n) for n in labels}
    current = [n for n, block in blocks.items() if not re.search(
        r'\((?:[^)]*; )?(STALE|SUPERSEDED|CANCELLED)', block)]
    repaired, dropped, added, issues = ground_citations(result['text'].strip(), blocks, current)
    flags, extra = [], {'prompt_tokens': 0, 'completion_tokens': 0, 'cost': 0.0, 'projected_cost': 0.0}
    if issues and os.environ.get('FOUNDER_VERIFY', '1') != '0':
        flags, repairs, extra = investigate(issues, blocks, labels, labels)
        repaired = apply_repairs(repaired, repairs)
    text, cited, ungrounded = verify(repaired, labels)
    cant = CANT_FIND.lower().rstrip('.') in text.lower()
    return {
        'question': question, 'answer': text, 'cited': [] if cant else cited,
        'found': not cant, 'cites_dropped': dropped, 'cites_added': added, 'ungrounded_sentences': [] if cant else ungrounded,
        'flags': [] if cant else flags,
        'retrieved': ids, 'intents': found['intents'], 'pulls': found['pulls'],
        'prompt_tokens': result['prompt_tokens'] + extra['prompt_tokens'],
        'completion_tokens': result['completion_tokens'] + extra['completion_tokens'],
        'cost': result['cost'] + extra['cost'], 'projected_cost': result['projected_cost'] + extra['projected_cost'],
        'verify_tokens': extra['prompt_tokens'] + extra['completion_tokens'],
        'seconds': time.time() - started,
    }


def render_digest(name, facts, plan_label='', total=0):
    """A digest as plain text with citations, no model involved"""
    def cite(f):
        return ''.join(f'[{i}]' for i in f['ids'][:2])

    if name == 'schedule':
        lines = [f"{plan_label}:"] + [f"- {f['text']} {cite(f)}" for f in facts]
        return '\n'.join(lines)
    if name == 'followups':
        asks = [f for f in facts if f['cat'] == 'ask' and not f['handled']]
        promises = [f for f in facts if f['cat'] == 'promise' and not f['handled']]
        done = [f for f in facts if f['handled']]
        lines = ['Waiting on you:'] + ([f"- {f['text']} {cite(f)}" for f in asks] or ['- nothing'])
        lines += ['', 'You said you would:'] + ([f"- {f['text']} {cite(f)}" for f in promises] or ['- nothing'])
        if done:
            lines += ['', 'Already handled:'] + [f"- {f['text']} {cite(f)}" for f in done]
        return '\n'.join(lines)
    if name == 'catchup':
        sections = (('What changed', ('change',)), ('At risk', ('stale', 'customer', 'blocked')),
                    ('Waiting on you', ('ask', 'promise')), ('Coming up today', ('meeting',)))
        lines = []
        for title, cats in sections:
            rows = [f for f in facts if f['cat'] in cats]
            if cats == ('change',):
                rows = sorted(rows, key=lambda f: f.get('ts', ''), reverse=True)
            if rows:
                lines += [f'{title}:'] + [f"- {f.get('short', f['text'])} {cite(f)}" for f in rows] + ['']
        return '\n'.join(lines).strip()
    if name == 'prep':
        return '\n'.join([facts[0]['text'], 'Before it:'] + [f"- {f['text']} {cite(f)}" for f in facts[1:]]) if len(facts) > 1 else facts[0]['text'] + ' ' + cite(facts[0])
    if name == 'blocked':
        total = total or len(facts)
        mine = sum(1 for f in facts if f.get('mine'))
        head = f"{total} blocked issue{'s' if total != 1 else ''}, {mine} yours:"
        more = [f'- and {total - len(facts)} more'] if total > len(facts) else []
        return '\n'.join([head] + [f"- {f['text']} {cite(f)}" for f in facts] + more)
    return '\n'.join(f"- {f['text']} {cite(f)}" for f in facts)


def ask_digest(conn, question, digest, started, plan=None):
    name, facts, instruction = digest
    if name in CODE_DIGESTS and os.environ.get('FOUNDER_DIGEST', 'code') == 'code' and facts:
        label = (plan.day_label if plan and plan.day_label else 'today')
        day = (plan.start if plan and plan.start else config.NOW)
        heading = (f"{label.capitalize()} ({day.strftime('%b %-d')} to {plan.end.strftime('%b %-d')})"
                   if label in ('coming up', 'next week', 'this week', 'last week')
                   else f"{label.capitalize()} ({day.strftime('%A %b %-d')})")
        text = render_digest(name, facts, heading, getattr(plan, 'total', 0) if plan else 0)
        cited = [i for f in facts for i in f['ids'][:2]]
        return {'question': question, 'answer': text, 'cited': list(dict.fromkeys(cited)), 'found': True,
                'cites_dropped': 0, 'cites_added': 0, 'ungrounded_sentences': [],
                'retrieved': [i for f in facts for i in f['ids']], 'intents': [name], 'pulls': {'digest': len(facts)},
                'prompt_tokens': 0, 'completion_tokens': 0, 'cost': 0.0, 'projected_cost': 0.0,
                'seconds': time.time() - started}
    if not facts:
        return {'question': question, 'answer': 'Nothing needs your attention here.', 'cited': [],
                'found': True, 'cites_dropped': 0, 'cites_added': 0, 'ungrounded_sentences': [],
                'retrieved': [], 'intents': [name], 'pulls': {'digest': 0}, 'prompt_tokens': 0,
                'completion_tokens': 0, 'cost': 0.0, 'projected_cost': 0.0,
                'seconds': time.time() - started}
    if name == 'focus':
        # same ranking and phrasing as the brief's focus section, so the two
        # cannot disagree about what matters today
        text, cited, result = brief.focus_section(facts, whole_docket=True)
        if result is None:
            return ask_digest(conn, question, (name, [], instruction), started, plan)
        return {'question': question, 'answer': text, 'cited': cited, 'found': True,
                'cites_dropped': 0, 'cites_added': 0, 'ungrounded_sentences': [],
                'retrieved': [i for f in facts for i in f['ids']], 'intents': [name],
                'pulls': {'digest': len(facts)}, 'prompt_tokens': result['prompt_tokens'],
                'completion_tokens': result['completion_tokens'],
                'cost': result['cost'], 'projected_cost': result['projected_cost'],
                'seconds': time.time() - started}
    labels = {n: f['ids'][0] for n, f in enumerate(facts, 1)}
    context = '\n\n'.join(f"[{n}] {f['text']}" for n, f in enumerate(facts, 1))
    left = getattr(plan, 'total', len(facts)) - len(facts)
    if left > 0:
        context += f'\n\n({left} more items exist and are not listed above. Say that {left} more exist.)'
    result = llm.chat(SYSTEM, f'Context items:\n\n{context}\n\nQuestion: {question}\n{instruction}\n'
                      'These items already answer the question. Summarise them, and do not refuse.',
                      max_tokens=300)
    blocks = {n: context_block(context, n) for n in labels}
    text, dropped, added, issues = ground_citations(result['text'].strip(), blocks, list(labels))
    flags, extra = [], {'prompt_tokens': 0, 'completion_tokens': 0, 'cost': 0.0, 'projected_cost': 0.0}
    if issues and os.environ.get('FOUNDER_VERIFY', '1') != '0':
        flags, repairs, extra = investigate(issues, blocks, labels, labels)
        text = apply_repairs(text, repairs)
    text, cited, ungrounded = verify(text, labels)
    cant = CANT_FIND.lower().rstrip('.') in text.lower()
    return {
        'question': question, 'answer': text, 'cited': [] if cant else cited, 'found': not cant,
        'cites_dropped': dropped, 'cites_added': added, 'flags': [] if cant else flags,
        'ungrounded_sentences': [] if cant else ungrounded, 'retrieved': list(labels.values()),
        'intents': [name], 'pulls': {'digest': len(facts)},
        'prompt_tokens': result['prompt_tokens'] + extra['prompt_tokens'],
        'completion_tokens': result['completion_tokens'] + extra['completion_tokens'],
        'cost': result['cost'] + extra['cost'], 'projected_cost': result['projected_cost'] + extra['projected_cost'],
        'verify_tokens': extra['prompt_tokens'] + extra['completion_tokens'],
        'seconds': time.time() - started,
    }
