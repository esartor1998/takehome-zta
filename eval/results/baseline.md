# Eval results (14 questions)

model `llama3.2:latest`, judge `llama3.2:latest`

```
accuracy 64% | citation recall 67% precision 67% | forbidden cites 0 | ungrounded sentences 14
latency p50 0.7s max 1.5s (0 over 5s) | projected hosted cost $0.0011/question, actual $0 (local)
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 0.6 |
| q02 | decision_reversal | NO | 1.00 | 1.00 | 0 | 0.7 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 0.9 |
| q04 | duplicate_conflict | NO | 1.00 | 1.00 | 0 | 0.7 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.4 |
| q06 | cancelled_meeting | yes | 0.50 | 0.50 | 0 | 0.6 |
| q07 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 0.4 |
| q08 | history | yes | 1.00 | 0.25 | 0 | 1.0 |
| q09 | identity | NO | 0.00 | 0.00 | 0 | 0.8 |
| q10 | tasks | NO | 0.00 | 0.00 | 0 | 1.5 |
| q11 | shared_inbox | NO | 0.00 | 0.00 | 0 | 0.4 |
| q12 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.4 |
| q13 | decisions | yes | 0.33 | 0.67 | 0 | 1.1 |
| q14 | meeting_prep | yes | 0.50 | 1.00 | 0 | 1.3 |

## Answers

**q01** What did Daniel Kim say about the billing migration?
> Daniel Kim asked to push the billing migration a week [gmail:c1abbf680fedaacd].
judge: pass (ref: Daniel Kim asked Priya to push the billing migration back by a week | cand: Daniel Kim asked to push the billing migration a week [gmail:c1abbf680fedaacd])

**q02** What is the current authentication decision for the v2 API?
> The current authentication decision for the v2 API is: OAuth + API keys. [linear:ACME-142@20260314T2200] This replaced the previous decision of "ship v2 API with OAuth only" which was changed by Alex Chen. [linear:ACME-142@20260314T2200]
judge: FAIL (ref: OAuth only, then OAuth + API keys | cand: OAuth + API keys)

**q03** What time is the Weekly Product Sync today?
> The Weekly Product Sync is today at 16:00 UTC. [calendar:2ded3454537257a5518fa9905e] The meeting title is 'Weekly Product Sync', its time is 16:00 UTC, attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e] The meeting was rescheduled from its original time on Friday, March 13, 10:00-11:00 UTC, which was cancelled.
judge: pass (ref: Weekly Product Sync today 16:00 UTC | cand: The Weekly Product Sync is today at 16:00 UTC. [calendar:2ded3454537257a5518fa9905e] The meeting title is 'Weekly Product Sync', its time is 16:00 UTC, attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e] The meeting was rescheduled from its original time on Friday, March 13, 10:00-11:00 UTC, which was cancelled.)

**q04** What is the Q1 ship date?
> The current Q1 ship date is Mar 22. [gmail:69d12ca0960f4a7d] This decision replaced the previous ship date of Mar 20, which was corrected from the original plan of Mar 20. Sofia Reyes changed the ship date. [gmail:69d12ca0960f4a7d]
judge: FAIL (ref: March 20 | cand: Mar 22)

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.
judge: pass (correctly abstained)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> The Weekly Product Sync on Friday March 13 was initially CANCELLED [calendar:7d2712a17add94eb1a82e92b23] due to a meeting with Alex Chen, Priya Nair, Marcus Webb, Hannah Park, and Sofia Reyes [calendar:4554e5cfc14461dcdd7a91842f].
judge: pass (ref: Weekly Product Sync on Friday Mar 13 was initially CANCELLED | cand: The Weekly Product Sync on Friday March 13 was initially CANCELLED [calendar:7d2712a17add94eb1a82e92b23] due to a meeting with Alex Chen, Priya Nair, Marcus Webb, Hannah Park, and Sofia Reyes [calendar:4554e5cfc14461dcdd7a91842f])

**q07** Was the Daily Standup on March 13 cancelled?
> The Daily Standup on March 13 was cancelled due to offsite [calendar:4554e5cfc14461dcdd7a91842f].
judge: pass (ref: Daily Standup on March 13 was cancelled | cand: The Daily Standup on March 13 was cancelled due to offsite [calendar:4554e5cfc14461dcdd7a91842f])

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is: ship v2 API with OAuth only [gmail:ceece9b31878fe40][slack:C02PROD:1772640000.222201]. The original decision on March 6 was: ship v2 API with OAuth only [gmail:403df41545d6ec2d], made by Priya Nair. Priya Nair changed the decision to ship v2 API with OAuth only, replacing the original decision [gmail:403df41545d6ec2d], and Alex Chen updated the Linear issue to reflect this change [gmail:10db167a8a1afba8].
judge: pass (ref: Priya Nair decided on March 6 to ship the v2 API with OAuth only | cand: The current decision is: ship v2 API with OAuth only [gmail:ceece9b31878fe40][slack:C02PROD:1772640000.222201]. The original decision on March 6 was: ship v2 API with OAuth only [gmail:403df41545d6ec2d], made by Priya Nair.)

**q09** What did Rebecca Liu say about Globex?
> Rebecca Liu said Globex call was moved [slack:C01ENG:1772528400.200772][slack:C02PROD:1773057600.343529][slack:C01ENG:1772100000.278901]. She also mentioned Globex sync #160, #19, and #250 [gmail:a8b6be6230717ae2][gmail:d69f5f805cec364c][gmail:51b0025c92175c4d]. Additionally, she mentioned Globex renewal is still pending legal review [gmail:ab8aaf5585d14de2].
judge: FAIL (ref: Globex signed the OAuth-only addendum, and asked for ACME-142 to be updated | cand: Globex call was moved to Slack, and mentioned Globex sync #160, #19, and #250, and Globex renewal is still pending legal review)

**q10** Which Linear issues owned by me are blocked?
> ACME-369, Billing webhook retry, Marcus Webb
ACME-310, Cache warming, Omar Haddad
ACME-380, Improve logging, Omar Haddad
ACME-331, Update dependency, Sofia Reyes
ACME-316, Billing webhook retry, Alex Chen
ACME-304, Fix flaky test, Sofia Reyes
ACME-325, Rate limit tuning, Marcus Webb
ACME-371, Fix flaky test, Daniel Kim
ACME-363, Rate limit tuning, Alex C. Morgan
ACME-311, Billing webhook retry, Omar Haddad [linear:ACME-311@20260225T0900]
judge: FAIL (ref: ACME-316 (Billing webhook retry), ACME-342 (Add pagination), ACME-349 (Rate limit tuning), ACME-352 (Update dependency) and ACME-365 (Rate limit tuning) | cand: ACME-369, Billing webhook retry, Marcus Webb)

**q11** Who was out of office last week and who has context on billing?
> I can't find that in the available data.
judge: FAIL (abstained on an answerable question)

**q12** Summarize investor-related activity this week.
> I can't find that in the available data.
judge: pass (correctly abstained)

**q13** What decisions were made recently?
> The current decision is to ship v2 API with OAuth only [linear:ACME-142@20260314T2200]. This replaced the previous decision to ship v2 API with OAuth + API keys, which was made by Alex Chen on Sun 2026-03-08 19:00 UTC [gmail:10db167a8a1afba8]. The decision was also made by Rebecca Liu on Sat 2026-03-14 21:00 UTC [slack:C01ENG:1773522000.994933].
judge: pass (ref: v2 API auth decision went back to OAuth only on Mar 14 | cand: The current decision is to ship v2 API with OAuth only [linear:ACME-142@20260314T2200].)

**q14** What should I know before my next meeting?
> Before your next meeting, you should know that the meeting title is 'Weekly Product Sync', it will be held on Sunday, 2026-03-15 16:00 UTC, and attendees include Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e] The meeting was rescheduled from its original time on Friday, 2026-03-13 10:00 UTC, which was cancelled due to a Globex call moved by Sofia Reyes on Saturday, 2026-03-07 07:00 UTC.
judge: pass (ref: Weekly Product Sync today at 16:00 UTC with Priya Nair, Marcus Webb and Hannah Park. It was rescheduled from Friday Mar 13 | cand: Weekly Product Sync, Sunday, 2026-03-15 16:00 UTC, Priya Nair, Marcus Webb, and Hannah Park. The meeting was rescheduled from its original time on Friday, 2026-03-13 10:00 UTC, which was cancelled due to a Globex call moved by Sofia Reyes on Saturday, 2026-03-07 07:00 UTC.)
