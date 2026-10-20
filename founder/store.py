"""Central context layer: sqlite is the source of truth, chroma is a vector index.

Chroma only ever holds item ids, vectors and a few filter fields. Anything we
cite or display is read back out of sqlite, so the two cannot disagree about
what an item says
"""
import json
import re
import sqlite3

import chromadb
from chromadb.config import Settings

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY, source TEXT, kind TEXT, thread_key TEXT, ts TEXT,
    title TEXT, body TEXT, quoted TEXT, author TEXT, author_how TEXT,
    people TEXT, status TEXT, start TEXT, end TEXT, flags TEXT, meta TEXT,
    state TEXT DEFAULT 'current', superseded_by TEXT, dup_group TEXT,
    topic TEXT, embed_text TEXT, novelty REAL DEFAULT 0, gate REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS items_ts ON items(ts);
CREATE INDEX IF NOT EXISTS items_topic ON items(topic);
CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    title, body, who, content='', tokenize='porter unicode61'
);
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY, name TEXT, emails TEXT, slack_handle TEXT, linear_name TEXT,
    org TEXT, external INTEGER, aliases TEXT, role TEXT
);
CREATE TABLE IF NOT EXISTS links (a TEXT, b TEXT, reason TEXT);
CREATE TABLE IF NOT EXISTS vocab (term TEXT PRIMARY KEY, doc INTEGER);
CREATE TABLE IF NOT EXISTS stale_records (
    item_id TEXT PRIMARY KEY, newer_id TEXT, current_fact TEXT, why TEXT
);
CREATE TABLE IF NOT EXISTS followups (
    item_id TEXT, kind TEXT, who TEXT, whom TEXT, what TEXT, due TEXT, status TEXT, evidence TEXT, ts TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
    item_id TEXT PRIMARY KEY, topic TEXT, kind TEXT, value TEXT, retracts TEXT,
    summary TEXT, ts TEXT, status TEXT, why TEXT, source TEXT, subject TEXT, anchor INTEGER DEFAULT 0
);
"""

JSON_FIELDS = ('people', 'flags', 'meta')


def connect():
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset():
    """Drop and recreate everything. Ingest is a full rebuild, which is cheap
    here (llm calls are cached) and avoids partial-update bugs"""
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
    conn = connect()
    conn.executescript(SCHEMA)
    return conn


def _chroma():
    client = chromadb.PersistentClient(
        path=str(config.CHROMA_PATH), settings=Settings(anonymized_telemetry=False))
    return client


def reset_vectors():
    client = _chroma()
    try:
        client.delete_collection('items')
    except Exception:  # first run, nothing to delete
        pass
    return client.create_collection('items', metadata={'hnsw:space': 'cosine'})


def vector_collection():
    return _chroma().get_collection('items')


def row_to_item(row):
    item = dict(row)
    for key in JSON_FIELDS:
        item[key] = json.loads(item[key]) if item[key] else ([] if key != 'meta' else {})
    return item


def write_items(conn, items, people):
    for person in people.values():
        conn.execute('INSERT OR REPLACE INTO people VALUES (?,?,?,?,?,?,?,?,?)',
                     (person.id, person.name, json.dumps(sorted(person.emails)),
                      person.slack_handle, person.linear_name, person.org, int(person.external),
                      json.dumps(sorted(person.aliases())), person.role))
    for item in items:
        row = dict(item)
        for key in JSON_FIELDS:
            row[key] = json.dumps(row.get(key, []))
        row.setdefault('state', 'current')
        row.setdefault('superseded_by', None)
        row.setdefault('dup_group', None)
        row.setdefault('topic', None)
        row.setdefault('novelty', 0.0)
        row.setdefault('gate', 0.0)
        cols = ['id', 'source', 'kind', 'thread_key', 'ts', 'title', 'body', 'quoted',
                'author', 'author_how', 'people', 'status', 'start', 'end', 'flags', 'meta',
                'state', 'superseded_by', 'dup_group', 'topic', 'embed_text', 'novelty', 'gate']
        conn.execute(f"INSERT INTO items ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                     [row[c] for c in cols])
        names = ' '.join(people[p].name for p in [item['author']] + item['people']
                         if p and p in people)
        conn.execute('INSERT INTO items_fts(rowid, title, body, who) VALUES '
                     '((SELECT rowid FROM items WHERE id=?),?,?,?)',
                     (item['id'], f"{item['title']} {item['meta'].get('identifier', '')}".strip(), item['body'], names))
    # the words the inbox contains, unstemmed, with how many items use each. the fts
    # index holds stems ('price' for 'pricing'), which cannot correct a typo
    counts = {}
    for item in items:
        if item['state'] == 'automated':
            continue
        for word in set(re.findall(r'[a-z]{3,}', f"{item['title']} {item['body']}".lower())):
            counts[word] = counts.get(word, 0) + 1
    for person in people.values():
        for word in re.findall(r'[a-z]{3,}', ' '.join([person.name, person.org]).lower()):
            counts[word] = counts.get(word, 0) + 5
    conn.executemany('INSERT OR REPLACE INTO vocab VALUES (?,?)', counts.items())
    conn.commit()


def write_vectors(collection, items, vectors):
    for start in range(0, len(items), 200):
        chunk = items[start:start + 200]
        collection.add(
            ids=[i['id'] for i in chunk],
            embeddings=[vectors[i['id']] for i in chunk],
            metadatas=[{'source': i['source'], 'kind': i['kind'], 'state': i['state']}
                       for i in chunk])


def topic_label(conn, topic):
    """A readable name for a decision topic: the linear title if the topic has
    an issue, else the subject the model gave the newest event"""
    row = conn.execute(
        "SELECT i.title FROM decisions d JOIN items i ON i.id=d.item_id WHERE d.topic=? "
        "AND d.source='linear' ORDER BY d.ts DESC LIMIT 1", (topic,)).fetchone()
    if row:
        return re.sub(r'\s*\(ACME-\d+\)$', '', row['title'])
    # the subject of the event that changed the plan, not of a stray message that followed it
    row = conn.execute('SELECT subject FROM decisions WHERE topic=? ORDER BY anchor DESC, ts DESC LIMIT 1', (topic,)).fetchone()
    return row['subject'] if row and row['subject'] else 'plan'
