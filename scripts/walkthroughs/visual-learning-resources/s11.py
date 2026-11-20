"""Part 15 · 07 Attention variants in numbers: KV cache size, sliding windows and hybrids.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Growth     Start here: "The KV cache can grow to many gigabytes for long inputs. This section shows the numbers, how sharing or compressing keys and values shrinks it, and how cheaper attention cuts compute."; "KV cache = The keys and values the model stores for every earlier token, for every layer, so it does not recompute them."
  2 Counting   Body, "The KV cache, in numbers": "Take a model shaped like Llama 3 8B: 32 layers, 32 query heads, head size 128, FP16 (2 bytes per number). For each token and layer, the cache holds one K and one V for each KV head." and the formula.
  3 MHA        The table: "MHA | 32 | 512 KiB | 64 GiB".
  4 GQA        The table: "GQA (Llama 3 8B uses 8) | 8 | 128 KiB | 16 GiB"; Start here: "Several query heads share one KV head".
  5 MQA        The table: "MQA | 1 | 16 KiB | 2 GiB"; Start here: "The extreme case where all query heads share just 1 KV head. It has the smallest cache."
  6 MLA        Body: "MLA goes further than GQA. The DeepSeek-V2 paper reports a KV cache that is 93.3% smaller than that of its earlier dense model, DeepSeek 67B."; Start here: "storing one compressed form and rebuilding the keys and values."
  7 Window     Body, "Cheaper attention": "Sliding window: a token reads only the last w tokens. Gemma 3 uses five local layers for each global layer, with a window of 1,024 tokens. The guide notes that its ablation shows only a small loss in quality."
  8 Sparse     Same part: "DeepSeek sparse attention ..." and "Hybrid: most layers use a linear or state-space mixer that costs little at long length. Every few layers, a full-attention layer restores exact lookup. Qwen3-Next uses a 3 : 1 mix."
  9 Remember   "Know the limit" callout, and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("tok", "note", ("Token", "টোকেন"), 110, 162),
    node("q", "model", ("Query heads", "কুয়েরি হেড"), 110, 162),
    node("latent", "storage", ("Compressed", "সংকুচিত"), 110, 162),
    node("cheap", "tool", ("Cheap layers", "সস্তা লেয়ার"), 110, 162),
    node("kv", "cache", ("KV cache", "KV ক্যাশ"), 380, 162),
    node("win", "clock", ("Window", "উইন্ডো"), 380, 162),
    node("full", "model", ("Full attention", "ফুল অ্যাটেনশন"), 380, 162),
    node("mem", "server", ("GPU memory", "GPU মেমরি"), 650, 162),
]

METRICS = [
    ("KV heads", "KV হেড"),
    ("Per token", "প্রতি টোকেন"),
    ("At 128K tokens", "১২৮K টোকেনে"),
    ("DeepSeek-V2", "DeepSeek-V2"),
]

CAPTION = (
    "A model shaped like Llama 3 8B: 32 layers, 32 query heads, head size 128, FP16. The cache figures below are the section's own.",
    "Llama 3 8B-র মতো আকারের মডেল: ৩২ লেয়ার, ৩২ কুয়েরি হেড, হেড সাইজ ১২৮, FP16। নিচের ক্যাশের হিসাব সেকশনেরই।",
)

STEPS = [
    st(("Growth", "বড় হওয়া"),
       ("The KV cache can grow huge", "KV ক্যাশ অনেক বড় হতে পারে"),
       [("The KV cache holds the keys and values the model stores for every earlier token, for every layer, so it does not recompute them.",
         "KV ক্যাশ মডেল প্রতিটি আগের টোকেনের জন্য, প্রতিটি লেয়ারে যে কী আর ভ্যালু জমা রাখে, তা ধরে রাখে, যাতে আবার হিসাব করতে না হয়।"),
        ("For long inputs it can grow to many gigabytes. This section shows the numbers, how sharing or compressing keys and values shrinks it, and how cheaper attention cuts compute.",
         "লম্বা ইনপুটে এটি অনেক গিগাবাইট পর্যন্ত বড় হতে পারে। এই সেকশনে সংখ্যাগুলো আছে, আর আছে কী আর ভ্যালু ভাগ বা সংকুচিত করলে ক্যাশ কীভাবে ছোট হয় এবং সস্তা অ্যাটেনশন কীভাবে কম্পিউট কমায়।")],
       [sh("tok", "hot", ("every earlier one", "প্রতিটি আগেরটি")), sh("kv", "hot", ("keys and values", "কী আর ভ্যালু")),
        sh("mem", "warn", ("many gigabytes", "অনেক গিগাবাইট"))],
       [ln("tok", "kv", "to", state="hot"), ln("kv", "mem", "to", state="warn")],
       [None, None, None, None]),

    st(("Counting", "হিসাব"),
       ("Counting the cache", "ক্যাশের হিসাব"),
       [("Take a model shaped like Llama 3 8B: 32 layers, 32 query heads, head size 128, FP16 (2 bytes per number).",
         "Llama 3 8B-র মতো আকারের একটি মডেল ধরুন: ৩২ লেয়ার, ৩২ কুয়েরি হেড, হেড সাইজ ১২৮, FP16 (প্রতি সংখ্যায় ২ বাইট)।"),
        ("For each token and layer, the cache holds one K and one V for each KV head.",
         "প্রতিটি টোকেন আর লেয়ারে ক্যাশ প্রতিটি KV হেডের জন্য একটি K আর একটি V ধরে রাখে।")],
       [sh("tok", "hot"), sh("kv", "hot", ("one K and one V", "K আর V"))],
       [ln("tok", "kv", "to", state="hot")],
       [None, None, None, None],
       note=("insight",
             "The formula is <code>2 × layers × kv_heads × head_size × bytes × tokens</code>.",
             "সূত্র: <code>2 × layer × kv_head × head_size × byte × token</code>।")),

    st(("MHA", "MHA"),
       ("MHA: 32 KV heads", "MHA: ৩২টি KV হেড"),
       [("MHA has 32 KV heads. The cache costs 512 KiB per token, and 64 GiB at 128K tokens.",
         "MHA-তে ৩২টি KV হেড। ক্যাশে প্রতি টোকেনে ৫১২ KiB লাগে, আর ১২৮K টোকেনে ৬৪ GiB।")],
       [sh("q", "hot", ("32 query heads", "৩২ কুয়েরি হেড")), sh("kv", "hot", ("32 KV heads", "৩২ KV হেড"))],
       [ln("q", "kv", "to", state="hot")],
       [("32", "৩২"), ("512 KiB", "৫১২ KiB"), ("64 GiB", "৬৪ GiB"), None]),

    st(("GQA", "GQA"),
       ("GQA: several query heads share one", "GQA: কয়েকটি কুয়েরি হেড একটি ভাগ করে"),
       [("GQA (grouped-query attention) lets several query heads share one KV head. Llama 3 8B uses 8, so its cache is smaller: 128 KiB per token and 16 GiB at 128K tokens.",
         "GQA (গ্রুপড-কুয়েরি অ্যাটেনশন) কয়েকটি কুয়েরি হেডকে একটি KV হেড ভাগ করতে দেয়। Llama 3 8B ৮টি ব্যবহার করে, তাই ক্যাশ ছোট: প্রতি টোকেনে ১২৮ KiB, আর ১২৮K টোকেনে ১৬ GiB।")],
       [sh("q", "hot", ("32 query heads", "৩২ কুয়েরি হেড")), sh("kv", "hot", ("8 KV heads", "৮টি KV হেড"))],
       [ln("q", "kv", "to", state="hot")],
       [("8", "৮"), ("128 KiB", "১২৮ KiB"), ("16 GiB", "১৬ GiB"), None]),

    st(("MQA", "MQA"),
       ("MQA: all query heads share one", "MQA: সব কুয়েরি হেড একটি ভাগ করে"),
       [("MQA (multi-query attention) is the extreme case: all query heads share just 1 KV head. It has the smallest cache: 16 KiB per token and 2 GiB at 128K tokens.",
         "MQA (মাল্টি-কুয়েরি অ্যাটেনশন) হলো চরম রূপ: সব কুয়েরি হেড মাত্র ১টি KV হেড ভাগ করে। এর ক্যাশ সবচেয়ে ছোট: প্রতি টোকেনে ১৬ KiB, আর ১২৮K টোকেনে ২ GiB।")],
       [sh("q", "hot", ("32 query heads", "৩২ কুয়েরি হেড")), sh("kv", "hot", ("1 KV head", "১টি KV হেড"))],
       [ln("q", "kv", "to", state="hot")],
       [("1", "১"), ("16 KiB", "১৬ KiB"), ("2 GiB", "২ GiB"), None]),

    st(("MLA", "MLA"),
       ("MLA: store one compressed form", "MLA: একটি সংকুচিত রূপ জমা রাখে"),
       [("MLA (multi-head latent attention) goes further than GQA: it stores one compressed form and rebuilds the keys and values.",
         "MLA (মাল্টি-হেড ল্যাটেন্ট অ্যাটেনশন) GQA-এর চেয়েও এগিয়ে যায়: একটি সংকুচিত রূপ জমা রাখে এবং কী আর ভ্যালু আবার বানায়।"),
        ("The DeepSeek-V2 paper reports a KV cache that is 93.3% smaller than that of its earlier dense model, DeepSeek 67B.",
         "DeepSeek-V2 পেপার জানায়, তার KV ক্যাশ আগের ডেন্স মডেল DeepSeek 67B-এর চেয়ে ৯৩.৩% ছোট।")],
       [sh("latent", "hot", ("one stored form", "একটি জমানো রূপ")), sh("kv", "hot", ("keys and values", "কী আর ভ্যালু"))],
       [ln("latent", "kv", "to", state="hot", label=("rebuilds", "আবার বানায়"))],
       [None, None, None, ("93.3% smaller", "৯৩.৩% ছোট")]),

    st(("Window", "উইন্ডো"),
       ("A sliding window", "স্লাইডিং উইন্ডো"),
       [("In a sliding window, a token reads only the last w tokens. Gemma 3 uses five local layers for each global layer, with a window of 1,024 tokens.",
         "স্লাইডিং উইন্ডোতে একটি টোকেন শুধু শেষ w টোকেন পড়ে। Gemma 3 প্রতিটি গ্লোবাল লেয়ারের জন্য পাঁচটি লোকাল লেয়ার ব্যবহার করে, উইন্ডো ১,০২৪ টোকেনের।"),
        ("The guide notes that its ablation shows only a small loss in quality.",
         "গাইডটি জানায়, এর অ্যাবলেশনে মানের ক্ষতি সামান্য।")],
       [sh("tok", "hot", ("one token", "একটি টোকেন")), sh("win", "hot", ("1,024 tokens", "১,০২৪ টোকেন"))],
       [ln("tok", "win", "to", state="hot")],
       [None, None, None, None]),

    st(("Sparse and hybrid", "স্পার্স আর হাইব্রিড"),
       ("Fewer pairs, or fewer full layers", "কম জোড়া, বা কম ফুল লেয়ার"),
       [("Cheaper attention can also use fewer pairs or fewer full layers:",
         "সস্তা অ্যাটেনশনে জোড়া কমানো যায়, বা ফুল লেয়ার কমানো যায়:")],
       [sh("cheap", "hot", ("cheap at long length", "লম্বা ইনপুটে সস্তা")), sh("full", "hot", ("exact lookup", "নির্ভুল খোঁজা"))],
       [ln("cheap", "full", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "DeepSeek sparse attention: the window is not fixed. A small indexer scores earlier tokens, and a selector keeps the best ones.",
                 "DeepSeek স্পার্স অ্যাটেনশন: উইন্ডো স্থির নয়। একটি ছোট ইনডেক্সার আগের টোকেনগুলোকে স্কোর দেয়, আর একটি সিলেক্টর সেরাগুলো রাখে।"),
                ("+", "Hybrid: most layers use a linear or state-space mixer that costs little at long length. Every few layers, a full-attention layer restores exact lookup.",
                 "হাইব্রিড: বেশিরভাগ লেয়ার লিনিয়ার বা স্টেট-স্পেস মিক্সার ব্যবহার করে, যা লম্বা ইনপুটে খরচ কম। কয়েক লেয়ার পরপর একটি ফুল-অ্যাটেনশন লেয়ার নির্ভুল খুঁজে দেখা ফিরিয়ে আনে।"),
                ("+", "Qwen3-Next uses a 3 : 1 mix. The guide notes a small quality trade-off.",
                 "Qwen3-Next-এ ৩ : ১ মিশ্রণ। গাইডটি জানায়, মানের সামান্য বিনিময় আছে।")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Know the limit: the guide explains architecture ideas, and it does not rank the models.",
         "সীমা: আর্টিকেলটি নকশার ধারণা ব্যাখ্যা করে। এটি মডেলগুলোর র‍্যাংকিং করে না।")],
       [sh("tok"), sh("kv"), sh("mem")],
       [ln("tok", "kv", "to"), ln("kv", "mem", "to")],
       [None, None, None, None],
       points=[("For a Llama 3 8B-shaped model (32 layers, head size 128, FP16), the cache grows with KV heads and tokens.",
                "Llama 3 8B-র মতো আকারের মডেলে (৩২ লেয়ার, হেড সাইজ ১২৮, FP16) ক্যাশ KV হেড আর টোকেনের সাথে বাড়ে।"),
               ("At 128K tokens, it needs 64 GiB with 32 KV heads, 16 GiB with 8, 2 GiB with 1.",
                "১২৮K টোকেনে লাগে ৩২ KV হেডে ৬৪ GiB, ৮টিতে ১৬ GiB, আর ১টিতে ২ GiB।"),
               ("DeepSeek-V2 reports a KV cache that is 93.3% smaller than its earlier dense model.",
                "DeepSeek-V2 জানায়, তার KV ক্যাশ আগের ডেন্স মডেলের চেয়ে ৯৩.৩% ছোট।"),
               ("Gemma 3 uses a window of 1,024 tokens. Qwen3-Next uses a 3 : 1 hybrid mix.",
                "Gemma 3-এ উইন্ডো ১,০২৪ টোকেন। Qwen3-Next-এ হাইব্রিড অনুপাত ৩ : ১।"),
               ("For each variant, ask what it saves and what it gives up. Real speed also depends on software and GPU.",
                "প্রতিটি ভ্যারিয়েন্টে জিজ্ঞেস করুন কী বাঁচে আর কী ছাড়তে হয়। আসল গতি সফটওয়্যার আর GPU-র ওপরও নির্ভর করে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
