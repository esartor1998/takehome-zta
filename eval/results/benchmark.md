# Model benchmark

judge: `anthropic:claude-haiku-4-5-20251001` for every column. questions: 18.

| metric | anthropic:claude-haiku-4-5-20251001 |
| --- | --- |
| where it runs | hosted |
| first call incl. load (s) | 8.1 |
| **ingest** wall (s) | 16.5 |
| ingest model calls | 16 |
| ingest tokens in/out | 13380/1242 |
| ingest cost ($) | 0.0196 |
| ingest decision checks passed | 4/4 |
| **brief** wall (s) | 1.7 |
| brief cost ($) | 0.00088 |
| brief invalid ids | 0 |
| brief stale record called out | yes |
| brief meeting in focus | yes |
| **ask** accuracy (judge) | 89% |
| ask citation recall | 100% |
| ask citation precision | 84% |
| ask forbidden cites | 0 |
| ask uncited sentences | 4 |
| ask latency p50 (s) | 1.4 |
| ask latency p95 (s) | 2.0 |
| ask latency max (s) | 2.2 |
| ask questions over 5s | 0 |
| ask tokens in/out (mean) | 796/81 |
| ask cost per question ($) | 0.00120 |
| ask refusals | 2 |
| schema failures (ask+judge) | 0 |
| judge cost for this run ($) | 0.0319 |
