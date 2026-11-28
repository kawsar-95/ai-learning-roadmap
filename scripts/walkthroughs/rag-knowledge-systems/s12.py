"""Agentic retrieval: workflows, agents and what they cost: the model steers the search, so calls, time and tokens multiply, and a hard step limit is needed.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Agentic    Body: "Agentic retrieval lets the model itself decide whether to retrieve, what to search for, whether the results are good enough, and when to stop. The price is more LLM calls, more latency and a harder system to debug."
  2 Workflow   Start here: "Workflow: A system where the LLM and tools follow steps that your code fixed in advance."
  3 Agent      Start here: "Agent: A system where the LLM directs its own steps and its own use of tools." "file_search: ... The model chooses when to call it, and it searches by meaning and by keywords."
  4 Subagents  Body: "a lead agent spawns parallel subagents that search iteratively." Diagram: "Lead agent: plans, spawns, merges"; "Subagent: search + read".
  5 Cost       Body: "agents use about 4x the tokens of chat, and multi-agent systems about 15x." Diagram: "chat 1x, agent ~4x, multi-agent ~15x".
  6 Step limit Warn: "loops need a hard step limit and a stopping rule, or a confused model keeps searching." Start here: "Step limit and stopping rule: A hard cap on how many rounds a loop may run, plus a rule that says when to stop."
  7 Start simple  Warn: "Start with single-step retrieval, and add iteration only for questions that fail it." "One well-tuned LLM call with retrieval is often enough."
  8 Remember   The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("Question", "প্রশ্ন"), 80, 162),
    node("lead", "model", ("Lead agent", "লিড এজেন্ট"), 255, 162),
    node("fs", "tool", ("file_search", "file_search"), 630, 162),
    node("sub1", "service", ("Subagent", "সাবএজেন্ট"), 450, 60),
    node("sub2", "service", ("Subagent", "সাবএজেন্ট"), 450, 162),
    node("sub3", "service", ("Subagent", "সাবএজেন্ট"), 450, 260),
    node("limit", "clock", ("Step limit", "ধাপের সীমা"), 450, 162),
    node("tok", "chart", ("Token use", "টোকেন খরচ"), 615, 162),
]

METRICS = [
    ("Who decides", "কে ঠিক করে"),
    ("Token use", "টোকেন খরচ"),
    ("Step limit", "ধাপের সীমা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and multiples are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর গুণিতক সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Agentic", "এজেন্টিক"),
       ("The model steers the search", "মডেল নিজেই সার্চ চালায়"),
       [("Agentic retrieval lets the model decide whether to retrieve, what to search for, whether the results are good enough, and when to stop.",
         "এজেন্টিক রিট্রিভালে মডেল নিজেই ঠিক করে রিট্রিভ করবে কি না, কী খুঁজবে, ফল যথেষ্ট ভালো কি না, আর কখন থামবে।"),
        ("The price is more LLM calls, more latency and a harder system to debug.",
         "দাম হলো বেশি LLM কল, বেশি ল্যাটেন্সি আর ডিবাগে কঠিন সিস্টেম।")],
       [sh("user", "hot"), sh("lead", "hot", ("decides", "ঠিক করে")), sh("fs", "hot")],
       [ln("user", "lead", "to", state="hot"), ln("lead", "fs", "to", state="hot")],
       [("the model", "মডেল"), None, None]),

    st(("Workflow", "ওয়ার্কফ্লো"),
       ("Workflow: the steps are fixed", "ওয়ার্কফ্লো: ধাপ আগে থেকে ঠিক করা"),
       [("In a workflow, the LLM and tools follow steps that your code fixed in advance.",
         "ওয়ার্কফ্লোতে LLM আর টুল এমন ধাপে চলে, যা আপনার কোড আগে থেকেই ঠিক করে রেখেছে।")],
       [sh("user", "hot"), sh("lead", "hot", ("fixed in advance", "আগে থেকে ঠিক করা")), sh("fs", "hot")],
       [ln("user", "lead", "to", state="hot"), ln("lead", "fs", "to", state="hot")],
       [("your code", "আপনার কোড"), None, None]),

    st(("Agent", "এজেন্ট"),
       ("Agent: the model directs itself", "এজেন্ট: মডেল নিজেই চালায়"),
       [("In an agent, the LLM directs its own steps and its own use of tools.",
         "এজেন্টে LLM নিজের ধাপ আর নিজের টুল ব্যবহার নিজেই ঠিক করে।"),
        ("OpenAI's file_search is a hosted search tool: the model chooses when to call it, and it searches by meaning and by keywords.",
         "OpenAI-এর file_search একটি হোস্টেড সার্চ টুল: মডেল নিজে ঠিক করে কখন ডাকবে; এটি অর্থ আর কিওয়ার্ড দুই ভাবেই খোঁজে।")],
       [sh("lead", "hot", ("chooses when", "কখন ডাকবে")), sh("fs", "hot", ("meaning + keywords", "অর্থ + কিওয়ার্ড"))],
       [ln("lead", "fs", "to", state="hot")],
       [("the LLM", "LLM"), None, None]),

    st(("Subagents", "সাবএজেন্ট"),
       ("A lead agent and subagents", "লিড এজেন্ট আর সাবএজেন্ট"),
       [("A lead agent plans, spawns and merges. It starts subagents that search iteratively.",
         "লিড এজেন্ট পরিকল্পনা করে, সাবএজেন্ট চালু করে আর ফল মেলায়। সাবএজেন্টরা বারবার খোঁজে।"),
        ("Several subagents can search at the same time.",
         "কয়েকটি সাবএজেন্ট একসাথে খুঁজতে পারে।")],
       [sh("lead", "hot", ("plans, merges", "পরিকল্পনা, মেলানো")),
        sh("sub1", "hot", ("search + read", "খোঁজা + পড়া")), sh("sub2", "hot", ("search + read", "খোঁজা + পড়া")),
        sh("sub3", "hot", ("search + read", "খোঁজা + পড়া"))],
       [ln("lead", "sub1", "to", state="hot"), ln("lead", "sub2", "to", state="hot"), ln("lead", "sub3", "to", state="hot")],
       [("lead agent", "লিড এজেন্ট"), None, None]),

    st(("Cost", "খরচ"),
       ("Tokens multiply", "টোকেন কয়েক গুণ বাড়ে"),
       [("Anthropic reports that its agents used about 4x the tokens of chat, and its multi-agent system about 15x.",
         "Anthropic-এর রিপোর্টে তাদের এজেন্ট চ্যাটের প্রায় ৪x টোকেন খরচ করেছে, আর তাদের মাল্টি-এজেন্ট সিস্টেম প্রায় ১৫x।"),
        ("Agentic systems multiply tokens and latency, so track cost per answered question.",
         "এজেন্টিক সিস্টেমে টোকেন আর ল্যাটেন্সি কয়েক গুণ বাড়ে, তাই প্রতিটি উত্তরের খরচ মাপুন।")],
       [sh("user", "hot", ("chat: 1x", "চ্যাট: ১x")), sh("lead", "hot", ("agent: about 4x", "এজেন্ট: প্রায় ৪x")),
        sh("tok", "warn", ("multi-agent: about 15x", "মাল্টি-এজেন্ট: প্রায় ১৫x"))],
       [ln("user", "lead", "to", state="hot"), ln("lead", "tok", "to", state="warn")],
       [None, ("about 4x, about 15x", "প্রায় ৪x, প্রায় ১৫x"), None],
       note=("warn", "The Anthropic numbers come from the vendor's own internal evaluation, not an independent benchmark.",
             "Anthropic-এর সংখ্যাগুলো তাদের নিজেদের অভ্যন্তরীণ মূল্যায়ন থেকে, কোনো স্বাধীন বেঞ্চমার্ক থেকে নয়।")),

    st(("Step limit", "ধাপের সীমা"),
       ("Every loop needs a hard limit", "প্রতিটি লুপে কড়া সীমা চাই"),
       [("Loops need a hard step limit and a stopping rule, or a confused model keeps searching.",
         "লুপে কড়া ধাপের সীমা আর থামার শর্ত লাগে, নইলে বিভ্রান্ত মডেল খুঁজতেই থাকে।"),
        ("A step limit is a hard cap on how many rounds a loop may run. A stopping rule says when to stop.",
         "ধাপের সীমা মানে লুপ সর্বোচ্চ কত রাউন্ড চলবে তার কড়া সীমা। থামার শর্ত বলে কখন থামতে হবে।")],
       [sh("lead", "hot"), sh("limit", "hot", ("hard cap", "কড়া সীমা")), sh("fs", "warn", ("keeps searching", "খুঁজতেই থাকে"))],
       [ln("lead", "limit", "to", state="hot"), ln("limit", "fs", "to", state="warn")],
       [None, None, ("hard cap and stopping rule", "কড়া সীমা আর থামার শর্ত")]),

    st(("Start simple", "সহজ শুরু"),
       ("Start with one search", "এক সার্চ দিয়ে শুরু করুন"),
       [("One well-tuned LLM call with retrieval is often enough.",
         "রিট্রিভাল সহ একটি ভালোভাবে সাজানো LLM কলই প্রায়ই যথেষ্ট।"),
        ("Add iteration only for questions that fail single-step retrieval.",
         "শুধু যেসব প্রশ্নে এক ধাপের রিট্রিভাল ব্যর্থ হয়, সেগুলোতে পুনরাবৃত্তি যোগ করুন।")],
       [sh("user", "hot"), sh("lead", "hot", ("one call", "একটি কল")), sh("fs", "hot")],
       [ln("user", "lead", "to", state="hot"), ln("lead", "fs", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("The model can steer the search, but every extra round costs calls, time and tokens.",
         "মডেল সার্চ চালাতে পারে, কিন্তু প্রতিটি বাড়তি রাউন্ডে কল, সময় আর টোকেন খরচ হয়।")],
       [sh("user"), sh("lead"), sh("limit"), sh("fs")],
       [ln("user", "lead", "to"), ln("lead", "limit", "to"), ln("limit", "fs", "to")],
       [None, None, None],
       points=[("Start simple. One well-tuned LLM call with retrieval is often enough.",
                "সহজ থেকে শুরু করুন। রিট্রিভাল সহ একটি ভালোভাবে সাজানো LLM কলই প্রায়ই যথেষ্ট।"),
               ("Anthropic reports that its agents used about 4x the tokens of chat, and its multi-agent system about 15x.",
                "Anthropic-এর রিপোর্টে তাদের এজেন্ট চ্যাটের প্রায় ৪x টোকেন খরচ করেছে, আর তাদের মাল্টি-এজেন্ট সিস্টেম প্রায় ১৫x।"),
               ("Give every loop a hard step limit and a stopping rule, or a confused model keeps searching.",
                "প্রতিটি লুপে কড়া ধাপের সীমা আর থামার শর্ত দিন, নইলে বিভ্রান্ত মডেল খুঁজতেই থাকে।"),
               ("Track cost per answered question, because agentic systems multiply tokens and latency.",
                "প্রতিটি উত্তরের খরচ মাপুন, কারণ এজেন্টিক সিস্টেমে টোকেন আর ল্যাটেন্সি কয়েক গুণ বাড়ে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
