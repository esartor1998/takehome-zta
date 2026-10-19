# Eval results (18 questions)

model `llama3.2:latest`, judge `llama3.2:latest`

```
accuracy 78% | citation recall 88% precision 81% | forbidden cites 0 | ungrounded sentences 4
latency p50 0.7s max 1.9s (0 over 5s) | projected hosted cost $0.0010/question, actual $0 (local)
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 0.7 |
| q02 | decision_reversal | NO | 1.00 | 0.50 | 0 | 0.8 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 0.8 |
| q04 | duplicate_conflict | yes | 1.00 | 1.00 | 0 | 0.6 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.2 |
| q06 | cancelled_meeting | yes | 0.50 | 1.00 | 0 | 0.6 |
| q07 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 0.6 |
| q08 | history | NO | 1.00 | 0.33 | 0 | 1.1 |
| q09 | identity | yes | 1.00 | 1.00 | 0 | 0.3 |
| q10 | tasks | yes | 1.00 | 1.00 | 0 | 0.7 |
| q11 | shared_inbox | yes | 1.00 | 1.00 | 0 | 0.5 |
| q12 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.2 |
| q13 | decisions | yes | 0.33 | 0.25 | 0 | 1.9 |
| q14 | meeting_prep | yes | 0.50 | 1.00 | 0 | 0.8 |
| q15 | stale_record | NO | 0.50 | 0.33 | 0 | 0.7 |
| q16 | daily_priorities | NO | 1.00 | 0.67 | 0 | 1.2 |
| q17 | followups | yes | 1.00 | 1.00 | 0 | 0.4 |
| q18 | meeting_prep | yes | 1.00 | 0.50 | 0 | 1.1 |

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

This decision replaced the previous decision: Ship v2 API with OAuth + API keys (v2 API authentication; this was later replaced) by Marcus Webb on Mar 8 [slack:C01ENG:1772992800.207664].

The original decision on Mar 6 was made by Priya Nair, who decided: Ship v2 API with OAuth only (v2 API authentication; this was later replaced) [slack:C01ENG:1772812800.963148].
judge: FAIL (ref: Priya Nair decided on March 6 to ship the v2 API with OAuth only | cand: The current decision is: Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [slack:C01ENG:1773522000.994933].)

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
> Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya has context on billing [gmail:469b8c07901db7d8].
judge: pass (ref: Daniel Kim was out of office Mar 10 to 14, and said Priya Nair has context on billing | cand: Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya has context on billing [gmail:469b8c07901db7d8])

**q12** Summarize investor-related activity this week.
> I can't find that in the available data.
judge: pass (correctly abstained)

**q13** What decisions were made recently?
> 1. The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933].
2. It replaced the previous decision to ship v2 API with OAuth + API keys, which was changed by Marcus Webb [slack:C01ENG:1772992800.207664].
3. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth only, made by Priya Nair [gmail:403df41545d6ec2d].
4. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth + API keys, made by Priya Nair [slack:C01ENG:1772812800.963148].
5. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth + API keys, made by Marcus Webb [slack:C01ENG:1772992800.207664].
judge: pass (ref: v2 API auth decision went back to OAuth only on Mar 14. Q1 ship date was corrected to Mar 22. Weekly Product Sync moved to Sunday Mar 15 at 16:00 UTC | cand: 1. The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933]. 2. It replaced the previous decision to ship v2 API with OAuth + API keys, which was changed by Marcus Webb [slack:C01ENG:1772992800.207664]. 3. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth only, made by Priya Nair [gmail:403df41545d6ec2d]. 4. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth + API keys, made by Priya Nair [slack:C01ENG:1772812800.963148]. 5. The current decision is to ship v2 API with OAuth only, which replaced the previous decision to ship v2 API with OAuth + API keys, made by Marcus Webb [slack:C01ENG:1772992800.207664].)

**q14** What should I know before my next meeting?
> Before your next meeting, you should know that the Weekly Product Sync meeting has been rescheduled from Friday, March 13 to Sunday, March 15 at 16:00 UTC. The attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park [calendar:2ded3454537257a5518fa9905e]. The meeting was originally scheduled for Friday, March 13 but was moved due to a calendar note.
judge: pass (ref: Weekly Product Sync meeting rescheduled from Friday Mar 13 | cand: Weekly Product Sync meeting has been rescheduled from Friday, March 13 to Sunday, March 15 at 16:00 UTC)

**q15** Is the Linear issue ACME-231 up to date?
> The current decision for Linear issue ACME-231 is: Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [linear:ACME-142@20260314T2200].

It replaced the previous decision: Ship v2 API with OAuth + API keys (v2 API authentication; this was later replaced) [slack:C01ENG:1772992800.207664].

It was changed by Sofia Reyes [slack:C02PROD:1772640000.222201].
judge: FAIL (ref: ACME-231 still says freeze Mar 10 and ship Mar 20, but the ship date was corrected to Mar 22 | cand: The current decision for Linear issue ACME-231 is: Ship v2 API with OAuth only (v2 API authentication; this is the CURRENT decision) [linear:ACME-142@20260314T2200].)

**q16** What should I focus on today?
> 1. Confirm attendance at the rescheduled Weekly Product Sync meeting at 16:00 UTC today, as it's crucial for aligning the team's efforts. [calendar:2ded3454537257a5518fa9905e]
2. Update the record ACME-231 to reflect the new ship date of Mar 22, ensuring the Q1 roadmap stays on track. [slack:C02PROD:1772640000.222201]
3. Review and address the Rate limit tuning issue, as it's currently blocked and owned by you, requiring your attention to resolve. [linear:ACME-365@20260222T0500]
judge: FAIL (ref: Weekly Product Sync at 16:00 UTC today, update Linear issue ACME-231 ship date to Mar 22 | cand: Confirm attendance at the rescheduled Weekly Product Sync meeting at 16:00 UTC today, as it's crucial for aligning the team's efforts. Update the record ACME-231 to reflect the new ship date of Mar 22, ensuring the Q1 roadmap stays on track.)

**q17** What follow-ups am I missing?
> Rebecca Liu's ask is already handled, no action needed [gmail:ceece9b31878fe40]. Hannah Park's ask is already handled, no action needed [gmail:ff9c102bbfa27a06].
judge: pass (ref: None are outstanding | cand: Rebecca Liu's ask is already handled, no action needed [gmail:ceece9b31878fe40]. Hannah Park)

**q18** Which emails relate to upcoming meetings?
> Here are the emails related to upcoming meetings:

1. Hannah Park, subject: Weekly Product Sync moved, Tue 2026-03-10 18:00 UTC, Weekly Product Sync [gmail:ff9c102bbfa27a06]
2. Hannah Park, subject: Weekly Product Sync moved, Sun 2026-03-15 16:00 UTC, Weekly Product Sync [gmail:ff9c102bbfa27a06]
3. Priya Nair, subject: Pushing Weekly Product Sync by a week, Sun 2026-03-15 14:00 UTC, Weekly Product Sync [calendar:2ded3454537257a5518fa9905e]
judge: pass (ref: Hannah Park's email 'Weekly Product Sync moved' (Mar 10), about the Weekly Product Sync on Sunday Mar 15 at 16:00 UTC | cand: Here are the emails related to upcoming meetings:
1. Hannah Park, subject: Weekly Product Sync moved, Tue 2026-03-10 18:00 UTC, Weekly Product Sync [gmail:ff9c102bbfa27a06]
2. Hannah Park, subject: Weekly Product Sync moved, Sun 2026-03-15 16:00 UTC, Weekly Product Sync [gmail:ff9c102bbfa27a06]
3. Priya Nair, subject: Pushing Weekly Product Sync by a week, Sun 2026-03-15 14:00 UTC, Weekly Product Sync [calendar:2ded3454537257a5518fa9905e])
