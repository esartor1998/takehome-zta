"""
API-shaped synthetic dataset for Founder AI Assistant take-home.
Run: python synthetic_data_generator.py
Outputs:
  data/raw/          <- API-shaped payloads (what real APIs return)
  data/normalized/   <- your context layer's output
  data/answer_key.json
  data/SOURCES.md

Sources modeled: Gmail API, Google Calendar API, Slack conversations.history, Linear GraphQL.
Shape fidelity notes cited in SOURCES.md.
"""

import json, os, random, base64
from datetime import datetime, timedelta, timezone

random.seed(20260315)
# separate seeded RNG for ids: reproducible output without perturbing the
# content RNG stream
_id_rng = random.Random(20260316)
def _hex(n): return f"{_id_rng.getrandbits(128):032x}"[:n]
RAW = "data/raw"
NORM = "data/normalized"
os.makedirs(RAW, exist_ok=True)
os.makedirs(NORM, exist_ok=True)

CURRENT_TIME = datetime(2026, 3, 15, 14, 0, 0, tzinfo=timezone.utc)
def iso(dt): return dt.isoformat().replace("+00:00", "Z")
def epoch_ms(dt): return int(dt.timestamp() * 1000)
def t(days=0, hours=0, minutes=0):
    return CURRENT_TIME + timedelta(days=days, hours=hours, minutes=minutes)

# ============================================================
# PEOPLE — canonical map (lives in answer_key, not in raw data)
# ============================================================
PEOPLE = {
    "P1": {"name":"Alex Chen","work":"alex.chen@acmerobotics.com","personal":"alexchen.personal@gmail.com",
           "slack_id":"U01ALEXCHEN","slack_handle":"@alex.c","linear_id":"usr_alexchen","linear_name":"alexchen"},
    "P2": {"name":"Priya Nair","work":"priya.nair@acmerobotics.com","personal":"priya.nair88@gmail.com",
           "slack_id":"U02PRIYAN","slack_handle":"@priya","linear_id":"usr_priyanair","linear_name":"priyanair"},
    "P3": {"name":"Marcus Webb","work":"marcus.webb@acmerobotics.com","personal":"mwebb.dev@outlook.com",
           "slack_id":"U03MARCUS","slack_handle":"@marcus","linear_id":"usr_mwebb","linear_name":"mwebb"},
    "P4": {"name":"Sofia Reyes","work":"sofia.reyes@acmerobotics.com","personal":"sofia.reyes@proton.me",
           "slack_id":"U04SOFIA","slack_handle":"@sofia","linear_id":"usr_sofiar","linear_name":"sofiar"},
    "P5": {"name":"Daniel Kim","work":"daniel.kim@acmerobotics.com","personal":"dkim.work@gmail.com",
           "slack_id":"U05DANIEL","slack_handle":"@daniel","linear_id":"usr_dkim","linear_name":"dkim"},
    "P6": {"name":"Alex C. Morgan","work":"alex.morgan@acmerobotics.com","personal":"acmorgan@yahoo.com",
           "slack_id":"U06ALEXM","slack_handle":"@alex.m","linear_id":"usr_alexmorgan","linear_name":"alexmorgan"},
    "P7": {"name":"Hannah Park","work":"hannah.park@acmerobotics.com","personal":"hpark.personal@gmail.com",
           "slack_id":"U07HANNAH","slack_handle":"@hannah","linear_id":"usr_hpark","linear_name":"hpark"},
    "P8": {"name":"Omar Haddad","work":"omar.haddad@acmerobotics.com","personal":"ohaddad@icloud.com",
           "slack_id":"U08OMAR","slack_handle":"@omar","linear_id":"usr_ohaddad","linear_name":"ohaddad"},
    "P9": {"name":"Rebecca Liu","work":"rebecca.liu@acmerobotics.com","personal":"becky.liu@personal.com",
           "slack_id":"U09BECKY","slack_handle":"@becky","linear_id":"usr_rliu","linear_name":"rliu"},
}
SHARED_INBOX = "eng-team@acmerobotics.com"

