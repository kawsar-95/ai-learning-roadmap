"""Part 1 · 09 Embedding models & reranker models: embeddings find candidates fast, a reranker checks the best of them.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Question  Layman's voice: a knowledge base of "10,000-doc" and "10 million docs"; Start here: "a system first finds the right pieces fast, then checks them carefully".
  2 Embed     Start here: Embedding ("A list of numbers that stands for the meaning of a text. Texts with similar meanings get similar numbers."), Vector ("Another name for that list").
              Body: "Encode each side (query and document) independently into a fixed-size vector."
  3 Search    Start here: Cosine similarity ("how much two vectors point the same way. A high score means the texts have similar meanings").
              Body: "O(1) per pair, allowing billion-scale approximate nearest-neighbour (ANN) search". Layman's voice: "narrows 10 million docs → 100 likely candidates".
  4 Rerank    Start here: Reranker (cross-encoder) ("reads the question and one document together and scores how well they match").
              Body: "much more accurate but O(n) per pair. Best used as the second stage on top-K=100 candidates"; the table: "~50–200 ms per (q, d) pair".
  5 Answer    Layman's voice: "Reranker picks the best 5 from those 100 ... The LLM reads those 5 and writes the final answer". Start here: RAG.
  6 Hybrid    Start here: BM25 ("documents that share the question's words score higher"), Hybrid retrieval ("usually beats either one alone").
  7 Remember  The three "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ব্যবহারকারী"), 90, 75),
    node("docs", "storage", ("Your documents", "আপনার ডকুমেন্ট"), 90, 250),
    node("embed", "model", ("Embedding model", "এমবেডিং মডেল"), 285, 75),
    node("index", "database", ("Vector index", "ভেক্টর ইনডেক্স"), 475, 75),
    node("rerank", "model", ("Reranker", "রিরেংকার"), 670, 75),
    node("llm", "model", ("LLM", "LLM"), 670, 250),
    node("bm25", "service", ("BM25 keywords", "BM25 কিওয়ার্ড"), 285, 250),
]

METRICS = [
    ("Documents left", "বাকি ডকুমেন্ট"),
    ("Time for one pair", "এক জোড়ার সময়"),
]

CAPTION = ("Example numbers from this section.", "উদাহরণের সংখ্যাগুলো এই সেকশন থেকে নেওয়া।")

MILLION = ("10 million", "১ কোটি")
FAST = ("fast", "দ্রুত")

STEPS = [
    st(("Question", "প্রশ্ন"),
       ("A question about your own documents", "আপনার নিজের ডকুমেন্ট নিয়ে একটি প্রশ্ন"),
       [("A user asks a question that your own documents can answer. There are 10 million of them.",
         "ব্যবহারকারী এমন একটি প্রশ্ন করে, যার উত্তর আপনার নিজের ডকুমেন্টে আছে। ডকুমেন্ট আছে ১ কোটি।"),
        ("A system cannot read them all for every question. It first finds the right pieces fast, then checks them carefully.",
         "প্রতিটি প্রশ্নের জন্য সবগুলো ডকুমেন্ট পড়া সম্ভব নয়। তাই সিস্টেম আগে দ্রুত ঠিক অংশগুলো খোঁজে, তারপর যত্ন করে যাচাই করে।")],
       [sh("user", "hot", sub=("asks a question", "প্রশ্ন করে")), sh("docs", sub=MILLION)],
       [],
       [MILLION, None]),

    st(("Embed", "এমবেডিং"),
       ("An embedding model turns text into numbers", "এমবেডিং মডেল লেখাকে সংখ্যায় বদলায়"),
       [("The embedding model turns the question and each document into an embedding: a list of numbers that stands for the meaning of a text. This list is also called a vector.",
         "এমবেডিং মডেল প্রশ্ন আর প্রতিটি ডকুমেন্টকে এমবেডিংয়ে বদলায়। এমবেডিং হলো একটি লেখার অর্থ বোঝানো সংখ্যার তালিকা, যাকে ভেক্টরও বলে।"),
        ("Texts with similar meanings get similar numbers.",
         "কাছাকাছি অর্থের লেখা কাছাকাছি সংখ্যা পায়।")],
       [sh("user", "dim"), sh("docs", "dim", sub=MILLION), sh("embed", "hot", sub=("text → numbers", "লেখা → সংখ্যা"))],
       [ln("user", "embed", "to", state="hot"), ln("docs", "embed", "to", state="hot")],
       [MILLION, None],
       note=("insight",
             "Each side, the question and the document, is turned into numbers on its own.",
             "প্রশ্ন আর ডকুমেন্ট, প্রত্যেকটাকে আলাদাভাবে সংখ্যায় বদলানো হয়।")),

    st(("Search", "খোঁজা"),
       ("Stage 1: find candidates fast", "স্টেজ ১: দ্রুত ক্যান্ডিডেট খোঁজা"),
       [("The question's numbers are compared with the documents' numbers. Cosine similarity scores how much two vectors point the same way: a high score means similar meanings.",
         "প্রশ্নের সংখ্যার সঙ্গে ডকুমেন্টগুলোর সংখ্যা মিলিয়ে দেখা হয়। কোসাইন সিমিলারিটি বলে দুটি ভেক্টর কতটা একই দিকে তাক করে আছে; স্কোর বেশি মানে অর্থ কাছাকাছি।"),
        ("This is fast enough to search billions of vectors. It narrows 10 million documents to about 100 candidates.",
         "এটা এত দ্রুত যে বিলিয়ন-স্কেল ভেক্টরেও খোঁজা যায়। ১ কোটি ডকুমেন্ট থেকে প্রায় ১০০টি ক্যান্ডিডেটে নেমে আসে।")],
       [sh("embed", "dim"), sh("index", "hot", sub=("100 candidates", "১০০ ক্যান্ডিডেট"))],
       [ln("embed", "index", "to", state="hot")],
       ["100", FAST],
       changes=[("-", "10 million documents → about 100 candidates", "১ কোটি ডকুমেন্ট → প্রায় ১০০ ক্যান্ডিডেট")]),

    st(("Rerank", "যাচাই"),
       ("Stage 2: a reranker reads each pair together", "স্টেজ ২: রিরেংকার প্রতিটি জোড়া একসাথে পড়ে"),
       [("A reranker, also called a cross-encoder, reads the question and one document together and scores how well they match.",
         "রিরেংকার, যাকে ক্রস-এনকোডারও বলে, প্রশ্ন আর একটি ডকুমেন্ট একসাথে পড়ে এবং দুটো কতটা মেলে তার স্কোর দেয়।"),
        ("This is more accurate but slower: about 50–200 ms for each pair. So it only sees the 100 candidates, not the 10 million documents.",
         "এটা বেশি নির্ভুল, কিন্তু ধীর: প্রতি জোড়ায় প্রায় ৫০–২০০ ms। তাই রিরেংকার শুধু ১০০টি ক্যান্ডিডেট দেখে, ১ কোটি ডকুমেন্ট নয়।")],
       [sh("index", "dim", sub=("100 candidates", "১০০ ক্যান্ডিডেট")), sh("rerank", "hot", sub=("careful, slower", "যত্ন করে, ধীরে"))],
       [ln("index", "rerank", "to", state="hot")],
       ["100", "50–200 ms"],
       changes=[("+", "Each candidate gets a careful score", "প্রতিটি ক্যান্ডিডেট যত্ন করে স্কোর পায়")]),

    st(("Answer", "উত্তর"),
       ("The best few go to the LLM", "সেরা কয়েকটি LLM পায়"),
       [("The reranker picks the best 5 of the 100. The LLM reads those 5 pieces and writes the final answer.",
         "রিরেংকার ১০০টির মধ্য থেকে সেরা ৫টি বাছে। LLM সেই ৫টি অংশ পড়ে আর চূড়ান্ত উত্তর লেখে।"),
        ("This is retrieval-augmented generation, RAG: find the relevant text first, then answer from that text.",
         "একেই বলে রিট্রিভাল-অগমেন্টেড জেনারেশন, RAG: আগে দরকারি লেখা খুঁজে নেওয়া, তারপর সেই লেখা থেকে উত্তর দেওয়া।")],
       [sh("rerank", "dim", sub=("best 5", "সেরা ৫টি")), sh("llm", "hot", sub=("reads 5 pieces", "৫টি অংশ পড়ে"))],
       [ln("rerank", "llm", "to", state="hot", label=("best 5", "সেরা ৫"))],
       ["5", "50–200 ms"],
       changes=[("-", "100 candidates → the best 5", "১০০ ক্যান্ডিডেট → সেরা ৫টি")]),

    st(("Hybrid", "হাইব্রিড"),
       ("Keywords and meaning work better together", "কিওয়ার্ড আর অর্থ একসাথে ভালো কাজ করে"),
       [("BM25 is a classic keyword score: documents that share the question's words score higher. Hybrid retrieval uses it together with embedding search.",
         "BM25 কিওয়ার্ড দিয়ে খোঁজার পুরনো স্কোর: প্রশ্নের শব্দ যে ডকুমেন্টে আছে, সেটা বেশি স্কোর পায়। হাইব্রিড রিট্রিভাল এটাকে এমবেডিং সার্চের সঙ্গে একসাথে ব্যবহার করে।"),
        ("On standard retrieval tests, this usually beats either one alone.",
         "প্রচলিত রিট্রিভাল পরীক্ষায় এটা সাধারণত যেকোনো একটার চেয়ে ভালো করে।")],
       [sh("docs", "dim", sub=MILLION), sh("embed", "hot"), sh("bm25", "hot", sub=("keyword score", "কিওয়ার্ড স্কোর")),
        sh("index", "hot", sub=("100 candidates", "১০০ ক্যান্ডিডেট"))],
       [ln("docs", "embed", "to", state="dim"), ln("docs", "bm25", "to", state="dim"),
        ln("embed", "index", "to", state="hot"), ln("bm25", "index", "to", state="hot")],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Two stages, one pipeline: a fast search first, a careful check second.",
         "দুই স্টেজ, একটাই পাইপলাইন: আগে দ্রুত খোঁজা, তারপর যত্ন করে যাচাই।")],
       [sh("user"), sh("embed"), sh("index"), sh("rerank"), sh("llm")],
       [ln("user", "embed", "to"), ln("embed", "index", "to"), ln("index", "rerank", "to"), ln("rerank", "llm", "to")],
       [None, None],
       points=[("Stage 1: embeddings narrow millions of documents down to a few hundred, fast.",
                "স্টেজ ১: এমবেডিং লাখ লাখ ডকুমেন্ট থেকে দ্রুত কয়েকশোতে নামিয়ে আনে।"),
               ("Stage 2: a reranker picks the best few. It is more accurate, but slower.",
                "স্টেজ ২: রিরেংকার সেরা কয়েকটি বাছে। এটা বেশি নির্ভুল, কিন্তু ধীর।"),
               ("On standard tests, keyword search (BM25) plus embeddings usually beats either alone.",
                "প্রচলিত পরীক্ষায় কিওয়ার্ড সার্চ (BM25) আর এমবেডিং মেলালে সাধারণত যেকোনো একটার চেয়ে ভালো ফল আসে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
