"""Part AI Engineering book · 02 Understanding Foundation Models: training data, architecture and size.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Data        Start here: "A model is only as good as its data. No Vietnamese text in training means no Vietnamese translation."
  2 Languages   Terms: "Low-resource language: A language with little text in the training data. Models usually do worse on it."
  3 Token cost  Start here: "The same meaning needs about 7 tokens in English, 32 in Hindi, and 72 in Burmese, so costs differ." Body: "Non-English users can therefore pay far more and wait far longer for the same request."
  4 Seq2seq     Body: "A seq2seq encoder reads the input one token at a time and compresses it into a single final hidden state. The decoder generates the output from that state." Terms: Seq2seq.
  5 Attention   Terms: "Attention mechanism ... like flipping to any page of a book". Body: "Transformers also process input tokens in parallel ... decoding is still sequential."
  6 Chinchilla  Terms: "compute-optimal training needs about 20 training tokens per parameter. Model size and data grow together." Start here: "Bigger is not always better".
  7 Experts     Terms: "Mixture-of-experts (MoE) runs only a few parameter groups, called experts, per token. A 46.7-billion-parameter model can run at roughly the cost and speed of a 12.9-billion one."
  8 Remember    The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "file", ("Training data", "ট্রেনিং ডেটা"), 110, 162),
    node("model", "model", ("Model", "মডেল"), 380, 162),
    node("meaning", "note", ("Same meaning", "একই অর্থ"), 110, 162),
    node("en", "file", ("English", "ইংরেজি"), 380, 70),
    node("hi", "file", ("Hindi", "হিন্দি"), 380, 162),
    node("my", "file", ("Burmese", "বর্মিজ"), 380, 254),
    node("input", "file", ("Whole input", "পুরো ইনপুট"), 110, 162),
    node("summary", "note", ("One summary", "একটা সারাংশ"), 380, 162),
    node("dec", "model", ("Decoder", "ডিকোডার"), 650, 162),
    node("prev", "file", ("Earlier tokens", "আগের টোকেন"), 110, 162),
    node("params", "chart", ("Parameters", "প্যারামিটার"), 380, 162),
    node("experts", "tool", ("Experts", "এক্সপার্ট"), 650, 162),
]

METRICS = [
    ("Tokens for same meaning", "একই অর্থে টোকেন"),
    ("Tokens per parameter", "প্রতি প্যারামিটারে টোকেন"),
    ("Active parameters", "চালু প্যারামিটার"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Data", "ডেটা"),
       ("A model is only as good as its data", "মডেল তার ডেটার চেয়ে ভালো হয় না"),
       [("A model is only as good as its data.",
         "মডেল তার ডেটার চেয়ে ভালো হয় না।"),
        ("No Vietnamese text in training means no Vietnamese translation.",
         "ট্রেনিংয়ে ভিয়েতনামি লেখা না থাকলে ভিয়েতনামিতে অনুবাদ হয় না।")],
       [sh("data", "hot", ("no Vietnamese text", "ভিয়েতনামি লেখা নেই")),
        sh("model", "warn", ("no Vietnamese translation", "ভিয়েতনামিতে অনুবাদ নেই"))],
       [ln("data", "model", "to", state="warn")],
       [None, None, None]),

    st(("Languages", "ভাষা"),
       ("Low-resource languages", "লো-রিসোর্স ল্যাঙ্গুয়েজ"),
       [("A low-resource language has little text in the training data.",
         "লো-রিসোর্স ল্যাঙ্গুয়েজ হলো যে ভাষার লেখা ট্রেনিং ডেটায় কম।"),
        ("Models usually do worse on it.",
         "মডেল সাধারণত এতে দুর্বল পারফর্ম করে।")],
       [sh("data", "hot", ("little text", "কম লেখা")),
        sh("model", "warn", ("usually does worse", "সাধারণত দুর্বল"))],
       [ln("data", "model", "to", state="warn")],
       [None, None, None]),

    st(("Token cost", "টোকেন খরচ"),
       ("The same meaning costs different tokens", "একই অর্থে টোকেন আলাদা"),
       [("The same meaning needs about 7 tokens in English, 32 in Hindi, and 72 in Burmese, so costs differ.",
         "একই অর্থে ইংরেজিতে প্রায় ৭, হিন্দিতে ৩২ আর বর্মিজে ৭২টি টোকেন লাগে, তাই খরচ আলাদা হয়।"),
        ("Non-English users can therefore pay far more and wait far longer for the same request.",
         "তাই ইংরেজি ছাড়া অন্য ভাষার ব্যবহারকারী একই অনুরোধে অনেক বেশি খরচ করতে পারেন, আর অনেক বেশি অপেক্ষাও করতে পারেন।")],
       [sh("meaning", "hot"),
        sh("en", "hot", ("about 7 tokens", "প্রায় ৭টি টোকেন")),
        sh("hi", "warn", ("32 tokens", "৩২টি টোকেন")),
        sh("my", "warn", ("72 tokens", "৭২টি টোকেন"))],
       [ln("meaning", "en", "to", state="hot"), ln("meaning", "hi", "to", state="warn"), ln("meaning", "my", "to", state="warn")],
       [("7, 32, 72", "৭, ৩২, ৭২"), None, None]),

    st(("Seq2seq", "seq2seq"),
       ("Seq2seq: one summary", "seq2seq: একটাই সারাংশ"),
       [("A seq2seq encoder reads the input one token at a time and compresses it into a single final hidden state. The decoder generates the output from that state.",
         "seq2seq এনকোডার ইনপুট একটা একটা করে টোকেন পড়ে আর চেপে একটা শেষ হিডেন স্টেটে আনে। ডিকোডার সেই স্টেট থেকে আউটপুট লেখে।"),
        ("The decoder only ever sees a compressed summary of the input, like answering questions about a book using only its summary.",
         "ডিকোডার ইনপুটের শুধু চাপা সারাংশ দেখে, যেন বইয়ের সারাংশ দেখে বইয়ের প্রশ্নের উত্তর দেওয়া।")],
       [sh("input", "hot"), sh("summary", "warn", ("compressed", "চাপা")), sh("dec", "hot")],
       [ln("input", "summary", "to", state="hot"), ln("summary", "dec", "to", state="warn")],
       [None, None, None]),

    st(("Attention", "অ্যাটেনশন"),
       ("Attention looks at every earlier token", "অ্যাটেনশন আগের প্রতিটি টোকেন দেখে"),
       [("The attention mechanism lets the model look directly at every earlier piece of text when writing the next. It is like flipping to any page of a book.",
         "অ্যাটেনশন মেকানিজমে পরের অংশ লেখার সময় মডেল আগের প্রতিটি টুকরোর দিকে সরাসরি তাকাতে পারে। যেন বইয়ের যেকোনো পাতা উল্টে দেখা।"),
        ("Transformers also process input tokens in parallel. Decoding, one output token at a time, is still sequential.",
         "ট্রান্সফরমার ইনপুট টোকেন একসাথে প্রসেস করে। তবে একটা একটা করে আউটপুট টোকেন বানানো (ডিকোডিং) এখনো ক্রমানুসারে হয়।")],
       [sh("prev", "hot", ("every earlier token", "আগের প্রতিটি টোকেন")),
        sh("model", "hot", ("attention", "অ্যাটেনশন")),
        sh("dec", "dim", ("next token", "পরের টোকেন"))],
       [ln("prev", "model", "to", state="hot"), ln("model", "dec", "to", state="dim")],
       [None, None, None]),

    st(("Chinchilla", "চিনচিলা"),
       ("Size and data grow together", "মডেল আর ডেটা একসাথে বাড়ে"),
       [("The Chinchilla scaling law says compute-optimal training needs about 20 training tokens per parameter. Model size and data grow together.",
         "চিনচিলা স্কেলিং ল বলে, কম্পিউট-অপটিমাল ট্রেনিংয়ে প্রতি প্যারামিটারে প্রায় ২০টি ট্রেনিং টোকেন লাগে। মডেল আর ডেটা একসাথে বাড়াতে হয়।"),
        ("Bigger is not always better: a large model on too little data can lose to a smaller, well-trained one.",
         "বড় মানেই ভালো নয়: কম ডেটায় ট্রেইন করা বড় মডেল, ভালোভাবে ট্রেইন করা ছোট মডেলের কাছে হারতে পারে।")],
       [sh("data", "hot", ("training tokens", "ট্রেনিং টোকেন")),
        sh("params", "hot", ("about 20 per parameter", "প্রতি প্যারামিটারে প্রায় ২০"))],
       [ln("data", "params", "to", state="hot")],
       [None, "about 20", None]),

    st(("Experts", "এক্সপার্ট"),
       ("Mixture-of-experts: few active parameters", "মিক্সচার-অব-এক্সপার্টস: অল্প চালু প্যারামিটার"),
       [("Mixture-of-experts (MoE) runs only a few parameter groups, called experts, per token.",
         "মিক্সচার-অব-এক্সপার্টস (MoE) প্রতি টোকেনে প্যারামিটারের মাত্র কয়েকটা গ্রুপ, মানে এক্সপার্ট, চালায়।"),
        ("A 46.7-billion-parameter model can run at roughly the cost and speed of a 12.9-billion one.",
         "তাই ৪৬.৭ বিলিয়ন প্যারামিটারের মডেল মোটামুটি ১২.৯ বিলিয়নের মডেলের খরচ আর গতিতে চলতে পারে।")],
       [sh("model", "hot", ("46.7B parameters", "৪৬.৭B প্যারামিটার")),
        sh("experts", "hot", ("a few per token", "প্রতি টোকেনে কয়েকটা"))],
       [ln("model", "experts", "to", state="hot")],
       [None, None, ("roughly 12.9B", "মোটামুটি ১২.৯B")]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Data, architecture and size shape a model.",
         "ডেটা, আর্কিটেকচার আর সাইজ মডেলকে গড়ে তোলে।")],
       [sh("data", "hot", x=112), sh("model", "hot", x=365), sh("params", "hot", x=630)],
       [ln("data", "model", "to", state="hot"), ln("model", "params", "to", state="hot")],
       [None, None, None],
       points=[("A model is only as good as its data.", "মডেল তার ডেটার চেয়ে ভালো হয় না।"),
               ("Attention lets the model look at every earlier token, not just a summary. Transformers still dominate.",
                "অ্যাটেনশন শুধু সারাংশ নয়, আগের প্রতিটি টোকেন দেখতে দেয়। ট্রান্সফরমার এখনো এগিয়ে।"),
               ("Bigger is not always better.", "বড় মানেই ভালো নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
