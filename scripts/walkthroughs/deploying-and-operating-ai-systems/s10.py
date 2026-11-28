"""Part 14 · 10 MLOps: the loop from data to retraining, and why a model can get worse when nobody touches the code.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Why       Body: "A model can get worse even when nobody changes the code, because its data keeps changing. MLOps applies DevOps habits to keep such models tracked, deployed and watched."
  2 Loop      "The loop is: collect data, train, evaluate, register the model, deploy, monitor, and retrain. Each step is automated, so a new model reaches production the same way every time."
  3 Track     Table: Experiment tracking "Records the parameters, metrics and files of every training run"; Model registry "Versions a trained model and marks which one is in staging or production".
  4 Orchestrate Table: Orchestration "Runs the steps in order, on a schedule or when new data arrives".
  5 Features  Table: Feature store "Serves the same features in training and in production".
  6 Drift     "Data drift means the inputs no longer look like the training data. Concept drift means the right answer for the same input has changed. Watch the statistics of the inputs and, when true labels arrive later, the live accuracy."
  7 Hosted    Info: "If you call a hosted model you do not train it, so there is no retraining loop. ... This section matters when you fine-tune or serve your own models."
  8 Remember  The remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "database", ("Collect data", "ডেটা সংগ্রহ"), 115, 90),
    node("train", "model", ("Train", "ট্রেনিং"), 290, 90),
    node("eval", "chart", ("Evaluate", "ইভ্যালুয়েশন"), 460, 90),
    node("reg", "storage", ("Model registry", "মডেল রেজিস্ট্রি"), 650, 90),
    node("deploy", "server", ("Deploy", "ডিপ্লয়"), 640, 250),
    node("mon", "chart", ("Monitor", "মনিটর"), 440, 250),
    node("track", "file", ("Experiment tracking", "এক্সপেরিমেন্ট ট্র্যাকিং"), 290, 250),
    node("feat", "cache", ("Feature store", "ফিচার স্টোর"), 115, 250),
    node("hosted", "model", ("Hosted model", "হোস্টেড মডেল"), 150, 250),
]

METRICS = [
    ("Code", "কোড"),
    ("Data", "ডেটা"),
    ("Model", "মডেল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

LOOP = [("data", "train"), ("train", "eval"), ("eval", "reg"), ("reg", "deploy"), ("deploy", "mon"), ("mon", "train")]

STEPS = [
    st(("Why", "কেন"),
       ("A model can get worse alone", "মডেল নিজে থেকেই খারাপ হতে পারে"),
       [("A model can get worse even when nobody changes the code, because its data keeps changing.",
         "কোড কেউ না বদলালেও মডেল খারাপ হতে পারে, কারণ তার ডেটা বদলাতে থাকে।"),
        ("MLOps applies DevOps habits to keep such models tracked, deployed and watched.",
         "MLOps এমন মডেলকে ট্র্যাক, ডিপ্লয় আর পর্যবেক্ষণে রাখতে DevOps-এর অভ্যাস কাজে লাগায়।")],
       [sh("data", "warn", ("keeps changing", "বদলাতে থাকে")), sh("train", "hot", ("worse", "খারাপ")), sh("eval", "dim")],
       [ln("data", "train", "to", state="warn"), ln("train", "eval", "to", state="dim")],
       [None, ("keeps changing", "বদলাতে থাকে"), ("worse", "খারাপ")]),

    st(("Loop", "চক্র"),
       ("The loop", "চক্র"),
       [("The loop is: collect data, train, evaluate, register the model, deploy, monitor, and retrain.",
         "চক্রটা হলো: ডেটা সংগ্রহ, ট্রেনিং, ইভ্যালুয়েশন, রেজিস্ট্রিতে রাখা, ডিপ্লয়, মনিটর, আর আবার ট্রেনিং।"),
        ("Each step is automated, so a new model reaches production the same way every time.",
         "প্রতিটি ধাপ অটোমেট করা, যাতে নতুন মডেল প্রতিবার একই পথে প্রোডাকশনে যায়।")],
       [sh("data", "hot"), sh("train", "hot"), sh("eval", "hot"), sh("reg", "hot"), sh("deploy", "hot"), sh("mon", "hot")],
       [ln(a, b, "to", state="hot", label=(("retrain", "আবার ট্রেনিং") if (a, b) == ("mon", "train") else None)) for a, b in LOOP],
       [None, None, None]),

    st(("Track", "ট্র্যাক"),
       ("Track runs, register models", "রান ট্র্যাক, মডেল রেজিস্টার"),
       [("Experiment tracking records the parameters, metrics and files of every training run.",
         "এক্সপেরিমেন্ট ট্র্যাকিং প্রতিটি ট্রেনিং রানের প্যারামিটার, মেট্রিক আর ফাইল লিখে রাখে।"),
        ("A model registry versions each trained model and marks which one is in staging or production.",
         "মডেল রেজিস্ট্রি প্রতিটি ট্রেন করা মডেলের ভার্সন রাখে আর চিহ্নিত করে কোনটা স্টেজিং বা প্রোডাকশনে আছে।")],
       [sh("train", "hot"), sh("track", "hot", ("every run", "প্রতিটি রান")), sh("eval", "hot"), sh("reg", "hot", ("versions", "ভার্সন")), sh("deploy", "hot", ("staging or production", "স্টেজিং বা প্রোডাকশন"))],
       [ln("train", "track", "to", state="hot"), ln("eval", "reg", "to", state="hot"), ln("reg", "deploy", "to", state="hot")],
       [None, None, None]),

    st(("Orchestrate", "অর্কেস্ট্রেশন"),
       ("Orchestration runs the steps", "অর্কেস্ট্রেশন ধাপ চালায়"),
       [("Orchestration runs the steps in order.",
         "অর্কেস্ট্রেশন ধাপগুলো ক্রমে চালায়।"),
        ("It runs them on a schedule or when new data arrives.",
         "নির্দিষ্ট সময়ে বা নতুন ডেটা এলে চালায়।")],
       [sh("data", "hot", ("new data arrives", "নতুন ডেটা এলে")), sh("train", "hot", ("in order", "ক্রমে")), sh("eval", "hot", ("in order", "ক্রমে")), sh("reg", "hot", ("in order", "ক্রমে"))],
       [ln("data", "train", "to", state="hot"), ln("train", "eval", "to", state="hot"), ln("eval", "reg", "to", state="hot")],
       [None, None, None]),

    st(("Features", "ফিচার"),
       ("The same features everywhere", "সবখানে একই ফিচার"),
       [("A feature store gives the same input values, called features, in training and in production.",
         "ফিচার স্টোর ট্রেনিংয়ে আর প্রোডাকশনে একই ইনপুট মান, মানে ফিচার, দেয়।")],
       [sh("feat", "hot", ("same features", "একই ফিচার")), sh("train", "hot", ("in training", "ট্রেনিংয়ে")), sh("deploy", "hot", ("in production", "প্রোডাকশনে"))],
       [ln("feat", "train", "to", state="hot"), ln("feat", "deploy", "to", state="hot")],
       [None, None, None]),

    st(("Drift", "ড্রিফট"),
       ("Data drift and concept drift", "ডেটা ড্রিফট আর কনসেপ্ট ড্রিফট"),
       [("Data drift means the inputs no longer look like the data the model was trained on. Concept drift means the right answer for the same input has changed.",
         "ডেটা ড্রিফট মানে ইনপুট আর মডেলের ট্রেনিং ডেটার মতো দেখতে নেই। কনসেপ্ট ড্রিফট মানে একই ইনপুটের সঠিক উত্তর বদলে গেছে।"),
        ("Watch the statistics of the inputs and, when true labels arrive later, the live accuracy.",
         "ইনপুটের পরিসংখ্যান দেখুন, আর আসল লেবেল পরে এলে লাইভ accuracy দেখুন।")],
       [sh("data", "warn", ("data drift", "ডেটা ড্রিফট")), sh("deploy", "hot", ("concept drift", "কনসেপ্ট ড্রিফট")), sh("mon", "hot", ("live accuracy", "লাইভ accuracy"))],
       [ln("deploy", "mon", "to", state="hot")],
       [None, ("keeps changing", "বদলাতে থাকে"), ("worse", "খারাপ")],
       note=("warn", "A model can get worse without any code change.", "কোড না বদলেও মডেল খারাপ হতে পারে।")),

    st(("Hosted", "হোস্টেড"),
       ("Hosted model: no retraining loop", "হোস্টেড মডেল: রিট্রেনিং চক্র নেই"),
       [("If you only call a hosted model, there is no retraining loop.",
         "শুধু হোস্টেড মডেল কল করলে রিট্রেনিং চক্র নেই।"),
        ("This section matters when you fine-tune or serve your own.",
         "নিজে ফাইন-টিউন বা সার্ভ করলে এই সেকশন কাজে লাগে।")],
       [sh("hosted", "hot", ("you do not train it", "আপনি ট্রেন করেন না")), sh("train", "dim"), sh("mon", "dim")],
       [ln("hosted", "train", "to", state="dim")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A model can break while nobody touches the code, because its data keeps changing.",
         "কোড কেউ না ছুঁলেও মডেল খারাপ হতে পারে, কারণ তার ডেটা বদলাতে থাকে।")],
       [sh("data", "hot"), sh("train", "hot"), sh("eval", "hot"), sh("reg", "hot"), sh("deploy", "hot"), sh("mon", "hot")],
       [ln(a, b, "to") for a, b in LOOP],
       [None, None, None],
       points=[("The loop is: collect data, train, evaluate, register, deploy, monitor, and retrain.",
                "চক্রটা হলো: ডেটা সংগ্রহ, ট্রেনিং, ইভ্যালুয়েশন, রেজিস্ট্রিতে রাখা, ডিপ্লয়, মনিটর, আর আবার ট্রেনিং।"),
               ("Automate each step, so a new model reaches production the same way every time.",
                "প্রতিটি ধাপ অটোমেট করুন, যাতে নতুন মডেল প্রতিবার একই পথে প্রোডাকশনে যায়।"),
               ("Watch the statistics of the inputs and, when true labels arrive later, the live accuracy.",
                "ইনপুটের পরিসংখ্যান দেখুন, আর আসল লেবেল পরে এলে লাইভ accuracy দেখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
