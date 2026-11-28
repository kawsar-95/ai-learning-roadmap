"""RAG and Knowledge Systems · 06 GraphRAG & knowledge-graph augmentation: a graph and community summaries built at index time, for questions no single chunk answers.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Gap       Body: "Vector search returns chunks that look like the query. It struggles with 'global' questions such as 'what are the main themes in this dataset?', which no single chunk answers."
  2 Graph     Body: "An LLM builds an entity knowledge graph". Pipeline: "segments documents into TextUnits, extracts entities, relationships and claims". "Knowledge graph: A map of entities, such as people or companies, and how they relate to each other."
  3 Community "runs Leiden hierarchical clustering, and summarizes each community." "Community: A group of related entities in the graph. GraphRAG writes a summary for each group before any question arrives."
  4 Global    "Global search: reasoning over community summaries"; "At query time, GraphRAG merges partial answers from those summaries."
  5 Local     "Local search: expanding from matched entities to their neighbours"; "Multi-hop question: A question that needs several linked facts about connected entities to answer."
  6 Lighter   "Lighter variants (LightRAG, HippoRAG) and graph-database tooling (Neo4j) target the same gap with different cost profiles."
  7 Cost      "The main cost is LLM extraction and summarization at index time. Microsoft warns it can be expensive." "Start on a small slice of the corpus, and compare against a plain hybrid baseline."
  8 Remember  Start here: "Graph papers report their gains on whole-corpus and multi-hop questions. For simple lookups, a plain vector or hybrid pipeline is the natural default." "Missed or merged entities hurt everything after, and summaries go stale when documents change unless you re-index."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Question", "প্রশ্ন"), 115, 60),
    node("vec", "cache", ("Vector search", "ভেক্টর সার্চ"), 380, 60),
    node("docs", "file", ("Documents", "ডকুমেন্ট"), 100, 190),
    node("llm", "model", ("LLM", "LLM"), 350, 190),
    node("graph", "database", ("Entity graph", "এন্টিটি গ্রাফ"), 625, 190),
    node("comm", "note", ("Communities", "কমিউনিটি"), 625, 320),
    node("ans", "note", ("Merged answer", "মেলানো উত্তর"), 380, 60),
    node("nbr", "note", ("Neighbours", "প্রতিবেশী"), 625, 60),
    node("light", "tool", ("LightRAG", "LightRAG"), 625, 60),
    node("hippo", "tool", ("HippoRAG", "HippoRAG"), 625, 190),
    node("neo", "tool", ("Neo4j", "Neo4j"), 625, 320),
]

METRICS = [
    ("Built when", "কখন বানানো"),
    ("Main cost", "মূল খরচ"),
    ("Simple lookups", "সাধারণ খোঁজ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Gap", "ফাঁক"),
       ("Big questions have no single chunk", "বড় প্রশ্নের উত্তর কোনো একটি টুকরোয় নেই"),
       [("Vector search returns chunks that look like the query.",
         "ভেক্টর সার্চ প্রশ্নের মতো দেখতে লেখার টুকরো আনে।"),
        ("It struggles with global questions such as the main themes in a dataset, which no single chunk answers.",
         "ডেটাসেটের প্রধান থিমের মতো গ্লোবাল প্রশ্নে সে হোঁচট খায়, কারণ উত্তর কোনো একটি টুকরোয় থাকে না।")],
       [sh("q", "hot", ("main themes?", "প্রধান থিম?")), sh("vec", "warn", ("no single chunk answers", "কোনো একটি টুকরো উত্তর দেয় না"))],
       [ln("q", "vec", "to", state="warn")],
       [None, None, None]),

    st(("Graph", "গ্রাফ"),
       ("An LLM builds a graph of entities", "LLM এন্টিটির গ্রাফ বানায়"),
       [("An LLM builds an entity knowledge graph: a map of entities, such as people or companies, and how they relate.",
         "LLM একটি এন্টিটি নলেজ গ্রাফ বানায়: এন্টিটির, যেমন মানুষ বা কোম্পানির, মানচিত্র, আর তাদের মধ্যে সম্পর্ক।"),
        ("The documented pipeline segments documents into TextUnits, then extracts entities, relationships and claims.",
         "ডকুমেন্টেড পাইপলাইনে ডকুমেন্ট TextUnit-এ ভাগ হয়, তারপর এন্টিটি, সম্পর্ক ও দাবি বের করা হয়।")],
       [sh("docs", "hot"), sh("llm", "hot", ("entities, relationships, claims", "এন্টিটি, সম্পর্ক, দাবি")), sh("graph", "hot")],
       [ln("docs", "llm", "to", state="hot"), ln("llm", "graph", "to", state="hot")],
       [("index time", "ইনডেক্সের সময়"), None, None]),

    st(("Community", "কমিউনিটি"),
       ("Group the graph, summarize each group", "গ্রাফ ভাগ করুন, প্রতিটির সারসংক্ষেপ লিখুন"),
       [("Leiden hierarchical clustering groups closely connected points in the graph, layer by layer.",
         "Leiden হায়ারার্কিক্যাল ক্লাস্টারিং গ্রাফে ঘনিষ্ঠভাবে যুক্ত পয়েন্টদের স্তরে স্তরে দলে ভাগ করে।"),
        ("Each group is a community, and GraphRAG writes a summary for each one before any question arrives.",
         "প্রতিটি দল একটি কমিউনিটি, আর প্রশ্ন আসার আগেই GraphRAG প্রতিটির সারসংক্ষেপ লিখে রাখে।")],
       [sh("graph", "hot"), sh("comm", "hot", ("summary written first", "সারসংক্ষেপ আগে লেখা"))],
       [ln("graph", "comm", "to", state="hot")],
       [None, None, None]),

    st(("Global", "গ্লোবাল"),
       ("Global search: answer from summaries", "গ্লোবাল সার্চ: সারসংক্ষেপ থেকে উত্তর"),
       [("Global search reasons over the community summaries.",
         "গ্লোবাল সার্চ কমিউনিটি সারসংক্ষেপ থেকে ভাবে।"),
        ("At query time, GraphRAG merges partial answers from those summaries.",
         "প্রশ্নের সময় GraphRAG সেই সারসংক্ষেপগুলোর আংশিক উত্তর মিলিয়ে দেয়।")],
       [sh("q", "hot", ("main themes?", "প্রধান থিম?"), x=115, y=190), sh("comm", "hot", ("partial answers", "আংশিক উত্তর")), sh("ans", "hot")],
       [ln("q", "comm", "to", state="hot"), ln("comm", "ans", "to", state="hot")],
       [None, None, None],
       note=("tip", "This is the answer that no single chunk holds.",
             "এই উত্তর কোনো একটি টুকরোয় থাকে না।")),

    st(("Local", "লোকাল"),
       ("Local search: start from matched entities", "লোকাল সার্চ: মিলে যাওয়া এন্টিটি থেকে শুরু"),
       [("Local search starts from matched entities and expands to their neighbours.",
         "লোকাল সার্চ মিলে যাওয়া এন্টিটি থেকে শুরু করে প্রতিবেশীতে ছড়ায়।"),
        ("That suits a multi-hop question, which needs several linked facts about connected entities.",
         "মাল্টি-হপ প্রশ্নে এটা কাজে লাগে, যেখানে সংযুক্ত এন্টিটির কয়েকটি জোড়া তথ্য লাগে।")],
       [sh("q", "hot", x=115, y=190), sh("graph", "hot", ("matched entities", "মিলে যাওয়া এন্টিটি")), sh("nbr", "hot")],
       [ln("q", "graph", "to", state="hot"), ln("graph", "nbr", "to", state="hot")],
       [None, None, None]),

    st(("Lighter", "হালকা"),
       ("Lighter variants and Neo4j", "হালকা রূপ আর Neo4j"),
       [("Lighter variants (LightRAG, HippoRAG) and graph-database tooling (Neo4j) target the same gap.",
         "হালকা রূপ (LightRAG, HippoRAG) আর গ্রাফ-ডেটাবেস টুলিং (Neo4j) একই ফাঁক পূরণ করতে চায়।"),
        ("They have different cost profiles.",
         "তাদের খরচের ধরন আলাদা।")],
       [sh("graph", "dim", x=130, y=190), sh("light", "hot"), sh("hippo", "hot", ("Personalized PageRank", "Personalized PageRank")), sh("neo", "hot")],
       [ln("graph", "light", "to", state="dim"), ln("graph", "hippo", "to", state="dim"), ln("graph", "neo", "to", state="dim")],
       [None, ("different cost profiles", "আলাদা খরচের ধরন"), None]),

    st(("Cost", "খরচ"),
       ("The cost is paid at index time", "খরচ দিতে হয় ইনডেক্সের সময়"),
       [("The main cost is LLM extraction and summarization at index time. Microsoft warns it can be expensive.",
         "মূল খরচ ইনডেক্সের সময়ের LLM এক্সট্র্যাকশন ও সামারাইজেশন। Microsoft নিজেই বলেছে তা ব্যয়বহুল হতে পারে।"),
        ("Start on a small slice of the corpus, and compare against a plain hybrid baseline.",
         "কর্পাসের ছোট অংশ দিয়ে শুরু করুন, আর সাধারণ হাইব্রিড বেসলাইনের সাথে তুলনা করুন।")],
       [sh("docs", "warn", ("small slice first", "ছোট অংশ আগে")), sh("llm", "warn", ("expensive", "ব্যয়বহুল")), sh("comm", "warn")],
       [ln("docs", "llm", "to", state="warn"), ln("llm", "comm", "to", state="warn")],
       [None, ("LLM extraction and summaries", "LLM এক্সট্র্যাকশন ও সারসংক্ষেপ"), None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Graph papers report their gains on whole-corpus and multi-hop questions.",
         "গ্রাফ নিয়ে পেপারগুলো পুরো কর্পাস আর মাল্টি-হপ প্রশ্নে তাদের উন্নতির কথা জানায়।"),
        ("For simple lookups, a plain vector or hybrid pipeline is the natural default.",
         "সাধারণ তথ্য খোঁজায় ভেক্টর বা হাইব্রিড পাইপলাইনই স্বাভাবিক ডিফল্ট।")],
       [sh("vec", "hot", ("simple lookups", "সাধারণ খোঁজ")), sh("graph", "warn", ("missed or merged entities", "এন্টিটি মিস বা গুলিয়ে যাওয়া")), sh("comm", "warn", ("stale unless re-indexed", "রি-ইনডেক্স না করলে পুরোনো"))],
       [ln("graph", "comm", "to", state="warn")],
       [None, None, ("plain vector or hybrid", "ভেক্টর বা হাইব্রিড")],
       note=("warn", "Missed or merged entities hurt everything after, and summaries go stale when documents change unless you re-index.",
             "এন্টিটি মিস বা গুলিয়ে গেলে পরের সব কাজ নষ্ট হয়, আর ডকুমেন্ট বদলালে রি-ইনডেক্স না করলে সারসংক্ষেপ পুরোনো হয়ে যায়।")),
]

WALK = walk(760, 400, NODES, METRICS, CAPTION, STEPS)
