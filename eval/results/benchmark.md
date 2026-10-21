# Model benchmark

judge: `openai:gpt-6-luna` for every column. questions: 70.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | openrouter:deepseek/deepseek-v4.1-flash-1017 | openrouter:minimax/minimax-m3.1-flash:free | openrouter:xiaomi/mimo-v2.6-pro |
| --- | --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | hosted | hosted | hosted |
| first call incl. load (s) | 0.6 | 0.1 | 0.7 | 6.3 | 0.8 |
| **ingest** wall (s) | 257.3 | 307.9 | 220.8 | 1294.4 | 563.4 |
| ingest model calls | 177 | 176 | 175 | 175 | 175 |
| ingest tokens in/out | 173651/24834 | 52015/30592 | 52919/12870 | 81604/103564 | 50254/10823 |
| ingest cost ($) | 0.2978 | 0.0000 | 0.0157 | 0.0000 | 0.0313 |
| ingest checks passed (decisions, stale, follow-ups) | 51/51 | 50/51 | 51/51 | 51/51 | 51/51 |
| **brief** wall (s) | 1.8 | 0.8 | 1.0 | 12.8 | 12.4 |
| brief cost ($) | 0.00103 | 0.00000 | 0.00014 | 0.00000 | 0.00030 |
| brief invalid ids | 0 | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes | yes |
| brief meeting in focus | yes | yes | yes | yes | yes |
| **ask** accuracy (judge) | 83% | 63% | 79% | 69% | 79% |
| ask accuracy, original questions (q*) | 15/18 | 14/18 | 17/18 | 13/18 | 13/18 |
| ask accuracy, vague questions (v*) | 16/23 | 12/23 | 18/23 | 14/23 | 19/23 |
| ask citation recall | 91% | 85% | 92% | 77% | 89% |
| ask citation recall, vague (v*) | 91% | 83% | 92% | 70% | 93% |
| ask citation precision | 53% | 44% | 53% | 50% | 48% |
| ask answers with a citation flag | 10 | 9 | 3 | 1 | 1 |
| ask flag precision (flagged and judged wrong) | 20% | 56% | 0% | 0% | 100% |
| ask flag recall (wrong answers that were flagged) | 17% | 19% | 0% | 0% | 7% |
| ask forbidden cites | 0 | 2 | 0 | 1 | 0 |
| ask uncited sentences | 30 | 22 | 16 | 6 | 5 |
| ask latency p50 (s) | 1.9 | 1.6 | 1.2 | 6.3 | 2.7 |
| ask latency p95 (s) | 4.0 | 4.0 | 2.4 | 26.8 | 9.3 |
| ask latency max (s) | 4.7 | 4.9 | 9.8 | 32.1 | 21.7 |
| ask questions over 5s | 0 | 0 | 1 | 36 | 8 |
| ask output tokens per second | 67 | 81 | 66 | 84 | 31 |
| ask latency mean (s) | 1.8 | 1.7 | 1.2 | 9.0 | 3.0 |
| ask questions answered without a model call | 23 | 23 | 23 | 23 | 23 |
| ask tokens in/out (mean) | 1535/123 | 1268/134 | 689/79 | 809/756 | 711/91 |
| ask cost per question ($) | 0.00149 | 0.00000 | 0.00015 | 0.00000 | 0.00039 |
| ask refusals | 0 | 0 | 4 | 1 | 7 |
| judge verdicts that failed (counted wrong) | 0 | 0 | 0 | 0 | 0 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 595 | 628 | 487 | 2150 | 962 |
| judge cost for this run ($) | 0.1427 | 0.1492 | 0.1520 | 0.1350 | 0.1409 |
