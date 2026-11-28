"""Part AI Engineering book · 04 Evaluation Methodology: language modeling metrics and exact evaluation.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Open-ended  Body: "Foundation models are open-ended: a single prompt can have countless acceptable answers." "Open-ended tasks have no fixed list of correct outputs to compare against."
  2 Perplexity  Body: "Perplexity (PPL) is the exponential of cross entropy ... The more uncertain a model is about the next token, the higher its perplexity." Info: "less reliable as a quality signal after post-training (SFT/RLHF)".
  3 Run tests   Body: "Functional correctness checks whether a system actually does what it was asked to do ... The generated code is run against test cases."
  4 pass@k      Body: "a model's score (e.g., pass@k) reflects how often at least one of k generated samples passes all tests. Benchmarks like HumanEval and MBPP use this approach."
  5 Word overlap Body: "When functional correctness can't be automated, you can instead compare a generated response against reference (ground-truth) responses." "lexical similarity: token overlap, measured with metrics like BLEU, ROUGE ..."
  6 Embeddings  Body: "An embedding is a numerical vector that tries to capture the meaning of a piece of data ... Good embeddings place similar inputs closer together, measured by cosine similarity." "semantic similarity depends on the quality of the underlying embedding model."
  7 Miss phrasing Body: "Exact match fails whenever there's more than one valid phrasing. Lexical similarity depends heavily on having a comprehensive, correct set of references."
  8 Remember    Start here: "When you can, run generated code against tests. Otherwise, compare with reference answers."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("root", "model", ("Model output", "মডেলের আউটপুট"), 110, 162),
    node("ppl", "chart", ("Perplexity", "পারপ্লেক্সিটি"), 380, 162),
    node("tests", "tool", ("Test cases", "টেস্ট কেস"), 380, 70),
    node("passk", "chart", ("pass@k", "pass@k"), 650, 70),
    node("ref", "file", ("Reference answer", "রেফারেন্স উত্তর"), 380, 254),
    node("lex", "tool", ("Word overlap", "শব্দের মিল"), 650, 254),
    node("emb", "note", ("Embedding", "এমবেডিং"), 380, 162),
    node("cos", "chart", ("Cosine similarity", "কোসাইন সিমিলারিটি"), 650, 162),
]

METRICS = [
    ("Perplexity", "পারপ্লেক্সিটি"),
    ("Tests", "টেস্ট"),
    ("Similarity", "সিমিলারিটি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Open-ended", "খোলা ধরন"),
       ("Open-ended answers are hard to check", "খোলা ধরনের উত্তর যাচাই করা কঠিন"),
       [("Foundation models are open-ended: a single prompt can have countless acceptable answers.",
         "ফাউন্ডেশন মডেল খোলা ধরনের: একটা প্রম্পটের অসংখ্য গ্রহণযোগ্য উত্তর থাকতে পারে।"),
        ("There is no fixed list of correct outputs to compare against.",
         "তুলনা করার মতো সঠিক আউটপুটের কোনো নির্দিষ্ট তালিকা নেই।")],
       [sh("root", "hot", ("many answers", "অসংখ্য উত্তর")),
        sh("ref", "warn", ("no fixed list", "নির্দিষ্ট তালিকা নেই"))],
       [ln("root", "ref", "to", state="warn")],
       [None, None, None]),

    st(("Perplexity", "পারপ্লেক্সিটি"),
       ("Perplexity: how unsure is the model", "পারপ্লেক্সিটি: মডেল কতটা অনিশ্চিত"),
       [("Perplexity is the exponential of cross entropy. The more uncertain a model is about the next token, the higher its perplexity.",
         "পারপ্লেক্সিটি ক্রস এন্ট্রপির এক্সপোনেনশিয়াল। পরের টোকেন নিয়ে মডেল যত অনিশ্চিত, পারপ্লেক্সিটি তত বেশি।"),
        ("Lower perplexity means better prediction.",
         "পারপ্লেক্সিটি কম মানে ভালো অনুমান।")],
       [sh("root", "hot"), sh("ppl", "hot", ("more unsure, higher", "যত অনিশ্চিত, তত বেশি"))],
       [ln("root", "ppl", "to", state="hot")],
       [("Higher when unsure", "অনিশ্চিত হলে বেশি"), None, None],
       note=("warn", "Perplexity is less reliable as a quality signal after post-training (SFT/RLHF).",
             "পোস্ট-ট্রেনিংয়ের (SFT/RLHF) পর পারপ্লেক্সিটি মানের সংকেত হিসেবে কম নির্ভরযোগ্য।")),

    st(("Run tests", "টেস্ট চালান"),
       ("Run the code against tests", "কোড টেস্টের বিপরীতে চালান"),
       [("Functional correctness checks whether a system actually does what it was asked to do. It is easiest to automate for tasks with testable outcomes, such as code generation.",
         "ফাংশনাল করেক্টনেস দেখে সিস্টেম সত্যিই যা করতে বলা হয়েছে তা করছে কি না। কোড জেনারেশনের মতো টেস্ট করা যায় এমন কাজে এটা স্বয়ংক্রিয় করা সবচেয়ে সহজ।"),
        ("The generated code is run against test cases. The result is right or wrong, with no interpretation needed.",
         "বানানো কোড টেস্ট কেসের বিপরীতে চালানো হয়। ফলাফল ঠিক বা ভুল, ব্যাখ্যার দরকার নেই।")],
       [sh("root", "hot", ("generated code", "বানানো কোড")), sh("tests", "hot", ("right or wrong", "ঠিক বা ভুল"))],
       [ln("root", "tests", "to", state="hot")],
       [None, ("right or wrong", "ঠিক বা ভুল"), None]),

    st(("pass@k", "pass@k"),
       ("pass@k scores the tests", "pass@k টেস্টের স্কোর দেয়"),
       [("A model's score, such as pass@k, reflects how often at least one of k generated samples passes all tests.",
         "মডেলের স্কোর, যেমন pass@k, বলে বানানো k সংখ্যক নমুনার অন্তত একটা কতবার সব টেস্ট পাস করে।"),
        ("Benchmarks like HumanEval and MBPP use this approach.",
         "HumanEval আর MBPP-এর মতো বেঞ্চমার্ক এই পদ্ধতি ব্যবহার করে।")],
       [sh("root", "dim"), sh("tests", "hot"), sh("passk", "hot", ("all tests", "সব টেস্ট"))],
       [ln("root", "tests", "to", state="dim"), ln("tests", "passk", "to", state="hot")],
       [None, ("at least one of k passes", "k-এর অন্তত একটা পাস"), None]),

    st(("Word overlap", "শব্দের মিল"),
       ("No tests? Compare with references", "টেস্ট নেই? রেফারেন্সের সাথে মেলান"),
       [("When functional correctness can't be automated, you can compare a generated response against reference (ground-truth) responses.",
         "ফাংশনাল করেক্টনেস স্বয়ংক্রিয় করা না গেলে বানানো উত্তরকে রেফারেন্স (ground-truth) উত্তরের সাথে মেলানো যায়।"),
        ("Lexical similarity is token overlap, measured with metrics like BLEU and ROUGE.",
         "লেক্সিক্যাল সিমিলারিটি হলো টোকেনের মিল, যা BLEU আর ROUGE-এর মতো মেট্রিক দিয়ে মাপা হয়।")],
       [sh("root", "hot"), sh("ref", "hot"), sh("lex", "hot", ("BLEU, ROUGE", "BLEU, ROUGE"))],
       [ln("root", "ref", "to", state="hot"), ln("ref", "lex", "to", state="hot")],
       [None, None, None],
       note=("warn", "Lexical similarity depends heavily on having a comprehensive, correct set of references.",
             "লেক্সিক্যাল সিমিলারিটি অনেকটাই নির্ভর করে পূর্ণাঙ্গ ও সঠিক রেফারেন্সের সেটের ওপর।")),

    st(("Embeddings", "এমবেডিং"),
       ("Compare meaning with embeddings", "এমবেডিং দিয়ে অর্থ মেলান"),
       [("An embedding is a numerical vector that tries to capture the meaning of a piece of data. Good embeddings place similar inputs closer together.",
         "এমবেডিং হলো ডেটার অর্থ ধরার চেষ্টা করা সংখ্যার ভেক্টর। ভালো এমবেডিং কাছাকাছি অর্থের ইনপুট কাছাকাছি রাখে।"),
        ("Semantic similarity compares them by cosine similarity.",
         "সেমান্টিক সিমিলারিটি সেগুলোকে কোসাইন সিমিলারিটি দিয়ে মেলায়।")],
       [sh("root", "hot"), sh("emb", "hot", ("captures meaning", "অর্থ ধরে")), sh("cos", "hot", ("closer", "কাছাকাছি"))],
       [ln("root", "emb", "to", state="hot"), ln("emb", "cos", "to", state="hot")],
       [None, None, ("closer is more similar", "যত কাছে, তত মিল")],
       note=("warn", "Semantic similarity depends on the quality of the underlying embedding model.",
             "সেমান্টিক সিমিলারিটি নির্ভর করে এমবেডিং মডেলের মানের ওপর।")),

    st(("Miss phrasing", "অন্য বাক্য"),
       ("Exact match misses valid phrasings", "এক্সাক্ট ম্যাচ অন্য সঠিক বাক্য ধরে না"),
       [("Exact match fails whenever there is more than one valid phrasing.",
         "একাধিক সঠিক বাক্য থাকলেই এক্সাক্ট ম্যাচ ব্যর্থ হয়।"),
        ("So a valid answer in different words can be missed.",
         "তাই অন্য শব্দে লেখা সঠিক উত্তর ধরা না-ও পড়তে পারে।")],
       [sh("root", "hot", ("other words", "অন্য শব্দ")), sh("ref", "hot"), sh("lex", "warn", ("misses it", "ধরতে পারে না"))],
       [ln("root", "ref", "to", state="hot"), ln("ref", "lex", "to", state="warn")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("When you can, run generated code against tests.",
         "পারলে বানানো কোড টেস্ট দিয়ে চালান।"),
        ("Otherwise, compare with reference answers.",
         "না পারলে রেফারেন্স উত্তরের সাথে মেলান।")],
       [sh("root", "hot"), sh("tests", "hot", ("run against tests", "টেস্ট দিয়ে চালান")), sh("passk", "hot"),
        sh("ref", "hot", ("otherwise compare", "না পারলে মেলান")), sh("lex", "hot")],
       [ln("root", "tests", "to", state="hot"), ln("tests", "passk", "to", state="hot"),
        ln("root", "ref", "to", state="hot"), ln("ref", "lex", "to", state="hot")],
       [None, None, None],
       points=[("Each comparison method has a weakness: exact match misses other valid phrasings, and semantic similarity depends on the embedding model.",
                "প্রতিটি তুলনার পদ্ধতির দুর্বলতা আছে: এক্সাক্ট ম্যাচ অন্য সঠিক বাক্য ধরে না, আর সেমান্টিক সিমিলারিটি এমবেডিং মডেলের ওপর নির্ভর করে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
