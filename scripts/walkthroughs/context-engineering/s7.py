"""Part 4 · 07 Lost in the Middle & mitigation: models recall the start and end of a long input, and miss the middle.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Finding   Start here: "Models remember the start and end of a long input well, but they often miss facts in the middle. This is Lost in the Middle, and it changes how you should arrange a prompt."
  2 Test      Body, the evidence: "Liu et al. varied the position of the relevant information in multi-document question answering and key-value retrieval tasks, and measured accuracy. Result: U-shaped performance curve — accuracy is high at the start, drops in the middle, recovers at the end."
              Needle fact ("A single fact hidden at a chosen spot in a long text, used to test whether the model can find it."); U-shaped curve ("A graph that is high at the start, low in the middle, and high again at the end.").
  3 Longer    Sub-title: "The longer the context, the worse the middle."; body: "The effect appeared in both standard and extended-context models (e.g. Claude-1.3 100K), and extended-context models were not necessarily better at using their input."
  4 Why       Body, "Why does it happen?": attention is biased by position (RoPE, ALiBi, YaRN "help but don't fully fix it"); the training distribution ("Most pre-training data has shorter contexts"); "Positional primacy & recency ... the same bias that affects humans."
  5 Ends      Layman's voice, ways 1 and 2: "Sandwich it: put the most important stuff at the very top of your prompt AND repeat it at the very bottom. Hit both attention peaks." "Re-order documents: if you retrieved 10 documents, put the most relevant at the start or the end, the least relevant in the middle."
  6 Shorter   Layman's voice, ways 3 and 4: "Cut shorter: shorter prompts = better recall. If you can fit it in 8K tokens, don't use 50K (a rule of thumb)." "Mark the important: wrap critical info in <important>…</important> tags. This keeps the prompt organised, but it is not proven to fix the middle problem."
  7 Again     Layman's voice, ways 5 and 6: "Re-query when unsure: if the AI doesn't find the answer in one pass, ask it to look again with what it learned." "Ask the question twice: put your question before the documents and again after them. In the paper this helped a lot on key-value lookups, and little on multi-document Q&amp;A."
  8 Later     Body, "The empirical reality check": "Follow-up work (RULER, 2024; Summary-of-a-Haystack, 2024; BABILong, 2024) refined the picture: Almost all models show large performance drops as context length grows (RULER). Summary of a Haystack can also be used to study position bias in long-context models. Multi-hop reasoning across long contexts remains an open problem. BABILong reports that popular LLMs effectively use only 10–20% of their context."
  9 Remember  The practical rule ("Rule of thumb (the author's heuristic, not from a paper): ... If neither works, the model may not handle that fact — use a smaller context, or external retrieval, or a different architecture.") and the four "remember" points of the Start here box.

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
       ("The position test", "অবস্থানের পরীক্ষা"),
       [("Liu et al. (2023) varied the position of the relevant information in multi-document question answering and key-value retrieval tasks, and measured accuracy. A needle fact is a single fact hidden at a chosen spot in a long text, used to test whether the model can find it.",
         "Liu et al. (২০২৩) মাল্টি-ডকুমেন্ট প্রশ্নোত্তর ও কি-ভ্যালু রিট্রিভাল কাজে প্রাসঙ্গিক তথ্যের অবস্থান বদলে অ্যাকুরেসি মেপেছিলেন। নিডল ফ্যাক্ট মানে লম্বা লেখার বেছে নেওয়া জায়গায় লুকিয়ে রাখা একটি তথ্য, মডেল সেটি খুঁজে পায় কি না তা পরীক্ষা করতে লাগে।"),
        ("The result is a U-shaped curve: accuracy is high at the start, drops in the middle, and recovers at the end.",
         "ফল একটি ইউ-আকৃতির কার্ভ: শুরুতে অ্যাকুরেসি উঁচু, মাঝখানে নিচু, শেষে আবার উঠে আসে।")],
       [sh("start", "hot"), sh("mid", "warn"), sh("end", "hot"), sh("needle", "hot", ("position varied", "অবস্থান বদলানো"))],
       [ln("needle", "start", "to", state="hot"), ln("needle", "mid", "to", state="warn"), ln("needle", "end", "to", state="hot")],
       [HIGH, LOW, HIGH, None]),

    st(("Longer", "লম্বা"),
       ("Longer context, worse middle", "কনটেক্সট যত লম্বা, মাঝখান তত খারাপ"),
       [("The longer the context, the worse the middle.",
         "কনটেক্সট যত লম্বা, মাঝখানের অবস্থা তত খারাপ।"),
        ("The effect appeared in both standard and extended-context models (e.g. Claude-1.3 100K), and extended-context models were not necessarily better at using their input.",
         "এই প্রভাব সাধারণ ও এক্সটেন্ডেড-কনটেক্সট (যেমন Claude-1.3 100K) দুই ধরনের মডেলেই দেখা গেছে; এক্সটেন্ডেড-কনটেক্সট মডেল ইনপুট কাজে লাগাতে সবসময় ভালো নয়।")],
       [sh("start", "hot"), sh("mid", "warn", ("worse when long", "লম্বা হলে আরও খারাপ")), sh("end", "hot"),
        sh("model", "hot", ("extended context", "এক্সটেন্ডেড কনটেক্সট"))],
       fan("warn"),
       [HIGH, LOW, HIGH, ("100K", "১০০K")]),

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
        ("Re-order documents: if you retrieved 10 documents, put the most relevant at the start or the end, and the least relevant in the middle.",
         "ডকুমেন্ট নতুন করে সাজান: ১০টি ডকুমেন্ট পেলে সবচেয়ে প্রাসঙ্গিকগুলো শুরুতে বা শেষে রাখুন, কম প্রাসঙ্গিকগুলো মাঝখানে।")],
       [sh("start", "hot", ("key content", "জরুরি অংশ")), sh("mid", "dim", ("least relevant", "কম প্রাসঙ্গিক")),
        sh("end", "hot", ("repeated", "আবার বলা")), sh("model", "hot")],
       fan("dim", ()),
       [None, None, None, None],
       changes=[("+", "The key content appears at both ends", "জরুরি অংশ দুই প্রান্তেই থাকে")]),

    st(("Shorter", "ছোট"),
       ("Cut it shorter, and mark it", "ছোট করুন, আর চিহ্নিত করুন"),
       [("Shorter context usually helps recall. Rule of thumb: if it fits in 8K tokens, do not use 50K.",
         "ছোট কনটেক্সটে সাধারণত রিকল ভালো। অভিজ্ঞতালব্ধ নিয়ম: ৮K টোকেনে আঁটলে ৫০K ব্যবহার করবেন না।"),
        ("Mark the important part: wrap critical information in <code>&lt;important&gt;</code> tags. This keeps the prompt organised, but it is not proven to fix the middle problem.",
         "জরুরি অংশ চিহ্নিত করুন: জরুরি তথ্য <code>&lt;important&gt;</code> ট্যাগে মুড়ুন। এতে প্রম্পট গোছানো থাকে, তবে এটি মাঝের সমস্যা মেটায়, এমন প্রমাণ নেই।")],
       [sh("start", "dim"), sh("mid", "hot", ("marked", "চিহ্নিত")), sh("end", "dim"), sh("model", "hot", ("shorter input", "ছোট ইনপুট"))],
       fan("hot", ("start", "end")),
       [None, None, None, ("8K tokens", "৮K টোকেন")],
       changes=[("-", "Rule of thumb: 8K tokens instead of 50K", "অভিজ্ঞতালব্ধ নিয়ম: ৫০K টোকেনের বদলে ৮K"),
                ("+", "The critical part is wrapped in tags, which keeps the prompt organised", "জরুরি অংশ ট্যাগে মোড়া, এতে প্রম্পট গোছানো থাকে")]),

    st(("Again", "আবার"),
       ("Look again, and ask twice", "আবার দেখুন, প্রশ্ন দুবার করুন"),
       [("Re-query when unsure: if the AI does not find the answer in one pass, ask it to look again with what it learned.",
         "অনিশ্চিত হলে আবার কুয়েরি করুন: এক চেষ্টায় উত্তর না পেলে আংশিক উত্তর নিয়ে আবার কুয়েরি করুন।"),
        ("Ask the question twice: put your question before the documents and again after them. In the paper this helped a lot on key-value lookups, and little on multi-document Q&amp;A.",
         "প্রশ্ন দুইবার করুন: ডকুমেন্টের আগে ও পরে দুই জায়গাতেই প্রশ্ন রাখুন। গবেষণাপত্রে এতে কি-ভ্যালু লুকআপে বড় উন্নতি হয়েছে, কিন্তু মাল্টি-ডকুমেন্ট QA-তে প্রভাব সামান্য।")],
       [sh("start", "hot", ("question", "প্রশ্ন")), sh("mid", "dim", ("documents", "ডকুমেন্ট")), sh("end", "hot", ("question again", "আবার প্রশ্ন")), sh("model", "hot", ("looks again", "আবার দেখে"))],
       fan("dim", ("mid",)),
       [None, None, None, None]),

    st(("Later", "পরে"),
       ("Later work: big drops with length", "পরের গবেষণা: দৈর্ঘ্যে বড় পতন"),
       [("Follow-up work (RULER, Summary-of-a-Haystack and BABILong, all in 2024) refined the picture. Almost all models show large performance drops as context length grows (RULER).",
         "পরের গবেষণা (RULER, Summary-of-a-Haystack, BABILong, ২০২৪) ছবিটি আরও পরিষ্কার করেছে। প্রায় সব মডেলেই কনটেক্সট লম্বা হলে পারফরম্যান্স বড়ভাবে কমে (RULER)।"),
        ("Summary of a Haystack can also be used to study position bias in long-context models. Multi-hop reasoning across long contexts remains an open problem. BABILong reports that popular LLMs effectively use only 10–20% of their context.",
         "Summary of a Haystack দিয়ে লং-কনটেক্সট মডেলের পজিশন বায়াসও পরীক্ষা করা যায়। দীর্ঘ কনটেক্সট জুড়ে মাল্টি-হপ রিজনিং এখনও খোলা সমস্যা। BABILong বলছে, জনপ্রিয় LLM-গুলো তাদের কনটেক্সটের মাত্র ১০–২০% কার্যকরভাবে কাজে লাগায়।")],
       [sh("start", "hot"), sh("mid", "warn", ("large drops", "বড় পতন")), sh("end", "hot"), sh("model", "hot", ("long context", "দীর্ঘ কনটেক্সট"))],
       fan("warn"),
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Rule of thumb (the author's heuristic, not from a paper): if neither works, the model may not handle that fact. Use a smaller context, external retrieval, or a different architecture.",
         "অভিজ্ঞতালব্ধ নিয়ম (লেখকের নিজস্ব হিউরিস্টিক, গবেষণাপত্রের নয়): তাতেও না হলে ছোট কনটেক্সট, এক্সটার্নাল রিট্রিভাল বা ভিন্ন আর্কিটেকচার ব্যবহার করুন।")],
       [sh("start"), sh("mid"), sh("end"), sh("model")],
       [ln("start", "model", "to"), ln("mid", "model", "to"), ln("end", "model", "to")],
       [None, None, None, None],
       points=[("Rule of thumb: put facts that must be recalled in the first 10% or the last 10% of the context.",
                "অভিজ্ঞতালব্ধ নিয়ম: যে তথ্য মনে রাখাতে চান, তা কনটেক্সটের প্রথম ১০% বা শেষ ১০%-এ রাখুন।"),
               ("If you cannot, repeat them at both ends. Sandwich the key content.",
                "না পারলে দুই প্রান্তেই পুনরাবৃত্তি করুন। জরুরি অংশ স্যান্ডউইচ করুন।"),
               ("Shorter context usually helps recall. Rule of thumb: if it fits in 8K, do not use 50K.",
                "ছোট কনটেক্সটে সাধারণত রিকল ভালো। অভিজ্ঞতালব্ধ নিয়ম: ৮K-তে আঁটলে ৫০K ব্যবহার করবেন না।"),
               ("Do not assume a bigger model removes the U-shape. Test your own prompts.",
                "বড় মডেল হলেই ইউ-আকৃতি চলে যাবে, ধরে নেবেন না। নিজের প্রম্পটে পরীক্ষা করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
