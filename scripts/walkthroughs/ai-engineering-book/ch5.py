"""Part 5 · 07 Prompt Engineering: prompts, in-context learning and context length.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Prompt     Body, "What a prompt actually is": "It usually combines three things: a task description ... optional examples of the task done correctly; the actual task itself."
  2 Weights    Body: "Prompt engineering is the cheapest, fastest way to adapt a foundation model to your use case. It changes nothing about the model's weights ... It is worth exhausting good prompting before reaching for fine-tuning."
  3 Shots      Body, "In-context learning": "Models can learn a new behavior just from examples placed inside the prompt, without any weight update ... zero examples is zero-shot, five examples is 5-shot. More shots generally help, but they cost more tokens and are capped by the model's context length."
  4 Two parts  Body, "System prompt vs. user prompt": the system prompt holds the task description and persona, the user prompt holds the actual question or request, "concatenated with a model-specific chat template".
  5 Template   Body: "Getting that template wrong causes silent, hard-to-debug performance drops." Start here: "A wrong chat template causes silent performance drops that are hard to debug."
  6 Long       Body, "Context length and context efficiency": "from about 1K tokens in early GPT models to millions of tokens in newer ones. But a longer context window does not mean every position in it is used equally well."
  7 Ends       Body: "models recall information near the beginning or end of a prompt far more reliably than information buried in the middle ... putting critical instructions first or last — can help." Start here: needle-in-a-haystack.
  8 Remember   The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("task", "file", ("Task description", "কাজের বর্ণনা"), 140, 70),
    node("ex", "file", ("Examples", "উদাহরণ"), 140, 162),
    node("real", "file", ("Actual task", "আসল কাজ"), 140, 254),
    node("model", "model", ("Model", "মডেল"), 600, 162),
    node("ft", "tool", ("Fine-tuning", "ফাইন-টিউনিং"), 600, 262),
    node("sys", "note", ("System prompt", "সিস্টেম প্রম্পট"), 140, 90),
    node("usr", "user", ("User prompt", "ইউজার প্রম্পট"), 140, 234),
    node("tmpl", "tool", ("Chat template", "চ্যাট টেমপ্লেট"), 380, 162),
    node("begin", "file", ("Beginning", "শুরু"), 120, 162),
    node("mid", "file", ("Middle", "মাঝখান"), 380, 162),
    node("end", "file", ("End", "শেষ"), 640, 162),
]

METRICS = [
    ("Changes", "বদলায়"),
    ("Examples", "উদাহরণ"),
    ("Recall", "মনে থাকে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Prompt", "প্রম্পট"),
       ("What a prompt holds", "প্রম্পটে কী থাকে"),
       [("A prompt is the instruction you give a model to perform a task. It usually combines a task description, optional examples, and the actual task itself.",
         "প্রম্পট হলো আপনি মডেলকে কাজ করার জন্য যে নির্দেশ দেন। এতে সাধারণত থাকে কাজের বর্ণনা, চাইলে কিছু উদাহরণ (ঐচ্ছিক), আর আসল কাজ।"),
        ("The task description says what to do, what role to play, and what format to answer in.",
         "কাজের বর্ণনা বলে কী করতে হবে, কী ভূমিকা নিতে হবে, আর কোন ফরম্যাটে উত্তর দিতে হবে।")],
       [sh("task", "hot", ("what to do, role, format", "কী করতে হবে, ভূমিকা, ফরম্যাট")), sh("ex", "dim", ("optional", "ঐচ্ছিক")), sh("real", "hot"), sh("model", "hot")],
       [ln("task", "model", "to", state="hot"), ln("ex", "model", "to", state="dim"), ln("real", "model", "to", state="hot")],
       [None, None, None]),

    st(("Weights", "ওয়েট"),
       ("Only the prompt changes", "শুধু প্রম্পট বদলায়"),
       [("Prompt engineering is the cheapest, fastest way to adapt a foundation model to your use case.",
         "প্রম্পট ইঞ্জিনিয়ারিং ফাউন্ডেশন মডেলকে আপনার কাজের উপযোগী করার সবচেয়ে সস্তা আর দ্রুত উপায়।"),
        ("It changes nothing about the model's weights, it only changes what you feed into it. Try good prompting before fine-tuning.",
         "এতে মডেলের ওয়েটে কিছুই বদলায় না, শুধু মডেলকে যা দেওয়া হয় তা বদলায়। ফাইন-টিউনিংয়ের আগে ভালো প্রম্পটিং করে দেখুন।")],
       [sh("real", "hot", ("what you feed in", "যা দেওয়া হয়")), sh("model", "dim", ("weights unchanged", "ওয়েট বদলায় না")), sh("ft", "dim", ("after good prompting", "ভালো প্রম্পটিংয়ের পরে"))],
       [ln("real", "model", "to", state="hot")],
       [("Only the prompt", "শুধু প্রম্পট"), None, None]),

    st(("Shots", "শট"),
       ("Learn from examples in the prompt", "প্রম্পটের উদাহরণ থেকে শেখা"),
       [("Models can learn a new behavior just from examples placed inside the prompt, without any weight update. This is called in-context learning.",
         "প্রম্পটের ভেতরে রাখা উদাহরণ থেকেই মডেল নতুন আচরণ শিখতে পারে, কোনো ওয়েট আপডেট ছাড়াই। একে বলে ইন-কনটেক্সট লার্নিং।"),
        ("Each example is a shot: zero examples is zero-shot, five examples is 5-shot. More shots generally help, but they cost more tokens and are capped by the model's context length.",
         "প্রতিটি উদাহরণ একটি শট: কোনো উদাহরণ না থাকলে zero-shot, ৫টি উদাহরণ হলে ৫-shot। বেশি শট সাধারণত কাজে লাগে, কিন্তু বেশি টোকেন লাগে আর মডেলের context length-এ সীমা আছে।")],
       [sh("task", "hot"), sh("ex", "hot", ("zero-shot or 5-shot", "zero-shot বা ৫-shot")), sh("real", "hot"), sh("model", "hot")],
       [ln("task", "model", "to", state="hot"), ln("ex", "model", "to", state="hot"), ln("real", "model", "to", state="hot")],
       [None, ("zero-shot, 5-shot", "zero-shot, ৫-shot"), None],
       note=("tip", "Few-shot examples still help a lot for niche or domain-specific tasks the model has rarely seen.",
             "যে নিশ বা ডোমেইন-নির্দিষ্ট কাজ মডেল কমই দেখেছে, সেখানে few-shot উদাহরণ এখনও অনেক কাজে লাগে।")),

    st(("Two parts", "দুই অংশ"),
       ("System prompt and user prompt", "সিস্টেম প্রম্পট আর ইউজার প্রম্পট"),
       [("Most model APIs let you split a prompt into two parts. The system prompt holds the task description and persona, usually set by the application developer.",
         "অনেক মডেল API প্রম্পটকে দুই ভাগে ভাগ করতে দেয়। সিস্টেম প্রম্পটে থাকে কাজের বর্ণনা আর persona, সাধারণত অ্যাপ্লিকেশন ডেভেলপার ঠিক করে দেন।"),
        ("The user prompt holds the actual question or request, usually from the end user. A model-specific chat template joins the two into one text.",
         "ইউজার প্রম্পটে থাকে আসল প্রশ্ন বা অনুরোধ, সাধারণত শেষ ব্যবহারকারীর। মডেলের নিজস্ব চ্যাট টেমপ্লেট দুটোকে জুড়ে একটি লেখা বানায়।")],
       [sh("sys", "hot", ("developer", "ডেভেলপার")), sh("usr", "hot", ("end user", "শেষ ব্যবহারকারী")), sh("tmpl", "hot"), sh("model", "hot")],
       [ln("sys", "tmpl", "to", state="hot"), ln("usr", "tmpl", "to", state="hot"), ln("tmpl", "model", "to", state="hot")],
       [None, None, None]),

    st(("Template", "টেমপ্লেট"),
       ("A wrong template fails silently", "ভুল টেমপ্লেট চুপচাপ ব্যর্থ হয়"),
       [("Getting the chat template wrong causes silent, hard-to-debug performance drops.",
         "চ্যাট টেমপ্লেট ভুল হলে পারফরম্যান্স চুপচাপ খারাপ হয়, আর ধরা কঠিন।"),
        ("System prompts often perform better, but not because the model treats them as special by nature. They come first in the final text, and many models are explicitly post-trained to weigh them more heavily.",
         "সিস্টেম প্রম্পট প্রায়ই ভালো কাজ করে, কিন্তু মডেল সেটাকে স্বভাবগতভাবে বিশেষ ভাবে বলে নয়। চূড়ান্ত লেখায় সেটা আগে আসে, আর অনেক মডেলকে স্পষ্টভাবে পোস্ট-ট্রেইন করা হয় যাতে সেটাকে বেশি গুরুত্ব দেয়।")],
       [sh("sys", "dim"), sh("usr", "dim"), sh("tmpl", "warn", ("wrong template", "ভুল টেমপ্লেট")), sh("model", "warn", ("silent drop", "চুপচাপ পতন"))],
       [ln("sys", "tmpl", "to", state="dim"), ln("usr", "tmpl", "to", state="dim"), ln("tmpl", "model", "to", state="warn")],
       [None, None, None],
       note=("warn", "A wrong chat template causes silent performance drops that are hard to debug.",
             "চ্যাট টেমপ্লেট ভুল হলে পারফরম্যান্স চুপচাপ খারাপ হয়, আর ধরা কঠিন।")),

    st(("Long", "লম্বা"),
       ("A long context is not used equally", "লম্বা কনটেক্সট সমানভাবে কাজে লাগে না"),
       [("Context length limits have exploded, from about 1K tokens in early GPT models to millions of tokens in newer ones.",
         "কনটেক্সট লেংথের সীমা বিস্ফোরকভাবে বেড়েছে, আগের GPT মডেলে প্রায় ১K টোকেন থেকে নতুন মডেলে লক্ষ লক্ষ টোকেন।"),
        ("But a longer context window does not mean every position in it is used equally well.",
         "কিন্তু লম্বা কনটেক্সট উইন্ডো মানে এই নয় যে তার প্রতিটি জায়গা সমান ভালোভাবে কাজে লাগে।")],
       [sh("begin", "hot"), sh("mid", "hot"), sh("end", "hot")],
       [],
       [None, None, None]),

    st(("Ends", "শুরু-শেষ"),
       ("Start and end are recalled best", "শুরু আর শেষ সবচেয়ে ভালো মনে থাকে"),
       [("Needle-in-a-haystack tests hide one fact in a long prompt and check whether the model can find it. They show that models recall information near the beginning or end of a prompt far more reliably than information buried in the middle.",
         "নিডল-ইন-আ-হেস্ট্যাক টেস্টে লম্বা প্রম্পটে একটি তথ্য লুকিয়ে দেখা হয় মডেল সেটা খুঁজে পায় কিনা। এতে দেখা যায়, প্রম্পটের শুরু বা শেষের তথ্য মডেল মাঝখানে চাপা পড়া তথ্যের চেয়ে অনেক বেশি নির্ভরযোগ্যভাবে মনে রাখে।"),
        ("If accuracy drops as prompts get longer, shortening or re-ordering the prompt can help.",
         "প্রম্পট লম্বা হলে নির্ভুলতা কমলে প্রম্পট ছোট করা বা ক্রম বদলানো কাজে লাগতে পারে।")],
       [sh("begin", "hot", ("recalled well", "ভালো মনে থাকে")), sh("mid", "warn", ("easily missed", "সহজে বাদ পড়ে")), sh("end", "hot", ("recalled well", "ভালো মনে থাকে"))],
       [],
       [None, None, ("start and end, not middle", "শুরু আর শেষ, মাঝখান নয়")],
       note=("tip", "Put critical instructions first or last.",
             "জরুরি নির্দেশ প্রথমে বা শেষে রাখুন।")),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("A prompt usually has a task description, optional examples, and the actual task. Try good prompting before fine-tuning, because it changes nothing inside the model itself.",
         "প্রম্পটে সাধারণত থাকে কাজের বর্ণনা, চাইলে কিছু উদাহরণ (ঐচ্ছিক), আর আসল কাজ। ফাইন-টিউনিংয়ের আগে ভালো প্রম্পটিং করে দেখুন, কারণ এতে মডেলের ভেতরে কিছুই বদলায় না।"),
        ("A wrong chat template causes silent performance drops that are hard to debug. Models recall the start and end of a prompt better than the middle.",
         "চ্যাট টেমপ্লেট ভুল হলে পারফরম্যান্স চুপচাপ খারাপ হয়, আর ধরা কঠিন। মডেল প্রম্পটের শুরু আর শেষের তথ্য মাঝের চেয়ে ভালো মনে রাখে।")],
       [sh("task", "hot"), sh("ex", "dim", ("optional", "ঐচ্ছিক")), sh("real", "hot"), sh("model", "hot")],
       [ln("task", "model", "to", state="hot"), ln("ex", "model", "to", state="dim"), ln("real", "model", "to", state="hot")],
       [None, None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
