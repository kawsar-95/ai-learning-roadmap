"""Part 16 · 09 RAG and Agents: retrieval-augmented generation.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Context     Body, "Why context construction matters": "A model's instructions tell it how to behave; its context gives it the facts it needs for a specific query. Without relevant context, even a well-instructed model will guess or hallucinate. Two dominant patterns build this context automatically. RAG (retrieval-augmented generation) pulls in relevant documents. The agentic pattern lets a model call tools to fetch information or take action."
  2 Two parts   Body, "RAG architecture": "A RAG system has two parts. A retriever finds relevant chunks of data in an external memory (documents, tables, chat history). A generator writes a response using what was retrieved. Long documents are split into smaller chunks so that only the most relevant pieces are fed into the model, keeping the prompt short and focused."
  3 Keywords    Body, "Retrieval algorithms", and its table: "Term-based retrieval (lexical search) matches keywords; algorithms such as TF-IDF ... and BM25 score documents by how often and how distinctively a term appears." Table, term-based column: "Fast to index and query", "Strong out of the box, exact keyword matches", "Cheap", "Misses semantic similarity".
  4 Meaning     Same part: "Embedding-based retrieval (semantic search) compares the meaning of the query and the documents using vector embeddings. The embeddings are stored and searched in a vector database ..." Table, embedding column: "Slower; needs embedding generation and vector search", "Captures meaning, handles paraphrased queries", "Can be expensive at scale", "Can blur exact codes/names into fuzzy meaning".
  5 Hybrid      Same part: "Because each approach has blind spots, production systems often combine them. Running a cheap retriever first and reranking with a more precise one is called hybrid search. Reciprocal rank fusion can merge rankings from multiple retrievers into one list."
  6 Optimize    Body, "Retrieval optimization": the four bullets (chunking strategy, reranking, query rewriting, contextual retrieval), and the remember point "Better chunking, reranking, query rewriting, and contextual retrieval all improve what the model receives."
  7 Beyond text Body, "RAG beyond text": "RAG is not limited to plain text. Multimodal RAG retrieves images, audio, or video alongside text using a shared multimodal embedding model such as CLIP."
  8 Tables      Same part: "RAG with tabular data works differently. Instead of embedding rows, the system translates the question into a SQL query (text-to-SQL), runs it against the database, and feeds the result back to the generator."
  9 Remember    The idea and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("query", "user", ("Query", "প্রশ্ন"), 110, 162),
    node("tools", "tool", ("Tools", "টুল"), 380, 250),
    node("retriever", "service", ("Retriever", "রিট্রিভার"), 380, 162),
    node("keyword", "file", ("Keyword search", "কিওয়ার্ড সার্চ"), 380, 162),
    node("vectors", "database", ("Vector database", "ভেক্টর ডেটাবেজ"), 380, 162),
    node("embedder", "model", ("Embedding model", "এমবেডিং মডেল"), 380, 162),
    node("sql", "tool", ("Text-to-SQL", "text-to-SQL"), 380, 162),
    node("rerank", "service", ("Rerank", "রির‍্যাঙ্ক"), 650, 162),
    node("memory", "storage", ("External memory", "বাইরের মেমরি"), 650, 250),
    node("generator", "model", ("Generator", "জেনারেটর"), 650, 162),
]

METRICS = [
    ("Speed", "গতি"),
    ("Cost", "খরচ"),
    ("Finds", "খোঁজে"),
]

CAPTION = (
    "RAG finds relevant information first and gives it to the model, so it does not have to guess.",
    "RAG আগে প্রাসঙ্গিক তথ্য খুঁজে মডেলকে দেয়, যাতে তাকে আন্দাজ করতে না হয়।",
)

STEPS = [
    st(("Context", "কনটেক্সট"),
       ("Give the model the facts", "মডেলকে তথ্য দিন"),
       [("A model's instructions tell it how to behave; its context gives it the facts it needs for a specific query. Without relevant context, even a well-instructed model will guess or hallucinate.",
         "মডেলের ইনস্ট্রাকশন বলে কীভাবে চলতে হবে; তার কনটেক্সট দেয় একটি নির্দিষ্ট প্রশ্নের জন্য দরকারি তথ্য। প্রাসঙ্গিক কনটেক্সট ছাড়া ভালো ইনস্ট্রাকশন পাওয়া মডেলও আন্দাজ করবে, নয়তো ভুল তথ্য বানাবে।"),
        ("Two dominant patterns build this context automatically. RAG (retrieval-augmented generation) pulls in relevant documents. The agentic pattern lets a model call tools to fetch information or take action.",
         "দুটি প্রধান পদ্ধতি এই কনটেক্সট নিজে থেকে বানায়। RAG (retrieval-augmented generation) প্রাসঙ্গিক ডকুমেন্ট এনে দেয়। এজেন্ট পদ্ধতিতে মডেল টুল ডেকে তথ্য আনে বা কাজ করে।")],
       [sh("query", "hot"), sh("retriever", "hot", ("RAG pulls in documents", "RAG ডকুমেন্ট আনে"), y=75),
        sh("tools", "hot", ("fetch or take action", "তথ্য আনে বা কাজ করে")), sh("generator", "hot", ("needs the facts", "তথ্য দরকার"))],
       [ln("query", "retriever", "to", state="hot"), ln("query", "tools", "to", state="hot"),
        ln("retriever", "generator", "to", state="hot"), ln("tools", "generator", "to", state="hot")],
       [None, None, None]),

    st(("Two parts", "দুই অংশ"),
       ("A retriever and a generator", "রিট্রিভার আর জেনারেটর"),
       [("A RAG system has two parts. A retriever finds relevant chunks of data in an external memory (documents, tables, chat history). A generator writes a response using what was retrieved.",
         "একটি RAG সিস্টেমে দুটি অংশ থাকে। রিট্রিভার বাইরের মেমরি (ডকুমেন্ট, টেবিল, চ্যাট হিস্টরি) থেকে প্রাসঙ্গিক চাংক খোঁজে। জেনারেটর যা পাওয়া গেছে তা দিয়ে উত্তর লেখে।"),
        ("Long documents are split into smaller chunks so that only the most relevant pieces are fed into the model, keeping the prompt short and focused.",
         "লম্বা ডকুমেন্ট ছোট চাংকে ভাগ করা হয়, যাতে শুধু সবচেয়ে প্রাসঙ্গিক টুকরোগুলো মডেলে যায় এবং প্রম্পট ছোট ও কেন্দ্রীভূত থাকে।")],
       [sh("query"), sh("retriever", "hot", ("finds chunks", "চাংক খোঁজে")), sh("memory", "hot"),
        sh("generator", "hot", ("writes the response", "উত্তর লেখে"))],
       [ln("query", "retriever", "to"), ln("memory", "retriever", "to", state="hot", label=("chunks", "চাংক")), ln("retriever", "generator", "to", state="hot")],
       [None, None, None]),

    st(("Keywords", "কিওয়ার্ড"),
       ("Term-based retrieval", "টার্ম-ভিত্তিক রিট্রিভাল"),
       [("Retrievers rank documents by relevance using one of two broad mechanisms. Term-based retrieval (lexical search) matches keywords; algorithms such as TF-IDF and BM25 score documents by how often and how distinctively a term appears.",
         "রিট্রিভার দুটি বড় পদ্ধতির একটি দিয়ে ডকুমেন্টকে প্রাসঙ্গিকতা অনুযায়ী সাজায়। টার্ম-ভিত্তিক রিট্রিভাল (লেক্সিক্যাল সার্চ) কিওয়ার্ড মেলায়; TF-IDF আর BM25-এর মতো অ্যালগরিদম দেখে একটি টার্ম কত বার আর কতটা স্বতন্ত্রভাবে আসে, সেই অনুযায়ী ডকুমেন্টকে স্কোর দেয়।"),
        ("It is fast to index and query, cheap, and strong out of the box, with exact keyword matches.",
         "এটি ইনডেক্স আর কোয়েরি করতে দ্রুত, সস্তা, আর হুবহু কিওয়ার্ড মেলানোয় শুরু থেকেই ভালো।")],
       [sh("query", "hot"), sh("keyword", "hot", ("TF-IDF, BM25", "TF-IDF, BM25")), sh("memory", "hot", ("documents", "ডকুমেন্ট"), y=162)],
       [ln("query", "keyword", "to", state="hot"), ln("keyword", "memory", "to", state="hot")],
       [("Fast", "দ্রুত"), ("Cheap", "সস্তা"), ("Exact words", "হুবহু শব্দ")],
       note=("warn",
             "Its weakness: it misses semantic similarity.",
             "দুর্বলতা: অর্থের মিল ধরতে পারে না।")),

    st(("Meaning", "অর্থ"),
       ("Embedding-based retrieval", "এমবেডিং-ভিত্তিক রিট্রিভাল"),
       [("Embedding-based retrieval (semantic search) compares the meaning of the query and the documents using vector embeddings. The embeddings are stored and searched in a vector database, with approximate nearest-neighbor algorithms such as HNSW, IVF, or product quantization.",
         "এমবেডিং-ভিত্তিক রিট্রিভাল (সেম্যান্টিক সার্চ) ভেক্টর এমবেডিং দিয়ে প্রশ্ন আর ডকুমেন্টের অর্থ তুলনা করে। এমবেডিংগুলো ভেক্টর ডেটাবেজে জমা থাকে আর সেখানে খোঁজা হয়, HNSW, IVF বা প্রোডাক্ট কোয়ান্টাইজেশনের মতো approximate nearest-neighbor অ্যালগরিদম দিয়ে।"),
        ("It captures meaning and handles paraphrased queries. It is slower, since it needs embedding generation and vector search, and it can be expensive at scale.",
         "এটি অর্থ ধরে এবং অন্য শব্দে ঘুরিয়ে বলা প্রশ্নও সামলায়। এটি ধীর, কারণ এতে এমবেডিং বানাতে হয় আর ভেক্টর সার্চ করতে হয়, আর বড় স্কেলে খরচ বাড়তে পারে।")],
       [sh("query", "hot"), sh("vectors", "hot", ("compares meaning", "অর্থ তুলনা করে")), sh("memory", "hot", ("documents", "ডকুমেন্ট"), y=162)],
       [ln("query", "vectors", "to", state="hot"), ln("vectors", "memory", "to", state="hot")],
       [("Slower", "ধীর"), ("Costly at scale", "বড় স্কেলে ব্যয়বহুল"), ("Meaning", "অর্থ")],
       note=("warn",
             "It can blur exact codes and names into fuzzy meaning.",
             "এটি হুবহু কোড আর নামকে ঝাপসা অর্থে মিশিয়ে ফেলতে পারে।")),

    st(("Hybrid", "হাইব্রিড"),
       ("Combine them", "দুটোকে মেলান"),
       [("Because each approach has blind spots, production systems often combine them.",
         "প্রতিটি পদ্ধতির অন্ধ জায়গা আছে, তাই প্রোডাকশন সিস্টেমে প্রায়ই দুটোকে মেলানো হয়।"),
        ("Running a cheap retriever first and reranking with a more precise one is called hybrid search. Reciprocal rank fusion can merge rankings from multiple retrievers into one list.",
         "আগে একটি সস্তা রিট্রিভার চালিয়ে তারপর আরও নির্ভুল একটি দিয়ে আবার সাজানোকে বলে হাইব্রিড সার্চ। Reciprocal rank fusion অনেক রিট্রিভারের র‍্যাংকিং মিলিয়ে একটি তালিকা বানাতে পারে।")],
       [sh("query"), sh("keyword", "hot", ("cheap, first", "সস্তা, আগে"), y=75), sh("vectors", "hot", ("another retriever", "আরেকটি রিট্রিভার"), y=250),
        sh("rerank", "hot", ("one merged list", "একটি মেলানো তালিকা"))],
       [ln("query", "keyword", "to"), ln("query", "vectors", "to"),
        ln("keyword", "rerank", "to", state="hot", label=("ranking", "র‍্যাংকিং")), ln("vectors", "rerank", "to", state="hot", label=("ranking", "র‍্যাংকিং"))],
       [None, None, None]),

    st(("Optimize", "উন্নতি"),
       ("Improve what the model receives", "মডেল যা পায় তা ভালো করুন"),
       [("Better chunking, reranking, query rewriting, and contextual retrieval all improve what the model receives.",
         "ভালো চাংকিং, রির‍্যাঙ্কিং, কোয়েরি রিরাইটিং আর কনটেক্সচুয়াল রিট্রিভাল মডেলের পাওয়া তথ্য আরও ভালো করে।")],
       [sh("query", "hot", ("rewritten first", "আগে নতুন করে লেখা")), sh("retriever", "hot"),
        sh("memory", "hot", ("split into chunks", "চাংকে ভাগ"), y=250), sh("rerank", "hot", ("candidates reranked", "আবার সাজানো"))],
       [ln("query", "retriever", "to", state="hot"), ln("memory", "retriever", "to", state="hot"), ln("retriever", "rerank", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Chunking strategy: split documents by fixed size, by sentence or paragraph boundaries, or recursively; overlap chunk boundaries so key sentences are not cut in half.",
                 "চাংকিং কৌশল: ডকুমেন্ট ভাগ করুন নির্দিষ্ট আকারে, বাক্য বা অনুচ্ছেদের সীমানায়, বা রিকার্সিভভাবে; চাংকের সীমানা ওভারল্যাপ করুন, যাতে গুরুত্বপূর্ণ বাক্য মাঝখানে কেটে না যায়।"),
                ("+", "Reranking: after an initial cheap retrieval, rerank candidates for accuracy, recency, or better placement in the context window.",
                 "রির‍্যাঙ্কিং: প্রাথমিক সস্তা রিট্রিভালের পরে ক্যান্ডিডেটদের আবার সাজান নির্ভুলতা, সাম্প্রতিকতা বা কনটেক্সট উইন্ডোতে ভালো অবস্থানের জন্য।"),
                ("+", "Query rewriting: rewrite an ambiguous follow-up question (for example, “How about Emily Doe?”) into a self-contained query before retrieval.",
                 "কোয়েরি রিরাইটিং: অস্পষ্ট ফলো-আপ প্রশ্নকে (যেমন “How about Emily Doe?”) রিট্রিভালের আগে নিজে পূর্ণ একটি কোয়েরিতে বদলান।"),
                ("+", "Contextual retrieval: attach metadata, keywords, or an AI-generated summary to each chunk so it stays findable even out of its original context.",
                 "কনটেক্সচুয়াল রিট্রিভাল: প্রতিটি চাংকে মেটাডেটা, কিওয়ার্ড বা AI-তৈরি সারাংশ জুড়ুন, যাতে আসল কনটেক্সটের বাইরেও সেটি খুঁজে পাওয়া যায়।")]),

    st(("Beyond text", "টেক্সটের বাইরে"),
       ("Images, audio and video too", "ছবি, অডিও আর ভিডিওও"),
       [("RAG is not limited to plain text. Multimodal RAG retrieves images, audio, or video alongside text using a shared multimodal embedding model such as CLIP.",
         "RAG শুধু সাধারণ টেক্সটে সীমাবদ্ধ নয়। মাল্টিমোডাল RAG টেক্সটের সাথে ছবি, অডিও বা ভিডিও খুঁজে আনে, CLIP-এর মতো একটি যৌথ মাল্টিমোডাল এমবেডিং মডেল ব্যবহার করে।")],
       [sh("query", "hot"), sh("embedder", "hot", ("such as CLIP", "যেমন CLIP")), sh("vectors", "hot", ("images, audio, video", "ছবি, অডিও, ভিডিও"), x=650)],
       [ln("query", "embedder", "to", state="hot"), ln("embedder", "vectors", "to", state="hot")],
       [None, None, None]),

    st(("Tables", "টেবিল"),
       ("Text-to-SQL for tables", "টেবিলের জন্য text-to-SQL"),
       [("RAG with tabular data works differently. Instead of embedding rows, the system translates the question into a SQL query (text-to-SQL), runs it against the database, and feeds the result back to the generator.",
         "টেবিল ডেটার জন্য RAG আলাদাভাবে কাজ করে। সারি এমবেড না করে সিস্টেম প্রশ্নকে একটি SQL কোয়েরিতে বদলায় (text-to-SQL), সেটি ডেটাবেজে চালায়, আর ফলাফল জেনারেটরকে ফেরত দেয়।")],
       [sh("query", "hot"), sh("sql", "hot", ("question to SQL query", "প্রশ্ন থেকে SQL")), sh("memory", "hot", ("the database", "ডেটাবেজ"), y=75),
        sh("generator", "hot", ("gets the result", "ফলাফল পায়"), y=250)],
       [ln("query", "sql", "to", state="hot"), ln("sql", "memory", "to", state="hot"), ln("memory", "generator", "to", state="hot", label=("result", "ফলাফল"))],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A model needs the right facts to answer a specific question well. RAG finds relevant information first and gives it to the model, so it does not have to guess.",
         "একটি প্রশ্নের ভালো উত্তর দিতে মডেলের সঠিক তথ্য দরকার। RAG আগে প্রাসঙ্গিক তথ্য খুঁজে মডেলকে দেয়, যাতে তাকে আন্দাজ করতে না হয়।")],
       [sh("query"), sh("retriever"), sh("memory", y=250), sh("generator")],
       [ln("query", "retriever", "to"), ln("memory", "retriever", "to"), ln("retriever", "generator", "to")],
       [None, None, None],
       points=[("Instructions tell a model how to behave; context gives it the facts for one question.",
                "ইনস্ট্রাকশন মডেলকে বলে কীভাবে চলবে; কনটেক্সট দেয় একটি প্রশ্নের তথ্য।"),
               ("Keyword search is fast and exact. Embedding search finds meaning but costs more.",
                "কিওয়ার্ড সার্চ দ্রুত, আর হুবহু শব্দ মেলায়। এমবেডিং সার্চ অর্থ ধরে, কিন্তু খরচ বেশি।"),
               ("Combining both kinds of retrieval often works better in real systems.",
                "দুই ধরনের রিট্রিভাল মেলালে বাস্তব সিস্টেমে প্রায়ই ভালো কাজ হয়।"),
               ("Better chunking, reranking, query rewriting, and contextual retrieval all improve what the model receives.",
                "ভালো চাংকিং, রির‍্যাঙ্কিং, কোয়েরি রিরাইটিং আর কনটেক্সচুয়াল রিট্রিভাল মডেলের পাওয়া তথ্য আরও ভালো করে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
