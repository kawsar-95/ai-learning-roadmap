"""Part 5 · 05 Context compression & pruning: compression shortens text, pruning drops what does not matter; the goal is the same information in fewer tokens.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Goal       Body: "Long prompts cost money and time. Compression shortens text while keeping the meaning as much as possible, and pruning drops the parts that do not matter. The goal is the same information in fewer tokens."
  2 Compress   Definitions "Compression" ("Making text shorter by removing repeated or empty parts, while keeping as much of the meaning as possible.") and "LLMLingua" ("It can shrink prompts by up to 20×.").
  3 Low info   Definitions "LLMLingua" ("cuts low-information tokens from a prompt") and "Self-information (perplexity)" ("A measure of how surprising a phrase is. Phrases that add little new information can be dropped.").
  4 Pruning    Definition "Pruning": "Deleting the parts that do not matter for the current task, like cutting dead branches off a tree." Point: "Compression shrinks everything; pruning removes only what is not relevant."
  5 Recipe     Point: "A good recipe: retrieve 20 chunks, re-rank, prune to the top 5, then compress if still over budget." Definitions "Cross-encoder" and "Chunk".
  6 Duplicates Definitions "Deduplication" ("Finding near-copies of the same text and keeping only one." Point: "(cosine > 0.95)") and "Token-budget knapsack" ("Adding chunks in order of relevance until the token limit is full, then stopping.").
  7 Remember   Points: "Pruning keeps information density, or useful facts per token; compression reduces absolute size." "They work well together."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("long", "file", ("Long prompt", "লম্বা প্রম্পট"), 110, 162),
    node("lingua", "tool", ("LLMLingua", "LLMLingua"), 380, 162),
    node("short", "file", ("Fewer tokens", "কম টোকেন"), 650, 162),
    node("chunks", "file", ("Chunks", "চাঙ্ক"), 100, 162),
    node("rerank", "model", ("Cross-encoder", "ক্রস-এনকোডার"), 290, 162),
    node("top", "file", ("Top 5", "সেরা ৫টি"), 480, 162),
    node("dedup", "tool", ("Deduplication", "ডিডুপ্লিকেশন"), 380, 60),
    node("knap", "note", ("Token budget", "টোকেন বাজেট"), 380, 262),
]

METRICS = [
    ("Tokens", "টোকেন"),
    ("Information", "তথ্য"),
    ("Chunks", "চাঙ্ক"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Goal", "লক্ষ্য"),
       ("Same information, fewer tokens", "একই তথ্য, কম টোকেন"),
       [("Long prompts cost money and time.",
         "লম্বা প্রম্পটে টাকা আর সময় দুটোই লাগে।"),
        ("Compression shortens text while keeping the meaning as much as possible, and pruning drops the parts that do not matter.",
         "কমপ্রেশন অর্থ যথাসম্ভব রেখে লেখা ছোট করে, আর প্রুনিং অপ্রয়োজনীয় অংশ বাদ দেয়।")],
       [sh("long", "hot"), sh("short", "hot", ("same information", "একই তথ্য"))],
       [ln("long", "short", "to", state="hot")],
       [("fewer", "কম"), ("same", "একই"), None]),

    st(("Compress", "কমপ্রেশন"),
       ("Compression shortens the text", "কমপ্রেশন লেখা ছোট করে"),
       [("Compression makes text shorter by removing repeated or empty parts, while keeping as much of the meaning as possible.",
         "কমপ্রেশন পুনরাবৃত্তি বা ফাঁপা অংশ সরিয়ে লেখা ছোট করে, অর্থ যথাসম্ভব ঠিক রেখে।"),
        ("LLMLingua is one method. It can shrink prompts by up to 20×.",
         "LLMLingua একটি পদ্ধতি। এতে প্রম্পট ২০× পর্যন্ত ছোট হতে পারে।")],
       [sh("long", "hot"), sh("lingua", "hot"), sh("short", "hot")],
       [ln("long", "lingua", "to", state="hot"), ln("lingua", "short", "to", state="hot")],
       [("up to 20×", "২০× পর্যন্ত"), None, None]),

    st(("Low info", "কম-তথ্য"),
       ("Drop what adds little", "যা কম জানায় তা বাদ"),
       [("LLMLingua cuts low-information tokens from a prompt.",
         "LLMLingua প্রম্পট থেকে কম-তথ্যের টোকেন কেটে দেয়।"),
        ("Self-information, or perplexity, measures how surprising a phrase is. Phrases that add little new information can be dropped.",
         "সেলফ-ইনফরমেশন (পারপ্লেক্সিটি) মাপে একটি বাক্যাংশ কতটা নতুন বা চমকপ্রদ। যা নতুন কিছু জানায় না, সেটা বাদ দেওয়া যায়।")],
       [sh("long", "hot", ("surprising or not", "নতুন কি না")), sh("lingua", "hot", ("low-information", "কম-তথ্য")), sh("short", "hot")],
       [ln("long", "lingua", "to", state="hot"), ln("lingua", "short", "to", state="hot")],
       [None, None, None]),

    st(("Pruning", "প্রুনিং"),
       ("Pruning deletes what does not matter", "প্রুনিং অপ্রয়োজনীয় অংশ মুছে ফেলে"),
       [("Pruning deletes the parts that do not matter for the current task, like cutting dead branches off a tree.",
         "প্রুনিং বর্তমান কাজে যে অংশ লাগে না তা বাদ দেয়, গাছের মরা ডাল ছাঁটার মতো।"),
        ("Compression shrinks everything; pruning removes only what is not relevant.",
         "কমপ্রেশন সবকিছু ছোট করে; প্রুনিং শুধু অপ্রাসঙ্গিক অংশ কাটে।")],
       [sh("chunks", "hot"), sh("top", "hot", ("only what is relevant", "শুধু প্রাসঙ্গিক"))],
       [ln("chunks", "top", "to", state="hot")],
       [None, None, None]),

    st(("Recipe", "পদ্ধতি"),
       ("A good recipe: retrieve, re-rank, prune, compress", "ভালো পদ্ধতি: রিট্রিভ, রিরেংক, প্রুন, কমপ্রেস"),
       [("A good recipe: retrieve 20 chunks, re-rank, prune to the top 5, then compress if still over budget.",
         "ভালো পদ্ধতি: ২০টি চাঙ্ক রিট্রিভ করুন, রিরেংক করুন, সেরা ৫টিতে প্রুন করুন, তখনও বেশি হলে কমপ্রেস করুন।"),
        ("A cross-encoder reads the question and a chunk together and scores their match. It is used to re-rank.",
         "ক্রস-এনকোডার প্রশ্ন আর একটি চাঙ্ক একসাথে পড়ে, দুটো কতটা মেলে তার স্কোর দেয়। রিরেংক করতে এটি লাগে।")],
       [sh("chunks", "hot", ("retrieve", "রিট্রিভ"), x=110, y=70), sh("rerank", "hot", ("re-rank", "রিরেংক"), x=380, y=70),
        sh("top", "hot", ("prune", "প্রুন"), x=640, y=70), sh("lingua", "hot", ("compress", "কমপ্রেস"), x=640, y=250)],
       [ln("chunks", "rerank", "to", state="hot"), ln("rerank", "top", "to", state="hot"), ln("top", "lingua", "to", state="hot")],
       [None, None, ("top 5", "সেরা ৫টি")]),

    st(("Duplicates", "ডুপ্লিকেট"),
       ("Near-copies and the token limit", "প্রায় একই কপি আর টোকেনের সীমা"),
       [("Deduplication finds near-copies of the same text and keeps only one (cosine > 0.95).",
         "ডিডুপ্লিকেশন একই লেখার প্রায় হুবহু কপি খুঁজে শুধু একটি রাখে (কসাইন > ০.৯৫)।"),
        ("A token-budget knapsack adds chunks in order of relevance until the token limit is full, then stops.",
         "টোকেন-বাজেট ন্যাপস্যাক প্রাসঙ্গিকতার ক্রমে চাঙ্ক নিতে থাকে, টোকেনের সীমা ভরলে থামে।")],
       [sh("chunks", "hot", x=110, y=162), sh("dedup", "hot", ("keep one", "একটি রাখা")),
        sh("knap", "hot", ("in order of relevance", "প্রাসঙ্গিকতার ক্রমে")), sh("top", "hot", x=640, y=162)],
       [ln("chunks", "dedup", "to", state="hot"), ln("chunks", "knap", "to", state="hot"),
        ln("dedup", "top", "to", state="hot"), ln("knap", "top", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Compression shrinks everything; pruning removes only what is not relevant. They work well together.",
         "কমপ্রেশন সবকিছু ছোট করে; প্রুনিং শুধু অপ্রাসঙ্গিক অংশ কাটে। দুটো একসাথে ভালো কাজ করে।")],
       [sh("chunks", x=110, y=70), sh("rerank", x=380, y=70), sh("top", x=640, y=70), sh("lingua", x=640, y=250)],
       [ln("chunks", "rerank", "to"), ln("rerank", "top", "to"), ln("top", "lingua", "to")],
       [None, None, None],
       points=[("Pruning keeps information density, or useful facts per token.",
                "প্রুনিং তথ্যের ঘনত্ব, মানে প্রতি টোকেনে কাজের তথ্য, ধরে রাখে।"),
               ("Compression reduces absolute size.",
                "কমপ্রেশন মোট আকার কমায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
