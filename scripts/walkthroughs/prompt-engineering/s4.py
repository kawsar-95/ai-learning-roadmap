"""Prompt Engineering · 04 XML / Markdown structuring for reliable parsing: labeled sections give the model a shape and your code parts to pull out.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Prose     Body: "Free-form prose is fine for humans, but software needs structured output." "If the AI writes a wall of text ... your code has to parse English to pull out the answer."
  2 Labels    Body: "Labeled sections in Markdown or XML give the model a clear shape to follow and give your code clear parts to pull out. This is structured output."
  3 Anchoring Term "Anchoring": "The model pays more attention to content that has a label, such as a heading ## Summary."
  4 Regex     Term "Regex": "One regex can pull out a whole labeled section." "Labeled sections help the model and let your code pull out parts with one regex instead of parsing English."
  5 Audit     Body: "Labels also show which section failed when an output is wrong."
  6 Formats   Terms "Markdown sections" and "XML tags"; "Use Markdown for chat-facing output. Use XML tags for agents and tool pipelines."
  7 Remember  "Reuse the skeleton: role → context → task → output format → rules."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("model", "model", ("Model", "মডেল"), 100, 162),
    node("prose", "note", ("Free prose", "সাধারণ লেখা"), 300, 60),
    node("lab", "file", ("Labeled sections", "লেবেল দেওয়া সেকশন"), 300, 162),
    node("fail", "note", ("Failed section", "ব্যর্থ সেকশন"), 300, 268),
    node("rx", "tool", ("One regex", "একটা রেজেক্স"), 520, 162),
    node("code", "service", ("Your code", "আপনার কোড"), 680, 162),
    node("md", "file", ("Markdown", "Markdown"), 520, 60),
    node("xml", "file", ("XML tags", "XML ট্যাগ"), 520, 268),
]

METRICS = [
    ("Parsing", "পার্সিং"),
    ("Output", "আউটপুট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Prose", "লেখা"),
       ("Free prose is hard to read by code", "সাধারণ লেখা কোডের জন্য কঠিন"),
       [("Free-form prose is fine for humans, but software needs structured output.",
         "সাধারণ লেখা মানুষের জন্য ঠিক আছে, কিন্তু সফটওয়্যারের দরকার স্ট্রাকচার্ড আউটপুট।"),
        ("If the AI writes a wall of text, your code has to parse English to pull out the answer.",
         "AI লেখার দেয়াল লিখলে আপনার কোডকে ইংরেজি পার্স করে উত্তর তুলতে হয়।")],
       [sh("model", "hot"), sh("prose", "warn", ("wall of text", "লেখার দেয়াল")), sh("code", "dim")],
       [ln("model", "prose", "to", state="warn"), ln("prose", "code", "to", state="dim")],
       [("parse English", "ইংরেজি পার্স"), ("free prose", "সাধারণ লেখা")]),

    st(("Labels", "লেবেল"),
       ("Labeled sections give a shape", "লেবেল দেওয়া সেকশন কাঠামো দেয়"),
       [("Labeled sections in Markdown or XML give the model a clear shape to follow.",
         "Markdown বা XML-এর লেবেল দেওয়া সেকশন মডেলকে অনুসরণ করার মতো স্পষ্ট কাঠামো দেয়।"),
        ("They also give your code clear parts to pull out. This is structured output.",
         "আপনার কোডকেও তুলে আনার মতো স্পষ্ট অংশ দেয়। একেই বলে স্ট্রাকচার্ড আউটপুট।")],
       [sh("model", "hot"), sh("lab", "hot", ("clear parts", "স্পষ্ট অংশ")), sh("code", "hot")],
       [ln("model", "lab", "to", state="hot"), ln("lab", "code", "to", state="hot")],
       [("clear parts", "স্পষ্ট অংশ"), ("structured output", "স্ট্রাকচার্ড আউটপুট")]),

    st(("Anchoring", "অ্যাংকরিং"),
       ("Labels anchor the model", "লেবেল মডেলকে অ্যাংকর করে"),
       [("The model pays more attention to content that has a label, such as a heading ## Summary.",
         "লেবেল দেওয়া অংশে মডেল বেশি মনোযোগ দেয়, যেমন ## Summary হেডিং।")],
       [sh("model", "hot", ("more attention", "বেশি মনোযোগ")), sh("lab", "hot", ("## Summary", "## Summary"))],
       [ln("model", "lab", "to", state="hot")],
       [None, ("labeled", "লেবেল দেওয়া")]),

    st(("Regex", "রেজেক্স"),
       ("One regex pulls out a section", "একটা রেজেক্সেই সেকশন তোলা যায়"),
       [("A regex is a short pattern that finds matching text. One regex can pull out a whole labeled section.",
         "রেজেক্স মিলে যাওয়া লেখা খুঁজে বের করার একটা ছোট প্যাটার্ন। একটা রেজেক্সেই পুরো লেবেল দেওয়া সেকশন তোলা যায়।"),
        ("Your code does not need to parse English.",
         "আপনার কোডকে ইংরেজি বাক্য বিশ্লেষণ করতে হয় না।")],
       [sh("lab", "hot"), sh("rx", "hot", ("whole section", "পুরো সেকশন")), sh("code", "hot")],
       [ln("lab", "rx", "to", state="hot"), ln("rx", "code", "to", state="hot")],
       [("one regex", "একটা রেজেক্স"), ("labeled", "লেবেল দেওয়া")]),

    st(("Audit", "যাচাই"),
       ("Labels show which section failed", "লেবেল দেখায় কোন সেকশন ব্যর্থ"),
       [("Labels also show which section failed when an output is wrong.",
         "আউটপুট ভুল হলে লেবেল দেখে বোঝা যায় ঠিক কোন সেকশন ব্যর্থ হয়েছে।")],
       [sh("lab", "hot"), sh("fail", "warn", ("which one", "কোনটা"))],
       [ln("lab", "fail", "to", state="warn")],
       [None, ("labeled", "লেবেল দেওয়া")]),

    st(("Formats", "ফরম্যাট"),
       ("Two ways to label", "লেবেল দেওয়ার দুই উপায়"),
       [("Markdown sections are headings like ## Answer. They work for any model and are easy to read.",
         "Markdown সেকশন হলো ## Answer-এর মতো হেডিং। সব মডেলে কাজ করে আর পড়তে সহজ।"),
        ("XML tags open and close a block. The boundaries are stricter, and blocks can sit inside blocks.",
         "XML ট্যাগ একটা ব্লক খোলে ও বন্ধ করে। সীমানা বেশি কঠোর, আর ব্লকের ভেতরে ব্লক রাখা যায়।")],
       [sh("lab", "hot"), sh("md", "hot", ("chat-facing", "ব্যবহারকারীর দিকে")), sh("xml", "hot", ("agents, tool pipelines", "এজেন্ট, টুল পাইপলাইন"))],
       [ln("lab", "md", "to", state="hot"), ln("lab", "xml", "to", state="hot")],
       [None, ("Markdown or XML", "Markdown বা XML")],
       note=("tip", "Use Markdown for chat-facing output. Use XML tags for agents and tool pipelines.",
             "ব্যবহারকারীর দিকের আউটপুটে Markdown, আর এজেন্ট ও টুল পাইপলাইনে XML ট্যাগ ব্যবহার করুন।")),

    st(("Remember", "মনে রাখুন"),
       ("Remember: reuse the skeleton", "মনে রাখুন: কাঠামোটা বারবার ব্যবহার করুন"),
       [("Labeled sections help the model and let your code pull out parts with one regex instead of parsing English.",
         "লেবেল দেওয়া সেকশন মডেলকে সাহায্য করে, আর একটা রেজেক্সেই অংশ তোলা যায়, ইংরেজি বাক্য বিশ্লেষণ করতে হয় না।"),
        ("Reuse the skeleton: role → context → task → output format → rules.",
         "এই কাঠামো বারবার ব্যবহার করুন: রোল → কনটেক্সট → টাস্ক → আউটপুট ফরম্যাট → নিয়ম।")],
       [sh("model", "hot"), sh("lab", "hot", ("role → context → task", "রোল → কনটেক্সট → টাস্ক")), sh("rx", "hot"), sh("code", "hot")],
       [ln("model", "lab", "to", state="hot"), ln("lab", "rx", "to", state="hot"), ln("rx", "code", "to", state="hot")],
       [("one regex", "একটা রেজেক্স"), ("labeled", "লেবেল দেওয়া")],
       points=[("role → context → task → output format → rules", "রোল → কনটেক্সট → টাস্ক → আউটপুট ফরম্যাট → নিয়ম")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
