"""Paths, the fixed clock and model settings."""
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = Path(os.environ.get('FOUNDER_RAW', ROOT / 'data' / 'raw'))
STATE_DIR = Path(os.environ.get('FOUNDER_STATE', ROOT / '.state'))
DB_PATH = STATE_DIR / 'context.db'
CHROMA_PATH = STATE_DIR / 'chroma'
LLM_CACHE_PATH = STATE_DIR / 'llm_cache.json'

# the simulated clock. we never call datetime.now() anywhere: the machine date
# is nowhere near the dataset, so "today" would silently match nothing
NOW = datetime(2026, 3, 15, 14, 0, 0, tzinfo=timezone.utc)

# the founder in this simulation, used for "my meetings" and "waiting on me"
FOUNDER_PERSON_ID = 'P1'

# the week is mon..sun around NOW (mon mar 9 to sun mar 15)
WEEK_START = datetime(2026, 3, 9, 0, 0, 0, tzinfo=timezone.utc)

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
CHAT_MODEL = os.environ.get('FOUNDER_MODEL', 'llama3.2:latest')
EMBED_MODEL = os.environ.get('FOUNDER_EMBED_MODEL', 'nomic-embed-text')

# ollama silently truncates prompts past num_ctx, and the system prompt is the
# first thing to go. we set it explicitly and check prompt_eval_count after
NUM_CTX = 8192
KEEP_ALIVE = '30m'  # keeps the model warm so load time is not charged to answers

# hosted-model prices (usd per million tokens) used only to project what this
# would cost off the rig. local runs cost nothing
PROJECTED_PRICE_IN = 1.0
PROJECTED_PRICE_OUT = 5.0


def iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
