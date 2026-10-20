# Model benchmark

judge: `anthropic:claude-haiku-4-5-20251001` for every column. questions: 41.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b | ollama:qwen3.6:35b-a3b |
| --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | 6.4 GB, 66% on gpu | 4.0 GB, 95% on gpu |
| first call incl. load (s) | 0.6 | 11.9 | 19.4 | 204.9 |
| **ingest** wall (s) | 158.8 | 54.6 | 553.5 | 838.4 |
| ingest model calls | 137 | 137 | 137 | 137 |
| ingest tokens in/out | 122409/12883 | 26354/5525 | 26551/4074 | 26551/5685 |
| ingest cost ($) | 0.1868 | 0.0000 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 28/29 | 29/29 | 28/29 | 28/29 |
| **brief** wall (s) | 2.0 | 0.7 | 25.2 | 12.1 |
| brief cost ($) | 0.00102 | 0.00000 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes |
| brief meeting in focus | yes | NO | NO | yes |
| **ask** accuracy (judge) | 78% | 63% | 71% | 61% |
| ask accuracy, original questions (q*) | 15/18 | 12/18 | 12/18 | 12/18 |
| ask accuracy, vague questions (v*) | 17/23 | 14/23 | 17/23 | 13/23 |
| ask citation recall | 90% | 90% | 91% | 90% |
| ask citation recall, vague (v*) | 87% | 89% | 91% | 89% |
| ask citation precision | 64% | 64% | 67% | 61% |
| ask forbidden cites | 0 | 1 | 1 | 1 |
| ask uncited sentences | 11 | 17 | 4 | 12 |
| ask latency p50 (s) | 1.5 | 0.8 | 8.7 | 13.5 |
| ask latency p95 (s) | 2.3 | 1.9 | 24.9 | 43.8 |
| ask latency max (s) | 2.4 | 2.7 | 34.6 | 49.8 |
| ask questions over 5s | 0 | 0 | 26 | 27 |
| ask output tokens per second | 63 | 81 | 7 | 4 |
| ask latency mean (s) | 1.2 | 0.8 | 8.8 | 13.8 |
| ask questions answered without a model call | 12 | 12 | 12 | 12 |
| ask tokens in/out (mean) | 588/73 | 560/68 | 599/63 | 600/59 |
| ask cost per question ($) | 0.00095 | 0.00000 | 0.00000 | 0.00000 |
| ask refusals | 4 | 3 | 3 | 4 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 272 | 152 | 1003 | 1485 |
| judge cost for this run ($) | 0.0800 | 0.0789 | 0.0793 | 0.0791 |
