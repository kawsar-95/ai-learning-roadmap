"""RAG and Knowledge Systems · 09 Multi-hop retrieval patterns: IRCoT, ReAct, Self-RAG, CRAG and Adaptive-RAG: search, think, and search again.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Multi-hop  Body: "Some questions cannot be answered from one retrieval: the second search depends on what the first one found." Start here: "Multi-hop retrieval lets a model search, think, and search again."
  2 IRCoT      Start here: "A method that alternates searching with CoT steps. Each reasoning sentence becomes the query for the next search." Body: "retrieval gains of 11-21 points and QA gains of up to 15 F1", "up to 50% fewer factual errors in the CoT".
  3 ReAct      Start here: "A method that mixes reasoning steps with actions such as Wikipedia lookups." Body: "It reduced hallucination in QA and fact verification."
  4 Self-RAG   Start here: "Self-RAG lets the model decide when to retrieve and check its own output." Reflection tokens: "Special tokens that let the Self-RAG method's model critique the passages it found and its own output."
  5 CRAG       Start here: "A small evaluator rates how good the retrieval is. If it is poor, the system searches the web." "CRAG falls back to web search when retrieval from the corpus is not good enough."
  6 Adaptive   Start here: "A small classifier guesses how hard a question is, then picks no retrieval, one-step retrieval, or repeated retrieval."
  7 Remember   The four short points under Start here: IRCoT, Self-RAG, CRAG, Adaptive-RAG.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Question", "প্রশ্ন"), 80, 160),
    node("ret", "tool", ("Search", "খোঁজা"), 280, 80),
    node("llm", "model", ("Model", "মডেল"), 500, 80),
    node("nq", "note", ("Next query", "পরের কুয়েরি"), 390, 245),
    node("ans", "file", ("Final answer", "চূড়ান্ত উত্তর"), 665, 160),
    node("act", "tool", ("Wikipedia lookup", "Wikipedia লুকআপ"), 500, 245),
    node("ev", "service", ("Evaluator", "ইভ্যালুয়েটর"), 470, 160),
    node("web", "tool", ("Web search", "ওয়েব সার্চ"), 470, 255),
    node("cls", "service", ("Classifier", "ক্লাসিফায়ার"), 280, 160),
    node("none", "model", ("No retrieval", "রিট্রিভাল-ছাড়া"), 540, 65),
    node("single", "tool", ("One-step retrieval", "এক-ধাপ রিট্রিভাল"), 540, 160),
    node("iter", "queue", ("Repeated retrieval", "বহু-ধাপ রিট্রিভাল"), 540, 255),
]

METRICS = [
    ("Retrieval gain", "রিট্রিভালে উন্নতি"),
    ("QA gain", "QA-তে উন্নতি"),
    ("Factual errors", "তথ্যের ভুল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর হিসাব সেকশনের নিজস্ব।",
)

STEPS = [
    st(("Multi-hop", "মাল্টি-হপ"),
       ("The second search depends on the first", "দ্বিতীয় খোঁজ নির্ভর করে প্রথমের ওপর"),
       [("Some questions need more than one search, because the second search depends on what the first one found.",
         "কিছু প্রশ্নের উত্তর পেতে একবার খোঁজা যথেষ্ট নয়, কারণ দ্বিতীয় খোঁজ নির্ভর করে প্রথম খোঁজের ফলাফলের ওপর।"),
        ("Multi-hop retrieval lets a model search, think, and search again.",
         "মাল্টি-হপ রিট্রিভাল-এ মডেল খোঁজে, ভাবে, আবার খোঁজে।")],
       [sh("q", "hot"), sh("ret", "hot", ("first search", "প্রথম খোঁজ")), sh("nq", "hot", ("depends on the first", "প্রথমের ওপর নির্ভর"))],
       [ln("q", "ret", "to", state="hot"), ln("ret", "nq", "to", state="hot")],
       [None, None, None]),

    st(("IRCoT", "IRCoT"),
       ("IRCoT: each sentence is the next query", "IRCoT: প্রতিটি বাক্য পরের কুয়েরি"),
       [("IRCoT alternates searching with chain-of-thought (CoT) steps. Each reasoning sentence becomes the query for the next search.",
         "IRCoT খোঁজা আর CoT-এর ধাপ পালা করে চালায়। প্রতিটি যুক্তির বাক্য পরের খোঁজের কুয়েরি হয়।"),
        ("The paper reports retrieval gains of 11-21 points and QA gains of up to 15 F1.",
         "পেপারে রিট্রিভালে ১১-২১ পয়েন্ট ও QA-তে সর্বোচ্চ ১৫ F1 উন্নতির কথা আছে।")],
       [sh("q", "hot"), sh("ret", "hot"), sh("llm", "hot", ("next CoT sentence", "পরের CoT বাক্য")),
        sh("nq", "hot", ("last sentence", "শেষ বাক্য")), sh("ans", "hot")],
       [ln("q", "ret", "to", state="hot"), ln("ret", "llm", "to", state="hot"), ln("llm", "nq", "to", state="hot"),
        ln("nq", "ret", "to", state="hot"), ln("llm", "ans", "to", state="hot")],
       [("11-21 points", "১১-২১ পয়েন্ট"), ("up to 15 F1", "সর্বোচ্চ ১৫ F1"), ("up to 50% fewer", "সর্বোচ্চ ৫০% কম")]),

    st(("ReAct", "ReAct"),
       ("ReAct: reasoning mixed with actions", "ReAct: যুক্তির সাথে অ্যাকশন"),
       [("ReAct mixes reasoning steps with actions such as Wikipedia lookups.",
         "ReAct যুক্তির ধাপের সাথে Wikipedia লুকআপের মতো অ্যাকশন মিশিয়ে চলে।"),
        ("It reduced hallucination in QA and fact verification.",
         "এটি QA আর ফ্যাক্ট ভেরিফিকেশনে হ্যালুসিনেশন কমিয়েছে।")],
       [sh("q", "hot"), sh("llm", "hot", ("reasoning step", "যুক্তির ধাপ")), sh("act", "hot", ("action", "অ্যাকশন"))],
       [ln("q", "llm", "to", state="hot"), ln("llm", "act", "to", state="hot")],
       [None, None, None]),

    st(("Self-RAG", "Self-RAG"),
       ("Self-RAG: the model decides", "Self-RAG: মডেল নিজে ঠিক করে"),
       [("Self-RAG lets the model decide when to retrieve and check its own output.",
         "Self-RAG-এ মডেল নিজেই ঠিক করে কখন রিট্রিভ করবে, আর নিজের উত্তর যাচাই করে।"),
        ("Reflection tokens are special tokens that let it critique the passages it found and its own output.",
         "রিফ্লেকশন টোকেন বিশেষ টোকেন, যা দিয়ে মডেল পাওয়া লেখাগুলো আর নিজের উত্তর যাচাই করে।")],
       [sh("llm", "hot", ("reflection tokens", "রিফ্লেকশন টোকেন")), sh("ret", "hot", ("when it decides", "যখন ঠিক করে")), sh("ans", "hot", ("checked", "যাচাই করা"))],
       [ln("llm", "ret", "to", state="hot"), ln("llm", "ans", "to", state="hot")],
       [None, None, None]),

    st(("CRAG", "CRAG"),
       ("CRAG: evaluate, then correct", "CRAG: যাচাই করে সংশোধন"),
       [("In CRAG (Corrective RAG), a small evaluator rates how good the retrieval is.",
         "CRAG-এ (Corrective RAG) একটি ছোট ইভ্যালুয়েটর রিট্রিভাল কতটা ভালো তা মাপে।"),
        ("If it is poor, the system searches the web.",
         "খারাপ হলে সিস্টেম ওয়েবে খোঁজে।")],
       [sh("ret", "hot", ("from the corpus", "কর্পাস থেকে")), sh("ev", "hot", ("rates retrieval", "রিট্রিভাল মাপে")),
        sh("web", "warn", ("if poor", "খারাপ হলে")), sh("ans", "hot")],
       [ln("ret", "ev", "to", state="hot"), ln("ev", "web", "to", state="warn"), ln("ev", "ans", "to", state="hot"), ln("web", "ans", "to", state="warn")],
       [None, None, None]),

    st(("Adaptive", "Adaptive"),
       ("Adaptive-RAG: route by difficulty", "Adaptive-RAG: কঠিনতা অনুযায়ী পথ"),
       [("In Adaptive-RAG, a small classifier guesses how hard a question is.",
         "Adaptive-RAG-এ একটি ছোট ক্লাসিফায়ার প্রশ্ন কতটা কঠিন তা আন্দাজ করে।"),
        ("Then it picks no retrieval, one-step retrieval, or repeated retrieval.",
         "তারপর রিট্রিভাল-ছাড়া, এক-ধাপ বা বহু-ধাপের পথ বেছে দেয়।")],
       [sh("q", "hot"), sh("cls", "hot", ("guesses difficulty", "কঠিনতা আন্দাজ")), sh("none", "hot"), sh("single", "hot"), sh("iter", "hot")],
       [ln("q", "cls", "to", state="hot"), ln("cls", "none", "to", state="hot"), ln("cls", "single", "to", state="hot"), ln("cls", "iter", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Each pattern decides what to search next, and whether to search at all.",
         "প্রতিটি পদ্ধতি ঠিক করে পরে কী খুঁজবে, আর আদৌ খুঁজবে কি না।")],
       [sh("nq", "hot", ("IRCoT", "IRCoT")), sh("llm", "hot", ("Self-RAG", "Self-RAG")), sh("ev", "hot", ("CRAG", "CRAG")), sh("cls", "hot", ("Adaptive-RAG", "Adaptive-RAG"))],
       [],
       [None, None, None],
       points=[("In IRCoT, each reasoning sentence becomes the next query. The paper reports retrieval gains of 11-21 points.",
                "IRCoT-তে প্রতিটি যুক্তির বাক্য পরের কুয়েরি হয়। পেপারে রিট্রিভালে ১১-২১ পয়েন্ট উন্নতির কথা আছে।"),
               ("Self-RAG lets the model decide when to retrieve and check its own output.",
                "Self-RAG-এ মডেল নিজেই ঠিক করে কখন রিট্রিভ করবে, আর নিজের উত্তর যাচাই করে।"),
               ("CRAG falls back to web search when retrieval from the corpus is not good enough.",
                "কর্পাস থেকে রিট্রিভাল যথেষ্ট ভালো না হলে CRAG ওয়েব সার্চে ফিরে যায়।"),
               ("Adaptive-RAG sends each query down a path that matches how complex it is.",
                "Adaptive-RAG প্রতিটি প্রশ্নকে তার জটিলতা অনুযায়ী আলাদা পথে পাঠায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
