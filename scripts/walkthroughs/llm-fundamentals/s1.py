"""Part 1 · 01 Tokens, tokenization & context cost: text becomes tokens, and tokens become cost and delay.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Text      "Tokenization is the silent tax on every LLM call." is the sentence of the section's code, with its "11 tokens, not 8 words".
              Start here: "A model does not read whole words. It reads tokens, small pieces of text. Every token you send and every token you get back costs money and time."
  2 Tokens    Start here: Tokenizer ("cuts text into tokens before the model reads it"), Vocabulary ("The fixed list of all the tokens a model knows"), BPE
              ("keeps joining the pairs of pieces that appear side by side most often"), "often 32k to 200k". Body: "~1 token ≈ 4 characters in English ... varies wildly by language".
  3 Read      Start here: Prefill ("reads your whole prompt"), Context window ("The most tokens a model can handle in one call, counting your input and its output together").
  4 Write     Start here: Decode ("writes the answer one token at a time"), "Output tokens usually cost 3–5 times more than input tokens."
  5 Bill      Body: "APIs charge per token, not per character". The code: 11 tokens at 0.15 USD per 1M input tokens = $0.00000165 (gpt-4o-mini, Jul 2025 pricing).
  6 Shorter   Sub-title: "If your prompt shrinks from 800 to 200 tokens, you just cut cost by 75% and latency by a meaningful fraction ... the single biggest engineering lever".
              The two input costs are 800 and 200 tokens at the code's 0.15 USD per 1M: $0.00012 and $0.00003.
  7 Cache     Start here: Prompt caching ("Reusing the work done on the start of a prompt that repeats ... cuts the cost of that part by about 80–90%").
  8 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

nodes = [
    node("text", "file", ("Your text", "আপনার লেখা"), 96, 75),
    node("tok", "service", ("Tokenizer", "টোকেনাইজার"), 290, 75),
    node("model", "model", ("Model", "মডেল"), 495, 75),
    node("ans", "file", ("Answer", "উত্তর"), 690, 75),
    node("vocab", "database", ("Token list", "টোকেনের তালিকা"), 290, 250),
    node("bill", "chart", ("Bill", "বিল"), 495, 250),
    node("cache", "cache", ("Prompt cache", "প্রম্পট ক্যাশ"), 668, 250),
]

metrics = [("Words", "শব্দ"), ("Tokens in", "ইনপুট টোকেন"), ("Input cost", "ইনপুটের খরচ")]
caption = ("Example numbers. The price is the one in this section's code.", "উদাহরণের সংখ্যা। দাম এই সেকশনের কোডে যা আছে, তা-ই।")

steps = [
    st(
        ("Text", "লেখা"),
        ("A model does not read words", "মডেল শব্দ পড়ে না"),
        [
            (
                "You send a model some text: “Tokenization is the silent tax on every LLM call.” That is 8 words.",
                "আপনি মডেলকে একটি লেখা পাঠান: “Tokenization is the silent tax on every LLM call.” এতে ৮টি শব্দ আছে।",
            ),
            (
                "But the model does not read whole words. It reads tokens, small pieces of text.",
                "কিন্তু মডেল পুরো শব্দ পড়ে না। সে পড়ে টোকেন, মানে লেখার ছোট ছোট টুকরো।",
            ),
        ],
        [sh("text", "hot", sub=("8 words", "৮টি শব্দ")), sh("tok")],
        [ln("text", "tok", "to")],
        values=["8", None, None],
        note=(
            "insight",
            "Every token you send and every token you get back costs money and time.",
            "আপনি যত টোকেন পাঠান আর যত টোকেন ফেরত পান, প্রতিটির জন্য টাকা আর সময় দুটোই লাগে।",
        ),
    ),
    st(
        ("Tokens", "টোকেন"),
        ("The tokenizer cuts the text into tokens", "টোকেনাইজার লেখাকে টোকেনে কাটে"),
        [
            (
                "Before the model reads anything, a tokenizer cuts the text into tokens. It uses a fixed list of tokens, the vocabulary. Here, the 8 words become 11 tokens.",
                "মডেল কিছু পড়ার আগে টোকেনাইজার লেখাকে টোকেনে কেটে নেয়। সে টোকেনের একটি নির্দিষ্ট তালিকা ব্যবহার করে, যার নাম ভোকাবুলারি। এখানে ৮টি শব্দ হয়ে যায় ১১টি টোকেন।",
            ),
            (
                "The list is built with Byte-Pair Encoding. It keeps joining the pairs of pieces that appear side by side most often, until the list holds 32k to 200k tokens.",
                "তালিকাটা বানানো হয় Byte-Pair Encoding (BPE) দিয়ে। যে জোড়া টুকরো সবচেয়ে বেশি পাশাপাশি আসে, সেগুলোকে বারবার জুড়ে দেওয়া হয়, যতক্ষণ না তালিকায় ৩২k থেকে ২০০k টোকেন হয়।",
            ),
        ],
        [
            sh("text", "dim", sub=("8 words", "৮টি শব্দ")),
            sh("tok", "hot", sub=("11 tokens", "১১টি টোকেন")),
            sh("vocab", "hot", sub=("32k–200k tokens", "৩২k–২০০k টোকেন")),
        ],
        [ln("text", "tok", "to"), ln("vocab", "tok", "to")],
        values=["8", "11", None],
        note=(
            "tip",
            "In English, one token is about 4 characters. Other languages and code differ.",
            "ইংরেজিতে ১ টোকেন মোটামুটি ৪ অক্ষর। অন্য ভাষা আর কোডে এটা বদলে যায়।",
        ),
        changes=[("+", "The 8 words become 11 tokens.", "৮টি শব্দ হয়ে গেল ১১টি টোকেন।")],
    ),
    st(
        ("Read", "প্রম্পট পড়া"),
        ("The model reads every input token", "মডেল প্রতিটি ইনপুট টোকেন পড়ে"),
        [
            (
                "First the model reads your whole prompt. This step is called prefill.",
                "প্রথমে মডেল আপনার পুরো প্রম্পট পড়ে। এই ধাপের নাম প্রিফিল।",
            ),
            (
                "Everything it reads and writes must fit in the context window: the most tokens a model can handle in one call, input and output together.",
                "যা পড়ে আর যা লেখে, সবকিছু কনটেক্সট উইন্ডোর মধ্যে ধরতে হবে। এক কলে মডেল সর্বোচ্চ যত টোকেন সামলাতে পারে, ইনপুট আর আউটপুট মিলিয়ে, সেটাই কনটেক্সট উইন্ডো।",
            ),
        ],
        [sh("tok", "dim", sub=("11 tokens", "১১টি টোকেন")), sh("model", "hot", sub=("reads 11 tokens", "১১টি টোকেন পড়ছে"))],
        [ln("tok", "model", "to", state="hot")],
        values=["8", "11", None],
    ),
    st(
        ("Write", "উত্তর লেখা"),
        ("Then it writes the answer, one token at a time", "তারপর উত্তর লেখে, একবারে একটি টোকেন"),
        [
            (
                "After reading, the model writes the answer one token at a time. This step is called decode.",
                "পড়া শেষে মডেল উত্তর লেখে, একবারে একটি টোকেন করে। এই ধাপের নাম ডিকোড।",
            ),
        ],
        [sh("model", "hot", sub=("1 token at a time", "একবারে ১টি টোকেন")), sh("ans", "hot")],
        [ln("model", "ans", "to", ms=2200, state="hot")],
        values=["8", "11", None],
        note=(
            "insight",
            "Output tokens usually cost 3–5 times more than input tokens.",
            "আউটপুট টোকেন সাধারণত ইনপুট টোকেনের চেয়ে ৩–৫ গুণ দামি।",
        ),
    ),
    st(
        ("Bill", "বিল"),
        ("You pay for tokens", "টোকেন ধরে দাম দিতে হয়"),
        [
            (
                "APIs charge per token, not per word or per character. The cost of the input is the number of tokens × the price of one token.",
                "API দাম ধরে টোকেন অনুযায়ী, শব্দ বা অক্ষর অনুযায়ী নয়। ইনপুটের খরচ হলো টোকেনের সংখ্যা × এক টোকেনের দাম।",
            ),
            (
                "In this section's example, 11 input tokens at $0.15 per million tokens cost $0.00000165.",
                "এই সেকশনের উদাহরণে প্রতি ১ মিলিয়ন ইনপুট টোকেনে ০.১৫ ডলার ধরলে ১১ টোকেনের খরচ ০.০০০০০১৬৫ ডলার।",
            ),
        ],
        [sh("model", "dim"), sh("bill", "hot", sub=("$0.00000165", "$০.০০০০০১৬৫"))],
        [ln("model", "bill", "to", state="hot", label=("× price", "× দাম"))],
        values=["8", "11", "$0.00000165"],
        changes=[("+", "The input costs $0.00000165.", "ইনপুটের খরচ হলো ০.০০০০০১৬৫ ডলার।")],
    ),
    st(
        ("Shorter", "ছোট প্রম্পট"),
        ("A shorter prompt costs less", "ছোট প্রম্পটে খরচ কম"),
        [
            (
                "Take a prompt of 800 tokens and cut it to 200. The cost of the input falls by 75%, and the latency, the wait for the answer, falls too.",
                "৮০০ টোকেনের একটি প্রম্পটকে ২০০ টোকেনে নামিয়ে আনুন। ইনপুটের খরচ ৭৫% কমে, আর ল্যাটেন্সিও কমে, মানে উত্তরের জন্য অপেক্ষা কম লাগে।",
            ),
        ],
        [
            sh("text", "hot", sub=("800 → 200 tokens", "৮০০ → ২০০ টোকেন")),
            sh("tok", "dim"),
            sh("model", "dim"),
            sh("bill", "hot", sub=("75% less", "৭৫% কম")),
        ],
        [ln("text", "tok", "to", state="dim"), ln("tok", "model", "to", state="dim"), ln("model", "bill", "to", state="hot")],
        values=[None, "800 → 200", "$0.00012 → $0.00003"],
        note=(
            "insight",
            "This is the single biggest engineering lever you have.",
            "আপনার হাতে থাকা সবচেয়ে বড় ইঞ্জিনিয়ারিং সুবিধা এটাই।",
        ),
        changes=[
            ("-", "The prompt is 600 tokens shorter.", "প্রম্পট ৬০০ টোকেন ছোট হলো।"),
            ("-", "The cost of the input is 75% lower.", "ইনপুটের খরচ ৭৫% কমল।"),
        ],
    ),
    st(
        ("Cache", "ক্যাশ"),
        ("A repeated start can be cached", "বারবার আসা শুরুর অংশ ক্যাশ করা যায়"),
        [
            (
                "Often the start of a prompt is the same from one call to the next. Prompt caching reuses the work done on that start.",
                "অনেক সময় প্রম্পটের শুরুর অংশ এক কল থেকে আরেক কলে একই থাকে। প্রম্পট ক্যাশিং সেই অংশের জন্য করা কাজ আবার ব্যবহার করে।",
            ),
            (
                "It cuts the cost of that part by about 80–90%.",
                "এতে সেই অংশের খরচ প্রায় ৮০–৯০% কমে।",
            ),
        ],
        [
            sh("text", "dim"),
            sh("tok", "dim"),
            sh("model", "hot"),
            sh("cache", "hot", sub=("80–90% cheaper", "৮০–৯০% সস্তা")),
            sh("bill", "dim"),
        ],
        [
            ln("text", "tok", "to", state="dim"),
            ln("tok", "model", "to", state="dim"),
            ln("cache", "model", "to", state="hot", label=("reused", "আবার ব্যবহার")),
            ln("model", "bill", "to", state="dim"),
        ],
        values=[None, "200", "$0.00003"],
        note=(
            "insight",
            "The cache works on the start of a prompt, the part that repeats.",
            "ক্যাশ কাজ করে প্রম্পটের শুরুর অংশে, যে অংশ বারবার আসে।",
        ),
    ),
    st(
        ("Remember", "মনে রাখুন"),
        ("What to remember", "যা মনে রাখবেন"),
        [("Four things to take away from tokens.", "টোকেন থেকে চারটি কথা মনে রাখুন।")],
        [sh("text"), sh("tok"), sh("model"), sh("ans"), sh("bill")],
        [
            ln("text", "tok", "to"),
            ln("tok", "model", "to"),
            ln("model", "ans", "to"),
            ln("model", "bill", "to"),
        ],
        values=[None, "200", "$0.00003"],
        points=[
            ("You pay per token, not per word or per character.", "দাম হয় টোকেন ধরে, শব্দ বা অক্ষর ধরে নয়।"),
            ("Output tokens usually cost 3–5 times more than input tokens.", "আউটপুট টোকেন সাধারণত ইনপুট টোকেনের চেয়ে ৩–৫ গুণ দামি।"),
            (
                "A shorter prompt costs less: going from 800 to 200 tokens cuts the cost by 75%.",
                "প্রম্পট ছোট করলে খরচ কমে: ৮০০ থেকে ২০০ টোকেনে নামালে খরচ ৭৫% কমে।",
            ),
            (
                "A bigger context window does not mean better answers. Measure on your own work.",
                "বড় কনটেক্সট উইন্ডো মানেই ভালো উত্তর নয়। নিজের কাজে মেপে দেখুন।",
            ),
        ],
    ),
]

WALK = walk(760, 320, nodes, metrics, caption, steps)
