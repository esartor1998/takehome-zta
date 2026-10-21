# Model benchmark

judge: `openai:gpt-6-luna` for every column. questions: 70.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | openrouter:deepseek/deepseek-v4.1-flash-1017 | openrouter:minimax/minimax-m3.1-flash:free | openrouter:xiaomi/mimo-v2.6-pro |
| --- | --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | hosted | hosted | hosted |
| first call incl. load (s) | 0.6 | 0.1 | 0.7 | 1.6 | 0.6 |
| **ingest** wall (s) | 257.3 | 307.9 | 188.8 | 1263.0 | 733.7 |
| ingest model calls | 177 | 176 | 177 | 177 | 177 |
| ingest tokens in/out | 173651/24834 | 52015/30592 | 53701/12573 | 82393/99929 | 50682/10850 |
| ingest cost ($) | 0.2978 | 0.0000 | 0.0156 | 0.0000 | 0.0315 |
| ingest checks passed (decisions, stale, follow-ups) | 51/51 | 50/51 | 51/51 | 51/51 | 51/51 |
| **brief** wall (s) | 1.8 | 0.8 | 1.0 | 1.7 | 3.4 |
| brief cost ($) | 0.00103 | 0.00000 | 0.00013 | 0.00000 | 0.00029 |
| brief invalid ids | 0 | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes | yes |
| brief meeting in focus | yes | yes | yes | yes | yes |
| **ask** accuracy (judge) | 83% | 63% | 70% | 66% | 77% |
| ask accuracy, original questions (q*) | 15/18 | 14/18 | 12/18 | 10/18 | 15/18 |
| ask accuracy, vague questions (v*) | 16/23 | 12/23 | 17/23 | 14/23 | 17/23 |
| ask citation recall | 91% | 85% | 94% | 80% | 95% |
| ask citation recall, vague (v*) | 91% | 83% | 96% | 77% | 95% |
| ask citation precision | 53% | 44% | 53% | 53% | 49% |
| ask answers with a citation flag | 10 | 9 | 2 | 3 | 2 |
| ask flag precision (flagged and judged wrong) | 20% | 56% | 0% | 33% | 0% |
| ask flag recall (wrong answers that were flagged) | 17% | 19% | 0% | 4% | 0% |
| ask forbidden cites | 0 | 2 | 1 | 0 | 1 |
| ask uncited sentences | 30 | 22 | 14 | 10 | 12 |
| ask latency p50 (s) | 1.9 | 1.6 | 1.2 | 6.0 | 3.2 |
| ask latency p95 (s) | 4.0 | 4.0 | 3.8 | 18.7 | 13.4 |
| ask latency max (s) | 4.7 | 4.9 | 7.1 | 28.2 | 18.3 |
| ask questions over 5s | 0 | 0 | 3 | 37 | 15 |
| ask output tokens per second | 67 | 81 | 79 | 97 | 34 |
| ask latency mean (s) | 1.8 | 1.7 | 1.3 | 7.8 | 3.7 |
| ask questions answered without a model call | 23 | 23 | 23 | 23 | 23 |
| ask tokens in/out (mean) | 1535/123 | 1268/134 | 1214/106 | 1322/759 | 1244/125 |
| ask cost per question ($) | 0.00149 | 0.00000 | 0.00015 | 0.00000 | 0.00040 |
| ask refusals | 0 | 0 | 3 | 1 | 4 |
| judge verdicts that failed (counted wrong) | 0 | 0 | 0 | 0 | 0 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 595 | 628 | 492 | 2011 | 1203 |
| judge cost for this run ($) | 0.1427 | 0.1492 | 0.1525 | 0.1341 | 0.1484 |
