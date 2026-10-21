# Eval results (70 questions)

model `anthropic:claude-haiku-4-5-20251001`, judge `anthropic:claude-haiku-4-5-20251001`

```
accuracy 84% | citation recall 90% precision 54% | forbidden cites 0 | ungrounded sentences 18
latency p50 1.7s max 8.5s (1 over 5s) | cost $0.00137/question actual, $0.00137 at hosted rates
```

| id | category | correct | cite recall | cite precision | forbidden | sec |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | identity | yes | 1.00 | 1.00 | 0 | 1.2 |
| q02 | decision_reversal | yes | 1.00 | 0.75 | 0 | 1.9 |
| q03 | reschedule | yes | 1.00 | 1.00 | 0 | 4.2 |
| q04 | duplicate_conflict | yes | 1.00 | 0.67 | 0 | 2.1 |
| q05 | unanswerable | yes | 1.00 | 1.00 | 0 | 1.7 |
| q06 | cancelled_meeting | yes | 1.00 | 1.00 | 0 | 2.7 |
| q07 | cancelled_meeting | yes | 1.00 | 0.50 | 0 | 1.8 |
| q08 | history | yes | 1.00 | 0.20 | 0 | 1.8 |
| q09 | identity | NO | 1.00 | 1.00 | 0 | 1.0 |
| q10 | tasks | yes | 1.00 | 1.00 | 0 | 0.0 |
| q11 | shared_inbox | yes | 1.00 | 0.25 | 0 | 2.7 |
| q12 | topic_summary | NO | 0.67 | 0.50 | 0 | 2.1 |
| q13 | decisions | yes | 1.00 | 0.43 | 0 | 0.0 |
| q14 | meeting_prep | yes | 0.50 | 0.20 | 0 | 0.0 |
| q15 | stale_record | yes | 0.50 | 1.00 | 0 | 1.8 |
| q16 | daily_priorities | yes | 1.00 | 0.11 | 0 | 2.4 |
| q17 | followups | yes | 1.00 | 0.38 | 0 | 0.0 |
| q18 | meeting_prep | yes | 1.00 | 0.16 | 0 | 0.1 |
| v01 | vague_schedule | yes | 1.00 | 0.88 | 0 | 0.0 |
| v02 | vague_schedule | yes | 1.00 | 0.50 | 0 | 0.0 |
| v03 | vague_schedule | yes | 1.00 | 1.00 | 0 | 0.0 |
| v04 | vague_person | yes | 0.50 | 0.25 | 0 | 1.8 |
| v05 | vague_person | NO | 1.00 | 0.25 | 0 | 1.8 |
| v06 | vague_person | NO | 1.00 | 0.67 | 0 | 1.6 |
| v07 | vague_followups | yes | 1.00 | 0.38 | 0 | 0.0 |
| v08 | vague_followups | yes | 1.00 | 0.10 | 0 | 0.0 |
| v09 | vague_focus | yes | 1.00 | 0.11 | 0 | 2.4 |
| v10 | vague_catchup | yes | 1.00 | 0.12 | 0 | 0.0 |
| v11 | vague_tasks | yes | 1.00 | 0.21 | 0 | 0.0 |
| v12 | vague_topic | NO | 0.67 | 0.50 | 0 | 3.1 |
| v13 | vague_topic | yes | 1.00 | 0.67 | 0 | 1.9 |
| v14 | vague_topic | yes | 1.00 | 0.67 | 0 | 3.5 |
| v15 | vague_topic | yes | 1.00 | 0.20 | 0 | 4.7 |
| v16 | vague_topic | NO | 0.33 | 0.17 | 0 | 3.2 |
| v17 | vague_topic | yes | 0.50 | 0.33 | 0 | 1.7 |
| v18 | vague_person | yes | 1.00 | 0.50 | 0 | 2.3 |
| v19 | vague_stale | yes | 1.00 | 1.00 | 0 | 1.7 |
| v20 | vague_schedule | yes | 1.00 | 0.50 | 0 | 0.0 |
| v21 | vague_person | yes | 1.00 | 0.33 | 0 | 1.5 |
| v22 | unanswerable | yes | 1.00 | 1.00 | 0 | 1.5 |
| v23 | unanswerable | yes | 1.00 | 1.00 | 0 | 8.5 |
| s01 | spec_company_week | yes | 1.00 | 0.14 | 0 | 0.1 |
| s02 | spec_customer_issues | yes | 0.50 | 0.50 | 0 | 0.0 |
| s03 | spec_blocked | yes | 1.00 | 0.21 | 0 | 0.0 |
| t01 | typo | yes | 1.00 | 0.50 | 0 | 0.0 |
| t02 | typo | yes | 1.00 | 0.38 | 0 | 0.1 |
| t03 | typo | NO | 1.00 | 0.67 | 0 | 1.9 |
| t04 | typo | NO | 0.50 | 0.20 | 0 | 1.7 |
| t05 | typo | NO | 0.00 | 0.00 | 0 | 3.7 |
| t06 | typo | yes | 1.00 | 0.25 | 0 | 2.1 |
| t07 | typo | NO | 1.00 | 0.60 | 0 | 2.1 |
| t08 | typo | yes | 1.00 | 0.21 | 0 | 0.0 |
| n01 | renewal | yes | 1.00 | 0.50 | 0 | 2.3 |
| n02 | renewal_stale | yes | 1.00 | 1.00 | 0 | 2.7 |
| n03 | renewal_decision | yes | 0.00 | 0.00 | 0 | 3.4 |
| n04 | promise_informal | yes | 1.00 | 1.00 | 0 | 0.0 |
| n05 | fact_slash_date | yes | 1.00 | 0.33 | 0 | 3.2 |
| n06 | inline_reply | NO | 1.00 | 1.00 | 0 | 1.2 |
| n08 | customer_topic | yes | 1.00 | 0.67 | 0 | 0.0 |
| h01 | multi_hop | yes | 1.00 | 0.30 | 0 | 0.0 |
| h02 | overdue | yes | 1.00 | 1.00 | 0 | 0.0 |
| w01 | soft_change | yes | 1.00 | 0.50 | 0 | 3.1 |
| w02 | soft_change | yes | 1.00 | 1.00 | 0 | 3.2 |
| w03 | soft_change | yes | 1.00 | 1.00 | 0 | 1.7 |
| w04 | soft_change | yes | 1.00 | 1.00 | 0 | 1.6 |
| w05 | soft_change | yes | 1.00 | 1.00 | 0 | 1.7 |
| w06 | still_current | yes | 0.00 | 0.00 | 0 | 1.6 |
| w07 | still_current | yes | 1.00 | 0.50 | 0 | 2.1 |
| k01 | nickname | yes | 1.00 | 0.33 | 0 | 1.7 |
| k02 | nickname | yes | 1.00 | 0.29 | 0 | 2.7 |

## Answers

**q01** What did Daniel Kim say about the billing migration?
> Daniel Kim asked to push the billing migration by a week because he was on call [gmail:c1abbf680fedaacd] [slack:C01ENG:1773248400.000100]. He also reported that the billing migration was blocked on his side [slack:C01ENG:1773248400.000100].
judge: pass (ref: Daniel asked to push billing migration back by a week; said it was blocked on his side | cand: Daniel asked to push billing migration by a week; reported it was blocked on his side)

