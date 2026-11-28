"""Part ai-engineering-book · ch9 Inference Optimization: bottlenecks, metrics and accelerators.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Inference   "Inference means running a trained model to answer real requests. If it is too slow or too costly, people cannot use it." "The component that runs a model in production is the inference server."
  2 Levels      "Optimization can target the model, the hardware, or the service, and most systems combine more than one."
  3 Bottleneck  "Compute-bound: limited by how many calculations the hardware can do." "Memory bandwidth-bound: limited by how fast data moves between memory and the processor."
  4 Prefill     "Prefill reads the whole prompt at once. Decode then writes the answer one token at a time, reloading the model's weights each step." "Prefill is compute-bound. Decode is memory bandwidth-bound, and it dominates response time for long outputs."
  5 Latency     TTFT "depends on prefill and input length"; TPOT "depends on decode"; "Total latency is roughly TTFT plus TPOT times the number of output tokens."
  6 Throughput  "Throughput: output tokens per second across all requests. It is directly tied to compute cost." "Goodput: requests per second that meet a latency target, not just requests finished."
  7 Spread      "Latency is a spread, not one number. Teams report percentiles such as p50, p90, p95, and p99."
  8 Chips       "GPUs lead in AI because they pack thousands of smaller cores." "Compare chips on computational capability, memory size and bandwidth, and power consumption."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("request", "user", ("Request", "রিকোয়েস্ট"), 100, 162),
    node("server", "server", ("Inference server", "ইনফারেন্স সার্ভার"), 390, 162),
    node("model", "model", ("The model", "মডেল"), 110, 162),
    node("hw", "server", ("Hardware", "হার্ডওয়্যার"), 390, 162),
    node("svc", "service", ("Service", "সার্ভিস"), 650, 162),
    node("compute", "tool", ("Calculations", "হিসাব"), 190, 162),
    node("memory", "storage", ("Memory", "মেমোরি"), 570, 162),
    node("prefill", "service", ("Prefill", "প্রিফিল"), 330, 70),
    node("decode", "service", ("Decode", "ডিকোড"), 330, 254),
    node("answer", "file", ("Answer tokens", "উত্তরের টোকেন"), 620, 162),
    node("ttft", "clock", ("TTFT", "TTFT"), 250, 162),
    node("tpot", "clock", ("TPOT", "TPOT"), 510, 162),
]

METRICS = [
    ("TTFT", "TTFT"),
    ("TPOT", "TPOT"),
    ("Total latency", "মোট latency"),
    ("Throughput", "থ্রুপুট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Inference", "ইনফারেন্স"),
       ("Running a trained model", "ট্রেইন করা মডেল চালানো"),
       [("Inference means running a trained model to answer real requests.",
         "ইনফারেন্স মানে ট্রেইন করা মডেল চালিয়ে আসল রিকোয়েস্টের উত্তর দেওয়া।"),
        ("If it is too slow or too costly, people cannot use it.",
         "এটা খুব ধীর বা খুব খরচের হলে মানুষ ব্যবহার করতে পারে না।")],
       [sh("request", "hot"), sh("server", "hot", ("runs the model", "মডেল চালায়"))],
       [ln("request", "server", "to", state="hot")],
       [None, None, None, None]),

    st(("Levels", "স্তর"),
       ("Model, hardware or service", "মডেল, হার্ডওয়্যার বা সার্ভিস"),
       [("Optimization can target the model, the hardware, or the service.",
         "অপ্টিমাইজেশন হতে পারে মডেল, হার্ডওয়্যার বা সার্ভিসে।"),
        ("Most systems combine more than one.",
         "বেশিরভাগ সিস্টেম একাধিক স্তর মিলিয়ে ব্যবহার করে।")],
       [sh("model", "hot", ("smaller", "ছোট")), sh("hw", "hot", ("better chips", "ভালো চিপ")), sh("svc", "hot", ("manage requests", "রিকোয়েস্ট সামলানো"))],
       [ln("model", "hw", "to", state="hot"), ln("hw", "svc", "to", state="hot")],
       [None, None, None, None]),

    st(("Bottleneck", "বটলনেক"),
       ("Two bottlenecks", "দুই ধরনের বটলনেক"),
       [("A compute-bound task is limited by how many calculations the hardware can do.",
         "কম্পিউট-বাউন্ড কাজ আটকে থাকে হার্ডওয়্যার কতগুলো হিসাব করতে পারে তার ওপর।"),
        ("A memory bandwidth-bound task is limited by how fast data moves between memory and the processor.",
         "মেমোরি ব্যান্ডউইথ-বাউন্ড কাজ আটকে থাকে মেমোরি আর প্রসেসরের মধ্যে ডেটা কত দ্রুত যায় তার ওপর।")],
       [sh("compute", "hot", ("compute-bound", "compute-bound")), sh("memory", "hot", ("memory bandwidth-bound", "memory bandwidth-bound"))],
       [ln("memory", "compute", "to", state="hot", label=("data moves", "ডেটা যায়"))],
       [None, None, None, None]),

    st(("Prefill", "প্রিফিল"),
       ("Prefill reads, decode writes", "প্রিফিল পড়ে, ডিকোড লেখে"),
       [("Prefill reads the whole prompt at once. Decode then writes the answer one token at a time, reloading the model's weights each step.",
         "প্রিফিল পুরো প্রম্পট একবারে পড়ে। ডিকোড তারপর একবারে একটি টোকেন করে উত্তর লেখে, প্রতি ধাপে মডেলের ওয়েট আবার লোড করে।"),
        ("Prefill is compute-bound. Decode is memory bandwidth-bound, and it dominates response time for long outputs.",
         "প্রিফিল compute-bound। ডিকোড memory bandwidth-bound, আর লম্বা আউটপুটে ডিকোডই বেশি সময় নেয়।")],
       [sh("request", "hot", ("whole prompt", "পুরো প্রম্পট"), x=90), sh("prefill", "hot", ("compute-bound", "compute-bound")), sh("decode", "warn", ("memory bandwidth-bound", "memory bandwidth-bound")), sh("answer", "hot", ("one token at a time", "একবারে একটি টোকেন"))],
       [ln("request", "prefill", "to", state="hot"), ln("prefill", "decode", "to", state="hot"), ln("decode", "answer", "to", state="warn")],
       [None, None, None, None]),

    st(("Latency", "latency"),
       ("TTFT, TPOT and total latency", "TTFT, TPOT আর মোট latency"),
       [("TTFT is how long until the first token appears. It depends on prefill and input length.",
         "TTFT হলো প্রথম টোকেন আসতে কত সময় লাগে। এটা প্রিফিল আর ইনপুটের দৈর্ঘ্যের ওপর নির্ভর করে।"),
        ("TPOT is how quickly each later token arrives. It depends on decode.",
         "TPOT হলো পরের প্রতিটি টোকেন কত দ্রুত আসে। এটা ডিকোডের ওপর নির্ভর করে।")],
       [sh("ttft", "hot", ("prefill and input length", "প্রিফিল আর ইনপুটের দৈর্ঘ্য")), sh("tpot", "hot", ("decode", "ডিকোড"))],
       [ln("ttft", "tpot", "to", state="hot")],
       [("prefill, input length", "প্রিফিল, ইনপুটের দৈর্ঘ্য"), ("decode", "ডিকোড"), ("TTFT + TPOT × output tokens", "TTFT + TPOT × আউটপুট টোকেন"), None]),

    st(("Throughput", "থ্রুপুট"),
       ("Throughput and goodput", "থ্রুপুট আর গুডপুট"),
       [("Throughput is how much the service produces: output tokens per second across all requests. It is directly tied to compute cost.",
         "থ্রুপুট হলো সার্ভিস কতটা তৈরি করে: সব রিকোয়েস্ট মিলিয়ে প্রতি সেকেন্ডে কতগুলো আউটপুট টোকেন। এটা সরাসরি কম্পিউটের খরচের সাথে জড়িত।"),
        ("Goodput is requests per second that meet a latency target, not just requests finished.",
         "গুডপুট হলো প্রতি সেকেন্ডে কতগুলো রিকোয়েস্ট latency লক্ষ্য পূরণ করে। শুধু শেষ হওয়া রিকোয়েস্ট গোনা হয় না।")],
       [sh("request", "hot", ("all requests", "সব রিকোয়েস্ট")), sh("server", "hot", x=330), sh("answer", "hot", ("output tokens per second", "প্রতি সেকেন্ডে আউটপুট টোকেন"), x=620)],
       [ln("request", "server", "to", state="hot"), ln("server", "answer", "to", state="hot")],
       [None, None, None, ("output tokens per second", "প্রতি সেকেন্ডে আউটপুট টোকেন")]),

    st(("Spread", "বিস্তার"),
       ("Latency is a spread", "latency একটি বিস্তার"),
       [("Latency is a spread, not one number.",
         "latency একটি সংখ্যা নয়, একটি বিস্তার।"),
        ("A few slow outlier requests can badly skew an average. Teams report percentiles such as p50, p90, p95, and p99.",
         "কয়েকটি ধীর আউটলায়ার রিকোয়েস্ট গড়কে অনেক বিগড়ে দিতে পারে। টিমগুলো p50, p90, p95, p99 এর মতো পারসেন্টাইল জানায়।")],
       [sh("server", "hot", ("p50, p90, p95, p99", "p50, p90, p95, p99"))],
       [],
       [None, None, ("a spread", "একটি বিস্তার"), None]),

    st(("Chips", "চিপ"),
       ("Compare chips on three specs", "তিন দিকে চিপ তুলনা করুন"),
       [("An accelerator is a chip built for one kind of workload. GPUs lead in AI because they pack thousands of smaller cores.",
         "অ্যাক্সিলারেটর হলো একটি বিশেষ ধরনের কাজের জন্য বানানো চিপ। GPU-তে হাজার হাজার ছোট কোর থাকে, তাই AI-তে GPU এগিয়ে।"),
        ("Compare chips on computational capability, memory size and bandwidth, and power consumption.",
         "চিপ তুলনা করুন হিসাবের ক্ষমতা, মেমোরির আকার ও ব্যান্ডউইথ, আর বিদ্যুৎ খরচ দেখে।")],
       [sh("hw", "hot", ("thousands of smaller cores", "হাজার হাজার ছোট কোর"), x=150), sh("compute", "hot", ("computational capability", "হিসাবের ক্ষমতা"), x=470, y=75), sh("memory", "hot", ("memory size and bandwidth", "মেমোরির আকার ও ব্যান্ডউইথ"), x=470, y=250)],
       [ln("hw", "compute", "to", state="hot"), ln("hw", "memory", "to", state="hot")],
       [None, None, None, None],
       points=[("Also compare power consumption.", "আরও দেখুন বিদ্যুৎ খরচ।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
