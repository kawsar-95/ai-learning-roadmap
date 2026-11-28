"""Inference · 03 Hosted or self-hosted: the trade-off and the inference servers.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Hosted    Start here: "Most teams start by renting a hosted API." "Hosted API: A model that a vendor runs for you. You send requests and pay for what you use." "Start with a hosted API. It takes minutes, while self-hosting takes weeks." Table: Time to first token "Minutes"; Data privacy "Vendor's terms".
  2 Self-host Start here: "Self-hosted: Running the model yourself on your own GPU, so you control the setup and the data." "Inference server: The program that loads model weights into GPU memory and answers requests." Table: "You control everything".
  3 Trade-off Table: Time to first token "Minutes" / "Weeks (GPU procurement + ops)"; Cost per 1M tokens "$0.10 – $15" / "$0.04 – $2 (at scale)"; Data privacy; Model selection; Peak traffic; Customisation.
  4 Rule      Rule of thumb: "start hosted. Move to self-hosting once your bill exceeds the cost of a half-time ML engineer plus two H100s."
  5 Servers   "The five that matter in 2025": vLLM, TGI, SGLang, Ollama, llama.cpp, plus TensorRT-LLM / Triton, each with the line the section gives it. "TGI is now in maintenance mode; Hugging Face recommends vLLM or SGLang for new deployments."
  6 vLLM      Panel vLLM: "The throughput champion. PagedAttention + continuous batching improved throughput 2–4× over FasterTransformer and Orca at the same latency in the vLLM paper." Glossary: PagedAttention, Continuous batching.
  7 Small     Panels Ollama: "One-line CLI for local laptops and small servers. Best for dev and small-scale prod." llama.cpp: "CPU-first, GGUF-native, runs on phones and Raspberry Pis." Glossary: GGUF.
  8 Remember  Start here: the four points (start with a hosted API; self-hosting costs less per token at scale and gives full control of data; move when the bill exceeds ...; the servers).
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("app", "user", ("Your app", "আপনার অ্যাপ"), 90, 162),
    node("hosted", "cdn", ("Hosted API", "হোস্টেড API"), 360, 70),
    node("srv", "service", ("Inference server", "ইনফারেন্স সার্ভার"), 360, 254),
    node("gpu", "server", ("Your own GPU", "আপনার নিজের GPU"), 640, 254),
    node("bill", "chart", ("Your bill", "আপনার বিল"), 120, 162),
    node("cost", "note", ("Engineer plus two H100s", "ইঞ্জিনিয়ার আর দুটি H100"), 390, 162),
    node("vllm", "service", ("vLLM", "vLLM"), 330, 70),
    node("tgi", "service", ("TGI", "TGI"), 330, 162),
    node("sglang", "service", ("SGLang", "SGLang"), 330, 254),
    node("ollama", "service", ("Ollama", "Ollama"), 600, 70),
    node("llama", "service", ("llama.cpp", "llama.cpp"), 600, 162),
    node("trt", "service", ("TensorRT-LLM / Triton", "TensorRT-LLM / Triton"), 600, 254),
]

METRICS = [
    ("Time to first token", "টাইম টু ফার্স্ট টোকেন"),
    ("Cost per 1M tokens", "১M টোকেনে খরচ"),
    ("Data", "ডেটা"),
    ("Ops effort", "অপস প্রচেষ্টা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর অঙ্ক সেকশনের নিজস্ব।",
)

STEPS = [
    st(("Hosted", "হোস্টেড"),
       ("Start with a hosted API", "হোস্টেড API দিয়ে শুরু করুন"),
       [("A hosted API is a model that a vendor runs for you. You send requests and pay for what you use.",
         "হোস্টেড API হলো যে মডেল কোনো ভেন্ডর আপনার হয়ে চালায়। আপনি রিকোয়েস্ট পাঠান, আর যত ব্যবহার করেন তত টাকা দেন।"),
        ("Start here. It takes minutes, while self-hosting takes weeks.",
         "আগে এটা দিয়ে শুরু করুন। এতে মিনিট লাগে, আর সেলফ-হোস্টে লাগে কয়েক সপ্তাহ।")],
       [sh("app", "hot"), sh("hosted", "hot", ("vendor runs it", "ভেন্ডর চালায়"))],
       [ln("app", "hosted", "to", state="hot", label=("request", "রিকোয়েস্ট"))],
       [("Minutes", "মিনিট"), None, ("Vendor's terms", "ভেন্ডরের শর্ত"), None]),

    st(("Self-host", "সেলফ-হোস্ট"),
       ("Self-hosting: your own GPU", "সেলফ-হোস্ট: নিজের GPU"),
       [("Self-hosted means running the model yourself on your own GPU, so you control the setup and the data.",
         "সেলফ-হোস্টেড মানে নিজের GPU-তে নিজেই মডেল চালানো, ফলে সেটআপ আর ডেটা আপনার হাতে থাকে।"),
        ("An inference server is the program that loads model weights into GPU memory and answers requests.",
         "ইনফারেন্স সার্ভার হলো যে প্রোগ্রাম মডেলের ওয়েট GPU মেমরিতে তোলে আর রিকোয়েস্টের উত্তর দেয়।")],
       [sh("app", "hot"), sh("srv", "hot", ("loads the weights", "ওয়েট তোলে"), x=360, y=162), sh("gpu", "hot", ("you control it", "আপনার নিয়ন্ত্রণে"), x=640, y=162)],
       [ln("app", "srv", "to", state="hot"), ln("srv", "gpu", "to", state="hot")],
       [("Weeks", "সপ্তাহ"), None, ("You control everything", "সবকিছু আপনার নিয়ন্ত্রণে"), None]),

    st(("Trade-off", "ট্রেড-অফ"),
       ("The trade-off", "ট্রেড-অফ"),
       [("Hosted starts in minutes; self-hosting takes weeks. Per 1M tokens, hosted is $0.10 – $15 and self-hosted is $0.04 – $2 at scale.",
         "হোস্টেড মিনিটে শুরু হয়; সেলফ-হোস্টে লাগে কয়েক সপ্তাহ। ১M টোকেনে হোস্টেড $০.১০ – $১৫, আর স্কেলে সেলফ-হোস্টেড $০.০৪ – $২।")],
       [sh("hosted", "hot", ("Minutes", "মিনিট")), sh("srv", "hot", ("Weeks", "সপ্তাহ")), sh("app", "dim")],
       [ln("app", "hosted", "to", state="hot"), ln("app", "srv", "to", state="hot")],
       [("Minutes vs weeks", "মিনিট বনাম সপ্তাহ"), ("$0.10 – $15 vs $0.04 – $2", "$০.১০ – $১৫ বনাম $০.০৪ – $২"), ("Vendor's terms vs you", "ভেন্ডরের শর্ত বনাম আপনি"), None],
       changes=[("+", "Model selection: the vendor's catalogue, or anything you can fit on your GPU",
                 "মডেল বাছাই: ভেন্ডরের ক্যাটালগ, বা আপনার GPU-তে যা ধরে"),
                ("+", "Peak traffic: the vendor scales, or you scale",
                 "পিক ট্রাফিক: ভেন্ডর স্কেল করে, বা আপনি স্কেল করেন"),
                ("+", "Customisation: none or a fine-tune API, or full",
                 "কাস্টমাইজেশন: নেই বা ফাইন-টিউন API, বা পুরোপুরি")]),

    st(("Rule", "নিয়ম"),
       ("When to move", "কখন সরবেন"),
       [("Rule of thumb: start hosted.",
         "মোটামুটি নিয়ম: আগে হোস্টেড দিয়ে শুরু করুন।"),
        ("Move to self-hosting once your bill exceeds the cost of a half-time ML engineer plus two H100s.",
         "বিল আধা-সময়ের ML ইঞ্জিনিয়ার আর দুটি H100-এর খরচ ছাড়ালে সেলফ-হোস্টে যান।")],
       [sh("bill", "warn", ("exceeds", "ছাড়ালে")), sh("cost", "hot", ("half-time ML engineer", "আধা-সময়ের ML ইঞ্জিনিয়ার")), sh("srv", "hot", x=650, y=162)],
       [ln("bill", "cost", "to", state="warn"), ln("cost", "srv", "to", state="hot")],
       [None, None, None, None],
       note=("warn", "Self-hosting costs less per token at scale and gives you full control of your data.",
             "স্কেলে সেলফ-হোস্টে প্রতি টোকেনের খরচ কম, আর ডেটার পুরো নিয়ন্ত্রণ আপনার হাতে থাকে।")),

    st(("Servers", "সার্ভার"),
       ("The five servers, plus one", "পাঁচটি সার্ভার, সাথে আরও একটা"),
       [("Five main servers in 2025 are vLLM, TGI, SGLang, Ollama and llama.cpp.",
         "২০২৫-এ পাঁচটি প্রধান সার্ভার হলো vLLM, TGI, SGLang, Ollama আর llama.cpp।"),
        ("TensorRT-LLM / Triton is the fastest, but takes the most ops work.",
         "TensorRT-LLM / Triton সবচেয়ে দ্রুত, কিন্তু সবচেয়ে বেশি অপস কাজ লাগে।")],
       [sh("vllm", "hot"), sh("tgi", "hot"), sh("sglang", "hot"), sh("ollama", "hot"), sh("llama", "hot"), sh("trt", "hot")],
       [],
       [None, None, None, ("TensorRT-LLM / Triton: most", "TensorRT-LLM / Triton: সবচেয়ে বেশি")],
       changes=[("+", "SGLang: structured-output and multi-call programs",
                 "SGLang: স্ট্রাকচার্ড আউটপুট ও মাল্টি-কল প্রোগ্রামের জন্য"),
                ("+", "TGI: Hugging Face's server, now in maintenance mode; Hugging Face recommends vLLM or SGLang for new deployments",
                 "TGI: Hugging Face-এর সার্ভার, এখন maintenance mode-এ; নতুন ডিপ্লয়মেন্টের জন্য Hugging Face vLLM বা SGLang সুপারিশ করে")]),

    st(("vLLM", "vLLM"),
       ("vLLM: the throughput champion", "vLLM: থ্রুপুট চ্যাম্পিয়ন"),
       [("PagedAttention and continuous batching improved throughput 2–4× over FasterTransformer and Orca at the same latency in the vLLM paper.",
         "vLLM paper-এ PagedAttention আর কন্টিনিউয়াস ব্যাচিং একই ল্যাটেন্সিতে FasterTransformer ও Orca-র চেয়ে ২–৪× থ্রুপুট বাড়িয়েছে।"),
        ("PagedAttention stores the model's working memory in small pages, so little memory is wasted.",
         "PagedAttention মডেলের কাজের মেমরি ছোট ছোট পেজে রাখে, ফলে মেমরি কম নষ্ট হয়।")],
       [sh("srv", "hot", x=120, y=162), sh("vllm", "hot", ("PagedAttention", "PagedAttention"), x=420, y=162)],
       [ln("srv", "vllm", "to", state="hot")],
       [None, None, None, None],
       note=("tip", "vLLM has a Python API and an OpenAI-compatible HTTP server.",
             "vLLM-এ আছে Python API আর OpenAI-compatible HTTP সার্ভার।")),

    st(("Small", "ছোট"),
       ("Ollama and llama.cpp", "Ollama আর llama.cpp"),
       [("Ollama is a one-line CLI for local laptops and small servers, best for dev and small-scale prod.",
         "Ollama লোকাল ল্যাপটপ ও ছোট সার্ভারের জন্য এক-লাইনের CLI, ডেভ আর ছোট প্রোডের জন্য সেরা।"),
        ("llama.cpp is CPU-first and GGUF-native, and runs on phones and Raspberry Pis.",
         "llama.cpp হলো CPU-first, GGUF-native, ফোন ও Raspberry Pi-তেও চলে।")],
       [sh("ollama", "hot", ("laptops, small servers", "ল্যাপটপ, ছোট সার্ভার"), x=240, y=100), sh("llama", "hot", ("phones, Raspberry Pis", "ফোন, Raspberry Pi"), x=240, y=224)],
       [],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Start hosted, and self-host once the numbers justify it.",
         "আগে হোস্টেড দিয়ে শুরু করুন, আর হিসাবে পোষালে সেলফ-হোস্ট করুন।")],
       [sh("app"), sh("hosted"), sh("srv", x=360, y=254), sh("gpu")],
       [ln("app", "hosted", "to"), ln("app", "srv", "to"), ln("srv", "gpu", "to")],
       [None, None, None, None],
       points=[("Start with a hosted API. It takes minutes, while self-hosting takes weeks.",
                "আগে হোস্টেড API দিয়ে শুরু করুন। এতে মিনিট লাগে, আর সেলফ-হোস্টে লাগে কয়েক সপ্তাহ।"),
               ("Self-hosting costs less per token at scale and gives you full control of your data.",
                "স্কেলে সেলফ-হোস্টে প্রতি টোকেনের খরচ কম, আর ডেটার পুরো নিয়ন্ত্রণ আপনার হাতে থাকে।"),
               ("Move to self-hosting when your bill exceeds the cost of a half-time ML engineer plus two H100s.",
                "বিল আধা-সময়ের ML ইঞ্জিনিয়ার আর দুটি H100-এর খরচ ছাড়ালে সেলফ-হোস্টে যান।"),
               ("Five main servers in 2025 are vLLM, TGI, SGLang, Ollama and llama.cpp, plus TensorRT-LLM / Triton.",
                "২০২৫-এ পাঁচটি প্রধান সার্ভার হলো vLLM, TGI, SGLang, Ollama আর llama.cpp, সাথে TensorRT-LLM / Triton।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