**q02** What is the current authentication decision for the v2 API?
> The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933] [linear:ACME-142@20260314T2200]. This reverts the previous plan of OAuth + API keys that Marcus Webb set on Mar 8 [slack:C01ENG:1772992800.207664]. Rebecca Liu made this change on Mar 14 after Globex signed the OAuth-only addendum [gmail:ceece9b31878fe40]. The decision is final and logged in ACME-142, which is now closed [linear:ACME-142@20260314T2200] [slack:C01ENG:1773522000.994933]. Nothing remains open on this decision.
judge: pass (ref: v2 API authentication: OAuth only (Mar 14), reverted from OAuth + API keys (Mar 8), after Globex signed OAuth-only addendum (Rebecca Liu) | cand: v2 API current decision is OAuth only, reverted from OAuth + API keys on Mar 8, changed by Rebecca Liu on Mar 14 after Globex signed OAuth-only addendum)

**q03** What time is the Weekly Product Sync today?
> The Weekly Product Sync is today at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. It was rescheduled from Friday March 13 to today. Alex Chen, Priya Nair, Marcus Webb, and Hannah Park attend [calendar:2ded3454537257a5518fa9905e]. Hannah Park organized the move and asked attendees to decline the old Friday invite [gmail:ff9c102bbfa27a06]. The original Friday slot was cancelled.
judge: pass (ref: Weekly Product Sync is 16:00 UTC today (Sunday Mar 15), moved from Friday Mar 13, Friday event cancelled | cand: Weekly Product Sync today 16:00 UTC, rescheduled from Friday March 13, Friday slot cancelled)

**q04** What is the Q1 ship date?
> The current Q1 ship date is Mar 22 [slack:C02PROD:1772640000.222201] [slack:C02PROD:1772640000.222201]. Sofia Reyes corrected this from the original Mar 20 plan on Wed 2026-03-04 [gmail:69d12ca0960f4a7d] [slack:C02PROD:1772640000.222201]. Several records are now outdated: linear issue ACME-231 , notion page 'Roadmap (Q1)' , and record 4324f4a965bc64d11787c2369776502e  all still show the old Mar 20 date [linear:ACME-231@20260304T1800]. Anyone relying on those sources will have incorrect information.
judge: pass (ref: Q1 ship date is March 22, corrected from March 20 | cand: Q1 ship date is Mar 22, corrected from Mar 20 by Sofia Reyes on Wed 2026-03-04)

**q05** What is the exact revenue impact of the v2 API delay?
> I can't find that in the available data.

The context shows the v2 API authentication approach changed multiple times [linear:ACME-142@20260314T2200]. Globex signed an OAuth-only addendum on Friday , so the final decision is OAuth only [gmail:ceece9b31878fe40] [linear:ACME-142@20260314T2200]. However, the partner API v2 is slipping to Q3 because design partners cannot test before then [slack:C01ENG:1773338400.739782]. There is no information about revenue impact in the available data.
judge: pass (ref: Revenue impact of v2 API delay not available | cand: Cannot find that in available data)

**q06** Was the Weekly Product Sync on Friday March 13 cancelled?
> Yes, the Weekly Product Sync on Friday March 13 was cancelled [calendar:7d2712a17add94eb1a82e92b23]. The event was rescheduled to Sunday March 15 at 16:00 UTC [calendar:2ded3454537257a5518fa9905e]. The calendar note states: "Rescheduled from Fri Mar 13" [calendar:2ded3454537257a5518fa9905e]. Attendees are Alex Chen, Priya Nair, Marcus Webb, and Hannah Park, with Hannah Park as organizer [calendar:2ded3454537257a5518fa9905e]. The new meeting is confirmed.
judge: pass (ref: Friday Mar 13 Weekly Product Sync cancelled, moved to Sunday Mar 15 16:00 UTC | cand: Friday Mar 13 cancelled, rescheduled to Sunday Mar 15 16:00 UTC with attendees and organizer details)

**q07** Was the Daily Standup on March 13 cancelled?
> Yes, the Daily Standup on March 13 was cancelled [calendar:4554e5cfc14461dcdd7a91842f]. It was scheduled for Fri 2026-03-13 14:00 UTC to 14:15 UTC with attendees Alex Chen, Priya Nair, Marcus Webb, Sofia Reyes, and Daniel Kim [calendar:4554e5cfc14461dcdd7a91842f]. The calendar note states: "Cancelled due to offsite" [calendar:4554e5cfc14461dcdd7a91842f]. There is a replacement Standup confirmed for today (Sun 2026-03-15 09:30 UTC) with the same attendees [calendar:c5457a3e77f0e609f8407d2ecf].
judge: pass (ref: Daily Standup on March 13 was cancelled due to offsite | cand: Daily Standup on March 13 was cancelled due to offsite)

**q08** What was the original v2 API auth decision on March 6 and who made it?
> The current decision is to ship v2 API with OAuth only [slack:C01ENG:1773522000.994933] [linear:ACME-142@20260314T2200]. This was originally decided by Priya Nair on March 6 [slack:C01ENG:1772812800.963148]. It was then reversed to OAuth + API keys by Marcus Webb on March 8 , but Rebecca Liu reverted it back to OAuth-only on March 14 after Globex signed the addendum [slack:C01ENG:1772992800.207664] [slack:C01ENG:1773522000.994933] [gmail:ceece9b31878fe40] [slack:C01ENG:1773522000.994933]. Nothing is marked STALE or CANCELLED in the current context.
judge: pass (ref: Priya Nair decided March 6 to ship v2 API with OAuth only | cand: Priya Nair originally decided March 6 to ship v2 API with OAuth only)

**q09** What did Rebecca Liu say about the Globex addendum?
> Rebecca Liu said Globex signed the OAuth-only addendum on Friday, and she is reverting to OAuth-only and will update ACME-142 [gmail:ceece9b31878fe40].
judge: FAIL (ref: Globex signed OAuth-only addendum; v2 API reverts to OAuth only; ACME-142 update requested; issue closed | cand: Globex signed OAuth-only addendum Friday; reverting to OAuth-only; will update ACME-142)

**q10** Which Linear issues owned by me are blocked?
> 5 blocked issues, 5 yours:
- ACME-365 Rate limit tuning (yours, urgent) [linear:ACME-365@20260222T0500]
- ACME-342 Add pagination (yours, high) [linear:ACME-342@20260225T0900]
- ACME-349 Rate limit tuning (yours, high) [linear:ACME-349@20260307T0900]
- ACME-352 Update dependency (yours, high) [linear:ACME-352@20260225T1100]
- ACME-316 Billing webhook retry (yours, no priority) [linear:ACME-316@20260219T1200]
judge: pass (ref: 5 blocked issues owned by user: ACME-316, ACME-342, ACME-349, ACME-352, ACME-365 | cand: 5 blocked issues owned by user: ACME-365, ACME-342, ACME-349, ACME-352, ACME-316)

**q11** Who is out of office this week and who has context on billing?
> Daniel Kim is out of office through March 14 [calendar:b2906b68d5b89b412dce4976fd]. Priya Nair has context on billing [slack:C03GEN:1773068400.685084] [gmail:469b8c07901db7d8]. Daniel requested to push the billing migration by a week while on call , but there's no record of approval or a new date [gmail:c1abbf680fedaacd]. No items are marked STALE or CANCELLED in the available data.
judge: pass (ref: Daniel Kim out Mar 10-14; Priya Nair has billing context | cand: Daniel Kim out through Mar 14; Priya Nair has billing context)

