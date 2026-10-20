# Model benchmark

judge: `anthropic:claude-haiku-4-5-20251001` for every column. questions: 61.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b | ollama:qwen3.6:35b-a3b |
| --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | 6.4 GB, 66% on gpu | 4.0 GB, 95% on gpu |
| first call incl. load (s) | 0.6 | 4.0 | 14.7 | 187.3 |
| **ingest** wall (s) | 119.1 | 40.8 | 416.1 | 606.4 |
| ingest model calls | 107 | 107 | 107 | 107 |
| ingest tokens in/out | 94375/9590 | 19833/4118 | 20009/3134 | 20009/4210 |
| ingest cost ($) | 0.1423 | 0.0000 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 35/35 | 35/35 | 34/35 | 34/35 |
| **brief** wall (s) | 2.1 | 0.7 | 12.6 | 11.3 |
| brief cost ($) | 0.00108 | 0.00000 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes |
| brief meeting in focus | yes | NO | yes | yes |
| **ask** accuracy (judge) | 85% | 70% | 74% | 80% |
| ask accuracy, original questions (q*) | 15/18 | 12/18 | 12/18 | 13/18 |
| ask accuracy, vague questions (v*) | 21/23 | 19/23 | 18/23 | 18/23 |
| ask citation recall | 92% | 89% | 92% | 92% |
| ask citation recall, vague (v*) | 95% | 88% | 93% | 93% |
| ask citation precision | 60% | 58% | 60% | 58% |
| ask answers with a citation flag | 2 | 4 | 0 | 5 |
| ask flag precision (flagged and judged wrong) | 50% | 25% | - | 0% |
| ask flag recall (wrong answers that were flagged) | 11% | 6% | 0% | 0% |
| ask forbidden cites | 0 | 2 | 1 | 1 |
| ask uncited sentences | 17 | 34 | 4 | 25 |
| ask latency p50 (s) | 1.6 | 0.7 | 8.7 | 12.5 |
| ask latency p95 (s) | 3.7 | 3.5 | 24.9 | 38.6 |
| ask latency max (s) | 4.1 | 4.9 | 32.1 | 67.8 |
| ask questions over 5s | 0 | 0 | 38 | 38 |
| ask output tokens per second | 63 | 82 | 7 | 5 |
| ask latency mean (s) | 1.4 | 1.1 | 8.9 | 14.5 |
| ask questions answered without a model call | 23 | 23 | 23 | 23 |
| ask tokens in/out (mean) | 862/88 | 663/88 | 643/63 | 669/69 |
| ask cost per question ($) | 0.00130 | 0.00000 | 0.00000 | 0.00000 |
| ask refusals | 4 | 2 | 3 | 3 |
| judge verdicts that failed (counted wrong) | 0 | 0 | 0 | 0 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 313 | 212 | 1072 | 1606 |
| judge cost for this run ($) | 0.1261 | 0.1258 | 0.1258 | 0.1223 |
