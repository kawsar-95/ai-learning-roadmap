"""Inference · 02 What inference costs: GPU economics, edge devices and hosted providers: what a GPU costs to rent or buy, what running on the user's device trades away, and which hosted providers to rent from.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Rent or buy  Body: "An H100 rents for $2–$4/hr on the major clouds, ~$30k to buy." Layman's: "So if you're running millions of conversations, owning is cheaper. If you're running thousands, renting is cheaper." Start here: "H100: A top-end Nvidia GPU used to run large AI models."
  2 Requests     Body: "At a 70B model, you serve ~30 concurrent requests before latency collapses". Start here: "Concurrent requests: Requests the server handles at the same moment.", "Latency: How long a user waits for an answer."
  3 Cost         Body: "about $0.10 per 1k generated tokens fully loaded". Remember: "Fully loaded, this costs about $0.10 per 1k generated tokens."
  4 Edge         Body: "Edge inference pushes smaller models onto the user's device ... The trade-off: zero server cost, but quality and capability are limited." Start here: "Edge inference: Running small models on the user's own device, like a phone, instead of on a server."
  5 Providers    Body: "Hosted inference in 2025 is a commodity market." Table rows: Together "Open-weight catalogue, good default"; Groq "Ultra-low latency LPU hardware (Language Processing Unit, Groq's own chip)"; OpenRouter "Aggregator — one API, many providers".
  6 Pick         Body: "Pick by which model you want at what price with what SLA (service-level agreement)". Start here: "SLA: A written promise from a provider about how reliable and fast its service will be."
  7 Remember     The five "remember" points of the section.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("rent", "clock", ("Rent", "ভাড়া"), 130, 162),
    node("h100", "server", ("H100", "H100"), 380, 162),
    node("buy", "key", ("Buy", "কেনা"), 630, 162),
    node("reqs", "user", ("Concurrent requests", "একসাথে চলা রিকোয়েস্ট"), 130, 162),
    node("m70", "model", ("70B model", "৭০B মডেল"), 630, 162),
    node("small", "model", ("Smaller model", "ছোট মডেল"), 380, 162),
    node("dev", "browser", ("User's device", "ইউজারের ডিভাইস"), 130, 162),
    node("you", "user", ("Your app", "আপনার অ্যাপ"), 110, 162),
    node("tog", "service", ("Together", "Together"), 380, 75),
    node("groq", "service", ("Groq", "Groq"), 380, 162),
    node("or", "service", ("OpenRouter", "OpenRouter"), 380, 250),
    node("pick", "note", ("Model, price, SLA", "মডেল, দাম, SLA"), 650, 162),
]

METRICS = [
    ("Rent", "ভাড়া"),
    ("Buy", "কেনা"),
    ("At once", "একসাথে"),
    ("Per 1k tokens", "প্রতি ১k টোকেনে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the figures and labels are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: সংখ্যা আর লেবেলগুলো সেকশনের নিজের।",
)

RENT = ("$2–$4/hr", "ঘণ্টায় $২–$৪")
BUY = ("about $30k", "প্রায় $৩০k")
ONCE = ("about 30", "প্রায় ৩০টি")
COST = ("about $0.10", "প্রায় $০.১০")

STEPS = [
    st(("Rent or buy", "ভাড়া বা কেনা"),
       ("What an H100 costs", "একটা H100-এর খরচ"),
       [("An H100, a top-end Nvidia GPU, rents for $2–$4/hr on the major clouds and costs about $30k to buy.",
         "H100, মানে Nvidia-র একটি সেরা মানের GPU, প্রধান ক্লাউডে ঘণ্টায় $২–$৪-এ ভাড়া পাওয়া যায়, আর কিনতে প্রায় $৩০k লাগে।"),
        ("If you run millions of conversations, owning is cheaper. If you run thousands, renting is cheaper.",
         "লাখ লাখ কথোপকথন চালালে নিজে কেনা সস্তা। হাজার কয়েক চালালে ভাড়া নেওয়া সস্তা।")],
       [sh("rent", "hot", ("on the major clouds", "প্রধান ক্লাউডে")), sh("h100", "hot"), sh("buy", "hot")],
       [ln("rent", "h100", "to", state="hot"), ln("buy", "h100", "to", state="hot")],
       [RENT, BUY, None, None]),

    st(("Requests", "রিকোয়েস্ট"),
       ("How many requests at once", "একসাথে কত রিকোয়েস্ট"),
       [("Concurrent requests are the requests the server handles at the same moment.",
         "একসাথে চলা রিকোয়েস্ট হলো সার্ভার একই মুহূর্তে যত রিকোয়েস্ট সামলায়।"),
        ("With a 70B model, you can serve about 30 of them before latency collapses.",
         "৭০B মডেলে ল্যাটেন্সি ভেঙে পড়ার আগে এর প্রায় ৩০টি সামলানো যায়।")],
       [sh("reqs", "hot"), sh("h100", "hot", ("before latency collapses", "ল্যাটেন্সি ভেঙে পড়ার আগে")), sh("m70", "hot")],
       [ln("reqs", "h100", "to", state="hot"), ln("m70", "h100", "to", state="hot")],
       [None, None, ONCE, None],
       note=("info", "Latency is how long a user waits for an answer.",
             "ল্যাটেন্সি হলো উত্তরের জন্য ইউজারকে কতক্ষণ অপেক্ষা করতে হয়।")),

    st(("Cost", "খরচ"),
       ("What a token costs", "একটা টোকেনের খরচ"),
       [("Fully loaded, this costs about $0.10 per 1k generated tokens.",
         "পুরো লোডে এর খরচ প্রতি ১k জেনারেটেড টোকেনে প্রায় $০.১০।")],
       [sh("reqs", "hot"), sh("h100", "hot", ("fully loaded", "পুরো লোডে")), sh("m70", "hot")],
       [ln("reqs", "h100", "to", state="hot"), ln("m70", "h100", "to", state="hot")],
       [None, None, ONCE, COST]),

    st(("Edge", "এজ"),
       ("Edge inference: no server bill", "এজ ইনফারেন্স: সার্ভার খরচ নেই"),
       [("Edge inference runs smaller models on the user's own device, like a phone, instead of on a server.",
         "এজ ইনফারেন্স সার্ভারের বদলে ইউজারের নিজের ডিভাইসে, যেমন ফোনে, ছোট মডেল চালায়।"),
        ("The trade-off: zero server cost, but quality and capability are limited.",
         "বিনিময়ে: সার্ভার খরচ শূন্য, কিন্তু মান আর সামর্থ্য সীমিত।")],
       [sh("dev", "hot"), sh("small", "hot", ("limited", "সীমিত")), sh("h100", "dim", ("zero server cost", "সার্ভার খরচ শূন্য"), x=630, y=162)],
       [ln("small", "dev", "to", state="hot")],
       [None, None, None, None]),

    st(("Providers", "প্রোভাইডার"),
       ("Hosted providers", "হোস্টেড প্রোভাইডার"),
       [("Hosted inference in 2025 is a commodity market, and many providers offer the same models.",
         "২০২৫ সালে হোস্টেড ইনফারেন্স একটি কমোডিটি বাজার, আর অনেক প্রোভাইডার একই মডেল দেয়।"),
        ("Together is a good default, Groq runs on its own LPU chip, and OpenRouter is an aggregator: one API, many providers.",
         "Together ভালো ডিফল্ট, Groq চলে নিজের LPU চিপে, আর OpenRouter অ্যাগ্রিগেটর: একটা API, অনেক প্রোভাইডার।")],
       [sh("you", "hot"), sh("tog", "hot", ("good default", "ভালো ডিফল্ট")), sh("groq", "hot", ("LPU hardware", "LPU হার্ডওয়্যার")),
        sh("or", "hot", ("one API, many providers", "একটা API, অনেক প্রোভাইডার"))],
       [ln("you", "tog", "to", state="hot"), ln("you", "groq", "to", state="hot"), ln("you", "or", "to", state="hot")],
       [None, None, None, None]),

    st(("Pick", "বাছাই"),
       ("Pick by model, price and SLA", "মডেল, দাম আর SLA দেখে বাছুন"),
       [("Pick by which model you want, at what price, with what SLA.",
         "কোন মডেল চান, কী দামে, আর কোন SLA-তে, তা দেখে বাছুন।"),
        ("An SLA, a service-level agreement, is a written promise about how reliable and fast the service will be.",
         "SLA, মানে service-level agreement, হলো সেবা কতটা নির্ভরযোগ্য আর দ্রুত হবে তার লিখিত প্রতিশ্রুতি।")],
       [sh("tog", "dim"), sh("groq", "dim"), sh("or", "dim"), sh("pick", "hot")],
       [ln("tog", "pick", "to", state="dim"), ln("groq", "pick", "to", state="dim"), ln("or", "pick", "to", state="dim")],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Running your own model costs real money for GPUs, so it helps to know the numbers.",
         "নিজের মডেল চালাতে GPU-র পেছনে সত্যিকারের টাকা লাগে, তাই সংখ্যাগুলো জানা কাজে দেয়।")],
       [sh("rent", "hot"), sh("h100", "hot"), sh("buy", "hot")],
       [ln("rent", "h100", "to", state="hot"), ln("buy", "h100", "to", state="hot")],
       [RENT, BUY, None, None],
       points=[("An H100 rents for $2–$4/hr on the major clouds and costs about $30k to buy.",
                "H100 প্রধান ক্লাউডে ঘণ্টায় $২–$৪-এ ভাড়া পাওয়া যায়, আর কিনতে প্রায় $৩০k লাগে।"),
               ("With a 70B model, you can serve about 30 concurrent requests before latency collapses.",
                "৭০B মডেলে ল্যাটেন্সি ভেঙে পড়ার আগে প্রায় ৩০টি একসাথে চলা রিকোয়েস্ট সামলানো যায়।"),
               ("Fully loaded, this costs about $0.10 per 1k generated tokens.",
                "পুরো লোডে এর খরচ প্রতি ১k জেনারেটেড টোকেনে প্রায় $০.১০।"),
               ("Edge inference has zero server cost, but quality and capability are limited.",
                "এজ ইনফারেন্সে সার্ভার খরচ শূন্য, কিন্তু মান আর সামর্থ্য সীমিত।"),
               ("Many hosted providers offer the same models, so pick by model, price and SLA.",
                "অনেক হোস্টেড প্রোভাইডার একই মডেল দেয়, তাই মডেল, দাম আর SLA দেখে বাছুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
