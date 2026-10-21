# Founder assistant

A small context engine for a startup founder. It ingests Gmail, Google Calendar, Slack, Linear, GitHub, Notion and a CRM into one store, works out who is who, collapses duplicates, tracks which decisions are current and which records have gone stale, finds what you owe people and what people owe you, and answers questions with citations back to stored item ids. It also writes a morning brief without being asked.

The model is a setting, not a dependency. Any chat model can be swapped in with one environment variable, and `founder bench` runs the same work on several of them and compares time, cost, accuracy and failures side by side.

## What it supports

- 7 sources, about 1,010 items, with outsiders (customers, investors, a candidate) as well as the team
- identity across work and personal email, display names in any header style, nicknames learned from the mail (nothing is listed by hand), initials, slack, linear, github and notion ids, and shared inboxes
- cross-source duplicates, quoted replies in gmail, outlook and short styles, forwards, html-only and multipart mail, and machine mail that stays out of the default pulls and is answerable when a question names the system that sent it
- decision tracking: reversals, corrections, and records in other tools that still state the old plan
- follow-ups in both directions: asks made of you, and promises you made
- cancelled, tentative, all-day and other-timezone events
- vague questions ('what's on today', 'what is daniel saying', 'anything urgent') routed before any model runs
- cited answers where every citation is checked in code
- an eval set of 70 questions (the nine the take-home names, vague ones, typos, multi-step ones, unanswerable ones, plans that slipped without a date, and people who go by other names), 18 semantic probes for the vector store, 41 unit tests that need no model, and a benchmark that compares models

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
.venv/bin/founder bench --judge-check ollama:llama3.2:latest   # how much do two judges agree
.venv/bin/founder ablate --e2e    # what each retrieval pull contributes, vector store included
.venv/bin/python -m unittest discover -s tests   # model-free unit tests
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
- 61 GitHub PR rows, 27 Notion pages and 5 CRM rows, with directory exports (`github_users.json`, `notion_users.json`, `crm_contacts.json`) the way real tenants expose them

A noise pass runs last, over messages people typed and nothing else: about 30% of emails and Slack messages lose a capital or a final full stop, swap a word for shorthand (pls, thx, tmrw, abt), pick up a rare typo, or gain a mobile signature or a legal disclaimer. Dates, amounts, ids, names, addresses and the words that carry a decision (decision, correction, cancelled, moved, approved) are protected, so a human could still answer every question. It adds difficulty only where real inboxes have it. Newsletters, receipts, notifications and bot posts stay machine-clean.

Three more scenarios use that mess on purpose: a renewal whose terms changed in a two-word reply ('ok by me. 2yr 15% fine, go ahead') with a Notion page, a CRM deal and an issue still on the old terms; a security report promised for 'tmrw' with a deadline written '3/18'; and an investor update draft answered inline between quoted lines. Around them are five out-of-office auto-replies, 'ack' and '+1' replies in threads that still have an open ask, and one meeting on two calendars under two titles.

A last scenario, added after a review of the first benchmark, tests what the stale check could not see. Five plans change without a new date in the usual form: the beta is 'pushed back for now' (no date at all), the webinar moves 'to next friday', an export 'slipped to april', a partner API is 'slipping to q3', and a contract renewal is on hold. Five near misses must stay current: a restatement ('still on track for Apr 10'), a question ('should we push the docs migration back a week?'), a deferral of a different thing, meeting notes that wonder whether something might slip, and 'timeline is unchanged'. The same scenario adds people who go by other names: 'Hi Becky', '-- Becky', 'Dan F.' on a personal address, and a '-- Dan' from an address nobody knows in a thread that has Daniel Foster in it. It is written after the noise pass so nothing above it changed: every earlier row is byte for byte the same, and 24 rows are new.

The answer key (`data/answer_key.json`) has a fragment for every scenario. The ingest never reads it or `normalized/`. The fixed clock is Sunday 2026-03-15 14:00 UTC, in `founder/config.py`.

## How it handles the messy cases

**Identity.** `founder/identity.py` builds people from the contacts export and the CRM, then attaches ids from each tool by email. For a sender it tries the directory, then a display name that matches one person (`Daniel F. <danf.photo@gmail.example>` is Daniel Foster because the last initial rules out Daniel Kim), then a unique handle (`dkim.work@gmail.com` and linear `dkim`), then a signature, where a full name beats a bare first name, and a first name is looked up among everyone (customers sign with first names too) and settled by who is in the thread, or by teammates only when the sender is a role mailbox on our own domain. Unquoted `LAST, First <x@y>` headers are split by hand, since the standard parser reads them as two addresses. An unknown mailbox on the company domain is a shared inbox, and a bulk or no-reply sender is a machine. We never merge on a first name alone. Nicknames are not listed anywhere: `founder/names.py` ties a word to a roster first name when it truncates it (three letters or more: dan, pri, marc) or when the embedding model puts it clearly closest to that one name (a margin over the runner-up, because junk words score about 0.5 against every name and real nicknames 0.65 to 0.9). Ingest also reads the display names, greetings and sign-offs in the mail, so 'Hi Becky' and '-- Dan' teach the roster, and a question word the mail never used ('bex') gets the same test at question time. 'mark' stays unresolved when the roster has both Marcus and Michael. A first name in a question is the opposite case: it matches everyone who has it, and the answer says so.

**Decisions.** The model labels each candidate item (decision, reversal, correction, proposal) and names its subject. Code does the resolving. Candidates come from a regex plus similarity to generic 'change of plan' sentences. Groups are built around anchors, items that clearly change a plan, by thread and issue links, by embedding similarity of title and body, and by a shared specific person or company, with an average-similarity brake because single links chained every topic together. The last reversal or correction is the anchor, and everything after it is current. Rules override the model only when the wording starts a sentence ('Correction:', 'Reverting to'), because 'ship date needs another look after Sofia's correction' mentions a correction without making one.

**Stale records.** Latest timestamp is not enough: Linear ACME-231 was edited after Sofia's correction and still says March 20. Two detectors cover this. A correction that names the value it replaces ('not Mar 20') marks any later record still carrying it. And `founder/stale.py` goes record by record: it finds newer items that are close in meaning or share a specific person or company, keeps only those carrying a date, price or amount the record lacks (a relative date such as 'next Friday' is resolved against when it was written, and a bare month or quarter counts: 'slipped to April', 'now Q3'), or a status change. A change that carries no value at all ('pushed the timeline back for now', 'holding off on the renewal') is the one place the model reads a sentence: code picks the sentences that share a subject word with the record and are not questions or hedges, template mail and meeting notes are skipped, and the model answers yes or no. Similarity to example sentences could not do it, because 'the launch is on track' and 'we are holding off until Q3' scored alike. Among equally strong contradictions the newest item is the update. The model then picks which newer item shows it. A 3B model asked 'is this record outdated' says yes to everything and flagged 60 routine issues. Asked to pick the item, with plain code deciding whether the two disagree, it is useful. Meeting notes are history and are never stale.

**Follow-ups.** `founder/followups.py` finds asks (an email to you, a slack mention, a PR review request) and promises (your latest message in a thread). The model extracts what was asked and the deadline in the sender's words. Whether it is open is code: a reply by you or a teammate in the thread, an issue it names that moved to Done afterwards, a PR that merged. Deadlines resolve against the message's own date, so 'by Monday' sent on a Friday is the next Monday. Closers like 'let me know if you want a deeper dive' and 'I will follow up if nothing changes by EOD' are not asks or promises, and a pattern list keeps them out.

**Duplicates.** Quoted tails are cut before indexing and kept separately. Linear snapshots collapse to the newest per identifier. The same update posted in two tools needs the same author, a 3h window, embedding similarity and real word overlap, since embeddings alone merged unrelated one-liners.

**Time.** The clock is `config.NOW`, and `datetime.now()` appears nowhere. Items dated after the clock are quarantined. All-day events use a date, other events keep their original zone and are shown in UTC with the local time beside them. Events that end before they start are flagged and given an hour.

**Not in the data.** The prompt requires an exact refusal sentence, and the eval checks refusal both ways (runway and the CFO are unanswerable, and the system must not invent them from the fundraising figures that are in the data).

## Vague questions

`founder/route.py` turns 'tomorrow?' or 'dk?' into a plan before any model runs: what kind of answer is wanted, who is meant, which day, and which words stand for a family of words. It is plain rules, so the same question gets the same plan whichever model answers.

- `schedule`: what is on, in time order, with cancelled, tentative, all-day, already-happened and other-timezone events marked, and prep for meetings with outsiders (their open asks of you, their open issues)
- `followups` (and 'anything overdue', 'what did I promise hooli'), `blocked`, `customers`, `decisions`, `catchup`, `meeting emails`: lists of facts the database already holds, rendered by code from the same facts as the brief
- `prep` ('what do I need to do before the globex call', 'what should I know before my next meeting'): the meeting, its guests' open asks of you, your promises to them, open issues for their company and the pull requests waiting on you that name them, and the emails linked to it, all by code
- `company` ('globex', 'what's the story with hooli'): the whole account in one answer, meetings, open asks both ways, open issues, repeated problems, recent mail, and the deal with any out-of-date note
- `focus`: the model phrases the top ranked facts, and if it ignores the format the facts themselves become the lines
- `person`: what someone has been saying, ranked by how unlike the template mail each item is. A bare first name covers every person with it, labelled, a role word ('investors') covers the people with that role, and a company ('hooli') covers the people we know there
- `topic`: hybrid retrieval (fts5, vectors, structured sql) with a search glossary built from the mailbox at ingest, and exact pulls for named issues, PRs and meetings

Code-rendered answers use no tokens and cannot garble a list. Setting `FOUNDER_DIGEST=llm` sends them through the model instead, which is how a benchmark compares models on identical facts.

## Hardening against messy input

The noise and the new scenarios exposed gaps, and each fix below has a unit test or an eval question behind it.

| what real mail does | what handles it |
| --- | --- |
| answers typed between the quoted lines of the message they answer | quote splitting keeps the unquoted lines of an inline reply, and cuts only the quoted ones |
| out-of-office auto-replies | `Auto-Submitted` headers and 'Automatic reply' subjects make a message machine mail, which is indexed but never an ask or a decision |
| 'Dan F.' for Daniel Foster, '-- Dan' from an address nobody knows | nicknames come from names.py (prefix or a clear embedding winner), and a sign-off that fits two people is settled by the thread's participants |
| a plan that slips without a new date, or to 'next Friday', 'April', 'Q3' | relative dates are resolved against the message, months and quarters are values, and a model confirms a value-less deferral one sentence at a time |
| a personal block or focus slot with no guest list | the organizer is at their own event, so it shows in 'what is on today' |
| a forwarded message | its text is searchable and embedded with the forwarder's note, and never counted as the forwarder's own decision or ask |
| automated mail ('did the Paymint invoice arrive') | kept out of the default pulls, and a question that names a system that mails us gets its own pull |
| 'by Jan 10' written in December, or 18/3 in a day-first export | a month and day take the year nearest the message, and the slash order is read off the export |
| a calendar of all-day events in another time zone | all-day events start at local midnight in the founder's zone, read off the calendar |
| deadlines written 'tmrw', '3/18', 'thurs', 'the 20th', 'eow' | one parser against the message's own date, with 'mon' kept from matching 'month' |
| an 'ack' or '+1' from a teammate in a thread with an open ask | only a substantive reply (eight words or more, not an acknowledgement) closes an ask |
| a hedge ('maybe we go with $59?') | hedged wording is a proposal and cannot become the current decision |
| one meeting on two calendars under two titles | same start, two shared guests and a shared title word make one event, listed once |
| a template email that names the same issue after the real change | only an event that reads like a change can anchor a decision, and template mail (low novelty) never reaches the model |
| the founder typing 'whats on tdy', 'anyting from investers', 'dnaiel' | shorthand is expanded and typos are corrected against the words the inbox actually contains, not an English dictionary |
| a question that names a tool ('is the notion page current') | that tool is searched on its own, and a stale record brings the update behind it into the context |
| a one-line answer ('ok by me') that shares no words with the question | the conversation around the best hits is pulled in |
| a record that is out of date by a percentage or a term, not a date | values are typed (date, amount, percent, duration), and the new value's sentence must share a subject word with the record |

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

Judge `claude-haiku-4-5-20251001` for every column, 70 questions, one model at a time on an otherwise idle machine (RTX 2060 6GB, 23GB RAM, 4 cores). Every column is from the same code and the same data. Timings are wall clock. The full per-question results are in `eval/results/models/*.json`.

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

Run after the identity, stale-record, glossary and date changes described under hardening, on 70 questions (the 61 earlier ones plus 7 on softly worded changes and 2 on nicknames). The columns are not comparable with the earlier 61-question table, which scored Haiku 85%, Llama 70%, the 9B 74% and the 35B 80%. One caveat: these columns were run while an experimental query-time pull (`FOUNDER_FEEDBACK`, words learned from the top hits of each question word) was on. Ablation showed it lowered recall (89% against 92%) and it was removed. Haiku re-run without it scored 81% (57/70), citation recall 90%, precision 55%, p50 1.6s, which is within judge noise of the 83% above. The three local columns were not re-run.

**Fixes after this run (Haiku only, other columns not re-run).** The five questions every model failed were traced to the pipeline. Two fixes were made: a thread now contributes both its newest and its most distinctive message to a person's activity (the first message of a conversation carried the date and the ask, and 'newest per thread' dropped it), and 'what should I focus on' now lists the whole docket under the top three priorities, including the records that still state an old plan, instead of the first eight facts. Meeting prep also stopped listing a company's issues once per guest. Haiku then scored 84% (59/70), recall 90%, precision 54%, p50 1.7s: `q16`, `v09` and `v04` pass; `q12` still fails because a Slack message that says only 'Jordan says they cannot close before May 15' is not linked to Jordan Pryce, and `w01` is marked stale by an unrelated record that shares the word 'ships'. One answer ('who's our CFO') took 8.5s against 3.4s earlier, with no code on its path changed, so it reads as a slow API call. Two further measures were not built: linking bare first-name mentions to the roster at ingest, and matching stale records by subject words instead of any shared label word.

What the numbers say:

- **Haiku 4.5 is still the best trade.** 83% accuracy (81% on the re-run), 1.5s median, 4.2s slowest, about $0.0014 per question including the checks it runs on its own citations. It meets the 5s and $0.02 budget with room to spare. Ingesting everything once costs $0.29, up from $0.14 because ingest now also builds the glossary (about 40 extra model calls).
- **The 9B moved up and Llama down.** The 9B is at 80% (74% before) and the 35B at 79% (80%), so the ordering among the larger models is within noise on 70 questions. Llama 3B fell to 71% and is the only model that failed an ingest check (50/51), and it raised the most flags (7). Accuracy per model changes by a few points between runs of the same code, so read gaps under about five points as ties.
- **Five questions fail on every model**: `q12`, `q16`, `v04`, `v09`, `w01`. They point at the pipeline, not the models. `q12` (investor activity) leaves out that Northwind cannot close before May 15. `q16` and `v09` (what to focus on) bury the cohort ARR owed to an investor under a long list of Globex ticket states. `w01` invents 'Apr 10' as the new beta date by running two records together. `v04` (two Daniels) misses that Daniel Foster says the SSO loops are back.
- **Local ingest got much slower, from the glossary.** 317s for Llama, 1,908s for the 9B and 2,550s for the 35B, against 119s to 606s before. The extra calls are one per ten glossary terms. It runs once per mailbox, and the glossary is data, so a hosted model can build it and local models can reuse it.
- **Local speed is memory bound on this machine.** Llama 3B is on the card at 79 tokens per second. The 9B and the 35B-A3B run at 7 and 3, so 47 of 70 questions take over 5s on either.
- **23 of 70 questions are answered by code with no model call**, the same on every model.
- **Citation recall is 84% to 91%** because citations are checked and added by code. Precision fell to 48% to 56% from 58% to 60% because code-rendered lists are no longer cut (a founder wants the whole docket) so more items are cited that the key does not list. The key is minimal, so this is a cost of completeness and not of accuracy.
- **Ingest checks against the answer key** (51 checks across decisions, stale records, follow-ups, identity and nicknames): Haiku, the 9B and the 35B pass all 51, Llama 50.
- **Citation flags** (a claim whose citation did not hold and could not be repaired): Haiku raised 6, none on a wrong answer, Llama 7 (57% of flagged answers were wrong), the 9B and the 35B 2 each, none wrong. Flags are rare and still catch little.
- **The 35B missed the meeting in the brief** ('brief meeting in focus: NO'), the only model to do so in this run.

**How trustworthy is the judge?** `founder bench --judge-check ollama:llama3.2:latest` re-grades Haiku's answers with the Haiku judge twice and with Llama as a second judge. Haiku agrees with itself on 100% of verdicts, so repeats are stable. Haiku and Llama agree on 72% of verdicts with Cohen's kappa of -0.06, which is no agreement beyond chance, even though their accuracy figures (85% and 84%) look alike (measured on the earlier 61-question run and not repeated). A weak judge cannot compare models here, and a strong one is a single point of failure: at least three of Haiku's misses on its own answers (`n02`, `n06`, `q01`) read as correct to a person. Treat accuracy as a rough ranking and read the per-question table before drawing a conclusion.

## Evaluation

`eval/questions.json` has 70 questions, each with a reference answer and the item ids that support it (a group lists interchangeable copies, like the same update in gmail and slack). 18 are the original required cases, 3 are the take-home's own wording for what happened across the company, repeated customer issues and blocked tasks, 23 are vague (phrasing a founder would type, two Daniels, a role word, a company name, an issue id, two unanswerable questions), 8 are the same questions with typos and shorthand ('whats on tdy', 'anyting from investers'), 7 cover the earlier scenarios, 7 cover plans changed in soft words ('pushed back for now', 'moved to next friday'), 2 use a nickname or a first-name sign-off, and 2 need several steps ('what do I need to do before the Globex call', 'anything overdue'). `eval/semantic_probes.json` adds 18 questions worded unlike their source for the vector tests. Accuracy comes from an LLM judge. Citation recall and precision are plain id comparison. Abstention is judged like every other answer: the judge is told that when the reference says the information is not available, a candidate is right only if it says it cannot find it. An earlier version overrode the judge in code for this. That was removed, and regrading the saved answers changed one verdict out of 164. Ingest checks name items from the answer key and the status each must end with.

What running every model through the questions taught us, twice: the same questions failed on every model, so the pipeline was at fault and not the models. 'Is ACME-440 up to date' pulled every decision and buried the issue. 'Decision' in a history question sent it to the list of decisions. A bare 'what is blocked' listed other people's issues first. 'What changed' missed the seed close, the hiring outcome and the renewal terms because the model labelled them decisions and nothing anchored them, so stale records now feed back into the decision history. A template email that named the same issue after the real change became the current state, so only an event that reads like a change can anchor a decision. Each fix helped every model.

One lesson was about the key and not the code: seven references were incomplete, and the models were right to list more than the key did. They were corrected, and the benchmark notes say so.

## Citation checks and flags

Every citation in an answer is checked in code against the words it is supposed to support. When a claim's citation does not hold (the cited item says something else, or a sentence has no source at all), the model gets one narrow job: read the claim and the sources, say whether any source supports it, and name the best one. A supported verdict with a named source repairs the citation. Anything else becomes a flag, and `founder ask` prints it under the answer:

```
Check before relying on this (1):
- why the launch date was pushed  [not_supported: no source gives a reason]
```

**Measured** on the earlier 61 questions (not repeated on 70) with each model investigating its own answers: Haiku flagged 2 answers and 1 was wrong, Llama 4 and 1, the 35B 5 and none, the 9B none. Remarks about the answer ('Nothing is marked STALE', 'What remains open: ...') and answers whose other citations held are no longer flagged, which removed most of the noise of the first version. What is left is rare and catches about one wrong answer in ten, so it works as a prompt to look and does not yet identify bad answers.

Flags are in the result as `flags` (claim, kind, verdict, reason, cited ids). Only claims whose citation failed (a number, date, id or name in the sentence, and no citation that holds) are examined, at most four per answer, and the rest are flagged without a look. The extra calls count toward the answer's tokens, cost and time. `FOUNDER_VERIFY=0` turns the model step off and leaves the lexical check. `founder bench` reports how many answers carried a flag, and flag precision and recall against the judge's verdicts (what share of flagged answers were wrong, and what share of wrong answers were flagged).

## Does the vector store earn its place

`founder ablate` switches retrieval pulls off one at a time and measures what a model would see, with no model involved: recall of the expected evidence, precision, rank of the first hit, and per question whether the vector pull brought in or pushed out expected items. It covers the 33 eval questions that use retrieval, because schedule, follow-up and similar questions are rendered by code and never touch the vector store, and 15 semantic probes (`eval/semantic_probes.json`) worded unlike the source text ('who is unavailable this week' for an out-of-office note). `--e2e` repeats the comparison with a model answering and a judge grading.

| | eval questions (42) | semantic probes (15) |
| --- | --- | --- |
| everything | 92% recall | 77% recall |
| everything except vectors | 87% | 60% |
| vectors alone | 74% | 63% |
| full text search alone | 68% | 53% |
| vector pull helps / hurts / no change (recall) | 3 / 1 / 38 | 3 / 0 / 12 |

- On the questions as written the vector pull adds 5 points of recall (92% against 87%) and 0.06 of first-hit rank. It rescued three questions (out-of-office, billing, the onboarding date) and hurt one ('what's the deal with sso', where it pushed out an expected item).
- On questions worded unlike the source it does the work: recall 60% to 77%, first-hit rank 0.20 to 0.45. It found 'who is unavailable this week', 'when is the board getting together' and 'who needs to look at my code changes'. It never pushed an expected item out in this set.
- It makes the context a little bigger: 10.8 items against 9.4 on the probes, 8.7 against 8.6 on the questions.
- Weight is a free parameter. At double weight recall on the eval questions is 94% and first-hit rank 0.77 (against 0.65), with probe recall unchanged at 77%. That is a hint, not a result: the weight was not tuned on held-out questions and is left at 1.0.
- Neither pull is enough alone. Vectors alone reach 74% and full text alone 68% on the questions as written (63% and 53% on paraphrases), and both have the lowest precision, 12%. Together they reach 92% and 77%.
- Answered end to end by Haiku on the earlier 33 retrieval questions, accuracy was 91% with the vector pull and 94% without. That was not repeated on the new data. It was within noise and says better evidence did not obviously turn into better answers.
- It costs about 19 ms per question, one embedding call.

The probes were written by us, from knowledge of the data, to be paraphrases, and there are 15 of them. They show where the vector store can help, not how often a real founder's question falls there. The embeddings are also used at ingest (duplicates, the decision gate, stale records, novelty), which these tests do not switch off.

## Notes and limits

- **The judge is the weak link.** One model grades every column, which makes scores comparable and does not make them right. It fails some good answers (a correct focus answer with one extra item) and passes some bad ones. Treat accuracy as a rough signal. Citation numbers are id comparison and are the sturdier ones.
- **Precision is low for every model** (58% to 60%). Models cite the evidence they used and the key lists the minimum, so extra correct citations count against them. It is a property of the key as much as of the models.
- **Small models blend topics.** With two decision threads in one context a 3B model sometimes attributes one thread's facts to the other. Scoping retrieval to the named topic helps, and code-rendered digests avoid it, but 'how is billing going' style summaries still show it.
- **Stale detection has false positives.** A deal for a second investor is flagged because the plan document names both and gives a different date. It is arguable, and it is also not a miss.
- **The decision gate is similarity plus a regex, and its recall is only measured on the planted cases.** A change of plan phrased unlike any prototype is missed.
- **Two decision groups can still merge or split wrongly.** Thresholds were measured on this data, where same-topic similarity ran 0.62 to 0.86 and cross-topic 0.47 to 0.62. Real data will shift them.
- **Filler is random.** About half the items are template filler. The 'customer issues repeating' section needs a report from the customer or two tools to count, which filters most of it, and a founder with a noisier inbox would want a better test.
- **Local model speed is memory bound on this machine.** The 6GB card holds a fraction of anything above 3B, so the 9B runs at 7 tokens per second and the mixture of experts at 5. See the table.
- **The noise is mild and was added by us.** Real mail has more kinds of mess than a pass of shorthand, dropped capitals, rare typos and signatures: other languages, screenshots, attachments nobody reads, replies to the wrong thread. The numbers say the pipeline copes with this much, not with that.
- **Typo correction uses the inbox's own vocabulary.** It fixes 'investers' because the inbox has 'investors', and cannot fix a word the inbox has never seen, or a typo that is itself another word in it.
- **The vector pull did not improve end-to-end accuracy on our sample**, though it improves the evidence a model sees when the question is worded unlike the source. The weight is probably too high.
- **Nothing about this company is written into the code any more, except the taxonomy of customer problems** (`ISSUE_TYPES` in `founder/brief.py`: timeout, login loop, invoice, flake, outage). Slack channel names come from `slack_channels.json`, issue keys from the Linear identifiers, customers from the CRM, nicknames from the mail, related search words from the glossary. The taxonomy is the next thing to derive, by clustering.
- **The search glossary costs a little ranking.** A model lists related words for each word the inbox uses, and code keeps those the inbox contains and few items use. Against the hand-written table it replaced, retrieval recall is level (eval 0.93 against 0.94, paraphrase probes 0.83 on both), and the first expected item ranks lower on the paraphrase probes (MRR 0.54 to 0.29). Embedding neighbours of single words were tried first and are poor ('sso' lands next to 'https').
- **Lists are no longer cut.** A list rendered by code shows every item. A list a model phrases (`FOUNDER_DIGEST=llm`) is capped to its context and says how many more exist. Citation precision fell for the same reason: more items are listed, and each is cited.
- **Linear ids carry the snapshot time** (`linear:ACME-142@20260314T2200`) because the export has several records per identifier.
- **Full rebuild on ingest.** Cheap here, and it avoids partial-update bugs. Real incremental sync needs per-source cursors and idempotent upserts.
- **Single founder, single tenant.** `FOUNDER_PERSON_ID` is a constant.
- **Style.** Comments follow `STYLE.json`. Python uses 4-space indent and single quotes, since the guide is written for JavaScript.

### Metrics not built yet

The benchmark reports a lot and still hides parts of the story. Missing, and worth adding before a stronger model is judged against these numbers:

- claim-level citation precision (does the cited item entail the claim), instead of id overlap against a minimal key
- retrieval precision and recall at k by question type, kept per question so a regression names the question
- variance: repeated runs, other seeds, and a second judge to measure how often judges disagree
- cost per correct answer, and refusal calibration (refused when it should and answered when it should)
- a human-labelled sample to check the judge against
- latency under concurrent use, since every number here is one question at a time

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