# ============================================================
# GMAIL API-SHAPED RECORDS
# Shape: id, threadId, labelIds, snippet, internalDate (epoch ms),
#        payload.headers[] (From/To/Subject/Date), payload.body.data (base64url)
# ============================================================
gmail_raw = []
def gmail_msg(frm, to, subject, body, when, thread_id=None):
    msg_id = _hex(16)
    thread_id = thread_id or _hex(16)
    raw_mime = f"From: {frm}\r\nTo: {to}\r\nSubject: {subject}\r\nDate: {when.strftime('%a, %d %b %Y %H:%M:%S +0000')}\r\n\r\n{body}"
    rec = {
        "id": msg_id,
        "threadId": thread_id,
        "labelIds": ["INBOX", "UNREAD"] if random.random() < 0.4 else ["INBOX"],
        "snippet": body[:120].replace("\n", " "),
        "internalDate": str(epoch_ms(when)),           # Gmail returns string
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": frm},
                {"name": "To", "value": to},
                {"name": "Subject", "value": subject},
                {"name": "Date", "value": when.strftime('%a, %d %b %Y %H:%M:%S +0000')},
            ],
            "body": {"data": base64.urlsafe_b64encode(body.encode()).decode().rstrip("=")}
        }
    }
    gmail_raw.append(rec)
    return rec

# ---- R4: auth decision reversal thread ----
g0 = gmail_msg(PEOPLE["P2"]["work"], PEOPLE["P1"]["work"],
    "v2 API auth — decision",
    "Decision: ship v2 API with OAuth only. Please log in Linear.",
    t(-9,0), "thread_auth_001")
g1 = gmail_msg(PEOPLE["P1"]["work"], PEOPLE["P2"]["work"],
    "Re: v2 API auth — decision",
    "Logged ACME-142 as OAuth-only.\n\nOn Mar 6, Priya wrote:\n> Decision: ship v2 API with OAuth only.",
    t(-9,1), "thread_auth_001")
g2 = gmail_msg(PEOPLE["P3"]["work"], PEOPLE["P1"]["work"],
    "Re: v2 API auth — decision",
    "Globex still needs API keys. Reopening.\n\nOn Mar 6, Priya wrote:\n> Decision: ship v2 API with OAuth only.",
    t(-7,3), "thread_auth_001")
g3 = gmail_msg(PEOPLE["P1"]["work"], PEOPLE["P3"]["work"],
    "Re: v2 API auth — decision",
    "New plan: OAuth + API keys. Updating Linear.\n\nMarcus wrote:\n> Globex still needs API keys.",
    t(-7,5), "thread_auth_001")
g4 = gmail_msg(PEOPLE["P9"]["work"], PEOPLE["P1"]["work"],
    "Re: v2 API auth — decision",
    "Globex signed the OAuth-only addendum Friday. Reverting to OAuth-only. Please update ACME-142.",
    t(-1,6), "thread_auth_001")

# ---- R6: roadmap duplicate/quote thread ----
r0 = gmail_msg(PEOPLE["P4"]["work"], PEOPLE["P5"]["work"],
    "Q1 roadmap dates", "Freeze Mar 10. Ship Mar 20.", t(-12,2), "thread_roadmap_001")
r1 = gmail_msg(PEOPLE["P5"]["work"], PEOPLE["P4"]["work"],
    "Re: Q1 roadmap dates",
    "Thanks.\n\nSofia wrote:\n> Freeze Mar 10. Ship Mar 20.", t(-12,3), "thread_roadmap_001")
r2 = gmail_msg(PEOPLE["P4"]["work"], PEOPLE["P5"]["work"],
    "Re: Q1 roadmap dates",
    "Correction: ship Mar 22, not Mar 20.\n\nDaniel wrote:\n> Thanks.\n\nSofia wrote:\n> Freeze Mar 10. Ship Mar 20.",
    t(-11,1), "thread_roadmap_001")

# ---- R5: meeting reschedule ----
m0 = gmail_msg(PEOPLE["P7"]["work"], PEOPLE["P1"]["work"] + ", " + PEOPLE["P2"]["work"],
    "Weekly Product Sync moved",
    "Moving Weekly Product Sync from Fri Mar 13 to Sun Mar 15 16:00 UTC. Please decline the old invite.",
    t(-5,4), "thread_meeting_001")

