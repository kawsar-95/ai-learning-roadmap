"""Part 9 · 03 Single-agent vs multi-agent orchestration: one agent in one loop, or an orchestrator with workers, and what the team costs.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Single       Words: "Single agent: One LLM in one loop with one set of tools. You debug by reading one trace." Table: "Token cost ... single agent: about 4×".
  2 Multi        Words: "Multi-agent: Several agents, each with its own prompt and tools, working together on one task." Table: "Debugging ... N traces to correlate".
  3 Team         Words: "Orchestrator: The agent that hands out work to the others and puts their results together." "Worker: A specialised agent, such as a researcher, writer, critic, or coder, that does one part of the job."
  4 Talk         Words: "Shared scratchpad (blackboard): One shared file or in-memory dict that all agents read from and write to." "Message passing: The orchestrator sends messages in a fixed format to the workers."
  5 Cost         Body: "Multi-agent systems use far more tokens: Anthropic measured about 15× a chat, against about 4× for a single agent."
  6 When         Body: "As a rule of thumb, use a single agent for 5 tools or fewer in one domain. Use multi-agent for distinct roles and high stakes."
  7 Remember     Body: "Do not build a multi-agent system just because it sounds advanced." "One well-tuned agent often does the job, and a team of agents costs more."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("single", "model", ("Single agent", "সিঙ্গেল এজেন্ট"), 130, 162),
    node("tools", "tool", ("One set of tools", "একসেট টুল"), 400, 75),
    node("trace", "file", ("One trace", "একটি ট্রেস"), 400, 250),
    node("orch", "service", ("Orchestrator", "অর্কেস্ট্রেটর"), 130, 162),
    node("res", "model", ("Researcher", "গবেষক"), 400, 75),
    node("wri", "model", ("Writer", "লেখক"), 400, 162),
    node("cri", "model", ("Critic", "সমালোচক"), 400, 250),
    node("pad", "file", ("Shared scratchpad", "শেয়ার্ড স্ক্র্যাচপ্যাড"), 640, 162),
]

METRICS = [
    ("Debugging", "ডিবাগিং"),
    ("Token cost", "টোকেন খরচ"),
    ("Best when", "কখন ভালো"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Single", "সিঙ্গেল"),
       ("A single agent: one loop", "সিঙ্গেল এজেন্ট: একটি লুপ"),
       [("A single agent is one LLM in one loop with one set of tools.",
         "সিঙ্গেল এজেন্ট মানে একটি লুপে একটি LLM, একসেট টুলসহ।"),
        ("You debug by reading one trace.",
         "একটি ট্রেস পড়েই ডিবাগ করা যায়।")],
       [sh("single", "hot"), sh("tools", "hot"), sh("trace", "hot")],
       [ln("single", "tools", "to", state="hot"), ln("single", "trace", "to", state="hot")],
       [("one trace", "একটি ট্রেস"), ("about 4×", "প্রায় ৪ গুণ"), None]),

    st(("Multi", "মাল্টি"),
       ("Several agents on one task", "একটি কাজে একাধিক এজেন্ট"),
       [("A multi-agent setup has several agents, each with its own prompt and tools, working together on one task.",
         "মাল্টি-এজেন্টে একাধিক এজেন্ট থাকে, প্রত্যেকের নিজের প্রম্পট ও টুল, একটি কাজে একসাথে চলে।"),
        ("Debugging means matching N traces.",
         "ডিবাগে N-টি ট্রেস মেলাতে হয়।")],
       [sh("orch", "hot"), sh("res", "hot", ("own prompt, own tools", "নিজের প্রম্পট ও টুল")),
        sh("wri", "hot", ("own prompt, own tools", "নিজের প্রম্পট ও টুল")), sh("cri", "hot", ("own prompt, own tools", "নিজের প্রম্পট ও টুল"))],
       [ln("orch", "res", "to", state="hot"), ln("orch", "wri", "to", state="hot"), ln("orch", "cri", "to", state="hot")],
       [("N traces", "N-টি ট্রেস"), None, None]),

    st(("Team", "দল"),
       ("An orchestrator and its workers", "অর্কেস্ট্রেটর আর তার ওয়ার্কার"),
       [("The orchestrator hands out work to the others and puts their results together.",
         "অর্কেস্ট্রেটর অন্যদের কাজ ভাগ করে দেয় এবং তাদের ফল জোড়া লাগায়।"),
        ("A worker is a specialised agent, such as a researcher, writer, critic, or coder, that does one part of the job.",
         "ওয়ার্কার বিশেষায়িত এজেন্ট, যেমন গবেষক, লেখক, সমালোচক বা কোডার, যে কাজের একটি অংশ করে।")],
       [sh("orch", "hot", ("hands out work", "কাজ ভাগ করে")), sh("res", "hot", ("one part", "একটি অংশ")),
        sh("wri", "hot", ("one part", "একটি অংশ")), sh("cri", "hot", ("one part", "একটি অংশ"))],
       [ln("orch", "res", "to", state="hot"), ln("orch", "wri", "to", state="hot"), ln("orch", "cri", "to", state="hot")],
       [None, None, None]),

    st(("Talk", "যোগাযোগ"),
       ("How the agents talk", "এজেন্টরা কীভাবে কথা বলে"),
       [("With message passing, the orchestrator sends messages in a fixed format to the workers.",
         "মেসেজ পাসিংয়ে অর্কেস্ট্রেটর ওয়ার্কারদের কাছে নির্দিষ্ট ফরম্যাটে মেসেজ পাঠায়।"),
        ("With a shared scratchpad, also called a blackboard, all agents read from and write to one shared file or in-memory dict.",
         "শেয়ার্ড স্ক্র্যাচপ্যাডে (blackboard) সব এজেন্ট একটি শেয়ার করা ফাইল বা ইন-মেমরি ডিক্ট থেকে পড়ে ও লেখে।")],
       [sh("orch", "hot"), sh("res", "hot"), sh("wri", "hot"), sh("pad", "hot")],
       [ln("orch", "res", "to", state="hot", label=("message", "মেসেজ")), ln("orch", "wri", "to", state="hot"),
        ln("res", "pad", "to", state="hot"), ln("wri", "pad", "to", state="hot")],
       [None, None, None]),

    st(("Cost", "খরচ"),
       ("A team uses far more tokens", "দলে অনেক বেশি টোকেন লাগে"),
       [("Multi-agent systems use far more tokens.",
         "মাল্টি-এজেন্টে অনেক বেশি টোকেন লাগে।"),
        ("Anthropic measured about 15× a chat, against about 4× for a single agent.",
         "Anthropic-এর হিসাবে চ্যাটের প্রায় ১৫ গুণ, আর সিঙ্গেল এজেন্টের প্রায় ৪ গুণ।")],
       [sh("single", "hot", ("about 4×", "প্রায় ৪ গুণ"), x=200, y=162), sh("orch", "warn", ("about 15× a chat", "চ্যাটের প্রায় ১৫ গুণ"), x=560, y=162)],
       [],
       [None, ("about 15× a chat", "চ্যাটের প্রায় ১৫ গুণ"), None],
       note=("warn", "Debugging a single agent means reading one trace. Multi-agent means matching N traces.",
             "সিঙ্গেল এজেন্ট ডিবাগে একটি ট্রেস পড়তে হয়। মাল্টি-এজেন্টে N-টি ট্রেস মেলাতে হয়।")),

    st(("When", "কখন"),
       ("When to use which", "কখন কোনটা"),
       [("As a rule of thumb, use a single agent for 5 tools or fewer in one domain.",
         "সাধারণ নিয়ম: একটি ডোমেইনে ৫টি বা কম টুলে সিঙ্গেল এজেন্ট নিন।"),
        ("Use multi-agent for distinct roles and high stakes.",
         "আলাদা ভূমিকা আর বড় ঝুঁকিতে মাল্টি-এজেন্ট নিন।")],
       [sh("single", "hot", ("5 tools or fewer", "৫টি বা কম টুল"), x=200, y=162), sh("orch", "hot", ("distinct roles", "আলাদা ভূমিকা"), x=560, y=162)],
       [],
       [None, None, ("5 tools or fewer", "৫টি বা কম টুল")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("One well-tuned agent often does the job, and a team of agents costs more.",
         "একটি ভালোভাবে টিউন করা এজেন্টই প্রায়ই কাজ করে দেয়, আর এজেন্টের দলে খরচ বেশি।")],
       [sh("single", "hot", x=200, y=162), sh("orch", "dim", x=560, y=162)],
       [],
       [None, None, None],
       points=[("Do not build a multi-agent system just because it sounds advanced.",
                "শুধু উন্নত শোনায় বলে মাল্টি-এজেন্ট সিস্টেম বানাবেন না।"),
               ("Debugging a single agent means reading one trace. Multi-agent means matching N traces.",
                "সিঙ্গেল এজেন্ট ডিবাগে একটি ট্রেস পড়তে হয়। মাল্টি-এজেন্টে N-টি ট্রেস মেলাতে হয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
