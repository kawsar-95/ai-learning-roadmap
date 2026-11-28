"""LLM Fundamentals · 08 Multimodal inputs (vision, audio, PDFs): every kind of input becomes numbers that one model reads next to the text.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Inputs    Start here: "Many models now take images, audio, video frames, and PDF pages, not just text."
  2 Encoders  Glossary "Encoder": "A model that turns one kind of input, such as an image, into numbers". Diagram: "Each modality has a specialised encoder".
  3 Join      Diagram: "a learned projection maps them into the LLM's token space, where a single transformer attends over all of them." Glossary "Embedding vector": "The model reads these numbers, not pixels or sound."
  4 Tiny text Warning: "they still hallucinate on tiny text, fine numerics, and rotated pages." Lab: "A guess often looks as sure as a correct reading."
  5 OCR       Remember: "To read invoices or IDs exactly, use a dedicated OCR engine, then give the text to the LLM." Glossary "OCR".
  6 PDFs      Glossary "Text extraction": "fast and cheap, but it loses the layout and the pictures." Body: "Hybrid: text-extract + page-image for tables/figures. This is what production systems ship."
  7 Remember  Start here: "Every kind of input ends up as numbers that the same model reads next to the text." and the other three remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("img", "file", ("Image", "ছবি"), 110, 62),
    node("aud", "file", ("Audio", "অডিও"), 110, 162),
    node("pdf", "file", ("PDF page", "PDF-এর পাতা"), 110, 262),
    node("enc", "tool", ("Encoder", "এনকোডার"), 260, 162),
    node("vec", "chart", ("Numbers", "সংখ্যা"), 440, 162),
    node("txt", "note", ("Text tokens", "টেক্সট টোকেন"), 440, 262),
    node("llm", "model", ("LLM core", "LLM কোর"), 650, 162),
    node("ocr", "tool", ("OCR engine", "OCR ইঞ্জিন"), 380, 162),
    node("ext", "tool", ("Text extraction", "টেক্সট এক্সট্র্যাকশন"), 380, 62),
    node("pgs", "file", ("Page images", "পাতার ইমেজ"), 380, 262),
]

METRICS = [
    ("Kinds of input", "ইনপুটের ধরন"),
    ("Model reads", "মডেল পড়ে"),
    ("Exact reading", "নিখুঁত পড়া"),
]

CAPTION = (
    "Illustrative: the labels are the section's own words.",
    "উদাহরণমাত্র: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Inputs", "ইনপুট"),
       ("More than text", "শুধু লেখা নয়"),
       [("Many models now take images, audio, video frames, and PDF pages, not just text.",
         "এখন অনেক মডেল শুধু লেখা নয়, ছবি, অডিও, ভিডিওর ফ্রেম আর PDF-এর পাতাও নেয়।")],
       [sh("img", "hot"), sh("aud", "hot"), sh("pdf", "hot"), sh("llm", "hot")],
       [ln("img", "llm", "to", state="hot"), ln("aud", "llm", "to", state="hot"), ln("pdf", "llm", "to", state="hot")],
       [("images, audio, PDFs", "ছবি, অডিও, PDF"), None, None]),

    st(("Encoders", "এনকোডার"),
       ("An encoder for each kind", "প্রতিটি ধরনের জন্য একটি এনকোডার"),
       [("An encoder is a model that turns one kind of input, such as an image, into numbers.",
         "এনকোডার এমন একটি মডেল, যে এক ধরনের ইনপুটকে, যেমন ছবি, সংখ্যায় বদলায়।"),
        ("Each modality has a specialised encoder.",
         "প্রতিটি মোডালিটির জন্য আলাদা বিশেষায়িত এনকোডার আছে।")],
       [sh("img", "hot"), sh("aud", "hot"), sh("pdf", "hot"), sh("enc", "hot", ("into numbers", "সংখ্যায়"))],
       [ln("img", "enc", "to", state="hot"), ln("aud", "enc", "to", state="hot"), ln("pdf", "enc", "to", state="hot")],
       [None, ("numbers", "সংখ্যা"), None]),

    st(("Join", "জোড়া"),
       ("The numbers join the text", "সংখ্যাগুলো লেখার সঙ্গে জোড়া লাগে"),
       [("A projection maps the numbers into the LLM's token space, next to the text tokens.",
         "প্রজেকশন সংখ্যাগুলোকে LLM-এর টোকেন স্পেসে টেক্সট টোকেনের পাশে বসায়।"),
        ("A single transformer then attends over all of them. It reads numbers, not pixels or sound.",
         "তারপর একটি ট্রান্সফর্মার সবগুলোর ওপর অ্যাটেনশন দেয়। সে সংখ্যা পড়ে, পিক্সেল বা শব্দ নয়।")],
       [sh("enc", "dim"), sh("vec", "hot"), sh("txt", "hot"), sh("llm", "hot", ("joint attention", "জয়েন্ট অ্যাটেনশন"))],
       [ln("enc", "vec", "to", state="dim"), ln("vec", "llm", "to", state="hot"), ln("txt", "llm", "to", state="hot")],
       [None, ("numbers, next to the text", "সংখ্যা, লেখার পাশে"), None]),

    st(("Tiny text", "ছোট লেখা"),
       ("Tiny text is misread", "ছোট লেখা ভুল পড়া হয়"),
       [("Vision models still misread tiny text, exact numbers, and rotated pages.",
         "ভিশন মডেল এখনো ছোট লেখা, নিখুঁত সংখ্যা আর ঘোরানো পাতা ভুল পড়ে।"),
        ("To hallucinate is to state something wrong as if it were true.",
         "হ্যালুসিনেট করা মানে ভুল কিছুকে সত্যের মতো করে বলা।")],
       [sh("img", "warn", ("tiny text", "ছোট লেখা")), sh("enc", "dim"), sh("vec", "dim"), sh("llm", "warn", ("guesses", "আন্দাজ করে"))],
       [ln("img", "enc", "to", state="dim"), ln("enc", "vec", "to", state="dim"), ln("vec", "llm", "to", state="warn")],
       [None, None, ("can be wrong", "ভুল হতে পারে")],
       note=("warn", "A guess often looks as sure as a correct reading.",
             "আন্দাজও প্রায়ই সঠিক পড়ার মতোই নিশ্চিত শোনায়।")),

    st(("OCR", "OCR"),
       ("OCR first, then the LLM", "আগে OCR, তারপর LLM"),
       [("To read invoices or IDs exactly, use a dedicated OCR engine.",
         "ইনভয়েস বা আইডি নিখুঁতভাবে পড়তে আলাদা OCR ইঞ্জিন ব্যবহার করুন।"),
        ("OCR is software that reads the letters in a picture of text. Then give the text to the LLM.",
         "OCR এমন সফটওয়্যার, যা লেখার ছবি থেকে অক্ষর পড়ে। তারপর লেখাটা LLM-কে দিন।")],
       [sh("img", "hot", x=110, y=162), sh("ocr", "hot", ("reads the letters", "অক্ষর পড়ে")), sh("llm", "hot", ("gets the text", "লেখা পায়"))],
       [ln("img", "ocr", "to", state="hot"), ln("ocr", "llm", "to", state="hot", label=("text", "লেখা"))],
       [None, None, ("OCR, then the LLM", "আগে OCR, পরে LLM")]),

    st(("PDFs", "PDF"),
       ("PDFs: text and page images", "PDF: লেখা আর পাতার ছবি"),
       [("Text extraction pulls the plain text out of a PDF. It is fast and cheap, but it loses the layout and the pictures.",
         "টেক্সট এক্সট্র্যাকশন PDF থেকে শুধু লেখাটা বের করে। এটা দ্রুত আর সস্তা, কিন্তু লেআউট আর ছবি হারিয়ে যায়।"),
        ("Production systems mix text extraction with page images for tables and figures.",
         "প্রোডাকশন সিস্টেম টেক্সট এক্সট্র্যাকশনের সাথে টেবিল আর ছবির জন্য পাতার ইমেজ মেলায়।")],
       [sh("pdf", "hot", x=110, y=162), sh("ext", "hot", ("fast and cheap", "দ্রুত আর সস্তা")),
        sh("pgs", "hot", ("tables and figures", "টেবিল আর ছবি")), sh("llm", "hot")],
       [ln("pdf", "ext", "to", state="hot"), ln("pdf", "pgs", "to", state="hot"),
        ln("ext", "llm", "to", state="hot"), ln("pgs", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Every kind of input ends up as numbers that the same model reads next to the text.",
         "প্রতিটি ইনপুট শেষে সংখ্যা হয়ে যায়, যা একই মডেল লেখার পাশাপাশি পড়ে।")],
       [sh("img"), sh("aud"), sh("pdf"), sh("enc"), sh("vec"), sh("txt"), sh("llm")],
       [ln("img", "enc", "to"), ln("aud", "enc", "to"), ln("pdf", "enc", "to"),
        ln("enc", "vec", "to"), ln("vec", "llm", "to"), ln("txt", "llm", "to")],
       [None, None, None],
       points=[("Vision models still misread tiny text, exact numbers, and rotated pages.",
                "ভিশন মডেল এখনো ছোট লেখা, নিখুঁত সংখ্যা আর ঘোরানো পাতা ভুল পড়ে।"),
               ("To read invoices or IDs exactly, use a dedicated OCR engine, then give the text to the LLM.",
                "ইনভয়েস বা আইডি নিখুঁতভাবে পড়তে আলাদা OCR ইঞ্জিন ব্যবহার করুন, তারপর লেখাটা LLM-কে দিন।"),
               ("For PDFs, production systems mix text extraction with page images for tables and figures.",
                "PDF-এর জন্য প্রোডাকশন সিস্টেম টেক্সট এক্সট্র্যাকশনের সাথে টেবিল আর ছবির জন্য পাতার ইমেজ মেলায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
