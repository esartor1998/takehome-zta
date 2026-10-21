# Eval questions that use retrieval

42 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `ollama-llama3-2-latest`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 93% | 90% | 26% | 0.65 | 8.7 |
| no_vector | 90% | 86% | 27% | 0.60 | 8.5 |
| vector_only | 74% | 69% | 13% | 0.47 | 10.8 |
| no_fts | 91% | 86% | 26% | 0.68 | 8.7 |
| fts_only | 72% | 69% | 14% | 0.44 | 9.8 |
| no_structured | 85% | 83% | 16% | 0.57 | 10.9 |
| vector_x0.5 | 93% | 90% | 26% | 0.65 | 8.8 |
| vector_x2 | 92% | 88% | 27% | 0.72 | 8.7 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **2**, hurts on **1**, no change on 39
- precision: higher with the vector pull on 4, lower on 7
- expected items it brought in: **3**, expected items it pushed out: **1**
- items per context: 8.7 with, 8.5 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `q08` What was the original v2 API auth decision o | 100% | 100% | 11% | 10% | 0 | 0 |
| `q11` Who is out of office this week and who has c | 100% | 0% | 10% | 0% | 1 | 0 |
| `q12` Summarize investor-related activity this wee | 100% | 100% | 25% | 27% | 0 | 0 |
| `v05` what's dk up to | 100% | 100% | 12% | 17% | 0 | 0 |
| `v12` how's billing going | 100% | 33% | 30% | 10% | 2 | 0 |
| `v13` pricing? | 100% | 100% | 30% | 43% | 0 | 0 |
| `v14` did we hire taylor | 100% | 100% | 33% | 36% | 0 | 0 |
| `v16` what's the deal with sso | 0% | 33% | 0% | 8% | 0 | 1 |
| `t07` prcing? | 100% | 100% | 27% | 43% | 0 | 0 |
| `n06` what changes did priya ask for on the invest | 100% | 100% | 10% | 9% | 0 | 0 |
| `w04` partner api v2 timeline | 100% | 100% | 18% | 20% | 0 | 0 |

### On its own

The vector pull alone reaches 74% recall (every group on 69% of questions), against 72% for full text search alone and 90% for everything except vectors.

## Semantic probes: questions worded unlike the source text

15 answerable questions that go through retrieval (model: none, embeddings: `nomic-embed-text`, store: `ollama-llama3-2-latest`).

| configuration | recall | every group present | precision | mrr | items in context |
| --- | --- | --- | --- | --- | --- |
| full | 77% | 73% | 13% | 0.40 | 10.8 |
| no_vector | 60% | 60% | 10% | 0.30 | 9.7 |
| vector_only | 77% | 73% | 12% | 0.40 | 10.7 |
| no_fts | 63% | 60% | 11% | 0.36 | 10.1 |
| fts_only | 53% | 53% | 11% | 0.32 | 8.5 |
| no_structured | 83% | 80% | 14% | 0.47 | 11.8 |
| vector_x0.5 | 77% | 73% | 13% | 0.39 | 10.8 |
| vector_x2 | 63% | 60% | 12% | 0.45 | 10.1 |

### Vector pull, question by question (full against no_vector)

- recall: helps on **3**, hurts on **0**, no change on 12
- precision: higher with the vector pull on 5, lower on 2
- expected items it brought in: **6**, expected items it pushed out: **0**
- items per context: 10.8 with, 9.7 without

| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |
| --- | --- | --- | --- | --- | --- | --- |
| `p03` did the person we made an offer to take the  | 100% | 100% | 17% | 20% | 0 | 0 |
| `p07` who needs to look at my code changes | 50% | 0% | 9% | 0% | 1 | 0 |
| `p09` which company disputed the seat count on its | 100% | 0% | 17% | 0% | 2 | 0 |
| `p10` has anyone complained that data exports are  | 100% | 100% | 27% | 9% | 2 | 0 |
| `p11` when is the board getting together | 100% | 0% | 8% | 0% | 1 | 0 |
| `p13` why was the product launch date pushed | 100% | 100% | 18% | 17% | 0 | 0 |
| `p16` how long is the contract we are renewing wit | 100% | 100% | 8% | 9% | 0 | 0 |

### On its own

The vector pull alone reaches 77% recall (every group on 73% of questions), against 53% for full text search alone and 60% for everything except vectors.


## What each pull costs

Mean milliseconds per question: fts 0, vector 24, person 0, structured 0.
