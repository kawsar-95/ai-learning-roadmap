"""Part 6 · 06 Human-in-the-loop checkpoints: a risk ladder, a wait-for-human primitive, and the UI that is the hard part.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Ladder    Start here: "Most production agents need at least one step where a person approves an action. The riskier the action, the more human approval it needs."; body, the risk ladder: "Read-only: search, fetch, query. Auto-approve." "Local-write: edit a file the agent owns. Auto-approve with a soft cap."
  2 Per call  Body: "External-write: send an email, post to Slack. Approve per call." "Money: refund, charge, payout. Approve per call, plus a daily cap."
  3 Two       Body: "Destructive: delete a record. Two-person rule."; Two-person rule ("Two people must agree before a destructive action, such as deleting a record, can happen.").
  4 Checkpoint Body: "Every durable framework exposes a "wait for human" primitive. In LangGraph it's interrupt; in Temporal it's wait_for_signal; in Restate it's await call().ack()."; the code: interrupt({to, subject, body}); if not approved, "User rejected email send."; else the email is sent.
  5 UI        Warning callout: "The hard part is the UI, not the protocol. ... The framework gives you a clean "interrupt" primitive, but you still have to build the inbox, the diff view, the approve/reject buttons, the audit log, the SLA (service-level agreement), the mobile notifications. Budget at least 30% of agent project time for the human-facing surface."
  6 No answer Body, "Asynchronous approvals": "Soft timeout + default reject: if no response in 24 hours, the workflow terminates." "Soft timeout + default approve with rollback: if no response, the action proceeds but is logged and reversible." "Hard timeout + escalate: at 24 hours, route to a backup approver."
  7 Remember  Risk ladder ("The higher the step, the stricter the approval."); and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("agent", "model", ("Agent", "এজেন্ট"), 110, 162),
    node("read", "file", ("Read-only", "শুধু পড়া"), 380, 75),
    node("local", "file", ("Local write", "লোকাল রাইট"), 380, 250),
    node("ext", "service", ("External write", "বাইরে লেখা"), 380, 75),
    node("money", "service", ("Money", "টাকা"), 380, 250),
    node("del", "database", ("Destructive", "ধ্বংসাত্মক"), 380, 162),
    node("human", "user", ("Person", "মানুষ"), 650, 162),
    node("human2", "user", ("Second person", "দ্বিতীয় মানুষ"), 650, 250),
    node("gate", "lock", ("Checkpoint", "চেকপয়েন্ট"), 380, 162),
    node("ui", "browser", ("Approval UI", "অনুমোদনের UI"), 380, 250),
    node("backup", "user", ("Backup approver", "ব্যাকআপ অ্যাপ্রুভার"), 650, 250),
]

METRICS = [
    ("Approval", "অনুমোদন"),
    ("UI budget", "UI-এর বাজেট"),
    ("Timeout", "টাইমআউট"),
]

CAPTION = (
    "The higher the step on the risk ladder, the stricter the approval.",
    "ঝুঁকির সিঁড়িতে ধাপ যত ওপরে, অনুমোদনের নিয়ম তত কড়া।",
)

STEPS = [
    st(("Ladder", "সিঁড়ি"),
       ("A risk ladder", "ঝুঁকির সিঁড়ি"),
       [("Most production agents need at least one step where a person approves an action. The riskier the action, the more human approval it needs.",
         "বেশিরভাগ প্রোডাকশন এজেন্টের অন্তত একটি ধাপ লাগে, যেখানে একজন মানুষ কাজটি অনুমোদন করে। কাজ যত ঝুঁকিপূর্ণ, তত বেশি মানুষের অনুমোদন দরকার।"),
        ("At the bottom of the ladder, read-only actions (search, fetch, query) are auto-approved. A local write, such as editing a file the agent owns, is auto-approved with a soft cap.",
         "সিঁড়ির নিচে শুধু পড়ার কাজ (সার্চ, ফেচ, কুয়েরি) অটো-অ্যাপ্রুভ হয়। নিজের ফাইল এডিটের মতো লোকাল রাইট অটো-অ্যাপ্রুভ হয় নরম সীমা দিয়ে।")],
       [sh("agent", "hot"), sh("read", "hot", ("auto-approve", "অটো-অ্যাপ্রুভ")), sh("local", "hot", ("auto-approve, soft cap", "অটো-অ্যাপ্রুভ, নরম সীমা"))],
       [ln("agent", "read", "to", state="hot"), ln("agent", "local", "to", state="hot")],
       [("none", "লাগে না"), None, None]),

    st(("Per call", "প্রতি কল"),
       ("Approve each call", "প্রতিটি কলে অনুমোদন"),
       [("An external write, such as sending an email or posting to Slack, needs approval for each call.",
         "বাইরের কিছুতে লেখা, যেমন ইমেইল পাঠানো বা Slack-এ পোস্ট করা, প্রতিটি কলে অনুমোদন লাগে।"),
        ("Money actions, such as a refund, a charge or a payout, need approval for each call, plus a daily cap.",
         "টাকার কাজ, যেমন রিফান্ড, চার্জ বা পেআউট, প্রতিটি কলে অনুমোদন লাগে, সঙ্গে একটি দৈনিক সীমা।")],
       [sh("agent", "hot"), sh("ext", "hot", ("approve per call", "প্রতি কলে অনুমোদন")), sh("money", "hot", ("per call, daily cap", "প্রতি কলে, দৈনিক সীমা")),
        sh("human", "hot", ("approves", "অনুমোদন দেয়"))],
       [ln("agent", "ext", "to", state="hot"), ln("agent", "money", "to", state="hot"), ln("ext", "human", "to", state="hot"), ln("money", "human", "to", state="hot")],
       [("each call", "প্রতি কলে"), None, None]),

    st(("Two people", "দুজন"),
       ("Destructive: two people", "ধ্বংসাত্মক: দুজন মানুষ"),
       [("Deleting a record is destructive. It needs the two-person rule: two people must agree before it can happen.",
         "রেকর্ড মুছে ফেলা ধ্বংসাত্মক কাজ। এতে টু-পারসন রুল লাগে: কাজটি হওয়ার আগে দুজন মানুষকে রাজি হতে হয়।")],
       [sh("agent", "hot"), sh("del", "warn", ("two-person rule", "টু-পারসন রুল")), sh("human", "hot", ("agrees", "রাজি হয়")), sh("human2", "hot", ("must agree too", "তাকেও রাজি হতে হয়"))],
       [ln("agent", "del", "to", state="hot"), ln("del", "human", "to", state="hot"), ln("del", "human2", "to", state="hot")],
       [("two people", "দুজন মানুষ"), None, None]),

    st(("Checkpoint", "চেকপয়েন্ট"),
       ("The checkpoint primitive", "চেকপয়েন্ট প্রিমিটিভ"),
       [("Every durable framework has a “wait for human” primitive. In LangGraph it is <code>interrupt</code>, in Temporal <code>wait_for_signal</code>, and in Restate <code>await call().ack()</code>.",
         "প্রতিটি ডিউরেবল ফ্রেমওয়ার্কে “মানুষের জন্য অপেক্ষা” করার একটি প্রিমিটিভ থাকে। LangGraph-এ এটি <code>interrupt</code>, Temporal-এ <code>wait_for_signal</code>, আর Restate-এ <code>await call().ack()</code>।"),
        ("In the section's example, the email step calls <code>interrupt</code> with the recipient, subject and body. If the answer is not approved, it returns “User rejected email send.” Otherwise it sends the email.",
         "সেকশনের উদাহরণে ইমেইল ধাপ প্রাপক, বিষয় আর বডিসহ <code>interrupt</code> ডাকে। অনুমোদন না এলে সে “User rejected email send.” ফেরত দেয়। অনুমোদন এলে ইমেইল পাঠায়।")],
       [sh("agent", "hot"), sh("gate", "hot", ("waits for a human", "মানুষের জন্য অপেক্ষা")), sh("human", "hot", ("approves or rejects", "অনুমোদন বা বাতিল"))],
       [ln("agent", "gate", "to", state="hot"), ln("gate", "human", "both", state="hot")],
       [None, None, None]),

    st(("UI", "UI"),
       ("The hard part is the UI", "কঠিন অংশ UI"),
       [("The framework gives you a clean interrupt, but you still have to build the inbox, the diff view, the approve and reject buttons, the audit log, the SLA and the mobile notifications.",
         "ফ্রেমওয়ার্ক একটি পরিষ্কার interrupt দেয়, কিন্তু ইনবক্স, ডিফ ভিউ, অ্যাপ্রুভ আর রিজেক্ট বোতাম, অডিট লগ, SLA আর মোবাইল নোটিফিকেশন আপনাকেই বানাতে হবে।")],
       [sh("gate", "hot"), sh("ui", "warn", ("inbox, diff, buttons", "ইনবক্স, ডিফ, বোতাম")), sh("human", "hot")],
       [ln("gate", "ui", "to", state="hot"), ln("ui", "human", "to", state="hot")],
       [None, ("30%+", "৩০%+"), None],
       note=("warn",
             "Most teams underestimate the approval surface. Budget at least 30% of agent project time for the human-facing surface.",
             "বেশিরভাগ টিম অনুমোদনের এই অংশের কাজ কম ধরে। মানুষের সামনের অংশের জন্য এজেন্ট প্রজেক্টের অন্তত ৩০% সময় রাখুন।")),

    st(("No answer", "সাড়া নেই"),
       ("If no one answers", "কেউ সাড়া না দিলে"),
       [("When the human cannot respond right away, the workflow needs a timeout. With a soft timeout and default reject, the workflow ends if there is no answer in 24 hours.",
         "মানুষ সঙ্গে সঙ্গে সাড়া দিতে না পারলে ওয়ার্কফ্লোর টাইমআউট লাগে। নরম টাইমআউট আর ডিফল্ট রিজেক্টে ২৪ ঘণ্টায় সাড়া না এলে ওয়ার্কফ্লো শেষ হয়ে যায়।"),
        ("A soft timeout with default approve lets the action go ahead, logged and reversible. A hard timeout escalates: at 24 hours the request goes to a backup approver.",
         "নরম টাইমআউট আর ডিফল্ট অ্যাপ্রুভে কাজটি এগিয়ে যায়, লগ হয় আর ফেরানো যায়। কড়া টাইমআউটে এসকেলেট হয়: ২৪ ঘণ্টায় অনুরোধ যায় ব্যাকআপ অ্যাপ্রুভারের কাছে।")],
       [sh("gate", "hot"), sh("human", "warn", ("no answer", "সাড়া নেই")), sh("backup", "hot", ("after 24 hours", "২৪ ঘণ্টা পর"))],
       [ln("gate", "human", "to", state="warn"), ln("gate", "backup", "to", state="hot")],
       [None, None, ("24 hours", "২৪ ঘণ্টা")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("The higher the step on the risk ladder, the stricter the approval.",
         "ঝুঁকির সিঁড়িতে ধাপ যত ওপরে, অনুমোদনের নিয়ম তত কড়া।")],
       [sh("agent"), sh("read"), sh("del"), sh("money"), sh("human")],
       [ln("agent", "read", "to"), ln("agent", "del", "to"), ln("agent", "money", "to"), ln("del", "human", "to"), ln("money", "human", "to")],
       [None, None, None],
       points=[("Read-only actions are auto-approved. Money actions need approval per call plus a daily cap.",
                "শুধু পড়ার কাজ অটো-অ্যাপ্রুভ হয়। টাকার কাজে প্রতি কলে অনুমোদন আর দৈনিক সীমা লাগে।"),
               ("Deleting a record needs the two-person rule.",
                "রেকর্ড মুছতে টু-পারসন রুল লাগে।"),
               ("The hard part is the UI, not the protocol. Budget at least 30% of project time for it.",
                "কঠিন অংশ UI, প্রটোকল নয়। এর জন্য প্রজেক্ট সময়ের অন্তত ৩০% রাখুন।"),
               ("If no human answers, you can reject, approve with rollback, or escalate to a backup approver.",
                "কোনো মানুষ সাড়া না দিলে বাতিল করা, রোলব্যাকসহ অনুমোদন করা, বা ব্যাকআপ অ্যাপ্রুভারের কাছে পাঠানো যায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
