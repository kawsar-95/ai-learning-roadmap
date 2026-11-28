"""Fine-tuning roadmap · 04 Phase 4, evaluation: a test set the model never saw, scoring that fits the answer, and a regression suite that grows.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Test set    Body: "Build a held-out test set the model never saw during training, then compare the base model against your fine-tuned one on the same inputs." Start here: "Test examples kept apart from everything used in training, so the model has never seen them."
  2 Compare     Body: "Without this step, you cannot tell whether fine-tuning actually helped." Layman's: "check which answers are actually better, not just different."
  3 Clear       List: "Exact-match or rubric scoring for tasks with a clear right answer". Start here: exact-match and rubric scoring.
  4 Open-ended  List: "LLM-as-judge scoring for open-ended outputs, with spot-checks by a human". Start here: "Using a language model to score another model's answers when there is no single right answer."
  5 Regression  List: "A running regression suite built from every failure case you find". Start here: "rerun to check that old mistakes do not come back."
  6 Fluent      Callout: "refusing to trust a model's output just because it reads fluently." Layman's: "test it on cases it hasn't seen".
  7 Remember    The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("test", "file", ("Held-out test set", "হেল্ড-আউট টেস্ট সেট"), 135, 162),
    node("base", "model", ("Base model", "বেস মডেল"), 380, 75),
    node("tuned", "model", ("Fine-tuned model", "ফাইন-টিউন করা মডেল"), 380, 250),
    node("verdict", "note", ("Did it help?", "কাজে লেগেছে কি?"), 610, 162),
    node("exact", "tool", ("Exact-match scoring", "এক্সাক্ট-ম্যাচ স্কোরিং"), 380, 75),
    node("rubric", "tool", ("Rubric scoring", "রুব্রিক স্কোরিং"), 380, 250),
    node("judge", "model", ("LLM-as-judge", "LLM-as-judge"), 380, 162),
    node("human", "user", ("Human spot-check", "মানুষের স্পট-চেক"), 650, 162),
    node("fail", "note", ("Every failure", "প্রতিটা ব্যর্থতা"), 110, 162),
    node("regress", "chart", ("Regression suite", "রিগ্রেশন স্যুট"), 380, 162),
]

METRICS = [
    ("Test set", "টেস্ট সেট"),
    ("Scoring", "স্কোরিং"),
    ("Regression suite", "রিগ্রেশন স্যুট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Test set", "টেস্ট সেট"),
       ("A held-out test set", "হেল্ড-আউট টেস্ট সেট"),
       [("Build a held-out test set the model never saw during training. It is kept apart from everything used in training.",
         "ট্রেইনিংয়ে মডেল কখনো দেখেনি এমন একটা হেল্ড-আউট টেস্ট সেট বানান। ট্রেইনিংয়ে ব্যবহার হওয়া সবকিছু থেকে এটা আলাদা রাখা হয়।"),
        ("Then run the base model and your fine-tuned one on the same inputs.",
         "তারপর একই ইনপুটে বেস মডেল আর আপনার ফাইন-টিউন করা মডেল চালান।")],
       [sh("test", "hot", ("never seen", "কখনো দেখেনি")), sh("base", "hot", ("same inputs", "একই ইনপুট")), sh("tuned", "hot", ("same inputs", "একই ইনপুট"))],
       [ln("test", "base", "to", state="hot"), ln("test", "tuned", "to", state="hot")],
       [("never seen", "কখনো দেখেনি"), None, None]),

    st(("Compare", "তুলনা"),
       ("Compare base and fine-tuned", "বেস আর ফাইন-টিউনের তুলনা"),
       [("Compare the base model against the fine-tuned one on the same inputs.",
         "একই ইনপুটে বেস মডেলের সাথে ফাইন-টিউন করা মডেলের তুলনা করুন।"),
        ("Check which answers are actually better, not just different. Without this step, you cannot tell whether fine-tuning helped.",
         "কোন উত্তরগুলো সত্যিই ভালো তা দেখুন, শুধু আলাদা নয়। এই ধাপ ছাড়া বোঝার উপায় নেই ফাইন-টিউনিং কাজে লেগেছে কিনা।")],
       [sh("test", "hot"), sh("base", "hot"), sh("tuned", "hot"), sh("verdict", "hot", ("actually better", "সত্যিই ভালো"))],
       [ln("test", "base", "to", state="hot"), ln("test", "tuned", "to", state="hot"), ln("base", "verdict", "to", state="hot"),
        ln("tuned", "verdict", "to", state="hot")],
       [None, None, None]),

    st(("Clear", "স্পষ্ট উত্তর"),
       ("Clear answers: exact-match or rubric", "স্পষ্ট উত্তর: exact-match বা রুব্রিক"),
       [("Use exact-match or rubric scoring for tasks with a clear right answer.",
         "স্পষ্ট সঠিক উত্তর থাকা টাস্কের জন্য exact-match বা রুব্রিক স্কোরিং ব্যবহার করুন।"),
        ("Exact-match counts an answer as right only if it matches exactly. Rubric scoring checks it against a checklist of what a good answer must have.",
         "এক্সাক্ট-ম্যাচে উত্তর সঠিক ধরা হয় শুধু হুবহু মিললে। রুব্রিক স্কোরিংয়ে ভালো উত্তরে কী কী থাকতে হবে তার চেকলিস্টের সাথে মেলানো হয়।")],
       [sh("tuned", "hot", x=110, y=162), sh("exact", "hot", ("matches exactly", "হুবহু মেলে")), sh("rubric", "hot", ("a checklist", "একটা চেকলিস্ট"))],
       [ln("tuned", "exact", "to", state="hot"), ln("tuned", "rubric", "to", state="hot")],
       [None, ("clear right answer", "স্পষ্ট সঠিক উত্তর"), None]),

    st(("Open-ended", "ওপেন-এন্ডেড"),
       ("Open-ended: LLM-as-judge", "ওপেন-এন্ডেড: LLM-as-judge"),
       [("Use LLM-as-judge scoring for open-ended outputs: a language model scores another model's answers when there is no single right answer.",
         "ওপেন-এন্ডেড আউটপুটের জন্য LLM-as-judge স্কোরিং ব্যবহার করুন: যখন একটাই সঠিক উত্তর থাকে না, তখন একটি ল্যাঙ্গুয়েজ মডেল অন্য মডেলের উত্তরে নম্বর দেয়।"),
        ("A human spot-checks the judge.",
         "মানুষ জাজের কাজ স্পট-চেক করে।")],
       [sh("tuned", "hot", x=110, y=162), sh("judge", "hot", ("no single right answer", "একটাই সঠিক উত্তর নেই")), sh("human", "hot", ("spot-checks", "স্পট-চেক"))],
       [ln("tuned", "judge", "to", state="hot"), ln("judge", "human", "to", state="hot")],
       [None, ("LLM-as-judge", "LLM-as-judge"), None]),

    st(("Regression", "রিগ্রেশন"),
       ("A running regression suite", "চলমান রিগ্রেশন স্যুট"),
       [("Add every failure you find to a running regression suite.",
         "খুঁজে পাওয়া প্রতিটা ব্যর্থতা একটা চলমান রিগ্রেশন স্যুটে যোগ করুন।"),
        ("It is rerun to check that old mistakes do not come back.",
         "পুরনো ভুল ফিরে আসছে কিনা দেখতে এটা বারবার চালানো হয়।")],
       [sh("fail", "warn"), sh("regress", "hot", ("rerun", "বারবার চালানো")), sh("verdict", "hot", ("no old mistakes", "পুরনো ভুল নয়"))],
       [ln("fail", "regress", "to", state="warn"), ln("regress", "verdict", "to", state="hot")],
       [None, None, ("growing", "ক্রমে বাড়ছে")]),

    st(("Fluent", "ফ্লুয়েন্ট"),
       ("Fluent is not correct", "ফ্লুয়েন্ট মানে সঠিক নয়"),
       [("Do not trust an output just because it reads fluently.",
         "আউটপুট ফ্লুয়েন্ট শোনায় বলেই তাকে বিশ্বাস করবেন না।"),
        ("A model can sound confident and still be wrong, so test it on cases it has not seen.",
         "মডেল আত্মবিশ্বাসী শোনালেও ভুল হতে পারে, তাই যে কেসগুলো সে দেখেনি সেগুলোতে টেস্ট করুন।")],
       [sh("tuned", "warn", ("reads fluently", "ফ্লুয়েন্ট শোনায়")), sh("test", "hot", ("cases it has not seen", "যে কেস দেখেনি")), sh("verdict", "hot")],
       [ln("tuned", "verdict", "to", state="warn"), ln("test", "verdict", "to", state="hot")],
       [None, None, None],
       note=("warn", "A model can sound confident and still be wrong.", "মডেল আত্মবিশ্বাসী শোনালেও ভুল হতে পারে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Without a held-out test set, you cannot tell whether fine-tuning helped.",
         "হেল্ড-আউট টেস্ট সেট ছাড়া বোঝার উপায় নেই ফাইন-টিউনিং কাজে লেগেছে কিনা।")],
       [sh("test"), sh("base"), sh("tuned"), sh("verdict")],
       [ln("test", "base", "to"), ln("test", "tuned", "to"), ln("base", "verdict", "to"), ln("tuned", "verdict", "to")],
       [None, None, None],
       points=[("Without a held-out test set, you cannot tell whether fine-tuning helped.",
                "হেল্ড-আউট টেস্ট সেট ছাড়া বোঝার উপায় নেই ফাইন-টিউনিং কাজে লেগেছে কিনা।"),
               ("Use exact-match or rubric scoring for clear answers, and LLM-as-judge with human spot-checks for open-ended ones.",
                "স্পষ্ট উত্তরের জন্য exact-match বা রুব্রিক স্কোরিং, আর ওপেন-এন্ডেড উত্তরের জন্য মানুষের স্পট-চেকসহ LLM-as-judge ব্যবহার করুন।"),
               ("Add every failure you find to a running regression suite.",
                "খুঁজে পাওয়া প্রতিটা ব্যর্থতা একটা চলমান রিগ্রেশন স্যুটে যোগ করুন।"),
               ("Do not trust an output just because it reads fluently.",
                "আউটপুট ফ্লুয়েন্ট শোনায় বলেই তাকে বিশ্বাস করবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
