"""Dedupe and topic linking over normalised items.

Three separate jobs:
  collapse_linear_snapshots  several records share one issue identifier, only
                             the latest is current
  find_cross_source_dupes    the same update posted in two places
  build_topics               union-find over everything that talks about the
                             same thing, so a decision and its reversal land
                             in one cluster even across tools
"""
import re
from datetime import datetime, timedelta

from .normalize import ACME_RE

# same author, different source, close in time, and similar text. 3h covers the
# slowest repost in the data (a slack post 2h after the email). the cosine
# floor keeps an unrelated slack one-liner from merging into an email
DUPE_WINDOW = timedelta(hours=3)
DUPE_MIN_COSINE = 0.80

# embeddings alone merged unrelated one-liners from the same person, because
# the 'who and when' header we embed dominates a short body. so a pair also
# needs real content overlap: at least this many shared words, covering at
# least this share of the shorter text
MIN_SHARED_WORDS = 2
MIN_SHARED_RATIO = 0.5
STOPWORDS = frozenset('the a an and or to of in on at for is are was be we i you it this that '
                      'with as by from up so if not no can will our my me'.split())

# a calendar title only links to an email or message when it is specific. one
# word titles like 'Standup' or 'Retro' appear everywhere and would glue
# unrelated chatter together
MIN_TITLE_WORDS = 2
MIN_TITLE_CHARS = 8


def _ts(item):
    return datetime.fromisoformat(item['ts'].replace('Z', '+00:00'))


def collapse_linear_snapshots(items):
    """Mark every linear record except the newest per identifier as superseded"""
    by_ident = {}
    for item in items:
        if item['source'] == 'linear':
            by_ident.setdefault(item['meta']['identifier'], []).append(item)
    for versions in by_ident.values():
        versions.sort(key=lambda i: i['ts'])
        for older, newer in zip(versions, versions[1:]):
            older['state'] = 'superseded'
            older['superseded_by'] = newer['id']
    return items


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def _words(item):
    return {w for w in re.findall(r'[a-z0-9]+', item['body'].lower())
            if w not in STOPWORDS and len(w) > 1}


def _overlaps(first, second):
    a, b = _words(first), _words(second)
    shared = len(a & b)
    return shared >= MIN_SHARED_WORDS and shared / max(1, min(len(a), len(b))) >= MIN_SHARED_RATIO


def find_cross_source_dupes(items, vectors):
    """Group same-author near-duplicates across sources. Returns list of pairs"""
    by_author = {}
    for item in items:
        if item['author'] and item['source'] in ('gmail', 'slack') and 'after_now' not in item['flags']:
            by_author.setdefault(item['author'], []).append(item)
    pairs = []
    for group in by_author.values():
        group.sort(key=lambda i: i['ts'])
        for i, first in enumerate(group):
            for second in group[i + 1:]:
                if _ts(second) - _ts(first) > DUPE_WINDOW:
                    break
                if first['source'] == second['source']:
                    continue
                if (_cosine(vectors[first['id']], vectors[second['id']]) >= DUPE_MIN_COSINE
                        and _overlaps(first, second)):
                    pairs.append((first['id'], second['id']))
    return pairs


class _UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def _norm_title(text):
    text = re.sub(r'^(re|fwd?):\s*', '', text.strip(), flags=re.I)
    text = re.sub(r'\s*#\d+$|\s*\(ACME-\d+\)$', '', text)
    return re.sub(r'\W+', ' ', text).strip().lower()


def build_topics(items, dupe_pairs):
    """Assign each item a topic id. Returns (topics, links).

    Link reasons: thread, ref (shared ACME id), title (normalised subject equals
    an issue title, or an event title appears in a message), dupe
    """
    uf = _UnionFind()
    links = []

    def link(a, b, reason):
        uf.union(a, b)
        links.append((a, b, reason))

    # thread and issue identity
    first_in = {}
    for item in items:
        uf.find(item['id'])
        key = item['thread_key']
        if key in first_in:
            link(first_in[key], item['id'], 'thread')
        else:
            first_in[key] = item['id']

    # shared issue references
    ref_owner = {}
    for item in items:
        refs = set(ACME_RE.findall(item['title'] + ' ' + item['body']))
        if item['source'] == 'linear':
            refs.add(item['meta']['identifier'])
        for ref in refs:
            if ref in ref_owner:
                link(ref_owner[ref], item['id'], 'ref')
            else:
                ref_owner[ref] = item['id']

    # issue title equals a normalised email subject
    title_owner = {}
    for item in items:
        if item['source'] == 'linear':
            title_owner.setdefault(_norm_title(item['title']), item['id'])
    for item in items:
        if item['source'] == 'gmail' and _norm_title(item['title']) in title_owner:
            link(title_owner[_norm_title(item['title'])], item['id'], 'title')

    # event titles mentioned in messages
    events = {}
    for item in items:
        if item['source'] == 'calendar':
            words = item['title'].split()
            if len(words) >= MIN_TITLE_WORDS and len(item['title']) >= MIN_TITLE_CHARS:
                events.setdefault(item['title'].lower(), item['id'])
    for item in items:
        if item['source'] in ('gmail', 'slack'):
            text = (item['title'] + ' ' + item['body']).lower()
            for title, event_id in events.items():
                if title in text:
                    link(event_id, item['id'], 'title')

    for a, b in dupe_pairs:
        link(a, b, 'dupe')

    topics = {}
    for item in items:
        topics.setdefault(uf.find(item['id']), []).append(item['id'])
    return topics, links
