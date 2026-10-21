# Model benchmark

judge: `openai:gpt-6-luna` for every column. questions: 70.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b |
| --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | 6.4 GB, 66% on gpu |
| first call incl. load (s) | 0.7 | 9.2 | 33.5 |
| **ingest** wall (s) | 281.1 | 303.5 | 1815.1 |
| ingest model calls | 175 | 174 | 175 |
| ingest tokens in/out | 171788/24460 | 51566/30227 | 51590/14623 |
| ingest cost ($) | 0.2941 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 51/51 | 50/51 | 51/51 |
| **brief** wall (s) | 2.0 | 0.8 | 13.9 |
| brief cost ($) | 0.00109 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes |
| brief meeting in focus | yes | yes | yes |
| **ask** accuracy (judge) | 77% | 57% | 56% |
| ask accuracy, original questions (q*) | 14/18 | 11/18 | 9/18 |
| ask accuracy, vague questions (v*) | 17/23 | 14/23 | 12/23 |
| ask citation recall | 89% | 86% | 90% |
| ask citation recall, vague (v*) | 87% | 86% | 93% |
| ask citation precision | 55% | 50% | 52% |
| ask answers with a citation flag | 6 | 11 | 1 |
| ask flag precision (flagged and judged wrong) | 0% | 73% | 100% |
| ask flag recall (wrong answers that were flagged) | 0% | 27% | 3% |
| ask forbidden cites | 0 | 1 | 1 |
| ask uncited sentences | 21 | 32 | 12 |
| ask latency p50 (s) | 1.8 | 0.9 | 9.7 |
| ask latency p95 (s) | 3.5 | 3.2 | 26.3 |
| ask latency max (s) | 4.8 | 4.4 | 34.3 |
| ask questions over 5s | 0 | 0 | 47 |
| ask output tokens per second | 61 | 79 | 7 |
| ask latency mean (s) | 1.6 | 1.2 | 9.7 |
| ask questions answered without a model call | 23 | 23 | 23 |
| ask tokens in/out (mean) | 1015/99 | 740/94 | 730/71 |
| ask cost per question ($) | 0.00151 | 0.00000 | 0.00000 |
| ask refusals | 5 | 3 | 2 |
| judge verdicts that failed (counted wrong) | 0 | 0 | 0 |
| schema failures (ask+judge) | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 |
| whole benchmark wall time (s) | 595 | 607 | 2769 |
| judge cost for this run ($) | 0.1171 | 0.1215 | 0.1207 |
