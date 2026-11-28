"""Prompt Engineering · 05 Prompt templating & variable injection: a prompt is a template filled at call time, and untrusted input needs care.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Template  Body: "Real prompts are templates: text with blanks that get filled in when you call the model." Term "Template".
  2 Variables Body: "user input, retrieved context, today's date, the model's prior reply — spliced in at call time."
  3 Messages  "The production pattern is a function that returns the whole list of messages." Table row "Composition".
  4 f-string  "Never trust f-strings with user input. It is a real prompt injection path." Term "Prompt injection": "Sneaking fake instructions into a variable so the model follows them instead of your rules."
  5 Tags      "Wrap untrusted input in XML tags, and let the system message tell the model it is data, not instructions." "Tags reduce injection risk but do not prevent it."
  6 Size      "Use unique sentinels." Term "Sentinel". "Summarise or truncate big input first."
  7 Test      "Store templates as files, then version, lint (auto-check for mistakes), and test them." Term "Golden outputs": "Saved correct answers. A unit test compares the prompt's new output against them."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("vars", "note", ("Variables", "ভেরিয়েবল"), 120, 60),
    node("tpl", "file", ("Template", "টেমপ্লেট"), 120, 162),
    node("evil", "user", ("Fake instructions", "নকল নির্দেশ"), 285, 60),
    node("msgs", "tool", ("List of messages", "মেসেজ তালিকা"), 285, 162),
    node("sys", "note", ("System message", "সিস্টেম মেসেজ"), 285, 268),
    node("tags", "shield", ("XML tags", "XML ট্যাগ"), 490, 162),
    node("model", "model", ("Model", "মডেল"), 665, 162),
    node("gold", "file", ("Golden outputs", "গোল্ডেন আউটপুট"), 500, 268),
]

METRICS = [
    ("Input", "ইনপুট"),
    ("Risk", "ঝুঁকি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Template", "টেমপ্লেট"),
       ("A prompt is a template", "প্রম্পট মানে টেমপ্লেট"),
       [("Real prompts are templates: text with blanks that get filled in when you call the model.",
         "বাস্তব প্রম্পট হলো টেমপ্লেট: ফাঁকা ঘরওয়ালা লেখা, যা মডেলকে কল করার সময় ভরা হয়।"),
        ("Treat them like code: well structured, checked, and tested.",
         "একে কোডের মতো দেখুন: গোছানো, যাচাই করা আর পরীক্ষা করা।")],
       [sh("tpl", "hot", ("blanks", "ফাঁকা ঘর")), sh("model", "dim")],
       [ln("tpl", "model", "to", state="dim")],
       [None, None]),

    st(("Variables", "ভেরিয়েবল"),
       ("Variables fill the blanks", "ভেরিয়েবল ফাঁকা ঘর ভরে"),
       [("The blanks are called variables, such as user input, retrieved context, today's date, or the model's prior reply.",
         "ফাঁকা ঘরগুলোর নাম ভেরিয়েবল, যেমন ইউজারের ইনপুট, আনা কনটেক্সট, আজকের তারিখ বা মডেলের আগের উত্তর।"),
        ("You fill them in at call time.",
         "কল করার সময় আপনি সেগুলো ভরেন।")],
       [sh("vars", "hot", ("user input, date", "ইউজারের ইনপুট, তারিখ")), sh("tpl", "hot"), sh("model", "dim")],
       [ln("vars", "tpl", "to", state="hot"), ln("tpl", "model", "to", state="dim")],
       [("filled at call time", "কল করার সময় ভরা"), None]),

    st(("Messages", "মেসেজ"),
       ("A function returns the messages", "একটা ফাংশন মেসেজ ফেরত দেয়"),
       [("The production pattern is a function that returns the whole list of messages.",
         "প্রোডাকশনের প্যাটার্ন হলো এমন ফাংশন, যা পুরো মেসেজ তালিকা ফেরত দেয়।"),
        ("It is the most flexible: it handles tool definitions, history, retrieval, and dynamic few-shot.",
         "এটা সবচেয়ে নমনীয়: টুল ডেফিনিশন, হিস্ট্রি, রিট্রিভাল আর ডাইনামিক ফিউ-শট সামলায়।")],
       [sh("tpl", "hot"), sh("msgs", "hot"), sh("sys", "hot"), sh("model", "hot")],
       [ln("tpl", "msgs", "to", state="hot"), ln("sys", "msgs", "to", state="hot"), ln("msgs", "model", "to", state="hot")],
       [None, None]),

    st(("f-string", "f-string"),
       ("An f-string with user input is a risk", "ইউজারের ইনপুটসহ f-string ঝুঁকির"),
       [("Never trust f-strings with user input. It is a real prompt injection path.",
         "ইউজারের ইনপুটে f-string-কে বিশ্বাস করবেন না। এটা প্রম্পট ইনজেকশনের বাস্তব পথ।"),
        ("Prompt injection means sneaking fake instructions into a variable so the model follows them instead of your rules.",
         "প্রম্পট ইনজেকশন মানে ভেরিয়েবলের ভেতরে নকল নির্দেশ ঢুকিয়ে দেওয়া, যাতে মডেল আপনার নিয়মের বদলে সেটা মানে।")],
       [sh("evil", "warn"), sh("msgs", "warn"), sh("model", "warn", ("follows them", "সেটা মানে"))],
       [ln("evil", "msgs", "to", state="warn"), ln("msgs", "model", "to", state="warn")],
       [("untrusted", "আনট্রাস্টেড"), ("injection path", "ইনজেকশনের পথ")],
       note=("warn", "Wrap untrusted data in tags. Do not rely on a plain f-string.",
             "আনট্রাস্টেড ডেটা ট্যাগে মুড়ুন। সাধারণ f-string-এর ওপর ভরসা করবেন না।")),

    st(("Tags", "ট্যাগ"),
       ("Wrap untrusted input in tags", "আনট্রাস্টেড ইনপুট ট্যাগে মুড়ুন"),
       [("Wrap untrusted input in XML tags, and let the system message tell the model it is data, not instructions.",
         "আনট্রাস্টেড ইনপুট XML ট্যাগে মুড়ুন, আর সিস্টেম মেসেজে মডেলকে বলে দিন যে এটা ডেটা, নির্দেশ নয়।"),
        ("Tags reduce injection risk but do not prevent it.",
         "ট্যাগ ইনজেকশনের ঝুঁকি কমায়, কিন্তু আটকায় না।")],
       [sh("evil", "dim"), sh("msgs", "hot"), sh("tags", "hot", ("data only", "শুধু ডেটা")), sh("sys", "hot"), sh("model", "hot")],
       [ln("evil", "msgs", "to", state="dim"), ln("msgs", "tags", "to", state="hot"), ln("tags", "model", "to", state="hot"), ln("sys", "msgs", "to", state="hot")],
       [("wrapped in tags", "ট্যাগে মোড়া"), ("reduced, not prevented", "কমে, আটকায় না")]),

    st(("Sentinel", "সেন্টিনেল"),
       ("Sentinels and smaller input", "সেন্টিনেল আর ছোট ইনপুট"),
       [("A sentinel is a marker that will not collide with your data, such as triple quotes, a custom token, or a random ID.",
         "সেন্টিনেল এমন চিহ্ন যা ডেটার সাথে মিলে যাবে না, যেমন ট্রিপল কোট, কাস্টম টোকেন বা র‍্যান্ডম ID।"),
        ("Summarise or truncate big input first.",
         "বড় ইনপুট আগে সামারাইজ বা ট্রাঙ্কেট করুন।")],
       [sh("vars", "hot", ("summarise first", "আগে সামারাইজ")), sh("tpl", "hot"), sh("tags", "hot", ("unique sentinel", "ইউনিক সেন্টিনেল"))],
       [ln("vars", "tpl", "to", state="hot")],
       [("summarised or truncated", "সামারাইজ বা ট্রাঙ্কেট করা"), None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember: store, version, test", "মনে রাখুন: ফাইলে রাখুন, ভার্সন করুন, টেস্ট করুন"),
       [("Store templates as files, then version, lint, and test them.",
         "টেমপ্লেট ফাইলে রেখে ভার্সন, লিন্ট ও টেস্ট করুন।"),
        ("Golden outputs are saved correct answers. A unit test compares the prompt's new output against them.",
         "গোল্ডেন আউটপুট আগে থেকে রাখা সঠিক উত্তর। ইউনিট টেস্ট প্রম্পটের নতুন আউটপুট এর সাথে মিলিয়ে দেখে।")],
       [sh("tpl", "hot", ("a file", "একটা ফাইল")), sh("model", "hot"), sh("gold", "hot", ("saved correct answers", "রাখা সঠিক উত্তর"))],
       [ln("tpl", "model", "to", state="hot"), ln("model", "gold", "to", state="hot")],
       [None, None],
       points=[("Never trust f-strings with user input.", "ইউজারের ইনপুটে f-string-কে বিশ্বাস করবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
