# Founder assistant

A small context engine for a startup founder. It ingests Gmail, Google Calendar, Slack and Linear exports into one store, resolves who is who, collapses duplicates, works out which decisions are current, and answers questions with citations back to stored item ids. It also writes a morning brief without being asked.

Everything runs locally: llama 3.2 3B and nomic-embed-text through Ollama, SQLite, and ChromaDB. The model sits behind one file (`founder/llm.py`), so a hosted model is a rewrite of that file and nothing else.

## What it supports

- ingest from 4 sources, 666 items (311 gmail, 189 slack, 114 linear snapshots, 52 calendar)
- identity resolution across work email, personal email, slack id, linear id and shared inboxes
- cross-source duplicate detection and quoted-reply stripping
- decision tracking with reversals, corrections and stale records
- cancelled and rescheduled meetings
- hybrid retrieval (fts5, vectors, structured sql) with a fixed clock
- cited answers where every citation is checked in code
- a morning brief, and an eval harness with 15 questions

## How to run

You need Python 3.11+, [Ollama](https://ollama.com), and a GPU helps but is not required.

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/founder ingest          # builds .state/ (regenerates data/ first if it is missing)
.venv/bin/founder                 # no arguments prints the morning brief
.venv/bin/founder ask "What is the Q1 ship date?"
.venv/bin/founder chat            # interactive
.venv/bin/founder eval            # writes eval/results/latest.{json,md}
```

`data/` is gitignored because it is a symlink on my dev machine. `founder ingest` regenerates it from `synthetic_data_generator.py`, which is seeded and byte-for-byte reproducible. Set `FOUNDER_MODEL` to point at a different Ollama model.

## The dataset

`synthetic_data_generator.py` writes api-shaped exports: Gmail `users.messages.get`, Calendar `events.list`, Slack `conversations.history`, Linear GraphQL issues. It also writes directory exports (`slack_users.json`, `linear_users.json`, `contacts.json`) because real tenants expose those. `data/SOURCES.md` lists the real-world datasets and API docs the shapes were modelled on. The fixed clock is Sunday 2026-03-15 14:00 UTC, in `founder/config.py`.

Two things I changed in the generator: ids came from unseeded `uuid4`, so every run produced a different dataset, and a few identity cases were missing (Slack channels were empty, Daniel's Slack message did not exist). The ingest reads only `raw/`. It never touches `normalized/` or the answer key.

## How it handles the messy cases

**Identity.** `founder/identity.py` builds people from the contacts export, then attaches slack and linear ids by work email. Resolution order is directory match, then a unique handle match (`dkim.work@gmail.com` matches linear handle `dkim`), then a signature (`-- Daniel`). Daniel's personal address is deliberately missing from contacts, so his email resolves through the handle rule. An unknown mailbox on the company domain (`eng-team@`) is a shared inbox, not a person, and its signature identifies the author. We never merge on first name, so Alex Chen and Alex C. Morgan stay separate.

**Decision reversed.** The auth thread has three states across gmail, slack and linear (OAuth only, then OAuth plus API keys, then OAuth only). The local model labels each candidate item (decision, reversal, correction) and extracts a value. Code does the resolving: the last reversal or correction is the anchor, everything from there on is current, earlier events are superseded. The model is not allowed to decide what is current, because a 3B model asked that gets it wrong often enough to matter and code is testable. Rules override the model's label when the wording is unambiguous ("reverting", "corrected"), and a value the model did not copy from the text is thrown away. This happened 5 times on 16 events.

**Latest timestamp is not enough.** Linear ACME-231 was edited at t-11d+4h, after Sofia's correction (t-11d+1h) and the Slack repost (t-11d+2h), yet it still says "ship Mar 20". A max-timestamp rule picks the wrong answer. The rule here is claim level: a correction that retracts a value ("not Mar 20", "corrected from Mar 20") marks any later record still carrying that value as stale. The brief tells the founder to fix it.

**Duplicates.** Quoted tails ("Priya wrote: > ...") are cut off before indexing and kept separately, otherwise every later reply in a thread matches the old decision. Linear snapshots collapse to the newest per identifier, the older ones stay as history. Same update posted in two tools needs the same author, a 3h window, embedding cosine of at least 0.8 and real word overlap. Embeddings alone merged unrelated one-liners from the same person, because the "who and when" header we embed dominates a short body. Duplicates share a `dup_group`, take one slot in the answer context, and both copies stay citable.

**Cancelled and rescheduled meetings.** Calendar status is respected, cancelled events are excluded from "today" but pulled in when a question names the meeting, and the reschedule email and Slack post link to the event by title. A question about a named date returns that day's events plus where a cancelled one moved to.

**Time.** The clock is `config.NOW`. `datetime.now()` appears nowhere, because the machine date is nowhere near the dataset. Filler items dated after the clock (29 of them) are quarantined instead of showing up as "latest". 26 calendar events end before they start, so we assume an hour and flag them. "This week" is Mon Mar 9 to Sun Mar 15.

**Not in the data.** The prompt requires an exact refusal sentence when context does not contain the answer, and the eval checks abstention both ways (revenue impact and investor activity are both unanswerable).

## Architecture

```
raw exports -> identity -> normalise -> embed -> dedupe -> topics -> decisions -> sqlite + chroma
question -> intents, people, window -> 4 pulls -> rrf -> numbered context -> llm -> citation check
```

- `normalize.py` per-source adapters into one item shape
- `dedupe.py` snapshot collapse, cross-source dupes, topic clustering with union-find
- `extract.py` decision labelling and conflict resolution
- `store.py` sqlite is the source of truth, chroma only holds ids and vectors
- `retrieve.py` fts5 bm25, vector, structured sql (today, blocked, decisions, named meetings), person pull, fused with rrf
- `answer.py` context rendering, decision timelines, citation grounding
- `brief.py` morning brief, `evaluate.py` harness

Retrieval is hybrid on purpose. Embeddings are weak on exact ids, dates and status, which this dataset leans on, and weak lexical recall misses "customer issues repeating". Structured pulls get the highest weight.

**Citations.** The prompt numbers context items `[1]..[n]` and keeps real ids out of the text, since the model quotes headers it can see. Code maps numbers back to ids. Every citation is then checked against the words it supports: it is kept only if it covers the sentence about as well as the best retrieved item, and a missing citation is added from a current item with real overlap. History items (stale, superseded, cancelled) are never added to a bare sentence. This is lexical, so it can wrongly drop a cite on a heavily paraphrased answer.

## Morning brief

`samples/morning_brief.md` is the latest output. Sections are plain queries: today's schedule, plans that changed, stale records, blocked work you own, unanswered asks, and repeating customer issues. Asks are checked against evidence they were already handled (the issue moved to Done, the old invite is cancelled), so Rebecca's and Hannah's requests show as "looks handled". The model only phrases the top three facts, ranked by a score in code (a meeting soon, a record you must fix, an unhandled ask, a changed plan, blocked work). Given the whole list, an earlier version joined two unrelated issues in one line.

## Evaluation

`eval/questions.json` has 15 questions with a reference answer and the item ids that support it. Each expected-id entry is a group of interchangeable copies (the gmail and slack posts of one update). `founder eval` reports:

- accuracy from an LLM judge
- citation recall (share of expected groups with at least one cited member) and precision (share of cited ids that are expected)
- forbidden cites (stale or superseded items cited as current)
- latency and tokens per question, and a projected hosted cost

Latest results are in `eval/results/latest.md`, the starting point is `eval/results/baseline.md`.

| | baseline | latest |
| --- | --- | --- |
| accuracy (judge) | 64% | 87% |
| citation recall | 67% | 86% |
| citation precision | 67% | 85% |
| sentences without a citation | 14 | 1 |
| latency p50 / max | 0.7s / 1.5s | 0.6s / 1.7s |

Changes that moved those numbers, in order:

1. **Judge.** The first judge passed 86% on the baseline answers, including an answer about the wrong topic. Asking for lists of missing and wrong facts made it flag the reference's own facts as wrong. The version that behaved writes the reference key fact and what the candidate says before the verdict, with two worked examples, and abstention is decided in code. Same answers, regraded: 64%. The baseline above is the regraded number.
2. **Citation grounding.** The model cited two unrelated Linear issues for Daniel's billing question and left bare sentences uncited. The verifier raised citation recall from 67% to 76% on its own and dropped uncited sentences from 16 to 2 after a punctuation fix.
3. **Retrieval scoping.** Window became its own pull instead of a hard filter (a hard filter lost the out-of-office email, dated before the week it was about). Person results are ranked by the rest of the question instead of recency. Blocked is filtered to the named owner. Named meetings are pulled in every state, scoped to the named date. Decision topics are scored whole, so "Q1 ship date" stops pulling in the auth thread.
4. **Decision timelines.** A raw reversal thread made the model answer with whichever side it read last. Each topic is now a short set of plain sentences ("On Mar 14, Rebecca Liu reversed it to: ..."), one numbered entry per stage, each citing a person's own message. A labelled field list was garbled into the wrong person, so it is sentences.

Two questions (q09, q11) were reworded after the baseline because they were ambiguous (Rebecca also reported unrelated Globex flakes, and "last week" on a Sunday is ambiguous), and q15 was added afterward. The baseline file reflects the original wording.

### Performance budget

Under 5 seconds and under $0.02 per question: both met. Worst case is 1.7s on an RTX 2060 (the models are warmed before the run, so cold load is not charged to a question), and cost is $0 locally. At hosted prices of $1 and $5 per million tokens, the projected cost is about $0.001 per question (about 800 prompt tokens, 50 to 100 out). Ingest takes about 6s with cached model calls, or about 25s cold.

## Notes and limits

- **The judge is the weak link.** The same 3B model grades its own answers. q15 ("Is ACME-231 up to date?") passes the judge although the answer is wrong, because it says "ship Mar 22" without saying the record is stale. Treat accuracy as a rough signal with roughly plus or minus two questions of noise. Citation numbers are plain id comparison and are the more trustworthy ones. A stronger judge model is the first thing to change when a hosted model is allowed.
- **A 3B model blends topics.** With two decision topics in one context it sometimes attributes one topic's facts to the other. Scoping retrieval to the named topic helps. "What decisions were made recently?" still produces tangled answers, and q02 and q08 (the auth history questions) fail on the judge for that reason. The brief avoids it by not asking the model to reason.
- **"Is X up to date" questions** are answered by the brief deterministically, not by the question path.
- **The gate for decision extraction is a regex.** It is narrow on purpose (hundreds of filler items would otherwise hit the model), so a decision phrased without those words is missed. Recall of the gate is not measured.
- **Filler is random.** Roughly 600 of 666 items are generated filler. The customer-issue section of the brief counts mentions of customer names near words like "reported", which is noisy on this data.
- **Dedupe thresholds** (3h window, 0.8 cosine, 2 shared words) were tuned on 7 true pairs. One of the 7 pairs found is a loose match ("customer reported flake" and a Hooli email), and the Daniel billing pair is not detected as a duplicate because the wording differs. It is related, not a repeat.
- **Linear ids carry the snapshot time** (`linear:ACME-142@20260314T2200`) because the export has several records per identifier. A production adapter would key on identifier plus a history table.
- **Full rebuild on ingest.** Cheap here, and avoids partial-update bugs. Real incremental sync would need per-source cursors and idempotent upserts.
- **Single founder, single tenant.** `FOUNDER_PERSON_ID` is a constant.
- **Style.** Comments follow `STYLE.json` (checked with an adapted script). Python uses 4-space indent and single quotes, since the guide is written for JavaScript.

### Future work

- hosted model for answers and judging, with the same eval to compare
- measure gate recall on decision extraction against the answer key
- a per-claim check that a cited item entails the sentence, not just overlaps it
- real connectors with incremental cursors, and token-aware context packing
- a one-command install for the founder (the `founder` entry point is a start)

## Dataset sources

- Gmail, Calendar, Slack and Linear API shapes, documented in `data/SOURCES.md`
- identity matching: Ohio voter file and PPRL benchmarks
- decision and quoted-reply threads: LEDA (IETF mailing-list corpus)
- temporal grounding: UnSeenTimeQA, TempReason
- unanswerable questions: UAEval4RAG

## Traces

Development session: https://traces.com/s/jn71yyhd0t2x4zhbeyx533s2cs8gk8gq (currently private, set visibility before submitting)
