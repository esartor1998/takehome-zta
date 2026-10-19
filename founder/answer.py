"""Question answering: retrieve, render numbered context, answer, verify cites.

The model cites with short numbers like [3]. We map them back to real item ids
in code, because a 3B model copying a 16 character hex id or a slack ts will
mangle it sometimes, and a dropped digit is a citation to nothing
"""
import re
import time
from datetime import datetime

from . import brief, config, llm, retrieve, store

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
    'blocked': 'List each blocked issue as: identifier, title, owner.',
    'decisions': 'State the current decision first, then what it replaced and who changed it.',
}

# open questions with no single item as the answer. we answer these from the
# same verified facts the morning brief is built from, because retrieval over
# raw items gave 'the PR for the billing migration was merged' (nothing in the
# data says that) for 'what happened this week'
DIGEST_INTENTS = (
    ('followups', r'follow.?ups?|\bmissing\b|waiting on me|unanswered|owe a reply', {'ask'},
     'Say which asks are still open and which already look handled, with the reason. If none '
     'is open, say nothing is waiting on you.'),
    ('customers', r'\bcustomers?\b', {'customer'},
     'List each customer with how often it came up.'),
    ('focus', r'\bfocus\b|priorit\w+|what should i (do|work)', None,
     'Give up to 3 priorities, most urgent first, one line each. Skip items marked no action needed.'),
    ('company', r'across the company|what happened|what.s going on|company', None,
     'Summarise each item in one sentence, most important first.'),
)
DIGEST_LIMIT = 8

CITE_RE = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')


def _when(iso_text):
    from datetime import datetime
    dt = datetime.fromisoformat(iso_text.replace('Z', '+00:00'))
    return dt.strftime('%a %Y-%m-%d %H:%M UTC')


def render_item(conn, item, label, people_names):
    """One numbered context entry. Ids stay out of the text on purpose: the
    model quotes headers it can see, and the number is all it needs to cite"""
    row = store.row_to_item(item)
    author = people_names.get(row['author'], 'unknown sender')
    tags = []
    if row['kind'] == 'event':
        tags.append(row['status'].upper())
        attendees = ', '.join(people_names.get(p, p) for p in row['people'])
        head = (f"[{label}] calendar event '{row['title']}', {_when(row['start'])} to "
                f"{_when(row['end'])}, attendees: {attendees}, organizer: {author}")
    elif row['kind'] == 'email':
        head = f"[{label}] email from {author}, {_when(row['ts'])}, subject: {row['title']}"
    elif row['kind'] == 'message':
        head = f"[{label}] slack {row['title']} message from {author}, {_when(row['ts'])}"
    else:
        head = (f"[{label}] linear issue {row['meta'].get('identifier')} ({row['status']}), "
                f"owner {author}, updated {_when(row['ts'])}, title: {row['title']}")

    decision = conn.execute('SELECT * FROM decisions WHERE item_id=?', (row['id'],)).fetchone()
    if decision:
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
        tags.append('data issues: ' + ','.join(row['flags']))
    line = head + (f" ({'; '.join(tags)})" if tags else '')
    body = row['body'][:BODY_CHARS]
    if row['kind'] == 'event' and body:
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
    names = {r['id']: r['name'] for r in conn.execute('SELECT id, name FROM people')}
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


def digest_facts(conn, question):
    """(intent, facts) when the question is an open one, else None"""
    for name, pattern, cats, instruction in DIGEST_INTENTS:
        if re.search(pattern, question, re.I):
            facts = brief.collect_facts(conn)
            if cats:
                facts = [f for f in facts if f['cat'] in cats]
            return name, facts[:DIGEST_LIMIT], instruction
    return None


def ask(conn, question, k=10):
    started = time.time()
    digest = digest_facts(conn, question)
    if digest:
        return ask_digest(conn, question, digest, started)
    found = retrieve.retrieve(conn, question, k=k)
    intents = list(found['intents'])
    if re.search(r'\bemails?\b', question, re.I) and 'meetings' in intents:
        intents.append('emails')
    hints = ' '.join(MODE_HINTS[i] for i in intents if i in MODE_HINTS)
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
        'seconds': time.time() - started,
    }


def ask_digest(conn, question, digest, started):
    name, facts, instruction = digest
    if not facts:
        return {'question': question, 'answer': 'Nothing needs your attention here.', 'cited': [],
                'found': True, 'cites_dropped': 0, 'cites_added': 0, 'ungrounded_sentences': [],
                'retrieved': [], 'intents': [name], 'pulls': {'digest': 0}, 'prompt_tokens': 0,
                'completion_tokens': 0, 'seconds': time.time() - started}
    if name == 'focus':
        # same ranking and phrasing as the brief's focus section, so the two
        # cannot disagree about what matters today
        text, cited, result = brief.focus_section(facts)
        return {'question': question, 'answer': text, 'cited': cited, 'found': True,
                'cites_dropped': 0, 'cites_added': 0, 'ungrounded_sentences': [],
                'retrieved': [i for f in facts for i in f['ids']], 'intents': [name],
                'pulls': {'digest': len(facts)}, 'prompt_tokens': result['prompt_tokens'],
                'completion_tokens': result['completion_tokens'], 'seconds': time.time() - started}
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
        'seconds': time.time() - started,
    }
