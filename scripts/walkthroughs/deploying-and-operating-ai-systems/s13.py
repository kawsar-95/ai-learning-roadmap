"""Deploying and Operating AI Systems · 13 System design and data infrastructure: the queue, cache, limit and retry tools that keep a slow, costly model call from breaking an ordinary system.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Slow call  Body: "An AI feature is a slow, costly call inside an ordinary system, so ordinary tools help."
  2 Queue      Table: "A model call takes ten seconds and the web request cannot wait" / "The request returns a job id. Workers call the model and store the result." Remember: "Send slow model calls to a queue."
  3 Cache      Table: "The same question arrives again and again" / "Return a stored answer. A semantic cache also matches similar questions."
  4 Limits     Table: "Too many requests at once" / "Protect the model's quota and keep the service up." Glossary: "Rate limiting and backpressure".
  5 Retries    "Set a timeout on every call. A call without one can hold a worker forever. Retry with backoff, and make the operation idempotent ... send an idempotency key with the request."
  6 State      "Prefer scaling out (more copies behind a load balancer) to one bigger machine, and keep state in a database or a cache, not inside the process."
  7 Hashing    Info: "Consistent hashing spreads cache keys over many nodes, so that adding a node moves only a small share of the keys."
  8 Remember   The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("Request", "রিকোয়েস্ট"), 100, 160),
    node("bal", "balancer", ("Rate limit", "রেট লিমিট"), 295, 160),
    node("cache", "cache", ("Cache", "ক্যাশ"), 495, 60),
    node("queue", "queue", ("Queue", "কিউ"), 495, 160),
    node("workers", "service", ("Workers", "ওয়ার্কার"), 665, 160),
    node("db", "database", ("Database", "ডেটাবেস"), 665, 270),
]

METRICS = [
    ("Request", "রিকোয়েস্ট"),
    ("Same question", "একই প্রশ্ন"),
    ("Too many", "অনেক বেশি"),
    ("Retry", "রিট্রাই"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Slow call", "ধীর কল"),
       ("A slow, costly call", "ধীর আর দামি কল"),
       [("An AI feature is a slow, costly call inside an ordinary system.",
         "AI ফিচার একটা সাধারণ সিস্টেমের ভেতরে ধীর আর দামি কল।"),
        ("So ordinary tools help: queues, caches, limits and safe retries.",
         "তাই সাধারণ টুলই কাজে লাগে: কিউ, ক্যাশ, সীমা আর নিরাপদ রিট্রাই।")],
       [sh("user", "hot"), sh("workers", "warn", ("slow, costly", "ধীর, দামি"))],
       [ln("user", "workers", "to", state="warn")],
       [None, None, None, None]),

    st(("Queue", "কিউ"),
       ("Send slow calls to a queue", "ধীর কল কিউতে পাঠান"),
       [("When a model call takes ten seconds and the web request cannot wait, use a queue and workers. The request returns a job id.",
         "মডেল কল দশ সেকেন্ড নিলে আর ওয়েব রিকোয়েস্ট অপেক্ষা করতে না পারলে কিউ আর ওয়ার্কার ব্যবহার করুন। রিকোয়েস্ট একটা job id ফেরত দেয়।"),
        ("Workers call the model and store the result.",
         "ওয়ার্কার মডেল কল করে ফল জমা রাখে।")],
       [sh("user", "hot", ("gets a job id", "job id পায়")), sh("queue", "hot"), sh("workers", "hot", ("call the model", "মডেল কল করে")), sh("db", "hot", ("result stored", "ফল জমা"))],
       [ln("user", "queue", "to", state="hot"), ln("queue", "workers", "to", state="hot"), ln("workers", "db", "to", state="hot")],
       [("a job id", "একটা job id"), None, None, None]),

    st(("Cache", "ক্যাশ"),
       ("A cache returns a stored answer", "ক্যাশ জমানো উত্তর ফেরত দেয়"),
       [("When the same question arrives again and again, a cache such as Redis returns a stored answer.",
         "একই প্রশ্ন বারবার এলে Redis-এর মতো ক্যাশ জমানো উত্তর ফেরত দেয়।"),
        ("A semantic cache also matches similar questions.",
         "সেমান্টিক ক্যাশ মিল থাকা প্রশ্নও মেলায়।")],
       [sh("user", "hot", ("same question", "একই প্রশ্ন")), sh("cache", "hot", ("stored answer", "জমানো উত্তর"))],
       [ln("user", "cache", "to", state="hot")],
       [None, ("stored answer", "জমানো উত্তর"), None, None]),

    st(("Limits", "সীমা"),
       ("Rate limiting and backpressure", "রেট লিমিটিং আর ব্যাকপ্রেশার"),
       [("Rate limiting caps how many requests are allowed. Backpressure slows or refuses new work when the system is full.",
         "রেট লিমিটিং কত রিকোয়েস্ট চলবে তার সীমা বাঁধে। সিস্টেম ভরে গেলে ব্যাকপ্রেশার নতুন কাজ ধীর করে বা ফিরিয়ে দেয়।"),
        ("This protects the model's quota and keeps the service up.",
         "এতে মডেলের কোটা সুরক্ষিত থাকে আর সার্ভিস চালু থাকে।")],
       [sh("user", "hot"), sh("bal", "warn", ("caps, slows, refuses", "সীমা, ধীর, ফিরিয়ে দেয়")), sh("queue", "hot")],
       [ln("user", "bal", "to", state="warn"), ln("bal", "queue", "to", state="hot")],
       [None, None, ("slow or refuse", "ধীর বা ফিরিয়ে দেয়"), None]),

    st(("Retries", "রিট্রাই"),
       ("Timeouts, retries and idempotency", "টাইমআউট, রিট্রাই আর আইডেমপোটেন্সি"),
       [("Set a timeout on every call. A call without one can hold a worker forever.",
         "প্রতিটি কলে timeout দিন। timeout ছাড়া একটা কল ওয়ার্কারকে চিরকাল আটকে রাখতে পারে।"),
        ("Retry with backoff: wait a little longer before each retry. Make the operation idempotent, so running it twice has the same effect as running it once.",
         "backoff দিয়ে রিট্রাই করুন: প্রতিবার রিট্রাইয়ের আগে একটু বেশি অপেক্ষা করুন। কাজ আইডেমপোটেন্ট বানান, যাতে দুবার চললেও একবার চলার মতোই ফল হয়।")],
       [sh("queue", "hot"), sh("workers", "hot", ("timeout", "timeout"))],
       [ln("workers", "queue", "back", state="hot")],
       [None, None, None, ("wait a little longer", "একটু বেশি অপেক্ষা")],
       note=("tip", "A common way is to send an idempotency key with the request.",
             "একটা প্রচলিত উপায় হলো রিকোয়েস্টের সাথে idempotency key পাঠানো।")),

    st(("State", "স্টেট"),
       ("Scale out, and keep state outside", "স্কেল আউট করুন, state বাইরে রাখুন"),
       [("Prefer scaling out, which means more copies behind a load balancer, to one bigger machine.",
         "একটা বড় মেশিনের বদলে স্কেল আউট বেছে নিন, মানে লোড ব্যালান্সারের পেছনে আরও কপি।"),
        ("Keep state in a database or a cache, not inside the process.",
         "state রাখুন ডেটাবেস বা ক্যাশে, প্রসেসের ভেতরে নয়।")],
       [sh("bal", "hot", ("load balancer", "লোড ব্যালান্সার")), sh("workers", "hot", ("more copies", "আরও কপি")), sh("db", "hot", ("state here", "state এখানে")), sh("cache", "hot", ("or here", "বা এখানে"))],
       [ln("bal", "workers", "to", state="hot"), ln("workers", "db", "to", state="hot")],
       [None, None, None, None]),

    st(("Hashing", "হ্যাশিং"),
       ("Consistent hashing", "কনসিস্টেন্ট হ্যাশিং"),
       [("Consistent hashing spreads cache keys over many nodes, so that adding a node moves only a small share of the keys.",
         "কনসিস্টেন্ট হ্যাশিং ক্যাশ কী অনেক নোডে ছড়িয়ে দেয়, যাতে নতুন নোড যোগ করলে অল্প কী-ই সরে।"),
        ("It is why a cache cluster can grow without emptying itself.",
         "এ কারণেই ক্যাশ ক্লাস্টার নিজেকে খালি না করেই বড় হতে পারে।")],
       [sh("cache", "hot", ("keys over many nodes", "অনেক নোডে কী")), sh("workers", "dim")],
       [ln("workers", "cache", "to", state="dim")],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Four rules cover the section.", "চারটা নিয়মে পুরো সেকশন।")],
       [sh("queue", "hot"), sh("cache", "hot"), sh("workers", "hot"), sh("db", "hot")],
       [],
       [("a job id", "একটা job id"), ("stored answer", "জমানো উত্তর"), None, ("wait a little longer", "একটু বেশি অপেক্ষা")],
       points=[("Send slow model calls to a queue. Workers call the model and store the result.", "ধীর মডেল কল কিউতে পাঠান। ওয়ার্কার মডেল কল করে ফল জমা রাখে।"),
               ("A cache returns a stored answer when the same question arrives again.", "একই প্রশ্ন আবার এলে ক্যাশ জমানো উত্তর ফেরত দেয়।"),
               ("Set a timeout on every call, and retry with backoff: wait a little longer before each retry.", "প্রতিটি কলে timeout দিন, আর backoff দিয়ে রিট্রাই করুন: প্রতিবার রিট্রাইয়ের আগে একটু বেশি অপেক্ষা করুন।"),
               ("Make operations idempotent, and keep state in a database or cache, not inside the process.", "কাজ আইডেমপোটেন্ট বানান, আর state রাখুন ডেটাবেস বা ক্যাশে, প্রসেসের ভেতরে নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
