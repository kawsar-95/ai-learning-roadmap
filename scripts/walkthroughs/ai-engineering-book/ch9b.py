"""Part 15 · ch9b Inference Optimization: model-level and service-level techniques.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Slow      Remember: "Decode is slow because it goes one token at a time." Idea: "Inference optimization makes a trained model faster and cheaper to run."
  2 Draft     Speculative decoding: "A small, fast draft model proposes several tokens."
  3 Verify    "The large model checks them all in one pass and keeps the longest correct run." Remember: "Speculative decoding checks guesses in parallel; parallel decoding breaks that chain."
  4 KV cache  "A store of numbers the model computed for earlier tokens, so they are not redone each step. It can use a lot of memory." Remember: "attention redesigns and smarter cache management help."
  5 Batching  Continuous batching: "Requests are grouped together. Each response returns the moment it finishes and a new request takes its place, so no capacity is wasted."
  6 Prompt    Prompt caching: "Text shared across requests, like a system prompt or a long document, is processed once and reused. This cuts latency and cost."
  7 Split     Tensor parallelism: "Splitting single operations, such as a matrix multiply, across several devices so a large model fits and runs faster."
  8 Remember  "Service-level techniques manage compute and memory across requests without touching output quality. Model-level changes can shift quality." "Judge an inference provider's cost and speed together with its output quality, not alone."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("Request", "রিকোয়েস্ট"), 80, 162),
    node("draft", "model", ("Draft model", "draft মডেল"), 290, 70),
    node("large", "model", ("Large model", "বড় মডেল"), 460, 162),
    node("out", "file", ("Answer", "উত্তর"), 680, 162),
    node("kv", "cache", ("KV cache", "KV cache"), 460, 262),
    node("queue", "queue", ("Batch", "ব্যাচ"), 250, 162),
    node("pc", "cache", ("Prompt cache", "প্রম্পট ক্যাশ"), 290, 262),
    node("da", "server", ("Device", "ডিভাইস"), 670, 70),
    node("db", "server", ("Device", "ডিভাইস"), 670, 262),
    node("qual", "chart", ("Output quality", "আউটপুট কোয়ালিটি"), 650, 262),
]

METRICS = [
    ("Memory", "মেমোরি"),
    ("Output quality", "আউটপুট কোয়ালিটি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Slow", "ধীর"),
       ("Decode goes one token at a time", "ডিকোড একবারে একটি টোকেন"),
       [("Inference optimization makes a trained model faster and cheaper to run.",
         "ইনফারেন্স অপ্টিমাইজেশন ট্রেইন করা মডেলকে দ্রুত আর সস্তা করে চালায়।"),
        ("Decode is slow because it goes one token at a time.",
         "ডিকোড ধীর, কারণ এটা একবারে একটি টোকেন করে চলে।")],
       [sh("user", "hot"), sh("large", "hot", ("one token at a time", "একবারে একটি টোকেন")), sh("out", "hot")],
       [ln("user", "large", "to", state="hot"), ln("large", "out", "to", state="hot")],
       [None, None]),

    st(("Draft", "ড্রাফট"),
       ("A small model drafts guesses", "ছোট মডেল অনুমান লেখে"),
       [("In speculative decoding, a small, fast draft model proposes several tokens.",
         "স্পেকুলেটিভ ডিকোডিংয়ে একটি ছোট, দ্রুত draft মডেল কয়েকটি টোকেন প্রস্তাব করে।")],
       [sh("user", "dim"), sh("draft", "hot", ("proposes several tokens", "কয়েকটি টোকেন প্রস্তাব করে")), sh("large", "dim")],
       [ln("user", "draft", "to", state="hot"), ln("draft", "large", "to", state="hot")],
       [None, None]),

    st(("Verify", "যাচাই"),
       ("The large model checks in one pass", "বড় মডেল এক পাসে যাচাই করে"),
       [("The large model checks them all in one pass and keeps the longest correct run.",
         "বড় মডেল এক পাসে সব যাচাই করে সবচেয়ে লম্বা সঠিক অংশ রাখে।"),
        ("Speculative decoding checks guesses in parallel; parallel decoding breaks that chain.",
         "স্পেকুলেটিভ ডিকোডিং অনুমানগুলো একসাথে যাচাই করে; প্যারালাল ডিকোডিং সেই শিকলটাই ভাঙে।")],
       [sh("draft", "dim"), sh("large", "hot", ("checks them all in one pass", "এক পাসে সব যাচাই")), sh("out", "hot")],
       [ln("draft", "large", "to", state="dim"), ln("large", "out", "to", state="hot")],
       [None, None]),

    st(("KV cache", "KV cache"),
       ("The KV cache can fill memory", "KV cache মেমোরি ভরে দিতে পারে"),
       [("The KV cache is a store of numbers the model computed for earlier tokens, so they are not redone each step.",
         "KV cache হলো আগের টোকেনগুলোর জন্য মডেলের হিসাব করা সংখ্যার ভান্ডার, যাতে প্রতি ধাপে আবার হিসাব করতে না হয়।"),
        ("It can use a lot of memory, so attention redesigns and smarter cache management help.",
         "এটা অনেক মেমোরি নিতে পারে, তাই attention-এর নতুন নকশা আর ভালো cache ম্যানেজমেন্ট কাজে আসে।")],
       [sh("large", "hot"), sh("kv", "warn", ("a lot of memory", "অনেক মেমোরি"))],
       [ln("large", "kv", "to", state="warn")],
       [("a lot", "অনেক"), None]),

    st(("Batching", "ব্যাচিং"),
       ("Continuous batching wastes nothing", "কন্টিনিউয়াস ব্যাচিংয়ে কিছু নষ্ট হয় না"),
       [("Requests are grouped together. Each response returns the moment it finishes and a new request takes its place.",
         "রিকোয়েস্টগুলো একসাথে করা হয়। একটির উত্তর শেষ হলেই সেটা ফেরত যায় আর নতুন রিকোয়েস্ট জায়গা নেয়।"),
        ("So no capacity is wasted.", "তাই ক্ষমতা নষ্ট হয় না।")],
       [sh("user", "hot"), sh("queue", "hot"), sh("large", "hot"), sh("out", "hot")],
       [ln("user", "queue", "to", state="hot"), ln("queue", "large", "to", state="hot"), ln("large", "out", "to", state="hot")],
       [None, None]),

    st(("Prompt cache", "প্রম্পট ক্যাশ"),
       ("Shared text is processed once", "এক থাকা লেখা একবারই প্রসেস হয়"),
       [("Text shared across requests, like a system prompt or a long document, is processed once and reused.",
         "একাধিক রিকোয়েস্টে এক থাকা লেখা, যেমন system prompt বা লম্বা ডকুমেন্ট, একবার প্রসেস করে আবার ব্যবহার করা হয়।"),
        ("This cuts latency and cost.", "এতে latency আর খরচ কমে।")],
       [sh("user", "hot"), sh("pc", "hot", ("processed once, reused", "একবার প্রসেস, আবার ব্যবহার")), sh("large", "hot")],
       [ln("user", "pc", "to", state="hot"), ln("pc", "large", "to", state="hot")],
       [None, None]),

    st(("Split", "ভাগ"),
       ("Tensor parallelism splits operations", "টেনসর প্যারালেলিজম অপারেশন ভাগ করে"),
       [("Tensor parallelism splits single operations, such as a matrix multiply, across several devices.",
         "টেনসর প্যারালেলিজম ম্যাট্রিক্স গুণের মতো একেকটি অপারেশন কয়েকটি ডিভাইসে ভাগ করে।"),
        ("So a large model fits and runs faster.", "যাতে বড় মডেল ধরে আর দ্রুত চলে।")],
       [sh("large", "hot", ("one operation, split", "একটি অপারেশন, ভাগ করা")), sh("da", "hot"), sh("db", "hot")],
       [ln("large", "da", "to", state="hot"), ln("large", "db", "to", state="hot")],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("Judge cost and speed with quality", "খরচ আর গতি কোয়ালিটির সাথে বিচার করুন"),
       [("Service-level techniques manage compute and memory across requests without touching output quality. Model-level changes can shift quality.",
         "সার্ভিস লেভেলের কৌশল আউটপুট কোয়ালিটি না ছুঁয়ে কম্পিউট আর মেমোরি সামলায়। মডেল লেভেলের পরিবর্তনে কোয়ালিটি বদলাতে পারে।"),
        ("Judge an inference provider's cost and speed together with its output quality, not alone.",
         "কোনো inference provider-এর খরচ আর গতি আউটপুট কোয়ালিটির সাথে মিলিয়ে বিচার করুন, আলাদাভাবে নয়।")],
       [sh("queue", "hot"), sh("large", "warn", ("model level", "মডেল লেভেল")), sh("qual", "hot")],
       [ln("queue", "large", "to", state="hot"), ln("large", "qual", "to", state="warn")],
       [None, ("can shift", "বদলাতে পারে")],
       note=("warn", "Comparing cost and speed without checking output quality can be misleading.",
             "আউটপুট কোয়ালিটি না দেখে শুধু খরচ আর গতি তুলনা করলে বিভ্রান্তি হতে পারে।")),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
