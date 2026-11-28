"""LLM Fundamentals · 03 Closed vs open-weight models: who owns the brain, what each side costs, and the hybrid that mixes both.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Closed       Body, "Closed / proprietary": "Hosted behind APIs." "highest capability ceiling ... no infra to run." "vendor lock-in, ... data leaves your perimeter". Start here: "A closed model is hosted behind an API, and you cannot download it."
  2 Open-weight  Body, "Open-weight": "self-host on your hardware, ... no per-token fees, no data egress. Costs: you operate the infra (GPUs, networking, monitoring)". Start here: "An open-weight model can be downloaded and run on your own machines, but then running it is your job."
  3 Open-source  Sub: "open-source (you also have training code, data, and licence to modify and redistribute). Most \"open\" LLMs are open-weight." Start here: "Open-source: Open weights plus the training code, the data, and the right to change and share them."
  4 Open wins    Callout: "predictable cost at scale, data residency / compliance requirements, need to fine-tune on proprietary data, latency-sensitive serving where inference co-locates with state."
  5 Closed wins  Callout: "tasks where being at the very frontier matters (frontier coding agents, reasoning), small query volume makes self-hosting uneconomical, you need multimodal audio/video (Gemini)."
  6 Hybrid       "Routing: route easy queries to a local 8B, hard ones to a frontier API." Start here: "Many teams mix both: easy questions go to a small local model, hard ones to a frontier API."
  7 Remember     The four "remember" points of the section.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("you", "user", ("Your program", "আপনার প্রোগ্রাম"), 110, 162),
    node("api", "service", ("API", "API"), 380, 162),
    node("closed", "model", ("Closed model", "ক্লোজড মডেল"), 625, 162),
    node("open", "model", ("Open weights", "ওপেন ওয়েট"), 130, 162),
    node("mach", "server", ("Your machines", "আপনার মেশিন"), 630, 162),
    node("code", "file", ("Training code", "ট্রেনিং কোড"), 130, 60),
    node("data", "database", ("Data", "ডেটা"), 130, 265),
    node("lic", "key", ("Right to change and share", "বদলে বিলি করার অনুমতি"), 620, 162),
    node("osrc", "note", ("Open-source", "ওপেন-সোর্স"), 380, 162),
    node("router", "balancer", ("Routing", "রাউটিং"), 380, 162),
    node("small", "model", ("Small local model", "ছোট লোকাল মডেল"), 650, 75),
]

METRICS = [
    ("Your data", "আপনার ডেটা"),
    ("Servers", "সার্ভার"),
    ("Per-token fee", "টোকেন-প্রতি ফি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Closed", "ক্লোজড"),
       ("Closed: behind an API", "ক্লোজড: API-র পেছনে"),
       [("A closed model is hosted behind an API, and you cannot download it.",
         "ক্লোজড মডেল থাকে API-র পেছনে, আর সেটা ডাউনলোড করা যায় না।"),
        ("It has the highest capability ceiling and no infra to run, but your data leaves your network and you live with vendor lock-in.",
         "এর সক্ষমতার সীমা সবচেয়ে উঁচু আর নিজের ইনফ্রা চালাতে হয় না, কিন্তু আপনার ডেটা নেটওয়ার্কের বাইরে যায় আর ভেন্ডর লক-ইন মেনে নিতে হয়।")],
       [sh("you", "hot"), sh("api", "hot"), sh("closed", "hot", ("you cannot download it", "ডাউনলোড করা যায় না"))],
       [ln("you", "api", "to", state="hot"), ln("api", "closed", "to", state="hot")],
       [("leaves your network", "নেটওয়ার্কের বাইরে যায়"), ("none of your own", "নিজের লাগে না"), None]),

    st(("Open-weight", "ওপেন-ওয়েট"),
       ("Open-weight: you run it", "ওপেন-ওয়েট: আপনি চালান"),
       [("An open-weight model can be downloaded and run on your own machines, but then running it is your job.",
         "ওপেন-ওয়েট মডেল ডাউনলোড করে নিজের মেশিনে চালানো যায়, তবে তখন চালানোর দায়িত্বও আপনার।"),
        ("Your data stays in-house and there are no per-token fees, but you run the GPUs.",
         "ডেটা নিজের কাছে থাকে আর টোকেন-প্রতি ফি নেই, কিন্তু GPU চালাতে হয় আপনাকেই।")],
       [sh("open", "hot", ("download it", "ডাউনলোড করুন")), sh("mach", "hot", ("you run the GPUs", "GPU চালান আপনি"))],
       [ln("open", "mach", "to", state="hot")],
       [("stays in-house", "নিজের কাছে থাকে"), ("you run the GPUs", "GPU চালান আপনি"), ("none", "নেই")]),

    st(("Open-source", "ওপেন-সোর্স"),
       ("Open-source is more than open weights", "ওপেন-সোর্স মানে ওপেন ওয়েটের চেয়ে বেশি"),
       [("Open-source is open weights plus the training code, the data, and the right to change and share them.",
         "ওপেন-সোর্স মানে ওপেন ওয়েটের সাথে ট্রেনিং কোড, ডেটা আর সেগুলো বদলে আবার বিলি করার অনুমতিও।"),
        ("Most open LLMs are open-weight, not open-source.",
         "বেশিরভাগ ওপেন LLM আসলে ওপেন-ওয়েট, ওপেন-সোর্স নয়।")],
       [sh("open", "hot"), sh("code", "hot"), sh("data", "hot"), sh("lic", "hot"), sh("osrc", "hot")],
       [ln("open", "osrc", "to", state="hot"), ln("code", "osrc", "to", state="hot"),
        ln("data", "osrc", "to", state="hot"), ln("lic", "osrc", "to", state="hot")],
       [None, None, None]),

    st(("Open wins", "ওপেন জেতে"),
       ("When open-weight wins", "যখন ওপেন-ওয়েট জেতে"),
       [("These are the cases where open-weight wins.",
         "এই ক্ষেত্রগুলোতে ওপেন-ওয়েট জেতে।")],
       [sh("open", "hot"), sh("mach", "hot")],
       [ln("open", "mach", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Predictable cost at scale", "স্কেলে খরচ আগে থেকে বোঝা যায়"),
                ("+", "Data residency and compliance requirements", "ডেটা কোথায় থাকবে আর কমপ্লায়েন্সের শর্ত"),
                ("+", "You need to fine-tune on proprietary data", "নিজস্ব ডেটায় ফাইন-টিউন করা দরকার"),
                ("+", "Latency-sensitive serving, where inference sits next to the state", "ল্যাটেন্সি-সংবেদনশীল সার্ভিং, যেখানে ইনফারেন্স স্টেটের পাশেই চলে")]),

    st(("Closed wins", "ক্লোজড জেতে"),
       ("When closed wins", "যখন ক্লোজড জেতে"),
       [("These are the cases where closed wins.",
         "এই ক্ষেত্রগুলোতে ক্লোজড জেতে।")],
       [sh("you", "hot"), sh("api", "hot"), sh("closed", "hot")],
       [ln("you", "api", "to", state="hot"), ln("api", "closed", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Tasks where being at the very frontier matters, like frontier coding agents and reasoning",
                 "যেসব কাজে একদম ফ্রন্টিয়ারে থাকা জরুরি, যেমন ফ্রন্টিয়ার কোডিং এজেন্ট আর রিজনিং"),
                ("+", "A small query volume makes self-hosting uneconomical",
                 "কোয়েরির পরিমাণ কম হলে নিজে হোস্ট করা পোষায় না"),
                ("+", "You need multimodal audio or video, as in Gemini",
                 "মাল্টিমোডাল অডিও বা ভিডিও দরকার, যেমন Gemini-তে")]),

    st(("Hybrid", "হাইব্রিড"),
       ("Mix both with routing", "রাউটিং দিয়ে দুটোই মেলান"),
       [("Routing sends easy questions to a small, cheap model and hard ones to a big one.",
         "রাউটিং সহজ প্রশ্ন ছোট, সস্তা মডেলে আর কঠিন প্রশ্ন বড় মডেলে পাঠায়।"),
        ("Many teams do this: easy questions go to a small local model, hard ones to a frontier API.",
         "অনেক টিম এটাই করে: সহজ প্রশ্ন যায় লোকাল ছোট মডেলে, কঠিন প্রশ্ন ফ্রন্টিয়ার API-তে।")],
       [sh("you", "hot"), sh("router", "hot"), sh("small", "hot", ("easy questions", "সহজ প্রশ্ন")),
        sh("api", "hot", ("hard questions", "কঠিন প্রশ্ন"), x=650, y=250)],
       [ln("you", "router", "to", state="hot"), ln("router", "small", "to", state="hot"), ln("router", "api", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Most open LLMs are open-weight, not open-source.",
         "বেশিরভাগ ওপেন LLM আসলে ওপেন-ওয়েট, ওপেন-সোর্স নয়।")],
       [sh("you", "hot"), sh("router", "hot"), sh("small", "hot"), sh("api", "hot", x=650, y=250)],
       [ln("you", "router", "to", state="hot"), ln("router", "small", "to", state="hot"), ln("router", "api", "to", state="hot")],
       [None, None, None],
       points=[("Most open LLMs are open-weight, not open-source.",
                "বেশিরভাগ ওপেন LLM আসলে ওপেন-ওয়েট, ওপেন-সোর্স নয়।"),
               ("Closed models are the most capable and need no servers of your own, but your data leaves your network.",
                "ক্লোজড মডেল সবচেয়ে সক্ষম আর নিজের সার্ভার লাগে না, কিন্তু আপনার ডেটা আপনার নেটওয়ার্কের বাইরে যায়।"),
               ("Open-weight models keep your data in-house and have no per-token fees, but you run the GPUs.",
                "ওপেন-ওয়েট মডেলে ডেটা নিজের কাছে থাকে আর টোকেন-প্রতি ফি নেই, কিন্তু GPU চালাতে হয় আপনাকেই।"),
               ("Many teams mix both: easy questions go to a small local model, hard ones to a frontier API.",
                "অনেক টিম দুটোই মেলায়: সহজ প্রশ্ন যায় লোকাল ছোট মডেলে, কঠিন প্রশ্ন ফ্রন্টিয়ার API-তে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
