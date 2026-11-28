"""RAG and Knowledge Systems · 07 Query rewriting, expansion & HyDE: change the query before the search, at the price of one extra LLM call.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Problem    Start here: "People write short, vague questions, but documents are written differently."
  2 Rewrite    Start here: "Query transformation rewrites or widens the question before the search, at the price of one extra LLM call."
  3 HyDE       Start here: "An LLM writes a made-up answer. The system searches using that answer's meaning, not the query's." Contriever: "The encoder HyDE uses to turn the made-up answer into numbers. It is expected to filter out the invented details."
  4 Rewriter   Start here, "Rewrite-Retrieve-Read": "Adds a rewriting step before retrieval. The rewriter can be a prompted LLM or a small trainable T5 model."
  5 Step-back  Start here: "First ask a broader, higher-level question, then reason to the answer. It is a reasoning method, not only a retrieval trick."
  6 Query2doc  Start here: "An LLM writes a made-up passage that is joined to the query. It helps keyword scoring (BM25) far more than embedding search." "On in-domain sets, Query2doc gains 3–15% for BM25 but only 0.4–4% for dense retrievers."
  7 Fusion     Start here, "RAG-Fusion": "Writes several query variants, searches with each, and merges the lists by each document's rank before the LLM answers."
  8 Remember   Pitfalls: extra LLM call, drift, false details, and "Keep the original query among the search strings, and measure on your own queries."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Query", "কুয়েরি"), 100, 80),
    node("llm", "model", ("LLM", "LLM"), 300, 80),
    node("fake", "note", ("Made-up text", "বানানো লেখা"), 520, 80),
    node("enc", "tool", ("Contriever", "Contriever"), 520, 250),
    node("ret", "tool", ("Search", "খোঁজা"), 300, 250),
    node("docs", "file", ("Real documents", "আসল নথি"), 110, 250),
    node("broad", "note", ("Broader question", "বড় প্রশ্ন"), 520, 80),
    node("bm25", "tool", ("BM25", "BM25"), 520, 250),
    node("dense", "tool", ("Dense search", "ডেন্স সার্চ"), 300, 250),
    node("vars", "queue", ("Query variants", "কুয়েরি ভ্যারিয়েন্ট"), 300, 80),
    node("fuse", "chart", ("Merge by rank", "র‍্যাংক ধরে মেলানো"), 520, 250),
]

METRICS = [
    ("Extra cost", "বাড়তি খরচ"),
    ("BM25 gain", "BM25-এ লাভ"),
    ("Dense gain", "ডেন্সে লাভ"),
    ("Drift", "সরে যাওয়া"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর হিসাব সেকশনের নিজস্ব।",
)

STEPS = [
    st(("Problem", "সমস্যা"),
       ("Short questions, different words", "ছোট প্রশ্ন, আলাদা শব্দ"),
       [("People write short, vague questions, but documents are written differently.",
         "ব্যবহারকারীর প্রশ্ন ছোট ও অস্পষ্ট হয়, উত্তরের নথির মতো নয়।")],
       [sh("q", "hot", ("short, vague", "ছোট, অস্পষ্ট")), sh("docs", "warn", ("written differently", "অন্যভাবে লেখা"))],
       [ln("q", "docs", "to", state="warn")],
       [None, None, None, None]),

    st(("Rewrite", "রিরাইট"),
       ("A step before the search", "খোঁজার আগে একটি ধাপ"),
       [("Query transformation rewrites or widens the question before the search.",
         "কুয়েরি ট্রান্সফরমেশন খোঁজার আগে প্রশ্ন নতুন করে লেখে বা বাড়ায়।"),
        ("The price is one extra LLM call.",
         "এর দাম একটি বাড়তি LLM কল।")],
       [sh("q", "hot"), sh("llm", "hot", ("one extra call", "একটি বাড়তি কল")), sh("ret", "hot"), sh("docs", "hot")],
       [ln("q", "llm", "to", state="hot"), ln("llm", "ret", "to", state="hot"), ln("ret", "docs", "to", state="hot")],
       [("one extra LLM call", "একটি বাড়তি LLM কল"), None, None, None]),

    st(("HyDE", "HyDE"),
       ("HyDE: search with a made-up answer", "HyDE: বানানো উত্তর দিয়ে খোঁজা"),
       [("An LLM writes a made-up answer. The system searches using that answer's meaning, not the query's.",
         "LLM প্রশ্নের একটি বানানো উত্তর লেখে। সেই উত্তরের অর্থ ধরে খোঁজা হয়, প্রশ্নের নয়।"),
        ("Contriever turns the made-up answer into numbers. It is expected to filter out the invented details.",
         "Contriever বানানো উত্তরকে সংখ্যায় বদলায়। আশা করা হয়, এটি বানানো খুঁটিনাটি ছেঁটে ফেলে।")],
       [sh("q", "dim"), sh("llm", "hot"), sh("fake", "warn", ("false details", "ভুল তথ্য")),
        sh("enc", "hot"), sh("ret", "hot"), sh("docs", "hot")],
       [ln("q", "llm", "to", state="dim"), ln("llm", "fake", "to", state="hot"), ln("fake", "enc", "to", state="hot"),
        ln("enc", "ret", "to", state="hot"), ln("ret", "docs", "to", state="hot")],
       [None, None, None, ("false details", "ভুল তথ্য")]),

    st(("Rewriter", "রিরাইটার"),
       ("Rewrite-Retrieve-Read", "Rewrite-Retrieve-Read পদ্ধতি"),
       [("It adds a rewriting step before retrieval.",
         "খোঁজার আগে একটি নতুন করে লেখার ধাপ বসায়।"),
        ("The rewriter can be a prompted LLM or a small trainable T5 model.",
         "রিরাইটার হতে পারে প্রম্পট করা LLM বা প্রশিক্ষণযোগ্য ছোট T5 মডেল।")],
       [sh("q", "hot"), sh("llm", "hot", ("prompted or T5", "প্রম্পট বা T5")), sh("ret", "hot"), sh("docs", "hot")],
       [ln("q", "llm", "to", state="hot"), ln("llm", "ret", "to", state="hot"), ln("ret", "docs", "to", state="hot")],
       [None, None, None, None]),

    st(("Step-back", "স্টেপ-ব্যাক"),
       ("Step-back prompting", "স্টেপ-ব্যাক প্রম্পটিং"),
       [("First ask a broader, higher-level question, then reason to the answer.",
         "আগে একটি বড় ও সাধারণ প্রশ্ন করা, তারপর যুক্তি দিয়ে উত্তরে যাওয়া।"),
        ("It is a reasoning method, not only a retrieval trick.",
         "এটি রিজনিং পদ্ধতি, শুধু খোঁজার কৌশল নয়।")],
       [sh("q", "hot"), sh("llm", "hot", ("then reasons", "তারপর যুক্তি")), sh("broad", "hot")],
       [ln("q", "llm", "to", state="hot"), ln("llm", "broad", "to", state="hot")],
       [None, None, None, None]),

    st(("Query2doc", "Query2doc"),
       ("Query2doc: join a made-up passage", "Query2doc: বানানো লেখা জোড়া"),
       [("An LLM writes a made-up passage that is joined to the query. It helps keyword scoring (BM25) far more than embedding search.",
         "LLM একটি বানানো লেখা তৈরি করে, যা মূল কুয়েরির সাথে জোড়া হয়। এটি এমবেডিং সার্চের তুলনায় কীওয়ার্ড স্কোর (BM25)-কে অনেক বেশি সাহায্য করে।"),
        ("On in-domain sets, Query2doc gains 3–15% for BM25 but only 0.4–4% for dense retrievers.",
         "ইন-ডোমেইন সেটে Query2doc BM25-এ ৩–১৫% লাভ দেয়, কিন্তু ডেন্স রিট্রিভারে মাত্র ০.৪–৪%।")],
       [sh("q", "hot"), sh("llm", "hot"), sh("fake", "hot", ("joined to query", "কুয়েরিতে জোড়া")),
        sh("bm25", "hot", ("3–15%", "৩–১৫%")), sh("dense", "dim", ("0.4–4%", "০.৪–৪%"))],
       [ln("q", "llm", "to", state="hot"), ln("llm", "fake", "to", state="hot"),
        ln("fake", "bm25", "to", state="hot"), ln("fake", "dense", "to", state="dim")],
       [None, ("3–15%", "৩–১৫%"), ("0.4–4%", "০.৪–৪%"), None]),

    st(("Fusion", "ফিউশন"),
       ("RAG-Fusion: several variants", "RAG-Fusion: কয়েকটি ভ্যারিয়েন্ট"),
       [("RAG-Fusion writes several query variants and searches with each.",
         "RAG-Fusion প্রশ্নের কয়েকটি ভ্যারিয়েন্ট বানায়, প্রতিটি দিয়ে খোঁজে।"),
        ("It merges the lists by each document's rank before the LLM answers.",
         "তারপর LLM উত্তর দেওয়ার আগে র‍্যাংক ধরে তালিকাগুলো মেলায়।")],
       [sh("q", "hot"), sh("vars", "hot", ("several", "কয়েকটি")), sh("ret", "hot", ("one each", "প্রতিটির জন্য")), sh("fuse", "hot")],
       [ln("q", "vars", "to", state="hot"), ln("vars", "ret", "to", state="hot"), ln("ret", "fuse", "to", state="hot")],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Keep the original query among the search strings, and measure on your own queries.",
         "মূল কুয়েরি সার্চের তালিকায় রাখুন, আর নিজের কুয়েরিতে মেপে দেখুন।")],
       [sh("q", "hot", ("keep original", "মূলটা রাখুন")), sh("llm", "warn", ("one extra call", "একটি বাড়তি কল")), sh("ret", "hot")],
       [ln("q", "ret", "to", state="hot"), ln("q", "llm", "to", state="warn"), ln("llm", "ret", "to", state="warn")],
       [("one extra LLM call", "একটি বাড়তি LLM কল"), None, None, ("may drift", "সরে যেতে পারে")],
       points=[("Every rewrite adds one extra LLM call, so delay and cost grow before the first search.",
                "প্রতিটি রিরাইটে একটি বাড়তি LLM কল লাগে, তাই প্রথম সার্চের আগেই দেরি আর খরচ বাড়ে।"),
               ("Generated variants can drift from what the user meant. HyDE's made-up text may hold false details.",
                "তৈরি ভ্যারিয়েন্ট ব্যবহারকারীর উদ্দেশ্য থেকে সরে যেতে পারে। HyDE-এর বানানো লেখায় ভুল তথ্য থাকতে পারে।"),
               ("On in-domain sets, Query2doc gains 3–15% for BM25 but only 0.4–4% for dense retrievers.",
                "ইন-ডোমেইন সেটে Query2doc BM25-এ ৩–১৫% লাভ দেয়, কিন্তু ডেন্স রিট্রিভারে মাত্র ০.৪–৪%।"),
               ("Keep the original query among the search strings, and measure on your own queries.",
                "মূল কুয়েরি সার্চের তালিকায় রাখুন, আর নিজের কুয়েরিতে মেপে দেখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