**q12** Summarize investor-related activity this week.
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR by Monday for Tuesday's partner meeting term sheet discussion [gmail:75d73520ec4c68f3].

**Priya Nair** (Fri 2026-03-13): Edited investor update draft to say "roughly $1.8M," remove one slide, and add cohort chart [gmail:6c967d680a755c1f].

**Alex Chen** (Thu 2026-03-12): Sent investor update draft with ARR, churn, and asks sections [gmail:ec270de8c9f8fc39].

**Caroline Ades** (Thu 2026-03-12): Asked for data room access update [gmail:012ce504e5a045e9].
judge: FAIL (ref: Jordan Pryce followed up Mar 13 for cohort ARR before Mar 17 meeting; Caroline Ades asked Mar 12 about data room access; Priya said Northwind cannot close before May 15 | cand: Jordan Pryce requested cohort ARR by Monday for Tuesday partner meeting; Caroline Ades asked for data room access; no mention of Northwind May 15 close date)

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
- mobile beta plan: current plan is 'SDK release: ships Mar 25.'. Records already reflect this, no action needed [notion:bb99d013de107fd46b9c6b77b725b4f7]
- Partner API v2: current plan is 'partner api v2 is slipping to q3, the design partners cannot test before then'. Records already reflect this, no action needed [slack:C01ENG:1773338400.739782]
- Initech renewal paperwork: current plan is 'initech renewal is 2 yr at 15% now, legal redlining'. Records already reflect this, no action needed [slack:C03GEN:1773414000.655032]
- hiring - senior backend: current plan is 'Alex, Taylor accepted another offer, so we are closing the loop on this one. Lena'. Records already reflect this, no action needed [gmail:e98c5b9d26b114a1]
judge: pass (ref: Recent decisions: v2 API auth to OAuth only, Q1 ship Mar 22, pricing $59/$49, billing cutover Mar 31, seed close May 15, Taylor Brooks offer cancelled, Initech renewal 2yr at 15% | cand: Multiple decisions listed including v2 API OAuth-only, Q1 ship Mar 22, pricing $59/$49, billing cutover Mar 31, seed close May 15, Initech renewal 2yr at 15%, plus other unrelated decisions)

**q14** What should I know before my next meeting?
> Meeting: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13)
Before it:
- Priya Nair asked you: approve the data room request for Blue Harbor (nobody has handled it) [slack:C07FUND:1773500400.415602]
- Priya Nair asked you: @Alex Chen Northwind wants cohort ARR by Mon, can you send?, due 2026-03-16 (nobody has handled it) [slack:C07FUND:1773419400.449808]
- Marcus Webb asked you: review acme/api PR #231: fix: SSO redirect loop for Okta (ACME-431) (nobody has handled it) [github:acme/api#231]
- Hannah Park asked you: add a risks slide (nobody has handled it) [gmail:6a959648587ee4e0]
judge: pass (ref: Weekly Product Sync today 16:00 UTC with Priya Nair, Marcus Webb, Hannah Park; rescheduled from Friday Mar 13 | cand: 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park; rescheduled from Fri Mar 13)

**q15** Is the Linear issue ACME-231 up to date?
> No, ACME-231 is not up to date [linear:ACME-231@20260304T1800]. It is marked STALE, meaning it contains outdated information that was corrected later [linear:ACME-231@20260304T1800]. The issue states a freeze date of March 10 and ship date of March 20, but these values are no longer current [linear:ACME-231@20260304T1800]. You should not rely on these dates. The issue is owned by Sofia Reyes and remains reopened, so you may need to contact her for the corrected Q1 roadmap dates [linear:ACME-231@20260304T1800].
judge: pass (ref: ACME-231 not up to date; ship date corrected to Mar 22 | cand: ACME-231 not up to date, marked STALE, freeze Mar 10 ship Mar 20 outdated, ship date corrected to Mar 22)

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
- 17 records still state an old plan and need updating: Seed extension plan [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]; Partner API v2 [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]; Audit log export [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]; Update pricing page to $49/seat [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]; Customer webinar plan [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]; Northwind Ventures - seed extension [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]; CloudHost renewal [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]; Pricing v3 [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]; Initech renewal paperwork [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]; Initech - renewal [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]; Initech renewal terms [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]; Mobile beta plan [notion:a005e60800e96d471e9ea49de3f49c3e][notion:bb99d013de107fd46b9c6b77b725b4f7]; Hiring - Senior Backend [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]; Billing migration plan [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]; Roadmap (Q1) [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]; Blue Harbor Capital - seed extension [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]; Q1 roadmap dates [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
judge: pass (ref: Priorities: Globex check-in 17:30 UTC (SSO fix before Mar 20), cohort ARR to Jordan Pryce before Tuesday meeting, stale records with old plans | cand: Confirm SSO fix ships before Mar 20, call with Daniel Foster before 17:30-18:00 UTC check-in; send cohort metrics to Jordan Pryce; stale records need updating)

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
judge: pass (ref: Follow-ups waiting on you: Priya Nair (cohort ARR, Blue Harbor data room), Jordan Pryce (cohort ARR before Tuesday), Caroline Ades (data room access), Daniel Foster (SSO fix before Mar 20, call Thursday), Marcus Webb (PR 231), Omar Haddad (PR 230), Hannah Park (risks slide). Open promises: cohort ARR to Jordan Pryce, data room access to Caroline Ades, SOC 2 summary to Sam Okafor (all overdue). Rebecca Liu (sign-off by Mar 19, docs migration). | cand: Waiting on you: Priya Nair (cohort ARR, Blue Harbor data room), Jordan Pryce (cohort ARR before Tuesday), Caroline Ades (data room access), Daniel Foster (SSO fix before Mar 20, call Thursday), Marcus Webb (PR 231), Omar Haddad (PR 230), Hannah Park (risks slide), Rebecca Liu (sign-off by Mar 19, docs migration). Open promises: cohort ARR to Jordan Pryce, data room access to Caroline Ades, SOC 2 summary to Sam Okafor (all overdue).)

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
judge: pass (ref: Emails relating to upcoming meetings: Weekly Product Sync (Mar 10), Globex check-in (today), Northwind partner update (Mar 17), Sprint planning (Monday) | cand: Comprehensive list of emails for Weekly Product Sync, Globex check-in, Sprint Planning, Northwind Ventures partner update, and sync with Priya)

**v01** what's on today
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today's schedule: all-day offsite, standup (done), investor prep (done), 1:1 Marcus cancelled, product sync, Globex check-in, board prep (tentative) | cand: Same schedule with additional details: attendees, times, status updates, and context about Globex issues and Daniel Foster's requests)

**v02** what do i have on the calendar today?
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today (Sunday Mar 15): all-day Offsite travel; 09:30 Standup (done); 11:00 Investor update prep (done); 15:00 1:1 Marcus CANCELLED; 16:00 Weekly Product Sync (moved from Friday); 17:30 Globex check-in; 19:00 Board prep (tentative) | cand: All events listed with same times, statuses, and details. Candidate includes additional context like attendees, meeting notes, and task dependencies.)

