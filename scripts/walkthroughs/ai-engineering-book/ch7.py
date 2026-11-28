"""Part ai-engineering-book · 11 Finetuning: when to finetune, and the memory it needs.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Finetuning Body, "Finetuning overview": "Finetuning is extra training you run on top of a pre-trained foundation model, using your own task-specific data ... finetuning nudges that knowledge toward your task. It usually needs far fewer examples than training from scratch."
  2 Two kinds  Body: "Supervised finetuning trains the model on (input, output) pairs so it follows instructions and produces the right format. Preference finetuning trains the model on (instruction, better response, worse response) comparisons so it generates answers people prefer."
  3 When       Body, "When to finetune": "Finetuning is expensive in data, compute, and ML expertise, so it should usually come after you have already pushed prompting as far as it goes." The good reasons and the reasons to think twice.
  4 Form       Body, "Finetuning or RAG": "finetuning is for form, and RAG is for facts. If the model lacks or has outdated information, retrieval usually helps more than finetuning. If the model's facts are fine but its tone, structure, or syntax is wrong ..., finetuning is the better tool."
  5 Path       Info box, "A typical path": prompt engineering; more examples in the prompt; retrieval (RAG) for information gaps; finetuning for the remaining behavioral or formatting problems; RAG and finetuning combined, if you need the last bit of performance.
  6 Memory     Body, "Memory bottlenecks": "Every trainable parameter needs memory for its weight, its gradient, and one or two optimizer values. A frozen parameter needs none of that extra memory." Table (7B-parameter model, 16-bit): 14 GB, ~17 GB, 56 GB total.
  7 Quantize   Body, "Numerical representations and quantization": "Quantization means converting a model to a format with fewer bits per value. It shrinks memory roughly in proportion to the bits saved, and it often speeds up computation too, at the cost of some precision." Post-training quantization, mixed precision.
  8 Remember   The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("base", "model", ("Pre-trained model", "ট্রেইন করা মডেল"), 380, 162),
    node("data", "file", ("Your task data", "আপনার কাজের ডেটা"), 130, 250),
    node("pairs", "file", ("Input and right output", "ইনপুট আর সঠিক আউটপুট"), 130, 75),
    node("pref", "file", ("Better and worse response", "ভালো আর খারাপ উত্তর"), 130, 250),
    node("p1", "note", ("Prompt engineering", "প্রম্পট ইঞ্জিনিয়ারিং"), 130, 75),
    node("p2", "note", ("More examples", "আরও উদাহরণ"), 380, 75),
    node("p3", "service", ("Retrieval (RAG)", "রিট্রিভাল (RAG)"), 650, 75),
    node("p4", "tool", ("Finetuning", "ফাইন-টিউনিং"), 250, 250),
    node("p5", "tool", ("RAG and finetuning", "RAG আর ফাইন-টিউনিং"), 520, 250),
    node("train", "model", ("Trainable parameters", "ট্রেইনেবল প্যারামিটার"), 130, 162),
    node("gpu", "server", ("GPU memory", "GPU মেমরি"), 650, 162),
    node("qmodel", "model", ("Fewer bits per value", "প্রতি মানে কম বিট"), 380, 162),
]

METRICS = [
    ("Weights only (inference)", "শুধু ওয়েট (ইনফারেন্স)"),
    ("Plus activations", "সঙ্গে অ্যাক্টিভেশন"),
    ("Full finetuning, total", "পুরো ফাইন-টিউনিং, মোট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and figures are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর হিসাব সেকশনের নিজের।",
)

STEPS = [
    st(("Finetuning", "ফাইন-টিউনিং"),
       ("Extra training on your data", "আপনার ডেটায় বাড়তি ট্রেনিং"),
       [("Finetuning is extra training you run on top of a pre-trained foundation model, using your own task-specific data.",
         "ফাইন-টিউনিং হলো আগে ট্রেইন করা ফাউন্ডেশন মডেলের ওপর আপনার নিজের কাজের ডেটায় বাড়তি ট্রেনিং।"),
        ("The model already knows a lot from pre-training, and finetuning nudges that knowledge toward your task. It usually needs far fewer examples than training from scratch.",
         "প্রি-ট্রেনিং থেকে মডেল অনেক কিছু জানে, আর ফাইন-টিউনিং সেই জ্ঞানকে আপনার কাজের দিকে ঝোঁকায়। শুরু থেকে ট্রেনিংয়ের চেয়ে এতে সাধারণত অনেক কম উদাহরণ লাগে।")],
       [sh("base", "hot", y=75), sh("data", "hot"), sh("p4", "hot", x=380, y=162)],
       [ln("base", "p4", "to", state="hot"), ln("data", "p4", "to", state="hot")],
       [None, None, None]),

    st(("Two kinds", "দুই ধরন"),
       ("Supervised and preference", "সুপারভাইজড আর প্রেফারেন্স"),
       [("Supervised finetuning trains the model on (input, output) pairs, so it follows instructions and produces the right format.",
         "সুপারভাইজড ফাইন-টিউনিংয়ে (ইনপুট, আউটপুট) জোড়া দিয়ে মডেল ট্রেইন হয়, যাতে সে নির্দেশ মানে আর ঠিক ফরম্যাটে লেখে।"),
        ("Preference finetuning trains it on (instruction, better response, worse response) comparisons, so it generates answers people prefer.",
         "প্রেফারেন্স ফাইন-টিউনিংয়ে (নির্দেশ, ভালো উত্তর, খারাপ উত্তর) তুলনা দিয়ে ট্রেনিং হয়, যাতে মডেল মানুষের পছন্দের উত্তর লেখে।")],
       [sh("pairs", "hot", ("supervised", "সুপারভাইজড")), sh("pref", "hot", ("preference", "প্রেফারেন্স")), sh("base", "hot")],
       [ln("pairs", "base", "to", state="hot"), ln("pref", "base", "to", state="hot")],
       [None, None, None]),

    st(("When", "কখন"),
       ("Think before you finetune", "ফাইন-টিউনের আগে ভাবুন"),
       [("Finetuning is expensive in data, compute and ML expertise, so it should usually come after you have pushed prompting as far as it goes.",
         "ফাইন-টিউনিংয়ে ডেটা, কম্পিউট আর ML দক্ষতার খরচ বেশি, তাই সাধারণত প্রম্পটিং যতদূর যায় ততদূর ঠেলার পরেই এটা করা উচিত।"),
        ("It is not a replacement for prompting: the two are often combined.",
         "এটা প্রম্পটিংয়ের বিকল্প নয়: দুটো প্রায়ই একসাথে ব্যবহার হয়।")],
       [sh("p1", "hot", ("first", "আগে")), sh("p4", "hot", ("after", "পরে"), x=380, y=162)],
       [ln("p1", "p4", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Good reason: improving task-specific quality, such as following a strict output format",
                 "ভালো কারণ: কাজ-নির্দিষ্ট মান বাড়ানো, যেমন কড়া আউটপুট ফরম্যাট মানা"),
                ("+", "Good reason: adapting to a rare dialect or domain language, or mitigating specific biases with curated data",
                 "ভালো কারণ: বিরল উপভাষা বা ডোমেইনের ভাষায় মানানো, বা বাছাই করা ডেটা দিয়ে নির্দিষ্ট পক্ষপাত কমানো"),
                ("-", "Think twice: finetuning for one task can quietly hurt performance on others",
                 "দুবার ভাবুন: এক কাজের জন্য ফাইন-টিউনিং চুপচাপ অন্য কাজের পারফরম্যান্স নষ্ট করতে পারে"),
                ("-", "Think twice: a new base model often improves faster than you can re-finetune your own",
                 "দুবার ভাবুন: নতুন বেস মডেল প্রায়ই আপনার আবার ফাইন-টিউন করার চেয়ে দ্রুত ভালো হয়")]),

    st(("Form", "ফর্ম"),
       ("Finetuning is for form, RAG for facts", "ফর্মের জন্য ফাইন-টিউনিং, তথ্যের জন্য RAG"),
       [("If the model lacks or has outdated information, retrieval usually helps more than finetuning.",
         "মডেলের তথ্য না থাকলে বা পুরনো হলে সাধারণত ফাইন-টিউনিংয়ের চেয়ে রিট্রিভালই বেশি কাজে লাগে।"),
        ("If the facts are fine but the tone, structure or syntax is wrong, finetuning is the better tool.",
         "তথ্য ঠিক কিন্তু টোন, গঠন বা সিনট্যাক্স ভুল হলে ফাইন-টিউনিংই ভালো টুল।")],
       [sh("p3", "hot", ("facts", "তথ্য"), x=130, y=75), sh("p4", "hot", ("form", "ফর্ম"), x=130, y=250), sh("base", "hot")],
       [ln("p3", "base", "to", state="hot"), ln("p4", "base", "to", state="hot")],
       [None, None, None],
       note=("tip", "Finetuning is for form; RAG is for facts.",
             "ফাইন-টিউনিং ফর্মের জন্য; RAG তথ্যের জন্য।")),

    st(("Path", "পথ"),
       ("A typical path", "সাধারণ পথ"),
       [("A typical path is prompt engineering, then more examples in the prompt, then retrieval (RAG) for information gaps.",
         "সাধারণ পথ: প্রম্পট ইঞ্জিনিয়ারিং, তারপর প্রম্পটে আরও উদাহরণ, তারপর তথ্যের ঘাটতিতে রিট্রিভাল (RAG)।"),
        ("Next comes finetuning for the remaining behavioral or formatting problems, and RAG and finetuning combined if you need the last bit of performance.",
         "এরপর বাকি আচরণ বা ফরম্যাটের সমস্যায় ফাইন-টিউনিং, আর শেষ একটু পারফরম্যান্স লাগলে RAG আর ফাইন-টিউনিং একসাথে।")],
       [sh("p1", "hot"), sh("p2", "hot"), sh("p3", "hot"), sh("p4", "hot"), sh("p5", "hot")],
       [ln("p1", "p2", "to", state="hot"), ln("p2", "p3", "to", state="hot"), ln("p3", "p4", "to", state="hot"), ln("p4", "p5", "to", state="hot")],
       [None, None, None]),

    st(("Memory", "মেমরি"),
       ("Training needs far more memory", "ট্রেনিংয়ে অনেক বেশি মেমরি লাগে"),
       [("Every trainable parameter needs memory for its weight, its gradient, and one or two optimizer values. A frozen parameter needs none of that extra memory.",
         "প্রতিটি ট্রেইনেবল প্যারামিটারের ওয়েট, গ্রেডিয়েন্ট আর এক-দুটো অপটিমাইজার মানের জন্য মেমরি লাগে। ফ্রিজ করা প্যারামিটারের এই বাড়তি মেমরি লাগে না।"),
        ("For a 7B-parameter model at 16-bit, loading the weights takes 14 GB, and full finetuning takes 56 GB in total.",
         "১৬-বিটের ৭B-প্যারামিটার মডেলে ওয়েট লোড করতে ১৪ GB লাগে, আর পুরো ফাইন-টিউনিংয়ে মোট ৫৬ GB লাগে।")],
       [sh("train", "warn", ("weight, gradient, optimizer", "ওয়েট, গ্রেডিয়েন্ট, অপটিমাইজার")), sh("gpu", "warn")],
       [ln("train", "gpu", "to", state="warn")],
       ["14 GB", "~17 GB", "56 GB"]),

    st(("Quantize", "কোয়ান্টাইজ"),
       ("Fewer bits per value", "প্রতি মানে কম বিট"),
       [("Quantization means converting a model to a format with fewer bits per value. It shrinks memory roughly in proportion to the bits saved, and it often speeds up computation too, at the cost of some precision.",
         "কোয়ান্টাইজেশন মানে মডেলকে এমন ফরম্যাটে আনা যেখানে প্রতি মানে বিট কম। বাঁচানো বিটের অনুপাতে মেমরি কমে, প্রায়ই গণনাও দ্রুত হয়, তবে কিছুটা প্রিসিশন যায়।"),
        ("It is usually done after training, since training itself is more sensitive to low precision.",
         "এটা সাধারণত ট্রেনিংয়ের পরে করা হয়, কারণ ট্রেনিং নিজে কম প্রিসিশনে বেশি সংবেদনশীল।")],
       [sh("base", "hot", ("FP16 or BF16", "FP16 বা BF16"), x=130), sh("qmodel", "hot", ("INT8 or INT4", "INT8 বা INT4")), sh("gpu", "hot", ("less memory", "কম মেমরি"))],
       [ln("base", "qmodel", "to", state="hot"), ln("qmodel", "gpu", "to", state="hot")],
       [None, None, None],
       note=("info", "When training in low precision is needed, mixed precision keeps sensitive values like gradients in a higher-precision format.",
             "কম প্রিসিশনে ট্রেনিং দরকার হলে মিক্সড প্রিসিশন গ্রেডিয়েন্টের মতো সংবেদনশীল মান বেশি প্রিসিশনে রাখে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Finetuning is extra training on your own data, on top of a model that is already trained.",
         "ফাইন-টিউনিং মানে আগে থেকে ট্রেইন করা মডেলকে আপনার নিজের ডেটায় বাড়তি ট্রেনিং দেওয়া।")],
       [sh("p3"), sh("p4"), sh("base")],
       [ln("p3", "base", "to"), ln("p4", "base", "to")],
       [None, None, None],
       points=[("Finetuning is for form; RAG is for facts.",
                "ফাইন-টিউনিং ফর্মের জন্য; RAG তথ্যের জন্য।"),
               ("Try prompting, more examples, and RAG before finetuning.",
                "ফাইন-টিউনিংয়ের আগে প্রম্পটিং, বেশি উদাহরণ আর RAG চেষ্টা করুন।"),
               ("Full finetuning of a 16-bit 7B model needs about 56 GB, versus about 14 GB just to load the weights for inference.",
                "১৬-বিটের ৭B মডেলের পুরো ফাইন-টিউনিংয়ে প্রায় ৫৬ GB লাগে, আর ইনফারেন্সের জন্য শুধু ওয়েট লোড করতে লাগে প্রায় ১৪ GB।"),
               ("Fewer trainable parameters or fewer bits per value both cut the memory bill.",
                "ট্রেইনেবল প্যারামিটার কমালে বা প্রতিটি মান কম বিটে রাখলে মেমরির খরচ কমে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
