"""First-name matching without a hand-kept nickname table.

People get new nicknames all the time, so the roster's first names are the only
fixed input. A token (dan, becky, liz) stands for a roster first name when
  1. it is a truncation of it: a prefix of three letters or more (dan, pri, marc)
  2. or the embedding model puts it closest to that one roster name by a wide gap. 'A wide gap'
     is a margin over the runner-up, not an absolute cosine, because junk words
     score about 0.5 against any name while real nicknames score 0.65 to 0.9

Neither rule alone is enough. Embeddings miss short truncations (bec, sof, han
land on other names) and prefixes miss becky, liz and bob. Both leave 'mark'
unresolved when the roster has Marcus and Michael, which is right: it could be
either. The embedding function is injected so the rules can be tested without a
model, and without one only the prefix rule runs
"""
import re

MIN_PREFIX = 3
EMBED_COSINE = 0.65       # the closest roster name must be at least this similar
EMBED_MARGIN = 0.08       # and this far ahead of the second closest
DIMINUTIVE = re.compile(r'[a-z]?(y|ie|ey)')       # sam -> sammy, dan -> danny, will -> willie


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


class NameSense:
    def __init__(self, firsts, embed=None):
        self.firsts = sorted(set(firsts))
        self.embed = embed
        self._vec = {}
        self._seen = {}

    def _vectors(self, words):
        missing = [w for w in dict.fromkeys(words) if w not in self._vec]
        if missing:
            self._vec.update(zip(missing, self.embed(missing, kind='query')))
        return [self._vec[w] for w in words]

    def prefix_hits(self, token):
        return {f for f in self.firsts if len(token) >= MIN_PREFIX and len(token) < len(f) and f.startswith(token)}

    def resolve(self, token, use_embedding=True):
        """The roster first names a token could stand for: itself, the names it truncates, or
        the one name it is closest to by a wide gap"""
        token = token.lower().strip('.')
        if token in self.firsts:
            return {token}
        if not token.isalpha() or len(token) < MIN_PREFIX:
            return set()
        hits = self.prefix_hits(token)
        if hits or not use_embedding or not self.embed or len(self.firsts) < 2:
            return hits
        if token not in self._seen:
            # 'daniella' extends 'daniel' into a different name, 'sammy' only softens 'sam'
            candidates = [f for f in self.firsts
                          if not (token.startswith(f) and len(token) > len(f) and not DIMINUTIVE.fullmatch(token[len(f):]))]
            found = set()
            if candidates:
                vectors = self._vectors([token] + candidates)
                scored = sorted(((_cosine(vectors[0], v), f) for v, f in zip(vectors[1:], candidates)), reverse=True)
                runner = scored[1][0] if len(scored) > 1 else 0.0
                if scored[0][0] >= EMBED_COSINE and scored[0][0] - runner >= EMBED_MARGIN:
                    found = {scored[0][1]}
            self._seen[token] = found
        return self._seen[token]
