# Eval results (18 questions)

model `llama3.2:latest`, judge `llama3.2:latest`

```
accuracy 78% | citation recall 71% precision 63% | forbidden cites 0 | ungrounded sentences 10
latency p50 0.6s max 1.5s (0 over 5s) | projected hosted cost $0.0011/question, actual $0 (local)
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 0.5 |
| q02 | decision_reversal | NO | 1.00 | 1.00 | 0 | 0.7 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 1.0 |
| q04 | duplicate_conflict | yes | 1.00 | 1.00 | 0 | 0.6 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.2 |
| q06 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 0.6 |
| q07 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 0.4 |
| q08 | history | yes | 1.00 | 0.33 | 0 | 0.9 |
| q09 | identity | yes | 1.00 | 1.00 | 0 | 0.6 |
| q10 | tasks | NO | 0.00 | 0.00 | 0 | 0.4 |
| q11 | shared_inbox | yes | 1.00 | 0.33 | 0 | 0.4 |
| q12 | unanswerable | yes | 1.00 | 1.00 | 0 | 0.4 |
| q13 | decisions | yes | 0.33 | 0.67 | 0 | 0.9 |
| q14 | meeting_prep | yes | 0.00 | 0.00 | 0 | 0.8 |
| q15 | stale_record | NO | 0.00 | 0.00 | 0 | 0.6 |
| q16 | daily_priorities | NO | 0.50 | 0.50 | 0 | 0.7 |
| q17 | followups | yes | 0.00 | 0.00 | 0 | 1.5 |
| q18 | meeting_prep | yes | 1.00 | 0.50 | 0 | 1.4 |

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
judge: pass (ref: March 22 | cand: Mar 22. This decision replaced the previous ship date of Mar 20, which was corrected from the original plan of Mar 20.)

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.
judge: pass (correctly abstained)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> The Weekly Product Sync was initially scheduled for Friday March 13, but it was later moved to Sunday March 15 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The original event was cancelled [calendar:7d2712a17add94eb1a82e92b23], but it was rescheduled [calendar:2ded3454537257a5518fa9905e].
judge: pass (ref: Weekly Product Sync on Friday Mar 13 was cancelled | cand: The Weekly Product Sync was initially scheduled for Friday March 13, but it was later moved to Sunday March 15 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The original event was cancelled [calendar:7d2712a17add94eb1a82e92b23], but it was rescheduled [calendar:2ded3454537257a5518fa9905e].)

**q07** Was the Daily Standup on March 13 cancelled?
> The Daily Standup on March 13 was cancelled due to offsite [calendar:4554e5cfc14461dcdd7a91842f].
judge: pass (ref: Daily Standup on March 13 was cancelled | cand: The Daily Standup on March 13 was cancelled due to offsite [calendar:4554e5cfc14461dcdd7a91842f])

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is: ship v2 API with OAuth only [gmail:ceece9b31878fe40][slack:C02PROD:1772640000.222201]. The original decision on March 6 was: ship v2 API with OAuth only [gmail:403df41545d6ec2d], made by Priya Nair. Priya Nair changed the decision to ship v2 API with OAuth only, replacing the original decision [gmail:403df41545d6ec2d].
judge: pass (ref: Priya Nair decided on March 6 to ship the v2 API with OAuth only | cand: The current decision is: ship v2 API with OAuth only [gmail:ceece9b31878fe40][slack:C02PROD:1772640000.222201]. The original decision on March 6 was: ship v2 API with OAuth only [gmail:403df41545d6ec2d], made by Priya Nair. Priya Nair changed the decision to ship v2 API with OAuth only, replacing the original decision [gmail:403df41545d6ec2d].)

**q09** What did Rebecca Liu say about the Globex addendum?
> Rebecca Liu said the Globex addendum was signed, and the v2 API authentication ACME-142 was closed [slack:C01ENG:1773522000.994933].
judge: pass (ref: Globex signed the OAuth-only addendum, v2 API reverts to OAuth only, ACME-142 updated | cand: Globex signed the OAuth-only addendum, and the v2 API authentication ACME-142 was closed)

**q10** Which Linear issues owned by me are blocked?
> I can't find that in the available data.
judge: FAIL (abstained on an answerable question)

**q11** Who is out of office this week and who has context on billing?
> Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya Nair has context on billing [gmail:c1abbf680fedaacd][slack:C03GEN:1773097200.749458].
judge: pass (ref: Daniel Kim was out of office Mar 10 to 14, and said Priya Nair has context on billing | cand: Daniel Kim is out of office from March 10-14 [gmail:469b8c07901db7d8]. Priya Nair has context on billing [gmail:c1abbf680fedaacd][slack:C03GEN:1773097200.749458])

**q12** Summarize investor-related activity this week.
> I can't find that in the available data.
judge: pass (correctly abstained)

**q13** What decisions were made recently?
> The current decision is to ship v2 API with OAuth only [linear:ACME-142@20260314T2200]. This replaced the previous decision to ship v2 API with OAuth + API keys, which was made by Alex Chen on Sun 2026-03-08 19:00 UTC [gmail:10db167a8a1afba8]. The decision was also made by Rebecca Liu on Sat 2026-03-14 21:00 UTC [slack:C01ENG:1773522000.994933].
judge: pass (ref: v2 API auth decision went back to OAuth only on Mar 14 | cand: The current decision is to ship v2 API with OAuth only [linear:ACME-142@20260314T2200].)

**q14** What should I know before my next meeting?
> Before your next meeting, you should know that the Weekly Product Sync meeting has been rescheduled from Friday, March 13 to Sunday, March 15 at 16:00 UTC. The meeting was originally cancelled on Friday, March 13 due to a Globex call, but was rescheduled to accommodate the new event.
judge: pass (ref: Weekly Product Sync meeting rescheduled from Friday Mar 13 | cand: Weekly Product Sync meeting has been rescheduled from Friday, March 13 to Sunday, March 15 at 16:00 UTC)

**q15** Is the Linear issue ACME-231 up to date?
> The Linear issue ACME-231 is CURRENT. [linear:ACME-142@20260314T2200] It replaced the outdated "STALE" version, which had a ship date of Mar 20, and was updated by Sofia Reyes.
judge: FAIL (ref: ACME-231 still says freeze Mar 10 and ship Mar 20 | cand: The Linear issue ACME-231 is CURRENT. [linear:ACME-142@20260314T2200] It replaced the outdated )

**q16** What should I focus on today?
> The Weekly Product Sync meeting is rescheduled from Friday to Sunday at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The original meeting on Friday was cancelled and rescheduled [calendar:7d2712a17add94eb1a82e92b23]. The meeting attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e]
judge: FAIL (ref: Weekly Product Sync at 16:00 UTC today, update Linear issue ACME-231 ship date to Mar 22 | cand: Weekly Product Sync meeting is rescheduled from Friday to Sunday at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The original meeting on Friday was cancelled and rescheduled [calendar:7d2712a17add94eb1a82e92b23]. The meeting attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park. [calendar:2ded3454537257a5518fa9905e])

**q17** What follow-ups am I missing?
> 1. Daniel Kim is missing a follow-up for email #1 [gmail:39674cd28725364b]. 2. Alex Chen is missing a follow-up for email #2 [gmail:43bdab2891037118]. 3. Alex C. Morgan is missing a follow-up for email #3 [gmail:0ff144b62ef6b209]. 4. Omar Haddad is missing a follow-up for email #5 [gmail:004084f2ba0c1170]. 5. Priya Nair is missing a follow-up for email #7 [gmail:319d43c65089e537]. 6. Alex C. Morgan is missing a follow-up for email #8 [gmail:6dd18f0c91487b54]. 7. Sofia Reyes is missing a follow-up for email #9 [gmail:21735599e4ef7acc].
judge: pass (ref: None are outstanding. Rebecca Liu asked you to update ACME-142, which is already Done, and Hannah Park asked you to decline the old Weekly Product Sync invite, which is already cancelled. | cand: 1. Daniel Kim is missing a follow-up for email #1 [gmail:39674cd28725364b]. 2. Alex Chen is missing a follow-up for email #2 [gmail:43bdab2891037118]. 3. Alex C. Morgan is missing a follow-up for email #3 [gmail:0ff144b62ef6b209]. 4. Omar Haddad is missing a follow-up for email #5 [gmail:004084f2ba0c1170]. 5. Priya Nair is missing a follow-up for email #7 [gmail:319d43c65089e537]. 6. Alex C. Morgan is missing a follow-up for email #8 [gmail:6dd18f0c91487b54]. 7. Sofia Reyes is missing a follow-up for email #9 [gmail:21735599e4ef7acc].)

**q18** Which emails relate to upcoming meetings?
> [gmail:ff9c102bbfa27a06] email from Hannah Park, Tue 2026-03-10 18:00 UTC, subject: Weekly Product Sync moved
Weekly Product Sync moved from Fri Mar 13 to Sun Mar 15 16:00 UTC. Attendees: Alex Chen, Priya Nair, Marcus Webb, Hannah Park. [calendar:2ded3454537257a5518fa9905e] [calendar:2ded3454537257a5518fa9905e] calendar event 'Weekly Product Sync', Sun 2026-03-15 16:00 UTC to Sun 2026-03-15 17:00 UTC, attendees: Alex Chen, Priya Nair, Marcus Webb, Hannah Park, organizer: Hannah Park (CONFIRMED)
judge: pass (ref: Weekly Product Sync on Sunday Mar 15 at 16:00 UTC | cand: [gmail:ff9c102bbfa27a06] email from Hannah Park, Tue 2026-03-10 18:00 UTC, subject: Weekly Product Sync moved)
