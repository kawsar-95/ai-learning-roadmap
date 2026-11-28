"""Prompt Engineering · 07 Output parsers & graceful failure handling: constrain the model, validate the output, then recover.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Garbage   Intro: "A model will sometimes give output your code does not expect. Good apps use graceful failure handling: they constrain the output, check it, and recover when it is wrong."
  2 Constrain Term "Structured outputs / JSON mode": "Structured outputs match your schema; plain JSON mode only gives valid JSON. Both can still fail on refusal or truncation." Table row "Constrain the model": "Always for production. The cheapest insurance."
  3 Validate  Terms "Validation", "JSON Schema", "Hallucinated value". Table row "Validate the output": "Even constrained output needs validation (wrong field, hallucinated value)." "Defence in depth."
  4 Recover   Callout: "When validation fails, retry with a stricter prompt, fall back to defaults, or tell the user you do not know." Term "Retry with backoff".
  5 Failures  Table "Common failure modes and how to handle them": Malformed JSON, Hallucinated field, Refusal, Truncation, Empty output, Inconsistent format, each with its defence.
  6 Null      Practice: "use null (a value that means nothing here) and a problems list. Then your code can see the gap and act. ... Your code must still validate the reply."
  7 eval      Danger box: "Never use eval() on model output. The model can be tricked into writing harmful code."
  8 Remember  Callout: "Use three layers: constrain the model, validate the output, then recover gracefully."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("model", "model", ("Model", "মডেল"), 110, 100),
    node("cons", "shield", ("Constrain the model", "মডেলকে কনস্ট্রেইন"), 380, 100),
    node("val", "shield", ("Validate the output", "আউটপুট ভ্যালিডেট"), 640, 100),
    node("rec", "service", ("Recover gracefully", "গ্রেসফুলি রিকভার"), 640, 250),
    node("bad", "note", ("Unexpected output", "অপ্রত্যাশিত আউটপুট"), 130, 250),
    node("fail", "note", ("Failure modes", "ব্যর্থতার ধরন"), 130, 250),
    node("inv", "file", ("Smudged invoice", "ঝাপসা ইনভয়েস"), 130, 250),
    node("code", "service", ("Your code", "আপনার কোড"), 380, 250),
    node("ev", "tool", ("eval()", "eval()"), 380, 250),
]

METRICS = [
    ("Constrain", "কনস্ট্রেইন"),
    ("Validate", "ভ্যালিডেট"),
    ("Recover", "রিকভার"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Garbage", "ব্যর্থতা"),
       ("The model will sometimes surprise your code", "মডেল মাঝে মাঝে আপনার কোডকে অবাক করবে"),
       [("A model will sometimes give output your code does not expect.",
         "মডেল মাঝে মাঝে এমন আউটপুট দেবে, যা আপনার কোড আশা করেনি।"),
        ("Good apps use graceful failure handling: they constrain the output, check it, and recover when it is wrong.",
         "ভালো অ্যাপ সুন্দরভাবে ব্যর্থতা সামলায়: আউটপুট বেঁধে দেয়, যাচাই করে, আর ভুল হলে ঠিক করে নেয়।")],
       [sh("model", "hot"), sh("bad", "warn"), sh("rec", "dim")],
       [ln("model", "bad", "to", state="warn")],
       [None, None, None]),

    st(("Constrain", "কনস্ট্রেইন"),
       ("Layer one: constrain the model", "প্রথম স্তর: মডেলকে কনস্ট্রেইন করুন"),
       [("Structured outputs match your schema; plain JSON mode only gives valid JSON.",
         "স্ট্রাকচার্ড আউটপুট স্কিমা মেনে চলে; সাধারণ JSON মোড শুধু বৈধ JSON দেয়।"),
        ("Both can still fail on refusal or truncation.",
         "রিফিউজাল বা কেটে যাওয়া উত্তরে দুটোই ব্যর্থ হতে পারে।")],
       [sh("model", "hot"), sh("cons", "hot"), sh("val", "dim"), sh("rec", "dim")],
       [ln("model", "cons", "to", state="hot")],
       [("Always for production", "প্রোডাকশনে সবসময়"), None, None],
       note=("tip", "Always for production. It is the cheapest insurance.",
             "প্রোডাকশনে সবসময়। এটাই সবচেয়ে সস্তা বীমা।")),

    st(("Validate", "ভ্যালিডেট"),
       ("Layer two: validate the output", "দ্বিতীয় স্তর: আউটপুট ভ্যালিডেট করুন"),
       [("Even constrained output needs validation. It can still have a wrong field or an invented value.",
         "কনস্ট্রেইন করা আউটপুটেও ভ্যালিডেশন লাগে। তাতে তবু ভুল ফিল্ড বা বানানো মান আসতে পারে।"),
        ("Validation is a runtime check, with a tool like Pydantic, Zod, or JSON Schema.",
         "ভ্যালিডেশন হলো রানটাইমের যাচাই, যেমন Pydantic, Zod বা JSON Schema দিয়ে।")],
       [sh("cons", "dim"), sh("val", "hot", ("Pydantic, Zod", "Pydantic, Zod")), sh("rec", "dim")],
       [ln("cons", "val", "to", state="hot")],
       [None, ("Defence in depth", "ডিফেন্স ইন ডেপথ"), None]),

    st(("Recover", "রিকভার"),
       ("Layer three: recover gracefully", "তৃতীয় স্তর: গ্রেসফুলি রিকভার"),
       [("When validation fails, retry with a stricter prompt, fall back to defaults, or tell the user you do not know.",
         "ভ্যালিডেশন ব্যর্থ হলে কড়া প্রম্পটে রিট্রাই করুন, ডিফল্টে ফিরুন, বা ইউজারকে জানান যে আপনি জানেন না।"),
        ("Retry with backoff means trying again, and waiting a little longer before each new try.",
         "ব্যাকঅফ-সহ রিট্রাই মানে আবার চেষ্টা করা, আর প্রতিবার নতুন চেষ্টার আগে একটু বেশি অপেক্ষা করা।")],
       [sh("val", "warn"), sh("rec", "hot", ("stricter retry", "কড়া রিট্রাই"))],
       [ln("val", "rec", "to", state="hot")],
       [None, None, ("When validation fails", "ভ্যালিডেশন ব্যর্থ হলে")]),

    st(("Failures", "ব্যর্থতা"),
       ("Common failure modes", "সাধারণ ব্যর্থতার ধরন"),
       [("Each way the model breaks has its own defence.",
         "মডেল যেভাবে ভাঙে, প্রতিটার নিজস্ব প্রতিরক্ষা আছে।")],
       [sh("fail", "warn"), sh("cons", "hot"), sh("val", "hot"), sh("rec", "hot")],
       [ln("fail", "cons", "to", state="warn")],
       [None, None, None],
       changes=[("+", "Malformed JSON: use structured outputs / JSON mode",
                 "ভুল JSON: স্ট্রাকচার্ড আউটপুট / JSON মোড ব্যবহার করুন"),
                ("+", "Hallucinated field: strict schema and business-rule validation",
                 "বানানো ফিল্ড: কড়া স্কিমা আর বিজনেস নিয়মের ভ্যালিডেশন"),
                ("+", "Refusal: detect the refusal string, return null and tell the UI",
                 "রিফিউজাল: রিফিউজাল স্ট্রিং শনাক্ত করে null ফেরত দিন এবং UI-কে জানান"),
                ("+", "Truncation: detect the finish reason, increase max_tokens",
                 "ট্রাঙ্কেশন: ফিনিশ রিজন দেখুন, max_tokens বাড়ান"),
                ("+", "Empty output: retry with backoff, eventually return \"I couldn't answer\"",
                 "খালি আউটপুট: ব্যাকঅফ-সহ রিট্রাই, শেষে \"I couldn't answer\""),
                ("+", "Inconsistent format: JSON Schema validation and retry with a stricter prompt",
                 "অসঙ্গত ফরম্যাট: JSON Schema ভ্যালিডেশন আর কড়া প্রম্পটে রিট্রাই")]),

    st(("Null", "null"),
       ("A safe way out: null and problems", "নিরাপদ বের হওয়ার পথ: null আর problems"),
       [("Give the model a safe way out: use null, a value that means nothing here, and a problems list.",
         "মডেলকে একটা নিরাপদ বের হওয়ার পথ দিন: null (যে ভ্যালুর মানে এখানে কিছু নেই) আর একটা problems তালিকা।"),
        ("Then your code can see the gap and act. Rules in the prompt help, but your code must still validate the reply.",
         "তখন আপনার কোড ফাঁকটা দেখে ঠিক কাজ করতে পারে। প্রম্পটের নিয়ম সাহায্য করে, কিন্তু আপনার কোডকে তবু উত্তর ভ্যালিডেট করতে হবে।")],
       [sh("inv", "hot"), sh("model", "hot", ("null", "null")), sh("code", "hot"), sh("val", "hot")],
       [ln("inv", "model", "to", state="hot"), ln("model", "val", "to", state="hot"), ln("val", "code", "to", state="hot")],
       [None, ("types and values", "টাইপ আর ভ্যালু"), None]),

    st(("eval", "eval"),
       ("Never eval() model output", "মডেলের আউটপুটে কখনো eval() নয়"),
       [("Never use eval() on model output.",
         "মডেলের আউটপুটে কখনো eval() চালাবেন না।"),
        ("The model can be tricked into writing harmful code.",
         "মডেলকে ফাঁকি দিয়ে ক্ষতিকর কোড লেখানো যায়।")],
       [sh("model", "warn"), sh("ev", "warn")],
       [ln("model", "ev", "to", state="warn")],
       [None, None, None],
       note=("warn", "Never use eval() on model output. Use a proper parser such as json.loads or Pydantic.",
             "মডেলের আউটপুটে কখনো eval() নয়। json.loads বা Pydantic-এর মতো সঠিক পার্সার ব্যবহার করুন।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Use three layers: constrain the model, validate the output, then recover gracefully.",
         "তিন স্তর ব্যবহার করুন: মডেলকে কনস্ট্রেইন করুন, আউটপুট ভ্যালিডেট করুন, তারপর সুন্দরভাবে রিকভার করুন।")],
       [sh("model"), sh("cons", "hot"), sh("val", "hot"), sh("rec", "hot")],
       [ln("model", "cons", "to"), ln("cons", "val", "to"), ln("val", "rec", "to")],
       [None, None, None],
       points=[("Even constrained output needs validation.",
                "কনস্ট্রেইন করা আউটপুটেও ভ্যালিডেশন লাগে।"),
               ("When validation fails, retry with a stricter prompt, fall back to defaults, or tell the user you do not know.",
                "ভ্যালিডেশন ব্যর্থ হলে কড়া প্রম্পটে রিট্রাই করুন, ডিফল্টে ফিরুন, বা ইউজারকে জানান যে আপনি জানেন না।"),
               ("Never use eval() on model output.",
                "মডেলের আউটপুটে কখনো eval() চালাবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
