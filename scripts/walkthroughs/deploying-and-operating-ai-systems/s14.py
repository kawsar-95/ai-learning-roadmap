"""Deploying and Operating AI Systems · 14 AIOps: an AI assistant that sorts alerts and logs, added read-only first, with its claims checked against evidence.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Alert      Body: "AIOps uses AI to help run IT systems: it sorts alerts and logs so engineers can find and fix problems faster." Table: "Too many alerts".
  2 Sort       Table, "With AI": "Learn which alerts usually fire together and show one incident"; "A model of what is normal for this hour and this weekday"; "A summary of what changed around the first error".
  3 Runbook    Table: "An assistant that reads the runbook, runs read-only checks and drafts the update". "Start read-only: let the assistant look and explain, not change anything."
  4 Evidence   Warning: "Give it the same evidence an engineer would use, and check its claim against a metric or a log line before anything is changed."
  5 Wrong fix  Warning: "A confident wrong fix is worse than none. A language model can invent a command or a cause."
  6 Approval   "Keep a human approval step for every change, such as a restart, a scale-up or a rollback." Layman's: "The engineer still decides what to do."
  7 Remember   The four "remember" points; "Keep a record of what happens during an incident, and review it afterwards." "Measure it: time to detect, time to resolve ..."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("sys", "server", ("System", "সিস্টেম"), 90, 160),
    node("sig", "chart", ("Alerts and logs", "অ্যালার্ট আর লগ"), 280, 160),
    node("ai", "model", ("Assistant", "অ্যাসিস্ট্যান্ট"), 480, 160),
    node("rb", "file", ("Runbook", "রানবুক"), 480, 50),
    node("check", "chart", ("Metric, log line", "মেট্রিক, লগ লাইন"), 650, 60),
    node("eng", "user", ("Engineer", "ইঞ্জিনিয়ার"), 670, 160),
    node("wrong", "note", ("Wrong fix", "ভুল সমাধান"), 660, 270),
    node("log", "file", ("Log of actions", "কাজের লগ"), 480, 270),
]

METRICS = [
    ("Time to detect", "ধরতে সময়"),
    ("Time to resolve", "সারাতে সময়"),
    ("Changes made", "পরিবর্তন"),
    ("Approval", "অনুমোদন"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Alerts", "অ্যালার্ট"),
       ("Too many alerts and logs", "অনেক অ্যালার্ট আর লগ"),
       [("AIOps uses AI to help run IT systems. It is AI used to operate software.",
         "AIOps IT সিস্টেম চালাতে AI-এর সাহায্য নেয়। এটা সফটওয়্যার চালাতে AI ব্যবহার।"),
        ("It sorts alerts and logs so engineers can find and fix problems faster.",
         "এটা অ্যালার্ট আর লগ বাছাই করে, যাতে ইঞ্জিনিয়ার দ্রুত সমস্যা ধরতে আর সারাতে পারে।")],
       [sh("sys", "warn", ("a problem", "একটা সমস্যা")), sh("sig", "hot", ("too many alerts", "অনেক অ্যালার্ট"))],
       [ln("sys", "sig", "to", state="warn")],
       [None, None, None, None]),

    st(("Sort", "বাছাই"),
       ("The assistant sorts them", "অ্যাসিস্ট্যান্ট বাছাই করে"),
       [("It learns which alerts usually fire together and shows one incident. It uses a model of what is normal for this hour and this weekday.",
         "কোন অ্যালার্ট সাধারণত একসাথে বাজে তা শেখে আর একটা ঘটনা দেখায়। এই ঘণ্টা আর এই বারে কী স্বাভাবিক, তার একটা মডেল ব্যবহার করে।"),
        ("For a huge log it gives a summary of what changed around the first error.",
         "বিশাল লগে প্রথম এররের আশপাশে কী বদলেছে তার সারাংশ দেয়।")],
       [sh("sig", "hot"), sh("ai", "hot", ("one", "একটা"))],
       [ln("sig", "ai", "to", state="hot")],
       [None, None, None, None]),

    st(("Runbook", "রানবুক"),
       ("Read-only: look and explain", "রিড-অনলি: দেখা আর ব্যাখ্যা"),
       [("At 3 a.m. the assistant reads the runbook, runs read-only checks and drafts the update.",
         "রাত তিনটায় অ্যাসিস্ট্যান্ট রানবুক পড়ে, রিড-অনলি চেক চালায় আর আপডেটের খসড়া লেখে।"),
        ("Start read-only: let it look and explain, not change anything.",
         "রিড-অনলি দিয়ে শুরু করুন: সে দেখবে আর ব্যাখ্যা করবে, কিছু বদলাবে না।")],
       [sh("rb", "hot"), sh("ai", "hot", ("looks and explains", "দেখে আর ব্যাখ্যা করে")), sh("sys", "dim", ("read-only", "রিড-অনলি"))],
       [ln("rb", "ai", "to", state="hot"), ln("ai", "sys", "to", state="dim")],
       [None, None, ("read-only", "রিড-অনলি"), None]),

    st(("Evidence", "প্রমাণ"),
       ("Check the claim against evidence", "দাবি প্রমাণের সাথে মেলান"),
       [("Give the assistant the same evidence an engineer would use.",
         "অ্যাসিস্ট্যান্টকে সেই প্রমাণই দিন যা একজন ইঞ্জিনিয়ার ব্যবহার করত।"),
        ("Check its claim against a metric or a log line before anything is changed.",
         "কিছু বদলানোর আগে তার দাবি মেট্রিক বা লগ লাইনের সাথে মিলিয়ে নিন।")],
       [sh("ai", "hot", ("a claim", "একটা দাবি")), sh("check", "hot", ("compare first", "আগে মেলান"))],
       [ln("ai", "check", "to", state="hot")],
       [None, None, None, None]),

    st(("Wrong fix", "ভুল সমাধান"),
       ("A confident wrong fix", "আত্মবিশ্বাসী ভুল সমাধান"),
       [("A confident wrong fix is worse than none.",
         "আত্মবিশ্বাসী ভুল সমাধান কোনো সমাধান না থাকার চেয়ে খারাপ।"),
        ("A language model can invent a command or a cause.",
         "একটা ভাষা মডেল কমান্ড বা কারণ বানিয়ে ফেলতে পারে।")],
       [sh("ai", "warn", ("invented cause", "বানানো কারণ")), sh("check", "warn", ("does not match", "মেলে না")), sh("wrong", "warn")],
       [ln("ai", "wrong", "to", state="warn"), ln("check", "wrong", "to", state="warn")],
       [None, None, None, None]),

    st(("Approval", "অনুমোদন"),
       ("A human approves every change", "প্রতিটি পরিবর্তনে মানুষের অনুমোদন"),
       [("Keep a human approval step for every change, such as a restart, a scale-up or a rollback.",
         "প্রতিটি পরিবর্তনে মানুষের অনুমোদন রাখুন, যেমন রিস্টার্ট, স্কেল-আপ বা রোলব্যাক।"),
        ("The engineer still decides what to do.",
         "কী করতে হবে, তা ইঞ্জিনিয়ারই ঠিক করে।")],
       [sh("ai", "hot", ("suggests", "পরামর্শ")), sh("eng", "hot")],
       [ln("ai", "eng", "to", state="hot")],
       [None, None, None, ("human approval", "মানুষের অনুমোদন")]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Keep a record of what happens during an incident, and review it afterwards. Measure time to detect, time to resolve, and how often its suggestion was right.",
         "ঘটনার সময় কী হয় তার রেকর্ড রাখুন, আর পরে রিভিউ করুন। ধরতে সময়, সারাতে সময়, আর তার পরামর্শ কতবার ঠিক ছিল তা মাপুন।")],
       [sh("ai", "hot"), sh("eng", "hot"), sh("log", "hot", ("every action and evidence", "প্রতিটি কাজ আর প্রমাণ"))],
       [ln("ai", "log", "to", state="hot"), ln("eng", "log", "to", state="hot")],
       [("time to detect", "ধরতে সময়"), ("time to resolve", "সারাতে সময়"), None, ("every change", "প্রতিটি পরিবর্তনে")],
       points=[("Start read-only: let the assistant look and explain, not change anything.", "রিড-অনলি দিয়ে শুরু করুন: অ্যাসিস্ট্যান্ট দেখবে আর ব্যাখ্যা করবে, কিছু বদলাবে না।"),
               ("Keep a human approval step for every change, such as a restart, a scale-up or a rollback.", "প্রতিটি পরিবর্তনে মানুষের অনুমোদন রাখুন, যেমন রিস্টার্ট, স্কেল-আপ বা রোলব্যাক।"),
               ("Log every action and its evidence, and review the log after each incident.", "প্রতিটি কাজ আর তার প্রমাণ লগ করুন, আর প্রতিটি ঘটনার পরে লগ রিভিউ করুন।"),
               ("A confident wrong fix is worse than none. Check its claim against a metric or a log line.", "আত্মবিশ্বাসী ভুল সমাধান কোনো সমাধান না থাকার চেয়ে খারাপ। দাবি মেট্রিক বা লগ লাইনের সাথে মিলিয়ে নিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
