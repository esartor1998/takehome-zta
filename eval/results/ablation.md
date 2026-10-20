# Eval questions that use retrieval

33 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 96% | 91% | 30% | 0.66 | 8.4 |
| no_vector | 93% | 88% | 30% | 0.60 | 8.3 |
| vector_only | 70% | 64% | 13% | 0.47 | 10.6 |
| no_fts | 90% | 85% | 29% | 0.67 | 8.5 |
| fts_only | 77% | 67% | 15% | 0.41 | 9.9 |
| no_structured | 80% | 73% | 15% | 0.55 | 10.9 |
| vector_x0.5 | 96% | 91% | 30% | 0.66 | 8.4 |
| vector_x2 | 95% | 91% | 31% | 0.69 | 8.3 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **1**, hurts on **0**, no change on 32
- precision: higher with the vector pull on 2, lower on 3
- expected items it brought in: **1**, expected items it pushed out: **0**
- items per context: 8.4 with, 8.3 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `q12` Summarize investor-related activity this wee | 100% | 100% | 30% | 27% | 0 | 0 |
| `v05` what's dk up to | 100% | 100% | 25% | 33% | 0 | 0 |
| `v14` did we hire taylor | 100% | 100% | 33% | 36% | 0 | 0 |
| `t03` anyting from investers | 100% | 100% | 40% | 44% | 0 | 0 |
| `n05` when will the soc2 report be ready | 100% | 0% | 10% | 0% | 1 | 0 |

### On its own

The vector pull alone reaches 70% recall (every group on 64% of questions), against 77% for full text search alone and 93% for everything except vectors.

## Semantic probes: questions worded unlike the source text

15 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 83% | 80% | 14% | 0.54 | 11.3 |
| no_vector | 60% | 60% | 11% | 0.30 | 8.1 |
| vector_only | 83% | 80% | 13% | 0.40 | 10.9 |
| no_fts | 83% | 80% | 13% | 0.42 | 10.8 |
| fts_only | 53% | 53% | 11% | 0.27 | 8.3 |
| no_structured | 83% | 80% | 14% | 0.51 | 11.5 |
| vector_x0.5 | 83% | 80% | 14% | 0.49 | 11.2 |
| vector_x2 | 77% | 73% | 14% | 0.56 | 10.7 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **4**, hurts on **0**, no change on 11
- precision: higher with the vector pull on 9, lower on 4
- expected items it brought in: **11**, expected items it pushed out: **0**
- items per context: 11.3 with, 8.1 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `p01` who is unavailable this week | 100% | 0% | 10% | 0% | 1 | 0 |
| `p02` how much money are we trying to raise | 100% | 100% | 15% | 33% | 1 | 0 |
| `p03` did the person we made an offer to take the  | 100% | 100% | 9% | 14% | 0 | 0 |
| `p04` when does the new payments vendor go live | 100% | 100% | 30% | 18% | 1 | 0 |
| `p06` what are we charging per user | 100% | 100% | 30% | 25% | 0 | 0 |
| `p07` who needs to look at my code changes | 50% | 0% | 10% | 0% | 1 | 0 |
| `p08` which venture firm is leading our round | 100% | 100% | 25% | 40% | 1 | 0 |
| `p09` which company disputed the seat count on its | 100% | 0% | 17% | 0% | 2 | 0 |
| `p10` has anyone complained that data exports are  | 100% | 100% | 30% | 10% | 2 | 0 |
| `p11` when is the board getting together | 100% | 0% | 7% | 0% | 1 | 0 |
| `p13` why was the product launch date pushed | 100% | 100% | 10% | 9% | 0 | 0 |
| `p15` which investor has not heard back from us | 100% | 100% | 10% | 11% | 0 | 0 |
| `p16` how long is the contract we are renewing wit | 100% | 100% | 13% | 9% | 1 | 0 |

### On its own

The vector pull alone reaches 83% recall (every group on 80% of questions), against 53% for full text search alone and 60% for everything except vectors.


## What each pull costs

Mean milliseconds per question: fts 0, vector 42, person 0, structured 0.

## End to end with `anthropic:claude-haiku-4-5-20251001`, judged by `anthropic:claude-haiku-4-5-20251001`

| | accuracy | citation recall | citation precision | median seconds |
| --- | --- | --- | --- | --- |
| full | 91% | 87% | 57% | 1.9 |
| no_vector | 94% | 88% | 57% | 1.8 |

Judged correct only with the vector pull: q01, n05. Judged correct only without it: t03, t05, n06.