# ---- R3: personal email used for work ----
gmail_msg(PEOPLE["P5"]["personal"], PEOPLE["P2"]["work"],
    "billing migration — quick q",
    "Can we push billing migration a week? Asking from my personal since I'm on call.\n— Daniel",
    t(-4,2), "thread_billing_001")

# ---- R3: shared inbox ----
gmail_msg(SHARED_INBOX, PEOPLE["P2"]["work"],
    "Handoff — OOO",
    "I'm OOO Mar 10-14. Priya has context on billing. — Daniel",
    t(-6,1), "thread_ooo_001")

# ---- Filler Gmail (realistic length: 3-6 sentences) ----
subjects = ["Standup notes","Deploy checklist","Vendor invoice","Design review","Bug triage",
            "Hiring loop","Customer escalation","Sprint planning","Security audit","Docs update",
            "Release notes","On-call handoff","Globex sync","Initech renewal","Hooli demo"]
bodies_long = [
    "Quick update on this. {owner} owns the next step. Current status is {status}. "
    "We are blocked on {dep} until {when}. I will follow up if nothing changes by EOD.",
    "Heads up: {cust} reported a flake in the {area} flow. Repro steps are in Linear {issue}. "
    "{owner} is looking. If we cannot reproduce by {when}, we should escalate to the on-call.",
    "The deploy went green at {when}. I verified the {area} dashboard and saw no regressions. "
    "Rolling forward with the plan we discussed. cc {cc} for visibility.",
    "Invoice {inv} was paid. Finance confirmed receipt. The {cust} renewal is still pending legal review. "
    "Expect an update from {owner} by {when}. No action needed from you right now.",
    "I pulled the metrics for {area}. Error rate is flat. Latency p99 is up ~{pct}% but within budget. "
    "Recommend we ship as planned. Full numbers in the attached doc. Let me know if you want a deeper dive.",
]
custs = ["Globex","Initech","Hooli","Umbrella","Stark","Wayne"]
areas = ["checkout","billing","search","auth","ingest","export"]
for i in range(300):
    a = random.choice(list(PEOPLE.keys())); b = random.choice(list(PEOPLE.keys()))
    while b == a: b = random.choice(list(PEOPLE.keys()))
    s = random.choice(subjects) + f" #{i+1}"
    body = random.choice(bodies_long).format(
        owner=PEOPLE[a]["name"], status=random.choice(["open","blocked","done"]),
        dep=random.choice(["review","infra","legal"]),
        when=t(-random.randint(1,15),0).strftime("%b %d"),
        issue=f"ACME-{random.randint(100,399)}",
        cust=random.choice(custs), area=random.choice(areas),
        inv=f"INV-{random.randint(1000,9999)}",
        cc=PEOPLE[b]["name"], pct=random.randint(5,40))
    frm = PEOPLE[a]["work"] if random.random() < 0.8 else PEOPLE[a]["personal"]
    to = PEOPLE[b]["work"]
    if random.random() < 0.03: to = to + ", " + SHARED_INBOX
    gmail_msg(frm, to, s, body, t(-random.randint(0,20), random.randint(0,23)))

# ============================================================
# GOOGLE CALENDAR API-SHAPED RECORDS
# Shape: id, status, summary, start/end {dateTime, timeZone}, attendees[]
#        with responseStatus, organizer, recurringEventId
# ============================================================
cal_raw = []
def cal_event(summary, start, end, attendees, status="confirmed", organizer=None,
              note=None, recurring_id=None):
    rec = {
        "id": _hex(26),
        "status": status,
        "summary": summary,
        "start": {"dateTime": iso(start), "timeZone": "UTC"},
        "end": {"dateTime": iso(end), "timeZone": "UTC"},
        "attendees": [
            {"email": PEOPLE[a]["work"], "displayName": PEOPLE[a]["name"],
             "responseStatus": random.choice(["accepted","accepted","accepted","needsAction","declined"])}
            for a in attendees
        ],
        "organizer": {"email": PEOPLE[organizer]["work"], "displayName": PEOPLE[organizer]["name"]},
    }
    if note: rec["description"] = note
    if recurring_id: rec["recurringEventId"] = recurring_id
    cal_raw.append(rec)
    return rec

