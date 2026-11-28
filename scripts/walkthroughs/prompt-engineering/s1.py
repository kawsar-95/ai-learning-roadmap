"""Prompt Engineering · 01 System vs User vs Assistant message design: what goes in each role, and where important text should sit.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Roles      Start here: "Every message you send to a chat model has a role: system, user, or assistant." Glossary "Role": "A tag on each message that says who is speaking".
  2 System     Glossary "System message": "The app's fixed rules for every call: how the model should act, the output format, and safety limits. Think of it as the app's instruction sheet."
  3 User       Glossary "User message": "The real task for this turn: the request, the data to work on, and any retrieved text. Be specific and give all inputs."
  4 Assistant  Glossary "Assistant message": "The model's own earlier replies. In a multi-turn chat, you send this history again each turn."
  5 Placement  Start here: "Hard rules, like the output format and what the model must refuse, go in system. Soft style wishes go in user, next to the request."
  6 Crowded    Start here: "A very long, crowded system message can give worse results than a short, focused one."
  7 Middle     Glossary "Lost in the middle": "Models notice information in the middle of a long text less reliably than information at the start or end."
  8 Remember   The four remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("sys", "file", ("System message", "সিস্টেম মেসেজ"), 190, 60),
    node("usr", "user", ("User message", "ইউজার মেসেজ"), 190, 160),
    node("asst", "model", ("Assistant message", "অ্যাসিস্ট্যান্ট মেসেজ"), 190, 260),
    node("hard", "shield", ("Hard rules", "কঠিন নিয়ম"), 570, 60),
    node("soft", "note", ("Soft style wishes", "নরম স্টাইলের পছন্দ"), 570, 160),
    node("start", "note", ("Start", "শুরু"), 130, 160),
    node("mid", "note", ("Middle", "মাঝখান"), 380, 160),
    node("end", "note", ("End", "শেষ"), 630, 160),
]

METRICS = [
    ("Role", "রোল"),
    ("Holds", "যা থাকে"),
    ("Placement", "বসানো"),
]

CAPTION = (
    "Illustrative: the labels are the section's own words.",
    "উদাহরণমাত্র: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Roles", "রোল"),
       ("Every message has a role", "প্রতিটি মেসেজের একটা রোল আছে"),
       [("Every message you send to a chat model has a role: system, user, or assistant.",
         "চ্যাট মডেলে পাঠানো প্রতিটি মেসেজের একটা রোল থাকে: system, user বা assistant।"),
        ("A role is a tag that says who is speaking.",
         "রোল হলো মেসেজে লাগানো ট্যাগ, যা বলে কে কথা বলছে।")],
       [sh("sys", "hot"), sh("usr", "hot"), sh("asst", "hot")],
       [ln("sys", "usr", "to", state="hot"), ln("usr", "asst", "to", state="hot")],
       [("system, user, assistant", "system, user, assistant"), None, None]),

    st(("System", "সিস্টেম"),
       ("System: the fixed rules", "সিস্টেম: স্থির নিয়ম"),
       [("The system message holds the app's fixed rules for every call: how the model should act, the output format, and safety limits.",
         "সিস্টেম মেসেজে থাকে প্রতিটি কলের জন্য অ্যাপের স্থির নিয়ম: মডেল কীভাবে আচরণ করবে, আউটপুট ফরম্যাট, সেফটি সীমা।"),
        ("Think of it as the app's instruction sheet.",
         "এটা অ্যাপের নির্দেশিকার মতো।")],
       [sh("sys", "hot", ("true for every call", "প্রতিটি কলে যা সত্যি")), sh("usr", "dim"), sh("asst", "dim")],
       [ln("sys", "usr", "to", state="dim"), ln("usr", "asst", "to", state="dim")],
       [("system", "system"), ("rules for every call", "প্রতিটি কলের নিয়ম"), None]),

    st(("User", "ইউজার"),
       ("User: the task for this turn", "ইউজার: এই টার্নের কাজ"),
       [("The user message is the real task for this turn: the request, the data to work on, and any retrieved text.",
         "ইউজার মেসেজ হলো এই টার্নের আসল কাজ: অনুরোধ, কাজ করার ডেটা আর খুঁজে আনা লেখা।"),
        ("Be specific and give all inputs.",
         "স্পষ্ট হতে হবে, দরকারি সব ইনপুট দিতে হবে।")],
       [sh("sys", "dim"), sh("usr", "hot", ("request and data", "অনুরোধ আর ডেটা")), sh("asst", "dim")],
       [ln("sys", "usr", "to", state="dim"), ln("usr", "asst", "to", state="dim")],
       [("user", "user"), ("request, data, retrieved text", "অনুরোধ, ডেটা, খুঁজে আনা লেখা"), None]),

    st(("Assistant", "অ্যাসিস্ট্যান্ট"),
       ("Assistant: the earlier replies", "অ্যাসিস্ট্যান্ট: আগের উত্তর"),
       [("The assistant message is the model's own earlier reply.",
         "অ্যাসিস্ট্যান্ট মেসেজ হলো মডেলের নিজের আগের উত্তর।"),
        ("In a multi-turn chat, you send this history again each turn.",
         "মাল্টি-টার্ন চ্যাটে এই ইতিহাস প্রতি টার্নে আবার পাঠাতে হয়।")],
       [sh("sys", "dim"), sh("usr", "dim"), sh("asst", "hot", ("history, sent again", "ইতিহাস, আবার পাঠানো"))],
       [ln("sys", "usr", "to", state="dim"), ln("usr", "asst", "to", state="dim")],
       [("assistant", "assistant"), ("the model's earlier replies", "মডেলের আগের উত্তর"), None]),

    st(("Placement", "বসানো"),
       ("Hard rules in system, style in user", "কঠিন নিয়ম সিস্টেমে, স্টাইল ইউজারে"),
       [("Hard rules, like the output format and what the model must refuse, go in system.",
         "কঠিন নিয়ম, যেমন আউটপুট ফরম্যাট আর মডেল কী প্রত্যাখ্যান করবে, থাকবে সিস্টেমে।"),
        ("Soft style wishes go in user, next to the request.",
         "নরম স্টাইলের পছন্দ থাকবে ইউজার মেসেজে, অনুরোধের পাশেই।")],
       [sh("hard", "hot"), sh("sys", "hot"), sh("soft", "hot"), sh("usr", "hot")],
       [ln("hard", "sys", "to", state="hot"), ln("soft", "usr", "to", state="hot")],
       [None, None, ("hard in system, soft in user", "কঠিন সিস্টেমে, নরম ইউজারে")]),

    st(("Crowded", "ঠাসা"),
       ("A crowded system message", "ঠাসা সিস্টেম মেসেজ"),
       [("A very long, crowded system message can give worse results than a short, focused one.",
         "খুব লম্বা, ঠাসা সিস্টেম মেসেজ ছোট ও ফোকাসড মেসেজের চেয়ে খারাপ ফল দিতে পারে।")],
       [sh("sys", "warn", ("crowded", "ঠাসা")), sh("usr", "dim"), sh("asst", "dim")],
       [ln("sys", "usr", "to", state="dim"), ln("usr", "asst", "to", state="dim")],
       [None, None, ("short and focused", "ছোট ও ফোকাসড")],
       note=("warn", "Dumping every wish into the system message leaves the model unable to prioritise.",
             "সব ইচ্ছা সিস্টেম মেসেজে ঢোকালে মডেল অগ্রাধিকার ঠিক করতে পারে না।")),

    st(("Middle", "মাঝখান"),
       ("Lost in the middle", "লস্ট ইন দ্য মিডল"),
       [("Models notice information in the middle of a long text less reliably than information at the start or end.",
         "লম্বা লেখার মাঝখানের তথ্য মডেল শুরু বা শেষের তথ্যের চেয়ে কম নির্ভরযোগ্যভাবে খেয়াল করে।")],
       [sh("start", "hot", ("noticed", "খেয়াল করে")), sh("mid", "warn", ("less reliably", "কম নির্ভরযোগ্যভাবে")), sh("end", "hot", ("noticed", "খেয়াল করে"))],
       [ln("start", "mid", "to", state="dim"), ln("mid", "end", "to", state="dim")],
       [None, None, ("not in the middle", "মাঝখানে নয়")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Put your most important instructions at the beginning or end, not in the middle.",
         "সবচেয়ে জরুরি নির্দেশ শুরুতে বা শেষে রাখুন, মাঝখানে নয়।")],
       [sh("start", "hot"), sh("mid", "dim"), sh("end", "hot")],
       [ln("start", "mid", "to", state="dim"), ln("mid", "end", "to", state="dim")],
       [None, None, ("beginning or end", "শুরুতে বা শেষে")],
       points=[("Put what is true for every call in the system message. Put the specific request and its data in the user message.",
                "প্রতিটি কলে যা সত্যি, তা সিস্টেম মেসেজে রাখুন। নির্দিষ্ট অনুরোধ আর তার ডেটা রাখুন ইউজার মেসেজে।"),
               ("Hard rules, like the output format and what the model must refuse, go in system. Soft style wishes go in user, next to the request.",
                "কঠিন নিয়ম, যেমন আউটপুট ফরম্যাট আর মডেল কী প্রত্যাখ্যান করবে, থাকবে সিস্টেমে। নরম স্টাইলের পছন্দ থাকবে ইউজার মেসেজে, অনুরোধের পাশেই।"),
               ("A very long, crowded system message can give worse results than a short, focused one.",
                "খুব লম্বা, ঠাসা সিস্টেম মেসেজ ছোট ও ফোকাসড মেসেজের চেয়ে খারাপ ফল দিতে পারে।"),
               ("Put your most important instructions at the beginning or end, not in the middle.",
                "সবচেয়ে জরুরি নির্দেশ শুরুতে বা শেষে রাখুন, মাঝখানে নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
