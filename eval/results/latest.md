# Eval results (14 questions)

model `llama3.2:latest`, judge `llama3.2:latest`

```
accuracy 93% | citation recall 76% precision 83% | forbidden cites 0 | ungrounded sentences 16
latency p50 0.6s max 1.6s (0 over 5s) | projected hosted cost $0.0011/question, actual $0 (local)
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 0.3 |
| q02 | decision_reversal | yes | 1.00 | 1.00 | 0 | 0.7 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 0.8 |
| q04 | duplicate_conflict | yes | 1.00 | 1.00 | 0 | 0.6 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.5 |
| q06 | cancelled_meeting | yes | 0.50 | 1.00 | 0 | 0.6 |
| q07 | cancelled_meeting | yes | 0.00 | 0.00 | 0 | 1.0 |
| q08 | history | yes | 0.00 | 0.00 | 0 | 0.6 |
| q09 | identity | yes | 1.00 | 1.00 | 0 | 0.7 |
| q10 | tasks | NO | 1.00 | 1.00 | 0 | 0.6 |
| q11 | shared_inbox | yes | 1.00 | 1.00 | 0 | 0.3 |
| q12 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.2 |
| q13 | decisions | yes | 0.67 | 0.67 | 0 | 1.6 |
| q14 | meeting_prep | yes | 0.50 | 1.00 | 0 | 1.2 |

## Answers

**q01** What did Daniel Kim say about the billing migration?
> Daniel Kim asked to push the billing migration a week . [slack:C01ENG:1773248400.000100]
judge: pass (ref: Daniel Kim asked Priya to push the billing migration back by a week | cand: Daniel Kim asked to push the billing migration a week . [slack:C01ENG:1773248400.000100])

**q02** What is the current authentication decision for the v2 API?
> The current authentication decision for the v2 API is to Ship v2 API with OAuth only . [linear:ACME-142@20260314T2200] This decision replaced Ship v2 API with OAuth + API keys  and was changed by Alex Chen . [linear:ACME-142@20260314T2200]
judge: pass (ref: OAuth only, then OAuth plus API keys on Mar 8 for Globex, then reverted to OAuth only on Mar 14 | cand: The current authentication decision for the v2 API is to Ship v2 API with OAuth only . [linear:ACME-142@20260314T2200] This decision replaced Ship v2 API with OAuth + API keys  and was changed by Alex Chen . [linear:ACME-142@20260314T2200])

**q03** What time is the Weekly Product Sync today?
> The Weekly Product Sync is today at 16:00 UTC. [calendar:2ded3454537257a5518fa9905e] The meeting title is 'Weekly Product Sync', its time is 16:00 UTC, attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, and it was rescheduled from its earlier slot on Friday. [calendar:2ded3454537257a5518fa9905e]
judge: pass (ref: Weekly Product Sync today 16:00 UTC | cand: The Weekly Product Sync is today at 16:00 UTC. [calendar:2ded3454537257a5518fa9905e] The meeting title is 'Weekly Product Sync', its time is 16:00 UTC, attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, and it was rescheduled from its earlier slot on Friday. [calendar:2ded3454537257a5518fa9905e])

**q04** What is the Q1 ship date?
> The current Q1 ship date is Mar 22. [slack:C02PROD:1772640000.222201] This decision replaced the previous one, which said ship Mar 20, and was changed by Sofia Reyes. [slack:C02PROD:1772640000.222201]
judge: pass (ref: March 20 | cand: Mar 22)

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.
judge: pass (correctly abstained)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> The Weekly Product Sync was CANCELLED . [calendar:7d2712a17add94eb1a82e92b23] It was originally scheduled for Friday March 13 , but was rescheduled to Sunday March 15 , and then moved to its current time .
judge: pass (ref: Weekly Product Sync on Friday Mar 13 was cancelled | cand: The Weekly Product Sync was CANCELLED . [calendar:7d2712a17add94eb1a82e92b23] It was originally scheduled for Friday March 13 , but was rescheduled to Sunday March 15 , and then moved to its current time )

**q07** Was the Daily Standup on March 13 cancelled?
> The Daily Standup on March 13 is CANCELLED. [calendar:c570daa9bf859a23cf07cf85fe] The event was originally scheduled from 14:00 UTC to 14:15 UTC, but it was moved to a cancelled earlier slot on March 13 10:00 UTC to March 13 11:00 UTC, and then rescheduled to Sun Mar 15 16:00 UTC. The calendar note states: "Cancelled due to offsite".
judge: pass (ref: Daily Standup on March 13 was cancelled | cand: The Daily Standup on March 13 is CANCELLED.)

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is to ship v2 API with OAuth only. [linear:ACME-142@20260314T2200] It replaced the previous decision to ship v2 API with OAuth + API keys, which was made by Alex Chen on March 6. [linear:ACME-142@20260314T2200]
judge: pass (ref: Priya Nair decided on March 6 to ship the v2 API with OAuth only | cand: The current decision is to ship v2 API with OAuth only. [linear:ACME-142@20260314T2200] It replaced the previous decision to ship v2 API with OAuth + API keys, which was made by Alex Chen on March 6. [linear:ACME-142@20260314T2200])

**q09** What did Rebecca Liu say about the Globex addendum?
> Rebecca Liu said the Globex addendum was signed, and this led to the decision to revert to OAuth-only authentication for the v2 API, which is now marked as CURRENT . [slack:C01ENG:1773522000.994933]
judge: pass (ref: Globex signed the OAuth-only addendum, so the v2 API reverts to OAuth only, and asked for ACME-142 to be updated | cand: Globex signed the OAuth-only addendum, and this led to the decision to revert to OAuth-only authentication for the v2 API, which is now marked as CURRENT)

**q10** Which Linear issues owned by me are blocked?
> ACME-342, Add pagination, Alex Chen [linear:ACME-342@20260225T0900]
ACME-349, Rate limit tuning, Alex Chen [linear:ACME-349@20260307T0900]
ACME-365, Rate limit tuning, Alex Chen [linear:ACME-365@20260222T0500]
ACME-352, Update dependency, Alex Chen [linear:ACME-352@20260225T1100]
ACME-316, Billing webhook retry, Alex Chen [linear:ACME-316@20260219T1200]
judge: FAIL (judge returned invalid json)

**q11** Who is out of office this week and who has context on billing?
> Daniel Kim is out of office from March 10-14 . [gmail:469b8c07901db7d8] Priya has context on billing . [gmail:469b8c07901db7d8]
judge: pass (ref: Daniel Kim was out of office Mar 10 to 14, and said Priya Nair has context on billing | cand: Daniel Kim is out of office from March 10-14 . [gmail:469b8c07901db7d8] Priya has context on billing . [gmail:469b8c07901db7d8])

**q12** Summarize investor-related activity this week.
> I can't find that in the available data.
judge: pass (correctly abstained)

**q13** What decisions were made recently?
> 1. v2 API authentication: 
    CURRENT: Ship v2 API with OAuth only (Alex Chen, Mar 14) . [linear:ACME-142@20260314T2200]
    PREVIOUS, replaced: Ship v2 API with OAuth + API keys (Alex Chen, Mar 8) . [linear:ACME-142@20260314T2200]
    PREVIOUS, replaced: Ship v2 API with OAuth only (Alex Chen, Mar 6) . [linear:ACME-142@20260314T2200]

2. Q1 roadmap dates: 
    CURRENT: ship Mar 22 (Sofia Reyes, Mar 4) . [slack:C02PROD:1772640000.222201]
    OUTDATED: Freeze Mar 10, ship Mar 20 (ACME-231) . [linear:ACME-231@20260304T1800]
judge: pass (ref: v2 API auth decision | cand: v2 API authentication: CURRENT: Ship v2 API with OAuth only (Alex Chen, Mar 14) . [linear:ACME-142@20260314T2200])

**q14** What should I know before my next meeting?
> Before your next meeting, you should know that the meeting title is Weekly Product Sync, it will take place on Sun 2026-03-15 16:00 UTC, and attendees include Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e] The meeting was rescheduled from Fri Mar 13 10:00 UTC to Sun Mar 15 16:00 UTC, as previously announced by Hannah Park on Tue 2026-03-10 18:00 UTC. [calendar:2ded3454537257a5518fa9905e]
judge: pass (ref: Weekly Product Sync today at 16:00 UTC with Priya Nair, Marcus Webb and Hannah Park. It was rescheduled from Friday Mar 13 | cand: Weekly Product Sync, it will take place on Sun 2026-03-15 16:00 UTC, and attendees include Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. The meeting was rescheduled from Fri Mar 13 10:00 UTC to Sun Mar 15 16:00 UTC, as previously announced by Hannah Park on Tue 2026-03-10 18:00 UTC.)
