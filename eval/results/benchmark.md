# Model benchmark

judge: `anthropic:claude-haiku-4-5-20251001` for every column. questions: 41.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b |
| --- | --- | --- | --- |
| where it runs | hosted | 3.0 GB, 100% on gpu | 6.4 GB, 66% on gpu |
| first call incl. load (s) | 0.7 | 13.2 | 49.4 |
| **ingest** wall (s) | 178.7 | 56.0 | 578.3 |
| ingest model calls | 138 | 138 | 138 |
| ingest tokens in/out | 123496/12952 | 26744/5562 | 26981/4115 |
| ingest cost ($) | 0.1883 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 27/28 | 28/28 | 27/28 |
| **brief** wall (s) | 2.0 | 1.2 | 14.7 |
| brief cost ($) | 0.00103 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes |
| brief meeting in focus | yes | yes | yes |
| **ask** accuracy (judge) | 66% | 49% | 61% |
| ask accuracy, original questions (q*) | 12/18 | 11/18 | 11/18 |
| ask accuracy, vague questions (v*) | 15/23 | 9/23 | 14/23 |
| ask citation recall | 84% | 80% | 83% |
| ask citation recall, vague (v*) | 85% | 80% | 84% |
| ask citation precision | 57% | 54% | 56% |
| ask forbidden cites | 0 | 0 | 0 |
| ask uncited sentences | 9 | 23 | 6 |
| ask latency p50 (s) | 1.6 | 1.1 | 9.6 |
| ask latency p95 (s) | 2.5 | 2.0 | 26.7 |
| ask latency max (s) | 2.6 | 3.2 | 43.2 |
| ask questions over 5s | 0 | 0 | 29 |
| ask output tokens per second | 59 | 80 | 7 |
| ask latency mean (s) | 1.3 | 1.0 | 11.0 |
| ask questions answered without a model call | 11 | 11 | 11 |
| ask tokens in/out (mean) | 674/79 | 635/79 | 687/74 |
| ask cost per question ($) | 0.00107 | 0.00000 | 0.00000 |
| ask refusals | 5 | 2 | 5 |
| schema failures (ask+judge) | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 |
| whole benchmark wall time (s) | 314 | 162 | 1109 |
| judge cost for this run ($) | 0.0793 | 0.0792 | 0.0792 |