# R5: cancelled old + confirmed new (both records exist)
cal_event("Weekly Product Sync", t(-2,-4), t(-2,-3), ["P1","P2","P3","P7"],
          status="cancelled", organizer="P7", note="Moved to Sun Mar 15 16:00 UTC")
cal_event("Weekly Product Sync", t(0,2), t(0,3), ["P1","P2","P3","P7"],
          status="confirmed", organizer="P7", note="Rescheduled from Fri Mar 13")

# R2: yesterday/tomorrow distractors
cal_event("Design Review", t(-1,1), t(-1,2), ["P4","P2"], organizer="P4")
cal_event("Sprint Planning", t(1,0), t(1,1), ["P1","P5"], organizer="P1")

# Recurring event with one cancelled instance (realistic Google Calendar shape)
cal_event("Daily Standup", t(-3,0), t(-3,0)+timedelta(minutes=15),
          ["P1","P2","P3","P4","P5"], organizer="P1", recurring_id="rec_standup_001")
cal_event("Daily Standup", t(-2,0), t(-2,0)+timedelta(minutes=15),
          ["P1","P2","P3","P4","P5"], status="cancelled", organizer="P1",
          recurring_id="rec_standup_001", note="Cancelled due to offsite")

for i in range(46):
    a = random.choice(list(PEOPLE.keys()))
    day = -random.randint(0,20)
    cal_event(random.choice(["1:1","Standup","Retro","Office Hours","Customer Call"]),
              t(day, random.randint(0,20)), t(day, random.randint(0,20))+timedelta(hours=1),
              [a], organizer=a)

# ============================================================
# SLACK API-SHAPED RECORDS
# Shape: type, user (U...), text, ts (string with microseconds), thread_ts,
#        reactions[], edited {user, ts}, bot_id
# ============================================================
slack_raw = []
CHANNELS = {"C01ENG":"#eng","C02PROD":"#product","C03GEN":"#general",
            "C04INC":"#incidents","C05DES":"#design","C06RAND":"#random"}
def slack_msg(user_id, channel_id, text, when, thread_ts=None, edited=False, bot=False):
    ts = f"{int(when.timestamp())}.{random.randint(100000,999999):06d}"
    # channel_id is not in real conversations.history rows (the call is per-channel);
    # it is added here to model an export that tags each row with its source channel
    rec = {"type":"message","channel_id":channel_id,"user":user_id,"text":text,"ts":ts}
    if thread_ts: rec["thread_ts"] = thread_ts
    if edited:
        rec["edited"] = {"user": user_id, "ts": f"{int(when.timestamp())+60}.000000"}
    if random.random() < 0.2:
        rec["reactions"] = [{"name": random.choice(["eyes","+1","tada"]),
                             "count": random.randint(1,5), "users": []}]
    if bot: rec["bot_id"] = "B" + _hex(8).upper()
    slack_raw.append(rec)
    return rec

# R4 mirrored in Slack
slack_msg(PEOPLE["P2"]["slack_id"], "C01ENG",
    "Decision logged: v2 API = OAuth only (ACME-142).", t(-9,2))
slack_msg(PEOPLE["P3"]["slack_id"], "C01ENG",
    "Reversing: Globex needs API keys. ACME-142 updated.", t(-7,4))
slack_msg(PEOPLE["P1"]["slack_id"], "C01ENG",
    "Confirmed: OAuth + API keys.", t(-7,5))
slack_msg(PEOPLE["P9"]["slack_id"], "C01ENG",
    "Reverting to OAuth-only — Globex addendum signed. ACME-142 closed.", t(-1,7), edited=True)

# R6: roadmap duplicate in Slack
slack_msg(PEOPLE["P4"]["slack_id"], "C02PROD",
    "Roadmap: freeze Mar 10, ship Mar 22 (corrected from Mar 20).", t(-11,2))

# R5: meeting chatter in Slack
slack_msg(PEOPLE["P7"]["slack_id"], "C03GEN",
    "Weekly Product Sync now Sun Mar 15 16:00 UTC (was Fri Mar 13).", t(-5,6))

