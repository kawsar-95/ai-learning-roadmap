"""Part 5 · 04 Hierarchical memory: store different kinds of state in different layers, small and always seen near the model, unbounded and fetched on demand far away.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Working    Definition: "The current prompt: system, tools, retrieved text, and the current request. Small, rebuilt every call, and always in focus." Table: "Every call (ephemeral)".
  2 Short-term Definition: "Recent turns, tool results, and decisions of this session. It lives in a session store, and older turns become short summaries." Table: "Each turn, with rolling summarization".
  3 Long-term  Definition: "User preferences, known facts, and project context. It updates slowly, when explicit facts are extracted." Vector store: "A database that keeps the meaning of each text as a list of numbers, so related texts can be found."
  4 Episodic   Definition: "Short memories distilled from past sessions: lessons learned and what worked. Written at the end of a session or when triggered."
  5 Evict      Definitions "MemGPT" (a 2023 idea, Packer et al.: the model decides what to move out of its prompt and what to bring back, using tool calls like recall_storage.search) and "Evict and page in": "Evict means moving information from working memory to external storage."
  6 Page in    "Paging in means bringing it back when needed." Table, external: "Retrieved on demand".
  7 Stale      Warning: "Long-term memories can go stale or contradict the user. Tag each with a timestamp and a confidence score." "Ask the user to confirm doubtful old memories, or favor newer memories when retrieving."
  8 Remember   Points: "The layers are working, short-term, long-term, and episodic memory, plus external storage for everything else." "Closer to the model means smaller but always seen. Farther means unbounded but fetched only on demand."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("model", "model", ("Model", "মডেল"), 110, 50),
    node("work", "note", ("Working", "ওয়ার্কিং"), 380, 50),
    node("short", "database", ("Short-term", "শর্ট-টার্ম"), 650, 50),
    node("long", "database", ("Long-term", "লং-টার্ম"), 650, 160),
    node("epi", "database", ("Episodic", "এপিসোডিক"), 650, 270),
    node("ext", "storage", ("External", "এক্সটার্নাল"), 380, 270),
    node("tool", "tool", ("recall_storage.search", "recall_storage.search"), 380, 162),
]

METRICS = [
    ("Size", "আকার"),
    ("Seen", "দেখা হয়"),
    ("Updates", "আপডেট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Working", "ওয়ার্কিং"),
       ("Working memory: the current prompt", "ওয়ার্কিং মেমরি: বর্তমান প্রম্পট"),
       [("Working memory is the current prompt: system, tools, retrieved text, and the current request.",
         "ওয়ার্কিং মেমরি হলো বর্তমান প্রম্পট: সিস্টেম, টুল, খুঁজে আনা লেখা আর বর্তমান অনুরোধ।"),
        ("It is small, rebuilt every call, and always in focus.",
         "এটা ছোট, প্রতি কলে নতুন, আর সবসময় মনোযোগে থাকে।")],
       [sh("model", "hot"), sh("work", "hot", ("always in focus", "সবসময় মনোযোগে")),
        sh("short", "dim"), sh("long", "dim"), sh("epi", "dim"), sh("ext", "dim")],
       [ln("model", "work", "to", state="hot")],
       [(("small"), ("ছোট")), (("always"), ("সবসময়")), (("every call"), ("প্রতি কলে"))]),

    st(("Short-term", "শর্ট-টার্ম"),
       ("Short-term memory: this session", "শর্ট-টার্ম মেমরি: এই সেশন"),
       [("Short-term memory holds the recent turns, tool results, and decisions of this session.",
         "শর্ট-টার্ম মেমরিতে থাকে এই সেশনের সাম্প্রতিক টার্ন, টুলের ফল আর সিদ্ধান্ত।"),
        ("It lives in a session store, and older turns become short summaries.",
         "এটা সেশন স্টোরে থাকে, আর পুরোনো টার্ন ছোট সারসংক্ষেপ হয়ে যায়।")],
       [sh("work", "dim"), sh("short", "hot", ("session store", "সেশন স্টোর")),
        sh("long", "dim"), sh("model", "dim")],
       [ln("work", "short", "to", state="hot")],
       [None, None, (("each turn"), ("প্রতি টার্নে"))]),

    st(("Long-term", "লং-টার্ম"),
       ("Long-term memory: preferences and facts", "লং-টার্ম মেমরি: পছন্দ আর তথ্য"),
       [("Long-term memory holds user preferences, known facts, and project context.",
         "লং-টার্ম মেমরিতে থাকে ইউজারের পছন্দ, জানা তথ্য আর প্রজেক্টের প্রসঙ্গ।"),
        ("It updates slowly, when explicit facts are extracted.",
         "স্পষ্ট তথ্য বের করা হলে তবেই এটা ধীরে আপডেট হয়।")],
       [sh("short", "dim"), sh("long", "hot", ("vector store", "ভেক্টর স্টোর")), sh("epi", "dim")],
       [ln("short", "long", "to", state="hot")],
       [None, None, (("slow"), ("ধীরে"))],
       note=("tip", "A vector store is a database that keeps the meaning of each text as a list of numbers, so related texts can be found.",
             "ভেক্টর স্টোর এমন ডেটাবেস, যেখানে প্রতিটি লেখার অর্থ সংখ্যার তালিকা হিসেবে রাখা হয়, যাতে সম্পর্কিত লেখা খুঁজে পাওয়া যায়।")),

    st(("Episodic", "এপিসোডিক"),
       ("Episodic memory: lessons from past sessions", "এপিসোডিক মেমরি: আগের সেশনের শিক্ষা"),
       [("Episodic memory holds short memories distilled from past sessions: lessons learned and what worked.",
         "এপিসোডিক মেমরিতে থাকে আগের সেশন থেকে ছেঁকে নেওয়া ছোট স্মৃতি: কী শেখা গেল, কী কাজ করল।"),
        ("It is written at the end of a session or when triggered.",
         "এটা সেশন শেষে বা ট্রিগার হলে লেখা হয়।")],
       [sh("long", "dim"), sh("epi", "hot", ("lessons learned", "কী শেখা গেল")), sh("ext", "dim")],
       [ln("long", "epi", "to", state="hot")],
       [None, None, (("end of session"), ("সেশন শেষে"))]),

    st(("Evict", "ইভিক্ট"),
       ("MemGPT: the model moves things out", "MemGPT: মডেল নিজেই সরায়"),
       [("MemGPT is a 2023 idea (Packer et al.): the model itself decides what to move out of its prompt and what to bring back.",
         "MemGPT ২০২৩ সালের একটি ধারণা (Packer et al.): মডেল নিজেই ঠিক করে প্রম্পট থেকে কী সরাবে আর কী ফিরিয়ে আনবে।"),
        ("Evict means moving information from working memory to external storage.",
         "ইভিক্ট মানে তথ্য ওয়ার্কিং মেমরি থেকে বাইরের স্টোরেজে সরানো।")],
       [sh("work", "hot", x=90, y=162), sh("tool", "hot", ("tool call", "টুল কল")), sh("ext", "hot", x=670, y=162)],
       [ln("work", "tool", "to", state="hot", label=("evict", "ইভিক্ট")), ln("tool", "ext", "to", state="hot")],
       [None, None, None]),

    st(("Page in", "পেজ ইন"),
       ("Page in: bring it back when needed", "পেজ ইন: দরকারে ফিরিয়ে আনা"),
       [("Paging in means bringing information back when needed.",
         "পেজ ইন মানে দরকারে তথ্য ফিরিয়ে আনা।"),
        ("The model uses tool calls like recall_storage.search to do it. External storage is retrieved on demand.",
         "মডেল এর জন্য recall_storage.search-এর মতো টুল কল ব্যবহার করে। এক্সটার্নাল স্টোরেজ শুধু প্রয়োজনে আনা হয়।")],
       [sh("ext", "hot", x=670, y=162), sh("tool", "hot", ("tool call", "টুল কল")), sh("work", "hot", x=90, y=162)],
       [ln("ext", "tool", "to", state="hot"), ln("tool", "work", "to", state="hot", label=("page in", "পেজ ইন"))],
       [(("unbounded"), ("সীমাহীন")), (("only when retrieved"), ("শুধু প্রয়োজনে আনা")), (("on demand"), ("প্রয়োজনে"))]),

    st(("Stale", "পুরোনো"),
       ("Memories can go stale", "মেমরি পুরোনো হতে পারে"),
       [("Long-term memories can go stale or contradict the user.",
         "লং-টার্ম মেমরি পুরোনো বা ইউজারের কথার সাথে স্ববিরোধী হতে পারে।"),
        ("Tag each with a timestamp and a confidence score.",
         "প্রতিটিতে টাইমস্ট্যাম্প ও কনফিডেন্স স্কোর রাখুন।")],
       [sh("long", "warn", ("timestamp", "টাইমস্ট্যাম্প")), sh("model", "dim")],
       [ln("long", "model", "to", state="warn")],
       [None, None, None],
       note=("warn", "Ask the user to confirm doubtful old memories, or favor newer memories when retrieving.",
             "সন্দেহজনক পুরোনো মেমরি ইউজারকে দিয়ে নিশ্চিত করান, অথবা রিট্রিভালের সময় নতুন মেমরিকে বেশি ওজন দিন।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("The layers are working, short-term, long-term, and episodic memory, plus external storage for everything else.",
         "স্তরগুলো হলো ওয়ার্কিং, শর্ট-টার্ম, লং-টার্ম ও এপিসোডিক মেমরি, আর বাকি সবকিছুর জন্য এক্সটার্নাল স্টোরেজ।")],
       [sh("model"), sh("work"), sh("short"), sh("long"), sh("epi"), sh("ext")],
       [ln("model", "work", "to"), ln("work", "short", "to"), ln("short", "long", "to"),
        ln("long", "epi", "to"), ln("epi", "ext", "to")],
       [None, None, None],
       points=[("Closer to the model means smaller but always seen.",
                "মডেলের যত কাছে, স্তর তত ছোট কিন্তু সবসময় দেখা।"),
               ("Farther means unbounded but fetched only on demand.",
                "যত দূরে, তত সীমাহীন কিন্তু শুধু প্রয়োজনে আনা হয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
