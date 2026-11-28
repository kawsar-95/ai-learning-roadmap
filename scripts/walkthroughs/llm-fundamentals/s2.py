"""LLM Fundamentals · 02 Model families & trade-offs: no single best model; pick the trade-off that fits your work.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Question  Sub: "Picking \"the best model\" is a misframe — the right question is which trade-off matches your workload's centre of gravity." Start here: "Do not ask which model is best. Ask which trade-off fits your work."
  2 Families  Sub: "The frontier in 2025 is dominated by seven families". Chart: Anthropic, OpenAI, Google DeepMind on the PRIVATE / PROPRIETARY side; Meta, Mistral AI, Alibaba, DeepSeek on the OPEN-WEIGHT side. "Position is qualitative, not benchmark-exact."
  3 Open      Start here: "Llama, Qwen, DeepSeek, and Mistral's small models publish their weights, so you can host them yourself." "Open weights: The model file is published, so anyone can download it and run it on their own machines."
  4 Dense     Table "Dense transformers": "Every parameter is used on every token. Predictable compute, simple serving." Start here: "Dense model".
  5 MoE       Table "Mixture-of-Experts (MoE)": "Routes each token to a subset of expert feed-forward networks ... Total params large but active params per token small → cheaper inference, larger memory. ... DeepSeek-V3 (671B/37B active)".
  6 Long      Table "Multi-Head Latent Attention (MLA)": "compresses the KV cache ... slashing memory for long contexts." "Sliding-window / hybrid: Mistral 7B used sliding-window attention ... for cheap inference." Start here: "KV cache", "Sliding-window attention".
  7 Remember  The four "remember" points of the section.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("anth", "model", ("Anthropic", "Anthropic"), 120, 60),
    node("oai", "model", ("OpenAI", "OpenAI"), 120, 162),
    node("goog", "model", ("Google DeepMind", "Google DeepMind"), 120, 265),
    node("meta", "model", ("Meta", "Meta"), 450, 60),
    node("mis", "model", ("Mistral AI", "Mistral AI"), 650, 60),
    node("qwen", "model", ("Alibaba", "Alibaba"), 450, 265),
    node("deep", "model", ("DeepSeek", "DeepSeek"), 650, 265),
    node("work", "user", ("Your workload", "আপনার ওয়ার্কলোড"), 550, 162),
    node("tok", "note", ("A token", "একটা টোকেন"), 130, 162),
    node("dense", "model", ("Dense model", "ডেন্স মডেল"), 380, 162),
    node("moe", "model", ("MoE model", "MoE মডেল"), 380, 162),
    node("kv", "cache", ("KV cache", "KV ক্যাশ"), 380, 162),
]

METRICS = [
    ("Compute per token", "প্রতি টোকেনে কম্পিউট"),
    ("Memory", "মেমরি"),
    ("Cost to run", "চালানোর খরচ"),
]

CAPTION = (
    "Illustrative, not a benchmark: position is qualitative and the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: অবস্থান গুণগত আর লেবেলগুলো সেকশনের নিজের কথা।",
)

CLOSED_DIM = [sh("anth", "dim"), sh("oai", "dim"), sh("goog", "dim")]

STEPS = [
    st(("Question", "প্রশ্ন"),
       ("Not which is best, but which trade-off", "কোনটা সেরা নয়, কোন ট্রেড-অফ"),
       [("Do not ask which model is best. Ask which trade-off fits your work.",
         "কোন মডেল সেরা, তা জিজ্ঞেস করবেন না। জিজ্ঞেস করুন, কোন ট্রেড-অফ আপনার কাজের সাথে মেলে।"),
        ("A few big companies make most of the top models, and each family is good at different things.",
         "সেরা মডেলগুলোর বেশিরভাগ বানায় অল্প কয়েকটি বড় কোম্পানি, আর প্রতিটি ফ্যামিলি আলাদা কাজে ভালো।")],
       [sh("work", "hot", ("which trade-off?", "কোন ট্রেড-অফ?")), sh("anth", "dim"), sh("oai", "dim"), sh("goog", "dim"),
        sh("meta", "dim"), sh("mis", "dim"), sh("qwen", "dim"), sh("deep", "dim")],
       [],
       [None, None, None]),

    st(("Families", "ফ্যামিলি"),
       ("Seven families, two sides", "সাতটি ফ্যামিলি, দুই দিক"),
       [("The frontier in 2025 is dominated by seven families, each with its own architectural and commercial philosophy.",
         "২০২৫ সালে ফ্রন্টিয়ারে সাতটি ফ্যামিলির দাপট। প্রতিটির আর্কিটেকচার আর ব্যবসার দর্শন আলাদা।"),
        ("The chart puts Anthropic, OpenAI and Google DeepMind on the private side, and Meta, Mistral AI, Alibaba and DeepSeek on the open-weight side.",
         "চার্টে Anthropic, OpenAI আর Google DeepMind প্রাইভেট দিকে, আর Meta, Mistral AI, Alibaba ও DeepSeek ওপেন-ওয়েট দিকে।")],
       [sh("anth", "hot", ("private", "প্রাইভেট")), sh("oai", "hot", ("private", "প্রাইভেট")), sh("goog", "hot", ("private", "প্রাইভেট")),
        sh("meta", "hot", ("open-weight", "ওপেন-ওয়েট")), sh("mis", "hot", ("open-weight", "ওপেন-ওয়েট")),
        sh("qwen", "hot", ("open-weight", "ওপেন-ওয়েট")), sh("deep", "hot", ("open-weight", "ওপেন-ওয়েট"))],
       [],
       [None, None, None],
       note=("insight", "The position is qualitative, not benchmark-exact.",
             "অবস্থান গুণগত, বেঞ্চমার্কের হুবহু মান নয়।")),

    st(("Open", "ওপেন"),
       ("Open weights you can host", "ওপেন ওয়েট, নিজে হোস্ট করা যায়"),
       [("Llama, Qwen, DeepSeek and Mistral's small models publish their weights, so you can host them yourself.",
         "Llama, Qwen, DeepSeek আর Mistral-এর ছোট মডেলগুলো তাদের ওয়েট প্রকাশ করে, তাই নিজে হোস্ট করা যায়।"),
        ("Open weights means the model file is published, so anyone can download it and run it on their own machines.",
         "ওপেন ওয়েট মানে মডেলের ফাইল প্রকাশ করা হয়, তাই যে কেউ ডাউনলোড করে নিজের মেশিনে চালাতে পারে।")],
       CLOSED_DIM + [sh("meta", "hot", ("weights published", "ওয়েট প্রকাশিত")), sh("mis", "hot", ("weights published", "ওয়েট প্রকাশিত")),
                     sh("qwen", "hot", ("weights published", "ওয়েট প্রকাশিত")), sh("deep", "hot", ("weights published", "ওয়েট প্রকাশিত"))],
       [],
       [None, None, None]),

    st(("Dense", "ডেন্স"),
       ("A dense model uses everything", "ডেন্স মডেল সবটাই ব্যবহার করে"),
       [("A dense model uses all of its parameters for every token.",
         "ডেন্স মডেল প্রতিটি টোকেনের জন্য তার সব প্যারামিটার ব্যবহার করে।"),
        ("Its compute is predictable, and it is simple to serve.",
         "এর কম্পিউট আগে থেকে বোঝা যায়, চালানোও সহজ।")],
       [sh("tok", "hot"), sh("dense", "hot", ("every parameter", "প্রতিটি প্যারামিটার"))],
       [ln("tok", "dense", "to", state="hot")],
       [("predictable", "আগে থেকে বোঝা যায়"), None, ("simple to serve", "চালানো সহজ")]),

    st(("MoE", "MoE"),
       ("Mixture-of-Experts: a few experts per token", "মিক্সচার-অফ-এক্সপার্টস: টোকেনে কয়েকজন এক্সপার্ট"),
       [("A Mixture-of-Experts model sends each token to only a few of its expert parts.",
         "মিক্সচার-অফ-এক্সপার্টস মডেল প্রতিটি টোকেনকে তার অল্প কয়েকটি এক্সপার্ট অংশে পাঠায়।"),
        ("Its total size is large but only a small part is active per token, so it is cheaper to run but needs more memory. DeepSeek-V3 is 671B/37B active.",
         "মোট আকার বড়, কিন্তু প্রতিটি টোকেনে অল্প একটা অংশ অ্যাক্টিভ থাকে, তাই চালাতে সস্তা, তবে মেমরি বেশি লাগে। DeepSeek-V3 হলো ৬৭১B/৩৭B অ্যাক্টিভ।")],
       [sh("tok", "hot"), sh("moe", "hot", ("a few experts", "কয়েকজন এক্সপার্ট")),
        sh("deep", "hot", ("671B/37B active", "৬৭১B/৩৭B অ্যাক্টিভ"), x=630, y=162)],
       [ln("tok", "moe", "to", state="hot")],
       [("cheaper per token", "প্রতি টোকেনে সস্তা"), ("more memory", "বেশি মেমরি"), ("cheaper to run", "চালাতে সস্তা")]),

    st(("Long input", "লম্বা ইনপুট"),
       ("Cheaper long inputs", "লম্বা ইনপুট সস্তা"),
       [("The KV cache is the stored notes about earlier tokens. Long inputs make it big, and DeepSeek's MLA compresses it to save memory.",
         "KV ক্যাশ আগের টোকেন নিয়ে জমিয়ে রাখা নোট। লম্বা ইনপুটে এটা বড় হয়, আর DeepSeek-এর MLA একে ছোট করে মেমরি বাঁচায়।"),
        ("With sliding-window attention, each token looks only at a window of nearby tokens, which makes the model cheaper to run.",
         "স্লাইডিং-উইন্ডো অ্যাটেনশনে প্রতিটি টোকেন শুধু কাছের কিছু টোকেনের একটা উইন্ডো দেখে, তাই মডেল চালানো সস্তা হয়।")],
       [sh("kv", "hot", ("long inputs make it big", "লম্বা ইনপুটে বড় হয়")),
        sh("deep", "hot", ("MLA compresses it", "MLA একে ছোট করে"), x=650, y=162),
        sh("mis", "hot", ("sliding-window", "স্লাইডিং-উইন্ডো"), x=110, y=162)],
       [ln("deep", "kv", "to", state="hot"), ln("mis", "kv", "to", state="hot")],
       [None, ("saved by MLA", "MLA-তে বাঁচে"), ("cheaper", "সস্তা")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("There is no single best model. Pick the trade-off that fits your work.",
         "একক কোনো সেরা মডেল নেই। আপনার কাজের সাথে মেলে এমন ট্রেড-অফ বাছুন।")],
       [sh("work", "hot"), sh("anth", "dim"), sh("oai", "dim"), sh("goog", "dim"),
        sh("meta", "dim"), sh("mis", "dim"), sh("qwen", "dim"), sh("deep", "dim")],
       [],
       [None, None, None],
       points=[("There is no single best model. Pick the trade-off that fits your work.",
                "একক কোনো সেরা মডেল নেই। আপনার কাজের সাথে মেলে এমন ট্রেড-অফ বাছুন।"),
               ("Llama, Qwen, DeepSeek, and Mistral's small models publish their weights, so you can host them yourself.",
                "Llama, Qwen, DeepSeek আর Mistral-এর ছোট মডেলগুলো তাদের ওয়েট প্রকাশ করে, তাই নিজে হোস্ট করা যায়।"),
               ("MoE models are large in total but use only a small part for each token, so they are cheaper to run.",
                "MoE মডেল মোট আকারে বড়, কিন্তু প্রতিটি টোকেনে অল্প একটা অংশ চলে, তাই চালাতে সস্তা।"),
               ("Tricks like MLA and sliding-window attention make long inputs cheaper to handle.",
                "MLA আর স্লাইডিং-উইন্ডো অ্যাটেনশনের মতো কৌশল লম্বা ইনপুট সামলানো সস্তা করে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
