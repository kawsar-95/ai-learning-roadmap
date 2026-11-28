"""Prompt Engineering · 06 Prompt versioning — prompts as code: treat a prompt change like a code release.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Source     Body: "Keep prompts as files in source control. Every change is a pull request you can review."
  2 Pin        "Pin the model, the temperature, and the prompt. Without all three, you cannot reproduce a good output." Term "Pin the model version": "instead of a moving label like latest."
  3 Golden     Term "Golden test cases": "Pairs of an input and the output you expect. You run them on every prompt change." Remember: "Run golden test cases on every prompt change to catch regressions before users do."
  4 Regression Term "Regression": "When a change breaks something that used to work." Practice: "A rule that fixes one ticket can break another one."
  5 Rollout    Terms "Canary rollout" and "A/B in production": a small group or part of traffic first, measure business metrics, then promote.
  6 Log        "Log (prompt, output, user_feedback) for every call, then mine the failures."
  7 Remember   "A prompt that ships is like deployed code. ... every change is reviewed, tested, and rolled out with care, not edited live in production."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("file", "file", ("Prompt file", "প্রম্পট ফাইল"), 110, 80),
    node("pr", "service", ("Pull request", "পুল রিকোয়েস্ট"), 330, 80),
    node("tests", "chart", ("Golden tests", "গোল্ডেন টেস্ট"), 560, 80),
    node("canary", "balancer", ("Canary rollout", "ক্যানারি রোলআউট"), 560, 250),
    node("promo", "user", ("Promote", "চালু করা"), 330, 250),
    node("logs", "database", ("Logs", "লগ"), 110, 250),
]

METRICS = [
    ("Pinned", "পিন করা"),
    ("Tests", "টেস্ট"),
    ("Traffic", "ট্রাফিক"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Source", "সোর্স"),
       ("Prompts live in source control", "প্রম্পট থাকে সোর্স কন্ট্রোলে"),
       [("Keep prompts as files in source control.",
         "প্রম্পট সোর্স কন্ট্রোলে ফাইল হিসেবে রাখুন।"),
        ("Every change is a pull request you can review.",
         "প্রতিটি পরিবর্তন হবে পর্যালোচনাযোগ্য পুল রিকোয়েস্ট।")],
       [sh("file", "hot"), sh("pr", "hot", ("review", "রিভিউ"))],
       [ln("file", "pr", "to", state="hot")],
       [None, None, None]),

    st(("Pin", "পিন"),
       ("Pin the model, temperature, prompt", "মডেল, টেম্পারেচার, প্রম্পট পিন করুন"),
       [("Pin the model, the temperature, and the prompt. Without all three, you cannot reproduce a good output.",
         "মডেল, টেম্পারেচার আর প্রম্পট, তিনটাই পিন করুন। নইলে ভালো আউটপুট আবার বানানো যায় না।"),
        ("Pinning the model version means fixing an exact version instead of a moving label like latest.",
         "মডেল ভার্সন পিন মানে latest-এর মতো বদলে যাওয়া নামের বদলে নির্দিষ্ট মডেল ভার্সন বেঁধে রাখা।")],
       [sh("file", "hot", ("all three", "তিনটাই")), sh("pr", "dim")],
       [ln("file", "pr", "to", state="dim")],
       [("model, temperature, prompt", "মডেল, টেম্পারেচার, প্রম্পট"), None, None]),

    st(("Golden", "গোল্ডেন"),
       ("Run golden test cases", "গোল্ডেন টেস্ট কেস চালান"),
       [("Golden test cases are pairs of an input and the output you expect.",
         "গোল্ডেন টেস্ট কেস হলো ইনপুট আর প্রত্যাশিত আউটপুটের জোড়া।"),
        ("You run them on every prompt change.",
         "প্রতিটি প্রম্পট পরিবর্তনে এগুলো চালানো হয়।")],
       [sh("file", "hot"), sh("pr", "hot"), sh("tests", "hot", ("input, output", "ইনপুট, আউটপুট"))],
       [ln("file", "pr", "to", state="hot"), ln("pr", "tests", "to", state="hot")],
       [None, ("every prompt change", "প্রতিটি প্রম্পট পরিবর্তন"), None]),

    st(("Regression", "রিগ্রেশন"),
       ("A regression is caught early", "রিগ্রেশন আগেই ধরা পড়ে"),
       [("A regression is when a change breaks something that used to work. A rule that fixes one ticket can break another one.",
         "রিগ্রেশন হলো কোনো পরিবর্তনের ফলে আগে ঠিকঠাক চলা জিনিস ভেঙে যাওয়া। একটা নিয়ম এক টিকেট ঠিক করে আরেকটা ভেঙে দিতে পারে।"),
        ("Golden tests catch it before users do.",
         "গোল্ডেন টেস্ট ইউজারের আগেই সেটা ধরে।")],
       [sh("pr", "warn", ("change", "পরিবর্তন")), sh("tests", "warn", ("regression", "রিগ্রেশন"))],
       [ln("pr", "tests", "to", state="warn"), ln("tests", "pr", "to", state="warn")],
       [None, ("regression caught", "রিগ্রেশন ধরা পড়েছে"), None]),

    st(("Rollout", "রোলআউট"),
       ("Canary, A/B, then promote", "ক্যানারি, A/B, তারপর চালু"),
       [("A canary rollout sends a new version to a small group of users first, to catch problems before everyone gets it.",
         "ক্যানারি রোলআউটে নতুন ভার্সন আগে অল্প কিছু ইউজারকে দেওয়া হয়, যাতে সবার কাছে যাওয়ার আগেই সমস্যা ধরা পড়ে।"),
        ("With A/B in production, you send a small part of traffic to the new prompt, measure business metrics, then promote it.",
         "প্রোডাকশনে A/B-তে ট্রাফিকের ছোট অংশ নতুন প্রম্পটে পাঠানো হয়, বিজনেস মেট্রিক মাপা হয়, তারপর সেটা চালু করা হয়।")],
       [sh("tests", "hot"), sh("canary", "hot", ("small group", "অল্প কিছু ইউজার")), sh("promo", "hot", ("then promote", "তারপর চালু"))],
       [ln("tests", "canary", "to", state="hot"), ln("canary", "promo", "to", state="hot")],
       [None, None, ("a small part", "ছোট অংশ")]),

    st(("Log", "লগ"),
       ("Log every call, mine the failures", "প্রতিটি কল লগ করুন, ব্যর্থতা খুঁড়ুন"),
       [("Log (prompt, output, user_feedback) for every call.",
         "প্রতিটি কলের (prompt, output, user_feedback) লগ করুন।"),
        ("Then mine the failures.",
         "তারপর ব্যর্থতাগুলো খুঁড়ে দেখুন।")],
       [sh("promo", "hot"), sh("logs", "hot", ("mine failures", "ব্যর্থতা খোঁড়া")), sh("file", "hot", ("next edit", "পরের পরিবর্তন"))],
       [ln("promo", "logs", "to", state="hot"), ln("logs", "file", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember: a prompt is deployed code", "মনে রাখুন: প্রম্পট ডিপ্লয় করা কোড"),
       [("A prompt that ships is like deployed code.",
         "যে প্রম্পট ইউজারের কাছে পৌঁছে গেছে, সেটা ডিপ্লয় করা কোডের মতো।"),
        ("Every change is reviewed, tested, and rolled out with care, not edited live in production.",
         "প্রতিটি পরিবর্তন যত্ন করে রিভিউ, টেস্ট আর রোলআউট করা হয়, সরাসরি প্রোডাকশনে বদলানো হয় না।")],
       [sh("file", "hot"), sh("pr", "hot"), sh("tests", "hot"), sh("canary", "hot"), sh("promo", "hot"), sh("logs", "hot")],
       [ln("file", "pr", "to", state="hot"), ln("pr", "tests", "to", state="hot"), ln("tests", "canary", "to", state="hot"), ln("canary", "promo", "to", state="hot"), ln("promo", "logs", "to", state="hot"), ln("logs", "file", "to", state="hot")],
       [None, None, None],
       points=[("Run golden test cases on every prompt change to catch regressions before users do.",
                "প্রতিটি প্রম্পট পরিবর্তনে গোল্ডেন টেস্ট কেস চালান, যাতে রিগ্রেশন ইউজারের আগে ধরা পড়ে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
