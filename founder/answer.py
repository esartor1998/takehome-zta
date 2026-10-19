"""Question answering: retrieve, render numbered context, answer, verify cites.

The model cites with short numbers like [3]. We map them back to real item ids
in code, because a 3B model copying a 16 character hex id or a slack ts will
mangle it sometimes, and a dropped digit is a citation to nothing.
"""
import re
import time

from . import config, llm, retrieve, store

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
Answer: Priya Nair owns the billing migration [2]. Daniel Kim asked to push it by a week [4][5]."""

# extra instruction by detected intent. a bare 'what should I know' makes the
# 3B model refuse, so we say what a good answer to that kind of question covers
MODE_HINTS = {
    'meetings': 'Cover: the meeting title, its time, who attends, and anything that changed '
                '(a reschedule, a cancelled earlier slot) with the reason.',
    'blocked': 'List each blocked issue as: identifier, title, owner.',
    'decisions': 'State the current decision first, then what it replaced and who changed it.',
}

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
    return f"{line}\n    {row['body'][:BODY_CHARS]}"


def expand_decision_context(conn, ids, limit=3):
    """For retrieved items that belong to a decision topic, make sure the
    current state of that topic is in the context. Otherwise a question that
    matches the old wording retrieves only the superseded side of a reversal."""
    topics = []
    for item_id in ids:
        row = conn.execute('SELECT topic FROM decisions WHERE item_id=?', (item_id,)).fetchone()
        if row and row['topic'] not in topics:
            topics.append(row['topic'])
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


def build_context(conn, ids):
    names = {r['id']: r['name'] for r in conn.execute('SELECT id, name FROM people')}
    labels, lines = {}, []
    for number, item_id in enumerate(ids, 1):
        row = conn.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        labels[number] = item_id
        lines.append(render_item(conn, row, number, names))
    return labels, '\n\n'.join(lines)


def _content_words(text):
    return {w for w in re.findall(r'[a-z0-9]+', text.lower()) if len(w) > 2 and w not in retrieve.STOP}


def repair_citations(text, context_by_label):
    """Attach a citation to sentences the model left bare, but only when one
    retrieved item clearly says the same thing: at least two shared content
    words and half of the sentence covered. The 3B model drops markers on short
    answers about 1 time in 5, and a bare correct sentence is a harness miss,
    not a hallucination. Anything weaker stays uncited and is reported"""
    out = []
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        if sentence.strip() and not CITE_RE.search(sentence) and len(sentence.split()) > 3 \
                and CANT_FIND.lower().rstrip('.') not in sentence.lower():
            words = _content_words(sentence)
            best = max(context_by_label, key=lambda n: len(words & _content_words(context_by_label[n])),
                       default=None)
            shared = len(words & _content_words(context_by_label[best])) if best else 0
            if best and shared >= 2 and shared / max(1, len(words)) >= 0.5:
                sentence = sentence.rstrip() + f' [{best}]'
        out.append(sentence)
    return ' '.join(out)


def verify(text, labels):
    """Map [n] to ids, drop markers that point at nothing, and count sentences
    that state something without a valid citation. Returns (text, cited, ungrounded)."""
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


def ask(conn, question, k=10):
    started = time.time()
    found = retrieve.retrieve(conn, question, k=k)
    hints = ' '.join(MODE_HINTS[i] for i in found['intents'] if i in MODE_HINTS)
    ids = expand_decision_context(conn, found['ids'])
    labels, context = build_context(conn, ids)
    result = llm.chat(SYSTEM, f'Context items:\n\n{context}\n\nQuestion: {question}\n{hints}', max_tokens=300)
    # history is never a repair target: a bare 'ship date is Mar 22' must not
    # get pinned on the stale record that says Mar 20 just because they share words
    bodies = {n: block for n in labels if not re.search(
        r'\((?:[^)]*; )?(STALE|SUPERSEDED|CANCELLED)', block := context_block(context, n))}
    repaired = repair_citations(result['text'].strip(), bodies)
    text, cited, ungrounded = verify(repaired, labels)
    cant = CANT_FIND.lower().rstrip('.') in text.lower()
    return {
        'question': question, 'answer': text, 'cited': [] if cant else cited,
        'found': not cant, 'ungrounded_sentences': [] if cant else ungrounded,
        'retrieved': ids, 'intents': found['intents'], 'pulls': found['pulls'],
        'prompt_tokens': result['prompt_tokens'], 'completion_tokens': result['completion_tokens'],
        'seconds': time.time() - started,
    }
