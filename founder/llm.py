"""Thin ollama client on urllib, so the only third-party dependency is chroma.

Everything model-shaped goes through chat() and embed(). Swapping in a hosted
model later means rewriting this file and nothing else.
"""
import hashlib
import json
import time
import urllib.request

from . import config

_cache = None


def _post(path, payload, timeout=300):
    req = urllib.request.Request(
        config.OLLAMA_URL + path, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _load_cache():
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(config.LLM_CACHE_PATH.read_text())
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _save_cache():
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    config.LLM_CACHE_PATH.write_text(json.dumps(_cache))


def chat(system, user, schema=None, cache=False, max_tokens=700):
    """One chat turn. Returns dict(text, prompt_tokens, completion_tokens, seconds).

    schema is a json schema passed as ollama's `format`, which constrains
    decoding. cache=True is for ingest-time extraction only: the key is the
    full prompt, so re-ingesting unchanged data costs no model calls.
    """
    key = hashlib.sha256(json.dumps([config.CHAT_MODEL, system, user, schema]).encode()).hexdigest()
    if cache and key in _load_cache():
        return dict(_load_cache()[key], cached=True)
    payload = {
        'model': config.CHAT_MODEL, 'stream': False, 'keep_alive': config.KEEP_ALIVE,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'options': {'num_ctx': config.NUM_CTX, 'temperature': 0, 'seed': 7,
                    'num_predict': max_tokens},
    }
    if schema:
        payload['format'] = schema
    start = time.time()
    resp = _post('/api/chat', payload)
    out = {'text': resp['message']['content'],
           'prompt_tokens': resp.get('prompt_eval_count', 0),
           'completion_tokens': resp.get('eval_count', 0),
           'seconds': time.time() - start, 'cached': False}
    # if the prompt filled the window the oldest tokens were dropped, which is
    # the system prompt. fail loudly instead of answering without instructions
    if out['prompt_tokens'] >= config.NUM_CTX - 16:
        raise RuntimeError('prompt reached num_ctx, context was truncated')
    if cache:
        _load_cache()[key] = {k: v for k, v in out.items() if k != 'cached'}
        _save_cache()
    return out


def embed(texts, kind='document'):
    """Embed with nomic's task prefixes. Without them retrieval quality drops."""
    prefix = 'search_document: ' if kind == 'document' else 'search_query: '
    vectors = []
    for start in range(0, len(texts), 32):
        batch = [prefix + t[:2000] for t in texts[start:start + 32]]
        vectors.extend(_post('/api/embed', {'model': config.EMBED_MODEL, 'input': batch,
                                            'keep_alive': config.KEEP_ALIVE})['embeddings'])
    return vectors


def warm():
    """Load both models so first-call latency is not charged to a question."""
    chat('ok', 'ok', max_tokens=1)
    embed(['ok'])
