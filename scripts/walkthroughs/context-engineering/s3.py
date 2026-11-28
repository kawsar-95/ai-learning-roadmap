"""Part 4 · 03 Prompt caching strategies: a stable prefix is reused, so only the new tail is paid for in full.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Resend    Layman's voice: "they send the full system prompt + tool descriptions + retrieved context + the user's question every single call. Even if nothing changed from the last call." and "You're paying the AI company to re-read the same ... words over and over."
              Bangla voice: "ক্যাশ ছাড়া ৬৪K টোকেনের পুরো দাম লাগে".
  2 Prefix    Start here: Prefix ("The first part of a prompt. If it is identical across calls, the provider can reuse its earlier work."); "Prompt caching can cut most of the input cost (cached reads are 0.1× on Anthropic) for apps with stable instructions and long fetched documents, but only if that start stays exactly the same."
  3 Layout    Remember: "Put stable parts first (system prompt, tools, reused documents) and changing parts, like the user message, last."; layman's voice: "Cache the start, send the end fresh each time."
  4 Breakpoint Start here: Cache breakpoint ("A marker in the prompt. Everything before it is cached; everything after is rebuilt each call. Anthropic allows up to 4.").
  5 Hit       Start here: Cache hit ("A call whose start matches the cache, so the saved work is reused. In Anthropic's API, response.usage.cache_read_input_tokens above 0 means a hit."); TTL ("For Anthropic it is 5 minutes by default (1 hour is optional at a higher write price), and it refreshes on a hit.").
  6 Math      Body, the cost math: "a 60K-token system + tools prefix and a 4K-token user message ... No cache: 64K input tokens ... With cache: 60K cached (≈10× cheaper) + 4K uncached ... ~85% on input costs for the steady state".
  7 Break     Start here: Cache invalidation ("The cache breaking because of a change. One new character in the cached part breaks the cache for everything after it.");
              callout: "Change a version number, fix a typo, even add a dynamic timestamp — cache miss."
  8 Guard     Remember: "keep the prefix byte-identical and free of timestamps"; "Keep a fingerprint (hash) of the system prompt in your automatic test pipeline (CI); alert if it changes."; layman's voice: "Put anything dynamic ... AFTER the cache breakpoint."
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("system", "note", ("System prompt", "সিস্টেম প্রম্পট"), 95, 75),
    node("tools", "tool", ("Tools", "টুল"), 285, 75),
    node("docs", "storage", ("Documents", "ডকুমেন্ট"), 480, 75),
    node("msg", "user", ("User message", "ইউজারের বার্তা"), 655, 75),
    node("ci", "shield", ("CI check", "CI চেক"), 95, 250),
    node("cache", "cache", ("Cache", "ক্যাশ"), 285, 250),
    node("model", "model", ("Model", "মডেল"), 500, 250),
    node("bill", "chart", ("Input bill", "ইনপুট বিল"), 675, 250),
]

METRICS = [
    ("Prefix", "প্রিফিক্স"),
    ("Message", "বার্তা"),
    ("Input saving", "ইনপুটে সাশ্রয়"),
    ("Cache", "ক্যাশ"),
]

CAPTION = (
    "Example: an agent with a 60K-token prefix and a 4K-token user message.",
    "উদাহরণ: ৬০K টোকেনের প্রিফিক্স আর ৪K টোকেনের ইউজার মেসেজ থাকা একটি এজেন্ট।",
)

HIT = ("hit", "হিট")
MISS = ("miss", "মিস")
K60 = ("60K tokens", "৬০K টোকেন")
K4 = ("4K tokens", "৪K টোকেন")
BLOCKS = ["system", "tools", "docs", "msg"]


def to_model(state=None, only=None):
    return [ln(b, "model", "to", state=state) for b in BLOCKS if only is None or b in only]


STEPS = [
    st(("Resend", "আবার পাঠানো"),
       ("The same text, sent again and again", "একই লেখা, বারবার পাঠানো"),
       [("Most apps send the full system prompt, the tool descriptions, the retrieved context and the user's question on every call, even if nothing changed since the last call.",
         "বেশিরভাগ অ্যাপ প্রতিবার কলে একই সিস্টেম প্রম্পট, টুলের বর্ণনা, রিট্রিভ করা ডকুমেন্ট আর ইউজারের প্রশ্ন বারবার পাঠায়, আগের কলের পর কিছু না বদলালেও।"),
        ("Without a cache you pay full price for all of it, 64K input tokens in the example, to read the same text over and over.",
         "ক্যাশ ছাড়া এ সবের পুরো দাম দিতে হয়, উদাহরণে ৬৪K ইনপুট টোকেনের, একই লেখা বারবার পড়ানোর জন্য।")],
       [sh("system", "hot"), sh("tools", "hot"), sh("docs", "hot"), sh("msg", "hot"), sh("model", "hot"), sh("bill", "warn", ("full price", "পুরো দাম"))],
       to_model("hot") + [ln("model", "bill", "to", state="warn")],
       [None, None, None, None]),

    st(("Prefix", "প্রিফিক্স"),
       ("The unchanged start is the prefix", "না-বদলানো শুরুর অংশই প্রিফিক্স"),
       [("The prefix is the first part of a prompt. If it is identical across calls, the provider can reuse its earlier work.",
         "প্রিফিক্স হলো প্রম্পটের শুরুর অংশ। কলের পর কলে হুবহু এক থাকলে প্রোভাইডার আগের কাজ আবার ব্যবহার করতে পারে।"),
        ("Prompt caching can cut most of the input cost (cached reads are 0.1× on Anthropic) for apps with stable instructions and long fetched documents, but only if that start stays exactly the same.",
         "স্থির নির্দেশ আর খুঁজে আনা লম্বা ডকুমেন্ট আছে এমন অ্যাপে প্রম্পট ক্যাশিং ইনপুট খরচের বেশিরভাগ কমাতে পারে (Anthropic-এ ক্যাশ রিড ০.১×), তবে শুরুর অংশ হুবহু একই থাকতে হবে।")],
       [sh("system", "hot", ("prefix", "প্রিফিক্স")), sh("tools", "hot", ("prefix", "প্রিফিক্স")), sh("docs", "hot", ("prefix", "প্রিফিক্স")), sh("msg", "dim"), sh("model", "hot")],
       to_model("hot", ["system", "tools", "docs"]) + to_model("dim", ["msg"]),
       [None, None, None, None],
       changes=[("+", "The start of the prompt can be reused", "প্রম্পটের শুরুর অংশ আবার ব্যবহার করা যায়")]),

    st(("Layout", "সাজানো"),
       ("Stable parts first, changing parts last", "স্থির অংশ আগে, বদলানো অংশ শেষে"),
       [("Put the stable parts first: the system prompt, the tools and the documents you reuse. Put the changing parts, like the user message, last.",
         "স্থির অংশ আগে রাখুন (সিস্টেম প্রম্পট, টুল, বারবার ব্যবহৃত ডকুমেন্ট), বদলানো অংশ, যেমন ইউজারের বার্তা, শেষে।"),
        ("Then the start stays identical, and only the end is new on each call.",
         "তাহলে শুরুর অংশ একই থাকে, আর প্রতি কলে শুধু শেষটা নতুন হয়।")],
       [sh("system", "hot", ("stable", "স্থির")), sh("tools", "hot", ("stable", "স্থির")), sh("docs", "hot", ("stable", "স্থির")), sh("msg", "hot", ("changes", "বদলায়"))],
       [ln("system", "tools", "to", state="hot"), ln("tools", "docs", "to", state="hot"), ln("docs", "msg", "to", state="hot")],
       [None, None, None, None]),

    st(("Breakpoint", "ব্রেকপয়েন্ট"),
       ("A breakpoint marks what is cached", "ব্রেকপয়েন্ট বলে কী ক্যাশ হবে"),
       [("A cache breakpoint is a marker in the prompt. Everything before it is cached, and everything after it is rebuilt on each call.",
         "ক্যাশ ব্রেকপয়েন্ট হলো প্রম্পটের একটি চিহ্ন। এর আগের অংশ ক্যাশ হয়, পরের অংশ প্রতি কলে নতুন করে বানানো হয়।"),
        ("Anthropic allows up to 4 breakpoints in a prompt.",
         "Anthropic-এ একটি প্রম্পটে সর্বোচ্চ ৪টি ব্রেকপয়েন্ট।")],
       [sh("system", "hot"), sh("tools", "hot"), sh("docs", "hot"), sh("msg", "hot", ("rebuilt each call", "প্রতি কলে নতুন")),
        sh("cache", "hot", ("breakpoint", "ব্রেকপয়েন্ট")), sh("model", "hot")],
       [ln("system", "cache", "to", state="hot"), ln("tools", "cache", "to", state="hot"), ln("docs", "cache", "to", state="hot"),
        ln("cache", "model", "to", state="hot"), ln("msg", "model", "to", state="hot")],
       [None, None, None, None]),

    st(("Hit", "হিট"),
       ("The next call hits the cache", "পরের কল ক্যাশ ধরে ফেলে"),
       [("A cache hit is a call whose start matches the cache, so the saved work is reused. In Anthropic's API, <code>response.usage.cache_read_input_tokens</code> above 0 means a hit.",
         "ক্যাশ হিট হলো যে কলে প্রম্পটের শুরু ক্যাশের সাথে মেলে, তাই আগের কাজ আবার ব্যবহার হয়। Anthropic-এর API-তে <code>response.usage.cache_read_input_tokens</code> ০-এর বেশি হলে হিট।"),
        ("The cache entry lives for a TTL, a time to live. For Anthropic it is 5 minutes by default (1 hour is optional at a higher write price), and a hit starts the time again.",
         "ক্যাশ কতক্ষণ থাকে তা TTL, মানে time to live। Anthropic-এ ডিফল্ট ৫ মিনিট (বেশি লেখার দামে ঐচ্ছিকভাবে ১ ঘণ্টা), আর হিট হলে সময় নতুন করে শুরু হয়।")],
       [sh("cache", "hot", HIT), sh("msg", "hot"), sh("model", "hot", ("reads the cache", "ক্যাশ থেকে পড়ে"))],
       [ln("cache", "model", "to", state="hot"), ln("msg", "model", "to", state="hot")],
       [None, None, None, HIT],
       changes=[("+", "The saved work is reused", "আগের কাজ আবার ব্যবহার হলো")]),

    st(("Math", "হিসাব"),
       ("The savings, worked out", "সাশ্রয়ের হিসাব"),
       [("Take a 60K-token prefix and a 4K-token user message. With no cache, you pay full price for 64K input tokens.",
         "৬০K টোকেনের প্রিফিক্স আর ৪K টোকেনের ইউজার মেসেজ ধরুন। ক্যাশ ছাড়া ৬৪K টোকেনের পুরো দাম লাগে।"),
        ("With a cache, the 60K are about 10× cheaper and the 4K cost the usual price. In the steady state that saves about 85% on input.",
         "ক্যাশ থাকলে ৬০K প্রায় ১০ গুণ সস্তা, আর ৪K সাধারণ দামে। স্টেডি স্টেটে ইনপুট খরচে প্রায় ৮৫% সাশ্রয় হয়।")],
       [sh("cache", "hot", ("60K, ≈10× cheaper", "৬০K, ≈১০ গুণ সস্তা")), sh("msg", "hot", ("4K, usual price", "৪K, সাধারণ দাম")), sh("model", "hot"),
        sh("bill", "hot", ("~85% less", "~৮৫% কম"))],
       [ln("cache", "model", "to", state="hot"), ln("msg", "model", "to", state="hot"), ln("model", "bill", "to", state="hot")],
       [K60, K4, "~85%", HIT],
       changes=[("-", "64K tokens at full price become 60K cached plus 4K uncached", "৬৪K টোকেনের পুরো দাম বদলে হলো ৬০K ক্যাশ করা আর ৪K ক্যাশ ছাড়া")]),

    st(("Break", "ভাঙা"),
       ("One changed character breaks the cache", "একটি অক্ষর বদলালেই ক্যাশ ভাঙে"),
       [("Cache invalidation is the cache breaking because of a change. One new character in the cached part breaks the cache for everything after it.",
         "ক্যাশ ইনভ্যালিডেশন হলো বদলের কারণে ক্যাশ নষ্ট হওয়া। ক্যাশ করা অংশে একটি অক্ষর বদলালেও তার পরের সবকিছুর ক্যাশ বাতিল হয়।"),
        ("A fixed typo, a new version number or a timestamp is enough: a cache miss, at full price.",
         "টাইপো ঠিক করা, ভার্সন নম্বর বা টাইমস্ট্যাম্পই যথেষ্ট: ক্যাশ মিস, পুরো দামে।")],
       [sh("system", "warn", ("one character", "একটি অক্ষর")), sh("tools", "dim"), sh("docs", "dim"), sh("cache", "warn", ("broken", "ভাঙা")),
        sh("model", "hot"), sh("bill", "warn", ("full price", "পুরো দাম"))],
       [ln("system", "cache", "to", state="warn"), ln("tools", "cache", "to", state="dim"), ln("docs", "cache", "to", state="dim"),
        ln("cache", "model", "to", state="warn"), ln("model", "bill", "to", state="warn")],
       [None, None, None, MISS],
       note=("warn",
             "Even one new character in the cached part breaks the cache for everything after it.",
             "ক্যাশ করা অংশে একটি নতুন অক্ষর এলেও তার পরের সবকিছুর ক্যাশ ভাঙে।")),

    st(("Guard", "পাহারা"),
       ("Keep the prefix byte-identical", "প্রিফিক্স রাখুন বাইট-টু-বাইট হুবহু"),
       [("Keep the prefix byte-identical and free of timestamps. Put anything dynamic after the cache breakpoint.",
         "প্রিফিক্স বাইট-টু-বাইট হুবহু আর টাইমস্ট্যাম্প ছাড়া রাখুন। যা কিছু প্রতি কলে বদলায়, তা ব্রেকপয়েন্টের পরে দিন।"),
        ("Keep a fingerprint, a hash, of the system prompt in your CI, and raise an alert if it changes.",
         "CI-তে সিস্টেম প্রম্পটের একটি ফিঙ্গারপ্রিন্ট (হ্যাশ) রাখুন; তা বদলালে সতর্কতা দিন।")],
       [sh("system", "hot", ("hashed", "হ্যাশ করা")), sh("ci", "hot", ("alerts on change", "বদলালে সতর্ক করে")), sh("cache", "dim"), sh("msg", "hot", ("dynamic parts", "বদলানো অংশ"))],
       [ln("system", "ci", "to", state="hot", label=("hash", "হ্যাশ")), ln("system", "cache", "to", state="dim")],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Stable first, changing last, and keep the stable part exactly the same.",
         "স্থির অংশ আগে, বদলানো অংশ শেষে, আর স্থির অংশ হুবহু একই রাখুন।")],
       [sh("system"), sh("tools"), sh("docs"), sh("msg"), sh("cache"), sh("model")],
       [ln("system", "cache", "to"), ln("tools", "cache", "to"), ln("docs", "cache", "to"), ln("cache", "model", "to"), ln("msg", "model", "to")],
       [None, None, None, None],
       points=[("Put stable parts first (system prompt, tools, reused documents) and changing parts, like the user message, last.",
                "স্থির অংশ আগে রাখুন (সিস্টেম প্রম্পট, টুল, বারবার ব্যবহৃত ডকুমেন্ট), বদলানো অংশ, যেমন ইউজারের বার্তা, শেষে।"),
               ("If cached tokens cost about 10× less, repeated calls with a 60K-token prefix and 4K-token message save about 85% on input.",
                "ক্যাশ করা টোকেন প্রায় ১০ গুণ সস্তা হলে, ৬০K টোকেনের প্রিফিক্স আর ৪K টোকেনের বার্তায় বারবার কলে ইনপুট খরচ প্রায় ৮৫% কমে।"),
               ("One changed character breaks the cache for everything after it, so keep the prefix byte-identical and free of timestamps.",
                "একটি অক্ষর বদলালেই তার পরের সবকিছুর ক্যাশ ভাঙে, তাই প্রিফিক্স বাইট-টু-বাইট হুবহু আর টাইমস্ট্যাম্প ছাড়া রাখুন।"),
               ("Keep a fingerprint (hash) of the system prompt in your automatic test pipeline (CI); alert if it changes.",
                "স্বয়ংক্রিয় টেস্ট পাইপলাইনে (CI) সিস্টেম প্রম্পটের একটি ফিঙ্গারপ্রিন্ট (হ্যাশ) রাখুন; তা বদলালে সতর্কতা দিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
