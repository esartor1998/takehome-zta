"""Paths, the fixed clock and model settings"""
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = Path(os.environ.get('FOUNDER_RAW', ROOT / 'data' / 'raw'))


def load_dotenv(path=ROOT / '.env'):
    """Read KEY=VALUE lines into os.environ without overriding what is already
    set. Values are never printed or logged, and .env is gitignored"""
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('\'"'))
    except OSError:
        pass  # no .env is fine, local models need no key


load_dotenv()

# a model is named 'provider:name', like 'ollama:llama3.2:latest' or
# 'anthropic:claude-haiku-4-5-20251001'. a bare name means ollama
CHAT_MODEL = os.environ.get('FOUNDER_MODEL', 'ollama:llama3.2:latest')
EMBED_MODEL = os.environ.get('FOUNDER_EMBED_MODEL', 'nomic-embed-text')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_KEY', '')


def model_slug(spec):
    return ''.join(c if c.isalnum() else '-' for c in spec).strip('-')


# the store depends on the model: decision labels are extracted by it at ingest
# time, so each model gets its own state directory and swapping one is a
# re-ingest (the llm cache makes a repeat of the same model free)
def use_model(spec):
    """Point the module-level paths at the state for one model"""
    global CHAT_MODEL, STATE_DIR, DB_PATH, CHROMA_PATH, LLM_CACHE_PATH
    CHAT_MODEL = spec if ':' in spec and spec.split(':')[0] in ('ollama', 'anthropic', 'openai') \
        else f'ollama:{spec}'
    STATE_DIR = Path(os.environ.get('FOUNDER_STATE', ROOT / '.state')) / model_slug(CHAT_MODEL)
    DB_PATH = STATE_DIR / 'context.db'
    CHROMA_PATH = STATE_DIR / 'chroma'
    LLM_CACHE_PATH = STATE_DIR / 'llm_cache.json'


use_model(CHAT_MODEL)

# the simulated clock. we never call datetime.now() anywhere: the machine date
# is nowhere near the dataset, so "today" would silently match nothing
NOW = datetime(2026, 3, 15, 14, 0, 0, tzinfo=timezone.utc)

# the founder in this simulation, used for "my meetings" and "waiting on me"
FOUNDER_PERSON_ID = 'P1'

# the week is mon..sun around NOW (mon mar 9 to sun mar 15)
WEEK_START = datetime(2026, 3, 9, 0, 0, 0, tzinfo=timezone.utc)

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')

# ollama silently truncates prompts past num_ctx, and the system prompt is the
# first thing to go. we set it explicitly and check prompt_eval_count after
NUM_CTX = 8192
KEEP_ALIVE = '30m'  # keeps the model warm so load time is not charged to answers

# usd per million tokens (input, output). local models are free to run, so
# 'projected' uses the PROJECTED_* rate to say what the same traffic would cost
# on a hosted model. add a line here when a new hosted model is wired in
PRICES = {
    'claude-haiku-4-5-20251001': (1.0, 5.0),
}
PROJECTED_PRICE_IN = 1.0
PROJECTED_PRICE_OUT = 5.0

# qwen3 and later think by default, which adds seconds of hidden tokens per
# call. we turn it off for latency and note it in the benchmark
THINKING = os.environ.get('FOUNDER_THINK', '0') == '1'


def iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
