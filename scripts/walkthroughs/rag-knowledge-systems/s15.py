"""Choosing a parsing strategy, and where parsing fails: pick the Unstructured strategy by file type, and plan an OCR fallback.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Choose    Body: "Which parsing strategy fits depends on the file: a text-only PDF, a document with tables, or a scan." Diagram: "strategy=auto: default; picks for you".
  2 Fast      Term "fast": "A strategy that only reads the selectable text layer already in the PDF." "fast needs a text layer".
  3 hi_res    Term "hi_res": "The Unstructured strategy for files with tables; the auto setting chooses it when tables are needed." Diagram: "struggles with multi-column", "per the Unstructured docs".
  4 Scan      "A plain scan has no such layer." Term "ocr_only": "only reads text from the picture of the page, so it can handle scans." "for a scanned PDF use auto or ocr_only (OCR needs Tesseract)".
  5 Check     "check the result is not empty." "Plan an OCR fallback: if the result is empty, re-run with ocr_only or a parser that reads page layout."
  6 Columns   "Check multi-column documents by eye, and test parsers on your own documents." Layman: "the AI may answer with a wrong number."
  7 Remember  The three "Plan" and "Check" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("pdf", "file", ("PDF file", "PDF ফাইল"), 75, 160),
    node("auto", "service", ("strategy=auto", "strategy=auto"), 235, 160),
    node("fast", "tool", ("fast", "fast"), 420, 60),
    node("hires", "tool", ("hi_res", "hi_res"), 420, 160),
    node("ocr", "tool", ("ocr_only", "ocr_only"), 420, 260),
    node("check", "shield", ("Empty check", "খালি কি না দেখা"), 600, 260),
    node("out", "file", ("Typed elements", "টাইপ-ঠিক-করা অংশ"), 655, 130),
]

METRICS = [
    ("Strategy", "স্ট্র্যাটেজি"),
    ("Needs", "যা লাগে"),
    ("Result", "ফল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Choose", "বাছুন"),
       ("Pick the strategy by file type", "ফাইলের ধরন দেখে স্ট্র্যাটেজি বাছুন"),
       [("Which strategy fits depends on the file: text-only, tables, or a scan.",
         "কোন স্ট্র্যাটেজি ঠিক, তা ফাইলের ওপর নির্ভর করে: শুধু টেক্সট, টেবিল, নাকি স্ক্যান।"),
        ("auto is the default and picks for you.",
         "auto ডিফল্ট, সে আপনার জন্য বেছে নেয়।")],
       [sh("pdf", "hot"), sh("auto", "hot"),
        sh("fast", "hot"), sh("hires", "hot"), sh("ocr", "hot")],
       [ln("pdf", "auto", "to", state="hot"), ln("auto", "fast", "to", state="hot"),
        ln("auto", "hires", "to", state="hot"), ln("auto", "ocr", "to", state="hot")],
       [("auto", "auto"), None, None]),

    st(("Fast", "fast"),
       ("fast reads only the text layer", "fast শুধু টেক্সট লেয়ার পড়ে"),
       [("fast only reads the selectable text layer already in the PDF.",
         "fast শুধু PDF-এ আগে থেকে থাকা, সিলেক্ট করা যায় এমন টেক্সট লেয়ার পড়ে।"),
        ("So it needs a text layer.",
         "তাই এর টেক্সট লেয়ার লাগে।")],
       [sh("pdf", "dim"), sh("auto", "dim"), sh("fast", "hot")],
       [ln("pdf", "auto", "to", state="dim"), ln("auto", "fast", "to", state="hot")],
       [("fast", "fast"), ("text layer", "টেক্সট লেয়ার"), None]),

    st(("hi_res", "hi_res"),
       ("hi_res is for files with tables", "টেবিলওয়ালা ফাইলের জন্য hi_res"),
       [("hi_res is the Unstructured strategy for files with tables. The auto setting chooses it when tables are needed.",
         "hi_res টেবিলওয়ালা ফাইলের জন্য Unstructured-এর স্ট্র্যাটেজি। টেবিল দরকার হলে auto সেটিং এটি বেছে নেয়।"),
        ("It struggles with multi-column pages, per the Unstructured docs.",
         "Unstructured ডকুমেন্টেশন অনুযায়ী মাল্টি-কলাম পাতায় এর সমস্যা হয়।")],
       [sh("auto", "dim"), sh("hires", "hot"), sh("out", "hot")],
       [ln("auto", "hires", "to", state="hot"), ln("hires", "out", "to", state="hot")],
       [("hi_res", "hi_res"), ("tables", "টেবিল"), ("typed elements", "টাইপ-ঠিক-করা অংশ")]),

    st(("Scan", "স্ক্যান"),
       ("A scan has no text layer", "স্ক্যানে টেক্সট লেয়ার নেই"),
       [("A plain scan has no text layer, so fast has nothing to read. ocr_only reads text from the picture of the page, so it can handle scans.",
         "সাধারণ স্ক্যানে টেক্সট লেয়ার থাকে না, তাই fast-এর পড়ার মতো কিছু থাকে না। ocr_only পাতার ছবি থেকে লেখা পড়ে, তাই স্ক্যানও সামলাতে পারে।"),
        ("For a scanned PDF use auto or ocr_only. OCR needs Tesseract.",
         "স্ক্যান করা PDF-এ auto বা ocr_only ব্যবহার করুন। OCR-এর জন্য Tesseract লাগে।")],
       [sh("pdf", "warn"), sh("auto", "dim"), sh("fast", "warn"), sh("ocr", "hot")],
       [ln("pdf", "auto", "to", state="dim"), ln("auto", "fast", "to", state="warn"), ln("auto", "ocr", "to", state="hot")],
       [("ocr_only", "ocr_only"), ("Tesseract", "Tesseract"), None]),

    st(("Check", "যাচাই"),
       ("Plan an OCR fallback", "OCR বিকল্প রাখুন"),
       [("Check that the result is not empty.",
         "ফল খালি কি না দেখে নিন।"),
        ("If the result is empty, re-run with ocr_only or a parser that reads page layout.",
         "ফল ফাঁকা হলে ocr_only বা পাতার লেআউট পড়তে পারে এমন পার্সার দিয়ে আবার চালান।")],
       [sh("fast", "warn"), sh("ocr", "hot"), sh("check", "hot"), sh("out", "hot")],
       [ln("fast", "ocr", "to", state="warn"), ln("ocr", "check", "to", state="hot"), ln("check", "out", "to", state="hot")],
       [("ocr_only", "ocr_only"), None, ("not empty", "খালি নয়")],
       note=("warn", "Always plan an OCR fallback, and check the parser output before you use it.",
             "সবসময় OCR বিকল্প রাখুন, আর ব্যবহারের আগে পার্সারের আউটপুট দেখে নিন।")),

    st(("Columns", "কলাম"),
       ("Check multi-column pages by eye", "মাল্টি-কলাম পাতা চোখে দেখুন"),
       [("Check multi-column documents by eye, and test parsers on your own documents.",
         "একাধিক কলামের নথি চোখে দেখে নিন, আর নিজের নথিতে পার্সার পরীক্ষা করুন।"),
        ("With mixed columns the words come out in the wrong order, so the AI may answer with a wrong number.",
         "কলাম মিশে গেলে শব্দগুলো ভুল অর্ডারে আসে, তাই AI ভুল সংখ্যা বলতে পারে।")],
       [sh("pdf", "hot"), sh("hires", "warn"), sh("out", "warn")],
       [ln("pdf", "hires", "to", state="hot"), ln("hires", "out", "to", state="warn")],
       [None, None, ("check by eye", "চোখে দেখুন")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Pick the strategy by file type: text-only, tables, or a scan.",
         "ফাইলের ধরন দেখে স্ট্র্যাটেজি বাছুন: শুধু টেক্সট, টেবিল, নাকি স্ক্যান।")],
       [sh("pdf"), sh("auto"), sh("fast"), sh("hires"), sh("ocr"), sh("check"), sh("out")],
       [ln("pdf", "auto", "to"), ln("auto", "fast", "to"), ln("auto", "hires", "to"), ln("auto", "ocr", "to"),
        ln("ocr", "check", "to"), ln("check", "out", "to")],
       [None, None, None],
       points=[("fast needs a text layer, so for a scanned PDF use auto or ocr_only and check the result is not empty.",
                "fast-এর টেক্সট লেয়ার লাগে, তাই স্ক্যান করা PDF-এ auto বা ocr_only ব্যবহার করুন এবং ফল খালি কি না দেখে নিন।"),
               ("Plan an OCR fallback: if the result is empty, re-run with ocr_only or a parser that reads page layout.",
                "OCR বিকল্প রাখুন: ফল ফাঁকা হলে ocr_only বা পাতার লেআউট পড়তে পারে এমন পার্সার দিয়ে আবার চালান।"),
               ("Check multi-column documents by eye, and test parsers on your own documents.",
                "একাধিক কলামের নথি চোখে দেখে নিন, আর নিজের নথিতে পার্সার পরীক্ষা করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
