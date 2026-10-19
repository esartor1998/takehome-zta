"""Ingest pipeline: raw exports -> identity -> normalize -> dedupe -> topics ->
decisions -> sqlite + chroma. Run as `founder ingest`."""
import subprocess
import sys
import time

from . import config, dedupe, extract, llm, store
from .identity import IdentityResolver
from .normalize import normalize_all


def ensure_raw_data():
    """data/ is gitignored (it is a symlink on the dev rig), so a fresh clone
    regenerates it from the seeded script"""
    if (config.RAW_DIR / 'gmail_messages.jsonl').exists():
        return
    print('raw data missing, running synthetic_data_generator.py')
    subprocess.run([sys.executable, 'synthetic_data_generator.py'], cwd=config.ROOT, check=True)


def embed_text(item, ident):
    """What we embed: a readable line with who and when, then the content.
    Names in the text are what let 'what did Daniel say' find his email even
    when it was sent from a personal address"""
    author = ident.name(item['author']) if item['author'] else 'unknown sender'
    day = item['ts'][:10]
    head = {'email': f"Email from {author} on {day}, subject: {item['title']}",
            'event': f"Calendar event ({item['status']}) {item['title']} on {day}",
            'message': f"Slack {item['title']} message from {author} on {day}",
            'issue': f"Linear issue {item['meta'].get('identifier', '')} ({item['status']}) "
                     f"assigned to {author}, {item['title']}"}[item['kind']]
    return f"{head}\n{item['body']}".strip()


def run(skip_decisions=False):
    started = time.time()
    ensure_raw_data()
    ident = IdentityResolver(config.RAW_DIR)
    items = normalize_all(config.RAW_DIR, ident)
    for item in items:
        item['embed_text'] = embed_text(item, ident)
        item['state'] = 'quarantined' if 'after_now' in item['flags'] else 'current'
        item.update(superseded_by=None, dup_group=None, topic=None)

    print(f'embedding {len(items)} items with {config.EMBED_MODEL}')
    vectors = dict(zip((i['id'] for i in items), llm.embed([i['embed_text'] for i in items])))

    dedupe.collapse_linear_snapshots(items)
    dupe_pairs = dedupe.find_cross_source_dupes(items, vectors)
    by_id = {i['id']: i for i in items}
    for first, second in dupe_pairs:
        # the earlier post is canonical. both stay searchable and citable
        group = by_id[first]['dup_group'] or first
        by_id[first]['dup_group'] = by_id[second]['dup_group'] = group

    topics, links = dedupe.build_topics(items, dupe_pairs)
    for topic_id, members in topics.items():
        for member in members:
            by_id[member]['topic'] = topic_id

    decisions = [] if skip_decisions else extract.extract_decisions(items, topics, ident)

    conn = store.reset()
    store.write_items(conn, items, ident.people)
    conn.executemany('INSERT INTO links VALUES (?,?,?)', links)
    extract.write_decisions(conn, decisions)
    conn.commit()
    store.write_vectors(store.reset_vectors(), items, vectors)

    print(f'{len(items)} items, {len(dupe_pairs)} cross-source dupes, '
          f'{sum(len(m) > 1 for m in topics.values())} multi-item topics, '
          f'{len(decisions)} decision events, {time.time() - started:.1f}s')
    return {'items': items, 'dupe_pairs': dupe_pairs, 'topics': topics, 'decisions': decisions}