**v03** tomorrow?
> Tomorrow (Monday Mar 16):
- Mon Mar 16 14:00-15:00 UTC Sprint Planning with Daniel Kim (you have not accepted) [calendar:5c545e66becd5507a0709683f4]
- Mon Mar 16 15:00-15:30 UTC sync w/ priya re raise with Priya Nair [calendar:fac33a36f31a1bd1329721d22d]
- Mon Mar 16 16:00-16:45 UTC Customer escalations review with Marcus Webb, Sofia Reyes (16:00 London time) [calendar:94d8a5fa7f930cba2bb0bba41f]
judge: pass (ref: Tomorrow Monday Mar 16: three meetings at 14:00, 15:00, 16:00 UTC | cand: Tomorrow Monday Mar 16: three meetings at 14:00, 15:00, 16:00 UTC with same titles and times)

**v04** what is daniel saying
> **Daniel Kim:**
- Mon 2026-03-09: Out of office Mar 10-14; Priya has billing context [gmail:469b8c07901db7d8]
- Thu 2026-03-12: Data retention review timeline unchanged, still Mar 30 [slack:C01ENG:1773352800.648477]

**Daniel Foster (Globex):**
- Fri 2026-03-13 17:00: Okta redirect fails on Safari only [gmail:49670ab720e678cb]
- Fri 2026-03-13 16:00: SSO still looping for two admins; requested call for Thursday (Mar 19) [gmail:4dd6e4165f18c195]
judge: pass (ref: Two Daniels: Kim asked to push billing migration a week, out Mar 10-14. Foster says SSO login loops are back, asks for fix confirmation before Mar 20. | cand: Daniel Kim: out of office Mar 10-14, billing context. Daniel Foster: Okta redirect fails Safari only, SSO looping for two admins, requested call Thursday Mar 19.)

**v05** what's dk up to
> Daniel Kim: Data retention review stays on track for Mar 30 [slack:C01ENG:1773352800.648477]. Security audit prep is in evidence collection phase, scheduled Mar 24-26 [notion:8c194cecb9a5a1d46e58108e2ae470cc]. He was OOO Mar 10-14 [gmail:469b8c07901db7d8].

Sofia Reyes: Corrected Q1 roadmap ship date to Mar 22, not Mar 20 [gmail:69d12ca0960f4a7d].
judge: FAIL (ref: Daniel Kim asked Priya to push billing migration a week; was OOO Mar 10-14 | cand: Daniel Kim: data retention review Mar 30, security audit prep Mar 24-26, OOO Mar 10-14. Sofia Reyes: Q1 roadmap ship date Mar 22)

**v06** anything from investors?
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR before Tuesday's partner meeting, asking for confirmation by Monday [gmail:75d73520ec4c68f3].

**Caroline Ades** (Thu 2026-03-12): Asked for an update on data room access [gmail:012ce504e5a045e9].

**Priya Nair** (Fri 2026-03-13): Provided feedback on investor update draft, requesting approximate figures and a cohort chart [gmail:6c967d680a755c1f].
judge: FAIL (ref: Jordan Pryce asked for cohort ARR before Mar 17 meeting; Caroline Ades asked about data room access | cand: Jordan Pryce requested cohort ARR before Tuesday meeting; Caroline Ades asked for data room access update; Priya Nair provided feedback on investor update)

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
judge: pass (ref: Waiting on you: Priya Nair (cohort ARR, Blue Harbor data room), Jordan Pryce (cohort ARR before Tuesday), Caroline Ades (data room access), Daniel Foster (SSO fix before Mar 20, call Thursday), Marcus Webb (PR 231), Omar Haddad (PR 230), Hannah Park (risks slide), Rebecca Liu (Initech redline by Mar 19, docs migration) | cand: Waiting on you: Priya Nair (cohort ARR, Blue Harbor data room), Jordan Pryce (cohort ARR before Tuesday), Caroline Ades (data room access), Daniel Foster (SSO fix before Mar 20, call Thursday), Marcus Webb (PR 231), Omar Haddad (PR 230), Hannah Park (risks slide), Rebecca Liu (redline by Mar 19, docs migration))

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
judge: pass (ref: Promised Jordan Pryce cohort ARR (overdue Mar 9), Caroline Ades data room access by Mar 10 (overdue), Sam Okafor SOC 2 summary by Mar 12 (overdue). | cand: Promised Sam Okafor summary due Mar 12 (overdue), Jordan Pryce cohort metrics due Mar 9 (overdue), Caroline Ades data room access due Mar 10 (overdue).)

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
- 17 records still state an old plan and need updating: Seed extension plan [notion:d66e87731f6d486a58818da6ad1da108][slack:C07FUND:1773421200.357681]; Partner API v2 [linear:ACME-481@20260306T1700][slack:C01ENG:1773338400.739782]; Audit log export [linear:ACME-480@20260306T1600][slack:C01ENG:1773334800.910984]; Update pricing page to $49/seat [linear:ACME-440@20260306T1500][gmail:7d0d75121cdeaac6]; Customer webinar plan [notion:1d661025d9081de511d174c8a6871148][gmail:32a980202cbd8f93]; Northwind Ventures - seed extension [crm:deal:23a551d6fe][slack:C07FUND:1773421200.357681]; CloudHost renewal [notion:32c79bea43b658e1eea8a977aa70b0e4][gmail:2dbbf43ced346885]; Pricing v3 [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc][gmail:7d0d75121cdeaac6]; Initech renewal paperwork [linear:ACME-460@20260304T1800][slack:C03GEN:1773414000.655032]; Initech - renewal [crm:deal:feeb461b12][slack:C03GEN:1773414000.655032]; Initech renewal terms [notion:fdfd76a06532aec244da50d79fa1676a][slack:C03GEN:1773414000.655032]; Mobile beta plan [notion:a005e60800e96d471e9ea49de3f49c3e][notion:bb99d013de107fd46b9c6b77b725b4f7]; Hiring - Senior Backend [notion:0f72e0247be2673ff5388bb55ebd12b3][gmail:e98c5b9d26b114a1]; Billing migration plan [notion:0f8a538c21e4ef3f1024c7d25666cd47][gmail:bfda57e5a3e21af0]; Roadmap (Q1) [notion:4324f4a965bc64d11787c2369776502e][slack:C02PROD:1772640000.222201]; Blue Harbor Capital - seed extension [crm:deal:5916d3104d][notion:d66e87731f6d486a58818da6ad1da108]; Q1 roadmap dates [linear:ACME-231@20260304T1800][slack:C02PROD:1772640000.222201]
judge: pass (ref: Urgent: Globex check-in 17:30 UTC today, SSO fix before Mar 20, cohort ARR to Northwind before Tuesday meeting, old plan records | cand: Globex SSO fix before Mar 20 and call with Daniel Foster today; cohort metrics to Northwind immediately; old plan records still open)

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
- 03-10 weekly product sync meeting date: Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC. [gmail:ff9c102bbfa27a06]
- 03-05 mobile beta plan: SDK release: ships Mar 25. [notion:bb99d013de107fd46b9c6b77b725b4f7]
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
- Mobile beta plan (notion) still says 'Beta timeline: ships Apr 3. Scope: iOS first, Android after. Owner: Marcus Webb.', but the newer information says: SDK release: ships Mar 25.. It is out of date and needs updating [notion:a005e60800e96d471e9ea49de3f49c3e][notion:bb99d013de107fd46b9c6b77b725b4f7]
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
judge: pass (ref: v2 auth OAuth only, billing Mar 31, pricing $59/$49, seed May 15, Taylor Brooks offer dead, Globex SSO recurred, Initech 2yr 15% | cand: v2 auth OAuth only, billing Mar 31, pricing $59/$49, seed May 15, Taylor offer dead, Globex SSO recurred, Initech 2yr 15%)

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
judge: pass (ref: Five blocked issues yours: ACME-316, ACME-342, ACME-349, ACME-352, ACME-365. Customer-facing: ACME-433 blocked by ACME-420. | cand: 28 blocked issues, 5 yours (ACME-365, ACME-342, ACME-349, ACME-352, ACME-316). ACME-433 blocked by ACME-420.)

