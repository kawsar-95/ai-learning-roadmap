"""Part · 01 Introduction to Building AI Applications with Foundation Models: how foundation models made AI engineering a discipline anyone can enter.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Language  Body: "A language model is just a system that predicts which token is likely to come next in a piece of text ... The breakthrough came from self-supervision, where the text itself supplies the training labels. Every word in a sentence can serve as the 'answer' that the model predicts from the words before it."
  2 Foundation Body: "As models learned to handle images, audio, and video in addition to text ... The field now calls them foundation models: large, general-purpose models that can be adapted to many different downstream applications."
  3 Service   Body: "a handful of large labs train them and offer them as a service through APIs (model as a service). Everyone else can now build applications on top of these models without training anything ... AI engineering: the process of building applications on top of readily available foundation models."
  4 Stack     Body: "three layers: application development ...; model development ...; infrastructure ... Most AI engineers today spend most of their time in the application development layer."
  5 Success   Body, "Setting expectations": "define success with concrete business metrics ... Set a usefulness threshold the product must clear before going live."
  6 Last mile Body, "Milestone planning": "going from an 80% working demo to a 95%+ reliable product takes far longer than the initial demo."
  7 Change    Body, "Maintenance": "foundation models and their pricing change quickly ... build so that you can swap models or providers."
  8 Remember  Start here: the four points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("text", "file", ("Text", "লেখা"), 130, 162),
    node("lm", "model", ("Language model", "ল্যাঙ্গুয়েজ মডেল"), 400, 162),
    node("fm", "model", ("Foundation model", "ফাউন্ডেশন মডেল"), 400, 162),
    node("lab", "server", ("A handful of large labs", "কিছু বড় ল্যাব"), 130, 162),
    node("api", "service", ("API", "API"), 400, 162),
    node("app", "browser", ("Your application", "আপনার অ্যাপ্লিকেশন"), 640, 162),
    node("l1", "service", ("Application development", "অ্যাপ্লিকেশন ডেভেলপমেন্ট"), 260, 60),
    node("l2", "model", ("Model development", "মডেল ডেভেলপমেন্ট"), 260, 162),
    node("l3", "server", ("Infrastructure", "ইনফ্রাস্ট্রাকচার"), 260, 262),
    node("thresh", "shield", ("Usefulness threshold", "উপযোগিতার সীমা"), 400, 162),
    node("alt", "model", ("Another model or provider", "অন্য মডেল বা প্রোভাইডার"), 400, 262),
    node("prod", "chart", ("Reliable product", "নির্ভরযোগ্য প্রোডাক্ট"), 640, 162),
]

METRICS = [
    ("Model", "মডেল"),
    ("Reliability", "নির্ভরযোগ্যতা"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Language", "ল্যাঙ্গুয়েজ"),
       ("From text to a language model", "লেখা থেকে ল্যাঙ্গুয়েজ মডেল"),
       [("A language model is a system that predicts which token is likely to come next in a piece of text.",
         "ল্যাঙ্গুয়েজ মডেল এমন একটি সিস্টেম, যে অনুমান করে লেখার পরের টোকেন কী হতে পারে।"),
        ("Self-supervision was the breakthrough: the text itself supplies the labels, so every word is the answer predicted from the words before it.",
         "সেলফ-সুপারভিশন ছিল সাফল্যের চাবি: লেখাটাই লেবেল জোগায়, তাই আগের শব্দগুলো দেখে প্রতিটি শব্দই অনুমান করার উত্তর।")],
       [sh("text", "hot", ("each word is the answer", "প্রতিটি শব্দই উত্তর")), sh("lm", "hot", ("predicts the next token", "পরের টোকেন অনুমান করে"))],
       [ln("text", "lm", "to", state="hot")],
       [None, None],
       note=("tip", "This removed the labeling bottleneck and let models scale up into large language models (LLMs).",
             "এতে লেবেল করার বাধা সরে যায়, আর মডেল বড় ল্যাঙ্গুয়েজ মডেলে (LLM) বড় হতে পারে।")),

    st(("Foundation", "ফাউন্ডেশন"),
       ("Foundation models", "ফাউন্ডেশন মডেল"),
       [("Models learned to handle images, audio, and video in addition to text, so they outgrew the name language model.",
         "মডেল লেখার পাশাপাশি ছবি, অডিও আর ভিডিও সামলাতে শিখল, তাই ল্যাঙ্গুয়েজ মডেল নামটা তাদের জন্য ছোট হয়ে গেল।"),
        ("The field now calls them foundation models: large, general-purpose models that can be adapted to many different applications.",
         "এখন তাদের বলা হয় ফাউন্ডেশন মডেল: বড় আর সাধারণ কাজের মডেল, যাকে অনেক ধরনের অ্যাপ্লিকেশনের জন্য মানিয়ে নেওয়া যায়।")],
       [sh("lm", "dim", x=130), sh("fm", "hot", ("general-purpose", "সাধারণ কাজের")), sh("app", "hot", ("many applications", "অনেক অ্যাপ্লিকেশন"))],
       [ln("lm", "fm", "to", state="dim"), ln("fm", "app", "to", state="hot")],
       [None, None]),

    st(("Service", "সার্ভিস"),
       ("Model as a service", "মডেল অ্যাজ আ সার্ভিস"),
       [("Foundation models are expensive to train, so a handful of large labs train them and offer them through APIs.",
         "ফাউন্ডেশন মডেল ট্রেইন করা ব্যয়বহুল, তাই কিছু বড় ল্যাব ট্রেইন করে API দিয়ে দেয়।"),
        ("Everyone else can build applications on top without training anything. This practice is AI engineering.",
         "বাকি সবাই কিছু ট্রেইন না করেই তার ওপর অ্যাপ্লিকেশন বানাতে পারে। এই কাজই AI ইঞ্জিনিয়ারিং।")],
       [sh("lab", "hot", ("train the models", "মডেল ট্রেইন করে")), sh("api", "hot", ("model as a service", "মডেল অ্যাজ আ সার্ভিস")), sh("app", "hot", ("no training needed", "ট্রেইন করতে হয় না"))],
       [ln("lab", "api", "to", state="hot"), ln("api", "app", "to", state="hot")],
       [("through an API", "API দিয়ে"), None]),

    st(("Stack", "স্ট্যাক"),
       ("The three layers of the stack", "স্ট্যাকের তিন লেয়ার"),
       [("The stack has three layers: application development, model development, and infrastructure.",
         "স্ট্যাকে তিন লেয়ার: অ্যাপ্লিকেশন ডেভেলপমেন্ট, মডেল ডেভেলপমেন্ট আর ইনফ্রাস্ট্রাকচার।"),
        ("Most AI engineers spend most of their time in application development, because the model is already available as a service.",
         "বেশিরভাগ AI ইঞ্জিনিয়ার বেশিরভাগ সময় অ্যাপ্লিকেশন ডেভেলপমেন্টে কাজ করেন, কারণ মডেল আগে থেকেই সার্ভিস হিসেবে পাওয়া যায়।")],
       [sh("l1", "hot", ("most engineers work here", "বেশিরভাগ ইঞ্জিনিয়ার এখানে")), sh("l2", "dim"), sh("l3", "dim")],
       [ln("l1", "l2", "to", state="dim"), ln("l2", "l3", "to", state="dim")],
       [None, None],
       changes=[("+", "Application development: prompting, context construction, evaluation, and the user-facing interface",
                 "অ্যাপ্লিকেশন ডেভেলপমেন্ট: প্রম্পট, কনটেক্সট, ইভ্যালুয়েশন আর ইন্টারফেস"),
                ("+", "Model development: training, finetuning, dataset engineering, and inference optimization",
                 "মডেল ডেভেলপমেন্ট: ট্রেইনিং, ফাইন-টিউনিং আর ডেটাসেট ইঞ্জিনিয়ারিং"),
                ("+", "Infrastructure: compute, data management, serving, and monitoring",
                 "ইনফ্রাস্ট্রাকচার: কম্পিউট, ডেটা, সার্ভিং আর মনিটরিং")]),

    st(("Success", "সফলতা"),
       ("Define success first", "আগে সফলতা ঠিক করুন"),
       [("Before building, define success with concrete business metrics, such as the percentage of tickets automated or response time saved.",
         "বানানোর আগে স্পষ্ট বিজনেস মেট্রিক দিয়ে সফলতা ঠিক করুন, যেমন কত শতাংশ টিকিট অটোমেট হলো বা কত সময় বাঁচল।"),
        ("Set a usefulness threshold the product must clear before going live.",
         "লাইভে যাওয়ার আগে একটা উপযোগিতার সীমা রাখুন, যা প্রোডাক্টকে পার হতে হবে।")],
       [sh("thresh", "hot", ("concrete business metrics", "স্পষ্ট বিজনেস মেট্রিক"), x=260), sh("app", "hot", ("going live", "লাইভে যাওয়া"))],
       [ln("thresh", "app", "to", state="hot")],
       [None, None]),

    st(("Last mile", "লাস্ট মাইল"),
       ("The last mile problem", "লাস্ট মাইল প্রবলেম"),
       [("An 80% working demo is the easy part.",
         "প্রায় ৮০% কাজ করা ডেমো বানানো সহজ অংশ।"),
        ("Going from that demo to a 95%+ reliable product takes far longer than the initial demo.",
         "সেই ডেমো থেকে ৯৫%+ নির্ভরযোগ্য প্রোডাক্টে যেতে ডেমোর চেয়ে অনেক বেশি সময় লাগে।")],
       [sh("app", "hot", ("about 80% working demo", "প্রায় ৮০% কাজ করা ডেমো"), x=150), sh("prod", "warn", ("95%+ reliable", "৯৫%+ নির্ভরযোগ্য"), x=600)],
       [ln("app", "prod", "to", state="warn", label=("far longer", "অনেক বেশি সময়"))],
       [None, "80% → 95%+"]),

    st(("Change", "বদল"),
       ("Plan for change", "বদলের জন্য তৈরি থাকুন"),
       [("Foundation models and their pricing change quickly. Plan for context lengths, costs, and capabilities to keep shifting.",
         "ফাউন্ডেশন মডেল আর তার দাম দ্রুত বদলায়। কনটেক্সট দৈর্ঘ্য, খরচ আর সক্ষমতা বদলাতে থাকবে ধরে নিয়ে তৈরি থাকুন।"),
        ("Build so that you can swap models or providers.",
         "মডেল বা প্রোভাইডার বদলানোর সুযোগ রেখে বানান।")],
       [sh("app", "hot", x=130, y=212), sh("fm", "hot", ("current model", "বর্তমান মডেল"), x=420, y=100), sh("alt", "dim", ("swap in", "বদলে নেওয়া যায়"), x=420, y=262)],
       [ln("app", "fm", "to", state="hot"), ln("app", "alt", "to", state="dim")],
       [("swappable", "বদলানো যায়"), None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("You can build on an existing model through an API instead of training your own.",
         "নিজের মডেল ট্রেইন না করে API দিয়ে আগে থেকে থাকা মডেলের ওপর বানানো যায়।")],
       [sh("lab", "hot"), sh("api", "hot"), sh("app", "hot")],
       [ln("lab", "api", "to", state="hot"), ln("api", "app", "to", state="hot")],
       [("through an API", "API দিয়ে"), None],
       points=[("Before building, define success with concrete business metrics and set a usefulness threshold to clear before going live.",
                "বানানোর আগে স্পষ্ট বিজনেস মেট্রিক দিয়ে সফলতা ঠিক করুন, আর লাইভে যাওয়ার আগে একটা উপযোগিতার সীমা রাখুন।"),
               ("The stack has three layers: application development, model development, and infrastructure. Most engineers work in application development.",
                "স্ট্যাকে তিন লেয়ার: অ্যাপ্লিকেশন ডেভেলপমেন্ট, মডেল ডেভেলপমেন্ট আর ইনফ্রাস্ট্রাকচার। বেশিরভাগ ইঞ্জিনিয়ার অ্যাপ্লিকেশন ডেভেলপমেন্টে কাজ করেন।"),
               ("Plan for change: build so you can swap models or providers.",
                "বদলের জন্য তৈরি থাকুন: মডেল বা প্রোভাইডার বদলানোর সুযোগ রেখে বানান।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
