# Eval questions that use retrieval

23 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 91% | 78% | 43% | 0.77 | 6.7 |
| no_vector | 86% | 74% | 43% | 0.75 | 6.7 |
| vector_only | 68% | 61% | 13% | 0.47 | 10.0 |
| no_fts | 89% | 78% | 43% | 0.79 | 6.7 |
| fts_only | 78% | 65% | 20% | 0.59 | 9.0 |
| no_structured | 80% | 70% | 16% | 0.67 | 10.0 |
| vector_x0.5 | 91% | 78% | 44% | 0.77 | 6.7 |
| vector_x2 | 89% | 78% | 44% | 0.82 | 6.7 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **1**, hurts on **0**, no change on 22
- precision: higher with the vector pull on 1, lower on 2
- expected items it brought in: **1**, expected items it pushed out: **1**
- items per context: 6.7 with, 6.7 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `q11` Who is out of office this week and who has c | 100% | 0% | 10% | 0% | 1 | 0 |
| `v14` did we hire taylor | 100% | 100% | 20% | 30% | 0 | 1 |
| `v15` when do we close the round | 100% | 100% | 10% | 12% | 0 | 0 |

### On its own

The vector pull alone reaches 68% recall (every group on 61% of questions), against 78% for full text search alone and 86% for everything except vectors.

## Semantic probes: questions worded unlike the source text

12 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `anthropic-claude-haiku-4-5-20251001`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 88% | 83% | 15% | 0.45 | 9.6 |
| no_vector | 67% | 67% | 15% | 0.26 | 6.7 |
| vector_only | 83% | 83% | 14% | 0.50 | 10.0 |
| no_fts | 83% | 83% | 15% | 0.52 | 9.6 |
| fts_only | 67% | 67% | 15% | 0.23 | 7.1 |
| no_structured | 88% | 83% | 14% | 0.42 | 10.0 |
| vector_x0.5 | 92% | 92% | 15% | 0.44 | 9.6 |
| vector_x2 | 79% | 75% | 15% | 0.49 | 9.6 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **4**, hurts on **1**, no change on 7
- precision: higher with the vector pull on 6, lower on 4
- expected items it brought in: **8**, expected items it pushed out: **1**
- items per context: 9.6 with, 6.7 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `p01` who is unavailable this week | 100% | 0% | 10% | 0% | 1 | 0 |
| `p02` how much money are we trying to raise | 100% | 100% | 20% | 50% | 1 | 0 |
| `p03` did the person we made an offer to take the  | 100% | 100% | 10% | 14% | 0 | 0 |
| `p04` when does the new payments vendor go live | 100% | 0% | 10% | 0% | 1 | 0 |
| `p06` what are we charging per user | 100% | 100% | 30% | 20% | 1 | 0 |
| `p07` who needs to look at my code changes | 50% | 0% | 10% | 0% | 1 | 0 |
| `p08` which venture firm is leading our round | 100% | 100% | 30% | 50% | 1 | 0 |
| `p09` which company disputed the seat count on its | 100% | 100% | 20% | 10% | 1 | 0 |
| `p11` when is the board getting together | 100% | 0% | 10% | 0% | 1 | 0 |
| `p13` why was the product launch date pushed | 0% | 100% | 0% | 10% | 0 | 1 |

### On its own

The vector pull alone reaches 83% recall (every group on 83% of questions), against 67% for full text search alone and 67% for everything except vectors.


## What each pull costs

Mean milliseconds per question: fts 0, vector 21, person 0, structured 0.

## End to end with `anthropic:claude-haiku-4-5-20251001`, judged by `anthropic:claude-haiku-4-5-20251001`

| | accuracy | citation recall | citation precision | median seconds |
| --- | --- | --- | --- | --- |
| full | 91% | 83% | 63% | 1.7 |
| no_vector | 87% | 82% | 63% | 1.7 |

Judged correct only with the vector pull: q11, v16. Judged correct only without it: q12.
