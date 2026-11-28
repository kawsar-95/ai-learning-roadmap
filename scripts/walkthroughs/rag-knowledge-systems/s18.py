"""RAG and Knowledge Systems · Late chunking, contextual retrieval, and choosing a chunking strategy: two ways to keep a chunk tied to its document, and how to choose.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Lost      Start here: "A chunk cut from a document can lose its meaning, like a chunk that says only the company."
  2 Naive     Body: "Conventional pipelines chunk first and embed each chunk alone, so a chunk saying 'the company' cannot know which company."
  3 Late      Body: "Late chunking embeds the whole document first, then splits just before mean pooling. It needs no extra training." Start here: "Mean pooling: Averaging the number lists of many tokens into one list for a chunk."
  4 Limit     Body: "it requires an embedding model whose context window can hold the document." Start here: "Long-context embedding model", "context window (how much text it can read at once)".
  5 Context   Body: "Contextual retrieval: Anthropic's method: an LLM writes a short note on where a chunk sits in its document, and the note goes in front of the chunk." "about 50 to 100 tokens of context to each chunk, for both embedding and BM25."
  6 Reported  Start here: "Anthropic reports failed retrievals falling from 5.7% to 1.9% with reranking. This is the vendor's own test." Start here: "Reranking: Re-scoring the top results with a more careful model."
  7 Choose    Body, \"Choosing a strategy\": the editorial table (each row: strength, watch out for). "The strategy table is editorial, not a benchmark: each method trades a strength for a cost." Layman: \"you have to test on your own\".
  8 Remember  Start here points: late chunking and contextual retrieval facts; the vendor-test and editorial-table cautions.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("doc", "file", ("Document", "ডকুমেন্ট"), 70, 162),
    node("chunk", "file", ("Chunk", "চাঙ্ক"), 235, 162),
    node("model", "model", ("Embedding model", "এমবেডিং মডেল"), 440, 162),
    node("pool", "tool", ("Mean pooling", "মিন পুলিং"), 440, 162),
    node("vec", "storage", ("Chunk vectors", "চাঙ্ক ভেক্টর"), 655, 162),
    node("llm", "model", ("LLM", "LLM"), 110, 75),
    node("ctx", "file", ("Chunk with note", "নোট-সহ চাঙ্ক"), 300, 162),
    node("emb", "storage", ("Embeddings", "এমবেডিং"), 500, 75),
    node("bm25", "storage", ("BM25", "BM25"), 500, 250),
    node("rerank", "tool", ("Reranking", "রিরেংকিং"), 660, 162),
    node("own", "note", ("Your own test", "আপনার নিজের পরীক্ষা"), 450, 162),
]

METRICS = [
    ("Extra training", "আলাদা ট্রেনিং"),
    ("Context added", "যোগ হয়"),
    ("Failed retrievals", "ব্যর্থ রিট্রিভাল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own words, and the figures are the vendor's own test.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর সংখ্যা সেকশনের নিজের কথা, আর সংখ্যাগুলো বিক্রেতার নিজের পরীক্ষার।",
)

STEPS = [
    st(("Lost", "হারানো"),
       ("A chunk can lose its meaning", "চাঙ্ক অর্থ হারাতে পারে"),
       [("A chunk cut from a document can lose its meaning, like a chunk that says only the company.",
         "কোনো ডকুমেন্ট থেকে কেটে নেওয়া চাঙ্ক অর্থ হারাতে পারে, যেমন যে চাঙ্কে শুধু কোম্পানিটি লেখা।"),
        ("Late chunking and contextual retrieval fix this by keeping each chunk tied to its document.",
         "লেট চাঙ্কিং আর কনটেক্সচুয়াল রিট্রিভাল প্রতিটি চাঙ্ককে তার ডকুমেন্টের সাথে জুড়ে রেখে এটা ঠিক করে।")],
       [sh("doc", "hot"), sh("chunk", "warn", ("only the company", "শুধু কোম্পানিটি"))],
       [ln("doc", "chunk", "to", state="warn")],
       [None, None, None]),

    st(("Naive", "নেইভ"),
       ("Naive: chunk, then embed", "নেইভ: আগে কাটা, তারপর এমবেড"),
       [("Conventional pipelines chunk first and embed each chunk alone.",
         "নেইভ পদ্ধতিতে আগে কাটা হয়, তারপর প্রতিটি চাঙ্ক আলাদাভাবে এনকোড হয়।"),
        ("So a chunk saying \"the company\" cannot know which company.",
         "তাই যে চাঙ্কে শুধু \"কোম্পানি\" লেখা, সে জানে না কোন কোম্পানি।")],
       [sh("doc", "hot"), sh("chunk", "hot", ("alone", "আলাদাভাবে")), sh("model", "hot"), sh("vec", "warn")],
       [ln("doc", "chunk", "to", state="hot"), ln("chunk", "model", "to", state="hot"), ln("model", "vec", "to", state="warn")],
       [None, None, None]),

    st(("Late", "লেট"),
       ("Late chunking: embed, then split", "লেট চাঙ্কিং: আগে এমবেড, তারপর কাটা"),
       [("Late chunking embeds the whole document first, then splits just before mean pooling.",
         "লেট চাঙ্কিং আগে পুরো ডকুমেন্ট এমবেড করে, তারপর মিন পুলিংয়ের ঠিক আগে কাটে।"),
        ("Mean pooling averages the number lists of many tokens into one list for a chunk. Late chunking needs no extra training.",
         "মিন পুলিং অনেক টোকেনের সংখ্যার তালিকার গড় নিয়ে একটি চাঙ্কের জন্য একটি তালিকা বানায়। আলাদা ট্রেনিং লাগে না।")],
       [sh("doc", "hot"), sh("model", "hot", ("whole document", "পুরো ডকুমেন্ট"), x=250), sh("pool", "hot", ("split just before", "ঠিক আগে কাটা")), sh("vec", "hot")],
       [ln("doc", "model", "to", state="hot"), ln("model", "pool", "to", state="hot"), ln("pool", "vec", "to", state="hot")],
       [("Not needed", "লাগে না"), None, None]),

    st(("Limit", "সীমা"),
       ("It needs a long-context model", "লং-কনটেক্সট মডেল লাগে"),
       [("Late chunking requires an embedding model whose context window can hold the document.",
         "লেট চাঙ্কিংয়ের জন্য এমন এমবেডিং মডেল লাগে, যার কনটেক্সট উইন্ডো ডকুমেন্ট ধরে রাখতে পারে।"),
        ("The context window is how much text the model can read at once.",
         "কনটেক্সট উইন্ডো মানে একবারে কতটা লেখা পড়তে পারে।")],
       [sh("doc", "hot"), sh("model", "warn", ("long-context", "লং-কনটেক্সট"), x=250)],
       [ln("doc", "model", "to", state="warn")],
       [None, None, None]),

    st(("Context", "কনটেক্সট"),
       ("Contextual retrieval: add a note", "কনটেক্সচুয়াল রিট্রিভাল: নোট জোড়া"),
       [("Contextual retrieval is Anthropic's method: an LLM writes a short note on where a chunk sits in its document.",
         "কনটেক্সচুয়াল রিট্রিভাল Anthropic-এর পদ্ধতি: LLM চাঙ্কটি ডকুমেন্টের কোথায় আছে তার একটি ছোট নোট লেখে।"),
        ("The note goes in front of the chunk, and the result is used for both embedding and BM25.",
         "নোটটি চাঙ্কের সামনে বসে, আর ফলটি এমবেডিং আর BM25 দুটোর জন্যই ব্যবহার হয়।")],
       [sh("llm", "hot", ("writes the note", "নোট লেখে")), sh("chunk", "hot", x=110, y=250), sh("ctx", "hot"), sh("emb", "hot"), sh("bm25", "hot")],
       [ln("llm", "ctx", "to", state="hot"), ln("chunk", "ctx", "to", state="hot"), ln("ctx", "emb", "to", state="hot"), ln("ctx", "bm25", "to", state="hot")],
       [None, ("about 50 to 100 tokens", "প্রায় ৫০ থেকে ১০০ টোকেন"), None]),

    st(("Reported", "রিপোর্ট"),
       ("What Anthropic reports", "Anthropic যা জানিয়েছে"),
       [("Reranking re-scores the top results with a more careful model, so the best ones come first.",
         "রিরেংকিং সেরা ফলগুলোকে আরও যত্নশীল মডেল দিয়ে আবার স্কোর করে, যাতে সেরাগুলো আগে আসে।"),
        ("Anthropic reports failed retrievals falling from 5.7% to 1.9% with reranking. This is the vendor's own test.",
         "Anthropic জানিয়েছে রিরেংকিং-সহ ব্যর্থ রিট্রিভাল ৫.৭% থেকে ১.৯%-এ নেমেছে। এটা বিক্রেতার নিজের পরীক্ষা।")],
       [sh("emb", "hot"), sh("bm25", "hot"), sh("rerank", "hot", ("5.7% to 1.9%", "৫.৭% থেকে ১.৯%"))],
       [ln("emb", "rerank", "to", state="hot"), ln("bm25", "rerank", "to", state="hot")],
       [None, None, ("5.7% to 1.9%", "৫.৭% থেকে ১.৯%")],
       note=("warn", "The figures are the vendor's own test, not a benchmark.",
             "এই সংখ্যাগুলো বিক্রেতার নিজের পরীক্ষার, বেঞ্চমার্ক নয়।")),

    st(("Choose", "বাছাই"),
       ("Choosing a strategy", "কৌশল বাছাই"),
       [("The strategy table is editorial, not a benchmark: each method trades a strength for a cost.",
         "কৌশলের তুলনার টেবিলটি লেখকের নিজের মত, বেঞ্চমার্ক নয়: প্রতিটি পদ্ধতিতে একটা সুবিধার বদলে একটা খরচ আছে।"),
        ("No single cutting rule is best for every kind of document, so you have to test on your own.",
         "সব ধরনের ডকুমেন্টের জন্য একটাই কাটার নিয়ম সেরা নয়, তাই নিজে পরীক্ষা করে দেখতে হবে।")],
       [sh("doc", "hot"), sh("own", "hot")],
       [ln("doc", "own", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Fixed + overlap: trivial, predictable, cheap. Watch out: can slice through sentences and facts",
                 "ফিক্সড + ওভারল্যাপ: সহজ, অনুমানযোগ্য, সস্তা। সতর্কতা: বাক্য আর তথ্যের মাঝখানে কেটে ফেলতে পারে"),
                ("+", "Recursive: keeps coherent units whenever they fit. Watch out: size is in characters by default",
                 "রিকার্সিভ: যেখানে সম্ভব সংগত অংশ একসাথে রাখে। সতর্কতা: আকার ডিফল্টভাবে অক্ষরে মাপা হয়"),
                ("+", "Structural: header metadata for filtering and citations. Watch out: needs clean, consistent markup",
                 "স্ট্রাকচারাল: ফিল্টার আর সাইটেশনের জন্য হেডার মেটাডেটা। সতর্কতা: পরিষ্কার, সামঞ্জস্যপূর্ণ মার্কআপ লাগে"),
                ("+", "Semantic: topic-coherent chunks. Watch out: extra embedding pass, and a threshold to tune",
                 "সিমান্টিক: বিষয়ে সংগত চাঙ্ক। সতর্কতা: বাড়তি এমবেডিং পাস, আর ঠিক করার মতো থ্রেশহোল্ড"),
                ("+", "Late chunking: chunk vectors carry document context. Watch out: needs a long-context embedding model",
                 "লেট চাঙ্কিং: চাঙ্ক ভেক্টর ডকুমেন্টের কনটেক্সট বহন করে। সতর্কতা: লং-কনটেক্সট এমবেডিং মডেল লাগে"),
                ("+", "Contextual retrieval: repairs lost context for dense and BM25. Watch out: one-time LLM cost per chunk",
                 "কনটেক্সচুয়াল রিট্রিভাল: ডেন্স আর BM25 দুটোর হারানো কনটেক্সট ঠিক করে। সতর্কতা: প্রতি চাঙ্কে একবারের LLM খরচ")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Two newer fixes keep a chunk tied to its document: late chunking, which splits after the transformer, and contextual retrieval, which prepends an explanation to every chunk.",
         "দুটি নতুন সমাধান চাঙ্ককে তার ডকুমেন্টের সাথে জুড়ে রাখে: লেট চাঙ্কিং, যা ট্রান্সফর্মারের পরে কাটে, আর কনটেক্সচুয়াল রিট্রিভাল, যা প্রতিটি চাঙ্কের সামনে একটি ব্যাখ্যা জোড়ে।")],
       [sh("doc", "hot"), sh("chunk", "hot"), sh("model", "hot"), sh("vec", "hot")],
       [ln("doc", "chunk", "to"), ln("chunk", "model", "to"), ln("model", "vec", "to")],
       [None, None, None],
       points=[("Late chunking embeds the whole document first, then splits just before mean pooling. It needs no extra training.",
                "লেট চাঙ্কিং আগে পুরো ডকুমেন্ট এমবেড করে, তারপর মিন পুলিংয়ের ঠিক আগে কাটে। আলাদা ট্রেনিং লাগে না।"),
               ("Contextual retrieval adds about 50 to 100 tokens of context to each chunk, for both embedding and BM25.",
                "কনটেক্সচুয়াল রিট্রিভাল প্রতিটি চাঙ্কে প্রায় ৫০ থেকে ১০০ টোকেনের কনটেক্সট জোড়ে, এমবেডিং আর BM25 দুটোর জন্যই।"),
               ("Anthropic's figures are the vendor's own test, and the strategy table is editorial, not a benchmark.",
                "Anthropic-এর সংখ্যা বিক্রেতার নিজের পরীক্ষার, আর কৌশলের টেবিল লেখকের নিজের মত, বেঞ্চমার্ক নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
