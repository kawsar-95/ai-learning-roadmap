"""LLM Fundamentals · 06 Structured outputs & JSON mode: three levels, each stricter, from JSON mode to a typed object in your code.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Free text  Start here: "Instead of free text, you can make a model answer in a fixed shape, such as JSON with the fields you named. Then your code can use the answer directly, with no guessing."
  2 JSON mode  Table: "The model is told to reply in JSON. It is the loosest of the three levels."
  3 Schema     Table: "A description of the exact shape you want: which fields, and what type each one is, such as text or a number."
  4 Blocked    Table: "At each step, the model is blocked from any token that would break the schema, so a normally finished output fits."
  5 Typed      Table: "Your code turns the answer into a typed object, such as an object of a Pydantic class in Python, and reads the fields directly."
  6 Still      "Schema-constrained output that finishes normally follows the schema, but you still handle refusals and incomplete answers." "The first request with a new schema is slower, but that costs far less than the checking it saves."
  7 Remember   "Use structured outputs whenever you can."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("free", "note", ("Free text", "খোলামেলা লেখা"), 200, 50),
    node("json", "file", ("1. JSON mode", "১. JSON মোড"), 200, 150),
    node("sc", "shield", ("2. Schema-constrained decoding", "২. স্কিমা-কনস্ট্রেইনড ডিকোডিং"), 200, 250),
    node("typed", "tool", ("3. Typed parsing", "৩. টাইপড পার্সিং"), 200, 350),
    node("code", "service", ("Your code", "আপনার কোড"), 620, 200),
    node("handle", "lock", ("Refusals, incomplete answers", "প্রত্যাখ্যান, অসম্পূর্ণ উত্তর"), 600, 330),
]

METRICS = [
    ("Level", "স্তর"),
    ("Shape", "আকার"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Free text", "খোলামেলা লেখা"),
       ("A fixed shape, not free text", "খোলামেলা লেখা নয়, নির্দিষ্ট আকার"),
       [("Instead of free text, you can make a model answer in a fixed shape, such as JSON with the fields you named.",
         "খোলামেলা লেখার বদলে মডেলকে একটা নির্দিষ্ট আকারে উত্তর দিতে বলা যায়, যেমন আপনার বলে দেওয়া ফিল্ডসহ JSON।"),
        ("Then your code can use the answer directly, with no guessing.",
         "তখন আপনার কোড কোনো আন্দাজ ছাড়াই সরাসরি উত্তরটা ব্যবহার করতে পারে।")],
       [sh("free", "dim"), sh("json", "hot", ("fields you named", "আপনার বলে দেওয়া ফিল্ড")), sh("code", "hot", ("no guessing", "আন্দাজ নেই"))],
       [ln("json", "code", "to", state="hot")],
       [None, None]),

    st(("JSON mode", "JSON মোড"),
       ("Level 1: JSON mode", "স্তর ১: JSON মোড"),
       [("In JSON mode the model is told to reply in JSON.",
         "JSON মোডে মডেলকে JSON-এ উত্তর দিতে বলা হয়।"),
        ("It is the loosest of the three levels.",
         "তিনটি স্তরের মধ্যে এটাই সবচেয়ে ঢিলেঢালা।")],
       [sh("free", "dim"), sh("json", "hot", ("loosest", "সবচেয়ে ঢিলেঢালা")), sh("sc", "dim"), sh("typed", "dim")],
       [ln("free", "json", "to", state="hot")],
       [(("JSON mode"), ("JSON মোড")), (("valid JSON, shape not enforced"), ("বৈধ JSON, আকার বাধ্যতামূলক নয়"))]),

    st(("Schema", "স্কিমা"),
       ("A schema names the shape", "স্কিমা আকারের নাম দেয়"),
       [("A schema describes the exact shape you want: which fields, and what type each one is, such as text or a number.",
         "স্কিমা আপনি ঠিক কোন আকার চান তার বর্ণনা: কোন কোন ফিল্ড, আর প্রতিটি কোন টাইপের, যেমন লেখা বা সংখ্যা।")],
       [sh("json", "dim"), sh("sc", "hot", ("which fields, which types", "কোন ফিল্ড, কোন টাইপ")), sh("typed", "dim")],
       [ln("json", "sc", "to", state="dim")],
       [None, None]),

    st(("Blocked", "ব্লক"),
       ("Level 2: tokens that break the schema are blocked", "স্তর ২: স্কিমা ভাঙা টোকেন ব্লক"),
       [("In schema-constrained decoding, the model is blocked at each step from any token that would break the schema.",
         "স্কিমা-কনস্ট্রেইনড ডিকোডিংয়ে প্রতিটি ধাপে মডেলকে এমন কোনো টোকেন বাছতে দেওয়া হয় না যা স্কিমা ভাঙবে।"),
        ("So a normally finished output fits the schema.",
         "তাই স্বাভাবিকভাবে শেষ হওয়া আউটপুট স্কিমায় খাপ খায়।")],
       [sh("json", "dim"), sh("sc", "hot", ("blocks tokens that break it", "ভাঙা টোকেন ব্লক করে")), sh("code", "hot")],
       [ln("sc", "code", "to", state="hot")],
       [(("schema-constrained decoding"), ("স্কিমা-কনস্ট্রেইনড ডিকোডিং")), (("output follows the schema"), ("আউটপুট স্কিমা মেনে চলে"))]),

    st(("Typed", "টাইপড"),
       ("Level 3: typed parsing", "স্তর ৩: টাইপড পার্সিং"),
       [("Your code turns the answer into a typed object, such as an object of a Pydantic class in Python.",
         "আপনার কোড উত্তরটাকে একটি টাইপড অবজেক্টে বদলায়, যেমন Python-এ একটি Pydantic ক্লাসের অবজেক্ট।"),
        ("Then it reads the fields directly.",
         "তারপর ফিল্ডগুলো সরাসরি পড়ে।")],
       [sh("sc", "dim"), sh("typed", "hot", ("typed object", "টাইপড অবজেক্ট")), sh("code", "hot", ("reads fields directly", "ফিল্ড সরাসরি পড়ে"))],
       [ln("sc", "typed", "to", state="dim"), ln("typed", "code", "to", state="hot")],
       [(("typed parsing"), ("টাইপড পার্সিং")), (("typed object in your code"), ("কোডে টাইপড অবজেক্ট"))]),

    st(("Still", "তবুও"),
       ("You still handle some cases", "কিছু ক্ষেত্র তবুও আপনাকে সামলাতে হয়"),
       [("Schema-constrained output that finishes normally follows the schema, but you still handle refusals and incomplete answers.",
         "স্কিমা-কনস্ট্রেইনড আউটপুট স্বাভাবিকভাবে শেষ হলে স্কিমা মেনে চলে, তবে প্রত্যাখ্যান (refusal) ও অসম্পূর্ণ উত্তর আপনাকেই সামলাতে হবে।"),
        ("The first request with a new schema is slower, but that costs far less than the checking it saves.",
         "নতুন স্কিমায় প্রথম রিকোয়েস্টে সামান্য বাড়তি সময় লাগে, কিন্তু যত যাচাই বাঁচে তার তুলনায় তা অনেক কম।")],
       [sh("sc", "hot"), sh("code", "hot"), sh("handle", "warn")],
       [ln("sc", "code", "to", state="hot"), ln("code", "handle", "to", state="warn")],
       [None, None],
       note=("warn", "Handle refusals and incomplete answers in your code.",
             "প্রত্যাখ্যান ও অসম্পূর্ণ উত্তর আপনার কোডে সামলান।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Use structured outputs whenever you can.",
         "যখনই পারেন, স্ট্রাকচার্ড আউটপুট ব্যবহার করুন।")],
       [sh("json"), sh("sc"), sh("typed"), sh("code")],
       [ln("json", "sc", "to"), ln("sc", "typed", "to"), ln("typed", "code", "to")],
       [None, None],
       points=[("Use structured outputs whenever you can.",
                "যখনই পারেন, স্ট্রাকচার্ড আউটপুট ব্যবহার করুন।"),
               ("You still handle refusals and incomplete answers.",
                "প্রত্যাখ্যান ও অসম্পূর্ণ উত্তর আপনাকেই সামলাতে হবে।"),
               ("The first request with a new schema is slower, but that costs far less than the checking it saves.",
                "নতুন স্কিমায় প্রথম রিকোয়েস্টে সামান্য বাড়তি সময় লাগে, কিন্তু যত যাচাই বাঁচে তার তুলনায় তা অনেক কম।")]),
]

WALK = walk(760, 400, NODES, METRICS, CAPTION, STEPS)
