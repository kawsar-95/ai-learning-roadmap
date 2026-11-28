"""Part 9 · 10 Browser and computer-use agents: a model that sees a screenshot and acts with mouse and keyboard, and where that wins and loses.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Loop       Body: "The model receives a screenshot ... picks an action, the runtime executes it, captures a new screenshot, and feeds both back. The loop continues until the model replies without a tool call." Start here: "A model sees a screenshot of the desktop and picks mouse or keyboard actions, in a loop, until it is done."
  2 Wins       List "Where computer use wins": no API exists; the API is hostile; one-off tasks; cross-app workflows.
  3 Loses      List "Where computer use loses": cost (vision tokens for every screenshot), latency (screenshot -> LLM -> action takes seconds), reliability, security.
  4 Browser    Body: "a constrained subset of computer use: the model can only see and act inside a single browser tab, not the whole desktop ... smaller surface area, which is why they're more reliable."
  5 Plan       Body, reliability pattern (1): "the model emits a structured plan up front ... which makes mid-run debugging easier".
  6 Checkpoint Body, reliability pattern (2): "each step is checkpointed, so a crash resumes from the last successful step".
  7 VM         Body, reliability pattern (3): "the agent runs in an isolated VM or browser profile, so a misclick can't reach the host system."
  8 Remember   Start here: "Have the model write a plan up front, checkpoint each step, and run in a VM or separate browser profile."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("agent", "model", ("Agent", "এজেন্ট"), 130, 162),
    node("shot", "file", ("Screenshot", "স্ক্রিনশট"), 130, 250),
    node("act", "tool", ("Mouse, keyboard", "মাউস, কিবোর্ড"), 620, 250),
    node("api", "server", ("API", "API"), 400, 60),
    node("app", "browser", ("App or site", "অ্যাপ বা সাইট"), 400, 162),
    node("bagent", "model", ("Browser agent", "ব্রাউজার এজেন্ট"), 130, 250),
    node("tab", "browser", ("One browser tab", "একটি ব্রাউজার ট্যাব"), 400, 250),
    node("desk", "server", ("Whole desktop", "পুরো ডেস্কটপ"), 400, 75),
    node("plan", "note", ("Plan up front", "আগে প্ল্যান"), 400, 162),
    node("ckpt", "storage", ("Checkpoint", "চেকপয়েন্ট"), 400, 162),
    node("vm", "shield", ("Sandboxed VM", "স্যান্ডবক্সড VM"), 400, 162),
    node("host", "server", ("Host system", "হোস্ট সিস্টেম"), 640, 162),
]

METRICS = [
    ("Cost", "খরচ"),
    ("Speed", "গতি"),
    ("Reliability", "নির্ভরযোগ্যতা"),
    ("Security", "নিরাপত্তা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Loop", "লুপ"),
       ("Screenshot, action, repeat", "স্ক্রিনশট, অ্যাকশন, আবার"),
       [("A computer-use agent looks at a screenshot and acts with the mouse and keyboard.",
         "কম্পিউটার-ইউজ এজেন্ট স্ক্রিনশট দেখে মাউস আর কিবোর্ড দিয়ে কাজ করে।"),
        ("The runtime runs the action, takes a new screenshot, and the loop continues until the model replies without a tool call.",
         "রানটাইম অ্যাকশন চালায়, নতুন স্ক্রিনশট নেয়, আর মডেল টুল কল ছাড়া উত্তর না দেওয়া পর্যন্ত লুপ চলে।")],
       [sh("shot", "hot"), sh("agent", "hot", ("picks an action", "অ্যাকশন বাছে"), x=380, y=60), sh("act", "hot")],
       [ln("shot", "agent", "to", state="hot"),
        ln("agent", "act", "to", state="hot"), ln("act", "shot", "to", state="hot")],
       [None, None, None, None]),

    st(("Wins", "জেতে"),
       ("Where computer use wins", "কোথায় কম্পিউটার ইউজ জেতে"),
       [("It wins when no API exists, or the API is hostile (costly or badly documented).",
         "API না থাকলে, বা API প্রতিকূল (দামি বা বাজে ডকুমেন্টেশনসহ) হলে এটি জেতে।"),
        ("It also wins for one-off tasks and cross-app work.",
         "কাজ একবারের হলে, বা একাধিক অ্যাপে ছড়ালেও এটি জেতে।")],
       [sh("agent", "hot", x=130), sh("app", "hot", ("the GUI is the way in", "GUI-ই ঢোকার পথ")), sh("api", "dim", ("none, or hostile", "নেই, বা প্রতিকূল"))],
       [ln("agent", "app", "to", state="hot"), ln("agent", "api", "to", state="dim")],
       [None, None, None, None],
       changes=[("+", "No API exists: the only way in is the GUI", "API নেই: ঢোকার একমাত্র পথ GUI"),
                ("+", "The API is hostile: costly or badly documented", "API প্রতিকূল: দামি বা বাজে ডকুমেন্টেশনসহ"),
                ("+", "One-off tasks, so the cost per task is acceptable", "একবারের কাজ, তাই প্রতি কাজের খরচ মেনে নেওয়া যায়"),
                ("+", "Cross-app workflows with no integration", "একাধিক অ্যাপের কাজ, যেখানে কোনো ইন্টিগ্রেশন নেই")]),

    st(("Loses", "হারে"),
       ("Where computer use loses", "কোথায় কম্পিউটার ইউজ হারে"),
       [("It loses on cost, latency, reliability, and security.",
         "খরচ, ল্যাটেন্সি, নির্ভরযোগ্যতা আর নিরাপত্তায় এটি হারে।"),
        ("Every screenshot costs vision tokens, and each screenshot → model → action cycle takes seconds.",
         "প্রতিটি স্ক্রিনশটে ভিশন টোকেন লাগে, আর প্রতিটি স্ক্রিনশট → মডেল → অ্যাকশন চক্রে কয়েক সেকেন্ড লাগে।")],
       [sh("shot", "warn", ("vision tokens", "ভিশন টোকেন")), sh("agent", "warn", ("seconds per cycle", "প্রতি চক্রে কয়েক সেকেন্ড"), x=380, y=60), sh("act", "warn")],
       [ln("shot", "agent", "to", state="warn"), ln("agent", "act", "to", state="warn"), ln("act", "shot", "to", state="warn")],
       [("more", "বেশি"), ("slower", "ধীর"), ("breaks easily", "সহজে ভাঙে"), None],
       changes=[("-", "Cost: more than a plain API call, with vision tokens for every screenshot", "খরচ: সাধারণ API কলের চেয়ে বেশি, প্রতিটি স্ক্রিনশটে ভিশন টোকেন"),
                ("-", "Latency: a click is instant, but the cycle takes seconds", "ল্যাটেন্সি: ক্লিক তাৎক্ষণিক, কিন্তু চক্রে কয়েক সেকেন্ড লাগে"),
                ("-", "Reliability: a shifted button, a popup, a captcha can kill the run", "নির্ভরযোগ্যতা: সরে যাওয়া বাটন, পপআপ বা ক্যাপচা রান নষ্ট করতে পারে"),
                ("-", "Security: the agent has unrestricted mouse and keyboard", "নিরাপত্তা: এজেন্টের মাউস আর কিবোর্ডে কোনো বাধা নেই")]),

    st(("Browser", "ব্রাউজার"),
       ("Browser agents are a smaller surface", "ব্রাউজার এজেন্টের পরিসর ছোট"),
       [("A browser agent can only see and act inside a single browser tab, not the whole desktop.",
         "ব্রাউজার এজেন্ট শুধু একটি ব্রাউজার ট্যাবের ভেতরে দেখতে ও কাজ করতে পারে, পুরো ডেস্কটপে নয়।"),
        ("It uses the same screenshot → action loop with a smaller surface, which is why it is more reliable.",
         "সে একই স্ক্রিনশট → অ্যাকশন লুপ ব্যবহার করে, কিন্তু পরিসর ছোট, তাই এটি বেশি নির্ভরযোগ্য।")],
       [sh("agent", "dim", x=130, y=75), sh("desk", "dim"), sh("bagent", "hot", ("smaller surface", "ছোট পরিসর")), sh("tab", "hot")],
       [ln("agent", "desk", "to", state="dim"), ln("bagent", "tab", "to", state="hot")],
       [None, None, ("more reliable", "বেশি নির্ভরযোগ্য"), None],
       note=("tip", "If you can frame the task in a browser, prefer a browser agent.",
             "কাজটা ব্রাউজারে করা গেলে ব্রাউজার এজেন্ট বেছে নিন।")),

    st(("Plan", "প্ল্যান"),
       ("Write a plan up front", "আগে প্ল্যান লেখান"),
       [("In the first reliability pattern, the model emits a structured plan up front.",
         "প্রথম নির্ভরযোগ্যতার প্যাটার্নে মডেল শুরুতেই একটি কাঠামোবদ্ধ প্ল্যান লেখে।"),
        ("This makes mid-run debugging easier.",
         "এতে চলার মাঝখানে ডিবাগ করা সহজ হয়।")],
       [sh("agent", "hot", x=130), sh("plan", "hot", ("makes debugging easier", "ডিবাগ সহজ হয়")), sh("act", "hot", x=630, y=162)],
       [ln("agent", "plan", "to", state="hot"), ln("plan", "act", "to", state="hot")],
       [None, None, None, None]),

    st(("Checkpoint", "চেকপয়েন্ট"),
       ("Checkpoint each step", "প্রতিটি ধাপ চেকপয়েন্ট করুন"),
       [("In the second pattern, each step is checkpointed.",
         "দ্বিতীয় প্যাটার্নে প্রতিটি ধাপ চেকপয়েন্ট করা হয়।"),
        ("So a crash resumes from the last successful step.",
         "তাই ক্র্যাশ হলে শেষ সফল ধাপ থেকে আবার চলে।")],
       [sh("act", "hot", x=130, y=162), sh("ckpt", "hot", ("last successful step", "শেষ সফল ধাপ")), sh("agent", "hot", x=620, y=162, sub=("resumes", "আবার চলে"))],
       [ln("act", "ckpt", "to", state="hot"), ln("ckpt", "agent", "to", state="hot")],
       [None, None, ("resumes", "আবার চলে"), None]),

    st(("VM", "VM"),
       ("Run in an isolated VM", "আলাদা VM-এ চালান"),
       [("In the third pattern, the agent runs in an isolated VM or browser profile.",
         "তৃতীয় প্যাটার্নে এজেন্ট চলে একটি আলাদা VM বা ব্রাউজার প্রোফাইলে।"),
        ("So a misclick can't reach the host system.",
         "তাই ভুল ক্লিক হোস্ট সিস্টেমে পৌঁছাতে পারে না।")],
       [sh("agent", "hot", x=130), sh("vm", "hot", ("isolated", "আলাদা করা")), sh("host", "dim", ("not reached", "পৌঁছায় না"))],
       [ln("agent", "vm", "to", state="hot"), ln("vm", "host", "to", state="dim")],
       [None, None, None, ("isolated", "আলাদা")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Have the model write a plan up front, checkpoint each step, and run in a VM or separate browser profile.",
         "মডেলকে দিয়ে আগে প্ল্যান লেখান, প্রতিটি ধাপ চেকপয়েন্ট করুন, আর VM বা আলাদা ব্রাউজার প্রোফাইলে চালান।")],
       [sh("agent", "hot", x=135, y=70), sh("plan", "hot", x=380, y=70), sh("ckpt", "hot", x=640, y=70), sh("vm", "hot", x=640, y=250)],
       [ln("agent", "plan", "to", state="hot"), ln("plan", "ckpt", "to", state="hot"), ln("ckpt", "vm", "to", state="hot")],
       [None, None, None, None],
       points=[("It can work where no API exists, but it costs more, is slower, and breaks more easily.",
                "যেখানে API নেই সেখানে সে কাজ করতে পারে, কিন্তু খরচ বেশি, গতি ধীর, আর সহজে ভেঙে যায়।"),
               ("If you can frame the task in a browser, prefer a browser agent.",
                "কাজটা ব্রাউজারে করা গেলে ব্রাউজার এজেন্ট বেছে নিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
