"""Part 1 · 10 Reasoning models & extended thinking: a reasoning model spends tokens thinking before it answers.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Standard    Sub-title: reasoning models "Instead of answering immediately, ... emit a chain of internal reasoning". Layman's voice: "A regular AI answers instantly ... (maybe wrong)".
                The table: Math, physics, formal proofs: Standard "poor", Reasoning "best".
  2 Think first Start here: "A reasoning model thinks before it answers. It writes out its working steps first, which helps on hard problems like math and code".
                Thinking tokens ("The model's working notes, written before the final answer"), Chain of thought ("like showing your working in a math test").
  3 Cost        Start here: thinking tokens "count as tokens too". Panel Costs: "Reasoning models can use many times more tokens per query, depending on the task and thinking budget". Callout: "They can cost many times more and are slower".
  4 Wait        Panel Latency: "TTFT is often slower because the model writes thinking tokens before the answer. Streaming the thinking tokens can help UX." Start here: TTFT ("How long it takes until the model's first output appears").
  5 Budget      Start here: Thinking budget ("A cap on how many thinking tokens the model may use, to control cost and waiting time"). Panel Costs: "set it to your latency/cost ceiling".
                The code: budget_tokens 10000. Layman's voice: "For easy questions it finishes early. For hard ones, it uses the full budget."
  6 Where       Start here: "Use reasoning models for math, hard coding, and planning, not for chat, summaries, or simple questions." The table: "overkill", "Reasoning models waste tokens".
                Callout: "Don't reach for reasoning models by reflex."
  7 Training    Start here: Reinforcement learning ("Training by reward: the model tries, gets a score, and learns to do more of what scored well"), Distillation.
                Body: "o1 is trained with large-scale reinforcement learning to reason using chain of thought". Panel Distillation: "DeepSeek-R1 distilled into Qwen 1.5B–32B".
  8 Remember    The three "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ব্যবহারকারী"), 80, 165),
    node("std", "model", ("Standard model", "স্ট্যান্ডার্ড মডেল"), 270, 165),
    node("rsn", "model", ("Reasoning model", "রিজনিং মডেল"), 270, 165),
    node("think", "note", ("Thinking tokens", "থিংকিং টোকেন"), 484, 165),
    node("ans", "file", ("Answer", "উত্তর"), 668, 165),
    node("budget", "lock", ("Thinking budget", "থিংকিং বাজেট"), 484, 45),
    node("bill", "chart", ("Bill", "বিল"), 484, 285),
    node("clock", "clock", ("First output (TTFT)", "প্রথম আউটপুট (TTFT)"), 270, 285),
    node("reward", "chart", ("Reward", "পুরস্কার"), 270, 45),
]

METRICS = [
    ("Tokens used", "ব্যবহৃত টোকেন"),
    ("Wait for first output", "প্রথম আউটপুটের অপেক্ষা"),
    ("Hard math answers", "কঠিন গণিতের উত্তর"),
]

CAPTION = ("Rough comparisons from this section. They depend on the task.", "এই সেকশন থেকে মোটামুটি তুলনা। কাজ অনুযায়ী বদলায়।")

SHORT = ("short", "কম")
FEWER = ("fewer", "কম")
MANY = ("many times more", "অনেক গুণ বেশি")
LONGER = ("longer", "বেশি")
POOR = ("poor", "দুর্বল")
BEST = ("best", "সেরা")
CAPPED = ("capped", "সীমিত")

STEPS = [
    st(("Standard", "সাধারণ"),
       ("A standard model answers right away", "সাধারণ মডেল সাথে সাথে উত্তর দেয়"),
       [("A standard model answers right away. It reads a hard problem and writes an answer at once.",
         "সাধারণ মডেল সাথে সাথে উত্তর দেয়। কঠিন সমস্যাটা পড়েই সে এক্ষুনি একটা উত্তর লিখে ফেলে।"),
        ("On hard math, that quick answer is often poor.",
         "কঠিন গণিতে সেই তাড়াতাড়ির উত্তর প্রায়ই খারাপ হয়।")],
       [sh("user", "hot", sub=("hard problem", "কঠিন সমস্যা")), sh("std", "hot", sub=("answers right away", "সাথে সাথে উত্তর")),
        sh("ans", "warn", sub=("may be wrong", "ভুল হতে পারে"))],
       [ln("user", "std", "to", state="hot"), ln("std", "ans", "to", 700, "warn")],
       [FEWER, SHORT, POOR]),

    st(("Think first", "আগে ভাবে"),
       ("A reasoning model thinks first", "রিজনিং মডেল আগে ভাবে"),
       [("A reasoning model thinks before it answers. It first writes out its working steps, called thinking tokens.",
         "রিজনিং মডেল উত্তর দেওয়ার আগে ভাবে। সে আগে নিজের কাজের ধাপগুলো লিখে নেয়, যাকে থিংকিং টোকেন বলে।"),
        ("Only then does it write the final answer. On hard problems like math and code, this helps.",
         "তারপরই সে চূড়ান্ত উত্তর লেখে। গণিত আর কোডের মতো কঠিন সমস্যায় এটা কাজে দেয়।")],
       [sh("user", sub=("hard problem", "কঠিন সমস্যা")), sh("rsn", "hot", sub=("thinks first", "আগে ভাবে")), sh("think", "hot"),
        sh("ans", "hot", sub=("final answer", "চূড়ান্ত উত্তর"))],
       [ln("user", "rsn", "to"), ln("rsn", "think", "to", 1800, "hot"), ln("think", "ans", "to", 1200, "hot")],
       [MANY, LONGER, BEST],
       note=("insight",
             "Thinking tokens are the model's working notes, like showing your working in a math test.",
             "থিংকিং টোকেন হলো মডেলের খসড়া নোট, যেমন অঙ্ক পরীক্ষায় পুরো কাজ দেখিয়ে লেখা।"),
       changes=[("+", "Thinking tokens come before the answer", "উত্তরের আগে থিংকিং টোকেন আসে"),
                ("+", "Better answers on hard math", "কঠিন গণিতে ভালো উত্তর")]),

    st(("Cost", "খরচ"),
       ("Thinking costs tokens", "ভাবতেও টোকেন লাগে"),
       [("Thinking tokens count as tokens too, so you pay for them and wait for them.",
         "থিংকিং টোকেনও টোকেন হিসেবে গোনা হয়, তাই এগুলোর জন্যও টাকা দিতে হয়, সময়ও লাগে।"),
        ("A reasoning model can use many times more tokens for one query, depending on the task and the thinking budget. That is why it costs more.",
         "একটি প্রশ্নে রিজনিং মডেল অনেক গুণ বেশি টোকেন খরচ করতে পারে, কাজ আর থিংকিং বাজেটের ওপর নির্ভর করে। তাই খরচও বেশি।")],
       [sh("rsn", "dim"), sh("think", "hot", sub=("count as tokens", "এগুলোও টোকেন")), sh("bill", "warn", sub=("many times more", "অনেক গুণ বেশি"))],
       [ln("rsn", "think", "to", state="dim"), ln("think", "bill", "to", state="warn")],
       [MANY, LONGER, BEST],
       changes=[("+", "Every thinking token is billed", "প্রতিটি থিংকিং টোকেনের দাম দিতে হয়")]),

    st(("Wait", "অপেক্ষা"),
       ("The first output comes later", "প্রথম আউটপুট আসে দেরিতে"),
       [("Thinking also changes the wait. TTFT, the time until the first output appears, is often slower, because the model writes thinking tokens before the answer.",
         "ভাবার ফলে অপেক্ষার সময়ও বদলায়। TTFT, মানে প্রথম আউটপুট দেখা দিতে যে সময় লাগে, তা প্রায়ই বেশি হয়, কারণ মডেল উত্তরের আগে থিংকিং টোকেন লেখে।"),
        ("Streaming the thinking tokens as they are written can help the user experience.",
         "থিংকিং টোকেন লেখা হওয়ার সঙ্গে সঙ্গে স্ট্রিম করলে ব্যবহারকারীর অভিজ্ঞতা ভালো হয়।")],
       [sh("user", "dim"), sh("rsn", "hot"), sh("think", sub=("can be streamed", "স্ট্রিম করা যায়")),
        sh("clock", "warn", sub=("often slower", "প্রায়ই ধীর"))],
       [ln("user", "rsn", "to", state="dim"), ln("rsn", "think", "to"), ln("rsn", "clock", "to", state="warn")],
       [MANY, LONGER, BEST],
       changes=[("~", "The first output appears later", "প্রথম আউটপুট দেরিতে আসে")]),

    st(("Budget", "বাজেট"),
       ("A thinking budget sets the cap", "থিংকিং বাজেট সীমা ঠিক করে"),
       [("A thinking budget caps how many thinking tokens the model may use. It controls cost and waiting time.",
         "থিংকিং বাজেট ঠিক করে দেয় মডেল সর্বোচ্চ কত থিংকিং টোকেন খরচ করতে পারবে। এতে খরচ আর অপেক্ষা নিয়ন্ত্রণে থাকে।"),
        ("In the section's code, <code>budget_tokens</code> is 10,000. Set it to your latency and cost ceiling.",
         "এই সেকশনের কোডে <code>budget_tokens</code> হলো ১০,০০০। এটা আপনার ল্যাটেন্সি আর খরচের সীমায় ঠিক করে দিন।")],
       [sh("rsn", "hot"), sh("think", "hot", sub=("stops at the cap", "সীমায় থামে")),
        sh("budget", "hot", sub=("10,000 tokens", "১০,০০০ টোকেন"))],
       [ln("rsn", "think", "to", state="hot"), ln("budget", "think", "to", state="hot")],
       [CAPPED, LONGER, BEST],
       note=("tip",
             "An easy question can finish before the cap. A hard one can use all of it.",
             "সহজ প্রশ্নে সীমা আসার আগেই শেষ হয়ে যায়। কঠিন প্রশ্নে পুরো সীমাই খরচ হতে পারে।"),
       changes=[("-", "Thinking tokens stop at the budget", "বাজেটে পৌঁছালে থিংকিং টোকেন থেমে যায়")]),

    st(("Where", "কোথায়"),
       ("Use it where it pays off", "যেখানে লাভ, সেখানেই ব্যবহার করুন"),
       [("Use a reasoning model for math, hard coding, and planning.",
         "গণিত, কঠিন কোডিং আর পরিকল্পনায় রিজনিং মডেল ব্যবহার করুন।"),
        ("Do not use one for chat, summaries, or simple questions. A standard model is best there, and a reasoning model would only cost more.",
         "চ্যাট, সারাংশ বা সহজ প্রশ্নে নয়। সেখানে সাধারণ মডেলই সবচেয়ে ভালো, রিজনিং মডেলে শুধু খরচ বাড়ে।")],
       [sh("user", x=380, y=50), sh("std", "hot", sub=("chat, summaries", "চ্যাট, সারাংশ"), x=190, y=235),
        sh("rsn", "hot", sub=("math, code, planning", "গণিত, কোড, পরিকল্পনা"), x=570, y=235)],
       [ln("user", "std", "to", state="hot", label=("easy", "সহজ")), ln("user", "rsn", "to", state="hot", label=("hard", "কঠিন"))],
       [CAPPED, LONGER, BEST],
       note=("warn",
             "Do not reach for a reasoning model by reflex.",
             "অভ্যাসবশে রিজনিং মডেল নেবেন না।")),

    st(("Training", "ট্রেনিং"),
       ("How a model learns to think", "মডেল কীভাবে ভাবতে শেখে"),
       [("A reasoning model is trained by reward, called reinforcement learning: it tries, gets a score, and learns to do more of what scored well.",
         "রিজনিং মডেলকে ট্রেন করা হয় পুরস্কার দিয়ে, যাকে রিইনফোর্সমেন্ট লার্নিং বলে: মডেল চেষ্টা করে, স্কোর পায়, আর যেটায় ভালো স্কোর আসে সেটা বেশি করতে শেখে।"),
        ("Reasoning models are trained with large-scale reinforcement learning to reason using chain of thought, a step-by-step line of reasoning.",
         "রিজনিং মডেলকে বড় মাপের রিইনফোর্সমেন্ট লার্নিং দিয়ে ট্রেন করা হয়, যাতে সে চেইন অফ থট, মানে ধাপে ধাপে যুক্তি, ব্যবহার করে ভাবতে শেখে।")],
       [sh("rsn", "hot"), sh("reward", "hot", sub=("a score", "একটি স্কোর"))],
       [ln("rsn", "reward", "both", 1400, "hot")],
       [CAPPED, LONGER, BEST],
       note=("insight",
             "A small model can learn the skill from a big model's outputs. This is called distillation.",
             "ছোট মডেল বড় মডেলের আউটপুট থেকে দক্ষতাটা শিখতে পারে। একে ডিস্টিলেশন বলে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A reasoning model trades cost and waiting time for better answers on hard problems.",
         "রিজনিং মডেল কঠিন সমস্যায় ভালো উত্তরের বদলে খরচ আর অপেক্ষার সময় বাড়ায়।")],
       [sh("user"), sh("rsn", x=270, y=85), sh("std", x=270, y=245), sh("ans")],
       [ln("user", "rsn", "to"), ln("user", "std", "to"), ln("rsn", "ans", "to"), ln("std", "ans", "to")],
       [CAPPED, LONGER, BEST],
       points=[("Use reasoning models for math, hard coding, and planning, not for chat, summaries, or simple questions.",
                "গণিত, কঠিন কোডিং আর পরিকল্পনায় রিজনিং মডেল ব্যবহার করুন; চ্যাট, সারাংশ বা সহজ প্রশ্নে নয়।"),
               ("They can use many times more tokens, so set a thinking budget.",
                "এরা অনেক গুণ বেশি টোকেন খরচ করতে পারে, তাই থিংকিং বাজেট ঠিক করে দিন।"),
               ("For most chat, extraction, and RAG, a standard model with careful prompting wins.",
                "বেশিরভাগ চ্যাট, এক্সট্র্যাকশন আর RAG-এ ভালো প্রম্পটিংসহ সাধারণ মডেলই সবচেয়ে ভালো কাজ করে।")]),
]

WALK = walk(760, 330, NODES, METRICS, CAPTION, STEPS)
