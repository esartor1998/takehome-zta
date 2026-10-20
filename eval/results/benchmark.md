# Model benchmark

judge: `anthropic:claude-haiku-4-5-20251001` for every column. questions: 70.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b | ollama:qwen3.6:35b-a3b |
| --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | 6.4 GB, 66% on gpu | 4.0 GB, 95% on gpu |
| first call incl. load (s) | 0.7 | 13.1 | 48.9 | 341.3 |
| **ingest** wall (s) | 256.0 | 317.3 | 1908.4 | 2549.7 |
| ingest model calls | 175 | 174 | 175 | 175 |
| ingest tokens in/out | 171788/24486 | 51566/31498 | 51590/14630 | 51584/23946 |
| ingest cost ($) | 0.2942 | 0.0000 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 51/51 | 50/51 | 51/51 | 51/51 |
| **brief** wall (s) | 1.8 | 0.9 | 14.4 | 60.0 |
| brief cost ($) | 0.00103 | 0.00000 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes |
| brief meeting in focus | yes | yes | yes | NO |
| **ask** accuracy (judge) | 83% | 71% | 80% | 79% |
| ask accuracy, original questions (q*) | 15/18 | 15/18 | 15/18 | 13/18 |
| ask accuracy, vague questions (v*) | 18/23 | 15/23 | 18/23 | 18/23 |
| ask citation recall | 88% | 84% | 87% | 91% |
| ask citation recall, vague (v*) | 91% | 83% | 91% | 93% |
| ask citation precision | 56% | 48% | 53% | 53% |
| ask answers with a citation flag | 6 | 7 | 2 | 2 |
| ask flag precision (flagged and judged wrong) | 0% | 57% | 0% | 0% |
| ask flag recall (wrong answers that were flagged) | 0% | 20% | 0% | 0% |
| ask forbidden cites | 0 | 1 | 1 | 0 |
| ask uncited sentences | 21 | 32 | 13 | 25 |
| ask latency p50 (s) | 1.5 | 0.8 | 9.7 | 20.0 |
| ask latency p95 (s) | 3.6 | 3.3 | 29.0 | 66.7 |
| ask latency max (s) | 4.2 | 4.0 | 33.3 | 90.1 |
| ask questions over 5s | 0 | 0 | 47 | 47 |
| ask output tokens per second | 65 | 79 | 7 | 3 |
| ask latency mean (s) | 1.4 | 1.2 | 10.4 | 22.6 |
| ask questions answered without a model call | 23 | 23 | 23 | 23 |
| ask tokens in/out (mean) | 956/92 | 707/92 | 752/74 | 753/72 |
| ask cost per question ($) | 0.00142 | 0.00000 | 0.00000 | 0.00000 |
| ask refusals | 6 | 3 | 4 | 5 |
| judge verdicts that failed (counted wrong) | 0 | 0 | 0 | 0 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 471 | 523 | 2767 | 4324 |
| judge cost for this run ($) | 0.1546 | 0.1556 | 0.1533 | 0.1484 |
