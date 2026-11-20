"""Part 11 · 01 Cost & performance optimization: three knobs that cut an LLM bill without losing quality.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Knobs     Start here: "LLM bills grow with usage. Three ideas cut the cost by 5–50× without losing quality: send easy work to cheap models, reuse past work, and shrink what you send or use a smaller model."
  2 Cascade   Body, "Model cascading": "Route easy requests to a small, cheap model; only escalate to a large, expensive one when the small model's confidence is low (use logprobs, self-critique, or a separate classifier). A well-tuned cascade often reaches frontier quality at 30–70% of the cost."
  3 Cache     Body, "Caching": "Caching is the single most powerful cost lever. Three kinds:" semantic cache (cosine > 0.95), output cache, prompt cache ("80–90% discount on cached prefix").
  4 Batch     Body, "Batch APIs": "OpenAI's /v1/batches, Google Batch, Together batch — submit a JSONL file, get results within 24h, at half the cost. Use for: nightly evals, bulk labelling, backfills, anything that doesn't need an answer in the next 5 seconds."
  5 Distill   Body, "Distillation": "Take 50,000 (prompt, big_model_answer) pairs from production (with consent), fine-tune a small open model on them. ... a well-distilled 7B beats an un-distilled 12B on reasoning benchmarks. Distillation is the only technique that simultaneously cuts cost and latency and unlocks self-hosting."
  6 Compress  Body, "Prompt compression": "Tools like LLMLingua remove stopwords, paraphrase verbose passages, and drop low-information tokens — often 5–20× compression with <3% quality hit. Particularly powerful for long RAG contexts where most chunks are filler."
  7 Budget    Body, "Token budgeting per feature": "Allocate a monthly token budget per feature, alert at 80%, throttle at 100%. This is the operational layer that prevents one runaway feature from blowing the company's bill."
  8 Gateway   Body, "Model gateways": "A model gateway sits between your app and every LLM provider. It gives you: one API for OpenAI + Anthropic + Together + your own vLLM; per-key rate limits; cost tracking; retries; fallbacks; semantic caching out of the box. The three major options are LiteLLM (Python proxy), Portkey (production-grade SaaS), and OpenRouter (consumer-grade aggregator)."
  9 Remember  The sub-title ("Three knobs ... cascade, cache, and compress"), and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("app", "server", ("App", "অ্যাপ"), 110, 162),
    node("prompt", "note", ("Long prompt", "লম্বা প্রম্পট"), 110, 162),
    node("small", "model", ("Small model", "ছোট মডেল"), 380, 162),
    node("cache", "cache", ("Cache", "ক্যাশ"), 380, 162),
    node("batch", "queue", ("Batch file", "ব্যাচ ফাইল"), 380, 162),
    node("squeeze", "tool", ("Compressor", "কম্প্রেসর"), 380, 250),
    node("budget", "chart", ("Token budget", "টোকেন বাজেট"), 380, 162),
    node("gateway", "balancer", ("Gateway", "গেটওয়ে"), 380, 162),
    node("big", "model", ("Large model", "বড় মডেল"), 650, 162),
]

METRICS = [
    ("Cost", "খরচ"),
    ("Quality", "মান"),
    ("Prompt", "প্রম্পট"),
]

CAPTION = (
    "LLM bills scale with usage. Three knobs cut the cost without losing quality: cascade, cache, and compress.",
    "LLM-এর বিল ব্যবহারের সাথে বাড়ে। তিনটি উপায়ে মান না হারিয়ে খরচ কমে: ক্যাসকেড, ক্যাশ আর কম্প্রেস।",
)

STEPS = [
    st(("Knobs", "উপায়"),
       ("Three knobs for the bill", "বিল কমানোর তিন উপায়"),
       [("LLM bills grow with usage. Three ideas cut the cost by 5–50× without losing quality: send easy work to cheap models, reuse past work, and shrink what you send or use a smaller model.",
         "LLM-এর বিল ব্যবহারের সাথে বাড়ে। তিনটি উপায়ে মান না হারিয়ে খরচ ৫–৫০× কমানো যায়: সহজ কাজ সস্তা মডেলে পাঠান, আগের কাজ আবার ব্যবহার করুন, আর যা পাঠান তা ছোট করুন বা ছোট মডেল ব্যবহার করুন।")],
       [sh("app"), sh("small", "hot", ("send easy work here", "সহজ কাজ এখানে"), y=75), sh("cache", "hot", ("reuse past work", "আগের কাজ আবার")),
        sh("squeeze", "hot", ("shrink what you send", "যা পাঠান তা ছোট"))],
       [ln("app", "small", "to", state="hot"), ln("app", "cache", "to", state="hot"), ln("app", "squeeze", "to", state="hot")],
       [("5–50× less", "৫–৫০× কম"), ("kept", "বজায় থাকে"), None]),

    st(("Cascade", "ক্যাসকেড"),
       ("Cheap first, expensive only if needed", "আগে সস্তা, দরকারে দামি"),
       [("Route easy requests to a small, cheap model. Only escalate to a large, expensive one when the small model's confidence is low.",
         "সহজ অনুরোধ ছোট, সস্তা মডেলে পাঠান। ছোট মডেলের আত্মবিশ্বাস কম হলেই কেবল বড়, দামি মডেলে নিন।"),
        ("A well-tuned cascade often reaches frontier quality at 30–70% of the cost.",
         "ভালোভাবে সাজানো ক্যাসকেড প্রায়ই খরচের ৩০–৭০%-এ সেরা মানে পৌঁছায়।")],
       [sh("app"), sh("small", "hot", ("tries first", "আগে চেষ্টা করে")), sh("big", "hot", ("if not confident", "নিশ্চিত না হলে"))],
       [ln("app", "small", "to", state="hot"), ln("small", "big", "to", state="hot")],
       [("30–70% of it", "এর ৩০–৭০%"), ("frontier", "সেরা মান"), None],
       note=("tip",
             "To tell how confident the small model is, use logprobs, self-critique, or a separate classifier.",
             "ছোট মডেল কতটা নিশ্চিত তা বুঝতে logprobs, সেলফ-ক্রিটিক বা আলাদা একটি ক্লাসিফায়ার ব্যবহার করুন।")),

    st(("Cache", "ক্যাশ"),
       ("Caching: the biggest lever", "ক্যাশিং: সবচেয়ে বড় উপায়"),
       [("Caching is the single most powerful cost lever. Three kinds:",
         "ক্যাশিংই খরচ কমানোর সবচেয়ে শক্তিশালী উপায়। তিন ধরন:")],
       [sh("app"), sh("cache", "hot", ("saved answers", "জমানো উত্তর")), sh("big", None, ("only on a miss", "না মিললে তবেই"))],
       [ln("app", "cache", "to", state="hot"), ln("cache", "big", "to")],
       [None, None, None],
       changes=[("+", "Semantic cache: if a near-identical prompt was answered recently (cosine above 0.95), return the cached answer.",
                 "সেম্যান্টিক ক্যাশ: প্রায় একই প্রম্পটের উত্তর সম্প্রতি দেওয়া হলে (কোসাইন ০.৯৫-এর বেশি) জমানো উত্তর ফেরত দিন।"),
                ("+", "Output cache: for deterministic tasks (extraction, classification with <code>temperature=0</code>), a key-value cache keyed on the input.",
                 "আউটপুট ক্যাশ: নির্ধারিত কাজে (এক্সট্র্যাকশন, <code>temperature=0</code> দিয়ে ক্লাসিফিকেশন) ইনপুট ধরে কী-ভ্যালু ক্যাশ।"),
                ("+", "Prompt cache: provider-level, it reuses the KV of the system prompt across calls, with an 80–90% discount on the cached prefix.",
                 "প্রম্পট ক্যাশ: প্রোভাইডার-স্তরের; কলের পর কলে সিস্টেম প্রম্পটের KV আবার ব্যবহার করে, ক্যাশ করা প্রিফিক্সে ৮০–৯০% ছাড়।")]),

    st(("Batch", "ব্যাচ"),
       ("Batch APIs for work that can wait", "যে কাজ অপেক্ষা করতে পারে তার ব্যাচ API"),
       [("OpenAI's <code>/v1/batches</code>, Google Batch, and Together batch let you submit a JSONL file and get results within 24h, at half the cost.",
         "OpenAI-র <code>/v1/batches</code>, Google Batch আর Together batch-এ একটি JSONL ফাইল জমা দিলে ২৪ ঘণ্টার মধ্যে অর্ধেক খরচে ফল পাওয়া যায়।"),
        ("Use them for nightly evals, bulk labeling, backfills, and anything that doesn't need an answer in the next 5 seconds.",
         "রাতের ইভ্যাল, বাল্ক লেবেলিং, ব্যাকফিল আর যে কাজে পরের ৫ সেকেন্ডের মধ্যে উত্তর লাগে না, তার জন্য এগুলো ব্যবহার করুন।")],
       [sh("app"), sh("batch", "hot", ("one JSONL file", "একটি JSONL ফাইল")), sh("big", "hot", ("results in 24h", "২৪ ঘণ্টায় ফল"))],
       [ln("app", "batch", "to", state="hot"), ln("batch", "big", "to", state="hot")],
       [("half", "অর্ধেক"), None, None]),

    st(("Distill", "ডিস্টিল"),
       ("Distillation: a small model from a big one", "ডিস্টিলেশন: বড় মডেল থেকে ছোট মডেল"),
       [("Take 50,000 <code>(prompt, big_model_answer)</code> pairs from production (with consent) and fine-tune a small open model on them.",
         "প্রোডাকশন থেকে (সম্মতি নিয়ে) ৫০,০০০ <code>(prompt, big_model_answer)</code> জোড়া নিন আর একটি ছোট ওপেন মডেলকে সেগুলো দিয়ে ফাইন-টিউন করুন।"),
        ("Distillation is the only technique that simultaneously cuts cost and latency and unlocks self-hosting.",
         "ডিস্টিলেশনই একমাত্র কৌশল, যা একসাথে খরচ ও ল্যাটেন্সি কমায় আর সেলফ-হোস্টিংয়ের পথ খুলে দেয়।")],
       [sh("big", "hot", ("50,000 answers", "৫০,০০০ উত্তর"), x=110), sh("small", "hot", ("fine-tuned on them", "এগুলোতে ফাইন-টিউন"))],
       [ln("big", "small", "to", state="hot")],
       [None, None, None],
       note=("insight",
             "DeepSeek-R1's “distilled Qwen” line showed that a well-distilled 7B beats an un-distilled 12B on reasoning benchmarks.",
             "DeepSeek-R1-এর “distilled Qwen” লাইন দেখিয়েছে, ভালোভাবে ডিস্টিল করা একটি 7B রিজনিং বেঞ্চমার্কে ডিস্টিল না করা 12B-কে ছাড়িয়ে যায়।")),

    st(("Compress", "কম্প্রেস"),
       ("Prompt compression", "প্রম্পট কম্প্রেশন"),
       [("Tools like LLMLingua remove stopwords, paraphrase verbose passages, and drop low-information tokens: often 5–20× compression with under 3% quality loss.",
         "LLMLingua-র মতো টুল স্টপওয়ার্ড বাদ দেয়, বিস্তারিত অংশ সংক্ষেপে বলে, আর কম তথ্যের টোকেন ফেলে দেয়: প্রায়ই ৫–২০× কম্প্রেশন, মান কমে ৩%-এরও কম।"),
        ("This is particularly powerful for long RAG contexts, where most chunks are filler.",
         "লম্বা RAG কনটেক্সটে এটি বিশেষভাবে কাজের, যেখানে বেশিরভাগ অংশই ফিলার।")],
       [sh("prompt", "hot", ("full of filler", "ফিলারে ভরা")), sh("squeeze", "hot", ("LLMLingua-style", "LLMLingua-ধাঁচের"), y=162),
        sh("big", "hot", ("gets the short one", "ছোটটি পায়"))],
       [ln("prompt", "squeeze", "to", state="hot"), ln("squeeze", "big", "to", state="hot")],
       [None, ("under 3% loss", "৩%-এরও কম ক্ষতি"), ("5–20× smaller", "৫–২০× ছোট")]),

    st(("Budget", "বাজেট"),
       ("A token budget per feature", "প্রতিটি ফিচারের টোকেন বাজেট"),
       [("Allocate a monthly token budget per feature, alert at 80%, throttle at 100%.",
         "প্রতিটি ফিচারের জন্য মাসিক টোকেন বাজেট দিন: ৮০%-এ সতর্কতা, ১০০%-এ থ্রটল।"),
        ("This is the operational layer that prevents one runaway feature from blowing the company's bill.",
         "এটিই সেই অপারেশনাল স্তর, যা একটি বেপরোয়া ফিচারকে কোম্পানির বিল ফুলিয়ে ফেলতে দেয় না।")],
       [sh("app", "hot", ("one feature", "একটি ফিচার")), sh("budget", "hot", ("alert at 80%", "৮০%-এ সতর্কতা")), sh("big", "hot", ("throttled at 100%", "১০০%-এ থ্রটল"))],
       [ln("app", "budget", "to", state="hot"), ln("budget", "big", "to", state="hot")],
       [None, None, None]),

    st(("Gateway", "গেটওয়ে"),
       ("A model gateway", "মডেল গেটওয়ে"),
       [("A model gateway sits between your app and every LLM provider. It gives you one API for OpenAI, Anthropic, Together, and your own vLLM, plus per-key rate limits, cost tracking, retries, fallbacks, and semantic caching out of the box.",
         "মডেল গেটওয়ে আপনার অ্যাপ আর প্রতিটি LLM প্রোভাইডারের মাঝে বসে। এটি দেয় OpenAI, Anthropic, Together আর আপনার নিজের vLLM-এর জন্য একটি API, সঙ্গে প্রতি-কী রেট লিমিট, খরচের হিসাব, রিট্রাই, ফলব্যাক আর রেডিমেড সেম্যান্টিক ক্যাশিং।")],
       [sh("app"), sh("gateway", "hot", ("one API", "একটি API")), sh("big", "hot", ("OpenAI, Anthropic", "OpenAI, Anthropic"), y=75),
        sh("small", "hot", ("your own vLLM", "আপনার নিজের vLLM"), x=650, y=250)],
       [ln("app", "gateway", "to", state="hot"), ln("gateway", "big", "to", state="hot"), ln("gateway", "small", "to", state="hot")],
       [None, None, None],
       note=("tip",
             "The three major options are LiteLLM (a Python proxy), Portkey (a production-grade SaaS), and OpenRouter (a consumer-grade aggregator).",
             "তিনটি প্রধান বিকল্প হলো LiteLLM (Python প্রক্সি), Portkey (প্রোডাকশন-মানের SaaS) আর OpenRouter (কনজিউমার-মানের অ্যাগ্রিগেটর)।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Cascade, cache, and compress are the three knobs that cut the cost without losing quality.",
         "ক্যাসকেড, ক্যাশ আর কম্প্রেস: মান না হারিয়ে খরচ কমানোর তিনটি উপায়।")],
       [sh("app"), sh("cache", None, None, None, 380, 75), sh("small", None, None, None, 380, 250), sh("big")],
       [ln("app", "cache", "to"), ln("cache", "big", "to"), ln("app", "small", "to"), ln("small", "big", "to")],
       [None, None, None],
       points=[("A well-tuned cascade often reaches top quality at 30–70% of the cost.",
                "ভালোভাবে সাজানো ক্যাসকেড প্রায়ই খরচের ৩০–৭০%-এ সেরা মানে পৌঁছায়।"),
               ("Caching is the single most powerful cost lever.",
                "ক্যাশিংই খরচ কমানোর সবচেয়ে শক্তিশালী উপায়।"),
               ("Batch APIs give half price for work that can wait up to 24h.",
                "যে কাজ ২৪ ঘণ্টা অপেক্ষা করতে পারে, ব্যাচ API-তে তার দাম অর্ধেক।"),
               ("Give each feature a monthly token budget: alert at 80%, throttle at 100%.",
                "প্রতিটি ফিচারের জন্য মাসিক টোকেন বাজেট রাখুন: ৮০%-এ সতর্কতা, ১০০%-এ থ্রটল।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
