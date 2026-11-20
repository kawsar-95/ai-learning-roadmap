"""Part 5 · 11 How rerankers score: bi-encoders, cross-encoders and late interaction: a quick search, then a careful second look.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Stages    Sub-title: "First-stage retrieval (BM25, dense vectors, or both) is built to be fast over a huge corpus. It scores each document without ever looking at the query and document together. A reranker is a second-stage model that does look at them together: it takes the short candidate list and re-orders it by a more accurate relevance score."
  2 Bi        Body: "a bi-encoder embeds each text independently and compares the vectors with cosine similarity"; the diagram: the query and document meet "never until the final cosine (bi-encoder)"; Bangla voice: "ডকুমেন্ট ভেক্টর আগে থেকে তৈরি থাকে, তাই দ্রুত".
  3 Cross     Body: "A cross-encoder processes the pair jointly and outputs a score. It produces no reusable embedding, and it is more accurate but slower."; the cost example: "clustering 10,000 sentences with a cross-encoder needs about 50 million pairwise comparisons, roughly 65 hours."
  4 Late      Body, "Late interaction (ColBERT)": "BERT encodes the query and the document independently, so document representations can be computed offline. The score is MaxSim: for each query token, take the maximum cosine against the document's token vectors, then sum."; MaxSim ("For each question token, find its best match among the document's tokens, then add up those best scores.").
  5 Speed     Body: "The paper reports about 170x faster and 14,000x fewer FLOPs (floating-point operations) per query than BERT rerankers, at competitive quality on MS MARCO and TREC CAR."; FLOPs ("A count of how many arithmetic steps a computer must do."); limits: "late interaction stores one vector per token, which costs index space, and the speed figures are from the paper's own setup, not your hardware."
  6 System    Body: "A full system is a first-stage retriever followed by the reranker."; "Qdrant exposes the same idea operationally: prefetch cheap dense candidates, then rescore the top candidates with a multivector (ColBERT-style) model."
  7 Remember  Layman's voice: "It is slower and costs money for every document you ask it to read, so you can only afford to show it a short pile."; and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("query", "user", ("Question", "প্রশ্ন"), 110, 75),
    node("first", "database", ("Quick search", "দ্রুত সার্চ"), 380, 75),
    node("cands", "file", ("Short list", "ছোট তালিকা"), 650, 75),
    node("rerank", "model", ("Reranker", "রিরেংকার"), 380, 250),
    node("sorted", "note", ("Best first", "সেরা আগে"), 110, 250),
    node("doc", "file", ("Document", "ডকুমেন্ট"), 110, 250),
    node("encq", "model", ("Encoder", "এনকোডার"), 380, 75),
    node("encd", "model", ("Encoder", "এনকোডার"), 380, 250),
    node("cross", "model", ("Cross-encoder", "ক্রস-এনকোডার"), 380, 162),
    node("score", "chart", ("Score", "স্কোর"), 650, 162),
]

METRICS = [
    ("Sentences", "বাক্য"),
    ("Comparisons", "তুলনা"),
    ("Time", "সময়"),
    ("ColBERT", "ColBERT"),
]

CAPTION = (
    "Example: a question, a short list of documents, and how each kind of model scores a pair.",
    "উদাহরণ: একটি প্রশ্ন, ডকুমেন্টের ছোট তালিকা, আর প্রতিটি ধরনের মডেল একটি জোড়ায় কীভাবে স্কোর দেয়।",
)


def pipeline(state: str | None = "hot"):
    """Question, quick search, short list, reranker, best first."""
    return [ln("query", "first", "to", state=state), ln("first", "cands", "to", state=state),
            ln("cands", "rerank", "to", state=state), ln("rerank", "sorted", "to", state=state)]


def apart(state: str | None = "hot"):
    """Question and document are encoded on their own, and meet in the score."""
    return [ln("query", "encq", "to", state=state), ln("doc", "encd", "to", state=state),
            ln("encq", "score", "to", state=state), ln("encd", "score", "to", state=state)]


STEPS = [
    st(("Stages", "দুই ধাপ"),
       ("A quick search, then a careful second look", "আগে দ্রুত খোঁজ, তারপর যত্ন করে আরেকবার"),
       [("First-stage retrieval (BM25, dense vectors, or both) is built to be fast over a huge corpus. It scores each document without ever looking at the question and the document together.",
         "প্রথম ধাপের রিট্রিভাল (BM25, ডেন্স ভেক্টর, বা দুটোই) বিশাল কর্পাসে দ্রুত চলার জন্য বানানো। সে প্রতিটি ডকুমেন্টের স্কোর দেয় প্রশ্ন আর ডকুমেন্ট একসাথে না দেখেই।"),
        ("A reranker is a second-stage model that does look at them together. It takes the short candidate list and re-orders it by a more accurate relevance score.",
         "রিরেংকার দ্বিতীয় ধাপের মডেল, যে দুটো একসাথে দেখে। ছোট ক্যান্ডিডেট তালিকা নিয়ে আরও নিখুঁত রেলেভেন্স স্কোর দিয়ে সেটা নতুন করে সাজায়।")],
       [sh("query", "hot"), sh("first", "hot", ("fast, not very exact", "দ্রুত, তবে খুব নিখুঁত নয়")), sh("cands", "hot"),
        sh("rerank", "hot", ("reads both together", "দুটো একসাথে পড়ে")), sh("sorted", "hot", ("re-ordered", "নতুন করে সাজানো"))],
       pipeline(),
       [None, None, None, None]),

    st(("Bi-encoder", "বাই-এনকোডার"),
       ("Bi-encoder: apart until the end", "বাই-এনকোডার: শেষ পর্যন্ত আলাদা"),
       [("A bi-encoder embeds each text on its own, then compares the two vectors with cosine similarity. The question and the document never meet until that last comparison.",
         "বাই-এনকোডার প্রতিটি লেখাকে আলাদাভাবে এমবেড করে, তারপর দুটি ভেক্টর কোসাইন সিমিলারিটি দিয়ে মেলায়। শেষ তুলনার আগে প্রশ্ন আর ডকুমেন্ট কখনো মেলে না।"),
        ("It is fast, because the document vectors can be made ahead of time.",
         "এটি দ্রুত, কারণ ডকুমেন্টের ভেক্টর আগে থেকেই তৈরি করে রাখা যায়।")],
       [sh("query", "hot"), sh("doc", "hot"), sh("encq", "hot", ("embeds alone", "একা এমবেড করে")), sh("encd", "hot", ("embeds alone", "একা এমবেড করে")),
        sh("score", "hot", ("cosine at the end", "শেষে কোসাইন"))],
       apart(),
       [None, None, None, None]),

    st(("Cross-encoder", "ক্রস-এনকোডার"),
       ("Cross-encoder: together, but slow", "ক্রস-এনকোডার: একসাথে, কিন্তু ধীর"),
       [("A cross-encoder reads the question and the document together, inside one model, and outputs a single score. It produces no reusable embedding, so it is more accurate but slower.",
         "ক্রস-এনকোডার প্রশ্ন আর ডকুমেন্ট একসাথে একটি মডেলের ভেতরে পড়ে একটি স্কোর দেয়। এ থেকে আবার ব্যবহার করার মতো এমবেডিং তৈরি হয় না, তাই এটি বেশি নিখুঁত, কিন্তু ধীর।"),
        ("The Sentence-Transformers docs give a cost example: clustering 10,000 sentences with a cross-encoder needs about 50 million comparisons, roughly 65 hours.",
         "Sentence-Transformers-এর উদাহরণ: ক্রস-এনকোডারে ১০,০০০ বাক্য ক্লাস্টার করতে প্রায় ৫ কোটি তুলনা লাগে, প্রায় ৬৫ ঘণ্টা।")],
       [sh("query", "hot"), sh("doc", "hot"), sh("cross", "hot", ("reads both together", "দুটো একসাথে পড়ে")), sh("score", "hot", ("one score", "একটি স্কোর"))],
       [ln("query", "cross", "to", state="hot"), ln("doc", "cross", "to", state="hot"), ln("cross", "score", "to", state="hot")],
       [("10,000", "১০,০০০"), ("~50 million", "~৫ কোটি"), ("~65 hours", "~৬৫ ঘণ্টা"), None]),

    st(("Late interaction", "লেট ইন্টারঅ্যাকশন"),
       ("ColBERT: apart, then matched per token", "ColBERT: আলাদা এনকোড, টোকেন ধরে মেলানো"),
       [("ColBERT sits in between. BERT encodes the query and the document independently, so document representations can be computed offline.",
         "ColBERT মাঝামাঝি। BERT প্রশ্ন আর ডকুমেন্ট আলাদাভাবে এনকোড করে, তাই ডকুমেন্টের রিপ্রেজেন্টেশন অফলাইনে হিসাব করে রাখা যায়।"),
        ("The score is MaxSim: for each query token, take its best match among the document's tokens, then add up those best scores.",
         "স্কোর হলো MaxSim: প্রশ্নের প্রতিটি টোকেনের জন্য ডকুমেন্টের সবচেয়ে ভালো মেলা টোকেন খুঁজে, সেই সেরা স্কোরগুলো যোগ করা।")],
       [sh("query", "hot"), sh("doc", "hot"), sh("encq", "hot", ("encodes alone", "একা এনকোড করে")), sh("encd", "hot", ("computed offline", "অফলাইনে হিসাব")),
        sh("score", "hot", ("MaxSim per token", "টোকেন ধরে MaxSim"))],
       apart(),
       [None, None, None, None]),

    st(("Speed", "গতি"),
       ("ColBERT's speed, and its price", "ColBERT-এর গতি আর তার মূল্য"),
       [("The paper reports ColBERT at competitive quality on MS MARCO and TREC CAR, compared with BERT rerankers. FLOPs count the arithmetic steps a computer must do.",
         "পেপারের রিপোর্টে MS MARCO আর TREC CAR-এ ColBERT BERT রিরেংকারের কাছাকাছি মানের। FLOPs মানে কম্পিউটারকে কতগুলো হিসাবের ধাপ করতে হয়, তার গণনা।")],
       [sh("query", "hot"), sh("doc", "hot"), sh("encq", "hot"), sh("encd", "warn", ("one vector per token", "প্রতি টোকেনে একটি ভেক্টর")), sh("score", "hot")],
       apart(),
       [None, None, None, ("170x faster", "১৭০x দ্রুত")],
       changes=[("+", "About 170x faster per query than BERT rerankers", "BERT রিরেংকারের চেয়ে প্রতি কুয়েরিতে প্রায় ১৭০x দ্রুত"),
                ("+", "About 14,000x fewer FLOPs per query", "প্রতি কুয়েরিতে প্রায় ১৪,০০০x কম FLOPs")],
       note=("warn",
             "Late interaction stores one vector per token, which costs index space. These speed figures come from the paper's own setup, not your hardware.",
             "লেট ইন্টারঅ্যাকশনে প্রতি টোকেনে একটি ভেক্টর রাখতে হয়, তাই ইনডেক্সের জায়গা বেশি লাগে। এই গতির হিসাব পেপারের নিজস্ব সেটআপ থেকে নেওয়া, আপনার হার্ডওয়্যারের নয়।")),

    st(("System", "সিস্টেম"),
       ("Retriever first, reranker second", "আগে রিট্রিভার, তারপর রিরেংকার"),
       [("A full system is a first-stage retriever followed by a reranker.",
         "পুরো সিস্টেম হলো প্রথম ধাপের রিট্রিভার, তারপর একটি রিরেংকার।"),
        ("Qdrant exposes the same idea: prefetch cheap dense candidates, then rescore the top candidates with a multivector, ColBERT-style, model.",
         "Qdrant একই ধারণা দেয়: সস্তা ডেন্স ক্যান্ডিডেট আগে তুলে আনুন, তারপর মাল্টিভেক্টর (ColBERT-ধাঁচের) মডেল দিয়ে সেরা ক্যান্ডিডেটদের আবার স্কোর করুন।")],
       [sh("query", "hot"), sh("first", "hot", ("cheap first pass", "সস্তা প্রথম পাস")), sh("cands", "hot"),
        sh("rerank", "hot", ("rescores the top", "সেরাদের আবার স্কোর")), sh("sorted", "hot")],
       pipeline(),
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A reranker is slower and costs money for every document you ask it to read, so you can only afford to show it a short pile.",
         "রিরেংকার ধীর, আর যত ডকুমেন্ট পড়তে দেবেন প্রতিটির জন্য খরচ হয়; তাই তাকে শুধু ছোট একটি স্তূপই দেখানো পোষায়।")],
       [sh("query"), sh("first"), sh("cands"), sh("rerank"), sh("sorted")],
       pipeline(None),
       [None, None, None, None],
       points=[("A full system is a first-stage retriever followed by a reranker.",
                "পুরো সিস্টেম হলো প্রথম ধাপের রিট্রিভার, তারপর একটি রিরেংকার।"),
               ("A cross-encoder needs about 50 million comparisons, roughly 65 hours, to cluster 10,000 sentences.",
                "ক্রস-এনকোডারে ১০,০০০ বাক্য ক্লাস্টার করতে প্রায় ৫ কোটি তুলনা লাগে, প্রায় ৬৫ ঘণ্টা।"),
               ("ColBERT reports about 170x faster and 14,000x fewer FLOPs per query than BERT rerankers, at competitive quality.",
                "ColBERT-এর রিপোর্টে BERT রিরেংকারের চেয়ে প্রতি কুয়েরিতে প্রায় ১৭০x দ্রুত আর ১৪,০০০x কম FLOPs, কাছাকাছি মান বজায় রেখেই।"),
               ("These speed figures come from the paper's own setup, not your hardware.",
                "এই গতির হিসাব পেপারের নিজস্ব সেটআপ থেকে নেওয়া, আপনার হার্ডওয়্যারের নয়।"),
               ("Late interaction stores one vector per token, which costs index space.",
                "লেট ইন্টারঅ্যাকশনে প্রতি টোকেনে একটি ভেক্টর রাখতে হয়, তাই ইনডেক্সের জায়গা বেশি লাগে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
