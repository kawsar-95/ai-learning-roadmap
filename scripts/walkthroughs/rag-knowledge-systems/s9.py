"""RAG and Knowledge Systems · 09 Document parsing pipelines: Docling, Unstructured and LlamaParse side by side: how messy files become clean text before chunking.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Files     Body: "A RAG system is only as good as the text it indexes. Most enterprise knowledge sits in PDFs, scans, slide decks and spreadsheets, not clean strings."
  2 Layout    Pipeline: "Layout analysis: regions, reading order". "Page layout and reading order: Where headings, text and tables sit on a page, and the order in which a person would read them." "DocLayNet: The layout model Docling uses".
  3 OCR       Pipeline: "OCR + tables: text, cell structure". "OCR (optical character recognition): Reading the text from a picture of a page, such as a scan." Docling: TableFormer.
  4 Output    "emits structured Markdown or JSON, and only then is the result chunked." "Chunker: The tool that splits parsed text into smaller pieces for search."
  5 Three     "Docling, Unstructured and LlamaParse differ in where they run, which files they read, and how they treat tables and scans." "It is not a benchmark."
  6 Strategy  "Strategy: A setting in Unstructured that picks how a PDF is read: auto, fast, hi_res or ocr_only." "In Unstructured, hi_res uses a layout model, and ocr_only is for scans."
  7 Garbled   "Everything after parsing builds on the parser's output, so garbled text means garbled answers." The note-taker analogy.
  8 Remember  The Start here lines and the "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("file", "file", ("PDF / scan", "PDF / স্ক্যান"), 115, 60),
    node("layout", "service", ("Layout analysis", "লেআউট বোঝা"), 380, 60),
    node("ocr", "service", ("OCR + tables", "OCR ও টেবিল"), 645, 60),
    node("md", "file", ("Markdown / JSON", "Markdown / JSON"), 645, 190),
    node("chunk", "tool", ("Chunker", "চাঙ্কার"), 380, 190),
    node("ans", "note", ("Answers", "উত্তর"), 115, 190),
    node("docling", "tool", ("Docling", "Docling"), 130, 330),
    node("unst", "tool", ("Unstructured", "Unstructured"), 380, 330),
    node("llama", "tool", ("LlamaParse", "LlamaParse"), 630, 330),
]

METRICS = [
    ("Stage", "ধাপ"),
    ("Output", "ফল"),
    ("Comparison", "তুলনা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Files", "ফাইল"),
       ("Files are not clean strings", "ফাইল পরিষ্কার স্ট্রিং নয়"),
       [("A RAG system is only as good as the text it indexes.",
         "RAG সিস্টেম ততটাই ভালো, যতটা ভালো টেক্সট সে ইনডেক্স করে।"),
        ("Most enterprise knowledge sits in PDFs, scans, slide decks and spreadsheets, not clean strings.",
         "বেশির ভাগ এন্টারপ্রাইজ জ্ঞান থাকে PDF, স্ক্যান, স্লাইড ও স্প্রেডশিটে, পরিষ্কার স্ট্রিংয়ে নয়।")],
       [sh("file", "hot", ("PDFs, scans, slides", "PDF, স্ক্যান, স্লাইড")), sh("chunk", "dim")],
       [ln("file", "chunk", "to", state="dim")],
       [("read the file", "ফাইল পড়া"), None, None]),

    st(("Layout", "লেআউট"),
       ("Find the layout and reading order", "লেআউট আর পড়ার ক্রম বোঝা"),
       [("A parser first works out the page layout and the reading order.",
         "পার্সার আগে পাতার লেআউট আর পড়ার ক্রম বোঝে।"),
        ("That means where headings, text and tables sit, and the order in which a person would read them.",
         "মানে হেডিং, লেখা আর টেবিল কোথায় আছে, আর একজন মানুষ কোন ক্রমে সেগুলো পড়বে।")],
       [sh("file", "hot"), sh("layout", "hot", ("regions, reading order", "অংশ, পড়ার ক্রম")), sh("docling", "hot", ("DocLayNet", "DocLayNet"))],
       [ln("file", "layout", "to", state="hot"), ln("docling", "layout", "to", state="hot")],
       [("layout analysis", "লেআউট বোঝা"), None, None]),

    st(("OCR", "OCR"),
       ("Recover the text and the tables", "লেখা আর টেবিল বের করা"),
       [("Next the parser recovers the text, using OCR for scanned pages, and the structure of tables.",
         "তারপর পার্সার লেখা বের করে, স্ক্যান করা পাতায় OCR দিয়ে, আর টেবিলের স্ট্রাকচারও বের করে।"),
        ("OCR means reading the text from a picture of a page, such as a scan.",
         "OCR মানে পাতার ছবি, যেমন স্ক্যান, থেকে লেখা পড়ে নেওয়া।")],
       [sh("layout", "dim"), sh("ocr", "hot", ("text, cell structure", "লেখা, ঘরের স্ট্রাকচার")), sh("docling", "hot", ("TableFormer", "TableFormer"))],
       [ln("layout", "ocr", "to", state="hot"), ln("docling", "ocr", "to", state="hot")],
       [("OCR + tables", "OCR ও টেবিল"), None, None]),

    st(("Output", "ফল"),
       ("Write Markdown or JSON, then chunk", "Markdown বা JSON লিখে তারপর চাঙ্ক"),
       [("The parser writes structured Markdown or JSON, and only then is the result chunked.",
         "পার্সার স্ট্রাকচার্ড Markdown বা JSON লেখে, আর তারপরই ফল চাঙ্কে ভাগ হয়।"),
        ("The chunker is the tool that splits parsed text into smaller pieces for search.",
         "চাঙ্কার সেই টুল, যা পার্স করা টেক্সটকে সার্চের জন্য ছোট টুকরোয় ভাগ করে।")],
       [sh("ocr", "dim"), sh("md", "hot", ("typed elements", "ধরনসহ এলিমেন্ট")), sh("chunk", "hot")],
       [ln("ocr", "md", "to", state="hot"), ln("md", "chunk", "to", state="hot")],
       [None, ("Markdown or JSON", "Markdown বা JSON"), None]),

    st(("Three", "তিন পার্সার"),
       ("Three parsers side by side", "পাশাপাশি তিনটি পার্সার"),
       [("Docling, Unstructured and LlamaParse differ in where they run, which files they read, and how they treat tables and scans.",
         "Docling, Unstructured ও LlamaParse আলাদা হয় কোথায় চলে, কোন ফাইল পড়ে, আর টেবিল ও স্ক্যান কীভাবে সামলায় তাতে।"),
        ("The comparison comes from each project's own documentation or paper. It is not a benchmark.",
         "তুলনাটি প্রতিটি প্রজেক্টের নিজস্ব ডকুমেন্টেশন বা পেপার থেকে নেওয়া। এটি বেঞ্চমার্ক নয়।")],
       [sh("docling", "hot", ("IBM Research, MIT-licensed", "IBM Research, MIT-লাইসেন্সড")), sh("unst", "hot", ("open source", "ওপেন সোর্স")), sh("llama", "hot", ("LlamaIndex", "LlamaIndex"))],
       [],
       [None, None, ("not a benchmark", "বেঞ্চমার্ক নয়")]),

    st(("Strategy", "স্ট্র্যাটেজি"),
       ("Unstructured picks a strategy", "Unstructured একটি স্ট্র্যাটেজি বেছে নেয়"),
       [("In Unstructured, a strategy setting picks how a PDF is read: auto, fast, hi_res or ocr_only.",
         "Unstructured-এ স্ট্র্যাটেজি সেটিং ঠিক করে PDF কীভাবে পড়া হবে: auto, fast, hi_res বা ocr_only।"),
        ("hi_res uses a layout model, and ocr_only is for scans.",
         "hi_res লেআউট মডেল ব্যবহার করে, আর ocr_only স্ক্যানের জন্য।")],
       [sh("file", "hot"), sh("unst", "hot", ("auto, fast, hi_res, ocr_only", "auto, fast, hi_res, ocr_only")), sh("md", "hot")],
       [ln("file", "unst", "to", state="hot"), ln("unst", "md", "to", state="hot")],
       [None, None, None]),

    st(("Garbled", "গুলিয়ে যাওয়া"),
       ("Garbled text means garbled answers", "গুলিয়ে যাওয়া টেক্সট মানে গুলিয়ে যাওয়া উত্তর"),
       [("Everything after parsing builds on the parser's output, so garbled text means garbled answers.",
         "পার্সিংয়ের পরের সব কাজ পার্সারের ফলের ওপর দাঁড়ায়, তাই গুলিয়ে যাওয়া টেক্সট মানে গুলিয়ে যাওয়া উত্তর।"),
        ("Think of a student copying a textbook into notes: the friend sees only the notes.",
         "ভাবুন একজন ছাত্র পাঠ্যবই থেকে নোট টুকছে: বন্ধু শুধু নোটই দেখে।")],
       [sh("md", "warn", ("garbled", "গুলিয়ে যাওয়া")), sh("chunk", "warn"), sh("ans", "warn")],
       [ln("md", "chunk", "to", state="warn"), ln("chunk", "ans", "to", state="warn")],
       [None, ("garbled", "গুলিয়ে যাওয়া"), None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("A parsing pipeline turns PDFs, scans and slides into clean, structured text before that text is split into pieces.",
         "পার্সিং পাইপলাইন PDF, স্ক্যান ও স্লাইডকে পরিষ্কার, সাজানো টেক্সটে বদলায়, তারপর সেই টেক্সট টুকরো করা হয়।")],
       [sh("file", "hot"), sh("md", "hot"), sh("chunk", "hot")],
       [ln("file", "md", "to", state="hot"), ln("md", "chunk", "to", state="hot")],
       [None, None, None],
       points=[("Everything after parsing builds on the parser's output, so garbled text means garbled answers.",
                "পার্সিংয়ের পরের সব কাজ পার্সারের ফলের ওপর দাঁড়ায়, তাই গুলিয়ে যাওয়া টেক্সট মানে গুলিয়ে যাওয়া উত্তর।"),
               ("Docling, Unstructured and LlamaParse differ in where they run, which files they read, and how they treat tables and scans.",
                "Docling, Unstructured ও LlamaParse আলাদা হয় কোথায় চলে, কোন ফাইল পড়ে, আর টেবিল ও স্ক্যান কীভাবে সামলায় তাতে।"),
               ("In Unstructured, hi_res uses a layout model, and ocr_only is for scans.",
                "Unstructured-এ hi_res লেআউট মডেল ব্যবহার করে, আর ocr_only স্ক্যানের জন্য।")]),
]

WALK = walk(760, 400, NODES, METRICS, CAPTION, STEPS)
