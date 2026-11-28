"""Tool use: schema design, parallel calls, API wrappers and result formatting: how the model picks a tool, and how its result goes back as prompt content.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Tool      Body: "A model can only write text until you give it tools, ways to call an API, run code, or read a file." Term "Tool": "A function the model is allowed to call".
  2 Describe  "A tool is a JSON Schema ... plus a short description that the LLM reads before deciding to call it." "Write each tool description to say what it does, when to use it, and what it returns."
  3 Schema    "Use a tight schema with clear types and enums. Avoid any." Term "Enum": a short fixed list of allowed values; the model must pick one. "the model hallucinates less when the schema is tight."
  4 Wrapper   "Every internal API becomes a tool: wrap each endpoint with a function that (a) describes its purpose in one sentence, (b) accepts a typed input, (c) returns either the result or an {error, retryable} envelope."
  5 Parallel  "Make independent tool calls in one turn so they run at the same time." "total wait is the slowest call, not the sum." Example: weather in Tokyo and the exchange rate.
  6 Result    "Tool output is prompt content: trim it, format it for reading, add a summary when the result is not obvious." "A 10,000-row SQL result will blow your context window. Return the top N, summarise the rest."
  7 Too many  "OpenAI suggests keeping fewer than about 20 tools available at once; many tools can make it harder for the model to pick the right one." "split into sub-agents by domain, use a router, or defer tools with tool search."
  8 Remember  The five points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ইউজার"), 70, 160),
    node("model", "model", ("Model", "মডেল"), 240, 160),
    node("tw", "tool", ("Weather, Tokyo", "টোকিওর আবহাওয়া"), 450, 60),
    node("t1", "tool", ("search_documents", "search_documents"), 450, 160),
    node("tx", "tool", ("Exchange rate", "এক্সচেঞ্জ রেট"), 450, 260),
    node("svc", "service", ("Your API", "আপনার API"), 660, 160),
    node("res", "note", ("Tool result", "টুলের ফলাফল"), 660, 260),
]

METRICS = [
    ("Tools in prompt", "প্রম্পটে টুল"),
    ("Total wait", "মোট অপেক্ষা"),
    ("Result", "ফলাফল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Tool", "টুল"),
       ("A tool lets the model act", "টুল পেলে মডেল কাজ করতে পারে"),
       [("A model can only write text until you give it tools: ways to call an API, run code, or read a file.",
         "টুল না দিলে মডেল শুধু লেখা তৈরি করতে পারে। টুল পেলে সে API কল করতে, কোড চালাতে বা ফাইল পড়তে পারে।"),
        ("A tool is a function the model is allowed to call.",
         "টুল হলো এমন ফাংশন, যা মডেল কল করতে পারে।")],
       [sh("user", "hot"), sh("model", "hot"), sh("t1", "hot")],
       [ln("user", "model", "to", state="hot"), ln("model", "t1", "to", state="hot")],
       [None, None, None]),

    st(("Describe", "বর্ণনা"),
       ("The description is what the model reads", "মডেল যা পড়ে, সেটাই ডেসক্রিপশন"),
       [("A tool is a JSON Schema plus a short description that the model reads before deciding to call it.",
         "টুল হলো JSON Schema আর একটি ছোট ডেসক্রিপশন, যা মডেল কল করার আগে পড়ে।"),
        ("Write each description to say what it does, when to use it, and what it returns.",
         "প্রতিটি টুলের ডেসক্রিপশনে লিখুন সে কী করে, কখন ব্যবহার করবেন আর কী ফেরত দেয়।")],
       [sh("model", "hot"), sh("t1", "hot")],
       [ln("model", "t1", "to", state="hot")],
       [None, None, None]),

    st(("Schema", "স্কিমা"),
       ("Keep the schema tight", "স্কিমা আঁটসাঁট রাখুন"),
       [("Use a tight schema with clear types and enums. Avoid any.",
         "স্পষ্ট টাইপ আর এনাম দিয়ে স্কিমা আঁটসাঁট রাখুন। any এড়িয়ে চলুন।"),
        ("An enum is a short fixed list of allowed values, and the model must pick one. The model hallucinates less when the schema is tight.",
         "এনাম হলো অনুমোদিত মানের ছোট নির্দিষ্ট তালিকা, মডেলকে তার একটি বাছতে হয়। স্কিমা আঁটসাঁট হলে মডেল কম ভুল বানায়।")],
       [sh("model", "hot"), sh("t1", "hot")],
       [ln("model", "t1", "to", state="hot")],
       [None, None, None]),

    st(("Wrapper", "র‍্যাপার"),
       ("Wrap each API as a tool", "প্রতিটি API-কে টুল বানান"),
       [("Every internal API becomes a tool: wrap each endpoint with a function.",
         "প্রতিটি ইন্টারনাল API হয়ে যায় একটি টুল: প্রতিটি এন্ডপয়েন্ট একটি ফাংশনে মুড়ে দিন।"),
        ("It describes its purpose in one sentence, accepts a typed input, and returns the result or an {error, retryable} envelope.",
         "সে এক বাক্যে উদ্দেশ্য বর্ণনা করে, টাইপ করা ইনপুট নেয়, আর ফলাফল অথবা {error, retryable} এনভেলপ ফেরত দেয়।")],
       [sh("t1", "hot"), sh("svc", "hot"), sh("res", "hot")],
       [ln("t1", "svc", "to", state="hot"), ln("svc", "res", "to", state="hot")],
       [None, None, ("result or error", "ফলাফল বা এরর")]),

    st(("Parallel", "প্যারালাল"),
       ("Independent calls in one turn", "স্বাধীন কল এক টার্নে"),
       [("Make independent tool calls in one turn, so they run at the same time.",
         "একে অপরের ওপর নির্ভর করে না এমন টুল কল এক টার্নে দিন, যাতে সেগুলো একসাথে চলে।"),
        ("The total wait is the slowest call, not the sum.",
         "মোট অপেক্ষা হলো সবচেয়ে ধীর কলের সময়, সবগুলোর যোগফল নয়।")],
       [sh("model", "hot"), sh("tw", "hot"), sh("tx", "hot")],
       [ln("model", "tw", "to", state="hot"), ln("model", "tx", "to", state="hot")],
       [None, ("slowest call, not the sum", "সবচেয়ে ধীর কল, যোগফল নয়"), None]),

    st(("Result", "ফলাফল"),
       ("The result is prompt content", "ফলাফল প্রম্পটেরই অংশ"),
       [("Tool output is prompt content: the model re-reads it as part of its next turn.",
         "টুলের আউটপুট প্রম্পটেরই অংশ: মডেল পরের টার্নে সেটা আবার পড়ে।"),
        ("Trim it, format it for reading, and add a summary when the result is not obvious.",
         "ছাঁটুন, পড়ার মতো ফরম্যাট করুন, আর ফলাফল অস্পষ্ট হলে সারমর্ম যোগ করুন।")],
       [sh("model", "hot"), sh("res", "hot")],
       [ln("res", "model", "to", state="hot")],
       [None, None, ("trim, then summarise", "ছাঁটুন, তারপর সারমর্ম")],
       note=("warn", "A 10,000-row SQL result will blow your context window. Return the top N, summarise the rest.",
             "১০,০০০ রো-এর SQL ফলাফল কনটেক্সট উইন্ডো উড়িয়ে দেবে। শীর্ষ N ফেরত দিন, বাকিটা সারমর্ম করুন।")),

    st(("Too many", "অনেক টুল"),
       ("Too many tools make choosing harder", "অনেক টুলে বাছা কঠিন হয়"),
       [("OpenAI suggests keeping fewer than about 20 tools available at once.",
         "OpenAI পরামর্শ দেয় একসাথে প্রায় ২০-এর কম টুল রাখতে।"),
        ("Many tools can make it harder for the model to pick the right one.",
         "অনেক টুল থাকলে মডেলের ঠিক টুল বাছা কঠিন হতে পারে।")],
       [sh("model", "warn"), sh("tw", "warn"), sh("t1", "warn"), sh("tx", "warn")],
       [ln("model", "tw", "to", state="warn"), ln("model", "t1", "to", state="warn"), ln("model", "tx", "to", state="warn")],
       [("fewer than about 20", "প্রায় ২০-এর কম"), None, None],
       note=("tip", "Split into sub-agents by domain, use a router, or defer tools with tool search.",
             "ডোমেইন অনুযায়ী সাব-এজেন্টে ভাগ করুন, রাউটার ব্যবহার করুন, বা টুল সার্চ দিয়ে টুল পিছিয়ে দিন।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Clear descriptions and good tool design make the difference between a demo and a real system.",
         "স্পষ্ট টুল ডেসক্রিপশন আর ভালো টুল ডিজাইনই ডেমো আর আসল সিস্টেমের পার্থক্য গড়ে।")],
       [sh("user"), sh("model"), sh("svc"), sh("res")],
       [ln("user", "model", "to"), ln("model", "svc", "to"), ln("svc", "res", "to"), ln("res", "model", "to")],
       [None, None, None],
       points=[("Write each tool description to say what it does, when to use it, and what it returns.",
                "প্রতিটি টুলের ডেসক্রিপশনে লিখুন সে কী করে, কখন ব্যবহার করবেন আর কী ফেরত দেয়।"),
               ("Use a tight schema with clear types and enums. Avoid any.",
                "স্পষ্ট টাইপ আর এনাম দিয়ে স্কিমা আঁটসাঁট রাখুন। any এড়িয়ে চলুন।"),
               ("Keep fewer than about 20 tools available at once.",
                "একসাথে প্রায় ২০-এর কম টুল রাখুন।"),
               ("Make independent tool calls in one turn so they run at the same time.",
                "একে অপরের ওপর নির্ভর করে না এমন টুল কল এক টার্নে দিন, যাতে সেগুলো একসাথে চলে।"),
               ("Tool output is prompt content: trim it, format it for reading, add a summary when the result is not obvious.",
                "টুলের আউটপুট প্রম্পটেরই অংশ: ছাঁটুন, পড়ার মতো ফরম্যাট করুন, আর ফলাফল অস্পষ্ট হলে সারমর্ম যোগ করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
