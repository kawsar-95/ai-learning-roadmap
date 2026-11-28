"""Part 8 · 03 Faster, cheaper inference: quantization, caching, batching and metrics: tricks for a self-hosted server, and the numbers that measure them.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Quantize  Body: "Quantization reduces the precision of model weights from 16-bit to 8- or 4-bit. It trades a small amount of quality for 2–4× less GPU memory and proportionally faster inference."
  2 Formats   Body, "The common formats": GGUF, AWQ, GPTQ, INT8 / FP8, INT4 / NF4, each with the line the section gives it.
  3 KV cache  Body: "The KV cache holds the attention keys and values already computed for earlier tokens, so the model does not recompute them for each new token." "Paged KV cache: instead of one contiguous buffer per request, KV cache memory is allocated in pages (à la OS virtual memory). vLLM's PagedAttention removes the wasted-memory problem of naive serving."
  4 Prefix    Body: "Prefix caching: if many requests share a long system prompt, the server hashes the prefix and reuses the cached KV. Anthropic's cache_control and OpenAI's automatic prompt caching cut the cost of the cached portion. Anthropic cache reads cost 0.1× the base input price (0.05× on some newer models; writes cost 1.25×). OpenAI discounts cached input by up to 90%, depending on model."
  5 Speculate Body: "A tiny draft model proposes the next 5–10 tokens; the big model verifies them in parallel. In Leviathan et al., this gave 2–3× faster decoding on T5-XXL with identical outputs. Gains depend on the model and how often the draft is accepted."
  6 Batching  Body: "Naive serving processes one request at a time per GPU. Continuous batching (vLLM, TGI, SGLang) interleaves tokens from many requests so the GPU is never idle waiting for one slow request. It is a core technique in vLLM; the vLLM paper reports 2–4× higher throughput than FasterTransformer and Orca, which already use it. Add max_num_seqs, max_model_len, and CUDA-graph capture for the next 2×."
  7 Metrics   Table, "Latency vs throughput (TTFT, TPS)": TTFT, TPS, Throughput and p99 latency, each with what it is and what moves it.
  8 Remember  Start here: "Quantization shrinks the model, caching skips repeated work, and batching keeps the GPU busy."; and the four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("w16", "model", ("Weights, 16-bit", "ওয়েট, ১৬-বিট"), 200, 162),
    node("w4", "model", ("Weights, 4-bit", "ওয়েট, ৪-বিট"), 560, 162),
    node("old", "note", ("Earlier tokens", "আগের টোকেন"), 110, 162),
    node("kv", "cache", ("KV cache", "KV ক্যাশ"), 380, 162),
    node("next", "note", ("Next tokens", "পরের টোকেন"), 650, 162),
    node("r1", "user", ("Request", "রিকোয়েস্ট"), 110, 75),
    node("r2", "user", ("Request", "রিকোয়েস্ট"), 110, 162),
    node("r3", "user", ("Request", "রিকোয়েস্ট"), 110, 250),
    node("draft", "model", ("Draft model", "ড্রাফট মডেল"), 110, 162),
    node("big", "model", ("Big model", "বড় মডেল"), 380, 162),
    node("batch", "queue", ("Mixed batch", "মেশানো ব্যাচ"), 380, 162),
    node("gpu", "server", ("GPU", "GPU"), 650, 162),
]

METRICS = [
    ("Memory", "মেমরি"),
    ("Cost", "খরচ"),
    ("Throughput", "থ্রুপুট"),
    ("Quality", "মান"),
]

CAPTION = (
    "Illustrative, not a benchmark: the sizes and speedups are the section's own figures.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: আকার আর গতির হিসাব সেকশনের নিজস্ব।",
)

REQS = ["r1", "r2", "r3"]

STEPS = [
    st(("Quantize", "কোয়ান্টাইজ"),
       ("Quantization: fewer bits per weight", "কোয়ান্টাইজেশন: ওয়েটে কম বিট"),
       [("Quantization stores model weights with fewer bits: it reduces precision from 16-bit to 8- or 4-bit.",
         "কোয়ান্টাইজেশন মডেলের ওয়েট কম বিটে রাখে: প্রিসিশন ১৬-বিট থেকে ৮ বা ৪ বিটে নামায়।"),
        ("It trades a small amount of quality for 2–4× less GPU memory and proportionally faster inference.",
         "সামান্য মানের বিনিময়ে GPU মেমরি ২–৪× কমে আর ইনফারেন্স আনুপাতিকভাবে দ্রুত হয়।")],
       [sh("w16", "hot"), sh("w4", "hot", ("fewer bits", "কম বিট"))],
       [ln("w16", "w4", "to", state="hot")],
       [("2–4× less", "২–৪× কম"), None, None, ("small loss", "সামান্য কমে")]),

    st(("Formats", "ফরম্যাট"),
       ("The common formats", "প্রচলিত ফরম্যাট"),
       [("The common formats are:",
         "প্রচলিত ফরম্যাটগুলো হলো:")],
       [sh("w16", "dim"), sh("w4", "hot", ("AWQ, GGUF, GPTQ", "AWQ, GGUF, GPTQ"))],
       [ln("w16", "w4", "to", state="dim")],
       [None, None, None, None],
       changes=[("+", "GGUF: llama.cpp's format, one file that runs on CPU, GPU or both",
                 "GGUF: llama.cpp-এর ফরম্যাট, একটি ফাইল, যা CPU, GPU বা দুটোতেই চলে"),
                ("+", "AWQ: 4-bit with near-FP16 quality, popular for vLLM and SGLang",
                 "AWQ: ৪-বিটে FP16-এর কাছাকাছি মান, vLLM আর SGLang-এ জনপ্রিয়"),
                ("+", "GPTQ: a post-training method, older and still common for GPU serving",
                 "GPTQ: পোস্ট-ট্রেনিং পদ্ধতি, পুরোনো, GPU সার্ভিংয়ে এখনও প্রচলিত"),
                ("+", "INT8 / FP8: minimal quality loss on H100s, with native hardware support",
                 "INT8 / FP8: H100-এ নেটিভ হার্ডওয়্যার সাপোর্টসহ সর্বনিম্ন মান-ক্ষতি"),
                ("+", "INT4 / NF4: four-bit formats, with bitsandbytes (QLoRA) for training, also used at inference",
                 "INT4 / NF4: ৪-বিট ফরম্যাট, bitsandbytes (QLoRA) ট্রেনিংয়ে, ইনফারেন্সেও ব্যবহৃত")]),

    st(("KV cache", "KV ক্যাশ"),
       ("The KV cache", "KV ক্যাশ"),
       [("The KV cache holds the attention keys and values already computed for earlier tokens, so the model does not recompute them for each new token.",
         "KV ক্যাশ আগের টোকেনের জন্য আগেই হিসাব করা অ্যাটেনশন কী আর ভ্যালু ধরে রাখে, যাতে প্রতিটি নতুন টোকেনে মডেলকে আবার হিসাব করতে না হয়।"),
        ("A paged KV cache allocates its memory in pages, like OS virtual memory, instead of one contiguous buffer per request. vLLM's PagedAttention removes the wasted memory of naive serving.",
         "পেজড KV ক্যাশ প্রতিটি রিকোয়েস্টের জন্য একটি কন্টিগুয়াস বাফারের বদলে মেমরি পেজে (OS ভার্চুয়াল মেমরির মতো) বরাদ্দ করে। vLLM-এর PagedAttention নেইভ সার্ভিংয়ের নষ্ট মেমরির সমস্যা দূর করে।")],
       [sh("old", "hot", ("already computed", "আগেই হিসাব করা")), sh("kv", "hot", ("keys and values", "কী আর ভ্যালু")), sh("next", "hot", ("no recompute", "আবার হিসাব নয়"))],
       [ln("old", "kv", "to", state="hot"), ln("kv", "next", "to", state="hot")],
       [None, None, None, None]),

    st(("Prefix", "প্রিফিক্স"),
       ("Prefix caching", "প্রিফিক্স ক্যাশিং"),
       [("If many requests share a long system prompt, the server hashes the prefix and reuses the cached KV.",
         "অনেক রিকোয়েস্ট একই দীর্ঘ সিস্টেম প্রম্পট শেয়ার করলে সার্ভার প্রিফিক্স হ্যাশ করে আর ক্যাশ করা KV আবার ব্যবহার করে।"),
        ("Anthropic's cache_control and OpenAI's automatic prompt caching cut the cost of the cached portion. Anthropic cache reads cost 0.1× the base input price (0.05× on some newer models; writes cost 1.25×). OpenAI discounts cached input by up to 90%, depending on model.",
         "Anthropic-এর cache_control আর OpenAI-র অটোমেটিক প্রম্পট ক্যাশিং ক্যাশ করা অংশের খরচ কমায়। Anthropic-এর ক্যাশ রিডের খরচ বেস ইনপুট দামের ০.১× (কিছু নতুন মডেলে ০.০৫×; রাইটে ১.২৫×)। OpenAI ক্যাশ করা ইনপুটে মডেলভেদে সর্বোচ্চ ৯০% ছাড় দেয়।")],
       [sh("r1", "hot", ("same system prompt", "একই সিস্টেম প্রম্পট")), sh("r2", "hot", ("same system prompt", "একই সিস্টেম প্রম্পট")),
        sh("r3", "hot", ("same system prompt", "একই সিস্টেম প্রম্পট")), sh("kv", "hot", ("shared prefix", "শেয়ার করা প্রিফিক্স"))],
       [ln("r1", "kv", "to", state="hot"), ln("r2", "kv", "to", state="hot"), ln("r3", "kv", "to", state="hot")],
       [None, ("up to 90% less", "সর্বোচ্চ ৯০% কম"), None, None]),

    st(("Speculate", "অনুমান"),
       ("Speculative decoding", "স্পেকুলেটিভ ডিকোডিং"),
       [("A tiny draft model proposes the next 5–10 tokens, and the big model verifies them in parallel.",
         "একটি ছোট ড্রাফট মডেল পরবর্তী ৫–১০ টোকেন প্রস্তাব করে; বড় মডেল সেগুলো সমান্তরালে যাচাই করে।"),
        ("In Leviathan et al., this gave 2–3× faster decoding on T5-XXL with identical outputs. Gains depend on the model and how often the draft is accepted.",
         "Leviathan et al.-এ এতে T5-XXL-এ একই আউটপুটে ডিকোডিং ২–৩× দ্রুত হয়েছে। লাভ নির্ভর করে মডেলের ওপর আর ড্রাফট কতবার গৃহীত হয় তার ওপর।")],
       [sh("draft", "hot", ("guesses ahead", "আগে আন্দাজ করে")), sh("big", "hot", ("checks them all", "সব একসাথে যাচাই করে")), sh("next", "hot")],
       [ln("draft", "big", "to", state="hot"), ln("big", "next", "to", state="hot")],
       [None, None, ("2–3× faster", "২–৩× দ্রুত"), ("identical output", "একই আউটপুট")]),

    st(("Batching", "ব্যাচিং"),
       ("Continuous batching", "কন্টিনিউয়াস ব্যাচিং"),
       [("Naive serving processes one request at a time per GPU. Continuous batching, in vLLM, TGI and SGLang, interleaves tokens from many requests so the GPU is never idle waiting for one slow request.",
         "নেইভ সার্ভিং GPU-তে একবারে একটি রিকোয়েস্ট প্রক্রিয়া করে। কন্টিনিউয়াস ব্যাচিং (vLLM, TGI, SGLang) অনেক রিকোয়েস্টের টোকেন মিলিয়ে চালায়, যাতে একটি ধীর রিকোয়েস্টের জন্য GPU কখনো বসে না থাকে।"),
        ("It is a core technique in vLLM; the vLLM paper reports 2–4× higher throughput than FasterTransformer and Orca, which already use it. Adding <code>max_num_seqs</code>, <code>max_model_len</code> and CUDA-graph capture gives the next 2×.",
         "এটি vLLM-এর একটি মূল কৌশল; vLLM পেপার FasterTransformer ও Orca-র চেয়ে ২–৪× বেশি থ্রুপুট জানায়, যারা আগে থেকেই এটি ব্যবহার করে। <code>max_num_seqs</code>, <code>max_model_len</code> আর CUDA-graph ক্যাপচার যোগ করলে আরও ২× পাওয়া যায়।")],
       [sh("r1", "hot"), sh("r2", "hot"), sh("r3", "hot"), sh("batch", "hot", ("mixed tokens", "মেশানো টোকেন")), sh("gpu", "hot", ("never idle", "কখনো বসে থাকে না"))],
       [ln("r1", "batch", "to", state="hot"), ln("r2", "batch", "to", state="hot"), ln("r3", "batch", "to", state="hot"), ln("batch", "gpu", "to", state="hot")],
       [None, None, ("2–4×", "২–৪×"), None]),

    st(("Metrics", "মেট্রিক"),
       ("Latency versus throughput", "ল্যাটেন্সি বনাম থ্রুপুট"),
       [("TTFT, the time to first token, is how long until the user sees the first word. TPS, tokens per second per request, is the generation speed the user sees. Throughput is the total tokens the server emits. p99 latency is the tail latency for the worst 1% of requests.",
         "TTFT (টাইম টু ফার্স্ট টোকেন) হলো ইউজার কত তাড়াতাড়ি প্রথম শব্দ দেখে। TPS (টোকেন পার সেকেন্ড, প্রতি রিকোয়েস্টে) হলো জেনারেশনের গতি, যা ইউজার দেখে। থ্রুপুট হলো সার্ভার মোট কত টোকেন তৈরি করে। p99 ল্যাটেন্সি হলো সবচেয়ে খারাপ ১% রিকোয়েস্টের টেইল ল্যাটেন্সি।")],
       [sh("r2", "hot", ("waits for a word", "প্রথম শব্দের অপেক্ষা")), sh("gpu", "hot", ("prefill, then tokens", "প্রিফিল, তারপর টোকেন"))],
       [ln("r2", "gpu", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "TTFT moves with prompt length, prefill compute and the network",
                 "TTFT বদলায় প্রম্পটের দৈর্ঘ্য, প্রিফিল কম্পিউট আর নেটওয়ার্কে"),
                ("+", "TPS moves with model size, batch size and KV-cache hits",
                 "TPS বদলায় মডেলের আকার, ব্যাচ সাইজ আর KV-ক্যাশ হিটে"),
                ("+", "Throughput moves with continuous batching and GPU occupancy",
                 "থ্রুপুট বদলায় কন্টিনিউয়াস ব্যাচিং আর GPU ব্যবহারে"),
                ("+", "p99 latency moves with queue depth and KV-cache pressure",
                 "p99 ল্যাটেন্সি বদলায় কিউয়ের গভীরতা আর KV-ক্যাশের চাপে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Quantization shrinks the model, caching skips repeated work, and batching keeps the GPU busy.",
         "কোয়ান্টাইজেশন মডেল ছোট করে, ক্যাশিং একই কাজ আবার করা এড়ায়, আর ব্যাচিং GPU-কে ব্যস্ত রাখে।")],
       [sh("r1"), sh("r2"), sh("r3"), sh("batch"), sh("gpu")],
       [ln("r1", "batch", "to"), ln("r2", "batch", "to"), ln("r3", "batch", "to"), ln("batch", "gpu", "to")],
       [None, None, None, None],
       points=[("Quantization cuts GPU memory by 2–4× for a small loss in quality.",
                "কোয়ান্টাইজেশন সামান্য মান কমিয়ে GPU মেমরি ২–৪× কমায়।"),
               ("Anthropic's and OpenAI's prompt caching cut the cost of the cached part, by up to 90%.",
                "Anthropic আর OpenAI-র প্রম্পট ক্যাশিং ক্যাশ করা অংশে খরচ সর্বোচ্চ ৯০% পর্যন্ত কমায়।"),
               ("Speculative decoding gave 2–3× faster decoding with identical outputs on T5-XXL; gains depend on the model.",
                "স্পেকুলেটিভ ডিকোডিং T5-XXL-এ একই আউটপুটে ডিকোডিং ২–৩× দ্রুত করেছে; লাভ মডেলের ওপর নির্ভর করে।"),
               ("Continuous batching is a core technique in vLLM, which reports 2–4× higher throughput than FasterTransformer and Orca.",
                "কন্টিনিউয়াস ব্যাচিং vLLM-এর একটি মূল কৌশল; vLLM FasterTransformer ও Orca-র চেয়ে ২–৪× বেশি থ্রুপুট জানায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
