"""Fine-Tuning Small Models · 06 Capstone and the full timeline: a realistic project on anonymized or synthetic data, and roughly 4-6 months in all.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Capstone  Start here: "A good capstone is a realistic project built only on anonymized or synthetic data." "Capstone: A final project that pulls together everything you learned and shows your skill."
  2 Idea      Body: "Fine-tune a small model to turn requirements into test cases, or to classify bug reports." "Classify: Give each item a label, such as putting a bug report into a group."
  3 Data      Danger callout: "Never fine-tune on real company or employee data ... Use anonymized or synthetic examples instead". "Anonymized data: Real data with the names and personal details removed". "Synthetic data: Made-up examples".
  4 Timeline  Table "The full timeline": the five phases and their durations (part-time).
  5 Total     Table row "Total": "Roughly 4–6 months". "Treat the total as an estimate, not a deadline."
  6 Hygiene   Body: "time spent getting Phase 1's data hygiene right shortens every phase after it." "Data hygiene: Keeping your data clean and correct before you use it."
  7 Remember  Start here: the four points (capstone, never real data, 4-6 months part-time, estimate); last paragraph: "what matters is finishing each phase before starting the next".
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("req", "file", ("Requirements", "রিকোয়ারমেন্ট"), 120, 90),
    node("bug", "file", ("Bug reports", "বাগ রিপোর্ট"), 120, 234),
    node("mdl", "model", ("Small model", "ছোট মডেল"), 400, 162),
    node("real", "shield", ("Real company or employee data", "আসল কোম্পানি বা কর্মীর ডেটা"), 150, 162),
    node("anon", "file", ("Anonymized data", "অ্যানোনিমাইজড ডেটা"), 530, 90),
    node("syn", "file", ("Synthetic data", "সিন্থেটিক ডেটা"), 530, 234),
    node("p1", "clock", ("Python for data", "ডেটার জন্য Python"), 130, 90),
    node("p2", "clock", ("How neural nets train", "নিউরাল নেট কীভাবে ট্রেইন হয়"), 390, 90),
    node("p3", "clock", ("Fine-tuning open models", "ওপেন মডেল ফাইন-টিউনিং"), 640, 90),
    node("p4", "clock", ("Evaluation", "ইভ্যালুয়েশন"), 260, 250),
    node("p5", "clock", ("Run it locally and ship it", "লোকালি চালানো আর শিপ করা"), 520, 250),
]

METRICS = [
    ("Data", "ডেটা"),
    ("Total", "মোট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels and durations are the section's own.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেল আর সময় সেকশনের নিজস্ব।",
)

PH = [
    ("p1", ("3–4 weeks", "৩–৪ সপ্তাহ")),
    ("p2", ("4–6 weeks", "৪–৬ সপ্তাহ")),
    ("p3", ("6–8 weeks", "৬–৮ সপ্তাহ")),
    ("p4", ("2–3 weeks", "২–৩ সপ্তাহ")),
    ("p5", ("3–4 weeks", "৩–৪ সপ্তাহ")),
]

STEPS = [
    st(("Capstone", "ক্যাপস্টোন"),
       ("A good capstone", "ভালো ক্যাপস্টোন"),
       [("A capstone is a final project that pulls together everything you learned and shows your skill.",
         "ক্যাপস্টোন শেষের প্রজেক্ট, যেখানে যা শিখেছেন সব একসাথে কাজে লাগে আর আপনার দক্ষতা দেখা যায়।"),
        ("A good one is a realistic project built only on anonymized or synthetic data.",
         "ভালো ক্যাপস্টোন হলো একটা বাস্তবসম্মত প্রজেক্ট, যা শুধু অ্যানোনিমাইজড বা সিন্থেটিক ডেটার উপর দাঁড়িয়ে।")],
       [sh("anon", "hot"), sh("syn", "hot"), sh("mdl", "hot", ("capstone", "ক্যাপস্টোন"))],
       [ln("anon", "mdl", "to", state="hot"), ln("syn", "mdl", "to", state="hot")],
       [("Anonymized or synthetic", "অ্যানোনিমাইজড বা সিন্থেটিক"), None]),

    st(("Idea", "আইডিয়া"),
       ("The capstone idea", "ক্যাপস্টোনের আইডিয়া"),
       [("Fine-tune a small model to turn requirements into test cases, or to classify bug reports.",
         "ছোট একটা মডেল ফাইন-টিউন করুন, যা রিকোয়ারমেন্ট থেকে টেস্ট কেস বানায় বা বাগ রিপোর্ট ক্লাসিফাই করে।"),
        ("To classify is to give each item a label, such as putting a bug report into a group.",
         "ক্লাসিফাই মানে প্রতিটি জিনিসকে একটি লেবেল দেওয়া, যেমন বাগ রিপোর্টকে একটা দলে রাখা।")],
       [sh("req", "hot", ("into test cases", "টেস্ট কেসে")), sh("bug", "hot", ("classify", "ক্লাসিফাই")), sh("mdl", "hot", ("fine-tuned", "ফাইন-টিউন করা"))],
       [ln("req", "mdl", "to", state="hot"), ln("bug", "mdl", "to", state="hot")],
       [None, None]),

    st(("Data", "ডেটা"),
       ("Never real company data", "আসল কোম্পানির ডেটা কখনো নয়"),
       [("Never fine-tune on real company or employee data, even for a personal project.",
         "ব্যক্তিগত প্রজেক্টেও আসল কোম্পানি বা কর্মীর ডেটা দিয়ে ফাইন-টিউন করবেন না।"),
        ("Use anonymized or synthetic examples instead.",
         "অ্যানোনিমাইজড বা সিন্থেটিক উদাহরণ ব্যবহার করুন।")],
       [sh("real", "warn", ("never", "কখনো নয়")), sh("anon", "hot", ("names removed", "নাম সরানো")), sh("syn", "hot", ("made-up examples", "কাল্পনিক উদাহরণ")), sh("mdl", "hot")],
       [ln("real", "mdl", "to", state="warn"), ln("anon", "mdl", "to", state="hot"), ln("syn", "mdl", "to", state="hot")],
       [("Anonymized or synthetic", "অ্যানোনিমাইজড বা সিন্থেটিক"), None],
       note=("warn", "The risk of leaking sensitive data through a model is not worth the convenience.",
             "সুবিধার জন্য মডেলের মাধ্যমে সংবেদনশীল ডেটা ফাঁস হওয়ার ঝুঁকি নেওয়ার মানে হয় না।")),

    st(("Timeline", "টাইমলাইন"),
       ("The full timeline", "পুরো টাইমলাইন"),
       [("The roadmap has five phases, and each has its own part-time duration.",
         "রোডম্যাপে পাঁচটা ফেজ, আর প্রতিটার নিজের পার্ট-টাইম সময় আছে।")],
       [sh(p, "hot", d) for p, d in PH],
       [ln("p1", "p2", "to", state="hot"), ln("p2", "p3", "to", state="hot"), ln("p3", "p4", "to", state="hot"), ln("p4", "p5", "to", state="hot")],
       [None, None]),

    st(("Total", "মোট"),
       ("Roughly 4–6 months", "আনুমানিক ৪–৬ মাস"),
       [("The full timeline takes roughly 4–6 months, part-time.",
         "পুরো টাইমলাইনে পার্ট-টাইমে আনুমানিক ৪–৬ মাস লাগে।"),
        ("Treat the total as an estimate, not a deadline.",
         "মোট সময়টাকে একটা হিসাব হিসেবে দেখুন, ডেডলাইন হিসেবে নয়।")],
       [sh(p, "hot") for p, _ in PH],
       [ln("p1", "p2", "to", state="hot"), ln("p2", "p3", "to", state="hot"), ln("p3", "p4", "to", state="hot"), ln("p4", "p5", "to", state="hot")],
       [None, ("Roughly 4–6 months", "আনুমানিক ৪–৬ মাস")]),

    st(("Hygiene", "হাইজিন"),
       ("Phase 1 data hygiene pays off", "Phase ১-এর ডেটা হাইজিনের ফল"),
       [("The phases build on each other. Time spent getting Phase 1's data hygiene right shortens every phase after it.",
         "ফেজগুলো একে অপরের উপর দাঁড়িয়ে আছে। Phase ১-এ ডেটা হাইজিন ঠিক করতে সময় দিলে পরের প্রতিটা ফেজের সময় কমে।"),
        ("Data hygiene means keeping your data clean and correct before you use it.",
         "ডেটা হাইজিন মানে ডেটা ব্যবহারের আগে তা পরিষ্কার আর ঠিক রাখা।")],
       [sh("p1", "hot", ("data hygiene", "ডেটা হাইজিন")), sh("p2", "dim"), sh("p3", "dim"), sh("p4", "dim"), sh("p5", "dim")],
       [ln("p1", "p2", "to", state="hot"), ln("p2", "p3", "to", state="dim"), ln("p3", "p4", "to", state="dim"), ln("p4", "p5", "to", state="dim")],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("What matters is finishing each phase before starting the next.",
         "যেটা জরুরি তা হলো পরেরটা শুরুর আগে প্রতিটা ফেজ শেষ করা।")],
       [sh("req"), sh("bug"), sh("mdl"), sh("anon"), sh("syn")],
       [ln("req", "mdl", "to"), ln("bug", "mdl", "to"), ln("anon", "mdl", "to"), ln("syn", "mdl", "to")],
       [None, None],
       points=[("For the capstone, fine-tune a small model to turn requirements into test cases or to classify bug reports.",
                "ক্যাপস্টোনের জন্য, ছোট একটা মডেল ফাইন-টিউন করুন, যা রিকোয়ারমেন্ট থেকে টেস্ট কেস বানায় বা বাগ রিপোর্ট ক্লাসিফাই করে।"),
               ("Never fine-tune on real company or employee data. Use anonymized or synthetic examples.",
                "আসল কোম্পানি বা কর্মীর ডেটা দিয়ে কখনো ফাইন-টিউন করবেন না। অ্যানোনিমাইজড বা সিন্থেটিক উদাহরণ ব্যবহার করুন।"),
               ("The full timeline takes roughly 4–6 months, part-time.",
                "পুরো টাইমলাইনে পার্ট-টাইমে আনুমানিক ৪–৬ মাস লাগে।"),
               ("The total is an estimate.",
                "মোট সময় একটা হিসাব।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
