"""Question answering: retrieve, render numbered context, answer, verify cites.

The model cites with short numbers like [3]. We map them back to real item ids
in code, because a 3B model copying a 16 character hex id or a slack ts will
mangle it sometimes, and a dropped digit is a citation to nothing
"""
import os
import re
import time
from datetime import datetime

from . import brief, config, llm, retrieve, route, store

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
    'meeting_emails': (None, 'List each email with the meeting it relates to.'),
    'decisions': ({'change'}, 'List each decision with its date, who made it and what it replaced. Newest first.'),
    'customers': ({'customer'}, 'List each customer problem, how many times it was reported, over how many days, '
                                'and whether a fix came back.'),
}
DIGEST_LIMIT = 8
FOLLOWUP_LIMIT = 12
BLOCKED_LIMIT = 12
SCHEDULE_LIMIT = 14

# these answers are lists of facts the database already holds. a model adds
# nothing to them and costs seconds, tokens and the occasional wrong line (a
# cancelled meeting called 'superseded', an open ask listed as handled), so
# they are rendered by code. FOUNDER_DIGEST=llm sends them through the model
# anyway, which is how the benchmark compares models on the same facts
CODE_DIGESTS = ('schedule', 'followups', 'customers', 'decisions', 'blocked', 'meeting_emails')

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
            when = f"all day {row['start'][:10]}"
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
    stale = conn.execute('SELECT s.current_fact, n.ts, n.source FROM stale_records s '
                         'JOIN items n ON n.id = s.newer_id WHERE s.item_id=?', (row['id'],)).fetchone()
    if stale:
        newer = f", for example: {stale['current_fact']}" if stale['current_fact'] else ''
        tags.append(f"STALE: newer information from {stale['source']} on {stale['ts'][:10]} changes this{newer}. "
                    'this record is NOT up to date')
    elif decision:
        if decision['status'] == 'stale':
            tags.append('STALE: this record still states a value that was corrected later, '
                        'so it is NOT up to date')
        else:
            tags.append(decision['status'].upper())
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
    Returns (text, dropped, added) where the counts feed the eval"""
    dropped = added = 0
    out_lines = []
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
            dropped += len([n for n in marks if n in blocks]) - len(kept)
            if not kept:
                cands = [n for n in current if support[n] >= MIN_SHARED
                         and support[n] / len(words) >= ADD_MIN_RATIO]
                if cands:
                    kept = [max(cands, key=lambda n: support[n])]
                    added += 1
            # markers go before the closing punctuation. after it, the sentence
            # splitter reads them as the start of the next sentence
            bare, tail = re.match(r'(.*?)([.!?]*)\s*$', CITE_RE.sub('', sentence).strip(), re.S).groups()
            pieces.append(bare.rstrip() + ''.join(f' [{n}]' for n in kept) + tail)
        out_lines.append(' '.join(pieces))
    return '\n'.join(out_lines), dropped, added


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
    if kind == 'blocked':
        facts = brief.blocked_facts(conn, mine_only=plan.mine)
        return kind, facts[:BLOCKED_LIMIT], instruction
    if kind == 'meeting_emails':
        return kind, brief.meeting_email_facts(conn)[:DIGEST_LIMIT], instruction
    if kind == 'schedule':
        return kind, brief.schedule_facts(conn, plan.start, plan.end, plan.people or None)[:SCHEDULE_LIMIT], instruction
    facts = brief.collect_facts(conn)
    if cats:
        facts = [f for f in facts if f['cat'] in cats]
    elif kind == 'catchup':
        # what changed first, then what is at risk, then what is waiting
        order = {'change': 0, 'stale': 1, 'customer': 2, 'ask': 3, 'promise': 4, 'blocked': 5, 'meeting': 6}
        facts = sorted((f for f in facts if f['cat'] != 'schedule'), key=lambda f: order.get(f['cat'], 9))
    if kind == 'followups':
        # asks with a deadline first, then the rest. facts are already scored
        facts = [f for f in facts if f['cat'] in ('ask', 'promise')]
    return kind, facts[:FOLLOWUP_LIMIT if kind == 'followups' else DIGEST_LIMIT], instruction


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
    ids = expand_decision_context(conn, found['ids'], found['decision_topics'])
    if re.search(r'\bemails?\b', question, re.I):
        # a question about emails gets emails and the events they relate to,
        # slack chatter in the list was presented as email
        ids = [i for i in ids if i.startswith(('gmail:', 'calendar:'))]
    labels, context = build_context(conn, ids, decision_timelines(conn, found['decision_topics']))
    result = llm.chat(SYSTEM, f'Context items:\n\n{context}\n\nQuestion: {question}\n{hints}', max_tokens=300)
    blocks = {n: context_block(context, n) for n in labels}
    current = [n for n, block in blocks.items() if not re.search(
        r'\((?:[^)]*; )?(STALE|SUPERSEDED|CANCELLED)', block)]
    repaired, dropped, added = ground_citations(result['text'].strip(), blocks, current)
    text, cited, ungrounded = verify(repaired, labels)
    cant = CANT_FIND.lower().rstrip('.') in text.lower()
    return {
        'question': question, 'answer': text, 'cited': [] if cant else cited,
        'found': not cant, 'cites_dropped': dropped, 'cites_added': added, 'ungrounded_sentences': [] if cant else ungrounded,
        'retrieved': ids, 'intents': found['intents'], 'pulls': found['pulls'],
        'prompt_tokens': result['prompt_tokens'], 'completion_tokens': result['completion_tokens'],
        'cost': result['cost'], 'projected_cost': result['projected_cost'],
        'seconds': time.time() - started,
    }


def render_digest(name, facts, plan_label=''):
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
            lines += ['', 'Already handled:'] + [f"- {f['text']} {cite(f)}" for f in done[:3]]
        return '\n'.join(lines)
    if name == 'blocked':
        total = len(facts)
        mine = sum(1 for f in facts if f.get('mine'))
        head = f"{total} blocked issue{'s' if total != 1 else ''}, {mine} yours:"
        return '\n'.join([head] + [f"- {f['text']} {cite(f)}" for f in facts])
    return '\n'.join(f"- {f['text']} {cite(f)}" for f in facts)


def ask_digest(conn, question, digest, started, plan=None):
    name, facts, instruction = digest
    if name in CODE_DIGESTS and os.environ.get('FOUNDER_DIGEST', 'code') == 'code' and facts:
        label = (plan.day_label if plan and plan.day_label else 'today')
        day = (plan.start if plan and plan.start else config.NOW)
        heading = (f"{label.capitalize()} ({day.strftime('%b %-d')} to {plan.end.strftime('%b %-d')})"
                   if label in ('coming up', 'next week', 'this week', 'last week')
                   else f"{label.capitalize()} ({day.strftime('%A %b %-d')})")
        text = render_digest(name, facts, heading)
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
        text, cited, result = brief.focus_section(facts)
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
    result = llm.chat(SYSTEM, f'Context items:\n\n{context}\n\nQuestion: {question}\n{instruction}',
                      max_tokens=300)
    blocks = {n: context_block(context, n) for n in labels}
    text, dropped, added = ground_citations(result['text'].strip(), blocks, list(labels))
    text, cited, ungrounded = verify(text, labels)
    cant = CANT_FIND.lower().rstrip('.') in text.lower()
    return {
        'question': question, 'answer': text, 'cited': [] if cant else cited, 'found': not cant,
        'cites_dropped': dropped, 'cites_added': added,
        'ungrounded_sentences': [] if cant else ungrounded, 'retrieved': list(labels.values()),
        'intents': [name], 'pulls': {'digest': len(facts)},
        'prompt_tokens': result['prompt_tokens'], 'completion_tokens': result['completion_tokens'],
        'cost': result['cost'], 'projected_cost': result['projected_cost'],
        'seconds': time.time() - started,
    }
