"""Deploying and operating AI systems · 04 Python and YAML for pipelines: separate environments, pinned versions, and YAML that breaks quietly.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Glue      Layman's: "Python is the all-purpose tool that ties the pieces of an AI system together: it calls the model, runs the tests, moves data around. YAML is the settings sheet that most deployment tools read."
  2 Venv      Body: "Install a project's packages into its own virtual environment, so two projects do not fight over versions."
  3 Lock      Body: "Pin the versions in a lock file, so a build next month installs what you installed today. A newer tool, uv, does the same job faster and writes a lock file."
  4 Spaces    YAML rules: "Structure comes from indentation with spaces. Tabs are not allowed. A mapping is key: value. A list item starts with - ."
  5 Quote     YAML rule: "Quote a string that could be read as something else, such as "no", "on" or "1.10". ... many tools still follow YAML 1.1, where unquoted no, yes, on and off are booleans."
  6 Anchors   YAML rules: "Anchors and aliases (&name, *name) reuse a block. Keep them rare, because they make a file hard to read. Comments start with #. Use them to say why a setting has its value."
  7 Lint      Warning: "Indentation is the syntax. One misplaced space moves a key under a different parent, and the file still parses. Run a linter such as yamllint, and read what the tool actually loaded."
  8 Remember  The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("py", "tool", ("Python", "Python"), 110, 162),
    node("model", "model", ("Model", "মডেল"), 380, 60),
    node("tests", "tool", ("Tests", "টেস্ট"), 380, 162),
    node("yaml", "file", ("YAML settings", "YAML সেটিংস"), 380, 262),
    node("dep", "service", ("Deployment tool", "ডিপ্লয়মেন্ট টুল"), 650, 262),
    node("pa", "service", ("Project", "প্রজেক্ট"), 110, 70),
    node("pb", "service", ("Other project", "অন্য প্রজেক্ট"), 110, 254),
    node("va", "storage", ("Virtual environment", "ভার্চুয়াল এনভায়রনমেন্ট"), 480, 70),
    node("vb", "storage", ("Virtual environment", "ভার্চুয়াল এনভায়রনমেন্ট"), 480, 254),
    node("lock", "file", ("Lock file", "লক ফাইল"), 650, 162),
    node("uv", "tool", ("uv", "uv"), 110, 162),
    node("lint", "shield", ("yamllint", "yamllint"), 380, 162),
]

METRICS = [
    ("Habit", "অভ্যাস"),
    ("Checked by", "যাচাই করে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Glue", "জোড়া"),
       ("Python ties, YAML configures", "Python জোড়ে, YAML কনফিগ করে"),
       [("Python ties the pieces of an AI system together: it calls the model, runs the tests and moves data around.",
         "Python AI সিস্টেমের অংশগুলো জোড়া লাগায়: মডেল ডাকে, টেস্ট চালায়, ডেটা সরায়।"),
        ("YAML is the settings sheet that most deployment tools read.",
         "YAML হলো সেটিংস শিট, যা বেশিরভাগ ডিপ্লয়মেন্ট টুল পড়ে।")],
       [sh("py", "hot"), sh("model", "hot"), sh("tests", "hot"), sh("yaml", "hot"), sh("dep", "hot")],
       [ln("py", "model", "to", state="hot"), ln("py", "tests", "to", state="hot"), ln("yaml", "dep", "to", state="hot")],
       [None, None]),

    st(("Venv", "ভার্চুয়াল এনভায়রনমেন্ট"),
       ("One environment per project", "প্রতি প্রজেক্টে একটি এনভায়রনমেন্ট"),
       [("Install a project's packages into its own virtual environment.",
         "প্রতিটি প্রজেক্টের প্যাকেজ নিজের ভার্চুয়াল এনভায়রনমেন্টে বসান।"),
        ("Then two projects do not fight over versions.",
         "তাহলে দুই প্রজেক্টের ভার্সন মেশে না।")],
       [sh("pa", "hot"), sh("va", "hot", ("its own packages", "নিজের প্যাকেজ")), sh("pb", "hot"), sh("vb", "hot", ("its own packages", "নিজের প্যাকেজ"))],
       [ln("pa", "va", "to", state="hot"), ln("pb", "vb", "to", state="hot")],
       [("own virtual environment", "আলাদা ভার্চুয়াল এনভায়রনমেন্ট"), None]),

    st(("Lock", "লক"),
       ("Pin versions in a lock file", "লক ফাইলে ভার্সন পিন"),
       [("Pin the versions in a lock file, so a build next month installs what you installed today.",
         "ভার্সন লক ফাইলে পিন করুন, তাই এক মাস পরের বিল্ডেও আজকের জিনিসই ইনস্টল হয়।"),
        ("A newer tool, uv, does the same job as pip and venv, but faster, and writes a lock file.",
         "uv একটি নতুন টুল, যা pip আর venv-এর কাজই আরও দ্রুত করে এবং একটি লক ফাইল লেখে।")],
       [sh("uv", "hot", ("faster", "আরও দ্রুত"), x=150, y=162), sh("lock", "hot", ("exact versions", "নির্দিষ্ট ভার্সন"))],
       [ln("uv", "lock", "to", state="hot")],
       [("pin versions in a lock file", "লক ফাইলে ভার্সন পিন"), None]),

    st(("Spaces", "স্পেস"),
       ("YAML is indentation", "YAML মানে ইন্ডেন্টেশন"),
       [("In YAML, structure comes from indentation with spaces. Tabs are not allowed.",
         "YAML-এ কাঠামো আসে স্পেস দিয়ে ইন্ডেন্টেশন থেকে। ট্যাব চলে না।"),
        ("A mapping is <code>key: value</code>. A list item starts with <code>- </code>.",
         "ম্যাপিং হলো <code>key: value</code>। লিস্টের আইটেম শুরু হয় <code>- </code> দিয়ে।")],
       [sh("yaml", "hot", ("spaces, not tabs", "স্পেস, ট্যাব নয়"), x=380, y=162), sh("dep", "dim", x=650, y=162)],
       [ln("yaml", "dep", "to", state="dim")],
       [("indent with spaces", "স্পেস দিয়ে ইন্ডেন্ট"), None]),

    st(("Quote", "কোটেশন"),
       ("Quote what could be misread", "ভুল পড়া হতে পারে এমন মান কোট করুন"),
       [("Quote a string that could be read as something else, such as <code>\"no\"</code>, <code>\"on\"</code> or <code>\"1.10\"</code>.",
         "যে স্ট্রিং অন্যভাবে পড়া হতে পারে তা কোটেশনে রাখুন, যেমন <code>\"no\"</code>, <code>\"on\"</code> বা <code>\"1.10\"</code>।"),
        ("Many tools still follow YAML 1.1, where unquoted no, yes, on and off are booleans.",
         "অনেক টুল এখনও YAML 1.1 মানে, যেখানে কোটেশন ছাড়া no, yes, on আর off বুলিয়ান।")],
       [sh("yaml", "hot", ("quote it", "কোটেশনে রাখুন"), x=150, y=162), sh("dep", "warn", ("may read a boolean", "বুলিয়ান পড়তে পারে"), x=610, y=162)],
       [ln("yaml", "dep", "to", state="warn")],
       [("quote the value", "মান কোটেশনে"), None]),

    st(("Anchors", "অ্যাংকর"),
       ("Anchors, aliases and comments", "অ্যাংকর, অ্যালিয়াস আর মন্তব্য"),
       [("Anchors and aliases (<code>&amp;name</code>, <code>*name</code>) reuse a block. Keep them rare, because they make a file hard to read.",
         "অ্যাংকর আর অ্যালিয়াস (<code>&amp;name</code>, <code>*name</code>) একটি ব্লক আবার ব্যবহার করে। কম ব্যবহার করুন, কারণ ফাইল পড়া কঠিন হয়ে যায়।"),
        ("Comments start with <code>#</code>. Use them to say why a setting has its value.",
         "মন্তব্য শুরু হয় <code>#</code> দিয়ে। কোনো সেটিংয়ের মান কেন তা বলতে এগুলো ব্যবহার করুন।")],
       [sh("yaml", "hot", ("reuse a block, rarely", "ব্লক আবার ব্যবহার, কম"), x=380, y=162)],
       [],
       [("keep anchors rare", "অ্যাংকর কম রাখুন"), None]),

    st(("Lint", "লিন্ট"),
       ("One space can move a key", "একটা স্পেসই কী সরিয়ে দিতে পারে"),
       [("Indentation is the syntax. One misplaced space moves a key under a different parent, and the file still parses.",
         "ইন্ডেন্টেশনই সিনট্যাক্স। একটা ভুল জায়গার স্পেস কোনো কী অন্য প্যারেন্টের নিচে সরিয়ে দেয়, তবু ফাইল পার্স হয়।"),
        ("Run a linter such as yamllint, and read what the tool actually loaded.",
         "yamllint-এর মতো লিন্টার চালান, আর দেখুন টুল আসলে কী লোড করেছে।")],
       [sh("yaml", "warn", ("still parses", "তবু পার্স হয়"), x=130, y=162), sh("lint", "hot", ("flags mistakes", "ভুল ধরিয়ে দেয়"), x=380, y=162), sh("dep", "hot", ("what it loaded", "যা লোড করেছে"), x=650, y=162)],
       [ln("yaml", "lint", "to", state="hot"), ln("lint", "dep", "to", state="hot")],
       [None, ("run a linter", "লিন্টার চালান")],
       note=("warn", "A linter is a checker that reads your YAML file and flags mistakes.",
             "লিন্টার এমন চেকার, যা আপনার YAML ফাইল পড়ে ভুল ধরিয়ে দেয়।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Give each project its own packages, and let a checker read your settings before the real tool does.",
         "প্রতিটি প্রজেক্টকে আলাদা প্যাকেজ দিন, আর আসল টুলের আগে একটা চেকারকে সেটিংস পড়তে দিন।")],
       [sh("va", "hot", x=140, y=162), sh("lock", "hot", x=380, y=162), sh("lint", "hot", x=650, y=162)],
       [],
       [None, None],
       points=[("Install each project's packages in its own virtual environment, and pin versions in a lock file.",
                "প্রতিটি প্রজেক্টের প্যাকেজ আলাদা ভার্চুয়াল এনভায়রনমেন্টে বসান, আর ভার্সন লক ফাইলে পিন করুন।"),
               ("YAML uses spaces for indentation. Tabs are not allowed.",
                "YAML-এ ইন্ডেন্টেশন হয় স্পেস দিয়ে। ট্যাব চলে না।"),
               ("Quote values that could be misread: <code>1.10</code> becomes a number, and in YAML 1.1 no and on are booleans.",
                "যে মান ভুলভাবে পড়া হতে পারে তা কোটেশনে রাখুন: <code>1.10</code> সংখ্যা হয়ে যায়, আর YAML 1.1-এ no ও on বুলিয়ান।"),
               ("One misplaced space can move a key, yet the file parses; run a linter and check what the tool loaded.",
                "একটা ভুল জায়গার স্পেস কোনো কী সরিয়ে দিতে পারে, তবু ফাইল পার্স হয়; লিন্টার চালান আর দেখুন টুল আসলে কী লোড করেছে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
