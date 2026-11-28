"""Part ai-engineering-book · ch8 Dataset Engineering.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Bad data  "No amount of compute or model skill can fix bad data." "Dataset engineering means building data that is good, covers real use, and is big enough, within your budget."
  2 Three     "the same three questions decide whether a dataset is good: is it high quality, does it have good coverage, and is there enough of it?" Coverage "Also called data diversity."
  3 Quality   "A few thousand careful examples can match or beat hundreds of thousands of messy ones."
  4 How much  "finetune on 25%, 50%, and 100% of it and plot the results." "A steep slope means more data will keep helping; a flat one means you're near the ceiling."
  5 Synthesis "Data synthesis: Making data that mimics real data without being built from one specific real example. It can be made with rules, simulation, or an AI model." Reverse instruction.
  6 Check     "Synthetic data still needs checking: run code tests, use an AI judge, or filter with simple rules." Model collapse.
  7 Distill   "Training a small student model to imitate a large teacher model, usually on data the teacher made."
  8 Prepare   "Before training, inspect, deduplicate, clean, and format the data to match what the target model expects." Deduplication: "Removing exact and near-duplicate examples from the data."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "file", ("Training data", "ট্রেনিং ডেটা"), 110, 162),
    node("model", "model", ("Model", "মডেল"), 620, 162),
    node("quality", "shield", ("Quality", "মান"), 320, 162),
    node("coverage", "chart", ("Coverage", "কভারেজ"), 520, 70),
    node("quantity", "storage", ("Quantity", "পরিমাণ"), 520, 254),
    node("plot", "chart", ("Plot the results", "ফল প্লট"), 480, 162),
    node("synth", "model", ("Data synthesis", "ডেটা সিন্থেসিস"), 400, 162),
    node("checks", "tool", ("Checks", "যাচাই"), 640, 162),
    node("teacher", "model", ("Teacher model", "teacher মডেল"), 160, 162),
    node("student", "model", ("Student model", "student মডেল"), 600, 162),
    node("process", "tool", ("Process", "প্রসেস"), 400, 162),
]

METRICS = [
    ("Quality", "মান"),
    ("Quantity", "পরিমাণ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Bad data", "খারাপ ডেটা"),
       ("Bad data cannot be fixed", "খারাপ ডেটা ঠিক করা যায় না"),
       [("No amount of compute or model skill can fix bad data.",
         "কোনো কম্পিউট বা দক্ষতা দিয়েই খারাপ ডেটা ঠিক করা যায় না।"),
        ("Dataset engineering means building data that is good, covers real use, and is big enough, within your budget.",
         "ডেটাসেট ইঞ্জিনিয়ারিং মানে বাজেটের মধ্যে এমন ডেটা বানানো, যা ভালোমানের, বাস্তব ব্যবহারের সব দিক ছোঁয় আর যথেষ্ট বড়।")],
       [sh("data", "warn", ("bad data", "খারাপ ডেটা")), sh("model", "hot")],
       [ln("data", "model", "to", state="warn")],
       [None, None]),

    st(("Three", "তিন প্রশ্ন"),
       ("Quality, coverage, quantity", "মান, কভারেজ, পরিমাণ"),
       [("The same three questions decide whether a dataset is good: is it high quality, does it have good coverage, and is there enough of it?",
         "একই তিনটি প্রশ্ন ঠিক করে ডেটাসেট ভালো কি না: মান ভালো কি না, কভারেজ ভালো কি না, আর যথেষ্ট পরিমাণ আছে কি না।"),
        ("Coverage means your data spans the inputs the model will see in real use. It is also called data diversity.",
         "কভারেজ মানে বাস্তবে মডেল যত ধরনের ইনপুট পাবে, আপনার ডেটা তা ছোঁয়। একে data diversity-ও বলে।")],
       [sh("data", "hot"), sh("quality", "hot", ("high quality?", "ভালো মান?")), sh("coverage", "hot", ("good coverage?", "ভালো কভারেজ?")), sh("quantity", "hot", ("enough of it?", "যথেষ্ট?"))],
       [ln("data", "quality", "to", state="hot"), ln("quality", "coverage", "to", state="hot"), ln("quality", "quantity", "to", state="hot")],
       [("high quality?", "ভালো মান?"), ("enough of it?", "যথেষ্ট?")]),

    st(("Quality", "মান"),
       ("Careful beats messy", "যত্নের ডেটা এলোমেলোকে হারায়"),
       [("A few thousand careful examples can match or beat hundreds of thousands of messy ones.",
         "কয়েক হাজার যত্নে লেখা উদাহরণ কয়েক লাখ এলোমেলো উদাহরণের সমান বা তার চেয়ে ভালো ফল দিতে পারে।"),
        ("Good data beats more data, almost every time.",
         "ভালো ডেটা বেশি ডেটাকে প্রায় সব সময় হারায়।")],
       [sh("quality", "hot", ("a few thousand careful", "কয়েক হাজার যত্নের")), sh("quantity", "dim", ("hundreds of thousands messy", "কয়েক লাখ এলোমেলো")), sh("model", "hot")],
       [ln("quality", "model", "to", state="hot"), ln("quantity", "model", "to", state="dim")],
       [("careful", "যত্নের"), ("messy", "এলোমেলো")]),

    st(("How much", "কত ডেটা"),
       ("Plot size against results", "আকারের সাথে ফল প্লট করুন"),
       [("To judge how much data you need, finetune on 25%, 50%, and 100% of it and plot the results.",
         "কত ডেটা লাগবে বুঝতে ডেটার ২৫%, ৫০% আর ১০০% দিয়ে ফাইন-টিউন করে ফল প্লট করুন।"),
        ("A steep slope means more data will keep helping; a flat one means you're near the ceiling.",
         "খাড়া ঢালের মানে আরও ডেটা কাজে দেবে; সমতল ঢালের মানে আপনি সীমার কাছে।")],
       [sh("data", "hot", ("25%, 50%, 100%", "২৫%, ৫০%, ১০০%")), sh("plot", "hot", ("steep or flat", "খাড়া না সমতল"))],
       [ln("data", "plot", "to", state="hot")],
       [None, ("how much data", "কত ডেটা")]),

    st(("Synthesis", "সিন্থেসিস"),
       ("Make data that mimics real data", "আসল ডেটার মতো ডেটা বানান"),
       [("Data synthesis makes data that mimics real data without being built from one specific real example.",
         "ডেটা সিন্থেসিস কোনো একটি নির্দিষ্ট আসল উদাহরণ থেকে তৈরি না করে আসল ডেটার মতো ডেটা বানায়।"),
        ("It can be made with rules, simulation, or an AI model. Reverse instruction starts from good existing text and asks the model to write the instruction that would have produced it.",
         "এটা নিয়ম, সিমুলেশন বা একটি AI মডেল দিয়ে বানানো যায়। রিভার্স ইনস্ট্রাকশনে ভালো লেখা নিয়ে শুরু করে মডেলকে সেই লেখা তৈরি করতে পারে এমন ইনস্ট্রাকশন লিখতে বলা হয়।")],
       [sh("data", "dim", ("real data", "আসল ডেটা")), sh("synth", "hot", ("rules, simulation, AI", "নিয়ম, সিমুলেশন, AI"))],
       [ln("data", "synth", "to", state="dim")],
       [None, None]),

    st(("Check", "যাচাই"),
       ("Synthetic data needs checking", "synthetic ডেটা যাচাই করতে হয়"),
       [("Synthetic data still needs checking: run code tests, use an AI judge, or filter with simple rules.",
         "synthetic ডেটাও যাচাই করতে হয়: কোড টেস্ট চালান, AI judge ব্যবহার করুন, বা সহজ নিয়মে ছেঁকে নিন।"),
        ("Model collapse is when a model gets worse over generations, trained again and again on AI-made data.",
         "মডেল কোলাপ্স হলো বারবার AI-র বানানো ডেটায় ট্রেনিং করালে মডেল প্রজন্মের পর প্রজন্মে খারাপ হওয়া।")],
       [sh("synth", "warn", ("AI-made data", "AI-র বানানো ডেটা")), sh("checks", "hot", ("tests, AI judge, rules", "টেস্ট, AI judge, নিয়ম"))],
       [ln("synth", "checks", "to", state="hot")],
       [None, None],
       note=("warn", "Training again and again on AI-made data makes rare patterns fade.",
             "বারবার AI-র বানানো ডেটায় ট্রেনিং করালে বিরল প্যাটার্ন মিলিয়ে যায়।")),

    st(("Distill", "ডিস্টিলেশন"),
       ("A student imitates a teacher", "student শেখে teacher-এর নকল করে"),
       [("Model distillation trains a small student model to imitate a large teacher model.",
         "মডেল ডিস্টিলেশনে একটি ছোট student মডেলকে বড় teacher মডেলের নকল করতে শেখানো হয়।"),
        ("It is usually done on data the teacher made.",
         "এটা সাধারণত teacher-এর বানানো ডেটা দিয়ে করা হয়।")],
       [sh("teacher", "hot", ("large", "বড়")), sh("student", "hot", ("small", "ছোট"))],
       [ln("teacher", "student", "to", state="hot", label=("data the teacher made", "teacher-এর বানানো ডেটা"))],
       [None, None]),

    st(("Prepare", "প্রস্তুতি"),
       ("Process the data before training", "ট্রেনিংয়ের আগে ডেটা প্রসেস করুন"),
       [("Before training, inspect, deduplicate, clean, and format the data to match what the target model expects.",
         "ট্রেনিংয়ের আগে ডেটা inspect, deduplicate, clean আর format করুন, যাতে টার্গেট মডেলের চাহিদার সাথে মেলে।"),
        ("Deduplication removes exact and near-duplicate examples from the data.",
         "ডিডুপ্লিকেশন হুবহু এক বা প্রায় একই রকম উদাহরণ ডেটা থেকে সরিয়ে ফেলে।")],
       [sh("data", "hot", ("raw data", "কাঁচা ডেটা")), sh("process", "hot"), sh("model", "hot", ("what the model expects", "মডেল যা চায়"))],
       [ln("data", "process", "to", state="hot"), ln("process", "model", "to", state="hot")],
       [None, None],
       points=[("Four steps: inspect, deduplicate, clean, format.", "চারটি ধাপ: inspect, deduplicate, clean, format।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
