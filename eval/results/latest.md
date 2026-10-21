# Eval results (70 questions)

model `anthropic:claude-haiku-4-5-20251001`, judge `openai:gpt-6-luna`

```
accuracy 71% | citation recall 89% precision 55% | forbidden cites 0 | ungrounded sentences 20
latency p50 1.7s max 4.7s (0 over 5s) | cost $0.00140/question actual, $0.00140 at hosted rates
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | NO | 1.00 | 1.00 | 0 | 1.2 |
| q02 | decision_reversal | yes | 1.00 | 0.75 | 0 | 1.9 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 4.0 |
| q04 | duplicate_conflict | yes | 1.00 | 0.33 | 0 | 3.0 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 1.7 |
| q06 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 2.7 |
| q07 | cancelled_meeting | yes | 1.00 | 0.50 | 0 | 1.7 |
| q08 | history | yes | 1.00 | 0.33 | 0 | 1.8 |
| q09 | identity | NO | 1.00 | 1.00 | 0 | 1.1 |
| q10 | tasks | yes | 1.00 | 1.00 | 0 | 0.0 |
| q11 | shared_inbox | NO | 0.00 | 0.00 | 0 | 2.6 |
| q12 | topic_summary | NO | 0.67 | 0.50 | 0 | 2.1 |
| q13 | decisions | yes | 1.00 | 0.43 | 0 | 0.0 |
| q14 | meeting_prep | NO | 0.50 | 0.20 | 0 | 0.0 |
| q15 | stale_record | NO | 0.50 | 1.00 | 0 | 1.8 |
| q16 | daily_priorities | yes | 1.00 | 0.11 | 0 | 2.5 |
| q17 | followups | yes | 1.00 | 0.38 | 0 | 0.0 |
| q18 | meeting_prep | yes | 1.00 | 0.16 | 0 | 0.1 |
| v01 | vague_schedule | yes | 1.00 | 0.88 | 0 | 0.0 |
| v02 | vague_schedule | yes | 1.00 | 0.50 | 0 | 0.0 |
| v03 | vague_schedule | yes | 1.00 | 1.00 | 0 | 0.0 |
| v04 | vague_person | NO | 0.50 | 0.25 | 0 | 1.9 |
| v05 | vague_person | NO | 1.00 | 0.25 | 0 | 1.5 |
| v06 | vague_person | yes | 1.00 | 0.67 | 0 | 1.6 |
| v07 | vague_followups | yes | 1.00 | 0.38 | 0 | 0.1 |
| v08 | vague_followups | yes | 1.00 | 0.10 | 0 | 0.0 |
| v09 | vague_focus | yes | 1.00 | 0.11 | 0 | 2.5 |
| v10 | vague_catchup | yes | 1.00 | 0.12 | 0 | 0.0 |
| v11 | vague_tasks | yes | 1.00 | 0.21 | 0 | 0.0 |
| v12 | vague_topic | NO | 0.67 | 0.50 | 0 | 3.1 |
| v13 | vague_topic | yes | 1.00 | 0.50 | 0 | 2.1 |
| v14 | vague_topic | NO | 1.00 | 0.67 | 0 | 2.5 |
| v15 | vague_topic | yes | 1.00 | 0.33 | 0 | 4.7 |
| v16 | vague_topic | NO | 0.00 | 0.00 | 0 | 1.1 |
| v17 | vague_topic | NO | 0.50 | 0.33 | 0 | 1.4 |
| v18 | vague_person | yes | 1.00 | 0.50 | 0 | 2.3 |
| v19 | vague_stale | NO | 1.00 | 1.00 | 0 | 1.7 |
| v20 | vague_schedule | yes | 1.00 | 0.50 | 0 | 0.0 |
| v21 | vague_person | NO | 1.00 | 0.33 | 0 | 1.5 |
| v22 | unanswerable | yes | 1.00 | 1.00 | 0 | 1.4 |
| v23 | unanswerable | yes | 1.00 | 1.00 | 0 | 3.4 |
| s01 | spec_company_week | yes | 1.00 | 0.14 | 0 | 0.1 |
| s02 | spec_customer_issues | yes | 0.50 | 0.50 | 0 | 0.1 |
| s03 | spec_blocked | yes | 1.00 | 0.21 | 0 | 0.0 |
| t01 | typo | yes | 1.00 | 0.50 | 0 | 0.0 |
| t02 | typo | yes | 1.00 | 0.38 | 0 | 0.1 |
| t03 | typo | yes | 1.00 | 0.67 | 0 | 1.6 |
| t04 | typo | NO | 0.50 | 0.20 | 0 | 1.7 |
| t05 | typo | yes | 0.00 | 0.00 | 0 | 2.6 |
| t06 | typo | NO | 1.00 | 0.33 | 0 | 3.3 |
| t07 | typo | yes | 1.00 | 1.00 | 0 | 3.1 |
| t08 | typo | yes | 1.00 | 0.21 | 0 | 0.0 |
| n01 | renewal | NO | 1.00 | 0.50 | 0 | 2.2 |
| n02 | renewal_stale | yes | 1.00 | 1.00 | 0 | 2.8 |
| n03 | renewal_decision | yes | 0.00 | 0.00 | 0 | 3.7 |
| n04 | promise_informal | yes | 1.00 | 1.00 | 0 | 0.1 |
| n05 | fact_slash_date | yes | 1.00 | 0.33 | 0 | 3.1 |
| n06 | inline_reply | NO | 1.00 | 1.00 | 0 | 1.0 |
| n08 | customer_topic | NO | 1.00 | 0.67 | 0 | 0.0 |
| h01 | multi_hop | yes | 1.00 | 0.30 | 0 | 0.0 |
| h02 | overdue | yes | 1.00 | 1.00 | 0 | 0.1 |
| w01 | soft_change | NO | 1.00 | 1.00 | 0 | 2.9 |
| w02 | soft_change | yes | 1.00 | 1.00 | 0 | 3.0 |
| w03 | soft_change | yes | 1.00 | 1.00 | 0 | 3.0 |
| w04 | soft_change | yes | 1.00 | 1.00 | 0 | 1.7 |
| w05 | soft_change | yes | 1.00 | 1.00 | 0 | 1.7 |
| w06 | still_current | yes | 1.00 | 0.50 | 0 | 1.8 |
| w07 | still_current | yes | 1.00 | 0.50 | 0 | 2.0 |
| k01 | nickname | yes | 1.00 | 0.33 | 0 | 1.7 |
| k02 | nickname | yes | 1.00 | 0.29 | 0 | 2.6 |

## Answers

**q01** What did Daniel Kim say about the billing migration?
> Daniel Kim asked to push the billing migration by a week because he was on call [gmail:c1abbf680fedaacd] [slack:C01ENG:1773248400.000100]. He also reported that the billing migration was blocked on his side [slack:C01ENG:1773248400.000100].
judge: FAIL (ref: Daniel asked Priya to delay the billing migration by a week, emailed from his personal address while on call, and said it was blocked on his side. | cand: Daniel asked to push the migration by a week because he was on call and said it was blocked on his side; it omits the personal email address.)

**q02** What is the current authentication decision for the v2 API?
> The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933] [linear:ACME-142@20260314T2200]. This reverts the previous plan of OAuth + API keys that Marcus Webb set on Mar 8 [slack:C01ENG:1772992800.207664]. Rebecca Liu made this change on Mar 14 after Globex signed the OAuth-only addendum [gmail:ceece9b31878fe40]. The decision is final and logged in ACME-142, which is now closed [linear:ACME-142@20260314T2200] [slack:C01ENG:1773522000.994933]. Nothing remains open on this decision.
judge: pass (ref: Current v2 API authentication is OAuth only, reverted Mar 14 after Globex signed the addendum. | cand: Current v2 API authentication is OAuth only, reverted Mar 14 after Globex signed the addendum.)

**q03** What time is the Weekly Product Sync today?
> The Weekly Product Sync is today at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. It was rescheduled from Friday March 13 to today. Alex Chen, Priya Nair, Marcus Webb, and Hannah Park attend [calendar:2ded3454537257a5518fa9905e]. Hannah Park organized the move and asked attendees to decline the old Friday invite [gmail:ff9c102bbfa27a06]. The original Friday slot was cancelled.
judge: pass (ref: Weekly Product Sync is today, Sunday Mar 15, at 16:00 UTC; Friday Mar 13 event is cancelled. | cand: It is today at 16:00 UTC, moved from Friday March 13, and the original Friday slot was cancelled.)

**q04** What is the Q1 ship date?
> The current Q1 ship date is March 22 [slack:C02PROD:1772640000.222201] [slack:C02PROD:1772640000.222201]. Sofia Reyes corrected this from the original March 20 plan on March 4 [slack:C02PROD:1772640000.222201] [slack:C02PROD:1772640000.222201]. Several records still show the outdated March 20 date: linear issue ACME-231 , notion page 'Roadmap (Q1)' , and the CRM deal record  are all marked STALE and contain superseded information [linear:ACME-231@20260304T1800] [notion:4324f4a965bc64d11787c2369776502e]. Anyone referencing these older records should use the March 22 date instead.
judge: pass (ref: Q1 ship date is March 22, corrected from March 20; Linear issue ACME-231 is outdated. | cand: Q1 ship date is March 22, corrected from March 20; ACME-231 and other records are outdated.)

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.

The context shows the v2 API authentication approach changed multiple times [linear:ACME-142@20260314T2200]. Globex signed an OAuth-only addendum on Friday , so the final decision is OAuth only [gmail:ceece9b31878fe40] [linear:ACME-142@20260314T2200]. However, the partner API v2 is slipping to Q3 because design partners cannot test before then [slack:C01ENG:1773338400.739782]. There is no information about revenue impact in the available data.
judge: pass (ref: No revenue or financial figures are available. | cand: The candidate can't find revenue impact in the available data.)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> Yes, the Weekly Product Sync on Friday March 13 was cancelled [calendar:7d2712a17add94eb1a82e92b23]. The event was rescheduled to Sunday March 15 at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The calendar note states: "Rescheduled from Fri Mar 13" [calendar:2ded3454537257a5518fa9905e]. Attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, with Hannah Park as organizer [calendar:2ded3454537257a5518fa9905e]. The new meeting is confirmed.
judge: pass (ref: The Friday March 13 event was cancelled because the meeting moved to Sunday March 15 at 16:00 UTC. | cand: The Friday March 13 sync was cancelled and rescheduled to Sunday March 15 at 16:00 UTC.)

**q07** Was the Daily Standup on March 13 cancelled?
> Yes, the Daily Standup on March 13 was cancelled [calendar:4554e5cfc14461dcdd7a91842f]. It was scheduled for Fri 2026-03-13 14:00 UTC to 14:15 UTC with attendees Alex Chen, Priya Nair, Marcus Webb, Sofia Reyes, and Daniel Kim [calendar:4554e5cfc14461dcdd7a91842f]. The calendar note states: "Cancelled due to offsite" [calendar:4554e5cfc14461dcdd7a91842f]. There is a replacement Standup meeting today (Sun 2026-03-15) at 09:30 UTC with the same attendees [calendar:c5457a3e77f0e609f8407d2ecf].
judge: pass (ref: The March 13 Daily Standup was cancelled because of the offsite. | cand: It was cancelled, and the calendar note says it was cancelled due to the offsite.)

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933] [linear:ACME-142@20260314T2200]. Priya Nair made the original decision on March 6 to ship with OAuth only [slack:C01ENG:1772812800.963148] [gmail:403df41545d6ec2d]. This was then reversed to OAuth + API keys by Marcus Webb on March 8 , but Rebecca Liu reverted it back to OAuth-only on March 14 after Globex signed the OAuth-only addendum [slack:C01ENG:1772992800.207664] [slack:C01ENG:1773522000.994933] [gmail:ceece9b31878fe40]. Nothing is marked STALE or CANCELLED in the current state.
judge: pass (ref: Priya Nair decided on March 6 to ship the v2 API with OAuth only | cand: Priya Nair made the original decision on March 6 to ship with OAuth only)

**q09** What did Rebecca Liu say about the Globex addendum?
> Rebecca Liu said Globex signed the OAuth-only addendum on Friday, and she is reverting to OAuth-only and will update ACME-142 [gmail:ceece9b31878fe40].
judge: FAIL (ref: Globex signed the OAuth-only addendum; Rebecca said the v2 API reverts to OAuth only, asked for ACME-142 to be updated, and said in Slack it was closed. | cand: Globex signed the OAuth-only addendum; Rebecca said she is reverting to OAuth only and will update ACME-142.)

**q10** Which Linear issues owned by me are blocked?
> 5 blocked issues, 5 yours:
- ACME-365 Rate limit tuning (yours, urgent) [linear:ACME-365@20260222T0500]
- ACME-342 Add pagination (yours, high) [linear:ACME-342@20260225T0900]
- ACME-349 Rate limit tuning (yours, high) [linear:ACME-349@20260307T0900]
- ACME-352 Update dependency (yours, high) [linear:ACME-352@20260225T1100]
- ACME-316 Billing webhook retry (yours, no priority) [linear:ACME-316@20260219T1200]
judge: pass (ref: Blocked issues owned by the user: ACME-316, ACME-342, ACME-349, ACME-352, and ACME-365. | cand: The same five issues are blocked and owned by the user.)

**q11** Who is out of office this week and who has context on billing?
> Daniel Kim is out of office this week through March 14. Priya Nair has context on billing [slack:C03GEN:1773068400.685084]. Daniel asked to push the billing migration by a week , and the billing cutover date was moved to March 31 (from March 24), with Omar and Daniel's agreement [gmail:c1abbf680fedaacd] [gmail:bfda57e5a3e21af0]. Nothing is marked STALE or CANCELLED in the available data.
judge: FAIL (ref: Daniel Kim was out of office March 10–14; Priya Nair has billing context. | cand: Daniel is out this week through March 14; Priya has billing context.)

**q12** Summarize investor-related activity this week.
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR by Monday for Tuesday's partner meeting term sheet discussion [gmail:75d73520ec4c68f3].

**Priya Nair** (Fri 2026-03-13): Edited investor update draft to say "roughly $1.8M," remove one slide, and add cohort chart [gmail:6c967d680a755c1f].

**Alex Chen** (Thu 2026-03-12): Sent investor update draft with ARR, churn, and asks sections [gmail:ec270de8c9f8fc39].

**Caroline Ades** (Thu 2026-03-12): Asked for data room access update [gmail:012ce504e5a045e9].
judge: FAIL (ref: Jordan requested cohort ARR before the Mar 17 meeting; Caroline asked about data room access; Priya said Northwind cannot close before May 15. | cand: Jordan requested cohort ARR, and Caroline asked for a data room access update; it omits Priya’s May 15 closing constraint.)

**q13** What decisions were made recently?
> - Globex SSO redirect loop: current plan is 'reopening ACME-431', replacing 'Recurred for Globex users on Okta. Needs a second fix.'. Records already reflect this, no action needed [slack:C04INC:1773339300.924615]
- Audit log export: current plan is 'slipped to april'. Records already reflect this, no action needed [slack:C01ENG:1773334800.910984]
- weekly product sync meeting date: current plan is 'Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC.'. Records already reflect this, no action needed [gmail:ff9c102bbfa27a06]
- billing cutover date: current plan is 'Mar 31'. Records already reflect this, no action needed [gmail:bfda57e5a3e21af0]
- v2 API authentication: current plan is 'Reverting to OAuth-only', replacing 'Confirmed: OAuth + API keys.'. Records already reflect this, no action needed [slack:C01ENG:1773522000.994933]
- Q1 roadmap dates: current plan is 'ship Mar 22'. Records already reflect this, no action needed [slack:C02PROD:1772640000.222201]
- fundraising close date: current plan is 'Jordan says they cannot close before May 15 because of the partner calendar.', replacing 'Attendees: Marcus, Priya, Omar. Discussed whether the SDK release might slip. No decision yet, revisit next week.'. Records already reflect this, no action needed [slack:C07FUND:1773421200.357681]
- Update pricing page to $59/seat for new customers: current plan is 'Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.', replacing 'Decision: new customers pay $59 per seat, existing customers stay at $49 (grandfathered).'. Records already reflect this, no action needed [gmail:7d0d75121cdeaac6]
- cloudhost renewal: current plan is 'fyi we're holding off on the cloudhost renewal until their new pricing is out.'. Records already reflect this, no action needed [gmail:2dbbf43ced346885]
- customer webinar plan: current plan is 'heads up, the speaker has a conflict so i moved the webinar to next friday.'. Records already reflect this, no action needed [gmail:32a980202cbd8f93]
- Partner API v2: current plan is 'partner api v2 is slipping to q3, the design partners cannot test before then'. Records already reflect this, no action needed [slack:C01ENG:1773338400.739782]
- mobile beta plan: current plan is 'pushed back the beta timeline for now, design is still waiting on the new onboarding flow'. Records already reflect this, no action needed [slack:C02PROD:1773331200.887947]
- Initech renewal paperwork: current plan is 'initech renewal is 2 yr at 15% now, legal redlining'. Records already reflect this, no action needed [slack:C03GEN:1773414000.655032]
- hiring - senior backend: current plan is 'Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena'. Records already reflect this, no action needed [gmail:e98c5b9d26b114a1]
judge: pass (ref: Decisions: OAuth-only auth, Q1 ship Mar 22, pricing $59/$49, billing Mar 31, seed close May 15, Taylor offer canceled, Initech renewal 2 years at 15%. | cand: Lists all these decisions, including OAuth-only, Mar 22 ship, $59/$49 pricing, Mar 31 billing, May 15 fundraising, Taylor’s offer, and Initech’s 2-year 15% renewal.)

**q14** What should I know before my next meeting?
> Meeting: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13)
Before it:
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
judge: FAIL (ref: Weekly Product Sync is today at 16:00 UTC with Priya Nair, Marcus Webb, and Hannah Park; rescheduled from Friday Mar 13. | cand: Weekly Product Sync is 16:00–17:00 UTC with the same attendees, rescheduled from Friday Mar 13; it omits that it is today.)

**q15** Is the Linear issue ACME-231 up to date?
> No, ACME-231 is not up to date [linear:ACME-231@20260304T1800]. It is marked STALE, meaning it contains outdated information that was corrected later [linear:ACME-231@20260304T1800]. The issue states a freeze date of March 10 and ship date of March 20, but these values are no longer current [linear:ACME-231@20260304T1800]. You should not rely on these dates. The issue is owned by Sofia Reyes and remains reopened, so you may need to contact her for the corrected Q1 roadmap dates [linear:ACME-231@20260304T1800].
judge: FAIL (ref: ACME-231 is outdated: it says ship Mar 20, corrected to Mar 22. | cand: ACME-231 is stale and still says ship Mar 20, but gives no corrected ship date.)

**q16** What should I focus on today?
> 1. Confirm a fix ships before Mar 20 and get someone on a call thurs with Daniel Foster (Globex) before the 17:30-18:00 UTC check-in today about SSO and the Mar 23 rollout, because Globex SSO redirect loop is Reopened and Globex integration is Blocked. [calendar:bbeda5b103cb82876dd4651501]
2. Send the summary to Sam Okafor (Hooli) immediately, because it was due 2026-03-12 and is still open. [gmail:c81c70603acf1120]
3. Deliver the cohort metrics to Jordan Pryce (Northwind Ventures) immediately, because it was due 2026-03-09 and is still open. [gmail:ccd9c787ded3995d]

Also open (38):
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]
- Meeting today: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- Blocked, owned by you: ACME-365 Rate limit tuning [linear:ACME-365@20260222T0500]
- Blocked, owned by you: ACME-349 Rate limit tuning [linear:ACME-349@20260307T0900]
- Blocked, owned by you: ACME-352 Update dependency [linear:ACME-352@20260225T1100]
- Blocked, owned by you: ACME-342 Add pagination [linear:ACME-342@20260225T0900]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
- Blocked, owned by you: ACME-316 Billing webhook retry [linear:ACME-316@20260219T1200]
- Meeting today: 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
- 17 records still state an old plan and need updating: Seed extension plan [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]; Partner API v2 [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]; Audit log export [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]; Update pricing page to $49/seat [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]; Customer webinar plan [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]; Northwind Ventures - seed extension [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]; CloudHost renewal [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]; Pricing v3 [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]; Initech renewal paperwork [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]; Initech - renewal [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]; Initech renewal terms [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]; Mobile beta plan [notion:a005e60800e96d471e9ea49de3f49c3e][slack:C02PROD:1773331200.887947]; Hiring - Senior Backend [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]; Billing migration plan [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]; Roadmap (Q1) [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]; Blue Harbor Capital - seed extension [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]; Q1 roadmap dates [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
judge: pass (ref: Prioritize Globex’s 17:30 UTC SSO-fix confirmation, Jordan Pryce’s cohort ARR before Tuesday’s partner meeting, and updating stale records. | cand: Prioritize confirming the Globex fix before Mar 20, delivering Jordan’s cohort metrics before Tuesday, and updating records that state old plans.)

**q17** What follow-ups am I missing?
> Waiting on you:
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]

Already handled:
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]
judge: pass (ref: Missing follow-ups include all listed requests and open promises, including Rebecca’s redline/docs migration and Daniel’s Thursday call. | cand: Lists every referenced follow-up and open promise.)

**q18** Which emails relate to upcoming meetings?
> - Email 'Weekly Product Sync moved' from Hannah Park (2026-03-10) relates to Weekly Product Sync on 2026-03-15 [gmail:ff9c102bbfa27a06][calendar:2ded3454537257a5518fa9905e]
- Email 'Re: SSO login loops for our users' from Daniel Foster (Globex) (2026-03-13) relates to Globex check-in on 2026-03-15 [gmail:49670ab720e678cb][calendar:bbeda5b103cb82876dd4651501]
- Email 'Re: SSO login loops for our users' from Daniel Foster (Globex) (2026-03-13) relates to Globex check-in on 2026-03-15 [gmail:4dd6e4165f18c195][calendar:bbeda5b103cb82876dd4651501]
- Email 'Re: SSO login loops for our users' from Daniel Foster (Globex) (2026-03-12) relates to Globex check-in on 2026-03-15 [gmail:bee95ff7ca51c987][calendar:bbeda5b103cb82876dd4651501]
- Email 'Re: SSO login loops for our users' from Daniel Foster (Globex) (2026-03-10) relates to Globex check-in on 2026-03-15 [gmail:ef094c02c13dd962][calendar:bbeda5b103cb82876dd4651501]
- Email 'Re: SSO login loops for our users' from Marcus Webb (2026-03-05) relates to Globex check-in on 2026-03-15 [gmail:23185a980c205f87][calendar:bbeda5b103cb82876dd4651501]
- Email 'SSO login loops for our users' from Daniel Foster (Globex) (2026-03-03) relates to Globex check-in on 2026-03-15 [gmail:c15f3037c23a7d15][calendar:bbeda5b103cb82876dd4651501]
- Email 'Sprint planning #196' from Rebecca Liu (2026-03-15) relates to Sprint Planning on 2026-03-16 [gmail:9d584224288c2000][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #249' from Priya Nair (2026-03-13) relates to Sprint Planning on 2026-03-16 [gmail:4be737c7e6b3d180][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #264' from Marcus Webb (2026-03-10) relates to Sprint Planning on 2026-03-16 [gmail:369c095708245d78][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #9' from Priya Nair (2026-03-10) relates to Sprint Planning on 2026-03-16 [gmail:73edccf59d0316d3][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #131' from Marcus Webb (2026-03-09) relates to Sprint Planning on 2026-03-16 [gmail:2a7a1f275c0428bf][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #286' from Sofia Reyes (2026-03-07) relates to Sprint Planning on 2026-03-16 [gmail:f7009a97932fc954][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #69' from Alex C. Morgan (2026-03-07) relates to Sprint Planning on 2026-03-16 [gmail:3a79d646dcb38a37][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #162' from Alex C. Morgan (2026-03-07) relates to Sprint Planning on 2026-03-16 [gmail:18f5f39909df4aaa][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #173' from Hannah Park (2026-03-05) relates to Sprint Planning on 2026-03-16 [gmail:18e79b16543b3131][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #215' from Sofia Reyes (2026-03-03) relates to Sprint Planning on 2026-03-16 [gmail:0c693340671f7de7][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #104' from Sofia Reyes (2026-03-02) relates to Sprint Planning on 2026-03-16 [gmail:f590c69ef0b5a71f][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #81' from Sofia Reyes (2026-03-02) relates to Sprint Planning on 2026-03-16 [gmail:a6496f2dab9cf45e][calendar:5c545e66becd5507a0709683f4]
- Email 'Sprint planning #261' from Daniel Kim (2026-03-02) relates to Sprint Planning on 2026-03-16 [gmail:de5ed4f0d537fd44][calendar:5c545e66becd5507a0709683f4]
- Email 'Re: Taylor Brooks - offer' from Priya Nair (2026-03-10) relates to sync w/ priya re raise on 2026-03-16 [gmail:07c7430cafafc2e3][calendar:fac33a36f31a1bd1329721d22d]
- Email 'Re: Acme Robotics seed extension - intro' from Jordan Pryce (Northwind Ventures) (2026-03-13) relates to Northwind Ventures partner update on 2026-03-17 [gmail:75d73520ec4c68f3][calendar:e252dcf3e06e42f839b9cd47db]
- Email 'Re: Northwind term sheet template' from Priya Nair (2026-03-09) relates to Northwind Ventures partner update on 2026-03-17 [gmail:aa8fb20768b8a5b2][calendar:e252dcf3e06e42f839b9cd47db]
- Email 'Fwd: Northwind term sheet template' from Priya Nair (2026-03-09) relates to Northwind Ventures partner update on 2026-03-17 [gmail:e79b33505f571a3b][calendar:e252dcf3e06e42f839b9cd47db]
- Email 'Re: Acme Robotics seed extension - intro' from Alex Chen (2026-03-06) relates to Northwind Ventures partner update on 2026-03-17 [gmail:ccd9c787ded3995d][calendar:e252dcf3e06e42f839b9cd47db]
- Email 'Re: Acme Robotics seed extension - intro' from Jordan Pryce (Northwind Ventures) (2026-03-05) relates to Northwind Ventures partner update on 2026-03-17 [gmail:6dff2b861992469a][calendar:e252dcf3e06e42f839b9cd47db]
- Email 'Acme Robotics seed extension - intro' from Alex Chen (2026-03-02) relates to Northwind Ventures partner update on 2026-03-17 [gmail:166efe0e6a6aa48a][calendar:e252dcf3e06e42f839b9cd47db]
judge: pass (ref: Upcoming-meeting emails cover Hannah’s Weekly Product Sync, Daniel’s Globex SSO thread, Jordan Pryce’s Northwind update, and Sprint planning. | cand: Lists those email groups and meeting dates, plus additional Northwind-related and unrelated email matches.)

**v01** what's on today
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today includes offsite travel, completed morning meetings, a cancelled 15:00 1:1, a 16:00 sync, a 17:30 Globex check-in, and tentative 19:00 board prep. | cand: The candidate lists all of those events with matching times and statuses.)

**v02** what do i have on the calendar today?
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today includes all-day offsite travel; Standup at 09:30; investor prep at 11:00; cancelled 15:00 1:1; sync at 16:00 UTC; Globex check-in at 17:30 UTC; tentative board prep at 19:00. | cand: Lists all these events with matching times and statuses; the Globex check-in is also given as 10:30 Los Angeles time.)

**v03** tomorrow?
> Tomorrow (Monday Mar 16):
- Mon Mar 16 14:00-15:00 UTC Sprint Planning with Daniel Kim (you have not accepted) [calendar:5c545e66becd5507a0709683f4]
- Mon Mar 16 15:00-15:30 UTC sync w/ priya re raise with Priya Nair [calendar:fac33a36f31a1bd1329721d22d]
- Mon Mar 16 16:00-16:45 UTC Customer escalations review with Marcus Webb, Sofia Reyes (16:00 London time) [calendar:94d8a5fa7f930cba2bb0bba41f]
judge: pass (ref: Tomorrow, Monday Mar 16: 14:00 UTC Sprint Planning (not accepted), 15:00 UTC sync about raise, and 16:00 London Customer escalations review. | cand: Lists all three events at the matching times and notes Sprint Planning is not accepted.)

**v04** what is daniel saying
> **Daniel Kim:**
- Mon 2026-03-09: Out of office Mar 10-14; Priya has billing context [gmail:469b8c07901db7d8]
- Thu 2026-03-12: Data retention review timeline unchanged, still Mar 30 [slack:C01ENG:1773352800.648477]

**Daniel Foster (Globex):**
- Fri 2026-03-13 17:00: Added that Okta redirect fails on Safari only [gmail:49670ab720e678cb]
- Fri 2026-03-13 16:00: SSO still looping for two admins; requested call for Thursday (Mar 19) [gmail:4dd6e4165f18c195]
judge: FAIL (ref: Kim asked Priya to delay the billing migration a week and was out Mar 10–14; Foster reported recurring SSO loops and wanted fix confirmation before Mar 20. | cand: Kim was out Mar 10–14 but omits the migration delay; Foster reported SSO loops and requested a Mar 19 call, not fix confirmation before Mar 20.)

**v05** what's dk up to
> Daniel Kim: Data retention review stays on track for Mar 30 [slack:C01ENG:1773352800.648477]. Security audit prep is in evidence collection phase, scheduled Mar 24-26 [notion:8c194cecb9a5a1d46e58108e2ae470cc]. He was OOO Mar 10-14 [gmail:469b8c07901db7d8].

Sofia Reyes: Corrected Q1 roadmap ship date to Mar 22, not Mar 20 [gmail:69d12ca0960f4a7d].
judge: FAIL (ref: Daniel Kim asked Priya to delay the billing migration by a week and was out of office Mar 10–14. | cand: Daniel Kim was out of office Mar 10–14; the billing migration request is not mentioned.)

**v06** anything from investors?
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR before Tuesday's partner meeting, asking for confirmation by Monday [gmail:75d73520ec4c68f3].

**Caroline Ades** (Thu 2026-03-12): Asked for an update on data room access [gmail:012ce504e5a045e9].

**Priya Nair** (Fri 2026-03-13): Provided feedback on investor update draft, requesting approximate figures and a cohort chart [gmail:6c967d680a755c1f].
judge: pass (ref: Jordan Pryce requested cohort ARR before the Mar 17 partner meeting; Caroline Ades asked about data room access. | cand: Jordan requested cohort ARR before Tuesday’s meeting; Caroline asked for a data room access update.)

**v07** who's waiting on me
> Waiting on you:
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]

Already handled:
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]
judge: pass (ref: Seven named people, plus Rebecca Liu and Daniel Foster, are waiting on specified tasks. | cand: Lists all referenced people and their waiting tasks, including Rebecca’s two requests and Daniel’s call and SSO confirmation.)

**v08** what did i promise people
> Waiting on you:
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]

Already handled:
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]
judge: pass (ref: Promised Jordan cohort ARR, Caroline data room access, and Sam a SOC 2 summary, all overdue. | cand: Promises to Jordan for cohort metrics, Caroline for data room access, and Sam for a summary, all overdue.)

**v09** anything urgent
> 1. Confirm a fix ships before Mar 20 and get someone on a call thurs with Daniel Foster (Globex) before the 17:30-18:00 UTC check-in today about SSO and the Mar 23 rollout, because Globex SSO redirect loop is Reopened and Globex integration is Blocked. [calendar:bbeda5b103cb82876dd4651501]
2. Send the summary to Sam Okafor (Hooli) immediately, because it was due 2026-03-12 and is still open. [gmail:c81c70603acf1120]
3. Deliver the cohort metrics to Jordan Pryce (Northwind Ventures) immediately, because it was due 2026-03-09 and is still open. [gmail:ccd9c787ded3995d]

Also open (38):
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]
- Meeting today: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- Blocked, owned by you: ACME-365 Rate limit tuning [linear:ACME-365@20260222T0500]
- Blocked, owned by you: ACME-349 Rate limit tuning [linear:ACME-349@20260307T0900]
- Blocked, owned by you: ACME-352 Update dependency [linear:ACME-352@20260225T1100]
- Blocked, owned by you: ACME-342 Add pagination [linear:ACME-342@20260225T0900]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
- Blocked, owned by you: ACME-316 Billing webhook retry [linear:ACME-316@20260219T1200]
- Meeting today: 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
- 17 records still state an old plan and need updating: Seed extension plan [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]; Partner API v2 [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]; Audit log export [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]; Update pricing page to $49/seat [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]; Customer webinar plan [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]; Northwind Ventures - seed extension [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]; CloudHost renewal [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]; Pricing v3 [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]; Initech renewal paperwork [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]; Initech - renewal [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]; Initech renewal terms [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]; Mobile beta plan [notion:a005e60800e96d471e9ea49de3f49c3e][slack:C02PROD:1773331200.887947]; Hiring - Senior Backend [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]; Billing migration plan [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]; Roadmap (Q1) [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]; Blue Harbor Capital - seed extension [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]; Q1 roadmap dates [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
judge: pass (ref: Urgent: Globex check-in at 17:30 UTC today and SSO fix confirmation before Mar 20; Northwind cohort ARR before Tuesday; records still state old plans. | cand: Lists the Globex check-in and fix confirmation, Northwind cohort metrics before Tuesday’s meeting, and records with old plans needing updates.)

**v10** catch me up
> What changed:
- 03-14 v2 API authentication: Reverting to OAuth-only (replaced 'Confirmed: OAuth + API keys.') [slack:C01ENG:1773522000.994933]
- 03-13 hiring - senior backend: Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena [gmail:e98c5b9d26b114a1]
- 03-13 Update pricing page to $59/seat for new customers: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49. (replaced 'Decision: new customers pay $59 per seat, existing customers stay at $49 (grandfathered).') [gmail:7d0d75121cdeaac6]
- 03-13 fundraising close date: Jordan says they cannot close before May 15 because of the partner calendar. (replaced 'Attendees: Marcus, Priya, Omar. Discussed whether the SDK release might slip. No decision yet, revisit next week.') [slack:C07FUND:1773421200.357681]
- 03-13 customer webinar plan: heads up, the speaker has a conflict so i moved the webinar to next friday. [gmail:32a980202cbd8f93]
- 03-13 Initech renewal paperwork: initech renewal is 2 yr at 15% now, legal redlining [slack:C03GEN:1773414000.655032]
- 03-12 Globex SSO redirect loop: reopening ACME-431 (replaced 'Recurred for Globex users on Okta. Needs a second fix.') [slack:C04INC:1773339300.924615]
- 03-12 billing cutover date: Mar 31 [gmail:bfda57e5a3e21af0]
- 03-12 cloudhost renewal: fyi we're holding off on the cloudhost renewal until their new pricing is out. [gmail:2dbbf43ced346885]
- 03-12 Partner API v2: partner api v2 is slipping to q3, the design partners cannot test before then [slack:C01ENG:1773338400.739782]
- 03-12 Audit log export: slipped to april [slack:C01ENG:1773334800.910984]
- 03-12 mobile beta plan: pushed back the beta timeline for now, design is still waiting on the new onboarding flow [slack:C02PROD:1773331200.887947]
- 03-10 weekly product sync meeting date: Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC. [gmail:ff9c102bbfa27a06]
- 03-04 Q1 roadmap dates: ship Mar 22 [slack:C02PROD:1772640000.222201]

At risk:
- Seed extension plan (notion) still says 'Target close: Apr 30. Raise: $3M extension at $12M pre. Lead: Northwind Ventures', but the newer information says: Jordan says they cannot close before May 15 because of the partner calendar.. It is out of date and needs updating [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]
- Partner API v2 (linear) still says 'Target: Q2 launch with two design partners.', but the newer information says: partner api v2 is slipping to q3, the design partners cannot test before then. It is out of date and needs updating [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]
- Audit log export (linear) still says 'Target: ship by Mar 31. Customers want CSV and JSON.', but the newer information says: audit log export slipped to april, legal wants another pass on the retention wording. It is out of date and needs updating [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]
- Update pricing page to $49/seat (linear) still says 'Change the pricing page to $49 per seat for everyone.', but the newer information says: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.. It is out of date and needs updating [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]
- Customer webinar plan (notion) still says 'Webinar: Thursday Mar 19, 11:00 UTC. Host: Hannah Park. Audience: Globex and Ini', but the newer information says: heads up, the speaker has a conflict so i moved the webinar to next friday.. It is out of date and needs updating [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]
- Northwind Ventures - seed extension (crm) still says 'Deal stage: partner meeting. Amount: $3,000,000. Expected close date: 2026-03-31', but the newer information says: Jordan says they cannot close before May 15 because of the partner calendar.. It is out of date and needs updating [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]
- CloudHost renewal (notion) still says 'Renewal date: Mar 31. Owner: Omar Haddad. Plan: renew at the current tier.', but the newer information says: fyi we're holding off on the cloudhost renewal until their new pricing is out.. It is out of date and needs updating [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]
- Pricing v3 (notion) still says 'Decision: $49 per seat per month for all customers. Owner: Hannah Park.', but the newer information says: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.. It is out of date and needs updating [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]
- Initech renewal paperwork (linear) still says 'Prepare 1 year renewal at 10% discount for legal.', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]
- Initech - renewal (crm) still says 'Deal stage: contract sent. Amount: $84,000. Expected close date: 2026-03-31. Typ', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]
- Initech renewal terms (notion) still says 'Term: 1 year. Discount: 10%. Owner: Rebecca Liu. Status: draft sent to legal.', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]
- Mobile beta plan (notion) still says 'Beta timeline: ships Apr 3. Scope: iOS first, Android after. Owner: Marcus Webb.', but the newer information says: pushed back the beta timeline for now, design is still waiting on the new onboarding flow. It is out of date and needs updating [notion:a005e60800e96d471e9ea49de3f49c3e][slack:C02PROD:1773331200.887947]
- Hiring - Senior Backend (notion) still says 'Offer to Taylor Brooks approved at $165k. Status: offer out.', but the newer information says: Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena. It is out of date and needs updating [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]
- Billing migration plan (notion) still says 'Cutover date: Mar 24. Vendor: Ledgerly replaces Paymint. Owner: Omar Haddad.', but the newer information says: Heads up, billing cutover is now Mar 31 (was Mar 24).. It is out of date and needs updating [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]
- Roadmap (Q1) (notion) still says 'Freeze Mar 10. Ship Mar 20. Owner: Sofia Reyes.', but the newer information says: Roadmap: freeze Mar 10, ship Mar 22 (corrected from Mar 20).. It is out of date and needs updating [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]
- Blue Harbor Capital - seed extension (crm) still says 'Deal stage: intro call. Amount: $2,000,000. Expected close date: 2026-04-15. Typ', but the newer information says: Target close: Apr 30.. It is out of date and needs updating [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]
- Q1 roadmap dates (linear) still says 'Freeze Mar 10, ship Mar 20', but the newer information says: value 'Mar 20' was retracted in slack:C02PROD:1772640000.222201. It is out of date and needs updating [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
- Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Blocked, owned by you: ACME-365 Rate limit tuning [linear:ACME-365@20260222T0500]
- Blocked, owned by you: ACME-349 Rate limit tuning [linear:ACME-349@20260307T0900]
- Blocked, owned by you: ACME-352 Update dependency [linear:ACME-352@20260225T1100]
- Blocked, owned by you: ACME-342 Add pagination [linear:ACME-342@20260225T0900]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
- Blocked, owned by you: ACME-316 Billing webhook retry [linear:ACME-316@20260219T1200]

Waiting on you:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]

Coming up today:
- Meeting today: 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- Meeting today: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- Meeting today: 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: OAuth-only auth; billing Mar 31; pricing $59 new/$49 existing; seed close May 15; Taylor offer dead; Globex SSO recurred; Initech renewal 2 years at 15%. | cand: States all listed updates, including OAuth-only, Mar 31 billing, $59/$49 pricing, May 15 seed close, Taylor accepting another offer, recurring Globex loop, and Initech 2 years at 15%.)

**v11** what's blocked
> 28 blocked issues, 5 yours:
- ACME-365 Rate limit tuning (yours, urgent) [linear:ACME-365@20260222T0500]
- ACME-342 Add pagination (yours, high) [linear:ACME-342@20260225T0900]
- ACME-349 Rate limit tuning (yours, high) [linear:ACME-349@20260307T0900]
- ACME-352 Update dependency (yours, high) [linear:ACME-352@20260225T1100]
- ACME-316 Billing webhook retry (yours, no priority) [linear:ACME-316@20260219T1200]
- ACME-433 Hooli export timeout (owner Omar Haddad, high; Blocked by infra change ACME-420) [linear:ACME-433@20260311T1500]
- ACME-363 Rate limit tuning (owner Alex C. Morgan, urgent) [linear:ACME-363@20260220T1200]
- ACME-311 Billing webhook retry (owner Omar Haddad, urgent) [linear:ACME-311@20260225T0900]
- ACME-371 Fix flaky test (owner Daniel Kim, urgent) [linear:ACME-371@20260228T1900]
- ACME-331 Update dependency (owner Sofia Reyes, urgent) [linear:ACME-331@20260302T0900]
- ACME-325 Rate limit tuning (owner Marcus Webb, urgent) [linear:ACME-325@20260308T0500]
- ACME-304 Fix flaky test (owner Sofia Reyes, urgent) [linear:ACME-304@20260314T2200]
- ACME-328 Rate limit tuning (owner Hannah Park, high) [linear:ACME-328@20260219T1200]
- ACME-398 Improve logging (owner Rebecca Liu, high) [linear:ACME-398@20260221T1000]
- ACME-301 Add pagination (owner Daniel Kim, high) [linear:ACME-301@20260225T0100]
- ACME-360 Update dependency (owner Alex C. Morgan, high) [linear:ACME-360@20260226T1700]
- ACME-309 Globex integration (owner Daniel Kim, high) [linear:ACME-309@20260226T1900]
- ACME-306 Rate limit tuning (owner Alex C. Morgan, high) [linear:ACME-306@20260313T0500]
- ACME-399 Update dependency (owner Rebecca Liu, medium) [linear:ACME-399@20260219T1700]
- ACME-382 Billing webhook retry (owner Marcus Webb, medium) [linear:ACME-382@20260227T0500]
- ACME-362 Fix flaky test (owner Daniel Kim, medium) [linear:ACME-362@20260306T0400]
- ACME-401 Add pagination (owner Alex C. Morgan, no priority) [linear:ACME-401@20260221T0700]
- ACME-380 Improve logging (owner Omar Haddad, no priority) [linear:ACME-380@20260224T0700]
- ACME-310 Cache warming (owner Omar Haddad, no priority) [linear:ACME-310@20260303T0100]
- ACME-358 Write migration (owner Rebecca Liu, no priority) [linear:ACME-358@20260304T0900]
- ACME-364 SSO cleanup (owner Marcus Webb, no priority) [linear:ACME-364@20260304T2100]
- ACME-369 Billing webhook retry (owner Marcus Webb, no priority) [linear:ACME-369@20260309T1100]
- ACME-312 Globex integration (owner Alex C. Morgan, no priority) [linear:ACME-312@20260312T1700]
judge: pass (ref: Five blocked issues are ACME-316, ACME-342, ACME-349, ACME-352, and ACME-365; customer-facing ACME-433 is blocked by ACME-420. | cand: Lists those five as yours and says ACME-433, the Hooli export timeout, is blocked by ACME-420.)

**v12** how's billing going
> The billing cutover is now scheduled for March 31 (moved from March 24) [gmail:bfda57e5a3e21af0]. Omar Haddad owns the billing migration and is replacing Paymint with Ledgerly [notion:0f8a538c21e4ef3f1024c7d25666cd47]. Recent invoices have been issued: INV-3004 for $2,416 on March 13 [gmail:3d8af3c57a01ad42]. An open pull request (#230) by Omar handles webhook retries with backoff [github:acme/billing#230]. Note: the Notion billing migration plan showing March 24 is outdated; the current date is March 31 [notion:0f8a538c21e4ef3f1024c7d25666cd47].
judge: FAIL (ref: Cutover moved to Mar 31; Daniel requested a one-week delay and was out until Mar 16; webhook PR 230 awaits your review. | cand: Cutover is Mar 31 and PR 230 is open, but omits Daniel’s request and absence and does not say the PR awaits your review.)

**v13** pricing?
> The pricing page is now live with $59 per seat for new customers and $49 per seat for existing customers [gmail:7d0d75121cdeaac6]. This pricing was decided in a meeting on March 11 and implemented by Sofia Reyes [linear:ACME-441@20260313T1900]. Several older records are outdated: ACME-440 proposed $49 for everyone , the "Pricing v3" notion page suggested $49 for all customers , and both are now stale [linear:ACME-440@20260306T1500] [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc]. The current pricing structure is finalized and active [gmail:7d0d75121cdeaac6] [linear:ACME-441@20260313T1900].
judge: pass (ref: Pricing is $59 per seat for new customers and $49 for existing customers, decided March 11. | cand: Pricing is $59 per seat for new customers and $49 for existing customers, decided March 11.)

**v14** did we hire taylor
> No, we did not hire Taylor. Taylor accepted another offer, so the hiring loop closed [gmail:e98c5b9d26b114a1]. The offer to Taylor Brooks had been approved at $165k , but it was held due to a budget freeze , and Taylor accepted a different position elsewhere [notion:0f72e0247be2673ff5388bb55ebd12b3] [gmail:07c7430cafafc2e3].
judge: FAIL (ref: Taylor was not hired; offer approved Mar 3, held Mar 10, accepted another offer Mar 13, while Notion still says offer is out. | cand: Taylor was not hired and accepted another position; the $165k offer was approved and held for a budget freeze.)

**v15** when do we close the round
> The current decision is that the round cannot close before May 15 because of the partner calendar [slack:C07FUND:1773421200.357681] [slack:C07FUND:1773421200.357681]. This replaced the earlier target of April 30, which Priya Nair had decided on March 12 [notion:d66e87731f6d486a58818da6ad1da108]. Priya Nair corrected this on March 13 based on Jordan's constraint [slack:C07FUND:1773421200.357681] [slack:C07FUND:1773421200.357681]. Omar noted that Ledgerly wants the round closed before signing anything over $50k , which is still an open constraint [slack:C07FUND:1773255600.389065]. Several outdated records still show earlier close dates (March 31 and April 15) and should not be relied on.
judge: pass (ref: The round is scheduled to close May 15, per Jordan at Northwind. | cand: The round cannot close before May 15.)

**v16** what's the deal with sso
> I can't find that in the available data.

The context does not contain any information about SSO (single sign-on) or related discussions.
judge: FAIL (ref: Globex SSO redirect loop ACME-431 returned for Okta users; PR 231 awaits review. | cand: The available data contains no information about SSO or related discussions.)

**v17** what's hooli saying
> Sam Okafor asked Alex to send the SOC 2 report by March 18 [gmail:b0358e336931b315]. Sam reported the nightly export timed out again, the second time this month [gmail:805093022b56ece6]. Alex replied he would send the summary tomorrow (March 12) [gmail:c81c70603acf1120].
judge: FAIL (ref: Nightly export timed out for the second time this month; ACME-433 is blocked by infra change ACME-420. | cand: Sam reported the nightly export timed out for the second time this month, but omits ACME-433 and ACME-420.)

**v18** what did mei say
> **Alex Chen:** Approved Initech's 2-year renewal at 15% discount  and confirmed INV-2207 should show 35 seats with a credit note coming [gmail:19d8c431017747e4] [gmail:67d8c49f3e07178f]. (Thu 2026-03-12 and Tue 2026-03-10) [gmail:42a6081b54253d8a]

**Mei Tanaka:** Asked if Initech could get a 2-year deal with 15% off  and flagged that INV-2207 shows 40 seats instead of the 35 purchased [gmail:b3e0be40fd6f1fea] [gmail:67d8c49f3e07178f]. (Mon 2026-03-09)

**Rebecca Liu:** Requested Alex's approval on Initech's 2-year/15% terms by Thursday for legal to redline [gmail:42a6081b54253d8a]. (Tue 2026-03-10)
judge: pass (ref: Mei asked about INV-2207 showing 40 seats instead of the 35 purchased. | cand: Mei flagged that INV-2207 shows 40 seats instead of the 35 purchased.)

**v19** is ACME-440 up to date
> ACME-440 is outdated [linear:ACME-440@20260306T1500]. Sofia Reyes originally planned to set pricing at $49/seat for everyone, but the pricing page went live on Friday with different terms [gmail:7d0d75121cdeaac6]. New customers now pay $59/seat while existing customers remain at $49/seat [gmail:7d0d75121cdeaac6]. The linear issue hasn't been updated to reflect this change. If anyone is still referencing ACME-440, they should check the current pricing email instead [gmail:7d0d75121cdeaac6].
judge: FAIL (ref: ACME-440 is outdated; new customers pay $59 and existing customers $49, and ACME-441 is done. | cand: ACME-440 is outdated; new customers pay $59 and existing customers $49. It omits ACME-441’s status.)

**v20** any meetings with investors coming up
> Coming up (Mar 15 to Mar 29):
- Tue Mar 17 15:00-16:00 UTC Northwind Ventures partner update with Priya Nair, Jordan Pryce (Northwind Ventures) (11:00 New York time). Before it: Jordan Pryce (Northwind Ventures) is waiting on you: send cohort ARR before Tuesday's partner meeting [calendar:e252dcf3e06e42f839b9cd47db][gmail:75d73520ec4c68f3]
judge: pass (ref: Northwind Ventures partner update Tuesday Mar 17 at 15:00 UTC (11:00 New York) with Jordan Pryce and Priya | cand: Same meeting, time, and participants; identifies Priya as Priya Nair)

**v21** who is jordan
> Jordan Pryce is from Northwind Ventures [gmail:75d73520ec4c68f3].

**Jordan Pryce:** Requested cohort ARR before Tuesday's partner meeting and asked Alex to confirm delivery by Monday [gmail:75d73520ec4c68f3].

**Alex Chen:** Said he would send cohort metrics early the following week , and initially committed to sending updated cohort metrics by Friday [gmail:ccd9c787ded3995d] [gmail:166efe0e6a6aa48a].
judge: FAIL (ref: Jordan Pryce is a partner at Northwind Ventures and the lead candidate for the seed extension. | cand: Jordan Pryce is from Northwind Ventures; it does not identify him as a partner or lead candidate.)

**v22** how much runway do we have
> I can't find that in the available data.

The context contains information about invoice corrections, checkout and export flow metrics, and a reported flake in the export flow, but does not include any details about runway or financial projections.
judge: pass (ref: Runway figure is not available in the sources. | cand: The candidate can't find a runway figure in the available data.)

**v23** who's our CFO
> I can't find that in the available data.

Regarding open items: Priya Nair is waiting on a review for the hiring loop until Mar 14 [gmail:319d43c65089e537]. Daniel Foster needs someone on a call Thursday (Mar 19) about SSO login loops [gmail:4dd6e4165f18c195]. Priya Nair requested cohort ARR data from you by Monday (Mar 16) [slack:C07FUND:1773419400.449808]. Several flakes in billing, checkout, and auth flows were being investigated with Mar 07-10 escalation deadlines , but those dates have passed—current status is unclear. [gmail:f8c2ce3c4f480f47]
judge: pass (ref: The available data does not identify the CFO. | cand: The candidate can't find who the CFO is in the available data.)

**s01** What happened across the company this week?
> What changed:
- 03-14 v2 API authentication: Reverting to OAuth-only (replaced 'Confirmed: OAuth + API keys.') [slack:C01ENG:1773522000.994933]
- 03-13 hiring - senior backend: Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena [gmail:e98c5b9d26b114a1]
- 03-13 Update pricing page to $59/seat for new customers: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49. (replaced 'Decision: new customers pay $59 per seat, existing customers stay at $49 (grandfathered).') [gmail:7d0d75121cdeaac6]
- 03-13 fundraising close date: Jordan says they cannot close before May 15 because of the partner calendar. (replaced 'Attendees: Marcus, Priya, Omar. Discussed whether the SDK release might slip. No decision yet, revisit next week.') [slack:C07FUND:1773421200.357681]
- 03-13 customer webinar plan: heads up, the speaker has a conflict so i moved the webinar to next friday. [gmail:32a980202cbd8f93]
- 03-13 Initech renewal paperwork: initech renewal is 2 yr at 15% now, legal redlining [slack:C03GEN:1773414000.655032]
- 03-12 Globex SSO redirect loop: reopening ACME-431 (replaced 'Recurred for Globex users on Okta. Needs a second fix.') [slack:C04INC:1773339300.924615]
- 03-12 billing cutover date: Mar 31 [gmail:bfda57e5a3e21af0]
- 03-12 cloudhost renewal: fyi we're holding off on the cloudhost renewal until their new pricing is out. [gmail:2dbbf43ced346885]
- 03-12 Partner API v2: partner api v2 is slipping to q3, the design partners cannot test before then [slack:C01ENG:1773338400.739782]
- 03-12 Audit log export: slipped to april [slack:C01ENG:1773334800.910984]
- 03-12 mobile beta plan: pushed back the beta timeline for now, design is still waiting on the new onboarding flow [slack:C02PROD:1773331200.887947]
- 03-10 weekly product sync meeting date: Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC. [gmail:ff9c102bbfa27a06]
- 03-04 Q1 roadmap dates: ship Mar 22 [slack:C02PROD:1772640000.222201]

At risk:
- Seed extension plan (notion) still says 'Target close: Apr 30. Raise: $3M extension at $12M pre. Lead: Northwind Ventures', but the newer information says: Jordan says they cannot close before May 15 because of the partner calendar.. It is out of date and needs updating [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]
- Partner API v2 (linear) still says 'Target: Q2 launch with two design partners.', but the newer information says: partner api v2 is slipping to q3, the design partners cannot test before then. It is out of date and needs updating [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]
- Audit log export (linear) still says 'Target: ship by Mar 31. Customers want CSV and JSON.', but the newer information says: audit log export slipped to april, legal wants another pass on the retention wording. It is out of date and needs updating [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]
- Update pricing page to $49/seat (linear) still says 'Change the pricing page to $49 per seat for everyone.', but the newer information says: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.. It is out of date and needs updating [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]
- Customer webinar plan (notion) still says 'Webinar: Thursday Mar 19, 11:00 UTC. Host: Hannah Park. Audience: Globex and Ini', but the newer information says: heads up, the speaker has a conflict so i moved the webinar to next friday.. It is out of date and needs updating [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]
- Northwind Ventures - seed extension (crm) still says 'Deal stage: partner meeting. Amount: $3,000,000. Expected close date: 2026-03-31', but the newer information says: Jordan says they cannot close before May 15 because of the partner calendar.. It is out of date and needs updating [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]
- CloudHost renewal (notion) still says 'Renewal date: Mar 31. Owner: Omar Haddad. Plan: renew at the current tier.', but the newer information says: fyi we're holding off on the cloudhost renewal until their new pricing is out.. It is out of date and needs updating [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]
- Pricing v3 (notion) still says 'Decision: $49 per seat per month for all customers. Owner: Hannah Park.', but the newer information says: Team, the pricing page is live: $59 per seat for new customers, existing customers stay at $49.. It is out of date and needs updating [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]
- Initech renewal paperwork (linear) still says 'Prepare 1 year renewal at 10% discount for legal.', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]
- Initech - renewal (crm) still says 'Deal stage: contract sent. Amount: $84,000. Expected close date: 2026-03-31. Typ', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]
- Initech renewal terms (notion) still says 'Term: 1 year. Discount: 10%. Owner: Rebecca Liu. Status: draft sent to legal.', but the newer information says: initech renewal is 2 yr at 15% now, legal redlining. It is out of date and needs updating [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]
- Mobile beta plan (notion) still says 'Beta timeline: ships Apr 3. Scope: iOS first, Android after. Owner: Marcus Webb.', but the newer information says: pushed back the beta timeline for now, design is still waiting on the new onboarding flow. It is out of date and needs updating [notion:a005e60800e96d471e9ea49de3f49c3e][slack:C02PROD:1773331200.887947]
- Hiring - Senior Backend (notion) still says 'Offer to Taylor Brooks approved at $165k. Status: offer out.', but the newer information says: Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena. It is out of date and needs updating [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]
- Billing migration plan (notion) still says 'Cutover date: Mar 24. Vendor: Ledgerly replaces Paymint. Owner: Omar Haddad.', but the newer information says: Heads up, billing cutover is now Mar 31 (was Mar 24).. It is out of date and needs updating [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]
- Roadmap (Q1) (notion) still says 'Freeze Mar 10. Ship Mar 20. Owner: Sofia Reyes.', but the newer information says: Roadmap: freeze Mar 10, ship Mar 22 (corrected from Mar 20).. It is out of date and needs updating [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]
- Blue Harbor Capital - seed extension (crm) still says 'Deal stage: intro call. Amount: $2,000,000. Expected close date: 2026-04-15. Typ', but the newer information says: Target close: Apr 30.. It is out of date and needs updating [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]
- Q1 roadmap dates (linear) still says 'Freeze Mar 10, ship Mar 20', but the newer information says: value 'Mar 20' was retracted in slack:C02PROD:1772640000.222201. It is out of date and needs updating [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
- Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Blocked, owned by you: ACME-365 Rate limit tuning [linear:ACME-365@20260222T0500]
- Blocked, owned by you: ACME-349 Rate limit tuning [linear:ACME-349@20260307T0900]
- Blocked, owned by you: ACME-352 Update dependency [linear:ACME-352@20260225T1100]
- Blocked, owned by you: ACME-342 Add pagination [linear:ACME-342@20260225T0900]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
- Blocked, owned by you: ACME-316 Billing webhook retry [linear:ACME-316@20260219T1200]

Waiting on you:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]

Coming up today:
- Meeting today: 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- Meeting today: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- Meeting today: 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: This week: OAuth-only auth, billing cutover Mar 31, pricing $59 new/$49 existing, seed close May 15, Taylor accepted elsewhere, Globex SSO loop returned, Initech renewal 2 years at 15%. | cand: Reports all seven changes, including the OAuth-only decision, Mar 31 cutover, pricing, May 15 seed close, Taylor’s acceptance, Globex loop reopening, and Initech terms.)

**s02** What customer issues are showing up repeatedly?
> - Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
judge: pass (ref: Globex SSO redirect loop recurred; Hooli export timeouts were reported repeatedly. | cand: Globex login loop and Hooli timeout were reported repeatedly.)

**s03** Which tasks are blocked?
> 28 blocked issues, 5 yours:
- ACME-365 Rate limit tuning (yours, urgent) [linear:ACME-365@20260222T0500]
- ACME-342 Add pagination (yours, high) [linear:ACME-342@20260225T0900]
- ACME-349 Rate limit tuning (yours, high) [linear:ACME-349@20260307T0900]
- ACME-352 Update dependency (yours, high) [linear:ACME-352@20260225T1100]
- ACME-316 Billing webhook retry (yours, no priority) [linear:ACME-316@20260219T1200]
- ACME-433 Hooli export timeout (owner Omar Haddad, high; Blocked by infra change ACME-420) [linear:ACME-433@20260311T1500]
- ACME-363 Rate limit tuning (owner Alex C. Morgan, urgent) [linear:ACME-363@20260220T1200]
- ACME-311 Billing webhook retry (owner Omar Haddad, urgent) [linear:ACME-311@20260225T0900]
- ACME-371 Fix flaky test (owner Daniel Kim, urgent) [linear:ACME-371@20260228T1900]
- ACME-331 Update dependency (owner Sofia Reyes, urgent) [linear:ACME-331@20260302T0900]
- ACME-325 Rate limit tuning (owner Marcus Webb, urgent) [linear:ACME-325@20260308T0500]
- ACME-304 Fix flaky test (owner Sofia Reyes, urgent) [linear:ACME-304@20260314T2200]
- ACME-328 Rate limit tuning (owner Hannah Park, high) [linear:ACME-328@20260219T1200]
- ACME-398 Improve logging (owner Rebecca Liu, high) [linear:ACME-398@20260221T1000]
- ACME-301 Add pagination (owner Daniel Kim, high) [linear:ACME-301@20260225T0100]
- ACME-360 Update dependency (owner Alex C. Morgan, high) [linear:ACME-360@20260226T1700]
- ACME-309 Globex integration (owner Daniel Kim, high) [linear:ACME-309@20260226T1900]
- ACME-306 Rate limit tuning (owner Alex C. Morgan, high) [linear:ACME-306@20260313T0500]
- ACME-399 Update dependency (owner Rebecca Liu, medium) [linear:ACME-399@20260219T1700]
- ACME-382 Billing webhook retry (owner Marcus Webb, medium) [linear:ACME-382@20260227T0500]
- ACME-362 Fix flaky test (owner Daniel Kim, medium) [linear:ACME-362@20260306T0400]
- ACME-401 Add pagination (owner Alex C. Morgan, no priority) [linear:ACME-401@20260221T0700]
- ACME-380 Improve logging (owner Omar Haddad, no priority) [linear:ACME-380@20260224T0700]
- ACME-310 Cache warming (owner Omar Haddad, no priority) [linear:ACME-310@20260303T0100]
- ACME-358 Write migration (owner Rebecca Liu, no priority) [linear:ACME-358@20260304T0900]
- ACME-364 SSO cleanup (owner Marcus Webb, no priority) [linear:ACME-364@20260304T2100]
- ACME-369 Billing webhook retry (owner Marcus Webb, no priority) [linear:ACME-369@20260309T1100]
- ACME-312 Globex integration (owner Alex C. Morgan, no priority) [linear:ACME-312@20260312T1700]
judge: pass (ref: The five blocked tasks that are yours are ACME-316, ACME-342, ACME-349, ACME-352, and ACME-365; customer-facing ACME-433 is blocked by ACME-420. | cand: Lists all five of your blocked tasks and says customer-facing ACME-433 is blocked by ACME-420.)

**t01** whats on tdy
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today includes offsite travel, completed 09:30 and 11:00 meetings, cancelled 15:00 1:1, 16:00 sync, 17:30 Globex check-in, and tentative 19:00 board prep. | cand: Lists all of those events with matching times and statuses.)

**t02** who is waitng on me
> Waiting on you:
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Jordan Pryce (Northwind Ventures) asked you: send cohort ARR before Tuesday's partner meeting, due 2026-03-16 (nobody has handled it) [gmail:75d73520ec4c68f3]
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Rebecca Liu asked you: sign-off on the redline, due 2026-03-19 (nobody has handled it) [gmail:2160a6b4c5ac5bdf]
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Rebecca Liu asked you: push the docs migration back a week (nobody has handled it) [gmail:a8bee2a3cdcd15eb]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Caroline Ades (Blue Harbor Capital) asked you: update on the data room access (nobody has handled it) [gmail:012ce504e5a045e9]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
- Omar Haddad asked you: review acme/billing PR #230: billing: webhook retry (ACME-316) (nobody has handled it) [github:acme/billing#230]

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]

Already handled:
- Rebecca Liu asked you: Update ACME-142, due 2026-03-20 (already handled) [gmail:ceece9b31878fe40][linear:ACME-142@20260314T2200]
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
- Hannah Park asked you: Please decline the old invite. (already handled) [gmail:ff9c102bbfa27a06][calendar:7d2712a17add94eb1a82e92b23]
- Rebecca Liu asked you: ok by you? (already answered) [gmail:42a6081b54253d8a][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: do 2 yrs w/ 15% off (already answered) [gmail:67d8c49f3e07178f][gmail:7d508a6afb1224fb]
- Mei Tanaka (Initech) asked you: Could you confirm? (already answered) [gmail:b3e0be40fd6f1fea][gmail:19d8c431017747e4]
- Priya Nair asked you: Log in Linear (already answered) [gmail:403df41545d6ec2d][gmail:1cba60683d78b2ee]
- Jordan Pryce (Northwind Ventures) asked you: Can we do a partner update Tue Mar 17? (already answered) [gmail:6dff2b861992469a][gmail:ccd9c787ded3995d]
- Daniel Foster (Globex) asked you: Can you take a look? (already answered) [gmail:c15f3037c23a7d15][gmail:23185a980c205f87]
judge: pass (ref: You are waiting on Priya, Jordan, Caroline, Daniel, Marcus, Omar, Hannah, and Rebecca for the listed tasks. | cand: The candidate lists all those people and their corresponding outstanding tasks.)

**t03** anyting from investers
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR by Monday before Tuesday's partner meeting, asking for confirmation [gmail:75d73520ec4c68f3].

**Caroline Ades** (Thu 2026-03-12): Asked for an update on data room access [gmail:012ce504e5a045e9].

**Priya Nair** (Fri 2026-03-13): Suggested saying "roughly $1.8M" instead of exact ARR, cutting a slide, and adding the cohort chart [gmail:6c967d680a755c1f].
judge: pass (ref: Jordan Pryce asked Mar 13 for cohort ARR before the Mar 17 partner meeting; Caroline Ades asked Mar 12 about data room access | cand: Jordan Pryce requested cohort ARR before the partner meeting; Caroline Ades asked for an update on data room access)

**t04** whats dnaiel sayin
> **Daniel Kim:** Data retention review timeline unchanged at Mar 30 [slack:C01ENG:1773352800.648477]. Out of office Mar 10-14; Priya has billing context [gmail:469b8c07901db7d8]. Security audit prep in evidence collection phase, audit window Mar 24-26 [notion:8c194cecb9a5a1d46e58108e2ae470cc].

**Daniel Foster (Globex):** SSO still looping for two admins; requested call for Thursday Mar 19 [gmail:4dd6e4165f18c195]. Okta redirect fails on Safari only [gmail:49670ab720e678cb].
judge: FAIL (ref: Daniel Kim asked Priya to delay the billing migration a week; Daniel Foster reported recurring SSO loops and wanted fix confirmation before Mar 20. | cand: Kim was out of office Mar 10–14; Foster reported SSO loops and requested a call for Mar 19.)

**t05** did we hire taylr
> I can't find that in the available data.

However, Taylor Brooks did not get hired. Taylor accepted another offer elsewhere, so the hiring loop closed [gmail:e98c5b9d26b114a1]. The offer to Taylor at $165k was held due to a budget freeze , and then Taylor accepted a different position [slack:C08HIRE:1773156600.279355] [gmail:07c7430cafafc2e3] [gmail:e98c5b9d26b114a1] [gmail:681e9cabc5b3cb1f].
judge: pass (ref: Taylor was not hired; after the $165k offer was put on hold, Taylor accepted another offer. | cand: Taylor Brooks was not hired and accepted another offer after the $165k offer was held.)

**t06** when do we clse the round
> The current plan targets closing before May 15, 2026 [slack:C07FUND:1773421200.357681]. This replaced the earlier April 30 target , which Priya Nair updated after Jordan flagged a partner calendar constraint [notion:d66e87731f6d486a58818da6ad1da108] [slack:C07FUND:1773421200.357681].

Northwind Ventures is the lead investor for the $3M seed extension , with Blue Harbor Capital as backup [notion:d66e87731f6d486a58818da6ad1da108]. However, Ledgerly requires the round closed before signing agreements over $50k [slack:C07FUND:1773255600.389065]. The notion plan from March 12 is outdated—use the current slack update from March 13 instead [slack:C07FUND:1773421200.357681] [notion:d66e87731f6d486a58818da6ad1da108].
judge: FAIL (ref: The round closes May 15, per Jordan at Northwind. | cand: The round is targeted to close before May 15, 2026.)

**t07** prcing?
> The pricing page is now live with $59 per seat for new customers and $49 per seat for existing customers (grandfathered) [gmail:7d0d75121cdeaac6] [linear:ACME-441@20260313T1900]. Sofia Reyes completed this update on Friday 2026-03-13 [gmail:7d0d75121cdeaac6] [linear:ACME-441@20260313T1900]. Earlier records showing $49 for everyone are outdated. There are no open pricing tasks remaining.
judge: pass (ref: Pricing is $59 per seat for new customers and $49 for existing customers | cand: New customers pay $59 per seat; existing customers pay $49 per seat)

**t08** whats blockd
> 28 blocked issues, 5 yours:
- ACME-365 Rate limit tuning (yours, urgent) [linear:ACME-365@20260222T0500]
- ACME-342 Add pagination (yours, high) [linear:ACME-342@20260225T0900]
- ACME-349 Rate limit tuning (yours, high) [linear:ACME-349@20260307T0900]
- ACME-352 Update dependency (yours, high) [linear:ACME-352@20260225T1100]
- ACME-316 Billing webhook retry (yours, no priority) [linear:ACME-316@20260219T1200]
- ACME-433 Hooli export timeout (owner Omar Haddad, high; Blocked by infra change ACME-420) [linear:ACME-433@20260311T1500]
- ACME-363 Rate limit tuning (owner Alex C. Morgan, urgent) [linear:ACME-363@20260220T1200]
- ACME-311 Billing webhook retry (owner Omar Haddad, urgent) [linear:ACME-311@20260225T0900]
- ACME-371 Fix flaky test (owner Daniel Kim, urgent) [linear:ACME-371@20260228T1900]
- ACME-331 Update dependency (owner Sofia Reyes, urgent) [linear:ACME-331@20260302T0900]
- ACME-325 Rate limit tuning (owner Marcus Webb, urgent) [linear:ACME-325@20260308T0500]
- ACME-304 Fix flaky test (owner Sofia Reyes, urgent) [linear:ACME-304@20260314T2200]
- ACME-328 Rate limit tuning (owner Hannah Park, high) [linear:ACME-328@20260219T1200]
- ACME-398 Improve logging (owner Rebecca Liu, high) [linear:ACME-398@20260221T1000]
- ACME-301 Add pagination (owner Daniel Kim, high) [linear:ACME-301@20260225T0100]
- ACME-360 Update dependency (owner Alex C. Morgan, high) [linear:ACME-360@20260226T1700]
- ACME-309 Globex integration (owner Daniel Kim, high) [linear:ACME-309@20260226T1900]
- ACME-306 Rate limit tuning (owner Alex C. Morgan, high) [linear:ACME-306@20260313T0500]
- ACME-399 Update dependency (owner Rebecca Liu, medium) [linear:ACME-399@20260219T1700]
- ACME-382 Billing webhook retry (owner Marcus Webb, medium) [linear:ACME-382@20260227T0500]
- ACME-362 Fix flaky test (owner Daniel Kim, medium) [linear:ACME-362@20260306T0400]
- ACME-401 Add pagination (owner Alex C. Morgan, no priority) [linear:ACME-401@20260221T0700]
- ACME-380 Improve logging (owner Omar Haddad, no priority) [linear:ACME-380@20260224T0700]
- ACME-310 Cache warming (owner Omar Haddad, no priority) [linear:ACME-310@20260303T0100]
- ACME-358 Write migration (owner Rebecca Liu, no priority) [linear:ACME-358@20260304T0900]
- ACME-364 SSO cleanup (owner Marcus Webb, no priority) [linear:ACME-364@20260304T2100]
- ACME-369 Billing webhook retry (owner Marcus Webb, no priority) [linear:ACME-369@20260309T1100]
- ACME-312 Globex integration (owner Alex C. Morgan, no priority) [linear:ACME-312@20260312T1700]
judge: pass (ref: Five blocked issues are yours: ACME-316, ACME-342, ACME-349, ACME-352, ACME-365; customer-facing ACME-433 is blocked by ACME-420. | cand: Lists those five as yours and identifies ACME-433 Hooli export timeout as blocked by ACME-420.)

**n01** what are the initech renewal terms
> The Initech renewal is 2 years at 15% discount [gmail:67d8c49f3e07178f]. Legal is currently redlining the agreement [slack:C03GEN:1773414000.655032].
judge: FAIL (ref: Two years at 15%, approved by Alex on Mar 12, replacing one year at 10%; legal is redlining. | cand: Two years at 15% discount; legal is redlining.)

**n02** is the initech renewal page in notion current
> No, the Initech renewal terms page in Notion is not current [notion:fdfd76a06532aec244da50d79fa1676a]. It shows a 1-year term at 10% discount, but the current terms are 2 years at 15% discount. Rebecca Liu updated the Slack channel on Friday 2026-03-13 with the current information, and legal is now redlining the agreement [slack:C03GEN:1773414000.655032].
judge: pass (ref: The Notion page is outdated: it says 1 year at 10%, while current terms are 2 years at 15%. | cand: The page is not current; it says 1 year at 10%, while current terms are 2 years at 15%.)

**n03** did i approve the initech discount
> Yes, you approved the Initech discount [gmail:42a6081b54253d8a]. You agreed to a 2-year renewal at 15% off. Rebecca Liu is currently handling the legal redlining [slack:C03GEN:1773414000.655032].
judge: pass (ref: You approved a 2-year Initech renewal at 15% off. | cand: You approved a 2-year Initech renewal at 15% off.)

**n04** what did i promise hooli
> Waiting on you:
- nothing

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]

Already handled:
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
judge: pass (ref: Promised Sam Okafor a SOC 2 summary by Mar 12; nothing shows it was sent. | cand: Promised Sam Okafor the summary by Mar 12, still open.)

**n05** when will the soc2 report be ready
> The audit report lands on March 20 [slack:C03GEN:1773328800.908829]. Alex Chen committed to sending a summary by Thursday, March 12 , which was the day after Sam Okafor from Hooli requested the full SOC 2 report by March 18 [gmail:c81c70603acf1120] [gmail:b0358e336931b315]. Omar Haddad clarified that the summary before the full report would be just the pen test executive summary [slack:C03GEN:1773328800.908829]. The full report won't be ready until March 20, which is after Hooli's March 18 deadline.
judge: pass (ref: The audit report lands March 20; before then, only the pen test executive summary is available. | cand: The full audit report lands March 20, and the summary beforehand is only the pen test executive summary.)

**n06** what changes did priya ask for on the investor update
> Priya asked to say roughly $1.8M instead of an exact figure, cut a slide that Jordan will ask about live, and add the cohort chart [gmail:6c967d680a755c1f].
judge: FAIL (ref: Priya asked to say roughly $1.8M ARR, cut the churn slide, and add the cohort chart to the asks section. | cand: Priya asked to say roughly $1.8M, cut a slide Jordan will ask about live, and add the cohort chart.)

**n08** what's the story with hooli
> - You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- Open issue: Hooli export timeout is Blocked (updated 2026-03-11) [linear:ACME-433@20260311T1500]
- Open issue: exports r slow again?? is Todo (updated 2026-03-02) [linear:ACME-470@20260302T1000]
- timeout reported again: 3 reports on 2 days across gmail, linear [gmail:805093022b56ece6][linear:ACME-433@20260311T1500]
- Email from them on 2026-03-11: SOC 2 report [gmail:b0358e336931b315]
- Email from them on 2026-03-11: Export timing out again [gmail:805093022b56ece6]
- Email from them on 2026-03-04: Export timeout [gmail:93c4a504d87495b9]
judge: FAIL (ref: Sam Okafor reported Hooli export timeouts on Mar 4 and 11 (ACME-433, blocked by ACME-420) and wants the SOC 2 report by Mar 18 before renewal. | cand: Reports the Mar 4 and 11 timeouts, says ACME-433 is blocked, and mentions a Mar 11 SOC 2 email; omits ACME-420 and the Mar 18 renewal deadline.)

**h01** what do i need to do before the globex call
> Meeting: 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout)
Before it:
- Daniel Foster (Globex) asked you: can we get someone on a call thurs? (nobody has handled it) [gmail:4dd6e4165f18c195]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Daniel Foster (Globex) asked you: Can you confirm a fix ships before Mar 20?, due 2026-03-20 (nobody has handled it) [gmail:bee95ff7ca51c987]
- Globex SSO redirect loop is Reopened [linear:ACME-431@20260312T1800]
- Globex integration is Blocked [linear:ACME-312@20260312T1700]
- Globex integration is In Progress [linear:ACME-396@20260309T0300]
- Globex integration is Blocked [linear:ACME-309@20260226T1900]
- Globex integration is In Progress [linear:ACME-302@20260225T0000]
- PR waiting on your review: fix: SSO redirect loop for Okta (ACME-431) [github:acme/api#231]
- Related gmail (2026-03-12): Invitation: Globex check-in [gmail:1a560f531ead7680]
judge: pass (ref: Before the 17:30 UTC call, confirm the SSO fix ships before Mar 20, review PR 231, and note ACME-431 reopened after the first fix. | cand: Confirm the fix ships before Mar 20, review PR 231, and note ACME-431 is reopened.)

**h02** anything overdue
> Waiting on you:
- nothing

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
judge: pass (ref: Overdue promises: cohort ARR to Jordan Pryce (Mar 9), data room access to Caroline Ades (Mar 10), SOC 2 summary to Sam Okafor (Mar 12). | cand: All three promises are still open and overdue, with the same recipients and due dates.)

**w01** is the mobile beta still shipping Apr 3
> No, the mobile beta is not shipping Apr 3 [notion:a005e60800e96d471e9ea49de3f49c3e]. Marcus Webb pushed back the beta timeline on Mar 12 [slack:C02PROD:1773331200.887947] [slack:C02PROD:1773331200.887947]. Design is still waiting on the new onboarding flow [slack:C02PROD:1773331200.887947] [slack:C02PROD:1773331200.887947]. The Apr 3 date was in an outdated Notion page from Mar 4 that hasn't been updated [notion:a005e60800e96d471e9ea49de3f49c3e]. Someone might still see the old Apr 3 date in that stale record [notion:a005e60800e96d471e9ea49de3f49c3e].
judge: FAIL (ref: Not shipping Apr 3; timeline pushed back pending onboarding flow, with no new date given. | cand: Not shipping Apr 3; timeline pushed back while design waits on the onboarding flow; the Notion date is stale.)

**w02** when is the customer webinar
> The customer webinar is now Friday, March 20 at an unspecified time [gmail:32a980202cbd8f93] [gmail:32a980202cbd8f93]. Hannah Park moved it from Thursday, March 19, 11:00 UTC because the speaker had a conflict [gmail:32a980202cbd8f93] [gmail:32a980202cbd8f93] [notion:1d661025d9081de511d174c8a6871148]. She sent updated invites to Globex and Initech admins. The outdated Notion page still lists the original Thursday date , which is stale [notion:1d661025d9081de511d174c8a6871148]. The current time is unspecified for the new Friday date [gmail:32a980202cbd8f93].
judge: pass (ref: The webinar was moved to Friday, March 20; the Notion date is outdated. | cand: The webinar is Friday, March 20; the Notion page’s Thursday date is outdated.)

**w03** when does the audit log export ship
> The audit log export slipped to April [slack:C01ENG:1773334800.910984] [slack:C01ENG:1773334800.910984]. Sofia Reyes reversed the previous target of March 31 on March 12 [slack:C01ENG:1773334800.910984]. The old Linear record ACME-480 still shows the outdated March 31 date and is not up to date [linear:ACME-480@20260306T1600] [linear:ACME-480@20260306T1600]. Legal wants another pass on the retention wording before shipping [slack:C01ENG:1773334800.910984].
judge: pass (ref: Audit log export slipped from March 31 to April because legal needs another pass on retention wording. | cand: It slipped to April from the outdated March 31 target because legal wants another pass on retention wording.)

**w04** partner api v2 timeline
> Partner API v2 was originally targeted for Q2 launch with two design partners [linear:ACME-481@20260306T1700]. However, it's now slipping to Q3 because the design partners cannot test before then [slack:C01ENG:1773338400.739782]. The STALE record ACME-481 still shows the Q2 target, but this is outdated [linear:ACME-481@20260306T1700]. Nothing is currently marked open or requiring immediate action on this item.
judge: pass (ref: ACME-481’s Q2 target is outdated; Priya Nair said on Mar 12 it is slipping to Q3 because design partners cannot test sooner. | cand: ACME-481 was targeted for Q2 but is now slipping to Q3 because design partners cannot test sooner; the Q2 record is stale.)

**w05** are we renewing cloudhost
> We're holding off on the CloudHost renewal until their new pricing is out [gmail:2dbbf43ced346885]. Omar Haddad will revisit the decision after that [gmail:2dbbf43ced346885]. An earlier Notion page from March 5 marked the renewal date as March 31 and planned to renew at the current tier , but this is now outdated [notion:32c79bea43b658e1eea8a977aa70b0e4]. The current status is that renewal is paused pending CloudHost's new pricing announcement [gmail:2dbbf43ced346885].
judge: pass (ref: Renewal is on hold until CloudHost publishes new pricing; the March 31 Notion plan is outdated. | cand: Renewal is on hold pending CloudHost's new pricing; the March 31 Notion plan is outdated.)

**w06** is the onboarding checklist redesign still on for Apr 10
> The onboarding checklist redesign is still on track for Apr 10 [slack:C02PROD:1773342000.878146]. Sofia Reyes owns it and it's in design review [notion:61f6d272497704be67c1d43e21410d9e].

However, the mobile beta plan's timeline was pushed back because design is waiting on this onboarding flow [slack:C02PROD:1773331200.887947] [slack:C02PROD:1773331200.887947]. The older notion page from Mar 4 said the mobile beta ships Apr 3, but that's now outdated [notion:a005e60800e96d471e9ea49de3f49c3e]. Marcus Webb made the correction on Mar 12 [slack:C02PROD:1773331200.887947].
judge: pass (ref: Onboarding checklist redesign remains on track for Apr 10, confirmed by Sofia Reyes on Mar 12 and in Notion. | cand: The redesign is still on track for Apr 10.)

**w07** has the docs migration moved
> The docs migration has not been confirmed as moved [gmail:a8bee2a3cdcd15eb]. Rebecca Liu's target date remains Mar 27 [notion:1c306b2522a0dee4bb268dcd8583284a]. However, she emailed on Thu 2026-03-12 asking whether to push it back a week, saying "not sure yet" [gmail:a8bee2a3cdcd15eb]. This means the decision is still open—no calendar note confirms a new date. The older billing migration plan showing Mar 24 is now outdated; the current cutover date is Mar 31 [notion:0f8a538c21e4ef3f1024c7d25666cd47] [gmail:bfda57e5a3e21af0].
judge: pass (ref: Docs migration was not moved; no decision was made, and the target remains Mar 27. | cand: The move remains undecided, and Rebecca Liu’s target date is still Mar 27.)

**k01** what does becky need from me
> Rebecca Liu needs your sign-off on the Initech redline by Thursday, March 19 [gmail:2160a6b4c5ac5bdf]. She also asked for confirmation on the 2yr/15% terms by Thursday, March 12 , but you already approved that on March 12 [gmail:42a6081b54253d8a]. She's now waiting to send you the redline once legal finishes [gmail:2bd8a42deda01cd8].
judge: pass (ref: Rebecca Liu needs your sign-off on the Initech redline by Thursday, March 19. | cand: Rebecca Liu needs your sign-off on the Initech redline by Thursday, March 19.)

**k02** what is dan f saying about sso
> **Daniel Foster (Globex):**
- Fri 2026-03-13 17:00: Okta redirect fails on Safari only [gmail:49670ab720e678cb]
- Fri 2026-03-13 16:00: SSO still looping for two admins, requested call for Thursday Mar 19 [gmail:4dd6e4165f18c195]
- Thu 2026-03-12 17:00: SSO looping returned, needs fix before Mar 20 for Mar 23 rollout [gmail:bee95ff7ca51c987]
- Tue 2026-03-10 18:00: Previous fix looked good [gmail:ef094c02c13dd962]
- Tue 2026-03-03 16:00: Reported SSO redirect loop started Monday Mar 9 [gmail:c15f3037c23a7d15]

**Daniel Kim (teammate):**
- Thu 2026-03-12 22:00: Data retention review timeline unchanged, still Mar 30 [slack:C01ENG:1773352800.648477]
- Mon 2026-03-09 15:00: Out of office Mar 10-14 [gmail:469b8c07901db7d8]
judge: pass (ref: Daniel Foster said SSO loops for two admins and requested a Thursday call; Okta redirect fails only on Safari. | cand: Daniel Foster reported both the SSO loop for two admins and the Safari-only Okta redirect failure, and requested a Thursday call.)