# Slack filler with thread replies
filler = ["pushed a fix, PTAL","standup in 10","blocked on review","deploy went green",
          "customer reported flake","updated the doc","can someone review ACME-{n}?",
          "on-call handoff done","merged the PR","rerunning CI","who owns billing migration?",
          "Globex call moved","meeting notes in the doc","billing migration is blocked"]
for i in range(160):
    uid_choice = random.choice(list(PEOPLE.keys()))
    cid = random.choice(list(CHANNELS.keys()))
    parent = slack_msg(PEOPLE[uid_choice]["slack_id"], cid,
                       random.choice(filler).format(n=random.randint(100,399)),
                       t(-random.randint(0,20), random.randint(0,23)))
    if random.random() < 0.15:
        slack_msg(random.choice(list(PEOPLE.keys())) and PEOPLE[random.choice(list(PEOPLE.keys()))]["slack_id"],
                  cid, "following up on this", t(-random.randint(0,10), random.randint(0,23)),
                  thread_ts=parent["ts"])

# ============================================================
# LINEAR GRAPHQL-SHAPED RECORDS
# Shape: id, identifier, title, description, state{name}, assignee{name,id},
#        priority, createdAt, updatedAt, labels{nodes[]}
# ============================================================
linear_raw = []
def linear_issue(identifier, title, desc, state, assignee_key, when, created_when,
                 priority=None, labels=None):
    rec = {
        "id": _hex(24),
        "identifier": identifier,
        "title": title,
        "description": desc,
        "state": {"name": state},
        "assignee": {"id": PEOPLE[assignee_key]["linear_id"], "name": PEOPLE[assignee_key]["linear_name"]},
        "priority": priority,
        "createdAt": iso(created_when),
        "updatedAt": iso(when),
        "labels": {"nodes": [{"name": l} for l in (labels or [])]},
    }
    linear_raw.append(rec)
    return rec

# R4: three states of the same issue (simulates an audit/snapshot export, not a single GraphQL query)
linear_issue("ACME-142","v2 API authentication","Ship v2 API with OAuth only.",
             "In Progress","P1", t(-9,1), t(-9,0), priority=1, labels=["backend"])
linear_issue("ACME-142","v2 API authentication",
             "Ship v2 API with OAuth + API keys (reversal for Globex).",
             "Blocked","P1", t(-7,3), t(-9,0), priority=1, labels=["backend"])
linear_issue("ACME-142","v2 API authentication",
             "Ship v2 API with OAuth only (final, Globex addendum signed).",
             "Done","P1", t(-1,8), t(-9,0), priority=1, labels=["backend"])

# R6: stale Linear record (says Mar 20; email/Slack corrected to Mar 22)
linear_issue("ACME-231","Q1 roadmap dates","Freeze Mar 10, ship Mar 20.",
             "Reopened","P4", t(-11,4), t(-14,0), priority=2)

# Filler Linear
titles = ["Fix flaky test","Add pagination","Improve logging","Update dependency",
          "Write migration","Refactor handler","Cache warming","Rate limit tuning",
          "Audit log export","SSO cleanup","Billing webhook retry","Globex integration"]
for i in range(110):
    iid = f"ACME-{300+i}"
    linear_issue(iid, random.choice(titles) + f" ({iid})",
                 f"Issue {iid} details.", random.choice(["Todo","In Progress","Done","Blocked"]),
                 random.choice(list(PEOPLE.keys())),
                 t(-random.randint(0,25), random.randint(0,23)),
                 t(-random.randint(26,40), 0),
                 priority=random.choice([0,1,2,3,None]),
                 labels=random.choice([["backend"],["frontend"],["infra"],["security"]]))

# R3: Daniel's Slack mention of the billing migration (added after all random-driven
# filler so the seeded filler data is unchanged). Appended directly: slack_msg would
# consume RNG state
_ts = t(-4,3)
slack_raw.append({"type":"message","channel_id":"C01ENG","user":PEOPLE["P5"]["slack_id"],
    "text":"billing migration is blocked on my side, asked Priya by email to push it a week.",
    "ts":f"{int(_ts.timestamp())}.000100"})

