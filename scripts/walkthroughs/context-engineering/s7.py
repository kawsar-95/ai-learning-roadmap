"""Part 4 · 07 Lost in the Middle & mitigation: models recall the start and end of a long input, and miss the middle.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Finding   Start here: "Models remember the start and end of a long input well, but they often miss facts in the middle. This is Lost in the Middle, and it changes how you should arrange a prompt."
  2 Test      Body, the evidence: "Liu et al. inserted random "needle" facts at varying positions in a long context and measured retrieval accuracy. Result: U-shaped performance curve — recall is high at the start, collapses in the middle, recovers at the end."
              Needle fact ("A single fact hidden at a chosen spot in a long text, used to test whether the model can find it."); U-shaped curve ("A graph that is high at the start, low in the middle, and high again at the end.").
  3 Longer    Sub-title: "The longer the context, the worse the middle."; body: "The effect is worse for longer contexts and weaker models, but persists even in frontier models with 100K+ context windows."
  4 Why       Body, "Why does it happen?": attention is biased by position (RoPE, ALiBi, YaRN "help but don't fully fix it"); the training distribution ("Most pre-training data has shorter contexts"); "Positional primacy & recency ... the same bias that affects humans."
  5 Ends      Layman's voice, ways 1 and 2: "Sandwich it: put the most important stuff at the very top of your prompt AND repeat it at the very bottom. Hit both attention peaks." "Re-order documents: if you retrieved 10 documents, put the most relevant at the start and the end, the least relevant in the middle."
  6 Shorter   Layman's voice, ways 3 and 4: "Cut shorter: shorter prompts = better recall. If you can fit it in 8K tokens, don't use 50K." "Mark the important: wrap critical info in <important>…</important> tags. Strong models pay attention to marked regions."
  7 Again     Layman's voice, ways 5 and 6: "Re-query when unsure: ... ask it to look again with what it learned. Two short passes beat one long one." "Add an "answer here" prompt: end the prompt with "based on the above, your answer:". This nudges the AI to look back over the whole context one more time before responding."
  8 Later     Body, "The empirical reality check": "Follow-up work (RULER, 2024; Summary-of-a-Haystack, 2024; BABILong, 2024) ... The U-curve flattens with better models and longer-context training, but never fully goes away. Variable-length tasks ... are harder than fixed-length. Multi-hop reasoning across long contexts remains an open problem. RAG + long-context is complementary, not redundant."
  9 Remember  The practical rule ("If neither works, the model genuinely can't handle that fact — use a smaller context, or external retrieval, or a different architecture.") and the four "remember" points of the Start here box.

Box labels are plain text, so the <important> tag appears only in step text, written as an escaped <code>.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("start", "note", ("Start of prompt", "প্রম্পটের শুরু"), 110, 75),
    node("mid", "note", ("Middle", "মাঝখান"), 380, 75),
    node("end", "note", ("End of prompt", "প্রম্পটের শেষ"), 650, 75),
    node("model", "model", ("Model", "মডেল"), 380, 250),
    node("needle", "file", ("Needle fact", "নিডল ফ্যাক্ট"), 380, 250),
    node("attn", "model", ("Attention", "অ্যাটেনশন"), 110, 250),
    node("pretrain", "database", ("Training data", "ট্রেনিং ডেটা"), 380, 250),
    node("bias", "user", ("Primacy & recency", "প্রাইমেসি ও রিসেন্সি"), 650, 250),
]

METRICS = [
    ("Start", "শুরু"),
    ("Middle", "মাঝখান"),
    ("End", "শেষ"),
    ("Context", "কনটেক্সট"),
]

CAPTION = (
    "Where a fact sits in a long prompt matters as much as what the fact is.",
    "লম্বা প্রম্পটে তথ্য কোথায় বসে, সেটা কী তথ্য তার মতোই গুরুত্বপূর্ণ।",
)

HIGH = ("high", "উঁচু")
LOW = ("low", "নিচু")


def fan(state_mid="hot", dim=()):
    """The start, the middle and the end all feed the model; the middle's line takes `state_mid`."""
    return [
        ln("start", "model", "to", state="dim" if "start" in dim else "hot"),
        ln("mid", "model", "to", state="dim" if "mid" in dim else state_mid),
        ln("end", "model", "to", state="dim" if "end" in dim else "hot"),
    ]


