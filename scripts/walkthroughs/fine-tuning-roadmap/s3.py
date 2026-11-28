"""Part 7 · 03 Phase 3, fine-tuning open models: why a small add-on (LoRA, QLoRA) fits a free GPU when a full fine-tune does not.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Load      Body: "transformers loads the base model and tokenizer; datasets loads and preprocesses your cleaned data from Phase 1." Start here: the base model is "the original model you start from".
  2 Full      Table row "Full fine-tune": "Every weight in the model", "Large — out of reach on a free GPU for most models".
  3 Freeze    Body: "Instead of updating every one of a model's weights, the PEFT library's LoRA ... freezes the base model and trains a small add-on of extra weights alongside it."
  4 LoRA      Table row "LoRA": "A small set of added low-rank weights", "Moderate — fits a single consumer or free-tier GPU for small models".
  5 QLoRA     Table row "QLoRA": "Same as LoRA, on a 4-bit quantized base model", "Lowest — the usual choice on a free Colab GPU". Start here: "Quantized: Stored with fewer bits per number, so the model takes less memory."
  6 Free GPU  Callout: "A free Colab GPU is generally enough for small models: 1–3B parameters is comfortable, and QLoRA can stretch to about 7B."
  7 Changes   Warning: "transformers, datasets, and PEFT change fast. Follow the current official docs for each release rather than an old tutorial."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "file", ("Your cleaned data", "আপনার পরিষ্কার ডেটা"), 135, 162),
    node("ds", "tool", ("datasets", "datasets"), 260, 70),
    node("tf", "tool", ("transformers", "transformers"), 260, 254),
    node("base", "model", ("Base model", "বেস মডেল"), 430, 162),
    node("peft", "tool", ("PEFT", "PEFT"), 260, 162),
    node("lora", "model", ("LoRA add-on", "LoRA অতিরিক্ত অংশ"), 430, 260),
    node("q4", "model", ("4-bit base model", "৪-বিট বেস মডেল"), 430, 162),
    node("gpu", "server", ("Free Colab GPU", "ফ্রি Colab GPU"), 650, 162),
    node("docs", "note", ("Current official docs", "বর্তমান অফিসিয়াল ডক"), 560, 162),
]

METRICS = [
    ("Trains", "ট্রেইন হয়"),
    ("GPU need", "GPU লাগে"),
    ("Free GPU", "ফ্রি GPU"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Load", "লোড"),
       ("Load the model and your data", "মডেল আর ডেটা লোড"),
       [("transformers loads the base model, the original model you start from, and its tokenizer.",
         "transformers বেস মডেল, মানে যে মূল মডেল থেকে শুরু করছেন, আর তার টোকেনাইজার লোড করে।"),
        ("datasets loads and prepares your cleaned data from Phase 1.",
         "datasets আপনার পরিষ্কার করা ডেটা লোড করে আর তৈরি করে, যা আপনি ফেজ ১-এ করেছেন।")],
       [sh("data", "hot"), sh("ds", "hot"), sh("tf", "hot"), sh("base", "hot")],
       [ln("data", "ds", "to", state="hot"), ln("tf", "base", "to", state="hot")],
       [None, None, None]),

    st(("Full", "ফুল"),
       ("A full fine-tune trains every weight", "ফুল ফাইন-টিউনে প্রতিটা ওয়েট ট্রেইন হয়"),
       [("A full fine-tune updates every weight in the model.",
         "ফুল ফাইন-টিউনে মডেলের প্রতিটা ওয়েট আপডেট হয়।"),
        ("That needs a large GPU, which is out of reach on a free GPU for most models.",
         "এতে বড় GPU লাগে, যা বেশির ভাগ মডেলের জন্য ফ্রি GPU-তে সম্ভব নয়।")],
       [sh("base", "warn", ("every weight", "প্রতিটা ওয়েট")), sh("gpu", "warn", ("Large", "বড়"))],
       [ln("base", "gpu", "to", state="warn")],
       [("every weight", "প্রতিটা ওয়েট"), ("Large", "বড়"), ("out of reach", "নাগালের বাইরে")]),

    st(("Freeze", "ফ্রিজ"),
       ("Freeze the base, train a small add-on", "বেস ফ্রিজ করুন, ছোট অংশ ট্রেইন করুন"),
       [("Instead of updating every weight, the PEFT library's LoRA freezes the base model.",
         "প্রতিটা ওয়েট বদলানোর বদলে PEFT লাইব্রেরির LoRA বেস মডেলটা ফ্রিজ করে।"),
        ("It trains a small add-on of extra weights alongside it.",
         "পাশে অতিরিক্ত ওয়েটের একটা ছোট অংশ ট্রেইন করে।")],
       [sh("peft", "hot"), sh("base", "dim", ("frozen", "ফ্রিজ করা")), sh("lora", "hot", ("small add-on", "ছোট অংশ"))],
       [ln("peft", "base", "to", state="hot"), ln("peft", "lora", "to", state="hot")],
       [None, None, None]),

    st(("LoRA", "LoRA"),
       ("LoRA: a moderate GPU is enough", "LoRA: মাঝারি GPU-ই যথেষ্ট"),
       [("LoRA trains a small set of added low-rank weights.",
         "LoRA যোগ করা কম-র‍্যাঙ্কের অল্প কিছু ওয়েট ট্রেইন করে।"),
        ("It needs a moderate GPU: it fits a single consumer or free-tier GPU for small models.",
         "এতে মাঝারি GPU লাগে: ছোট মডেলের জন্য একটা কনজিউমার বা ফ্রি-টিয়ার GPU-তে এটা ধরে যায়।")],
       [sh("base", "dim", ("frozen", "ফ্রিজ করা")), sh("lora", "hot", ("small add-on", "ছোট অংশ")), sh("gpu", "hot", ("Moderate", "মাঝারি"))],
       [ln("lora", "gpu", "to", state="hot")],
       [("small add-on", "ছোট অংশ"), ("Moderate", "মাঝারি"), ("small models", "ছোট মডেল")]),

    st(("QLoRA", "QLoRA"),
       ("QLoRA: LoRA on a 4-bit base", "QLoRA: ৪-বিট বেসের ওপর LoRA"),
       [("QLoRA is the same as LoRA, on a 4-bit quantized base model.",
         "QLoRA মানে LoRA-ই, কিন্তু ৪-বিট কোয়ান্টাইজড বেস মডেলের ওপর।"),
        ("Quantized means stored with fewer bits per number, so the model takes less memory.",
         "কোয়ান্টাইজড মানে প্রতিটি সংখ্যা কম বিটে রাখা, ফলে মডেল কম মেমরি নেয়।")],
       [sh("q4", "hot", ("fewer bits", "কম বিট")), sh("lora", "hot", ("small add-on", "ছোট অংশ")), sh("gpu", "hot", ("Lowest", "সর্বনিম্ন"))],
       [ln("q4", "gpu", "to", state="hot"), ln("lora", "gpu", "to", state="hot")],
       [("small add-on", "ছোট অংশ"), ("Lowest", "সর্বনিম্ন"), ("usual choice", "সচরাচর পছন্দ")],
       note=("tip", "QLoRA needs the least GPU memory. It is the usual choice on a free Colab GPU.",
             "QLoRA-তে GPU মেমরি সবচেয়ে কম লাগে। ফ্রি Colab GPU-তে এটাই সচরাচর পছন্দ।")),

    st(("Free GPU", "ফ্রি GPU"),
       ("What fits a free GPU", "ফ্রি GPU-তে কী ধরে"),
       [("A free Colab GPU is generally enough for small models.",
         "ছোট মডেলের জন্য একটা ফ্রি Colab GPU সাধারণত যথেষ্ট।"),
        ("1–3B parameters is comfortable, and QLoRA can stretch to about 7B.",
         "১–৩ বিলিয়ন প্যারামিটার স্বাচ্ছন্দ্যের, আর QLoRA দিয়ে প্রায় ৭ বিলিয়ন পর্যন্ত টানা যায়।")],
       [sh("gpu", "hot", ("1–3B comfortable", "১–৩B স্বাচ্ছন্দ্যের")), sh("q4", "hot", ("QLoRA: about 7B", "QLoRA: প্রায় ৭B")), sh("lora", "dim")],
       [ln("q4", "gpu", "to", state="hot"), ln("lora", "gpu", "to", state="dim")],
       [None, None, ("1–3B, QLoRA to about 7B", "১–৩B, QLoRA-তে প্রায় ৭B")]),

    st(("Changes", "বদল"),
       ("These libraries change fast", "এই লাইব্রেরিগুলো দ্রুত বদলায়"),
       [("transformers, datasets, and PEFT change fast.",
         "transformers, datasets আর PEFT দ্রুত বদলায়।"),
        ("Follow the current official docs, not an old tutorial.",
         "পুরনো টিউটোরিয়ালের বদলে বর্তমান অফিসিয়াল ডকুমেন্টেশন অনুসরণ করুন।")],
       [sh("docs", "hot"), sh("tf", "dim"), sh("ds", "dim"), sh("peft", "dim")],
       [ln("docs", "tf", "to", state="hot"), ln("docs", "ds", "to", state="hot"), ln("docs", "peft", "to", state="hot")],
       [None, None, None],
       note=("warn", "An old tutorial may use a removed argument or a renamed function.",
             "পুরনো টিউটোরিয়ালে এমন আর্গুমেন্ট থাকতে পারে যা সরানো হয়েছে, বা এমন ফাংশন যার নাম বদলেছে।")),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