# ---- second layer: breadth and variance (separate seeded rng, runs after every draw above) ----
_orig = dict(gmail=list(gmail_raw), cal=list(cal_raw), slack=list(slack_raw), linear=list(linear_raw))
from synthetic_data_expansion import expand
EXPANSION = expand(dict(PEOPLE=PEOPLE, hex=_hex, gmail_raw=gmail_raw, cal_raw=cal_raw,
                        slack_raw=slack_raw, linear_raw=linear_raw, CURRENT_TIME=CURRENT_TIME))

# ============================================================
# WRITE RAW FILES
# ============================================================
def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

# ---- directory exports ----
# no randomness below, so ids and filler above are unchanged. real tenants expose
# these through slack users.list, linear users and the google people api
SLACK_USERS = {"members": [
    {"id": v["slack_id"], "name": v["slack_handle"].lstrip("@"), "real_name": v["name"],
     "profile": {"display_name": v["slack_handle"].lstrip("@"), "email": v["work"]}}
    for v in PEOPLE.values()]}
LINEAR_USERS = {"nodes": [
    {"id": v["linear_id"], "name": v["linear_name"], "displayName": v["linear_name"],
     "email": v["work"]} for v in PEOPLE.values()]}
# personal addresses are missing for P5 and P8 on purpose, so the resolver has
# to fall back on signatures and handle matching for them
NO_PERSONAL_IN_CONTACTS = {"P5", "P8"}
CONTACTS = {"connections": [
    {"resourceName": f"people/{k}",
     "names": [{"displayName": v["name"]}],
     "emailAddresses": [{"value": v["work"], "type": "work"}] + (
         [] if k in NO_PERSONAL_IN_CONTACTS else
         [{"value": v["personal"], "type": "home"}])}
    for k, v in PEOPLE.items()]}
for fname, payload in (("slack_users.json", SLACK_USERS), ("linear_users.json", LINEAR_USERS),
                       ("contacts.json", CONTACTS)):
    with open(f"{RAW}/{fname}", "w") as f:
        json.dump(payload, f, indent=2)

write_jsonl(f"{RAW}/gmail_messages.jsonl", gmail_raw)
write_jsonl(f"{RAW}/calendar_events.jsonl", cal_raw)
write_jsonl(f"{RAW}/slack_messages.jsonl", slack_raw)
write_jsonl(f"{RAW}/linear_issues.jsonl", linear_raw)
write_jsonl(f"{RAW}/github_pulls.jsonl", EXPANSION["github"])
write_jsonl(f"{RAW}/notion_pages.jsonl", EXPANSION["notion"])
write_jsonl(f"{RAW}/crm_deals.jsonl", EXPANSION["crm"])
# like conversations.list: how a channel id is turned back into a name
SLACK_CHANNELS = {"channels": [{"id": k, "name": v.lstrip("#")} for k, v in CHANNELS.items()]
                  + [{"id": "C07FUND", "name": "fundraising"}, {"id": "C08HIRE", "name": "hiring"}]}
for fname, payload in (("slack_channels.json", SLACK_CHANNELS),
                       ("github_users.json", EXPANSION["github_users"]),
                       ("notion_users.json", EXPANSION["notion_users"]),
                       ("crm_contacts.json", EXPANSION["crm_contacts"])):
    with open(f"{RAW}/{fname}", "w") as f:
        json.dump(payload, f, indent=2)

# ============================================================
# NORMALIZED LAYER (what your context engine produces)
# ============================================================
norm = []
for g in _orig['gmail']:
    headers = {h["name"]: h["value"] for h in g["payload"]["headers"]}
    body = base64.urlsafe_b64decode(g["payload"]["body"]["data"] + "==").decode(errors="ignore")
    norm.append({
        "source":"gmail","source_id":g["id"],"thread_id":g["threadId"],
        "timestamp": datetime.fromtimestamp(int(g["internalDate"])/1000, tz=timezone.utc).isoformat(),
        "from":headers.get("From",""),"to":headers.get("To","").split(", "),
        "subject":headers.get("Subject",""),"body":body,
        "snippet":g["snippet"],
    })
