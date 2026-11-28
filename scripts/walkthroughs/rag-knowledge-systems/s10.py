"""Multimodal RAG: images, tables, charts: three designs that keep a chart or a scanned table searchable, and why a summary can lose a number.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Blind     Body: "Text-only search cannot answer when the answer sits in a chart, a scanned table, or a slide. Multimodal RAG keeps those things searchable".
  2 Three     Body: "turn them into text, embed images directly, or search page images."
  3 Embed     Term "CLIP": "puts images and text into one shared vector space. It learned from 400M image-text pairs." Diagram option 1: "Multimodal embedder, one vector space", "Multimodal LLM answers from raw images".
  4 Summary   Diagram option 2: "LLM summary describes the content in text", "Embed the summary", "Text LLM answers from summaries".
  5 Keep raw  Term "Multi-vector retriever": the item searched (a summary) is separate from the one the model answers from (the raw image or table). "Of the two summary designs, prefer the one keeping the raw object."
  6 Pages     Terms "ColPali" and "Late interaction": many vectors straight from a page image, no text extraction; each query token's best match, then add them up.
  7 Lost      Warning: "Summaries can hide detail. If a summary leaves out a number, no query can find it."
  8 Remember  The last two points of the Start here box: ColPali stores many vectors per page, so measure index size; test on your own documents.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("src", "file", ("Chart or table", "চার্ট বা টেবিল"), 90, 160),
    node("txt", "note", ("Text-only search", "শুধু টেক্সট-সার্চ"), 470, 60),
    node("clip", "model", ("Embedder", "এমবেডার"), 270, 60),
    node("summ", "model", ("LLM summary", "LLM সারসংক্ষেপ"), 270, 160),
    node("pages", "model", ("ColPali", "ColPali"), 270, 260),
    node("idx", "database", ("Index", "ইনডেক্স"), 450, 160),
    node("raw", "storage", ("Raw object", "কাঁচা জিনিস"), 450, 260),
    node("llm", "model", ("Answering model", "উত্তর-দেওয়া মডেল"), 650, 160),
]

METRICS = [
    ("Searched", "যেটায় খোঁজা হয়"),
    ("Answers from", "উত্তর আসে"),
    ("Learned from", "যা থেকে শেখা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Blind", "অন্ধ"),
       ("Text-only search goes blind", "শুধু টেক্সট-সার্চ অন্ধ হয়ে যায়"),
       [("Text-only search cannot answer when the answer sits in a chart, a scanned table, or a slide.",
         "উত্তর যখন চার্ট, স্ক্যান করা টেবিল বা স্লাইডে থাকে, তখন শুধু টেক্সট-সার্চ কাজ করে না।"),
        ("Multimodal RAG keeps those things searchable.",
         "মাল্টিমোডাল RAG সেগুলোকেও সার্চযোগ্য রাখে।")],
       [sh("src", "warn"), sh("txt", "warn")],
       [ln("src", "txt", "to", state="warn")],
       [None, None, None]),

    st(("Three", "তিনটি"),
       ("Three ways to keep them searchable", "সার্চযোগ্য রাখার তিনটি উপায়"),
       [("Turn them into text, embed images directly, or search page images.",
         "সেগুলোকে টেক্সটে বদলানো, ছবি সরাসরি এমবেড করা, বা পাতার ছবি খোঁজা।")],
       [sh("src", "hot"), sh("clip", "hot"), sh("summ", "hot"), sh("pages", "hot")],
       [ln("src", "clip", "to", state="hot"), ln("src", "summ", "to", state="hot"), ln("src", "pages", "to", state="hot")],
       [None, None, None]),

    st(("Embed", "এমবেড"),
       ("Embed images directly", "ছবি সরাসরি এমবেড"),
       [("A multimodal embedder such as CLIP puts images and text into one shared vector space.",
         "CLIP-এর মতো মাল্টিমোডাল এমবেডার ছবি আর টেক্সটকে একই ভেক্টর স্পেসে আনে।"),
        ("CLIP learned from 400M image-text pairs. A multimodal LLM answers from the raw images.",
         "CLIP ৪০ কোটি ছবি-টেক্সট জোড়া থেকে শিখেছে। মাল্টিমোডাল LLM কাঁচা ছবি থেকে উত্তর দেয়।")],
       [sh("src", "hot"), sh("clip", "hot"), sh("idx", "hot"), sh("llm", "hot")],
       [ln("src", "clip", "to", state="hot"), ln("clip", "idx", "to", state="hot"), ln("idx", "llm", "to", state="hot")],
       [("images and text", "ছবি আর টেক্সট"), ("raw images", "কাঁচা ছবি"), ("400M image-text pairs", "৪০ কোটি ছবি-টেক্সট জোড়া")]),

    st(("Summary", "সারসংক্ষেপ"),
       ("Summarize to text", "টেক্সটে সারসংক্ষেপ"),
       [("An LLM summary describes the image or table in text, and you embed the summary with ordinary text embeddings.",
         "LLM সারসংক্ষেপ ছবি বা টেবিলের কথা টেক্সটে বলে, আর সেই সারসংক্ষেপ সাধারণ টেক্সট এমবেডিং দিয়ে এমবেড করা হয়।"),
        ("A text LLM answers from the summaries.",
         "টেক্সট LLM সারসংক্ষেপ থেকে উত্তর দেয়।")],
       [sh("src", "hot"), sh("summ", "hot"), sh("idx", "hot"), sh("llm", "hot")],
       [ln("src", "summ", "to", state="hot"), ln("summ", "idx", "to", state="hot"), ln("idx", "llm", "to", state="hot")],
       [("summary", "সারসংক্ষেপ"), ("summaries", "সারসংক্ষেপ"), None]),

    st(("Keep raw", "মূল রাখুন"),
       ("Search the summary, keep the raw object", "সারসংক্ষেপে খুঁজুন, মূল জিনিস রাখুন"),
       [("A multi-vector retriever separates the item that gets searched, a summary, from the one the model answers from, the raw image or table.",
         "মাল্টি-ভেক্টর রিট্রিভার যেটার মধ্যে খোঁজা হয়, মানে সারসংক্ষেপ, আর যা থেকে মডেল উত্তর দেয়, মানে কাঁচা ছবি বা টেবিল, এ দুটোকে আলাদা রাখে।"),
        ("Of the two summary designs, prefer the one keeping the raw object, so the answering model sees the original.",
         "সারসংক্ষেপের দুটি নকশার মধ্যে যেটি মূল জিনিস রাখে সেটি বাছুন, তাহলে উত্তর-দেওয়া মডেল মূলটি দেখতে পায়।")],
       [sh("summ", "hot"), sh("idx", "hot"), sh("raw", "hot"), sh("llm", "hot")],
       [ln("summ", "idx", "to", state="hot"), ln("idx", "raw", "to", state="hot"), ln("raw", "llm", "to", state="hot")],
       [("summary", "সারসংক্ষেপ"), ("raw object", "কাঁচা জিনিস"), None]),

    st(("Pages", "পাতা"),
       ("Search page images", "পাতার ছবি খুঁজুন"),
       [("ColPali makes many vectors straight from a page image, so it skips text extraction.",
         "ColPali পাতার ছবি থেকেই সরাসরি অনেক ভেক্টর বানায়, তাই টেক্সট এক্সট্র্যাকশন লাগে না।"),
        ("Late interaction compares each query token with one vector for each small patch of the page, keeps each token's best match, then adds them up.",
         "লেট ইন্টারঅ্যাকশন প্রশ্নের প্রতিটি টোকেনকে পাতার প্রতিটি ছোট অংশের একটি করে ভেক্টরের সাথে মেলায়, প্রতিটি টোকেনের সেরা মিলটি রাখে, তারপর যোগ করে।")],
       [sh("src", "hot"), sh("pages", "hot"), sh("idx", "hot"), sh("llm", "hot")],
       [ln("src", "pages", "to", state="hot"), ln("pages", "idx", "to", state="hot"), ln("idx", "llm", "to", state="hot")],
       [("many vectors per page", "প্রতি পাতায় অনেক ভেক্টর"), None, None]),

    st(("Lost", "হারানো"),
       ("A summary can lose a number", "সারসংক্ষেপে সংখ্যা হারাতে পারে"),
       [("Summaries can hide detail. If a summary leaves out a number, no query can find it.",
         "সারসংক্ষেপ খুঁটিনাটি লুকিয়ে ফেলতে পারে। সারসংক্ষেপে কোনো সংখ্যা বাদ পড়লে কোনো প্রশ্নেই তা মেলে না।"),
        ("Keeping the raw object means the answering model still sees the original.",
         "মূল জিনিস রাখলে উত্তর-দেওয়া মডেল তবুও মূলটি দেখতে পায়।")],
       [sh("src", "hot"), sh("summ", "warn"), sh("idx", "warn"), sh("raw", "hot")],
       [ln("src", "summ", "to", state="warn"), ln("summ", "idx", "to", state="warn"), ln("idx", "raw", "to", state="hot")],
       [("summary", "সারসংক্ষেপ"), ("raw object", "কাঁচা জিনিস"), None],
       note=("warn", "If the summary leaves out a number, no query can find it.",
             "সারসংক্ষেপে কোনো সংখ্যা বাদ পড়লে কোনো প্রশ্নেই তা মেলে না।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Three designs keep charts, tables and slides searchable.",
         "তিনটি নকশা চার্ট, টেবিল আর স্লাইডকে সার্চযোগ্য রাখে।")],
       [sh("src"), sh("clip"), sh("summ"), sh("pages"), sh("idx"), sh("raw"), sh("llm")],
       [ln("src", "clip", "to"), ln("src", "summ", "to"), ln("src", "pages", "to"), ln("summ", "idx", "to"), ln("idx", "raw", "to")],
       [None, None, None],
       points=[("Of the two summary designs, prefer the one keeping the raw object.",
                "সারসংক্ষেপের দুটি নকশার মধ্যে যেটি মূল জিনিস রাখে সেটি বাছুন।"),
               ("ColPali stores many vectors per page, so measure index size.",
                "ColPali প্রতি পাতায় অনেক ভেক্টর রাখে, তাই ইনডেক্সের আকার মাপুন।"),
               ("Its gains come from the authors' benchmark, so test on your own documents.",
                "এর ফলাফল লেখকদের নিজেদের বেঞ্চমার্কে, তাই নিজের নথিতে পরীক্ষা করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
