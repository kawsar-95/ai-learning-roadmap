"""RAG and Knowledge Systems · 01 Chunking strategies: fixed-size, recursive, structural and semantic: how you cut the text decides what search can find.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Chunks    Intro: "Search works on small pieces of documents called chunks, not on whole documents. How you cut the text decides what the search can find, so cutting well matters." Term "Chunk".
  2 Overlap   "Fixed-size and recursive splitting": "Neighbouring windows share chunk_overlap units, so a fact that straddles a boundary still lands whole in at least one chunk." Term "Overlap".
  3 Recursive "The recursive variant tries separators in order (paragraph, line, word, character) so coherent units stay together for as long as possible." Term "Recursive splitting": "only when needed".
  4 Structure "Structural and sentence-aware splitting": "MarkdownHeaderTextSplitter groups text by header level and attaches the headers as metadata. ... Chain it with a recursive splitter so overlap applies inside a section and never crosses a header boundary." SentenceSplitter "breaks at sentence boundaries".
  5 Semantic  "Semantic chunking embeds sentences and cuts where adjacent-sentence similarity drops." Terms "Embedding", "Semantic chunking".
  6 Units     Warning: "LangChain measures characters, not tokens, so a '1000' chunk is not 1000 tokens. ... None of the sources I checked states a recommended chunk size or overlap percentage, so tune them against your own retrieval evals."
  7 Bad cut   Practice: the chunk cut mid-sentence lost "14" and "Basic plan"; the chunk cut at the end of a sentence keeps the whole fact. "A cutter that stops at sentence ends keeps the fact whole."
  8 Remember  Intro: "A chunk that is too coarse buries the answer in noise; one that is too fine strips away the context that made the sentence meaningful." Callouts on overlap, units and tuning.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("doc", "file", ("Document", "ডকুমেন্ট"), 90, 162),
    node("c1", "note", ("Chunk 1", "চাঙ্ক ১"), 330, 70),
    node("c2", "note", ("Chunk 2", "চাঙ্ক ২"), 330, 162),
    node("c3", "note", ("Chunk 3", "চাঙ্ক ৩"), 330, 254),
    node("par", "tool", ("Paragraph", "প্যারাগ্রাফ"), 100, 162),
    node("line", "tool", ("Line", "লাইন"), 280, 162),
    node("word", "tool", ("Word", "শব্দ"), 460, 162),
    node("chr", "tool", ("Character", "ক্যারেক্টার"), 650, 162),
    node("hdr", "tool", ("Header splitter", "হেডার স্প্লিটার"), 120, 162),
    node("rec", "tool", ("Recursive splitter", "রিকার্সিভ স্প্লিটার"), 390, 162),
    node("sem", "chart", ("Sentence similarity", "বাক্যের সিমিলারিটি"), 330, 162),
    node("bot", "service", ("Support bot", "সাপোর্ট বট"), 640, 162),
]

METRICS = [
    ("Cut", "কাটা"),
    ("Fact", "তথ্য"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Chunks", "চাঙ্ক"),
       ("Search works on chunks", "সার্চ চাঙ্কে কাজ করে"),
       [("Search works on small pieces of documents called chunks, not on whole documents.",
         "সার্চ পুরো ডকুমেন্টে নয়, ডকুমেন্টের ছোট টুকরায় কাজ করে, যাকে বলে চাঙ্ক।"),
        ("How you cut the text decides what the search can find, so cutting well matters.",
         "লেখা কীভাবে কাটছেন, তার ওপরই ঠিক হয় সার্চ কী খুঁজে পাবে। তাই ভালোভাবে কাটা জরুরি।")],
       [sh("doc", "hot"), sh("c1", "hot"), sh("c2", "hot"), sh("c3", "hot")],
       [ln("doc", "c1", "to", state="hot"), ln("doc", "c2", "to", state="hot"), ln("doc", "c3", "to", state="hot")],
       [None, None]),

    st(("Overlap", "ওভারল্যাপ"),
       ("Fixed-size windows with overlap", "ওভারল্যাপসহ ফিক্সড-সাইজ উইন্ডো"),
       [("Fixed-size splitting cuts a window of chunk_size units. Neighbouring windows share chunk_overlap units.",
         "ফিক্সড-সাইজ স্প্লিটিং chunk_size মাপের উইন্ডোতে কাটে। পাশাপাশি উইন্ডো chunk_overlap মাপের অংশ শেয়ার করে।"),
        ("So a fact on the cut line stays whole in at least one chunk.",
         "তাই কাটার রেখায় পড়া তথ্য অন্তত একটি চাঙ্কে পুরো থাকে।")],
       [sh("doc", "hot"), sh("c1", "hot", ("chunk_size", "chunk_size")), sh("c2", "hot", ("shared text", "শেয়ার করা লেখা")), sh("c3", "hot")],
       [ln("doc", "c1", "to", state="hot"), ln("c1", "c2", "to", state="hot"), ln("c2", "c3", "to", state="hot")],
       [None, None]),

    st(("Recursive", "রিকার্সিভ"),
       ("Recursive splitting: biggest break first", "রিকার্সিভ স্প্লিটিং: আগে বড় বিরতি"),
       [("Recursive splitting cuts at the biggest natural break first: paragraph, then line, then word, then character.",
         "রিকার্সিভ স্প্লিটিং আগে সবচেয়ে বড় স্বাভাবিক বিরতিতে কাটে: প্যারাগ্রাফ, তারপর লাইন, তারপর শব্দ, তারপর ক্যারেক্টার।"),
        ("It goes to a finer separator only when needed, so coherent units stay together for as long as possible.",
         "দরকার হলে তবেই সে সূক্ষ্ম বিভাজকে যায়, তাই অর্থপূর্ণ অংশ যতক্ষণ সম্ভব একসাথে থাকে।")],
       [sh("par", "hot", ("first", "আগে")), sh("line", "hot"), sh("word", "hot"), sh("chr", "hot", ("last", "শেষে"))],
       [ln("par", "line", "to", state="hot"), ln("line", "word", "to", state="hot"), ln("word", "chr", "to", state="hot")],
       [None, None]),

    st(("Structure", "স্ট্রাকচার"),
       ("Cut along headers and sentences", "হেডার আর বাক্য ধরে কাটুন"),
       [("A header splitter groups text by header level and attaches the headers as metadata, extra labels on each chunk. A sentence splitter breaks at sentence boundaries.",
         "হেডার স্প্লিটার হেডারের স্তর ধরে লেখা সাজায় আর হেডারগুলো মেটাডেটা হিসেবে জুড়ে দেয়, মানে চাঙ্কের বাড়তি লেবেল। সেন্টেন্স স্প্লিটার বাক্যের সীমানায় কাটে।"),
        ("Chain the header splitter with a recursive one, so overlap never crosses a header boundary.",
         "হেডার স্প্লিটারের সাথে রিকার্সিভ স্প্লিটার জুড়ুন, যাতে ওভারল্যাপ হেডারের সীমানা না পেরোয়।")],
       [sh("doc", "hot"), sh("hdr", "hot", ("headers as metadata", "হেডার মেটাডেটা হিসেবে"), x=270, y=162), sh("rec", "hot", ("overlap inside a section", "ওভারল্যাপ সেকশনের ভেতরে"), x=520, y=162)],
       [ln("doc", "hdr", "to", state="hot"), ln("hdr", "rec", "to", state="hot")],
       [None, None]),

    st(("Semantic", "সেম্যান্টিক"),
       ("Semantic chunking: cut where meaning shifts", "সেম্যান্টিক চাঙ্কিং: অর্থ যেখানে বদলায়"),
       [("Semantic chunking embeds sentences, and cuts where adjacent-sentence similarity drops.",
         "সেম্যান্টিক চাঙ্কিং বাক্যগুলো এমবেড করে, আর পাশাপাশি বাক্যের সিমিলারিটি যেখানে কমে সেখানে কাটে।"),
        ("An embedding is a list of numbers that stands for the meaning of a text.",
         "এমবেডিং হলো একটি লেখার অর্থ বোঝানো সংখ্যার তালিকা।")],
       [sh("doc", "hot", x=90, y=162), sh("sem", "hot", ("breakpoint where it drops", "যেখানে কমে সেখানে ব্রেকপয়েন্ট"), x=330, y=162), sh("c1", "hot", x=580, y=70), sh("c2", "hot", x=580, y=254)],
       [ln("doc", "sem", "to", state="hot"), ln("sem", "c1", "to", state="hot"), ln("sem", "c2", "to", state="hot")],
       [None, None]),

    st(("Units", "মাপ"),
       ("Units, and no best size", "মাপ, আর সেরা সাইজ নেই"),
       [("LangChain measures size in characters, not tokens, so a chunk of 1000 is not 1000 tokens.",
         "LangChain-এর মাপ ক্যারেক্টারে, টোকেনে নয়; তাই ১০০০ মাপের চাঙ্ক মানে ১০০০ টোকেন নয়।"),
        ("None of the sources checked gives a best chunk size, so tune it on your own retrieval tests.",
         "যাচাই করা কোনো সূত্রে সেরা চাঙ্ক সাইজ বলা নেই, তাই নিজের রিট্রিভাল টেস্টে ঠিক করুন।")],
       [sh("c1", "warn", ("characters, not tokens", "ক্যারেক্টার, টোকেন নয়")), sh("c2", "hot", ("tune on your tests", "নিজের টেস্টে ঠিক করুন"))],
       [ln("c1", "c2", "to", state="warn")],
       [None, None],
       note=("warn", "The values in the section's code are illustrative. Tune the size and overlap against your own retrieval evals.",
             "সেকশনের কোডের মানগুলো উদাহরণমাত্র। চাঙ্কের সাইজ আর ওভারল্যাপ নিজের রিট্রিভাল টেস্টে ঠিক করুন।")),

    st(("Bad cut", "ভুল কাটা"),
       ("A bad cut breaks an answer", "ভুল জায়গায় কাটলে উত্তর নষ্ট হয়"),
       [("A fixed-size cutter cuts after a set number of characters, even in the middle of a fact. Here the cut removed 14, so the AI could not answer.",
         "ফিক্সড-সাইজ কাটার নির্দিষ্ট সংখ্যক অক্ষর পরপর কাটে, তথ্যের মাঝখানে হলেও। এখানে কাটায় ১৪ হারিয়ে গেছে, তাই AI উত্তর দিতে পারেনি।"),
        ("A cutter that stops at sentence ends keeps the fact whole.",
         "যে কাটার বাক্যের শেষে থামে, সে তথ্যটা পুরো রাখে।")],
       [sh("c1", "warn", ("cut mid-sentence", "বাক্যের মাঝখানে কাটা")), sh("c2", "hot", ("cut at sentence end", "বাক্যের শেষে কাটা")), sh("bot", "hot", ("14 days", "১৪ দিন"), x=640, y=162)],
       [ln("c1", "bot", "to", state="warn"), ln("c2", "bot", "to", state="hot")],
       [("mid-sentence", "বাক্যের মাঝখানে"), ("14 days", "১৪ দিন")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A chunk that is too coarse buries the answer in noise; one that is too fine strips away the context that made the sentence meaningful.",
         "চাঙ্ক বেশি বড় হলে উত্তর বাড়তি লেখার ভিড়ে হারিয়ে যায়। বেশি ছোট হলে বাক্যটির অর্থ যে কনটেক্সট দিয়েছিল, তা চলে যায়।")],
       [sh("doc"), sh("c1", "hot"), sh("c2", "hot"), sh("c3", "hot")],
       [ln("doc", "c1", "to"), ln("doc", "c2", "to"), ln("doc", "c3", "to")],
       [None, None],
       points=[("Overlap keeps a fact that sits on a cut line whole in at least one chunk.",
                "ওভারল্যাপ থাকলে কাটার রেখায় পড়া তথ্য অন্তত একটি চাঙ্কে পুরো থাকে।"),
               ("Chain a header splitter with a recursive one, so overlap never crosses a header boundary.",
                "হেডার স্প্লিটারের সাথে রিকার্সিভ স্প্লিটার জুড়ুন, যাতে ওভারল্যাপ হেডারের সীমানা না পেরোয়।"),
               ("None of the sources checked gives a best chunk size, so tune it on your own retrieval tests.",
                "যাচাই করা কোনো সূত্রে সেরা চাঙ্ক সাইজ বলা নেই, তাই নিজের রিট্রিভাল টেস্টে ঠিক করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