for c in _orig['cal']:
    norm.append({
        "source":"calendar","source_id":c["id"],"timestamp":c["start"]["dateTime"],
        "title":c["summary"],"status":c["status"],
        "start":c["start"]["dateTime"],"end":c["end"]["dateTime"],
        "attendees":[a["email"] for a in c.get("attendees",[])],
        "organizer":c["organizer"]["email"],
        "description":c.get("description",""),
    })
slack_handles = {v["slack_id"]: v["slack_handle"] for v in PEOPLE.values()}
for s in _orig['slack']:
    norm.append({
        "source":"slack","source_id":s["ts"],"timestamp":datetime.fromtimestamp(float(s["ts"]), tz=timezone.utc).isoformat(),
        "user":slack_handles.get(s.get("user"), s.get("user","")),"text":s["text"],
        "thread_ts":s.get("thread_ts"),"edited":bool(s.get("edited")),"channel":s.get("channel_id",""),
    })
for l in _orig['linear']:
    norm.append({
        "source":"linear","source_id":l["id"],"issue_id":l["identifier"],
        "timestamp":l["updatedAt"],"title":l["title"],"description":l["description"],
        "state":l["state"]["name"],"assignee":l["assignee"]["name"] if l.get("assignee") else None,
        "priority":l.get("priority"),"labels":[n["name"] for n in l.get("labels",{}).get("nodes",[])],
        "created_at":l.get("createdAt"),
    })

write_jsonl(f"{NORM}/items.jsonl", norm)

# ============================================================
# ANSWER KEY
# ============================================================
answer_key = {
  "current_time": iso(CURRENT_TIME),
  "identity_map": PEOPLE,
  "shared_inbox": SHARED_INBOX,
  "raw_sources": {
    "gmail": {"file":"raw/gmail_messages.jsonl","shape":"Gmail API users.messages.get (format=full)",
              "note":"internalDate is epoch-ms string; body is base64url; headers are name/value pairs."},
    "calendar": {"file":"raw/calendar_events.jsonl","shape":"Google Calendar API events.list/events.get",
                 "note":"status includes cancelled/tentative/confirmed; attendees have responseStatus."},
    "slack": {"file":"raw/slack_messages.jsonl","shape":"Slack conversations.history",
              "note":"user is a U... ID; ts is a string with microseconds; edited is an object."},
    "linear": {"file":"raw/linear_issues.jsonl","shape":"Linear GraphQL issue query (per-snapshot)",
               "note":"Multiple records share the same identifier to simulate an audit export. A single GraphQL query returns one current state."},
  },
  "expansion": EXPANSION["answer_key"],
  "external_alt_emails": EXPANSION["alt_emails"],
  "required_cases": {
    "R3_identity": {
      "question": "What did Daniel Kim say about the billing migration?",
      "answer": "He asked Priya to push it a week, sent from his personal email dkim.work@gmail.com (Gmail thread thread_billing_001). Also mentioned in Slack #eng the same day.",
      "supporting_raw": ["gmail:thread_billing_001", "slack:#eng U05DANIEL message at t-4h3 ('billing migration is blocked on my side')"],
      "why_hard": "Daniel appears as daniel.kim@acmerobotics.com, dkim.work@gmail.com, @daniel, dkim. The email From header is his personal address; only the signature reveals it's Daniel."
    },
    "R4_reversal": {
      "question": "What is the current authentication decision for the v2 API?",
      "answer": "OAuth only. Reverted at T-1 by Rebecca Liu (Becky).",
      "supporting_raw": ["gmail:g4 (t-1)", "slack:U09BECKY message at t-1 (edited=true)", "linear:ACME-142 latest updatedAt t-1 state=Done"],
      "stale_answers": ["OAuth only (initial, t-9)", "OAuth + API keys (middle, t-7)"],
      "why_hard": "Three states exist across three tools. Only the latest updated_at / ts wins."
    },
    "R5_reschedule": {
      "question": "What time is the Weekly Product Sync today?",
      "answer": "16:00 UTC (rescheduled from Fri Mar 13; old calendar event status=cancelled).",
      "supporting_raw": ["gmail:m0", "slack:#general t-5", "calendar:confirmed event with note 'Rescheduled from Fri Mar 13'"],
      "why_hard": "Both calendar records exist. The cancelled one has status=cancelled and a description note."
    },
    "R6_duplicate": {
      "question": "What is the Q1 ship date?",
      "answer": "Mar 22 (corrected from Mar 20).",
      "supporting_raw": ["gmail:r2 (t-11)", "slack:#product t-11"],
      "stale_answers": ["Mar 20 (ACME-231 description; early Gmail thread)"],
      "why_hard": "Duplicate content across Gmail and Slack. Linear still says Mar 20."
    },
    "R7_unanswerable": {
      "question": "What is the exact revenue impact of the v2 API delay?",
      "answer": None,
      "note": "No financial figures anywhere in any raw source."
    }
  }
}
with open("data/answer_key.json","w") as f:
    json.dump(answer_key, f, indent=2)

