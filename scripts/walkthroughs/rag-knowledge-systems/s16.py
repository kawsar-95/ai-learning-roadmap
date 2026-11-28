"""RAG and Knowledge Systems · Choosing a vector database: key settings, filtered search and fit: the settings worth knowing, why filtered search is where engines differ, and which database to lean toward.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Index     Start here: "A few settings decide how well a vector database finds close matches." "HNSW index: A map of vectors that lets a search find close ones fast, without checking every vector."
  2 Build     Start here: "pgvector HNSW defaults: m 16 and ef_construction 64." Facts table: "pgvector HNSW defaults: m 16, ef_construction 64".
  3 Query     Start here: "hnsw.ef_search: A query-time setting that trades speed against recall. The pgvector default is 40."
  4 Quantize  Start here: "Quantization: Storing vectors in a smaller form to save memory. Qdrant claims up to 97% less RAM."
  5 Filtered  Start here: "Filtered search: Searching only among items that match a condition on their metadata, such as one customer's files." "Filtered search is where engines differ".
  6 Engines   Callout: "Qdrant's docs say payload indexes let it filter during a single graph traversal. pgvector offers partial indexes, partitioning and iterative index scans for filtered queries."
  7 Test      Start here: "test real filters at your real selectivity (how much of the data the filter keeps)." "A recall number measured without filters says little about filtered queries." Layman: "a shortcut map that ignores filters can return too few results".
  8 Fit       The \"When to choose what\" table, each row. "The when-to-choose table is the author's own inference, not vendor advice."
  9 Remember  Start here points: the defaults, test real filters, the table is the author's inference.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Query", "কুয়েরি"), 90, 162),
    node("idx", "service", ("HNSW index", "HNSW ইনডেক্স"), 340, 162),
    node("store", "database", ("Vectors", "ভেক্টর"), 620, 162),
    node("quant", "tool", ("Quantization", "কোয়ান্টাইজেশন"), 340, 270),
    node("filt", "shield", ("Metadata filter", "মেটাডেটা ফিল্টার"), 200, 162),
    node("payload", "key", ("Payload index", "পেলোড ইনডেক্স"), 470, 75),
    node("pg", "database", ("pgvector", "pgvector"), 470, 250),
    node("test", "chart", ("Your real filters", "আপনার আসল ফিল্টার"), 520, 162),
    node("sit", "user", ("Your situation", "আপনার পরিস্থিতি"), 150, 162),
    node("pick", "service", ("Lean toward", "যেটার দিকে ঝুঁকবেন"), 580, 162),
]

METRICS = [
    ("m", "m"),
    ("ef_construction", "ef_construction"),
    ("hnsw.ef_search", "hnsw.ef_search"),
    ("RAM", "RAM"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর সংখ্যা সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Index", "ইনডেক্স"),
       ("A few settings decide recall", "কয়েকটি সেটিং ঠিক করে"),
       [("A few settings decide how well a vector database finds close matches.",
         "ভেক্টর ডেটাবেস কাছের জিনিস কতটা ভালো খোঁজে, তা ঠিক করে কয়েকটি সেটিং।"),
        ("The HNSW index is a map of vectors that lets a search find close ones fast, without checking every vector.",
         "HNSW ইনডেক্স ভেক্টরের এমন একটি মানচিত্র, যা দিয়ে প্রতিটি ভেক্টর না দেখেই কাছের ভেক্টর দ্রুত খোঁজা যায়।")],
       [sh("q", "hot"), sh("idx", "hot", ("a map of vectors", "ভেক্টরের মানচিত্র")), sh("store", "hot")],
       [ln("q", "idx", "to", state="hot"), ln("idx", "store", "to", state="hot")],
       [None, None, None, None]),

    st(("Build", "বিল্ড"),
       ("pgvector's HNSW defaults", "pgvector-এর HNSW ডিফল্ট"),
       [("pgvector HNSW defaults: m 16 and ef_construction 64.",
         "pgvector HNSW-এর ডিফল্ট: m ১৬ আর ef_construction ৬৪।")],
       [sh("idx", "hot", ("m, ef_construction", "m, ef_construction")), sh("store", "dim")],
       [ln("idx", "store", "to", state="dim")],
       ["16", "64", None, None]),

    st(("Query", "কুয়েরি"),
       ("The query-time setting", "কুয়েরির সময়ের সেটিং"),
       [("hnsw.ef_search is a query-time setting that trades speed against recall.",
         "hnsw.ef_search কুয়েরির সময় বদলানো যায় এমন সেটিং, যা গতি আর রিকলের মধ্যে ভারসাম্য আনে।"),
        ("The pgvector default is 40.",
         "pgvector-এ ডিফল্ট ৪০।")],
       [sh("q", "hot", ("hnsw.ef_search", "hnsw.ef_search")), sh("idx", "hot"), sh("store", "hot")],
       [ln("q", "idx", "to", state="hot"), ln("idx", "store", "to", state="hot")],
       [None, None, "40", None]),

    st(("Quantize", "কোয়ান্টাইজ"),
       ("Quantization saves memory", "কোয়ান্টাইজেশন মেমরি বাঁচায়"),
       [("Quantization stores vectors in a smaller form to save memory.",
         "কোয়ান্টাইজেশন ভেক্টরকে ছোট আকারে রেখে মেমরি বাঁচায়।"),
        ("Qdrant claims up to 97% less RAM.",
         "Qdrant দাবি করে RAM ৯৭% পর্যন্ত কমে।")],
       [sh("idx", "hot"), sh("quant", "hot", ("smaller form", "ছোট আকার")), sh("store", "hot")],
       [ln("quant", "idx", "to", state="hot"), ln("idx", "store", "to", state="hot")],
       [None, None, None, ("up to 97% less", "৯৭% পর্যন্ত কম")],
       note=("info", "This is Qdrant's claim, not a number measured here.",
             "এটা Qdrant-এর দাবি, এখানে মাপা সংখ্যা নয়।")),

    st(("Filtered", "ফিল্টার"),
       ("Filtered search", "ফিল্টার-সহ সার্চ"),
       [("Filtered search looks only among items that match a condition on their metadata, such as one customer's files.",
         "ফিল্টার-সহ সার্চ মেটাডেটার কোনো শর্ত মেলে এমন আইটেমের মধ্যেই খোঁজে, যেমন শুধু একজন গ্রাহকের ফাইল।"),
        ("This is where engines differ.",
         "এখানেই ইঞ্জিনগুলো আলাদা।")],
       [sh("q", "hot", x=90), sh("filt", "hot", ("one customer's files", "একজন গ্রাহকের ফাইল"), x=330), sh("idx", "hot", x=570)],
       [ln("q", "filt", "to", state="hot"), ln("filt", "idx", "to", state="hot")],
       [None, None, None, None]),

    st(("Engines", "ইঞ্জিন"),
       ("How two engines filter", "দুই ইঞ্জিন কীভাবে ফিল্টার করে"),
       [("Qdrant's payload index lets filtering happen during a single pass through the graph.",
         "মেটাডেটার ফিল্ডের ওপর Qdrant-এর পেলোড ইনডেক্স গ্রাফে একবার খোঁজার সময়ই ফিল্টার করতে দেয়।"),
        ("pgvector offers partial indexes, partitioning and iterative index scans for filtered queries.",
         "pgvector ফিল্টার-সহ কুয়েরির জন্য পার্শিয়াল ইনডেক্স, পার্টিশনিং আর ইটারেটিভ ইনডেক্স স্ক্যান দেয়।")],
       [sh("filt", "hot"), sh("payload", "hot", ("Qdrant: one pass", "Qdrant: একবারে")), sh("pg", "hot", ("partial indexes", "পার্শিয়াল ইনডেক্স"))],
       [ln("filt", "payload", "to", state="hot"), ln("filt", "pg", "to", state="hot")],
       [None, None, None, None]),

    st(("Test", "পরীক্ষা"),
       ("Test your real filters", "আপনার আসল ফিল্টার পরীক্ষা করুন"),
       [("Test real filters at your real selectivity, which is how much of the data the filter keeps.",
         "নিজের আসল ফিল্টার আর আসল সিলেকটিভিটিতে (ফিল্টার ডেটার কতটা অংশ রাখে) পরীক্ষা করুন।"),
        ("A recall number measured without filters says little about filtered queries.",
         "ফিল্টার ছাড়া মাপা রিকল ফিল্টার-সহ কুয়েরি সম্পর্কে খুব কম বলে।")],
       [sh("filt", "warn"), sh("test", "hot", ("real selectivity", "আসল সিলেকটিভিটি"))],
       [ln("filt", "test", "to", state="warn")],
       [None, None, None, None],
       note=("warn", "A shortcut map that ignores filters can return too few results.",
             "যে শর্টকাট মানচিত্র ফিল্টার উপেক্ষা করে, সে খুব কম ফল ফেরত দিতে পারে।")),

    st(("Fit", "পছন্দ"),
       ("Which one to lean toward", "কোনটির দিকে ঝুঁকবেন"),
       [("The best pick depends on your situation. The when-to-choose table is the author's own inference, not vendor advice.",
         "সেরা বাছাই নির্ভর করে আপনার পরিস্থিতির ওপর। কোনটি কখন, এই তালিকা লেখকের নিজের অনুমান, বিক্রেতার পরামর্শ নয়।")],
       [sh("sit", "hot"), sh("pick", "hot")],
       [ln("sit", "pick", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "Data already in Postgres; want transactions and joins: pgvector",
                 "ডেটা আগে থেকেই Postgres-এ; লেনদেন আর জয়েন চান: pgvector"),
                ("+", "Prototype or laptop-scale experiment: Chroma (local mode)",
                 "প্রোটোটাইপ বা ল্যাপটপ-মাপের পরীক্ষা: Chroma (লোকাল মোড)"),
                ("+", "Minimal operations, managed service: Pinecone, or a managed tier of Qdrant, Chroma or Milvus",
                 "ন্যূনতম অপারেশন, ম্যানেজড সার্ভিস: Pinecone, বা Qdrant, Chroma অথবা Milvus-এর ম্যানেজড টিয়ার"),
                ("+", "Self-hosted, filter-heavy search: Qdrant",
                 "নিজে হোস্ট করা, ফিল্টার-নির্ভর সার্চ: Qdrant"),
                ("+", "Very large, distributed deployment on Kubernetes: Milvus",
                 "খুব বড়, Kubernetes-এ বিতরিত ডিপ্লয়মেন্ট: Milvus"),
                ("+", "Built-in hybrid fusion with tunable alpha, or many tenants: Weaviate",
                 "টিউন করা যায় এমন অ্যালফা-সহ বিল্ট-ইন হাইব্রিড ফিউশন, বা অনেক টেন্যান্ট: Weaviate")],
       ),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A few settings decide how well a vector database finds close matches. Filtered search is where engines differ.",
         "কয়েকটি সেটিং ঠিক করে ভেক্টর ডেটাবেস কাছের জিনিস কতটা ভালো খোঁজে। ফিল্টার-সহ সার্চেই ইঞ্জিনগুলো আলাদা।")],
       [sh("q", x=90), sh("filt", x=330), sh("idx", x=570)],
       [ln("q", "filt", "to"), ln("filt", "idx", "to")],
       [None, None, None, None],
       points=[("pgvector HNSW defaults: m 16 and ef_construction 64. The hnsw.ef_search default is 40.",
                "pgvector HNSW-এর ডিফল্ট: m ১৬ আর ef_construction ৬৪। hnsw.ef_search ডিফল্ট ৪০।"),
               ("Test real filters at your real selectivity.",
                "নিজের আসল ফিল্টার আর আসল সিলেকটিভিটিতে পরীক্ষা করুন।"),
               ("The when-to-choose table is the author's own inference, not vendor advice.",
                "কোনটি কখন, এই তালিকা লেখকের নিজের অনুমান, বিক্রেতার পরামর্শ নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