**v12** how's billing going
> The billing cutover is now scheduled for March 31 (moved from March 24) [gmail:bfda57e5a3e21af0]. Omar Haddad owns the billing migration and is replacing Paymint with Ledgerly [notion:0f8a538c21e4ef3f1024c7d25666cd47]. Recent invoices have been issued: INV-3004 for $2,416 on March 13 [gmail:3d8af3c57a01ad42]. An open pull request (#230) by Omar handles webhook retries with backoff [github:acme/billing#230]. Note: the Notion billing migration plan showing March 24 is outdated; the current date is March 31 [notion:0f8a538c21e4ef3f1024c7d25666cd47].
judge: FAIL (ref: Billing cutover moved to Mar 31; PR 230 webhook retry waiting on review | cand: Billing cutover Mar 31 (from Mar 24); PR 230 webhook retries by Omar; invoices issued)

**v13** pricing?
> The pricing page is now live with $59 per seat for new customers and $49 per seat for existing customers (grandfathered) [gmail:7d0d75121cdeaac6] [linear:ACME-441@20260313T1900]. This pricing was decided in a meeting on March 11 and Sofia Reyes completed the update on March 13 [linear:ACME-441@20260313T1900]. 

Older records showing $49 for everyone  are outdated and should not be used [linear:ACME-440@20260306T1500]. There are no open pricing items remaining.
judge: pass (ref: Pricing: $59 new customers, $49 existing customers (decided Mar 11) | cand: $59 new customers, $49 existing customers, decided Mar 11, updated Mar 13)

**v14** did we hire taylor
> No, we did not hire Taylor. Taylor accepted another offer, so the hiring loop closed [gmail:e98c5b9d26b114a1]. The offer to Taylor Brooks had been approved at $165k , but it was held due to a budget freeze , and Taylor accepted a different position elsewhere [notion:0f72e0247be2673ff5388bb55ebd12b3] [gmail:07c7430cafafc2e3].
judge: pass (ref: Did not hire Taylor; offer approved $165k Mar 3, held Mar 10 budget freeze, Taylor accepted another offer Mar 13 | cand: Did not hire Taylor; offer approved $165k, held for budget freeze, Taylor accepted different position elsewhere)

**v15** when do we close the round
> The current decision is that the round cannot close before May 15 because of the partner calendar [slack:C07FUND:1773421200.357681]. This replaced the earlier plan targeting April 30 , which Priya Nair updated on March 13 [notion:d66e87731f6d486a58818da6ad1da108]. The lead investor is Northwind Ventures with Blue Harbor Capital as backup [notion:d66e87731f6d486a58818da6ad1da108]. Omar Haddad noted that Ledgerly wants the round closed before signing anything over $50k , which may create timing pressure [slack:C07FUND:1773255600.389065]. Several outdated CRM records still show the old March 31 close date [crm:deal:23a551d6fe] [crm:deal:5916d3104d].
judge: pass (ref: Round closes May 15, per Jordan at Northwind (Mar 13) | cand: Round cannot close before May 15 due to partner calendar; earlier Apr 30 plan is outdated)

**v16** what's the deal with sso
> SSO login loops started on March 9 [gmail:c15f3037c23a7d15]. Marcus Webb reproduced it and fixed it in ACME-431 [gmail:23185a980c205f87]. Daniel Foster from Globex confirmed the fix looked good on March 10 , but the issue returned by March 12 [gmail:ef094c02c13dd962] [gmail:bee95ff7ca51c987]. Two problems remain open: SSO still loops for two of Globex's admins , and Okta redirect fails on Safari only [gmail:4dd6e4165f18c195] [gmail:49670ab720e678cb]. Daniel needs confirmation the fix ships before March 20, as Globex's rollout is March 23 [gmail:bee95ff7ca51c987]. A call is scheduled for Thursday, March 19.
judge: FAIL (ref: SSO redirect loop reported Mar 3, fixed Mar 10 in PR 218, returned Mar 12 for Okta users, PR 231 awaiting review, fix needed before Mar 20 rollout Mar 23 | cand: SSO loops started Mar 9, fixed in ACME-431, returned Mar 12, two problems remain open, fix needed before Mar 20 rollout Mar 23)

**v17** what's hooli saying
> Sam Okafor asked Alex to send the SOC 2 report by March 18 [gmail:b0358e336931b315]. Sam reported the nightly export timed out again, the second time this month [gmail:805093022b56ece6]. Alex replied he would send the summary tomorrow (March 12) [gmail:c81c70603acf1120].
judge: pass (ref: Hooli nightly export timed out again, second time this month; tracked by ACME-433, blocked by ACME-420 | cand: Nightly export timed out again, second time this month; also mentions SOC 2 report and Alex's response)

**v18** what did mei say
> **Alex Chen:** Approved Initech's 2-year renewal at 15% discount  and confirmed INV-2207 should show 35 seats with a credit note coming [gmail:19d8c431017747e4] [gmail:67d8c49f3e07178f]. (Thu 2026-03-12 and Tue 2026-03-10) [gmail:42a6081b54253d8a]

**Mei Tanaka:** Asked if Initech could get a 2-year deal with 15% off  and flagged that INV-2207 shows 40 seats instead of the 35 purchased [gmail:b3e0be40fd6f1fea] [gmail:67d8c49f3e07178f]. (Mon 2026-03-09)

**Rebecca Liu:** Requested Alex's approval on Initech's 2-year/15% terms by Thursday for legal to redline [gmail:42a6081b54253d8a]. (Tue 2026-03-10)
judge: pass (ref: Mei asked about INV-2207 showing 40 seats instead of 35 purchased | cand: Mei flagged INV-2207 shows 40 seats instead of 35 purchased and asked about 2-year 15% deal)

**v19** is ACME-440 up to date
> ACME-440 is outdated [linear:ACME-440@20260306T1500]. Sofia Reyes originally planned to set pricing at $49/seat for everyone, but the pricing page went live on Friday with different terms [gmail:7d0d75121cdeaac6]. New customers now pay $59/seat while existing customers remain at $49/seat [gmail:7d0d75121cdeaac6]. The linear issue hasn't been updated to reflect this change. If anyone is still referencing ACME-440, they should check the current pricing email instead [gmail:7d0d75121cdeaac6].
judge: pass (ref: ACME-440 outdated: pricing now $59 new, $49 existing customers | cand: ACME-440 outdated; new customers $59/seat, existing $49/seat; issue not updated)

**v20** any meetings with investors coming up
> Coming up (Mar 15 to Mar 29):
- Tue Mar 17 15:00-16:00 UTC Northwind Ventures partner update with Priya Nair, Jordan Pryce (Northwind Ventures) (11:00 New York time). Before it: Jordan Pryce (Northwind Ventures) is waiting on you: send cohort ARR before Tuesday's partner meeting [calendar:e252dcf3e06e42f839b9cd47db][gmail:75d73520ec4c68f3]
judge: pass (ref: Northwind Ventures partner update Tuesday Mar 17 15:00 UTC with Jordan Pryce and Priya | cand: Northwind Ventures partner update Tue Mar 17 15:00-16:00 UTC with Priya Nair, Jordan Pryce)

**v21** who is jordan
> Jordan Pryce is from Northwind Ventures [gmail:75d73520ec4c68f3].

**Jordan Pryce:** Requested cohort ARR before Tuesday's partner meeting and asked Alex to confirm delivery by Monday [gmail:75d73520ec4c68f3].

**Alex Chen:** Said he would send cohort metrics early the following week , and initially committed to sending updated cohort metrics by Friday [gmail:ccd9c787ded3995d] [gmail:166efe0e6a6aa48a].
judge: pass (ref: Jordan Pryce is a partner at Northwind Ventures, lead candidate for seed extension | cand: Jordan Pryce is from Northwind Ventures)

**v22** how much runway do we have
> I can't find that in the available data.

The context contains information about invoice corrections, checkout and export flow metrics, and a reported flake in the export flow, but does not include any details about runway or financial projections.
judge: pass (ref: Runway information not available; no cash, burn, or runway figures in sources | cand: Cannot find that in the available data)

**v23** who's our CFO
> I can't find that in the available data.

Regarding open items: Priya Nair is waiting on a review for the hiring loop until Mar 14 [gmail:319d43c65089e537]. Daniel Foster needs someone on a call Thursday (Mar 19) about SSO login loops [gmail:4dd6e4165f18c195]. Priya Nair requested cohort ARR data from you by Monday (Mar 16) [slack:C07FUND:1773419400.449808]. Several flakes in billing, checkout, and auth flows were being investigated with Mar 07-10 escalation deadlines , but those dates have passed—current status is unclear. [gmail:f8c2ce3c4f480f47]
judge: pass (ref: CFO information not available | cand: Cannot find CFO information in available data)

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
- 03-10 weekly product sync meeting date: Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC. [gmail:ff9c102bbfa27a06]
- 03-05 mobile beta plan: SDK release: ships Mar 25. [notion:bb99d013de107fd46b9c6b77b725b4f7]
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
- Mobile beta plan (notion) still says 'Beta timeline: ships Apr 3. Scope: iOS first, Android after. Owner: Marcus Webb.', but the newer information says: SDK release: ships Mar 25.. It is out of date and needs updating [notion:a005e60800e96d471e9ea49de3f49c3e][notion:bb99d013de107fd46b9c6b77b725b4f7]
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
judge: pass (ref: This week: v2 auth to OAuth only, billing cutover Mar 31, pricing $59/$49, seed close May 15, Taylor Brooks offer ended, Globex SSO loop back, Initech 2yr at 15% | cand: Lists 12 changes including v2 auth OAuth, billing Mar 31, pricing $59/$49, seed May 15, Taylor accepted elsewhere, Globex SSO loop, Initech 2yr 15%, plus other items)

**s02** What customer issues are showing up repeatedly?
> - Globex login loop reported again: 8 reports on 4 days across gmail, linear, slack, and a fix that was marked done came back [slack:C04INC:1773339300.924615][gmail:4dd6e4165f18c195]
- Hooli timeout reported again: 3 reports on 2 days across gmail, linear [gmail:93c4a504d87495b9][gmail:805093022b56ece6]
judge: pass (ref: Globex SSO redirect loop and Hooli export timeouts are recurring issues | cand: Globex login loop and Hooli timeout reported again with multiple reports across channels)

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
judge: pass (ref: Blocked tasks: yours are ACME-316, ACME-342, ACME-349, ACME-352, ACME-365; customer-facing ACME-433 blocked by ACME-420 | cand: 28 blocked issues listed with 5 yours (ACME-365, ACME-342, ACME-349, ACME-352, ACME-316); ACME-433 blocked by ACME-420)

**t01** whats on tdy
> Today (Sunday Mar 15):
- all day Offsite travel with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (in progress; flights, see the offsite doc) [calendar:f99876efd6449d8ae5bf15d181]
- 09:30-09:45 UTC Standup with Priya Nair, Marcus Webb, Sofia Reyes, Daniel Kim (already happened) [calendar:c5457a3e77f0e609f8407d2ecf]
- 11:00-11:45 UTC Investor update prep with Priya Nair (already happened) [calendar:cb4d6cb65474560e2b3602e163]
- 15:00-15:30 UTC 1:1 Marcus with Marcus Webb (CANCELLED; cancelled, Marcus is covering the Globex fix) [calendar:0b466c05a14a1a7932b277708b]
- 16:00-17:00 UTC Weekly Product Sync with Priya Nair, Marcus Webb, Hannah Park (rescheduled from Fri Mar 13) [calendar:2ded3454537257a5518fa9905e]
- 17:30-18:00 UTC Globex check-in with Marcus Webb, Daniel Foster (Globex) (10:30 Los Angeles time; customer check-in about SSO and the Mar 23 rollout). Before it: Daniel Foster (Globex) is waiting on you: Can you confirm a fix ships before Mar 20?; Daniel Foster (Globex) is waiting on you: can we get someone on a call thurs?; Globex SSO redirect loop is Reopened; Globex integration is Blocked; Globex integration is In Progress; Globex integration is Blocked; Globex integration is In Progress [calendar:bbeda5b103cb82876dd4651501][gmail:bee95ff7ca51c987]
- 19:00-20:00 UTC Board prep with Priya Nair (tentative) [calendar:de4afcd47267780be961f09a4f]
judge: pass (ref: Today's schedule: all-day offsite, standup (done), investor prep (done), 1:1 Marcus cancelled, product sync, Globex check-in, board prep | cand: Same schedule with additional details: attendees, times, status updates, and context about Globex issues and Daniel Foster's requests)

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
judge: pass (ref: 11 people waiting: Priya Nair, Jordan Pryce, Caroline Ades, Daniel Foster, Marcus Webb, Omar Haddad, Hannah Park, Rebecca Liu | cand: 11 people waiting with specific requests and due dates; 3 overdue promises; 9 already handled items)

**t03** anyting from investers
> **Jordan Pryce** (Fri 2026-03-13): Requested cohort ARR by Monday before Tuesday's partner meeting, asking for confirmation [gmail:75d73520ec4c68f3].

**Caroline Ades** (Thu 2026-03-12): Asked for update on data room access and expressed eagerness to keep moving [gmail:012ce504e5a045e9].

**Priya Nair** (Fri 2026-03-13): Suggested saying "roughly $1.8M" instead of exact figure, asked to cut a slide, and requested adding cohort chart [gmail:6c967d680a755c1f].
judge: FAIL (ref: Jordan Pryce asked for cohort ARR by Mar 17 meeting; Caroline Ades asked about data room access | cand: Jordan Pryce requested cohort ARR; Caroline Ades asked for data room access update; Priya Nair made suggestions about figures and slides)

**t04** whats dnaiel sayin
> **Daniel Kim:** Data retention review timeline unchanged at Mar 30 [slack:C01ENG:1773352800.648477]. Out of office Mar 10-14; Priya has billing context [gmail:469b8c07901db7d8]. Security audit prep in evidence collection phase, audit window Mar 24-26 [notion:8c194cecb9a5a1d46e58108e2ae470cc].

**Daniel Foster (Globex):** SSO still looping for two admins; requested call for Thursday Mar 19 [gmail:4dd6e4165f18c195]. Okta redirect fails on Safari only [gmail:49670ab720e678cb].
judge: FAIL (ref: Two Daniels: Kim asked to push billing migration a week, out Mar 10-14. Foster says SSO login loops are back, asks for fix confirmation before Mar 20. | cand: Kim: data retention review Mar 30, out Mar 10-14, Priya has billing context. Foster: SSO looping for two admins, requested call Thursday Mar 19, Okta redirect fails on Safari.)

**t05** did we hire taylr
> I can't find that in the available data.

However, Taylor Brooks did not get hired. Taylor accepted another offer elsewhere, so the hiring loop closed [gmail:e98c5b9d26b114a1]. The offer to Taylor at $165k was held due to a budget freeze , and then Taylor accepted a different position [slack:C08HIRE:1773156600.279355] [gmail:07c7430cafafc2e3] [gmail:e98c5b9d26b114a1] [gmail:681e9cabc5b3cb1f].
judge: FAIL (ref: Taylor not hired; $165k offer approved Mar 3, held Mar 10, Taylor accepted another offer Mar 13 | cand: Can't find data; Taylor didn't get hired, accepted another offer elsewhere)

**t06** when do we clse the round
> The round cannot close before May 15 due to the partner calendar [slack:C07FUND:1773421200.357681]. This replaced the earlier target of April 30 , which Priya Nair updated on March 13 [notion:d66e87731f6d486a58818da6ad1da108]. Jordan communicated the May 15 constraint, prompting the plan revision [slack:C07FUND:1773421200.357681]. The Northwind Ventures deal (lead candidate) previously showed March 31 as expected close, but that's now outdated [crm:deal:23a551d6fe]. Blue Harbor Capital remains the backup investor [crm:deal:5916d3104d].
judge: pass (ref: Round closes May 15; April 30 and March 31 dates are outdated | cand: Round closes May 15; April 30 and March 31 dates are outdated. Includes additional context about Jordan, partner calendar, and backup investor.)

**t07** prcing?
> The pricing page is now live with $59 per seat for new customers and $49 per seat for existing customers (grandfathered) [gmail:7d0d75121cdeaac6] [linear:ACME-441@20260313T1900]. Sofia Reyes completed this update on Friday, March 13 [linear:ACME-441@20260313T1900]. Two earlier records are outdated: ACME-440 proposed $49 for everyone , and the Pricing v3 notion page also suggested uniform $49 pricing —both have been superseded by the current tiered pricing decision [linear:ACME-440@20260306T1500] [notion:5b97d1fb3cdcf59ddcfe591d5807d0dc] [notion:163647759184b558a347537639422466].
judge: FAIL (ref: Pricing: $59 per seat new customers, $49 existing (decided Mar 11) | cand: $59 per seat new customers, $49 existing; completed Mar 13; identifies outdated records)

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
judge: pass (ref: Five blocked issues yours: ACME-316, ACME-342, ACME-349, ACME-352, ACME-365. Customer-facing: ACME-433 blocked by ACME-420. | cand: 28 blocked issues, 5 yours (ACME-365, ACME-342, ACME-349, ACME-352, ACME-316). ACME-433 blocked by ACME-420.)

**n01** what are the initech renewal terms
> The Initech renewal is 2 years at 15% discount [gmail:67d8c49f3e07178f]. Legal is currently redlining the agreement [slack:C03GEN:1773414000.655032].
judge: pass (ref: Initech renewal: 2 years at 15% discount, approved by Alex on Mar 12, legal redlining | cand: Initech renewal is 2 years at 15% discount, legal is redlining the agreement)

**n02** is the initech renewal page in notion current
> No, the Initech renewal terms page in Notion is not current [notion:fdfd76a06532aec244da50d79fa1676a]. It shows a 1-year term at 10% discount, but the current terms are 2 years at 15% discount. Rebecca Liu updated the Slack channel on Friday 2026-03-13 with the current information, and legal is now redlining the agreement [slack:C03GEN:1773414000.655032].
judge: pass (ref: Initech renewal terms outdated: shows 1 year 10% discount, should be 2 years 15% | cand: Initech renewal terms outdated: shows 1 year 10% discount, should be 2 years 15%)

**n03** did i approve the initech discount
> Yes, you approved the Initech discount [gmail:42a6081b54253d8a]. You agreed to a 2-year renewal at 15% off. Rebecca Liu is currently handling the legal redlining [slack:C03GEN:1773414000.655032].
judge: pass (ref: Approved Initech discount: 2 years at 15% | cand: Approved 2-year renewal at 15% off; Rebecca Liu handling legal redlining)

**n04** what did i promise hooli
> Waiting on you:
- nothing

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]

Already handled:
- Sam Okafor (Hooli) asked you: can u send by 3/18?, due 2026-03-18 (already answered) [gmail:b0358e336931b315][gmail:c81c70603acf1120]
judge: pass (ref: Alex promised Sam Okafor SOC 2 summary by Mar 12; Sam also wants SOC 2 report by Mar 18 | cand: Promised Sam Okafor: send summary due Mar 12 (overdue); Sam asked for report by Mar 18)

**n05** when will the soc2 report be ready
> The audit report lands on March 20 [slack:C03GEN:1773328800.908829]. Alex Chen committed to sending a summary by Thursday, March 12 , which was the day after Sam Okafor from Hooli requested the full SOC 2 report by March 18 [gmail:c81c70603acf1120] [gmail:b0358e336931b315]. Omar Haddad clarified that the summary before the full report would be just the pen test executive summary [slack:C03GEN:1773328800.908829]. The full report won't be ready until March 20, which is after Hooli's March 18 deadline.
judge: pass (ref: Audit report lands March 20; pen test executive summary available before | cand: Audit report lands March 20; pen test executive summary available before full report)

**n06** what changes did priya ask for on the investor update
> Priya asked to say roughly $1.8M instead of an exact figure, cut a slide that Jordan will ask about live, and add the cohort chart [gmail:6c967d680a755c1f].
judge: FAIL (ref: Priya asked to say roughly $1.8M ARR, cut churn slide, add cohort chart to asks | cand: Priya asked to say roughly $1.8M, cut slide Jordan will ask about, add cohort chart)

**n08** what's the story with hooli
> - You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- Open issue: Hooli export timeout is Blocked (updated 2026-03-11) [linear:ACME-433@20260311T1500]
- Open issue: exports r slow again?? is Todo (updated 2026-03-02) [linear:ACME-470@20260302T1000]
- timeout reported again: 3 reports on 2 days across gmail, linear [gmail:805093022b56ece6][linear:ACME-433@20260311T1500]
- Email from them on 2026-03-11: SOC 2 report [gmail:b0358e336931b315]
- Email from them on 2026-03-11: Export timing out again [gmail:805093022b56ece6]
- Email from them on 2026-03-04: Export timeout [gmail:93c4a504d87495b9]
judge: pass (ref: Sam Okafor at Hooli reported export timeouts on Mar 4 and Mar 11; wants SOC 2 report by Mar 18 | cand: Export timeouts reported Mar 4 and Mar 11; SOC 2 report requested Mar 11; summary due Mar 12 (overdue))

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
judge: pass (ref: Before 17:30 UTC Globex call: confirm SSO fix ships before Mar 20, review PR 231 (Okta fix), know ACME-431 reopened | cand: Before call: confirm fix ships before Mar 20, review PR 231 (SSO/Okta fix), ACME-431 reopened)

**h02** anything overdue
> Waiting on you:
- nothing

You said you would:
- You promised Sam Okafor (Hooli): will send the summary, due 2026-03-12 (overdue), and it is still open [gmail:c81c70603acf1120]
- You promised Jordan Pryce (Northwind Ventures): slipping on the cohort metrics, due 2026-03-09 (overdue), and it is still open [gmail:ccd9c787ded3995d]
- You promised Caroline Ades (Blue Harbor Capital): send data room access, due 2026-03-10 (overdue), and it is still open [gmail:3794ed2c45e9c301]
judge: pass (ref: Overdue promises: cohort ARR to Jordan Pryce (Mar 9), data room access to Caroline Ades (Mar 10), SOC 2 summary to Sam Okafor (Mar 12) | cand: Three overdue promises: Sam Okafor (Mar 12), Jordan Pryce (Mar 9), Caroline Ades (Mar 10))

**w01** is the mobile beta still shipping Apr 3
> No, the mobile beta is not shipping Apr 3 [notion:a005e60800e96d471e9ea49de3f49c3e]. Marcus Webb corrected the SDK release to ship Mar 25 instead [notion:bb99d013de107fd46b9c6b77b725b4f7] [notion:bb99d013de107fd46b9c6b77b725b4f7]. He then pushed back the beta timeline on Mar 12 because design is waiting on the new onboarding flow [slack:C02PROD:1773331200.887947]. The onboarding checklist redesign is on track for Apr 10 [slack:C02PROD:1773342000.878146]. An outdated notion page still lists Apr 3, but that's been superseded [notion:a005e60800e96d471e9ea49de3f49c3e].
judge: pass (ref: Mobile beta not shipping Apr 3; pushed back Mar 12, no new date given | cand: Mobile beta not shipping Apr 3; pushed back Mar 12 due to onboarding flow; Apr 10 target mentioned)

**w02** when is the customer webinar
> The customer webinar is now Friday, March 20 at an unspecified time [gmail:32a980202cbd8f93] [gmail:32a980202cbd8f93]. Hannah Park moved it from Thursday, March 19, 11:00 UTC because the speaker had a conflict [gmail:32a980202cbd8f93] [gmail:32a980202cbd8f93] [notion:1d661025d9081de511d174c8a6871148]. She sent updated invites to Globex and Initech admins. The outdated Notion page still lists the original Thursday date , which is stale and no longer current [notion:1d661025d9081de511d174c8a6871148].
judge: pass (ref: Customer webinar moved to Friday, March 20 due to speaker conflict | cand: Customer webinar is Friday, March 20; moved from Thursday March 19 due to speaker conflict)

**w03** when does the audit log export ship
> The audit log export slipped to April [slack:C01ENG:1773334800.910984] [slack:C01ENG:1773334800.910984]. Sofia Reyes made this decision on March 12 , reversing the previous target of March 31 [slack:C01ENG:1773334800.910984] [linear:ACME-480@20260306T1600]. Legal needs another pass on the retention wording before shipping [slack:C01ENG:1773334800.910984]. The Linear record ACME-480 still shows the outdated March 31 date and is not current [linear:ACME-480@20260306T1600] [linear:ACME-480@20260306T1600].
judge: pass (ref: Audit log export slipped to April; Sofia Reyes decided March 12; legal needs retention wording pass | cand: Audit log export slipped to April; Sofia Reyes decided March 12; legal needs retention wording pass; ACME-480 outdated)

**w04** partner api v2 timeline
> Partner API v2 was originally targeted for Q2 launch with two design partners [linear:ACME-481@20260306T1700]. However, it's now slipping to Q3 because the design partners cannot test before then [slack:C01ENG:1773338400.739782]. The previous Linear issue ACME-481 is stale and no longer reflects the current timeline [linear:ACME-481@20260306T1700]. There are no open action items or decisions pending on this project in the available data.
judge: pass (ref: Partner API v2 targets Q2 launch, slipping to Q3 per Priya Nair on Mar 12 | cand: Originally Q2, now slipping to Q3 because design partners cannot test before then)

**w05** are we renewing cloudhost
> We're holding off on the CloudHost renewal until their new pricing is out [gmail:2dbbf43ced346885]. Omar Haddad will revisit the decision after that [gmail:2dbbf43ced346885]. An earlier Notion page from March 5 marked the renewal date as March 31 and planned to renew at the current tier , but this is now outdated [notion:32c79bea43b658e1eea8a977aa70b0e4]. The current status is that renewal is paused pending CloudHost's new pricing announcement [gmail:2dbbf43ced346885].
judge: pass (ref: Holding off CloudHost renewal until new pricing published; will revisit after | cand: Holding off renewal until new pricing out; Omar Haddad will revisit after)

**w06** is the onboarding checklist redesign still on for Apr 10
> The onboarding checklist redesign is still on for Apr 10 [notion:61f6d272497704be67c1d43e21410d9e]. It's in design review and owned by Sofia Reyes [notion:61f6d272497704be67c1d43e21410d9e].

I can't find that in the available data about what this replaced or who changed it. No earlier versions or corrections are documented in the context.
judge: pass (ref: Onboarding checklist redesign on track for Apr 10, confirmed by Sofia Reyes Mar 12 | cand: Redesign still on for Apr 10, in design review, owned by Sofia Reyes)

**w07** has the docs migration moved
> The docs migration has not been confirmed as moved [gmail:a8bee2a3cdcd15eb]. Rebecca Liu's target date remains Mar 27 [notion:1c306b2522a0dee4bb268dcd8583284a]. However, she emailed on Thu 2026-03-12 asking whether to push it back a week, saying "not sure yet" [gmail:a8bee2a3cdcd15eb]. This means the decision is still open—no calendar note confirms a new date. The older billing migration plan showing Mar 24 is now outdated; the current cutover date is Mar 31 [notion:0f8a538c21e4ef3f1024c7d25666cd47] [gmail:bfda57e5a3e21af0].
judge: pass (ref: Docs migration not moved; target still Mar 27 | cand: Docs migration not confirmed moved; target Mar 27; decision still open)

**k01** what does becky need from me
> Rebecca Liu needs your sign-off on the Initech redline by Thursday, March 19 [gmail:2160a6b4c5ac5bdf]. She also asked for confirmation on the 2yr/15% terms by Thursday, March 12 , but you already approved that on March 12 [gmail:42a6081b54253d8a]. She's now waiting to send you the redline once legal finishes [gmail:2bd8a42deda01cd8].
judge: pass (ref: Rebecca Liu needs sign-off on Initech redline by Thursday, Mar 19 | cand: Rebecca Liu needs sign-off on Initech redline by Thursday, March 19; also mentions 2yr/15% terms and legal review)

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
judge: pass (ref: Daniel Foster: SSO looping for two admins, Okta redirect fails on Safari only | cand: SSO looping for two admins, Okta redirect fails on Safari only, plus earlier SSO issues)
