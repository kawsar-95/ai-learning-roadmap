"""RAG and Knowledge Systems · How vector search works: flat, IVF, HNSW and distance metrics: how a vector database finds close vectors without checking every one.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 ANN       Body: "A vector database stores embeddings and answers 'which stored vectors are closest to this one?' without comparing against every row." Start here: "an approximate nearest neighbour (ANN) index, a fast shortcut that can miss the very best match."
  2 Flat      Body, \"ANN basics\": "Flat search is a linear scan: exact, low memory, sensible for small collections." Start here: "Checking every vector one by one. It is exact, but slow on big collections."
  3 IVF       Body: "IVF (inverted file index) partitions vectors into lists and searches only some of them."
  4 HNSW      Body: "HNSW ... builds multi-layer proximity graphs ... with search cost that scales logarithmically." Figure: "start at a sparse top layer, take long hops to get near the target, then refine on denser layers". Start here: "very slowly as the collection grows".
  5 Recall    Start here: "Recall: What share of the truly best matches the search manages to find." "a fast shortcut that can miss the very best match".
  6 Metrics   Body, \"Distance metrics\": figure: "L2 measures the straight-line gap, cosine measures only the angle, and the dot product mixes angle with vector length."
  7 Match     Body: "Match the metric to the one your embedding model was trained for; for unit-length vectors cosine and dot product rank identically." Start here: "(vectors scaled to length 1)".
  8 Remember  Start here points: flat, IVF and HNSW lines; match the distance metric; unit-length vectors.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Query", "কুয়েরি"), 90, 162),
    node("items", "database", ("Stored vectors", "জমা-রাখা ভেক্টর"), 630, 162),
    node("ls1", "storage", ("List", "লিস্ট"), 330, 75),
    node("ls2", "storage", ("List", "লিস্ট"), 330, 162),
    node("ls3", "storage", ("List", "লিস্ট"), 330, 250),
    node("top", "service", ("Sparse top layer", "ফাঁকা উপরের স্তর"), 340, 60),
    node("mid", "service", ("Denser layers", "ঘন স্তর"), 340, 162),
    node("low", "service", ("Bottom layer", "নিচের স্তর"), 340, 262),
    node("model", "model", ("Embedding model", "এমবেডিং মডেল"), 100, 162),
    node("l2", "tool", ("L2", "L2"), 400, 75),
    node("cos", "tool", ("Cosine", "কোসাইন"), 400, 162),
    node("dot", "tool", ("Dot product", "ডট প্রোডাক্ট"), 400, 250),
]

METRICS = [
    ("Checks", "দেখে"),
    ("Result", "ফল"),
    ("Cost", "খরচ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("ANN", "ANN"),
       ("Find the closest without checking all", "সব না দেখে সবচেয়ে কাছেরটা খোঁজা"),
       [("A vector database finds the stored items closest to your query without checking every one.",
         "ভেক্টর ডেটাবেস সব আইটেম না দেখেই কুয়েরির সবচেয়ে কাছের জমা-রাখা আইটেমগুলো খুঁজে দেয়।"),
        ("It uses an approximate nearest neighbour (ANN) index, a fast shortcut that can miss the very best match.",
         "এজন্য সে অ্যাপ্রক্সিমেট নিয়ারেস্ট নেইবার (ANN) ইনডেক্স ব্যবহার করে, যা দ্রুত শর্টকাট, তবে সেরা মিলটা মাঝে মাঝে ফসকে যেতে পারে।")],
       [sh("q", "hot"), sh("items", "hot", ("ANN index", "ANN ইনডেক্স"))],
       [ln("q", "items", "to", state="hot")],
       [("not every one", "সব নয়"), ("very close", "খুব কাছাকাছি"), None]),

    st(("Flat", "ফ্ল্যাট"),
       ("Flat search checks every vector", "ফ্ল্যাট সার্চ প্রতিটি ভেক্টর দেখে"),
       [("Flat search checks every vector one by one.",
         "ফ্ল্যাট সার্চ প্রতিটি ভেক্টর একে একে মেলায়।"),
        ("It is exact and low on memory, and it suits small collections. It is slow on big ones.",
         "এটা নির্ভুল ও কম মেমরির, আর ছোট কালেকশনের জন্য উপযুক্ত। বড় কালেকশনে ধীর।")],
       [sh("q", "hot"), sh("items", "hot", ("every vector", "প্রতিটি ভেক্টর"))],
       [ln("q", "items", "to", state="hot")],
       [("every vector", "প্রতিটি ভেক্টর"), ("exact", "নির্ভুল"), ("slow when big", "বড় হলে ধীর")]),

    st(("IVF", "IVF"),
       ("IVF searches only some lists", "IVF শুধু কয়েকটি লিস্টে খোঁজে"),
       [("IVF, the inverted file index, splits vectors into lists.",
         "IVF (inverted file index) ভেক্টরকে লিস্টে ভাগ করে।"),
        ("It searches only some of them.",
         "আর শুধু কয়েকটি লিস্টে খোঁজে।")],
       [sh("q", "hot"), sh("ls1", "dim", ("not searched", "খোঁজা হয় না")), sh("ls2", "hot", ("searched", "খোঁজা হয়")), sh("ls3", "hot", ("searched", "খোঁজা হয়")), sh("items", "dim")],
       [ln("q", "ls1", "to", state="dim"), ln("q", "ls2", "to", state="hot"), ln("q", "ls3", "to", state="hot")],
       [("some lists", "কয়েকটি লিস্ট"), None, None]),

    st(("HNSW", "HNSW"),
       ("HNSW walks a layered graph", "HNSW স্তরে স্তরে গ্রাফ বেয়ে যায়"),
       [("HNSW, the hierarchical navigable small world, is a layered graph of nearby vectors.",
         "HNSW (hierarchical navigable small world) কাছের ভেক্টরদের স্তরে স্তরে সাজানো গ্রাফ।"),
        ("Search starts with long hops on a sparse top layer, then refines on denser layers. Its cost grows logarithmically.",
         "ফাঁকা উপরের স্তরে লম্বা লাফে শুরু, তারপর ঘন স্তরে সূক্ষ্ম খোঁজ। এর খরচ লগারিদমিক হারে বাড়ে।")],
       [sh("q", "hot"), sh("top", "hot", ("long hops", "লম্বা লাফ")), sh("mid", "hot", ("refine", "সূক্ষ্ম খোঁজ")), sh("low", "hot", ("every vector", "প্রতিটি ভেক্টর"))],
       [ln("q", "top", "to", state="hot"), ln("top", "mid", "to", state="hot"), ln("mid", "low", "to", state="hot")],
       [("a layered graph", "স্তরে স্তরে গ্রাফ"), None, ("logarithmic", "লগারিদমিক")],
       note=("tip", "Logarithmic means the cost grows very slowly as the collection grows.",
             "লগারিদমিক মানে কালেকশন বড় হলেও খরচ খুব ধীরে বাড়ে।")),

    st(("Recall", "রিকল"),
       ("The shortcut can miss", "শর্টকাট ফসকাতে পারে"),
       [("Recall is what share of the truly best matches the search manages to find.",
         "রিকল হলো সত্যিকারের সেরা মিলগুলোর কত অংশ সার্চ খুঁজে পায়।"),
        ("An ANN index is approximate, so it can occasionally miss the very best match.",
         "ANN ইনডেক্স আনুমানিক, তাই সে মাঝে মাঝে সেরা মিলটা ফসকে ফেলতে পারে।")],
       [sh("q", "hot"), sh("items", "warn", ("can miss the best", "সেরাটা ফসকাতে পারে"))],
       [ln("q", "items", "to", state="warn")],
       [None, ("can miss the best", "সেরাটা ফসকাতে পারে"), None]),

    st(("Metrics", "মেট্রিক"),
       ("Three ways to measure close", "কাছে মাপার তিনটি উপায়"),
       [("A distance metric is the rule for measuring how close two vectors are, such as L2, cosine or dot product.",
         "ডিস্ট্যান্স মেট্রিক হলো দুটি ভেক্টর কতটা কাছে তা মাপার নিয়ম, যেমন L2, কোসাইন বা ডট প্রোডাক্ট।"),
        ("L2 measures the straight-line gap, cosine measures only the angle, and the dot product mixes angle with vector length.",
         "L2 সরলরেখার দূরত্ব মাপে, কোসাইন শুধু কোণ মাপে, আর ডট প্রোডাক্ট কোণ ও দৈর্ঘ্য দুটোই ধরে।")],
       [sh("l2", "hot", ("straight-line gap", "সরলরেখার দূরত্ব")), sh("cos", "hot", ("angle only", "শুধু কোণ")), sh("dot", "hot", ("angle and length", "কোণ আর দৈর্ঘ্য"))],
       [],
       [None, None, None]),

    st(("Match", "মেলানো"),
       ("Match the metric to your model", "মেট্রিক মডেলের সাথে মেলান"),
       [("Match the distance metric to the one your embedding model was trained for.",
         "এমবেডিং মডেল যে মেট্রিকের জন্য ট্রেন হয়েছে, সেই ডিস্ট্যান্স মেট্রিকই বাছুন।"),
        ("For unit-length vectors, vectors scaled to length 1, cosine and dot product rank results the same way.",
         "ইউনিট-লেংথ ভেক্টর (দৈর্ঘ্য ১ করে নেওয়া ভেক্টর) হলে কোসাইন আর ডট প্রোডাক্ট একই র‍্যাংকিং দেয়।")],
       [sh("model", "hot", ("trained for one", "একটির জন্য ট্রেন")), sh("l2", "dim"), sh("cos", "hot", ("same ranking", "একই র‍্যাংকিং")), sh("dot", "hot", ("same ranking", "একই র‍্যাংকিং"))],
       [ln("model", "cos", "to", state="hot"), ln("model", "dot", "to", state="hot")],
       [None, None, None],
       note=("warn", "If you measure closeness the wrong way, the nearest result may not be the one you wanted.",
             "কাছে মাপার ভুল উপায় নিলে সবচেয়ে কাছের ফলটা আপনার চাওয়া ফল নাও হতে পারে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A vector database finds the closest stored vectors without comparing against every row, using an approximate index.",
         "ভেক্টর ডেটাবেস প্রতিটি সারি না মিলিয়েই কাছের জমা-রাখা ভেক্টর খোঁজে, আনুমানিক ইনডেক্স দিয়ে।")],
       [sh("q"), sh("items")],
       [ln("q", "items", "to")],
       [None, None, None],
       points=[("Flat search is exact and low on memory, and it suits small collections.",
                "ফ্ল্যাট সার্চ নির্ভুল ও কম মেমরির, আর ছোট কালেকশনের জন্য উপযুক্ত।"),
               ("IVF searches only some lists; HNSW walks a layered graph whose cost grows logarithmically.",
                "IVF শুধু কয়েকটি লিস্টে খোঁজে; HNSW স্তরে স্তরে গ্রাফ বেয়ে যায়, আর তার খরচ লগারিদমিক হারে বাড়ে।"),
               ("Match the distance metric to the one your embedding model was trained for.",
                "এমবেডিং মডেল যে মেট্রিকের জন্য ট্রেন হয়েছে, সেই ডিস্ট্যান্স মেট্রিকই বাছুন।"),
               ("For unit-length vectors, cosine and dot product rank results the same way.",
                "ইউনিট-লেংথ ভেক্টর হলে কোসাইন আর ডট প্রোডাক্ট একই র‍্যাংকিং দেয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
