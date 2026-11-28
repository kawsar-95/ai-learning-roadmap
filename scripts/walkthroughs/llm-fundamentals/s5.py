"""LLM Fundamentals · 05 Streaming vs non-streaming: same work, but streaming shows the first word early.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Tokens     Body: "A model writes its answer one token at a time."
  2 Waiting    Body: "non-streaming waits and sends the whole answer at the end."
  3 Streaming  Table: "Sending the answer in small pieces while the model is still writing it." "Server-Sent Events (SSE): A simple way for a server to keep pushing new pieces of text to a page over one connection."
  4 Latency    Table: "Streaming does not cut the total time; it cuts the wait before the first word." "Streaming makes an answer feel faster, but the model does the same work."
  5 Stream     "Stream any chat or text that a person reads as it arrives."
  6 Skip       "Skip streaming when code needs the full answer first, such as to parse or check JSON, and in batch jobs." Table: Pipeline, Batch job.
  7 Remember   The three "remember" lines above.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("model", "model", ("Model", "মডেল"), 110, 162),
    node("full", "file", ("Whole answer", "পুরো উত্তর"), 380, 75),
    node("ua", "user", ("Reader", "পাঠক"), 650, 75),
    node("pieces", "queue", ("Small pieces", "ছোট টুকরো"), 380, 250),
    node("ub", "user", ("Reader", "পাঠক"), 650, 250),
    node("parser", "tool", ("JSON parser", "JSON পার্সার"), 650, 162),
]

METRICS = [
    ("Wait before first word", "প্রথম শব্দের আগের অপেক্ষা"),
    ("Total time", "মোট সময়"),
    ("Model work", "মডেলের কাজ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Tokens", "টোকেন"),
       ("One token at a time", "একবারে একটি টোকেন"),
       [("A model writes its answer one token at a time.",
         "মডেল উত্তর লেখে একবারে একটি টোকেন করে।")],
       [sh("model", "hot", ("one token at a time", "একবারে একটি টোকেন"))],
       [],
       [None, None, None]),

    st(("Waiting", "অপেক্ষা"),
       ("Non-streaming waits", "নন-স্ট্রিমিং অপেক্ষা করে"),
       [("Non-streaming waits, and sends the whole answer at the end.",
         "নন-স্ট্রিমিং অপেক্ষা করে, আর শেষে পুরো উত্তর একসাথে পাঠায়।")],
       [sh("model", "hot"), sh("full", "warn", ("at the end", "শেষে")), sh("ua", "hot")],
       [ln("model", "full", "to", state="warn"), ln("full", "ua", "to", state="warn")],
       [(("waits"), ("অপেক্ষা")), None, None]),

    st(("Streaming", "স্ট্রিমিং"),
       ("Streaming sends small pieces", "স্ট্রিমিং ছোট টুকরো পাঠায়"),
       [("Streaming sends the answer in small pieces while the model is still writing it.",
         "স্ট্রিমিং মডেল লিখতে থাকার সময়েই উত্তরটা ছোট ছোট টুকরোয় পাঠায়।"),
        ("Server-Sent Events (SSE) is a simple way for a server to keep pushing new pieces of text to a page over one connection.",
         "Server-Sent Events (SSE) একটি সহজ উপায়, যাতে সার্ভার একটি কানেকশন দিয়েই পাতায় একের পর এক নতুন টুকরো পাঠাতে থাকে।")],
       [sh("model", "hot"), sh("pieces", "hot", ("while still writing", "লিখতে থাকার সময়েই")), sh("ub", "hot")],
       [ln("model", "pieces", "to", state="hot"), ln("pieces", "ub", "to", state="hot")],
       [(("earlier"), ("আগে")), None, None]),

    st(("Latency", "ল্যাটেন্সি"),
       ("Same work, earlier first word", "একই কাজ, আগে প্রথম শব্দ"),
       [("Streaming does not cut the total time. It cuts the wait before the first word.",
         "স্ট্রিমিং মোট সময় কমায় না; প্রথম শব্দের আগের অপেক্ষাটা কমায়।"),
        ("It makes an answer feel faster, but the model does the same work.",
         "এতে উত্তর দ্রুত মনে হয়, কিন্তু মডেলের কাজ একই থাকে।")],
       [sh("full", "dim"), sh("ua", "dim"), sh("pieces", "hot", ("first word sooner", "প্রথম শব্দ আগে")), sh("ub", "hot")],
       [ln("full", "ua", "to", state="dim"), ln("pieces", "ub", "to", state="hot")],
       [(("shorter"), ("কম")), (("not cut"), ("কমে না")), (("the same"), ("একই"))]),

    st(("Stream", "স্ট্রিম"),
       ("Stream what a person reads", "মানুষ যা পড়ে, তা স্ট্রিম করুন"),
       [("Stream any chat or text that a person reads as it arrives.",
         "মানুষ আসতে আসতেই পড়বে এমন যেকোনো চ্যাট বা লেখা স্ট্রিম করুন।")],
       [sh("model", "hot"), sh("pieces", "hot"), sh("ub", "hot", ("reads as it arrives", "আসতে আসতেই পড়ে"))],
       [ln("model", "pieces", "to", state="hot"), ln("pieces", "ub", "to", state="hot")],
       [None, None, None]),

    st(("Skip", "বাদ"),
       ("Skip it when code needs it all", "কোডের সবটা লাগলে বন্ধ রাখুন"),
       [("Skip streaming when code needs the full answer first, such as to parse or check JSON, and in batch jobs.",
         "কোডের যখন আগে পুরো উত্তর দরকার, যেমন JSON পার্স বা যাচাই করতে, আর ব্যাচ জবে, স্ট্রিমিং বন্ধ রাখুন।"),
        ("A pipeline is a chain of programs where one step's output is the next step's input, with no person reading in between.",
         "পাইপলাইন হলো প্রোগ্রামের একটা শিকল, যেখানে এক ধাপের আউটপুট পরের ধাপের ইনপুট; মাঝে কোনো মানুষ পড়ে না।")],
       [sh("model", "hot"), sh("full", "hot", ("full answer first", "আগে পুরো উত্তর")), sh("parser", "hot", ("parse or check", "পার্স বা যাচাই")), sh("pieces", "dim")],
       [ln("model", "full", "to", state="hot"), ln("full", "parser", "to", state="hot"), ln("model", "pieces", "to", state="dim")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Streaming makes an answer feel faster, but the model does the same work.",
         "স্ট্রিমিংয়ে উত্তর দ্রুত মনে হয়, কিন্তু মডেলের কাজ একই থাকে।")],
       [sh("model"), sh("pieces"), sh("ub")],
       [ln("model", "pieces", "to"), ln("pieces", "ub", "to")],
       [None, None, None],
       points=[("Stream any chat or text that a person reads as it arrives.",
                "মানুষ আসতে আসতেই পড়বে এমন যেকোনো চ্যাট বা লেখা স্ট্রিম করুন।"),
               ("Skip streaming when code needs the full answer first, such as to parse or check JSON.",
                "কোডের যখন আগে পুরো উত্তর দরকার, যেমন JSON পার্স বা যাচাই করতে, স্ট্রিমিং বন্ধ রাখুন।"),
               ("Skip streaming in batch jobs.",
                "ব্যাচ জবে স্ট্রিমিং বন্ধ রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