# ============================================================
# SOURCES.md
# ============================================================
with open("data/SOURCES.md","w") as f:
    f.write("""# Data Sources & Shape Fidelity

## Real-world inspiration
- **Ohio Voter File / PPRL benchmarks** — identity matching across sources (R3).
- **LEDA (IETF mailing-list decision-dialogue corpus)** — quoted replies, decision threads (R4, R6).
- **UnSeenTimeQA / TempReason** — temporal grounding against a fixed reference time (R2).
- **UAEval4RAG** — unanswerable-question taxonomy (R7).

## API shape fidelity (for grader tool compatibility)

### Gmail
Shape follows `users.messages.get` with `format=full`: `id`, `threadId`, `labelIds`, `snippet`, `internalDate` (epoch-ms string), `payload.headers[]` (name/value pairs), `payload.body.data` (base64url) [citation:1][citation:14]. The `raw` RFC 2822 field is omitted for readability; a real ingestion adapter would use `format=raw` or `format=full` identically.

### Google Calendar
Shape follows `events.list` items: `id`, `status` (confirmed/tentative/cancelled), `summary`, `start`/`end` objects with `dateTime`+`timeZone`, `attendees[]` with `email`/`displayName`/`responseStatus`, `organizer`, `recurringEventId` [citation:2][citation:9]. Cancelled instances of recurring events are modeled (a real API returns them with `status=cancelled`).

### Slack
Shape follows `conversations.history`: `type`, `user` (a `U…` ID, not handle), `text`, `ts` (string with microseconds, e.g. `"1512085950.000216"`), `thread_ts`, `reactions[]`, `edited` object, `bot_id` [citation:3]. Channel IDs are opaque (`C01ENG`); a real ingestion adapter would resolve them via `conversations.info`.

### Linear
Shape follows the GraphQL `issue` query: `id`, `identifier`, `title`, `description`, `state { name }`, `assignee { id name }`, `priority`, `createdAt`, `updatedAt`, `labels { nodes { name } }` [citation:16]. **Important:** a single GraphQL query returns one current state. This dataset emits multiple records with the same `identifier` to simulate an **audit/snapshot export** (e.g., webhook history or repeated polling). Document this in your README; a production adapter would dedupe by `identifier` and keep the record with max `updatedAt`.


### GitHub, Notion, CRM (second layer, synthetic_data_expansion.py)
GitHub rows follow the REST pulls shape (`number`, `title`, `state`, `merged_at`, `requested_reviewers`, `user.login`) with PR comments as separate rows. Notion rows follow the pages shape (`properties.title`, `last_edited_time`, `last_edited_by`) with the page text flattened to blocks. CRM rows follow the HubSpot deals shape (`properties.dealname`, `dealstage`, `closedate`, `hs_lastmodifieddate`, contact associations) with notes as separate rows and contacts in `crm_contacts.json`. Gmail rows in this layer add multipart and html-only payloads, Cc headers, forwards, outlook-style quotes and bulk-mail headers. Calendar rows add other timezones, all-day dates, tentative status and outside attendees.
""")

counts = {"gmail":len(gmail_raw),"calendar":len(cal_raw),"slack":len(slack_raw),"linear":len(linear_raw),
          "github":len(EXPANSION["github"]),"notion":len(EXPANSION["notion"]),"crm":len(EXPANSION["crm"])}
counts["total"] = sum(counts.values())
print("Wrote", counts, "raw records +", len(norm), "normalized items")