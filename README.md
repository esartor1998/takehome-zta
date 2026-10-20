# Founder assistant

A small context engine for a startup founder. It ingests Gmail, Google Calendar, Slack, Linear, GitHub, Notion and a CRM into one store, works out who is who, collapses duplicates, tracks which decisions are current and which records have gone stale, finds what you owe people and what people owe you, and answers questions with citations back to stored item ids. It also writes a morning brief without being asked.

The model is a setting, not a dependency. Any chat model can be swapped in with one environment variable, and `founder bench` runs the same work on several of them and compares time, cost, accuracy and failures side by side.

## What it supports

- 7 sources, about 950 items, with outsiders (customers, investors, a candidate) as well as the team
- identity across work and personal email, display names in any header style, nicknames, initials, slack, linear, github and notion ids, and shared inboxes
- cross-source duplicates, quoted replies in gmail, outlook and short styles, forwards, html-only and multipart mail, and machine mail that is indexed but kept out of answers
- decision tracking: reversals, corrections, and records in other tools that still state the old plan
- follow-ups in both directions: asks made of you, and promises you made
- cancelled, tentative, all-day and other-timezone events
- vague questions ('what's on today', 'what is daniel saying', 'anything urgent') routed before any model runs
- cited answers where every citation is checked in code
- an eval set of 41 questions, 23 of them vague, and a benchmark that compares models

## How to run

You need Python 3.11+ and [Ollama](https://ollama.com) for local models. A hosted model needs a key in `.env` (gitignored).

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/founder ingest          # builds .state/<model>/ (regenerates data/ first if it is missing)
.venv/bin/founder                 # no arguments prints the morning brief
.venv/bin/founder ask "what's on today"
.venv/bin/founder chat            # interactive
.venv/bin/founder eval            # runs eval/questions.json on the current model
.venv/bin/founder bench ollama:llama3.2:latest anthropic:claude-haiku-4-5-20251001
```

`data/` is gitignored because it is a symlink on my dev machine. `founder ingest` regenerates it from `synthetic_data_generator.py`, which is seeded and byte-for-byte reproducible.

## Swapping models

A model is named `provider:name`. Everything that touches a model goes through `chat()` and `embed()` in `founder/llm.py`, so a provider is one function and one line in a dict.

| provider | example | notes |
| --- | --- | --- |
| ollama | `ollama:llama3.2:latest` | local, schema output through `format`, qwen3 and later run with thinking off |
| anthropic | `anthropic:claude-haiku-4-5-20251001` | key in `.env` as `ANTHROPIC_KEY` or `ANTHROPIC_API_KEY`, schema output through a forced tool call |
| openai | `openai:gpt-4o-mini` | any server that speaks chat completions, with `FOUNDER_OPENAI_BASE` and `OPENAI_API_KEY`, checked here against ollama's `/v1` |

```bash
FOUNDER_MODEL=anthropic:claude-haiku-4-5-20251001 .venv/bin/founder ask "who's waiting on me"
```

Each model gets its own state directory under `.state/`, because decision labels, stale-record checks and follow-ups are extracted by the model at ingest time. Swapping models means one re-ingest, and the llm cache makes repeating a model free. Embeddings stay on local `nomic-embed-text` for every chat model: vectors from two embedders are not comparable, so the index should not move when the chat model does. Hosted calls retry on 429 and 5xx with backoff, and usage is tracked by role (extract, answer, brief, judge) so a benchmark can say where the tokens went.

## The dataset

Two layers, both seeded.

`synthetic_data_generator.py` is the first layer. It plants the required cases: an auth decision made, changed and reversed across three tools, a stale Linear record edited after the correction, a meeting rescheduled and a cancelled twin, duplicates, a personal address, a shared inbox, and a question with no answer.

`synthetic_data_expansion.py` is the second layer, and exists because real data is not like the first layer. It runs after every draw from the first, on its own generator, so ids from the first layer do not change. It adds:

- outsiders: Globex, Initech and Hooli contacts, two investors, a candidate and a recruiter, one of whom writes from a second address with a different display name
- two Daniels (a teammate and a customer), nicknames in chat (dan, danny, DK), and slack mentions as raw `<@U...>` ids
- six scenarios where a doc, a deal or an issue disagrees with what people said later: fundraising close date (Notion, CRM and Slack), pricing ($49 for everyone became $59 for new customers), a hiring offer put on hold and then lost, a billing cutover that moved, a customer SSO bug that came back after a fix, and the Q1 roadmap
- Alex's calendar today with a cancelled event, a tentative one, an all-day one, and meetings in Los Angeles, New York and London time
- asks nobody answered (email, a slack mention, two PR review requests) and promises Alex made that are overdue
- about 90 machine messages (newsletters, receipts, GitHub and Linear notifications, calendar invitations), forwards, one-word replies, html-only and multipart mail, and bot posts
- 61 GitHub PR rows, 17 Notion pages and 4 CRM rows, with directory exports (`github_users.json`, `notion_users.json`, `crm_contacts.json`) the way real tenants expose them

The answer key (`data/answer_key.json`) has a fragment for every scenario. The ingest never reads it or `normalized/`. The fixed clock is Sunday 2026-03-15 14:00 UTC, in `founder/config.py`.

## How it handles the messy cases

**Identity.** `founder/identity.py` builds people from the contacts export and the CRM, then attaches ids from each tool by email. For a sender it tries the directory, then a display name that matches one person (`Daniel F. <danf.photo@gmail.example>` is Daniel Foster because the last initial rules out Daniel Kim), then a unique handle (`dkim.work@gmail.com` and linear `dkim`), then a signature, where a full name beats a bare first name. Unquoted `LAST, First <x@y>` headers are split by hand, since the standard parser reads them as two addresses. An unknown mailbox on the company domain is a shared inbox, and a bulk or no-reply sender is a machine. We never merge on a first name alone. A first name in a question is the opposite case: it matches everyone who has it, and the answer says so.

**Decisions.** The model labels each candidate item (decision, reversal, correction, proposal) and names its subject. Code does the resolving. Candidates come from a regex plus similarity to generic 'change of plan' sentences. Groups are built around anchors, items that clearly change a plan, by thread and issue links, by embedding similarity of title and body, and by a shared specific person or company, with an average-similarity brake because single links chained every topic together. The last reversal or correction is the anchor, and everything after it is current. Rules override the model only when the wording starts a sentence ('Correction:', 'Reverting to'), because 'ship date needs another look after Sofia's correction' mentions a correction without making one.

**Stale records.** Latest timestamp is not enough: Linear ACME-231 was edited after Sofia's correction and still says March 20. Two detectors cover this. A correction that names the value it replaces ('not Mar 20') marks any later record still carrying it. And `founder/stale.py` goes record by record: it finds newer items that are close in meaning or share a specific person or company, keeps only those carrying a date, price or amount the record lacks (or a status change like 'accepted another offer'), and asks the model which newer item shows it. A 3B model asked 'is this record outdated' says yes to everything and flagged 60 routine issues. Asked to pick the item, with plain code deciding whether the two disagree, it is useful. Meeting notes are history and are never stale.

**Follow-ups.** `founder/followups.py` finds asks (an email to you, a slack mention, a PR review request) and promises (your latest message in a thread). The model extracts what was asked and the deadline in the sender's words. Whether it is open is code: a reply by you or a teammate in the thread, an issue it names that moved to Done afterwards, a PR that merged. Deadlines resolve against the message's own date, so 'by Monday' sent on a Friday is the next Monday. Closers like 'let me know if you want a deeper dive' and 'I will follow up if nothing changes by EOD' are not asks or promises, and a pattern list keeps them out.

**Duplicates.** Quoted tails are cut before indexing and kept separately. Linear snapshots collapse to the newest per identifier. The same update posted in two tools needs the same author, a 3h window, embedding similarity and real word overlap, since embeddings alone merged unrelated one-liners.

**Time.** The clock is `config.NOW`, and `datetime.now()` appears nowhere. Items dated after the clock are quarantined. All-day events use a date, other events keep their original zone and are shown in UTC with the local time beside them. Events that end before they start are flagged and given an hour.

**Not in the data.** The prompt requires an exact refusal sentence, and the eval checks refusal both ways (runway and the CFO are unanswerable, and the system must not invent them from the fundraising figures that are in the data).

## Vague questions

`founder/route.py` turns 'tomorrow?' or 'dk?' into a plan before any model runs: what kind of answer is wanted, who is meant, which day, and which words stand for a family of words. It is plain rules, so the same question gets the same plan whichever model answers.

- `schedule`: what is on, in time order, with cancelled, tentative, all-day, already-happened and other-timezone events marked, and prep for meetings with outsiders (their open asks of you, their open issues)
- `followups`, `blocked`, `customers`, `decisions`, `meeting emails`: lists of facts the database already holds, rendered by code from the same facts as the brief
- `focus` and `catchup`: the model phrases the top ranked facts, and if it ignores the format the facts themselves become the lines
- `person`: what someone has been saying, ranked by how unlike the template mail each item is. A bare first name covers every person with it, labelled, a role word ('investors') covers the people with that role, and a company ('hooli') covers the people we know there
- `topic`: hybrid retrieval (fts5, vectors, structured sql) with synonym expansion and exact pulls for named issues, PRs and meetings

Code-rendered answers use no tokens and cannot garble a list. Setting `FOUNDER_DIGEST=llm` sends them through the model instead, which is how a benchmark compares models on identical facts.

## Architecture

```
raw exports -> identity -> normalise -> embed -> dedupe -> topics
            -> decisions -> stale records -> follow-ups -> sqlite + chroma
question -> route (kind, people, day) -> digest by code | hybrid retrieval -> numbered context -> model -> citation check
```

- `normalize.py` per-source adapters into one item shape
- `identity.py`, `dedupe.py`, `extract.py`, `stale.py`, `followups.py` the context engine
- `store.py` sqlite is the source of truth, chroma only holds ids and vectors
- `route.py`, `retrieve.py`, `answer.py` question handling
- `brief.py` the morning brief and the facts both it and the open questions use
- `llm.py` providers, retries, usage tracking, `bench.py` and `evaluate.py` the measuring

**Citations.** The prompt numbers context items and keeps real ids out of the text, since models copy headers they can see. Code maps numbers back to ids, then checks each citation against the words it supports: it stays only if it covers the sentence about as well as the best retrieved item, and a missing citation is added from a current item with real overlap. History items (stale, superseded, cancelled) are never added to a bare sentence.

## Morning brief

`samples/morning_brief.md` is the latest brief, written by Haiku. Sections are queries: focus, today (with meeting prep), plans that changed and records that are out of date, waiting on you, you said you would, asked and already handled, blocked, repeating customer issues. A prepared customer meeting scores above a routine sync, an overdue promise scores above a status change, and a plan change with every record already updated is news, not a task.

## Benchmark

`founder bench` runs four tasks on each model against one fixed judge (Haiku, for every column, so scores compare): load, ingest (cold, with the llm cache cleared), the brief, and every eval question. Per model it reports where the model runs and how much of it is on the GPU, calls, tokens, cost and wall time for each task, latency (p50, p95, max, mean, questions over the 5s budget), output tokens per second, accuracy split into original and vague questions, citation recall and precision, uncited sentences, refusals, schema failures, retries, and ingest checks against the answer key (decisions, stale records, follow-ups).

Judge `claude-haiku-4-5-20251001` for every column, 41 questions, same code, one model at a time on an otherwise idle machine (RTX 2060 6GB, 23GB RAM, 4 cores). Timings are wall clock. The full per-question results are in `eval/results/models/*.json`.

| metric | anthropic:claude-haiku-4-5-20251001 | ollama:llama3.2:latest | ollama:qwen3.5:9b | ollama:qwen3.6:35b-a3b |
| --- | --- | --- | --- | --- |
| where it runs | hosted | 3.1 GB, 100% on gpu | 6.4 GB, 66% on gpu | 4.0 GB, 95% on gpu |
| first call incl. load (s) | 0.6 | 11.9 | 19.4 | 204.9 |
| **ingest** wall (s) | 158.8 | 54.6 | 553.5 | 838.4 |
| ingest model calls | 137 | 137 | 137 | 137 |
| ingest tokens in/out | 122409/12883 | 26354/5525 | 26551/4074 | 26551/5685 |
| ingest cost ($) | 0.1868 | 0.0000 | 0.0000 | 0.0000 |
| ingest checks passed (decisions, stale, follow-ups) | 28/29 | 29/29 | 28/29 | 28/29 |
| **brief** wall (s) | 2.0 | 0.7 | 25.2 | 12.1 |
| brief cost ($) | 0.00102 | 0.00000 | 0.00000 | 0.00000 |
| brief invalid ids | 0 | 0 | 0 | 0 |
| brief stale record called out | yes | yes | yes | yes |
| brief meeting in focus | yes | NO | NO | yes |
| **ask** accuracy (judge) | 78% | 63% | 71% | 61% |
| ask accuracy, original questions (q*) | 15/18 | 12/18 | 12/18 | 12/18 |
| ask accuracy, vague questions (v*) | 17/23 | 14/23 | 17/23 | 13/23 |
| ask citation recall | 90% | 90% | 91% | 90% |
| ask citation recall, vague (v*) | 87% | 89% | 91% | 89% |
| ask citation precision | 64% | 64% | 67% | 61% |
| ask forbidden cites | 0 | 1 | 1 | 1 |
| ask uncited sentences | 11 | 17 | 4 | 12 |
| ask latency p50 (s) | 1.5 | 0.8 | 8.7 | 13.5 |
| ask latency p95 (s) | 2.3 | 1.9 | 24.9 | 43.8 |
| ask latency max (s) | 2.4 | 2.7 | 34.6 | 49.8 |
| ask questions over 5s | 0 | 0 | 26 | 27 |
| ask output tokens per second | 63 | 81 | 7 | 4 |
| ask latency mean (s) | 1.2 | 0.8 | 8.8 | 13.8 |
| ask questions answered without a model call | 12 | 12 | 12 | 12 |
| ask tokens in/out (mean) | 588/73 | 560/68 | 599/63 | 600/59 |
| ask cost per question ($) | 0.00095 | 0.00000 | 0.00000 | 0.00000 |
| ask refusals | 4 | 3 | 3 | 4 |
| schema failures (ask+judge) | 0 | 0 | 0 | 0 |
| http retries (rate limits, 5xx) | 0 | 0 | 0 | 0 |
| whole benchmark wall time (s) | 272 | 152 | 1003 | 1485 |
| judge cost for this run ($) | 0.0800 | 0.0789 | 0.0793 | 0.0791 |

What the numbers say:

- **Haiku 4.5 is the best trade on every axis here.** 78% accuracy, 1.5s median answers, about $0.001 per question, $0.19 to ingest everything. It is under the 5s and $0.02 budget with room to spare.
- **Local models are free and fast only when they fit on the card.** llama 3B is 100% on the GPU and answers in 0.8s at 81 tokens per second. The 9B is 66% on the GPU and drops to 7 tokens per second (8.7s median, 26 of 41 questions over 5s). Ingest went from 55s to 554s.
- **The 35B-A3B mixture of experts was slower than the 9B and no more accurate.** Only 3B parameters are active per token, but all 22GB of weights have to be paged in from RAM and disk, which this machine cannot do quickly: 4 tokens per second, 13.5s median, 838s to ingest, and 205s to load the first time. ollama reports it as '95% on gpu' because only the resident part counts toward that figure. It scored 61%, level with llama 3B, with thinking off. On a card or unified memory that holds the weights, the picture would differ, and this run does not say how it would do there.
- **Accuracy is driven by the pipeline more than the model.** 12 of 41 questions are answered by code with no model call, and on those every model gets the same answer. Citation recall is 90% to 91% for every model, because citations are checked and added by code.
- **Where models differ is phrasing and discipline.** qwen3.5:9b leaves the fewest sentences uncited (4) and has the best precision (67%). llama 3B leaves the most (17) and its brief misses the customer meeting in the focus section. Every model produced the right structured output: zero schema failures in about 180 constrained calls per model.
- **Ingest checks against the answer key** (decisions, stale records, follow-ups, 29 checks): llama 29, Haiku and both Qwen models 28. The one miss is the same for all three: the email saying Taylor Brooks accepted another offer was not labelled as the current hiring decision. A 3B model passed it and three stronger models did not, which is a sign the check is sensitive to labelling choices, not to model size.
- **Hosted ingest is the expensive step** ($0.19 for 137 labelling calls, most of the 122k input tokens). It happens once per model and the result is cached, so swapping models costs one re-ingest.

## Evaluation

`eval/questions.json` has 41 questions, each with a reference answer and the item ids that support it (a group lists interchangeable copies, like the same update in gmail and slack). 18 are the original cases and 23 are vague: phrasing a founder would type, two Daniels, a role word, a company name, an issue id, and two unanswerable questions. Accuracy comes from an LLM judge. Citation recall and precision are plain id comparison, and abstention is checked in code (`apply_abstention`), because a judge passed 'I cannot find that' for answerable questions. Ingest checks name items from the answer key and the status each must end with.

What running every model through the vague questions taught us: the same questions failed on every model, so the pipeline was at fault and not the models. 'Is ACME-440 up to date' pulled every decision and buried the issue. 'Decision' in a history question sent it to the list of decisions. 'Meetings' sent an email question to the calendar. A bare 'what is blocked' listed other people's issues first. Each was a routing or retrieval bug, and each fix helped all four models. The first full run on this data scored 49% to 68%, and the table above is after those fixes.

## Notes and limits

- **The judge is the weak link.** One model grades every column, which makes scores comparable and does not make them right. It fails some good answers (a correct focus answer with one extra item) and passes some bad ones. Treat accuracy as a rough signal. Citation numbers are id comparison and are the sturdier ones.
- **Precision is low for every model** (about 60%). Models cite the evidence they used and the key lists the minimum, so extra correct citations count against them. It is a property of the key as much as of the models.
- **Small models blend topics.** With two decision threads in one context a 3B model sometimes attributes one thread's facts to the other. Scoping retrieval to the named topic helps, and code-rendered digests avoid it, but 'how is billing going' style summaries still show it.
- **Stale detection has false positives.** A deal for a second investor is flagged because the plan document names both and gives a different date. It is arguable, and it is also not a miss.
- **The decision gate is similarity plus a regex, and its recall is only measured on the planted cases.** A change of plan phrased unlike any prototype is missed.
- **Two decision groups can still merge or split wrongly.** Thresholds were measured on this data, where same-topic similarity ran 0.62 to 0.86 and cross-topic 0.47 to 0.62. Real data will shift them.
- **Filler is random.** About half the items are template filler. The 'customer issues repeating' section needs a report from the customer or two tools to count, which filters most of it, and a founder with a noisier inbox would want a better test.
- **Local model speed is memory bound on this machine.** The 6GB card holds a fraction of anything above 3B, so the 9B runs at 7 tokens per second and the mixture of experts at 4. See the table.
- **Linear ids carry the snapshot time** (`linear:ACME-142@20260314T2200`) because the export has several records per identifier.
- **Full rebuild on ingest.** Cheap here, and it avoids partial-update bugs. Real incremental sync needs per-source cursors and idempotent upserts.
- **Single founder, single tenant.** `FOUNDER_PERSON_ID` is a constant.
- **Style.** Comments follow `STYLE.json`. Python uses 4-space indent and single quotes, since the guide is written for JavaScript.

### Future work

- measure gate recall for decision extraction against the answer key, then widen it
- a per-claim entailment check for citations, not only word overlap
- a stronger judge for every column once spend is allowed, and a second judge to measure disagreement
- real connectors with incremental cursors and webhooks
- an install the founder can run without a terminal

## Dataset sources

- Gmail, Calendar, Slack, Linear, GitHub, Notion and HubSpot API shapes, documented in `data/SOURCES.md`
- identity matching: Ohio voter file and PPRL benchmarks
- decision and quoted-reply threads: LEDA (IETF mailing-list corpus)
- temporal grounding: UnSeenTimeQA, TempReason
- unanswerable questions: UAEval4RAG

## Traces

Development session: https://traces.com/s/jn71yyhd0t2x4zhbeyx533s2cs8gk8gq (currently private, set visibility before submitting)
