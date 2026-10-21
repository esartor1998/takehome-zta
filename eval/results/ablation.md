# Eval questions that use retrieval

42 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 92% | 83% | 27% | 0.65 | 8.7 |
| no_vector | 87% | 79% | 26% | 0.59 | 8.6 |
| vector_only | 74% | 69% | 12% | 0.45 | 10.8 |
| no_fts | 88% | 79% | 26% | 0.63 | 8.6 |
| fts_only | 68% | 64% | 12% | 0.34 | 10.4 |
| no_structured | 85% | 81% | 15% | 0.54 | 11.2 |
| vector_x0.5 | 90% | 83% | 26% | 0.62 | 8.6 |
| vector_x2 | 94% | 86% | 28% | 0.77 | 8.5 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **3**, hurts on **1**, no change on 38
- precision: higher with the vector pull on 9, lower on 6
- expected items it brought in: **7**, expected items it pushed out: **1**
- items per context: 8.7 with, 8.6 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `q01` What did Daniel Kim say about the billing mi | 100% | 100% | 20% | 18% | 0 | 0 |
| `q03` What time is the Weekly Product Sync today? | 100% | 100% | 25% | 12% | 1 | 0 |
| `q06` Was the Weekly Product Sync on Friday March  | 100% | 100% | 38% | 25% | 1 | 0 |
| `q08` What was the original v2 API auth decision o | 100% | 100% | 14% | 0% | 1 | 0 |
| `q09` What did Rebecca Liu say about the Globex ad | 100% | 100% | 8% | 8% | 0 | 0 |
| `q11` Who is out of office this week and who has c | 100% | 0% | 10% | 0% | 1 | 0 |
| `q12` Summarize investor-related activity this wee | 67% | 67% | 22% | 29% | 0 | 0 |
| `v05` what's dk up to | 100% | 100% | 12% | 17% | 0 | 0 |
| `v06` anything from investors? | 100% | 100% | 30% | 33% | 0 | 0 |
| `v12` how's billing going | 100% | 33% | 30% | 9% | 2 | 0 |
| `v14` did we hire taylor | 100% | 100% | 33% | 36% | 0 | 0 |
| `v16` what's the deal with sso | 33% | 67% | 8% | 15% | 0 | 1 |
| `n06` what changes did priya ask for on the invest | 100% | 100% | 9% | 8% | 0 | 0 |
| `w05` are we renewing cloudhost | 100% | 100% | 20% | 18% | 0 | 0 |
| `w06` is the onboarding checklist redesign still o | 50% | 0% | 7% | 0% | 1 | 0 |

### On its own

The vector pull alone reaches 74% recall (every group on 69% of questions), against 68% for full text search alone and 87% for everything except vectors.

## Semantic probes: questions worded unlike the source text

15 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 77% | 73% | 13% | 0.45 | 10.8 |
| no_vector | 60% | 60% | 8% | 0.20 | 9.4 |
| vector_only | 63% | 60% | 10% | 0.42 | 10.9 |
| no_fts | 63% | 60% | 11% | 0.35 | 10.5 |
| fts_only | 53% | 53% | 8% | 0.26 | 9.6 |
| no_structured | 77% | 73% | 13% | 0.52 | 11.2 |
| vector_x0.5 | 77% | 73% | 12% | 0.40 | 10.8 |
| vector_x2 | 77% | 73% | 14% | 0.49 | 10.3 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **3**, hurts on **0**, no change on 12
- precision: higher with the vector pull on 6, lower on 2
- expected items it brought in: **7**, expected items it pushed out: **0**
- items per context: 10.8 with, 9.4 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `p01` who is unavailable this week | 100% | 0% | 10% | 0% | 1 | 0 |
| `p02` how much money are we trying to raise | 100% | 100% | 10% | 11% | 0 | 0 |
| `p06` what are we charging per user | 100% | 100% | 30% | 18% | 1 | 0 |
| `p07` who needs to look at my code changes | 50% | 0% | 10% | 0% | 1 | 0 |
| `p08` which venture firm is leading our round | 100% | 100% | 30% | 20% | 1 | 0 |
| `p10` has anyone complained that data exports are  | 100% | 100% | 27% | 10% | 2 | 0 |
| `p11` when is the board getting together | 100% | 0% | 8% | 0% | 1 | 0 |
| `p15` which investor has not heard back from us | 100% | 100% | 10% | 11% | 0 | 0 |

### On its own

The vector pull alone reaches 63% recall (every group on 60% of questions), against 53% for full text search alone and 60% for everything except vectors.


## What each pull costs

Mean milliseconds per question: fts 0, vector 18, person 0, structured 0.
