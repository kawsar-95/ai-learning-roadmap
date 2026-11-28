"""Fine-tuning roadmap · 01 Phase 1, Python for data: pandas, data hygiene, and why a fine-tuned model is only as good as its data.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Data first  Body: "A fine-tuned model cannot be better than the data it is shown." "This phase teaches you to read and clean data with pandas before any AI work begins."
  2 pandas      Start here: "A Python tool for reading, cleaning, and reshaping tables of data. Think of a spreadsheet with superpowers."
  3 Hygiene     Table rows "Duplicate rows" and "Mislabeled rows": drop_duplicates(), value_counts() audits, manual spot-checks, and the "Why it matters" cells.
  4 Splits      Start here: "Dividing data into three parts: one to learn from, one to check progress, and one for the final test."
  5 Leakage     Table row "Split leakage": "group-aware splits (e.g. by source document)", "Near-duplicate rows in train and test inflate your eval score". Start here: "It makes your test results look better than they really are."
  6 Imbalance   Start here: "When some kinds of label have far more examples than others. This can skew training."
  7 Remember    Info: "a small set of clean, correctly labeled examples often beats a much larger noisy one. Time spent auditing data pays off more than time spent tuning hyperparameters."; and the four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "file", ("Your data", "আপনার ডেটা"), 130, 162),
    node("pandas", "tool", ("pandas", "pandas"), 380, 162),
    node("clean", "file", ("Clean data", "পরিষ্কার ডেটা"), 630, 162),
    node("model", "model", ("Fine-tuned model", "ফাইন-টিউন করা মডেল"), 620, 162),
    node("train", "file", ("Train", "ট্রেন"), 380, 60),
    node("val", "file", ("Validation", "ভ্যালিডেশন"), 380, 162),
    node("test", "file", ("Test", "টেস্ট"), 380, 260),
]

METRICS = [
    ("Data", "ডেটা"),
    ("Splits", "স্প্লিট"),
    ("Test result", "টেস্টের ফল"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Data first", "আগে ডেটা"),
       ("Data comes first", "আগে ডেটা"),
       [("A fine-tuned model cannot be better than the data it is shown.",
         "ফাইন-টিউন করা মডেল তাকে দেখানো ডেটার চেয়ে ভালো হতে পারে না।"),
        ("This phase teaches you to read and clean data with pandas before any AI work begins.",
         "AI-এর কাজ শুরুর আগে এই ধাপে pandas দিয়ে ডেটা পড়া আর পরিষ্কার করা শেখা হয়।")],
       [sh("data", "hot"), sh("model", "hot", ("no better", "ভালো নয়"))],
       [ln("data", "model", "to", state="hot")],
       [None, None, None]),

    st(("pandas", "pandas"),
       ("pandas reads and cleans", "pandas পড়ে আর পরিষ্কার করে"),
       [("pandas is a Python tool for reading, cleaning, and reshaping tables of data.",
         "pandas ডেটার টেবিল পড়া, পরিষ্কার করা আর নতুন করে সাজানোর একটি Python টুল।"),
        ("Think of a spreadsheet with superpowers.",
         "ভাবুন সুপারপাওয়ারওয়ালা স্প্রেডশিট।")],
       [sh("data", "hot"), sh("pandas", "hot", ("a spreadsheet with superpowers", "সুপারপাওয়ারওয়ালা স্প্রেডশিট")), sh("clean", "hot")],
       [ln("data", "pandas", "to", state="hot"), ln("pandas", "clean", "to", state="hot")],
       [None, None, None]),

    st(("Hygiene", "হাইজিন"),
       ("Data hygiene", "ডেটা হাইজিন"),
       [("Data hygiene is keeping data clean: removing duplicates, fixing bad labels, and handling missing values.",
         "ডেটা হাইজিন মানে ডেটা পরিষ্কার রাখা: ডুপ্লিকেট সরানো, ভুল লেবেল ঠিক করা আর মিসিং ভ্যালু সামলানো।")],
       [sh("data", "warn", ("duplicates, bad labels", "ডুপ্লিকেট, ভুল লেবেল")), sh("pandas", "hot"), sh("clean", "hot")],
       [ln("data", "pandas", "to", state="warn"), ln("pandas", "clean", "to", state="hot")],
       [("cleaned", "পরিষ্কার"), None, None],
       changes=[("+", "Duplicate rows: drop_duplicates(). Duplicates let the model memorize instead of generalize.",
                 "ডুপ্লিকেট সারি: drop_duplicates()। ডুপ্লিকেট থাকলে মডেল সাধারণীকরণের বদলে মুখস্থ করে।"),
                ("+", "Mislabeled rows: value_counts() audits and manual spot-checks. A fine-tune learns your labels as ground truth, errors included.",
                 "ভুল লেবেলের সারি: value_counts() দিয়ে যাচাই আর হাতে স্পট-চেক। ফাইন-টিউন আপনার লেবেলকে সঠিক ধরে শেখে, ভুলসহ।")]),

    st(("Splits", "স্প্লিট"),
       ("Train, validation, test", "ট্রেন, ভ্যালিডেশন, টেস্ট"),
       [("Train, validation and test splits divide the data into three parts.",
         "ট্রেন, ভ্যালিডেশন আর টেস্ট স্প্লিটে ডেটা তিন ভাগ করা হয়।"),
        ("One part is to learn from, one to check progress, and one for the final test.",
         "একভাগ থেকে শেখা, একভাগে অগ্রগতি দেখা, আর একভাগ শেষ পরীক্ষার জন্য।")],
       [sh("clean", "hot", x=130, y=162), sh("train", "hot", ("learn from", "শেখা")), sh("val", "hot", ("check progress", "অগ্রগতি দেখা")),
        sh("test", "hot", ("final test", "শেষ পরীক্ষা"))],
       [ln("clean", "train", "to", state="hot"), ln("clean", "val", "to", state="hot"), ln("clean", "test", "to", state="hot")],
       [None, ("three parts", "তিন ভাগ"), None]),

    st(("Leakage", "লিকেজ"),
       ("Split leakage", "স্প্লিট লিকেজ"),
       [("Split leakage is when the same or nearly the same examples land in both train and test.",
         "স্প্লিট লিকেজ হলো একই বা প্রায় একই উদাহরণ ট্রেন আর টেস্ট দুই দিকেই চলে যাওয়া।"),
        ("It makes your test results look better than they really are. Use group-aware splits, for example by source document.",
         "এতে টেস্টের ফল আসলের চেয়ে ভালো দেখায়। গ্রুপ-সচেতন স্প্লিট ব্যবহার করুন, যেমন সোর্স ডকুমেন্ট ধরে।")],
       [sh("clean", "hot", ("group-aware splits", "গ্রুপ-সচেতন স্প্লিট"), x=130, y=162), sh("train", "warn", ("near-duplicates", "প্রায় একই")),
        sh("test", "warn", ("near-duplicates", "প্রায় একই"))],
       [ln("clean", "train", "to", state="hot"), ln("clean", "test", "to", state="warn")],
       [None, None, ("looks better than real", "আসলের চেয়ে ভালো দেখায়")]),

    st(("Imbalance", "ইমব্যালান্স"),
       ("Class imbalance", "ক্লাস ইমব্যালান্স"),
       [("Class imbalance is when some kinds of label have far more examples than others.",
         "ক্লাস ইমব্যালান্স হলো যখন কিছু ধরনের লেবেলের উদাহরণ অন্যগুলোর চেয়ে অনেক বেশি থাকে।"),
        ("This can skew training, so spot it before training starts.",
         "এতে ট্রেইনিং একদিকে ঝুঁকে যেতে পারে, তাই ট্রেইনিংয়ের আগেই এটা ধরুন।")],
       [sh("data", "warn", ("far more examples", "উদাহরণ অনেক বেশি")), sh("model", "warn", ("skewed", "একদিকে ঝোঁকা"))],
       [ln("data", "model", "to", state="warn")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A small set of clean, correctly labeled examples often beats a much larger noisy one.",
         "অল্প কিছু পরিষ্কার, সঠিক লেবেলের উদাহরণ প্রায়ই অনেক বড় এলোমেলো ডেটাসেটের চেয়ে ভালো।")],
       [sh("data", "hot"), sh("pandas", "hot"), sh("clean", "hot")],
       [ln("data", "pandas", "to", state="hot"), ln("pandas", "clean", "to", state="hot")],
       [None, None, None],
       points=[("A fine-tuned model cannot be better than the data it is shown.",
                "ফাইন-টিউন করা মডেল তাকে দেখানো ডেটার চেয়ে ভালো হতে পারে না।"),
               ("A small set of clean, correctly labeled examples often beats a much larger noisy one.",
                "অল্প কিছু পরিষ্কার, সঠিক লেবেলের উদাহরণ প্রায়ই অনেক বড় এলোমেলো ডেটাসেটের চেয়ে ভালো।"),
               ("Auditing your data pays off more than tuning hyperparameters.",
                "হাইপারপ্যারামিটার ঠিক করার চেয়ে ডেটা যাচাই করায় বেশি লাভ হয়।"),
               ("Split data so similar examples do not leak across splits.",
                "ডেটা এমনভাবে ভাগ করুন, যাতে একই ধরনের উদাহরণ দুই ভাগে ফাঁস না হয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
