"""Part 4 · 01 Context window budgeting: one fixed window, shared by five parts, with room kept for the answer.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Window    Start here: "A model can only hold so much text at once. Context window budgeting means deciding in advance how much room each part gets, because every part competes for the same space."
              Context window ("The fixed amount of text a model can read at once. Everything you send, and the answer, must fit inside."); the diagram caption: "A 200K-token window".
  2 System    Start here: System prompt ("The standing instructions at the start: the persona, the output format, and the hard rules."); body: "floor of ~1–2K tokens ... Larger prompts cost more per call AND dilute attention."
              Bangla voice: "২০০K টোকেনের একটি উইন্ডোতে সাধারণ ভাগ হতে পারে: সিস্টেম ≈ ৮%, টুল ≈ ৭%, রিট্রিভাল ≈ ৪০%, হিস্ট্রি ≈ ৩০%, বর্তমান টার্ন ≈ ১৫%" and "এটি এজেন্টিক RAG অ্যাপের জন্য একটি সাধারণ উদাহরণ, সব ক্ষেত্রে এক নয়".
  3 Tools     Start here: Tool definitions ("Include only the tools the current step might need."); body: "floor of ~1–3K tokens ... load specialised tools lazily".
  4 Retrieval Start here: Retrieval ("Cap the number of pieces, and prefer quality over quantity."); body: "budget = window − system − tools − current turn − reserved output".
              Layman's voice: "If you're running over budget, shrink the retrieval first — not the system prompt."
  5 History   Body: "History: shrink aggressively. Use summarization (§2) or selective replay to keep it bounded."
  6 Turn      Sub-title: "the user's actual request"; the five shares of the Bangla voice (8, 7, 40, 30 and 15 %).
  7 Reserve   Start here: Output reservation ("Setting aside tokens for the answer before you fill the window. Without it, the answer gets cut off and fails silently."); body: "Forcing truncation produces silent failures."
  8 Middle    Start here: Lost in the Middle ("models recall the start and end of a long prompt well, but do close to random in the middle"); remember: "Put the most important information at the start or the end of the prompt, not the middle."
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("system", "note", ("System prompt", "সিস্টেম প্রম্পট"), 95, 75),
    node("tools", "tool", ("Tool definitions", "টুল ডেফিনিশন"), 285, 75),
    node("retr", "database", ("Retrieval", "রিট্রিভাল"), 480, 75),
    node("history", "queue", ("History", "হিস্ট্রি"), 670, 75),
    node("turn", "user", ("Current request", "বর্তমান অনুরোধ"), 130, 250),
    node("window", "model", ("Context window", "কনটেক্সট উইন্ডো"), 380, 250),
    node("answer", "file", ("Answer", "উত্তর"), 640, 250),
]

METRICS = [
    ("Window", "উইন্ডো"),
    ("Share", "ভাগ"),
    ("Floor", "সর্বনিম্ন"),
    ("Answer", "উত্তর"),
]

CAPTION = (
    "Example: a 200K-token window. The shares are typical for an agentic RAG app, not universal.",
    "উদাহরণ: ২০০K টোকেনের একটি উইন্ডো। ভাগগুলো এজেন্টিক RAG অ্যাপের জন্য সাধারণ, সব ক্ষেত্রে এক নয়।",
)

W = ("200K tokens", "২০০K টোকেন")
CLAIMANTS = ["system", "tools", "retr", "history", "turn"]


def feeds(state=None, only=None):
    """A line from each claimant into the window."""
    return [ln(c, "window", "to", state=state) for c in CLAIMANTS if only is None or c in only]


STEPS = [
    st(("Window", "উইন্ডো"),
       ("One window, fixed in size", "একটি উইন্ডো, আকার নির্দিষ্ট"),
       [("A model can only hold so much text at once. The context window is the fixed amount of text it can read at once. Everything you send, and the answer, must fit inside.",
         "মডেল একবারে সীমিত লেখাই ধরে রাখতে পারে। কনটেক্সট উইন্ডো হলো সে একবারে যতটুকু লেখা পড়তে পারে তার নির্দিষ্ট সীমা। আপনার পাঠানো সবকিছু আর উত্তর, এর ভেতরেই ধরাতে হয়।"),
        ("Budgeting means deciding in advance how much room each part gets, because every part competes for the same space.",
         "বাজেটিং মানে আগে থেকেই ঠিক করা, কোন অংশ কতটা জায়গা পাবে, কারণ সব অংশ একই জায়গার জন্য টানাটানি করে।")],
       [sh("system", "dim"), sh("tools", "dim"), sh("retr", "dim"), sh("history", "dim"), sh("turn", "dim"), sh("window", "hot", W)],
       feeds("dim"),
       [W, None, None, None]),

    st(("System", "সিস্টেম"),
       ("The system prompt: standing instructions", "সিস্টেম প্রম্পট: স্থায়ী নির্দেশ"),
       [("The system prompt holds the standing instructions: the persona, the output format, and the hard rules. It needs a floor of about 1–2K tokens.",
         "সিস্টেম প্রম্পটে থাকে স্থায়ী নির্দেশ: পারসোনা, আউটপুটের কাঠামো আর কড়া নিয়ম। এতে কমপক্ষে ~১–২K টোকেন লাগে।"),
        ("Larger prompts cost more per call and dilute attention. In the example it takes about 8% of the window.",
         "বেশি বড় করলে খরচ বাড়ে এবং মডেলের মনোযোগ পাতলা হয়ে যায়। উদাহরণে এটা উইন্ডোর প্রায় ৮%।")],
       [sh("system", "hot", ("≈ 8%", "≈ ৮%")), sh("window", "hot", W)],
       feeds("hot", ["system"]),
       [W, "≈ 8%", ("~1–2K tokens", "~১–২K টোকেন"), None],
       changes=[("+", "The system prompt takes its share", "সিস্টেম প্রম্পট তার ভাগ নেয়")]),

    st(("Tools", "টুল"),
       ("Tool definitions: only what this step needs", "টুল ডেফিনিশন: শুধু যা এই ধাপে লাগে"),
       [("Tool definitions describe the tools the model may call. They need a floor of about 1–3K tokens.",
         "টুল ডেফিনিশনে থাকে মডেল কোন টুল ডাকতে পারে তার বর্ণনা। এতে ~১–৩K টোকেন লাগে।"),
        ("Include only the tools the current step might need, and load specialised tools lazily. In the example it is about 7%.",
         "শুধু সেই টুলই রাখুন, যা এই ধাপে লাগতে পারে; বিশেষ টুল দরকারের সময় লোড করুন। উদাহরণে প্রায় ৭%।")],
       [sh("system", "dim"), sh("tools", "hot", ("≈ 7%", "≈ ৭%")), sh("window", "hot", W)],
       feeds("dim", ["system"]) + feeds("hot", ["tools"]),
       [W, "≈ 7%", ("~1–3K tokens", "~১–৩K টোকেন"), None],
       changes=[("+", "Only the tools this step might call", "শুধু সেই টুল, যা এই ধাপে ডাকা হতে পারে")]),

    st(("Retrieval", "রিট্রিভাল"),
       ("Retrieval is usually the biggest slice", "রিট্রিভালই সাধারণত সবচেয়ে বড় অংশ"),
       [("Retrieval means finding pieces of documents and putting them in the prompt. Its budget is what is left: the window minus the system prompt, the tools, the current turn and the reserved output.",
         "রিট্রিভাল মানে ডকুমেন্টের অংশ খুঁজে এনে প্রম্পটে দেওয়া। এর বাজেট হলো যা বাকি থাকে: উইন্ডো − সিস্টেম − টুল − বর্তমান টার্ন − রিজার্ভ করা আউটপুট।"),
        ("Cap the number of pieces, and prefer quality over quantity. In the example it is about 40%.",
         "অংশের সংখ্যা সীমিত রাখুন, আর পরিমাণের চেয়ে মানকে বেশি গুরুত্ব দিন। উদাহরণে এটা প্রায় ৪০%।")],
       [sh("system", "dim"), sh("tools", "dim"), sh("retr", "hot", ("≈ 40%", "≈ ৪০%")), sh("window", "hot", W)],
       feeds("dim", ["system", "tools"]) + feeds("hot", ["retr"]),
       [W, "≈ 40%", None, None],
       note=("tip",
             "If you run over budget, shrink the retrieval first, not the system prompt.",
             "বাজেট ছাড়িয়ে গেলে আগে রিট্রিভাল কমান, সিস্টেম প্রম্পট নয়।")),

    st(("History", "হিস্ট্রি"),
       ("History: shrink it aggressively", "হিস্ট্রি: কঠোরভাবে ছোট রাখুন"),
       [("Old chat messages take room too. Shrink the history aggressively, with summarization or selective replay, so it stays bounded.",
         "পুরোনো চ্যাট বার্তাও জায়গা নেয়। সামারাইজেশন বা বেছে বেছে আবার চালানো দিয়ে হিস্ট্রি কঠোরভাবে ছোট রাখুন, যাতে তা সীমার ভেতরে থাকে।"),
        ("In the example it is about 30%.",
         "উদাহরণে এটা প্রায় ৩০%।")],
       [sh("retr", "dim"), sh("history", "hot", ("≈ 30%", "≈ ৩০%")), sh("window", "hot", W)],
       feeds("dim", ["retr"]) + feeds("hot", ["history"]),
       [W, "≈ 30%", None, None],
       changes=[("-", "Old turns are summarized or replayed in part", "পুরোনো টার্ন সংক্ষেপ করা হয় বা আংশিক আবার চালানো হয়")]),

    st(("Turn", "টার্ন"),
       ("The current turn: the user's request", "বর্তমান টার্ন: ইউজারের অনুরোধ"),
       [("The current turn is what the user just asked. In the example it takes about 15% of the window.",
         "বর্তমান টার্ন হলো ইউজার এইমাত্র যা জিজ্ঞেস করেছে। উদাহরণে এটা উইন্ডোর প্রায় ১৫%।"),
        ("Together, the five parts share the window: about 8%, 7%, 40%, 30% and 15%.",
         "পাঁচটি অংশ মিলে উইন্ডো ভাগ করে নেয়: প্রায় ৮%, ৭%, ৪০%, ৩০% আর ১৫%।")],
       [sh("system", "hot", ("≈ 8%", "≈ ৮%")), sh("tools", "hot", ("≈ 7%", "≈ ৭%")), sh("retr", "hot", ("≈ 40%", "≈ ৪০%")),
        sh("history", "hot", ("≈ 30%", "≈ ৩০%")), sh("turn", "hot", ("≈ 15%", "≈ ১৫%")), sh("window", "hot", W)],
       feeds("hot"),
       [W, "≈ 15%", None, None]),

    st(("Reserve", "রিজার্ভ"),
       ("Reserve room for the answer first", "আগে উত্তরের জন্য জায়গা রাখুন"),
       [("Output reservation means setting aside tokens for the answer before you fill the window.",
         "আউটপুট রিজার্ভেশন মানে উইন্ডো ভরার আগেই উত্তরের জন্য টোকেন আলাদা করে রাখা।"),
        ("Without it, the answer gets cut off and fails silently.",
         "না রাখলে উত্তর কেটে যায় আর নীরবে ব্যর্থ হয়।")],
       [sh("window", "hot", W), sh("answer", "hot", ("reserved", "রিজার্ভ করা"))],
       [ln("window", "answer", "to", state="hot")],
       [W, None, None, ("reserved", "রিজার্ভ করা")],
       note=("warn",
             "Forcing truncation produces silent failures.",
             "জোর করে কেটে ফেললে নীরব ব্যর্থতা ঘটে।")),

    st(("Middle", "মাঝখান"),
       ("Lost in the Middle: where you put it matters", "Lost in the Middle: কোথায় রাখছেন, সেটাও জরুরি"),
       [("Models recall the start and end of a long prompt well, but do close to random in the middle.",
         "লম্বা প্রম্পটের শুরু আর শেষের তথ্য মডেল ভালো মনে রাখে, কিন্তু মাঝখানের তথ্যে ফল প্রায় র‍্যান্ডমের কাছাকাছি।"),
        ("So put the most important information at the start or the end of the prompt, not in the middle.",
         "তাই যা সবচেয়ে জরুরি, তা প্রম্পটের শুরুতে বা শেষে রাখুন, মাঝখানে নয়।")],
       [sh("system", "dim"), sh("tools", "dim"), sh("retr", "dim"), sh("history", "dim"), sh("turn", "dim"),
        sh("window", "warn", ("middle is risky", "মাঝখান ঝুঁকিপূর্ণ"))],
       feeds("dim"),
       [W, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("One window, five parts and a reserved answer: decide the budget before you fill it.",
         "একটি উইন্ডো, পাঁচটি অংশ আর রিজার্ভ করা উত্তর: ভরার আগেই বাজেট ঠিক করুন।")],
       [sh("system"), sh("tools"), sh("retr"), sh("history"), sh("turn"), sh("window"), sh("answer")],
       feeds() + [ln("window", "answer", "to")],
       [None, None, None, None],
       points=[("A system prompt needs a floor of ~1–2K tokens. Tool definitions need ~1–3K.",
                "সিস্টেম প্রম্পটে কমপক্ষে ~১–২K টোকেন লাগে। টুল ডেফিনিশনে লাগে ~১–৩K।"),
               ("Put the most important information at the start or the end of the prompt, not the middle.",
                "যা সবচেয়ে জরুরি, তা প্রম্পটের শুরুতে বা শেষে রাখুন, মাঝখানে নয়।"),
               ("Keep history small and cap retrieval chunks. Quality beats quantity.",
                "হিস্ট্রি ছোট রাখুন আর রিট্রিভালের অংশ সীমিত করুন। পরিমাণের চেয়ে মান ভালো।"),
               ("Always reserve tokens for the answer, or it is cut off and fails silently.",
                "উত্তরের জন্য টোকেন আগেই রাখুন, নইলে উত্তর কেটে গিয়ে নীরবে ব্যর্থ হয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
