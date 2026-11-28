"""Filtering a vector search: pre-filter, post-filter and what each engine does: a filter can leave too few results or break the graph, and engines repair this in different ways.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Mixed      Body: "Real questions mix meaning with hard rules, like a year or a rating." "Vector similarity alone cannot enforce a hard rule like a year after 2000, so you filter on metadata."
  2 Metadata   Start here: "Metadata: Labels stored with each piece of text, such as year or customer type. A filter uses them to keep only the right pieces."
  3 Post       Start here: "Post-filtering: Searching first, then throwing away results that do not match." Diagram: "search first, filter after".
  4 Too few    Start here: "A strict filter can leave fewer results than you asked for, or none." "Post-filtering can return fewer results than you asked for (k), or none, and then the LLM answers from nothing. Check the number of results, not only the scores."
  5 Pre        Start here: "Pre-filtering: Keeping only matching points before the search runs. Qdrant says it then compares the query with every matching point: exact, but costly at scale." Diagram: "k results, but costly at scale".
  6 Broken     Body: "a strict filter can leave so few eligible points that the paths between them break." Diagram: "every neighbour of a match is filtered out, so the search cannot hop between matches".
  7 Repair     Start here: "Filterable HNSW: Qdrant's fix: it adds extra links between the points that are left after filtering." "ACORN: A method that repairs the graph's connections at query time ... Weaviate uses it by default from v1.34+."
  8 Remember   The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Question", "প্রশ্ন"), 75, 162),
    node("db", "database", ("Vector search", "ভেক্টর সার্চ"), 235, 162),
    node("rule", "key", ("Metadata filter", "মেটাডেটা ফিল্টার"), 430, 162),
    node("res", "chart", ("Results", "ফল"), 620, 162),
    node("llm", "model", ("LLM", "LLM"), 620, 260),
    node("chunk", "file", ("Text with labels", "লেবেলসহ লেখা"), 235, 260),
    node("m1", "database", ("Match", "মিল"), 150, 110),
    node("m2", "database", ("Match", "মিল"), 610, 110),
    node("f1", "shield", ("Filtered out", "বাদ পড়া"), 380, 250),
]

METRICS = [
    ("Asked", "চাওয়া হয়েছে"),
    ("Returned", "ফেরত এসেছে"),
    ("Graph links", "গ্রাফের লিংক"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Mixed", "মেশানো"),
       ("Meaning plus a hard rule", "অর্থের সাথে কঠিন শর্ত"),
       [("Real questions mix meaning with hard rules, like a year or a rating.",
         "বাস্তব প্রশ্নে অর্থের সাথে কঠিন শর্তও থাকে, যেমন সাল বা রেটিং।"),
        ("Vector similarity alone cannot enforce a rule like a year after 2000.",
         "শুধু ভেক্টর সিমিলারিটি দিয়ে ২০০০ সালের পরের মতো শর্ত মানানো যায় না।")],
       [sh("q", "hot"), sh("db", "hot", ("meaning only", "শুধু অর্থ")),
        sh("rule", "warn", ("year after 2000", "২০০০ সালের পরের"), x=235, y=60)],
       [ln("q", "db", "to", state="hot"), ln("rule", "db", "to", state="warn")],
       [None, None, None]),

    st(("Metadata", "মেটাডেটা"),
       ("Labels on each piece of text", "প্রতিটি লেখার টুকরোয় লেবেল"),
       [("Each piece of text carries labels, called metadata, such as year or customer type.",
         "প্রতিটি লেখার টুকরোর সাথে লেবেল থাকে, যাকে মেটাডেটা বলে, যেমন সাল বা গ্রাহকের ধরন।"),
        ("A metadata filter uses them to keep only the right pieces.",
         "মেটাডেটা ফিল্টার সেগুলো দিয়ে শুধু সঠিক টুকরো রাখে।")],
       [sh("chunk", "hot", ("labels", "লেবেল")), sh("db", "hot"),
        sh("rule", "hot", x=235, y=60)],
       [ln("chunk", "db", "to", state="hot"), ln("rule", "db", "to", state="hot")],
       [None, None, None]),

    st(("Post-filter", "পোস্ট-ফিল্টার"),
       ("Post-filter: search, then filter", "পোস্ট-ফিল্টার: আগে সার্চ, পরে ফিল্টার"),
       [("Post-filtering searches first, then throws away results that do not match.",
         "পোস্ট-ফিল্টার আগে সার্চ করে, পরে না-মেলা ফল বাদ দেয়।"),
        ("A strict filter can leave fewer results than you asked for.",
         "কড়া ফিল্টারে চাওয়ার চেয়ে কম ফল থাকতে পারে।")],
       [sh("q", "hot"), sh("db", "hot", ("search first", "আগে সার্চ")), sh("rule", "hot", ("filter after", "পরে ফিল্টার")),
        sh("res", "warn", ("fewer than k", "k-এর চেয়ে কম"))],
       [ln("q", "db", "to", state="hot"), ln("db", "rule", "to", state="hot"), ln("rule", "res", "to", state="warn")],
       [("k", "k"), ("fewer than k", "k-এর চেয়ে কম"), None]),

    st(("Too few", "খুব কম"),
       ("Too few results, or none", "খুব কম ফল, এমনকি শূন্য"),
       [("Post-filtering can return fewer results than you asked for (k), or none. Then the LLM answers from nothing.",
         "পোস্ট-ফিল্টারে যতগুলো ফল চেয়েছেন (k) তার চেয়ে কম আসতে পারে, এমনকি শূন্য। তখন LLM ফাঁকা থেকে উত্তর বানায়।"),
        ("Check the number of results, not only the scores.",
         "শুধু স্কোর নয়, কয়টি ফল এল তাও দেখুন।")],
       [sh("db", "dim"), sh("res", "warn", ("fewer, or none", "কম, বা শূন্য")),
        sh("llm", "warn", ("from nothing", "ফাঁকা থেকে"))],
       [ln("db", "res", "to", state="dim"), ln("res", "llm", "to", state="warn")],
       [("k", "k"), ("fewer, or none", "কম, বা শূন্য"), None],
       note=("warn", "A downstream LLM that gets no results then answers from nothing.",
             "পরের ধাপের LLM কোনো ফল না পেলে ফাঁকা থেকে উত্তর বানায়।")),

    st(("Pre-filter", "প্রি-ফিল্টার"),
       ("Pre-filter: filter, then search", "প্রি-ফিল্টার: আগে ফিল্টার, পরে সার্চ"),
       [("Pre-filtering keeps only matching points before the search runs.",
         "প্রি-ফিল্টার সার্চের আগেই শুধু মিলে যাওয়া পয়েন্ট রাখে।"),
        ("Qdrant says it then compares the query with every matching point: exact, but costly at scale.",
         "Qdrant বলছে, এতে কুয়েরি প্রতিটি মিলে যাওয়া পয়েন্টের সাথে তুলনা করা হয়: ফল নির্ভুল, কিন্তু বড় স্কেলে খরচ বেশি।")],
       [sh("q", "hot"), sh("rule", "hot", ("filter first", "আগে ফিল্টার"), x=235, y=60),
        sh("db", "hot", ("every match", "প্রতিটি মিল")), sh("res", "hot", ("k results", "k-টি ফল"))],
       [ln("q", "db", "to", state="hot"), ln("rule", "db", "to", state="hot"), ln("db", "res", "to", state="hot")],
       [("k", "k"), ("k results", "k-টি ফল"), None],
       note=("tip", "Exact, but costly at scale.", "নির্ভুল, কিন্তু বড় স্কেলে খরচ বেশি।")),

    st(("Broken", "ভাঙা"),
       ("A strict filter breaks the graph", "কড়া ফিল্টার গ্রাফ ভাঙে"),
       [("A strict filter can leave so few points that the paths between them break.",
         "কড়া ফিল্টারে এত কম পয়েন্ট থাকতে পারে যে তাদের মধ্যকার পথ ভেঙে যায়।"),
        ("Every neighbour of a match is filtered out, so the search cannot hop between matches.",
         "মিলে যাওয়া পয়েন্টের প্রতিটি প্রতিবেশী বাদ পড়ে, তাই সার্চ এক মিল থেকে আরেক মিলে যেতে পারে না।")],
       [sh("m1", "hot"), sh("f1", "dim"), sh("m2", "hot")],
       [ln("m1", "f1", "to", state="warn"), ln("f1", "m2", "to", state="warn")],
       [None, None, ("broken", "ভাঙা")]),

    st(("Repair", "মেরামত"),
       ("Engines repair the links", "ইঞ্জিন লিংক মেরামত করে"),
       [("Qdrant's filterable HNSW adds extra links between the points that are left after filtering.",
         "Qdrant-এর ফিল্টারেবল HNSW ফিল্টারের পরে যে পয়েন্টগুলো থাকে, তাদের মধ্যে বাড়তি লিংক বসায়।"),
        ("ACORN repairs the graph's connections at query time. Weaviate uses it by default from v1.34+.",
         "ACORN কুয়েরির সময় গ্রাফের সংযোগ মেরামত করে। Weaviate v1.34+ থেকে এটি ডিফল্ট রেখেছে।")],
       [sh("m1", "hot"), sh("f1", "dim"), sh("m2", "hot")],
       [ln("m1", "f1", "to", state="dim"), ln("f1", "m2", "to", state="dim"),
        ln("m1", "m2", "to", state="hot", label=("extra link", "বাড়তি লিংক"))],
       [None, None, ("restored", "ফিরে এসেছে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Filter on metadata, and check how many results came back.",
         "মেটাডেটা দিয়ে ফিল্টার করুন, আর কয়টি ফল এল তা দেখুন।")],
       [sh("q"), sh("db"), sh("rule"), sh("res"), sh("llm")],
       [ln("q", "db", "to"), ln("db", "rule", "to"), ln("rule", "res", "to"), ln("res", "llm", "to")],
       [None, None, None],
       points=[("Vector similarity alone cannot enforce a hard rule like a year after 2000, so you filter on metadata.",
                "শুধু ভেক্টর সিমিলারিটি দিয়ে ২০০০ সালের পরের মতো কঠিন শর্ত মানানো যায় না, তাই মেটাডেটা দিয়ে ফিল্টার করতে হয়।"),
               ("Post-filtering can return fewer results than you asked for (k), or none, and then the LLM answers from nothing.",
                "পোস্ট-ফিল্টারে যতগুলো ফল চেয়েছেন (k) তার চেয়ে কম আসতে পারে, এমনকি শূন্য, আর তখন LLM ফাঁকা থেকে উত্তর বানায়।"),
               ("Check the number of results, not only the scores.",
                "শুধু স্কোর নয়, কয়টি ফল এল তাও দেখুন।"),
               ("Index the fields you filter on. Without an index, filtering forces scans or fallbacks.",
                "যে ফিল্ডে ফিল্টার দেবেন তার ইনডেক্স রাখুন। ইনডেক্স না থাকলে স্ক্যান বা ফলব্যাকে নামতে হয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
