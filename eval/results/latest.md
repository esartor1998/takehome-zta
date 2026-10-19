# Eval results (15 questions)

model `llama3.2:latest`, judge `llama3.2:latest`

```
accuracy 87% | citation recall 86% precision 85% | forbidden cites 0 | ungrounded sentences 1
latency p50 0.6s max 1.7s (0 over 5s) | projected hosted cost $0.0010/question, actual $0 (local)
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 0.6 |
| q02 | decision_reversal | NO | 1.00 | 0.50 | 0 | 0.8 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 0.7 |
| q04 | duplicate_conflict | yes | 1.00 | 1.00 | 0 | 0.6 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.4 |
| q06 | cancelled_meeting | yes | 0.50 | 1.00 | 0 | 0.6 |
| q07 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 0.6 |
| q08 | history | NO | 1.00 | 0.50 | 0 | 0.9 |
| q09 | identity | yes | 1.00 | 1.00 | 0 | 0.5 |
| q10 | tasks | yes | 1.00 | 1.00 | 0 | 0.7 |
| q11 | shared_inbox | yes | 1.00 | 1.00 | 0 | 0.5 |
| q12 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.4 |
| q13 | decisions | yes | 0.33 | 0.75 | 0 | 1.7 |
| q14 | meeting_prep | yes | 0.50 | 0.50 | 0 | 1.2 |
| q15 | stale_record | yes | 0.50 | 0.50 | 0 | 0.7 |

## Answers

**q01** What did Daniel Kim say about the billing migration?
> Daniel Kim asked to push the billing migration a week [gmail:c1abbf680fedaacd].
judge: pass (ref: Daniel Kim asked Priya to push the billing migration back by a week | cand: Daniel Kim asked to push the billing migration a week [gmail:c1abbf680fedaacd])

**q02** What is the current authentication decision for the v2 API?
> The current decision is Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [slack:C01ENG:1773522000.994933].

It replaced Ship v2 API with OAuth + API keys (v2 API authentication; this was later replaced) and was changed by Rebecca Liu [slack:C01ENG:1772992800.207664].
judge: FAIL (ref: OAuth only, then OAuth plus API keys on Mar 8, then reverted to OAuth only on Mar 14 | cand: The current decision is Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [slack:C01ENG:1773522000.994933].)

**q03** What time is the Weekly Product Sync today?
> The Weekly Product Sync is today at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The meeting title is 'Weekly Product Sync', its time is 16:00 UTC, attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, and it was rescheduled from its earlier slot on Friday [calendar:2ded3454537257a5518fa9905e].
judge: pass (ref: Weekly Product Sync today 16:00 UTC | cand: Weekly Product Sync is today at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The meeting title is )

**q04** What is the Q1 ship date?
> The current decision is: ship Mar 22 [slack:C02PROD:1772640000.222201].
It replaced the previous ship date of Mar 20, which was corrected by Sofia Reyes on Mar 4 [slack:C02PROD:1772640000.222201].
judge: pass (ref: Q1 ship date | cand: ship Mar 22 [slack:C02PROD:1772640000.222201])

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.
judge: pass (correctly abstained)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> The Weekly Product Sync was CANCELLED [calendar:7d2712a17add94eb1a82e92b23]. It was originally scheduled for Friday March 13 , but was rescheduled to Sunday March 15 , and then moved to its current time.
judge: pass (ref: Weekly Product Sync on Friday Mar 13 was cancelled | cand: The Weekly Product Sync was CANCELLED [calendar:7d2712a17add94eb1a82e92b23]. It was originally scheduled for Friday March 13 , but was rescheduled to Sunday March 15 , and then moved to its current time.)

**q07** Was the Daily Standup on March 13 cancelled?
> The Daily Standup on March 13 is CANCELLED [calendar:4554e5cfc14461dcdd7a91842f]. It was originally scheduled from 14:00 UTC to 14:15 UTC, but was cancelled due to being offsite [calendar:4554e5cfc14461dcdd7a91842f].
judge: pass (ref: Daily Standup on March 13 was cancelled | cand: The Daily Standup on March 13 is CANCELLED [calendar:4554e5cfc14461dcdd7a91842f]. It was originally scheduled from 14:00 UTC to 14:15 UTC, but was cancelled due to being offsite [calendar:4554e5cfc14461dcdd7a91842f].)

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is: Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [slack:C01ENG:1773522000.994933].

This decision replaced the original decision made by Priya Nair on Mar 6, which was: Ship v2 API with OAuth only (v2 API authentication; this was later replaced) [slack:C01ENG:1772812800.963148].
judge: FAIL (ref: Priya Nair decided on Mar 6 to ship the v2 API with OAuth only | cand: The current decision is: Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [slack:C01ENG:1773522000.994933].)

**q09** What did Rebecca Liu say about the Globex addendum?
> Rebecca Liu said the Globex addendum was signed, and the ACME-142 issue was closed [slack:C01ENG:1773522000.994933].
judge: pass (ref: Globex signed the OAuth-only addendum, ACME-142 update requested | cand: Globex signed the OAuth-only addendum, and the ACME-142 issue was closed [slack:C01ENG:1773522000.994933])

**q10** Which Linear issues owned by me are blocked?
> ACME-342, Add pagination, Alex Chen [linear:ACME-342@20260225T0900]
ACME-349, Rate limit tuning, Alex Chen [linear:ACME-349@20260307T0900]
ACME-365, Rate limit tuning, Alex Chen [linear:ACME-365@20260222T0500]
ACME-352, Update dependency, Alex Chen [linear:ACME-352@20260225T1100]
ACME-316, Billing webhook retry, Alex Chen [linear:ACME-316@20260219T1200]
judge: pass (ref: ACME-316, ACME-342, ACME-349, ACME-352, ACME-365 | cand: ACME-342, Add pagination, Alex Chen [linear:ACME-342@20260225T0900]
ACME-349, Rate limit tuning, Alex Chen [linear:ACME-349@20260307T0900]
ACME-365, Rate limit tuning, Alex Chen [linear:ACME-365@20260222T0500]
ACME-352, Update dependency, Alex Chen [linear:ACME-352@20260225T1100]
ACME-316, Billing webhook retry, Alex Chen [linear:ACME-316@20260219T1200])

**q11** Who is out of office this week and who has context on billing?
> Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya Nair has context on billing [gmail:469b8c07901db7d8].
judge: pass (ref: Daniel Kim was out of office Mar 10 to 14, and said Priya Nair has context on billing | cand: Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya Nair has context on billing [gmail:469b8c07901db7d8].)

**q12** Summarize investor-related activity this week.
> I can't find that in the available data.
judge: pass (correctly abstained)

**q13** What decisions were made recently?
> 1. The current decision is to ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [gmail:ceece9b31878fe40] [linear:ACME-142@20260314T2200].
2. It replaced the previous decision to ship v2 API with OAuth + API keys (v2 API authentication; this was later replaced) [slack:C01ENG:1772992800.207664].
3. The previous decision to ship v2 API with OAuth + API keys was changed by Marcus Webb [slack:C01ENG:1772992800.207664].
4. The current decision to ship v2 API with OAuth only was changed by Rebecca Liu [gmail:ceece9b31878fe40].
5. The current decision to ship v2 API with OAuth only was also changed by Priya Nair [slack:C01ENG:1773522000.994933].
judge: pass (ref: The v2 API auth decision went back to OAuth only on Mar 14. The Q1 ship date was corrected to Mar 22. The Weekly Product Sync moved to Sunday Mar 15 at 16:00 UTC | cand: 1. The current decision is to ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [gmail:ceece9b31878fe40] [linear:ACME-142@20260314T2200]. 2. It replaced the previous decision to ship v2 API with OAuth + API keys (v2 API authentication; this was later replaced) [slack:C01ENG:1772992800.207664]. 3. The previous decision to ship v2 API with OAuth + API keys was changed by Marcus Webb [slack:C01ENG:1772992800.207664]. 4. The current decision to ship v2 API with OAuth only was changed by Rebecca Liu [gmail:ceece9b31878fe40]. 5. The current decision to ship v2 API with OAuth only was also changed by Priya Nair [slack:C01ENG:1773522000.994933])

**q14** What should I know before my next meeting?
> Before your next meeting, you should know that the meeting title is 'Weekly Product Sync', it is scheduled for Sunday 2026-03-15 16:00 UTC, and it will be attended by Alex Chen, Priya Nair, Marcus Webb, and Hannah Park [calendar:2ded3454537257a5518fa9905e]. The meeting was rescheduled from Friday 2026-03-13 10:00 UTC, which was initially cancelled due to a Globex call moved [slack:C02PROD:1772866800.609886].
judge: pass (ref: Weekly Product Sync today at 16:00 UTC with Priya Nair, Marcus Webb and Hannah Park. It was rescheduled from Friday Mar 13 | cand: Weekly Product Sync, Sunday 2026-03-15 16:00 UTC, attended by Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, rescheduled from Friday 2026-03-13 10:00 UTC, initially cancelled due to Globex call)

**q15** Is the Linear issue ACME-231 up to date?
> The current decision for Linear issue ACME-231 is: ship Mar 22 [linear:ACME-142@20260314T2200].
It replaced the previous decision: Freeze Mar 10, ship Mar 20 [slack:C02PROD:1772640000.222201].
This change was made by Sofia Reyes [slack:C02PROD:1772640000.222201].
judge: pass (ref: ACME-231 still says freeze Mar 10 and ship Mar 20, but the ship date was corrected to Mar 22 | cand: The current decision for Linear issue ACME-231 is: ship Mar 22 [linear:ACME-142@20260314T2200].)