STEPS = [
    st(("Finding", "আবিষ্কার"),
       ("The middle gets lost", "মাঝখানটা হারিয়ে যায়"),
       [("Models remember the start and end of a long input well, but they often miss facts in the middle. This is Lost in the Middle.",
         "লম্বা ইনপুটের শুরু আর শেষ মডেল ভালো মনে রাখে, কিন্তু মাঝখানের তথ্য প্রায়ই হারিয়ে ফেলে। একে বলে Lost in the Middle।"),
        ("It changes how you should arrange a prompt.",
         "এটি প্রম্পট সাজানোর নিয়ম বদলে দেয়।")],
       [sh("start", "hot", ("well recalled", "ভালো মনে থাকে")), sh("mid", "warn", ("often missed", "প্রায়ই বাদ পড়ে")),
        sh("end", "hot", ("well recalled", "ভালো মনে থাকে")), sh("model", "hot")],
       fan("warn"),
       [None, None, None, None]),

    st(("Test", "পরীক্ষা"),
       ("The needle test", "নিডল পরীক্ষা"),
       [("Liu et al. (2023) hid “needle” facts at varying positions in a long context and measured retrieval accuracy. A needle fact is a single fact hidden at a chosen spot, to test whether the model can find it.",
         "Liu et al. (২০২৩) লম্বা কনটেক্সটের বিভিন্ন অবস্থানে “নিডল” তথ্য বসিয়ে রিট্রিভাল অ্যাকুরেসি মেপেছিলেন। নিডল ফ্যাক্ট মানে বেছে নেওয়া জায়গায় লুকিয়ে রাখা একটি তথ্য, মডেল সেটি খুঁজে পায় কি না তা পরীক্ষা করতে।"),
        ("The result is a U-shaped curve: recall is high at the start, collapses in the middle, and recovers at the end.",
         "ফল একটি ইউ-আকৃতির কার্ভ: শুরুতে রিকল উঁচু, মাঝখানে ধস, শেষে আবার উঠে আসে।")],
       [sh("start", "hot"), sh("mid", "warn"), sh("end", "hot"), sh("needle", "hot", ("hidden in the text", "লেখার ভেতরে লুকানো"))],
       [ln("needle", "start", "to", state="hot"), ln("needle", "mid", "to", state="warn"), ln("needle", "end", "to", state="hot")],
       [HIGH, LOW, HIGH, None]),

    st(("Longer", "লম্বা"),
       ("Longer and weaker is worse", "যত লম্বা আর দুর্বল, তত খারাপ"),
       [("The effect is worse for longer contexts and weaker models. The longer the context, the worse the middle.",
         "কনটেক্সট যত লম্বা বা মডেল যত দুর্বল, মাঝের সমস্যা তত বেশি।"),
        ("But it persists even in frontier models with 100K+ context windows.",
         "তবে ১০০K+ কনটেক্সটের ফ্রন্টিয়ার মডেলেও এটি থেকে যায়।")],
       [sh("start", "hot"), sh("mid", "warn", ("worse when long", "লম্বা হলে আরও খারাপ")), sh("end", "hot"),
        sh("model", "hot", ("100K+ window", "১০০K+ উইন্ডো"))],
       fan("warn"),
       [HIGH, LOW, HIGH, ("100K+", "১০০K+")]),

    st(("Why", "কেন"),
       ("Why it happens", "কেন এমন হয়"),
       [("Attention is biased by position. Long-context extensions such as RoPE, ALiBi and YaRN help, but do not fully fix it.",
         "অ্যাটেনশনে অবস্থানগত পক্ষপাত আছে; RoPE, ALiBi, YaRN-এর মতো লং-কনটেক্সট এক্সটেনশন সাহায্য করলেও পুরো সমাধান করে না।"),
        ("Most pre-training data had shorter contexts, so models never learned to join information across long distances. And models weight the first and last positions more heavily, a bias humans have too.",
         "প্রিট্রেনিং ডেটায় বেশিরভাগ কনটেক্সট ছোট ছিল, তাই মডেল দূরের তথ্য জোড়া দিতে শেখেনি। আর মডেল প্রথম ও শেষ অবস্থানকে বেশি গুরুত্ব দেয়, যে প্রবণতা মানুষের মধ্যেও দেখা যায়।")],
       [sh("attn", "hot", ("biased by position", "অবস্থানে পক্ষপাত")), sh("pretrain", "hot", ("mostly short texts", "বেশিরভাগ ছোট কনটেক্সট")),
        sh("bias", "hot", ("first and last", "প্রথম ও শেষ")), sh("mid", "warn", ("gets missed", "বাদ পড়ে"))],
       [ln("attn", "mid", "to", state="hot"), ln("pretrain", "mid", "to", state="hot"), ln("bias", "mid", "to", state="hot")],
       [None, LOW, None, None]),

    st(("Ends", "প্রান্ত"),
       ("Put it at the ends", "রাখুন দুই প্রান্তে"),
       [("Sandwich it: put the key content at the start of the prompt and repeat it at the end. That hits both attention peaks.",
         "স্যান্ডউইচ করুন: জরুরি অংশ প্রম্পটের শুরুতে রাখুন আর শেষে আবার বলুন। এতে অ্যাটেনশনের দুই চূড়াই ধরা যায়।"),
        ("Re-order documents: if you retrieved 10 documents, put the most relevant at the start and the end, and the least relevant in the middle.",
         "ডকুমেন্ট নতুন করে সাজান: ১০টি ডকুমেন্ট পেলে সবচেয়ে প্রাসঙ্গিকগুলো শুরুতে ও শেষে রাখুন, কম প্রাসঙ্গিকগুলো মাঝখানে।")],
       [sh("start", "hot", ("key content", "জরুরি অংশ")), sh("mid", "dim", ("least relevant", "কম প্রাসঙ্গিক")),
        sh("end", "hot", ("repeated", "আবার বলা")), sh("model", "hot")],
       fan("dim", ()),
       [None, None, None, None],
       changes=[("+", "The key content appears at both ends", "জরুরি অংশ দুই প্রান্তেই থাকে")]),

    st(("Shorter", "ছোট"),
       ("Cut it shorter, and mark it", "ছোট করুন, আর চিহ্নিত করুন"),
       [("Shorter context gives better recall. If it fits in 8K tokens, do not use 50K.",
         "ছোট কনটেক্সটে রিকল ভালো। ৮K টোকেনে আঁটলে ৫০K ব্যবহার করবেন না।"),
        ("Mark the important part: wrap critical information in <code>&lt;important&gt;</code> tags. Strong models pay attention to marked regions.",
         "জরুরি অংশ চিহ্নিত করুন: জরুরি তথ্য <code>&lt;important&gt;</code> ট্যাগে মুড়ুন। শক্তিশালী মডেল চিহ্নিত অংশে মনোযোগ দেয়।")],
       [sh("start", "dim"), sh("mid", "hot", ("marked", "চিহ্নিত")), sh("end", "dim"), sh("model", "hot", ("shorter input", "ছোট ইনপুট"))],
       fan("hot", ("start", "end")),
       [None, None, None, ("8K tokens", "৮K টোকেন")],
       changes=[("-", "A prompt of 50K tokens shrinks to 8K", "৫০K টোকেনের প্রম্পট ছোট হয়ে ৮K হয়"),
                ("+", "The critical part is wrapped in tags", "জরুরি অংশ ট্যাগে মোড়া")]),

    st(("Again", "আবার"),
       ("Look again, and point back", "আবার দেখুন, পেছনে তাকান"),
       [("Re-query when unsure: if the model does not find the answer in one pass, ask it to look again with what it learned. Two short passes beat one long one.",
         "অনিশ্চিত হলে আবার কুয়েরি করুন: এক চেষ্টায় উত্তর না পেলে, যা শিখেছে তা নিয়ে আবার দেখতে বলুন। দুটো ছোট কুয়েরি একটি লম্বা কুয়েরির চেয়ে ভালো।"),
        ("Add an “answer here” marker: end the prompt with “based on the above, your answer:”. This nudges the model to look back over the whole context once more before it responds.",
         "“উত্তর এখানে” মার্কার দিন: প্রম্পট শেষ করুন “based on the above, your answer:” দিয়ে। এতে মডেল উত্তরের আগে পুরো কনটেক্সটে আরেকবার চোখ বোলায়।")],
       [sh("start", "dim"), sh("mid", "dim"), sh("end", "hot", ("your answer:", "your answer:")), sh("model", "hot", ("looks back", "পেছনে তাকায়"))],
       fan("dim", ("start", "mid")),
       [None, None, None, None]),

    st(("Later", "পরে"),
       ("Later work: better, never gone", "পরের গবেষণা: ভালো, তবু যায়নি"),
       [("Follow-up work (RULER, Summary-of-a-Haystack and BABILong, all in 2024) refined the picture. The U-curve flattens with better models and longer-context training, but never fully goes away.",
         "পরের গবেষণা (RULER, Summary-of-a-Haystack, BABILong, ২০২৪) ছবিটি আরও পরিষ্কার করেছে। ভালো মডেল আর লম্বা-কনটেক্সট ট্রেনিংয়ে ইউ-কার্ভ চ্যাপ্টা হয়, কিন্তু পুরোপুরি যায় না।"),
        ("Variable-length tasks are harder than fixed-length ones, and multi-hop reasoning across long contexts is still an open problem. RAG and long context are complementary, not redundant.",
         "পরিবর্তনশীল দৈর্ঘ্যের কাজ নির্দিষ্ট দৈর্ঘ্যের কাজের চেয়ে কঠিন, আর দীর্ঘ কনটেক্সট জুড়ে মাল্টি-হপ রিজনিং এখনও খোলা সমস্যা। RAG আর লং-কনটেক্সট একে অপরের পরিপূরক।")],
       [sh("start", "hot"), sh("mid", "warn", ("flatter, not gone", "চ্যাপ্টা, তবু আছে")), sh("end", "hot"), sh("model", "hot", ("better models", "ভালো মডেল"))],
       fan("warn"),
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("If neither works, the model genuinely cannot handle that fact. Use a smaller context, external retrieval, or a different architecture.",
         "তাতেও না হলে মডেল সত্যিই সেই তথ্য সামলাতে পারছে না। ছোট কনটেক্সট, এক্সটার্নাল রিট্রিভাল বা ভিন্ন আর্কিটেকচার ব্যবহার করুন।")],
       [sh("start"), sh("mid"), sh("end"), sh("model")],
       [ln("start", "model", "to"), ln("mid", "model", "to"), ln("end", "model", "to")],
       [None, None, None, None],
       points=[("Put facts that must be recalled in the first 10% or the last 10% of the context.",
                "যে তথ্য মনে রাখাতে চান, তা কনটেক্সটের প্রথম ১০% বা শেষ ১০%-এ রাখুন।"),
               ("If you cannot, repeat them at both ends. Sandwich the key content.",
                "না পারলে দুই প্রান্তেই পুনরাবৃত্তি করুন। জরুরি অংশ স্যান্ডউইচ করুন।"),
               ("Shorter context gives better recall. If it fits in 8K, do not use 50K.",
                "ছোট কনটেক্সটে রিকল ভালো। ৮K-তে আঁটলে ৫০K ব্যবহার করবেন না।"),
               ("Better models flatten the U-shape, but it never fully goes away.",
                "ভালো মডেলে ইউ-আকৃতি চ্যাপ্টা হয়, কিন্তু পুরোপুরি যায় না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
