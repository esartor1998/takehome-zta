"""Model access. Everything model-shaped goes through chat() and embed().

A model is named 'provider:name'. Two providers exist today (ollama for local,
anthropic for hosted) and adding a third is one more _call_* function and one
line in PROVIDERS. Nothing outside this file knows which provider answered.

Embeddings stay on local ollama on purpose: the vector index is built once and
should not change when the chat model does. Swapping the embedding model means
re-ingesting, since vectors from two models are not comparable
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

from . import config

_cache = None

# running totals by role ('answer', 'extract', 'judge', ...). the benchmark
# reads and resets these to report calls, tokens, seconds and cost per task
USAGE = {}
COUNTERS = {'schema_failures': 0, 'retries': 0}

RETRY_STATUS = (429, 500, 502, 503, 529)
MAX_RETRIES = 4
BACKOFF_SECONDS = 1.5


class ModelError(RuntimeError):
    pass


def split_spec(spec):
    provider, _, name = spec.partition(':')
    if provider not in PROVIDERS:
        return 'ollama', spec
    return provider, name


def reset_usage():
    USAGE.clear()
    COUNTERS.update(schema_failures=0, retries=0)


def _record(role, out, cost):
    row = USAGE.setdefault(role, {'calls': 0, 'cached': 0, 'prompt_tokens': 0,
                                  'completion_tokens': 0, 'seconds': 0.0, 'cost': 0.0})
    if out.get('cached'):
        row['cached'] += 1
        return
    row['calls'] += 1
    row['prompt_tokens'] += out['prompt_tokens']
    row['completion_tokens'] += out['completion_tokens']
    row['seconds'] += out['seconds']
    row['cost'] += cost


def _http(url, payload, headers, timeout):
    """POST json with retry on rate limits and server errors. The hosted api
    returns 429 and 529 under load, and a benchmark that dies on one is useless"""
    body = json.dumps(payload).encode()
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors='replace')[:300]
            if err.code in RETRY_STATUS and attempt < MAX_RETRIES:
                COUNTERS['retries'] += 1
                time.sleep(BACKOFF_SECONDS * 2 ** attempt)
                continue
            raise ModelError(f'{url} returned {err.code}: {detail}') from None
        except (urllib.error.URLError, TimeoutError) as err:
            if attempt < MAX_RETRIES:
                COUNTERS['retries'] += 1
                time.sleep(BACKOFF_SECONDS * 2 ** attempt)
                continue
            raise ModelError(f'{url} unreachable: {err}') from None


# ---- providers ------------------------------------------------------------

def _call_ollama(name, system, user, schema, max_tokens):
    payload = {
        'model': name, 'stream': False, 'keep_alive': config.KEEP_ALIVE,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'options': {'num_ctx': config.NUM_CTX, 'temperature': 0, 'seed': 7,
                    'num_predict': max_tokens},
    }
    # the qwen3 line and later think by default. the flag is only sent to models
    # that accept it, since others reject unknown fields
    if name.startswith(('qwen3', 'deepseek-r1', 'gpt-oss')):
        payload['think'] = config.THINKING
    if schema:
        payload['format'] = schema
    resp = _http(config.OLLAMA_URL + '/api/chat', payload,
                 {'Content-Type': 'application/json'}, timeout=900)
    prompt_tokens = resp.get('prompt_eval_count', 0)
    # if the prompt filled the window the oldest tokens were dropped, which is
    # the system prompt. fail loudly instead of answering without instructions
    if prompt_tokens >= config.NUM_CTX - 16:
        raise ModelError('prompt reached num_ctx, context was truncated')
    return {'text': resp['message']['content'], 'prompt_tokens': prompt_tokens,
            'completion_tokens': resp.get('eval_count', 0)}


def _call_anthropic(name, system, user, schema, max_tokens):
    if not config.ANTHROPIC_KEY:
        raise ModelError('no ANTHROPIC_API_KEY or ANTHROPIC_KEY in the environment or .env')
    payload = {'model': name, 'max_tokens': max_tokens, 'temperature': 0, 'system': system,
               'messages': [{'role': 'user', 'content': user}]}
    if schema:
        # a forced tool call is how this api returns schema-shaped json. the
        # tool input comes back already parsed, and we re-serialise it so the
        # caller sees the same text it would get from any other provider
        payload['tools'] = [{'name': 'respond', 'description': 'Return the result',
                             'input_schema': schema}]
        payload['tool_choice'] = {'type': 'tool', 'name': 'respond'}
    resp = _http('https://api.anthropic.com/v1/messages', payload,
                 {'Content-Type': 'application/json', 'x-api-key': config.ANTHROPIC_KEY,
                  'anthropic-version': '2023-06-01'}, timeout=120)
    text = ''
    for block in resp['content']:
        if block['type'] == 'tool_use':
            text = json.dumps(block['input'])
        elif block['type'] == 'text' and not schema:
            text += block['text']
    usage = resp.get('usage', {})
    return {'text': text, 'prompt_tokens': usage.get('input_tokens', 0),
            'completion_tokens': usage.get('output_tokens', 0)}


def _call_openai(name, system, user, schema, max_tokens):
    """Any server speaking the openai chat completions api: openai itself,
    openrouter, vllm, lm studio, or ollama's own /v1. FOUNDER_OPENAI_BASE picks
    the server and OPENAI_API_KEY (or OPENAI_KEY) the key (local servers ignore it)"""
    base = os.environ.get('FOUNDER_OPENAI_BASE', 'https://api.openai.com/v1').rstrip('/')
    hosted = base.startswith('https://api.openai.com')
    payload = {'model': name, 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
    if hosted:
        # the current models reject max_tokens and a fixed temperature, and count the tokens they
        # spend reasoning against the limit, so a small budget would come back empty
        payload['max_completion_tokens'] = max_tokens + OPENAI_REASONING_ROOM
    else:
        payload.update({'max_tokens': max_tokens, 'temperature': 0})
    if schema:
        payload['response_format'] = {'type': 'json_schema',
                                      'json_schema': {'name': 'respond', 'schema': schema, 'strict': False}}
    if hosted and not config.OPENAI_KEY:
        raise ModelError('no OPENAI_API_KEY or OPENAI_KEY in the environment or .env')
    resp = _http(base + '/chat/completions', payload,
                 {'Content-Type': 'application/json', 'Authorization': f'Bearer {config.OPENAI_KEY or "none"}'},
                 timeout=900)
    usage = resp.get('usage', {})
    return {'text': resp['choices'][0]['message']['content'] or '',
            'prompt_tokens': usage.get('prompt_tokens', 0), 'completion_tokens': usage.get('completion_tokens', 0)}


OPENAI_REASONING_ROOM = 1500    # tokens a hosted reasoning model may spend thinking, on top of the answer


PROVIDERS = {'ollama': _call_ollama, 'anthropic': _call_anthropic, 'openai': _call_openai}


# ---- public api -----------------------------------------------------------

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


def forget_cache():
    """Drop the in-memory cache. Needed when the state directory changes"""
    global _cache
    _cache = None


def cost_of(provider, name, prompt_tokens, completion_tokens):
    """Actual spend. Local models are free"""
    if provider == 'ollama':
        return 0.0
    price_in, price_out = config.PRICES.get(name, (config.PROJECTED_PRICE_IN, config.PROJECTED_PRICE_OUT))
    return (prompt_tokens * price_in + completion_tokens * price_out) / 1e6


def chat(system, user, schema=None, cache=False, max_tokens=700, model=None, role='answer'):
    """One chat turn. Returns dict(text, prompt_tokens, completion_tokens, seconds, cost).

    schema is a json schema: ollama constrains decoding with it, anthropic gets
    it as a forced tool call. cache=True is for ingest-time extraction only,
    the key is the full prompt and the model, so re-ingesting unchanged data
    with the same model makes no calls
    """
    spec = model or config.CHAT_MODEL
    provider, name = split_spec(spec)
    key = hashlib.sha256(json.dumps([provider, name, system, user, schema]).encode()).hexdigest()
    if cache and key in _load_cache():
        out = dict(_load_cache()[key], cached=True)
        _record(role, out, 0.0)
        return out
    start = time.time()
    out = PROVIDERS[provider](name, system, user, schema, max_tokens)
    out['seconds'] = time.time() - start
    out['cached'] = False
    out['cost'] = cost_of(provider, name, out['prompt_tokens'], out['completion_tokens'])
    out['projected_cost'] = (out['prompt_tokens'] * config.PROJECTED_PRICE_IN
                             + out['completion_tokens'] * config.PROJECTED_PRICE_OUT) / 1e6
    _record(role, out, out['cost'])
    if cache:
        _load_cache()[key] = {k: v for k, v in out.items() if k != 'cached'}
        _save_cache()
    return out


def parse_json(text, fallback):
    """Parse model json, counting failures so a benchmark can report them"""
    try:
        return json.loads(text)
    except ValueError:
        COUNTERS['schema_failures'] += 1
        return fallback


def embed(texts, kind='document'):
    """Embed with nomic's task prefixes. Without them retrieval quality drops"""
    prefix = 'search_document: ' if kind == 'document' else 'search_query: '
    vectors = []
    for start in range(0, len(texts), 32):
        batch = [prefix + t[:2000] for t in texts[start:start + 32]]
        resp = _http(config.OLLAMA_URL + '/api/embed',
                     {'model': config.EMBED_MODEL, 'input': batch, 'keep_alive': config.KEEP_ALIVE},
                     {'Content-Type': 'application/json'}, timeout=300)
        vectors.extend(resp['embeddings'])
    return vectors


def warm(model=None):
    """Load the chat model and the embedder so first-call latency is not
    charged to a question. Returns seconds spent, which the benchmark reports
    as load time"""
    start = time.time()
    chat('ok', 'ok', max_tokens=2, model=model, role='warm')
    embed(['ok'])
    return time.time() - start


def placement(model=None):
    """Where a local model is resident: bytes in total and bytes in vram. A
    27b model on a 6gb card shows up here as mostly cpu, which is the number that
    explains its latency. None for hosted models"""
    provider, name = split_spec(model or config.CHAT_MODEL)
    if provider != 'ollama':
        return None
    try:
        with urllib.request.urlopen(config.OLLAMA_URL + '/api/ps', timeout=10) as resp:
            for m in json.load(resp).get('models', []):
                if m['name'].startswith(name.split(':')[0]) and (':' not in name or m['name'] == name
                                                                  or name.endswith('latest')):
                    return {'size_gb': m['size'] / 1e9, 'vram_gb': m.get('size_vram', 0) / 1e9}
    except (OSError, ValueError):
        pass
    return None
