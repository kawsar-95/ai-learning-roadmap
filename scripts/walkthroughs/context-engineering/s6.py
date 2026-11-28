"""Part 5 · 06 Tool result truncation strategies: keep tool results useful but bounded, so one call cannot fill the context window.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Problem    Body: "One tool call can return 100K tokens and fill your whole context window. Truncation keeps tool results useful but limited in size." Definition "Tool result": "The data a tool sends back to the model after a call, such as a file or database rows."
  2 Head/tail  Definitions "Truncation" ("Cutting a long result down to a smaller size, and keeping the parts that matter.") and "Head/tail" ("Keeping the first K and last K tokens, and dropping the middle.").
  3 Pages      Definitions "Pagination" and "Cursor". Point: "Never return the whole result at once. Return a small slice plus a cursor, and let the agent ask for more."
  4 Structure  Point: "For database results, return the schema, the first 10 rows, and the count."
  5 Just in time  Definition "Just-in-time": "Saving the data outside the prompt, giving a reference, and fetching it only when needed."
  6 Reserve    Point: "Reserve room for tool results in your token budget."
  7 Boundaries Point: "Do not cut code or JSON in the middle. Stop at function ends, closing braces, or line endings."
  8 Remember   Point: "Never return the whole result at once. Return a small slice plus a cursor, and let the agent ask for more." plus the points above.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("tool", "tool", ("Tool", "টুল"), 110, 162),
    node("res", "file", ("Tool result", "টুল রেজাল্ট"), 380, 162),
    node("win", "model", ("Context window", "কনটেক্সট উইন্ডো"), 640, 162),
    node("head", "file", ("First K", "প্রথম K"), 380, 60),
    node("mid", "file", ("Middle", "মাঝখান"), 380, 162),
    node("tail", "file", ("Last K", "শেষ K"), 380, 264),
    node("slice", "file", ("Small slice", "ছোট স্লাইস"), 380, 162),
    node("cursor", "key", ("Cursor", "কার্সর"), 380, 264),
    node("schema", "file", ("Schema", "স্কিমা"), 380, 60),
    node("rows", "database", ("First 10 rows", "প্রথম ১০ সারি"), 380, 162),
    node("count", "chart", ("Count", "মোট সংখ্যা"), 380, 264),
    node("store", "storage", ("Outside the prompt", "প্রম্পটের বাইরে"), 380, 162),
]

METRICS = [
    ("Result", "ফলাফল"),
    ("Window", "উইন্ডো"),
    ("Next", "পরের অংশ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Problem", "সমস্যা"),
       ("One tool call can fill the window", "একটি টুল কল পুরো উইন্ডো ভরতে পারে"),
       [("A tool result is the data a tool sends back to the model after a call, such as a file or database rows.",
         "টুল রেজাল্ট হলো কল করার পর টুল মডেলকে যে ডেটা ফেরত পাঠায়, যেমন ফাইল বা ডেটাবেসের সারি।"),
        ("One tool call can return 100K tokens and fill your whole context window.",
         "একটি টুল কল ১০০K টোকেন ফেরত দিয়ে পুরো কনটেক্সট উইন্ডো ভরে ফেলতে পারে।")],
       [sh("tool", "hot"), sh("res", "warn", ("100K tokens", "১০০K টোকেন")), sh("win", "warn", ("whole window", "পুরো উইন্ডো"))],
       [ln("tool", "res", "to", state="warn"), ln("res", "win", "to", state="warn")],
       [("100K tokens", "১০০K টোকেন"), ("whole window", "পুরো উইন্ডো"), None]),

    st(("Head/tail", "হেড/টেইল"),
       ("Truncation: keep the parts that matter", "ট্রাঙ্কেশন: দরকারি অংশ রাখা"),
       [("Truncation cuts a long result down to a smaller size, and keeps the parts that matter.",
         "ট্রাঙ্কেশন লম্বা ফলাফল ছোট করে কেটে নেয়, আর দরকারি অংশ রাখে।"),
        ("Head/tail keeps the first K and last K tokens, and drops the middle.",
         "হেড/টেইল শুরুর K আর শেষের K টোকেন রাখে, মাঝখান বাদ দেয়।")],
       [sh("res", "hot", x=110, y=162), sh("head", "hot"), sh("mid", "dim", ("dropped", "বাদ")), sh("tail", "hot"), sh("win", "hot")],
       [ln("res", "head", "to", state="hot"), ln("res", "tail", "to", state="hot"),
        ln("head", "win", "to", state="hot"), ln("tail", "win", "to", state="hot")],
       [("first K, last K", "প্রথম K, শেষ K"), None, None]),

    st(("Pages", "পেজ"),
       ("Pagination: a small slice plus a cursor", "পেজিনেশন: ছোট স্লাইস আর কার্সর"),
       [("Pagination returns results in small slices, so the agent asks for the next slice only if needed.",
         "পেজিনেশন ফলাফল ছোট ছোট অংশে দেয়, যাতে এজেন্ট দরকার হলেই পরের অংশ চায়।"),
        ("A cursor is a marker the tool returns to show where the next slice starts.",
         "কার্সর হলো টুলের ফেরত দেওয়া চিহ্ন, যা দেখায় পরের অংশ কোথা থেকে শুরু।")],
       [sh("tool", "hot"), sh("slice", "hot"), sh("cursor", "hot"), sh("win", "hot")],
       [ln("tool", "slice", "to", state="hot"), ln("tool", "cursor", "to", state="hot"), ln("slice", "win", "to", state="hot")],
       [("small slice", "ছোট স্লাইস"), None, ("cursor", "কার্সর")],
       note=("tip", "Never return the whole result at once. Let the agent ask for more.",
             "পুরো ফলাফল একসাথে দেবেন না। এজেন্ট দরকারে আরও চাইবে।")),

    st(("Structure", "কাঠামো"),
       ("Database results: schema, rows, count", "ডেটাবেসের ফলাফল: স্কিমা, সারি, সংখ্যা"),
       [("For database results, return the schema, the first 10 rows, and the count.",
         "ডেটাবেসের ফলাফলে স্কিমা, প্রথম ১০ সারি আর মোট সংখ্যা দিন।")],
       [sh("tool", "hot"), sh("schema", "hot"), sh("rows", "hot"), sh("count", "hot"), sh("win", "hot")],
       [ln("tool", "schema", "to", state="hot"), ln("tool", "rows", "to", state="hot"), ln("tool", "count", "to", state="hot"),
        ln("schema", "win", "to", state="hot"), ln("rows", "win", "to", state="hot"), ln("count", "win", "to", state="hot")],
       [None, None, None]),

    st(("Just in time", "জাস্ট-ইন-টাইম"),
       ("Just-in-time: save it, give a reference", "জাস্ট-ইন-টাইম: রেখে দিন, রেফারেন্স দিন"),
       [("Just-in-time means saving the data outside the prompt, giving a reference, and fetching it only when needed.",
         "জাস্ট-ইন-টাইম মানে ডেটা প্রম্পটের বাইরে রেখে একটি রেফারেন্স দেওয়া, আর দরকার হলেই আনা।")],
       [sh("tool", "hot"), sh("store", "hot", ("fetch when needed", "দরকারে আনা")), sh("win", "hot")],
       [ln("tool", "store", "to", state="hot"), ln("store", "win", "to", state="hot")],
       [None, None, None]),

    st(("Reserve", "রিজার্ভ"),
       ("Reserve room for tool results", "টুল রেজাল্টের জন্য জায়গা রাখুন"),
       [("Reserve room for tool results in your token budget.",
         "টোকেন বাজেটে টুল রেজাল্টের জন্য জায়গা আগেই রাখুন।")],
       [sh("tool", "hot"), sh("res", "hot"), sh("win", "hot", ("room reserved", "জায়গা রাখা"))],
       [ln("tool", "res", "to", state="hot"), ln("res", "win", "to", state="hot")],
       [None, ("room reserved", "জায়গা রাখা"), None]),

    st(("Boundaries", "সীমানা"),
       ("Do not cut code or JSON in the middle", "কোড বা JSON মাঝপথে কাটবেন না"),
       [("Do not cut code or JSON in the middle.",
         "কোড বা JSON মাঝপথে কাটবেন না।"),
        ("Stop at function ends, closing braces, or line endings.",
         "ফাংশনের শেষ, বন্ধনী বন্ধ হওয়া বা লাইনের শেষে থামুন।")],
       [sh("res", "warn", ("not in the middle", "মাঝপথে নয়")), sh("win", "dim")],
       [ln("res", "win", "to", state="warn")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Never return the whole result at once. Return a small slice plus a cursor, and let the agent ask for more.",
         "পুরো ফলাফল একসাথে দেবেন না। ছোট একটি স্লাইস আর কার্সর দিন, এজেন্ট দরকারে আরও চাইবে।")],
       [sh("tool"), sh("slice"), sh("cursor"), sh("win")],
       [ln("tool", "slice", "to"), ln("tool", "cursor", "to"), ln("slice", "win", "to")],
       [None, None, None],
       points=[("For database results, return the schema, the first 10 rows, and the count.",
                "ডেটাবেসের ফলাফলে স্কিমা, প্রথম ১০ সারি আর মোট সংখ্যা দিন।"),
               ("Reserve room for tool results in your token budget.",
                "টোকেন বাজেটে টুল রেজাল্টের জন্য জায়গা আগেই রাখুন।"),
               ("Do not cut code or JSON in the middle.",
                "কোড বা JSON মাঝপথে কাটবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
