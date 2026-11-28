"""Reranking in practice: the two-stage funnel, Cohere, Voyage and BGE: a cheap search narrows to N, a reranker re-orders only those, and the top k go to the LLM.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Funnel    Body: "A good setup works in two stages: a cheap search over everything, then a reranker on only the survivors." Start here: "Two-stage funnel: A cheap first search over the whole corpus, then a reranker on only the N survivors. The top k go to the LLM."
  2 Cheap     Diagram: "stage 1: recall", "whole corpus: ANN / BM25 / hybrid", "cheap per doc: precomputed index, scores the whole corpus, tune for recall".
  3 Top N     Body: "How many results to retrieve (N) and how many to keep (k) is an engineering choice. Tune both against your own evaluation set."
  4 Rerank    Start here: "Cross-encoder: A model that reads the question and one document together. It makes one pass per pair, so its cost grows in line with N." Diagram: "stage 2: precision". Table: Cohere Rerank, Voyage rerankers, BAAI bge-reranker-v2-m3.
  5 Top k     Diagram: "top-k chunks to LLM", "LLM sees only what survives: fewer, better chunks, less noise in the prompt".
  6 Double N  Body: "Doubling N roughly doubles reranking latency and cost."
  7 Missed    Start here: "A reranker can only re-order what stage 1 returned. It cannot recover a missing passage."
  8 Remember  The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Question", "প্রশ্ন"), 90, 75),
    node("corpus", "database", ("Whole corpus", "পুরো কর্পাস"), 260, 250),
    node("s1", "service", ("Cheap search", "সস্তা খোঁজ"), 260, 75),
    node("n", "queue", ("Top N", "টপ N"), 430, 75),
    node("rr", "model", ("Reranker", "রিরেংকার"), 600, 75),
    node("k", "queue", ("Top k", "টপ k"), 600, 250),
    node("llm", "model", ("LLM", "LLM"), 430, 250),
]

METRICS = [
    ("Reranker passes", "রিরেংকারের পাস"),
    ("Cost", "খরচ"),
    ("Right passage", "সঠিক প্যাসেজ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Funnel", "ফানেল"),
       ("A two-stage funnel", "দুই ধাপের ফানেল"),
       [("A good setup works in two stages: a cheap search over everything, then a reranker on only the survivors.",
         "ভালো সেটআপ দুই ধাপে চলে: আগে সব কিছুর ওপর সস্তা খোঁজ, তারপর শুধু টিকে থাকাগুলোর ওপর রিরেংকার।"),
        ("The top k go to the LLM.",
         "সেরা k-টি যায় LLM-এর কাছে।")],
       [sh("q", "hot"), sh("s1", "hot"), sh("n", "hot"), sh("rr", "hot"), sh("k", "hot"), sh("llm", "hot")],
       [ln("q", "s1", "to", state="hot"), ln("s1", "n", "to", state="hot"), ln("n", "rr", "to", state="hot"),
        ln("rr", "k", "to", state="hot"), ln("k", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Cheap", "সস্তা"),
       ("Stage 1: a cheap search", "প্রথম ধাপ: সস্তা খোঁজ"),
       [("A cheap first search runs over the whole corpus, using ANN, BM25 or hybrid search.",
         "পুরো কর্পাসে সস্তা প্রথম খোঁজ চলে, ANN, BM25 বা হাইব্রিড সার্চ দিয়ে।"),
        ("It is cheap per document because the index is precomputed, and it is tuned for recall.",
         "প্রতি ডকুমেন্টে এটি সস্তা, কারণ ইনডেক্স আগেই তৈরি, আর এটি রিকলের জন্য সাজানো।")],
       [sh("q", "hot"), sh("corpus", "hot", ("whole corpus", "পুরো কর্পাস")), sh("s1", "hot", ("recall", "রিকল"))],
       [ln("q", "s1", "to", state="hot"), ln("corpus", "s1", "to", state="hot")],
       [None, None, None]),

    st(("Top N", "টপ N"),
       ("The N survivors", "টিকে থাকা N-টি"),
       [("The N survivors go on to the reranker. How many to retrieve (N) and how many to keep (k) is an engineering choice.",
         "টিকে থাকা N-টি রিরেংকারের কাছে যায়। কয়টি আনবেন (N) আর কয়টি রাখবেন (k), তা ইঞ্জিনিয়ারিংয়ের সিদ্ধান্ত।"),
        ("Tune both against your own evaluation set.",
         "দুটোই নিজের ইভ্যালুয়েশন সেটে ঠিক করুন।")],
       [sh("s1", "dim"), sh("n", "hot", ("survivors", "টিকে থাকা")), sh("rr", "dim")],
       [ln("s1", "n", "to", state="hot"), ln("n", "rr", "to", state="dim")],
       [None, None, None]),

    st(("Rerank", "রিরেংক"),
       ("Stage 2: the cross-encoder", "দ্বিতীয় ধাপ: ক্রস-এনকোডার"),
       [("A cross-encoder reads the question and one document together. It makes one pass per pair, so its cost grows in line with N.",
         "ক্রস-এনকোডার প্রশ্ন আর একটি ডকুমেন্ট একসাথে পড়ে। প্রতি জোড়ায় একবার চলে, তাই খরচ N-এর সাথে সমান তালে বাড়ে।"),
        ("This stage is tuned for precision.",
         "এই ধাপ প্রিসিশনের জন্য সাজানো।")],
       [sh("q", "dim"), sh("n", "hot"), sh("rr", "hot", ("per pair", "প্রতি জোড়ায়")), sh("k", "hot")],
       [ln("n", "rr", "to", state="hot"), ln("rr", "k", "to", state="hot")],
       [("one per pair", "প্রতি জোড়ায় একটি"), ("grows with N", "N-এর সাথে বাড়ে"), None],
       note=("tip", "Hosted options include Cohere Rerank and Voyage rerankers. Open weights include BAAI's BGE rerankers.",
             "হোস্টেড অপশনের মধ্যে আছে Cohere Rerank আর Voyage রিরেংকার। ওপেন ওয়েটের মধ্যে আছে BAAI-এর BGE রিরেংকার।")),

    st(("Top k", "টপ k"),
       ("Top k go to the LLM", "টপ k যায় LLM-এর কাছে"),
       [("The LLM sees only what survives: fewer, better chunks.",
         "LLM শুধু টিকে থাকাগুলোই দেখে: কম, কিন্তু ভালো চাঙ্ক।"),
        ("That means less noise in the prompt.",
         "অর্থাৎ প্রম্পটে গোলমাল কম।")],
       [sh("rr", "dim"), sh("k", "hot", ("better chunks", "ভালো চাঙ্ক")), sh("llm", "hot", ("less noise", "গোলমাল কম"))],
       [ln("rr", "k", "to", state="dim"), ln("k", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Double N", "N দ্বিগুণ"),
       ("Doubling N doubles the cost", "N দ্বিগুণ করলে খরচ দ্বিগুণ"),
       [("Doubling N roughly doubles reranking latency and cost.",
         "N দ্বিগুণ করলে রিরেংকিংয়ের ল্যাটেন্সি আর খরচ প্রায় দ্বিগুণ হয়।"),
        ("So tune N on your own evaluation set.",
         "তাই নিজের ইভ্যালুয়েশন সেটে N ঠিক করুন।")],
       [sh("n", "warn", ("N doubled", "N দ্বিগুণ")), sh("rr", "warn", ("grows with N", "N-এর সাথে বাড়ে"))],
       [ln("n", "rr", "to", state="warn")],
       [None, ("roughly doubles", "প্রায় দ্বিগুণ"), None]),

    st(("Missed", "বাদ পড়া"),
       ("A missed passage stays missed", "বাদ পড়া প্যাসেজ বাদই থাকে"),
       [("A reranker can only re-order what stage 1 returned.",
         "রিরেংকার শুধু প্রথম ধাপের আনা ফলই নতুন করে সাজায়।"),
        ("If the right passage is not in the top N, no reranker can recover it.",
         "সঠিক প্যাসেজ টপ N-এ না থাকলে কোনো রিরেংকার তা ফেরাতে পারে না।")],
       [sh("corpus", "warn", ("right passage", "সঠিক প্যাসেজ")), sh("s1", "dim"), sh("n", "warn", ("not in N", "N-এ নেই")), sh("rr", "dim")],
       [ln("corpus", "s1", "to", state="dim"), ln("s1", "n", "to", state="dim"), ln("n", "rr", "to", state="dim")],
       [None, None, ("not in N", "N-এ নেই")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A cheap search narrows the corpus, a reranker re-orders only the survivors, and the top k go to the LLM.",
         "সস্তা খোঁজ কর্পাস ছোট করে, রিরেংকার শুধু টিকে থাকাগুলো সাজায়, আর সেরা k যায় LLM-এর কাছে।")],
       [sh("s1"), sh("n"), sh("rr"), sh("k"), sh("llm")],
       [ln("s1", "n", "to"), ln("n", "rr", "to"), ln("rr", "k", "to"), ln("k", "llm", "to")],
       [None, None, None],
       points=[("Tune N and k on your own evaluation set; doubling N roughly doubles reranking latency and cost.",
                "নিজের ইভ্যালুয়েশন সেটে N আর k ঠিক করুন; N দ্বিগুণ করলে রিরেংকিংয়ের ল্যাটেন্সি আর খরচ প্রায় দ্বিগুণ হয়।"),
               ("A reranker can only re-order what stage 1 returned. It cannot recover a missing passage.",
                "রিরেংকার শুধু প্রথম ধাপের আনা ফলই নতুন করে সাজায়। যে অংশ আসেনি, তা ফেরাতে পারে না।"),
               ("Rerank chunks, not whole files, because token limits cut long documents.",
                "পুরো ফাইলের বদলে চাঙ্ক রিরেংক করুন, কারণ টোকেন সীমায় লম্বা ডকুমেন্ট কাটা পড়ে।"),
               ("Scores from different rerankers share no common scale, so pick score thresholds per model and per corpus.",
                "আলাদা রিরেংকারের স্কোর একই স্কেলে নয়, তাই থ্রেশহোল্ড মডেল আর কর্পাস ধরে ঠিক করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
