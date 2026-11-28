"""Prompt Engineering · 08 Prompt injection defense at the prompt layer: instructions hidden in data, and the layers that lower the risk.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Injection Intro: "Prompt injection is when instructions hidden inside data try to hijack the model. Prompt-layer defenses lower the risk but never remove it, so use several together." Term "Prompt injection".
  2 Two ways  Diagram "The attack surface": "Direct: the attacker types the prompt. Indirect: the attacker poisons the data the model reads. Both bypass naive system prompts." Term "Indirect injection".
  3 Wrap      "1. Data wrapping": "Wrap every piece of untrusted input ... in clearly labeled tags. Tell the model in the system prompt that content inside the tags is data, not instructions."
  4 Sandwich  "2. Sandwich / repeat instructions": "Repeat the critical rules at the end of the prompt ... instructions, data, instructions". Callout: "Repeating the rules at the end may help the model follow them."
  5 Limits    "4. Length / structure limits": "Cap the size of injected content (e.g., max 4K tokens of retrieved text)". "6. Output-side detection": check the response after the call.
  6 Allowlist "5. Output constraints": "Tool calls have an allowlist." Callout: "Enforce the tool allowlist in your own code, not by trusting the model."
  7 Not a lock Danger box: "No prompt-layer defense is bulletproof ... Combine prompt-layer defenses with system-layer defenses." Practice: "prompt rules are a speed bump, not a lock."
  8 Remember  Callout: "No prompt-layer defense is bulletproof. Use them together, and add system-layer defenses too."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ইউজার"), 130, 80),
    node("doc", "file", ("Retrieved document", "খুঁজে আনা ডকুমেন্ট"), 130, 250),
    node("model", "model", ("Model", "মডেল"), 630, 100),
    node("rules", "note", ("System rules", "সিস্টেম নিয়ম"), 130, 100),
    node("tags", "shield", ("Tagged data", "ট্যাগে মোড়া ডেটা"), 380, 100),
    node("remind", "note", ("Rules again", "নিয়ম আবার"), 630, 250),
    node("cap", "shield", ("Capped input", "সীমা দেওয়া ইনপুট"), 380, 250),
    node("out", "note", ("Output check", "আউটপুট পরীক্ষা"), 630, 250),
    node("allow", "lock", ("Tool allowlist", "টুল অ্যালাউলিস্ট"), 380, 250),
    node("sys", "service", ("System-layer defenses", "সিস্টেম-স্তরের প্রতিরক্ষা"), 630, 250),
]

METRICS = [
    ("Risk", "ঝুঁকি"),
    ("Layers", "স্তর"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Injection", "ইনজেকশন"),
       ("Instructions hidden in data", "ডেটার ভেতরে লুকানো নির্দেশ"),
       [("Prompt injection is when instructions hidden inside data try to hijack the model.",
         "প্রম্পট ইনজেকশন হলো ডেটার ভেতরে লুকানো নির্দেশ দিয়ে মডেলকে হাইজ্যাক করার চেষ্টা।"),
        ("Prompt-layer defenses lower the risk but never remove it, so use several together.",
         "প্রম্পট-স্তরের প্রতিরক্ষা ঝুঁকি কমায়, শেষ করে না, তাই একসাথে কয়েকটা ব্যবহার করুন।")],
       [sh("rules", "dim", x=130, y=250), sh("user", "warn", x=130, y=100), sh("model", "warn", ("hijack", "হাইজ্যাক"), x=630, y=162)],
       [ln("user", "model", "to", state="warn")],
       [("lowered, not removed", "কমে, শেষ হয় না"), None]),

    st(("Two ways", "দুই পথ"),
       ("Direct and indirect injection", "ডাইরেক্ট আর ইনডাইরেক্ট ইনজেকশন"),
       [("Direct: the attacker types the prompt.",
         "ডাইরেক্ট: আক্রমণকারী নিজেই প্রম্পট টাইপ করে।"),
        ("Indirect: the attacker poisons the data the model reads, such as a retrieved document. Both bypass naive system prompts.",
         "ইনডাইরেক্ট: আক্রমণকারী মডেলের পড়া ডেটা, যেমন খুঁজে আনা কোনো ডকুমেন্ট, বিষিয়ে রাখে। উভয়ই সাধারণ সিস্টেম প্রম্পট এড়িয়ে যেতে পারে।")],
       [sh("user", "warn", ("types it", "টাইপ করে")), sh("doc", "warn", ("poisoned", "বিষানো")), sh("model", "hot", x=630, y=162)],
       [ln("user", "model", "to", state="warn"), ln("doc", "model", "to", state="warn")],
       [None, None]),

    st(("Wrap", "র‍্যাপ"),
       ("Wrap untrusted input in tags", "আনট্রাস্টেড ইনপুট ট্যাগে মুড়ুন"),
       [("Wrap every piece of untrusted input in clearly labeled tags.",
         "প্রতিটি আনট্রাস্টেড ইনপুট স্পষ্ট নামের ট্যাগে মুড়ে দিন।"),
        ("Tell the model in the system prompt that the content inside the tags is data, not instructions.",
         "সিস্টেম প্রম্পটে মডেলকে বলে দিন যে ট্যাগের ভেতরটা ডেটা, নির্দেশ নয়।")],
       [sh("rules", "hot"), sh("tags", "hot", ("data", "ডেটা")), sh("model", "hot")],
       [ln("rules", "tags", "to", state="hot"), ln("tags", "model", "to", state="hot")],
       [("lowered", "কমে"), None]),

    st(("Sandwich", "স্যান্ডউইচ"),
       ("Sandwich: repeat the rules", "স্যান্ডউইচ: নিয়ম আবার বলুন"),
       [("A sandwich is instructions, then data, then the instructions again.",
         "স্যান্ডউইচ মানে নির্দেশ, তারপর ডেটা, তারপর আবার নির্দেশ।"),
        ("Repeating the rules at the end may help the model follow them.",
         "শেষে আবার বলা নিয়ম মডেলকে সেগুলো মানতে সাহায্য করতে পারে।")],
       [sh("rules", "hot"), sh("tags", "hot", ("data", "ডেটা")), sh("model", "hot"), sh("remind", "hot")],
       [ln("rules", "tags", "to", state="hot"), ln("tags", "model", "to", state="hot"), ln("model", "remind", "to", state="hot")],
       [None, None]),

    st(("Limits", "সীমা"),
       ("Cap the input, check the output", "ইনপুটের সীমা দিন, আউটপুট দেখুন"),
       [("Cap the injected content, for example 4K tokens of retrieved text.",
         "ইনজেক্ট করা কনটেন্টের সীমা দিন, যেমন ৪K টোকেন।"),
        ("After the call, check the output for signs of a hijack.",
         "কলের পরে হাইজ্যাকের লক্ষণ আছে কি না আউটপুটে দেখুন।")],
       [sh("doc", "hot"), sh("cap", "hot", ("4K tokens", "৪K টোকেন")), sh("model", "hot"), sh("out", "hot")],
       [ln("doc", "cap", "to", state="hot"), ln("cap", "model", "to", state="hot"), ln("model", "out", "to", state="hot")],
       [None, None]),

    st(("Allowlist", "অ্যালাউলিস্ট"),
       ("Enforce the tool allowlist in your code", "টুল অ্যালাউলিস্ট নিজের কোডে প্রয়োগ করুন"),
       [("An allowlist is a list of the only tools allowed to run. Anything not on the list is refused.",
         "অ্যালাউলিস্ট হলো শুধু যেসব টুল চালানোর অনুমতি আছে তার তালিকা। তালিকায় না থাকলে প্রত্যাখ্যান করা হয়।"),
        ("Enforce it in your own code, not by trusting the model.",
         "এটা নিজের কোডে প্রয়োগ করুন, মডেলের ওপর ভরসা করে নয়।")],
       [sh("model", "hot"), sh("allow", "hot")],
       [ln("model", "allow", "to", state="hot")],
       [None, None]),

    st(("Not a lock", "তালা নয়"),
       ("No prompt-layer defense is bulletproof", "কোনো প্রম্পট-স্তরের প্রতিরক্ষাই অভেদ্য নয়"),
       [("Use the prompt-layer defenses together, and add system-layer defenses too.",
         "প্রম্পট-স্তরের প্রতিরক্ষাগুলো একসাথে ব্যবহার করুন, সাথে সিস্টেম-স্তরের প্রতিরক্ষাও যোগ করুন।"),
        ("Defence in depth means many layers, so that one broken layer does not break everything.",
         "ডিফেন্স ইন ডেপথ মানে অনেক স্তর, যাতে এক স্তর ভাঙলেও সব না ভাঙে।")],
       [sh("tags", "hot", x=130, y=100), sh("remind", "hot", x=380, y=100), sh("allow", "hot", x=630, y=100), sh("sys", "hot", ("add these too", "এগুলোও যোগ করুন"))],
       [ln("allow", "sys", "to", state="hot")],
       [("lowered, not removed", "কমে, শেষ হয় না"), ("use several together", "একসাথে কয়েকটা")],
       note=("warn", "A prompt rule is a speed bump, not a lock.",
             "প্রম্পটের নিয়ম স্পিড ব্রেকার, তালা নয়।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("No prompt-layer defense is bulletproof. Use them together, and add system-layer defenses too.",
         "কোনো প্রম্পট-স্তরের প্রতিরক্ষাই অভেদ্য নয়। এগুলো একসাথে ব্যবহার করুন, সাথে সিস্টেম-স্তরের প্রতিরক্ষাও যোগ করুন।")],
       [sh("tags", "hot", x=130, y=100), sh("remind", "hot", x=380, y=100), sh("allow", "hot", x=630, y=100), sh("sys", "hot")],
       [ln("allow", "sys", "to")],
       [None, None],
       points=[("Wrap untrusted input in tags, and tell the model in the system prompt that it is data.",
                "আনট্রাস্টেড ইনপুট ট্যাগে মুড়ুন, আর সিস্টেম প্রম্পটে মডেলকে বলে দিন যে এটা ডেটা।"),
               ("Enforce the tool allowlist in your own code, not by trusting the model.",
                "টুল অ্যালাউলিস্ট নিজের কোডে প্রয়োগ করুন, মডেলের ওপর ভরসা করে নয়।"),
               ("Cap injected content, for example 4K tokens, and check the output for signs of a hijack.",
                "ইনজেক্ট করা কনটেন্টের সীমা দিন, যেমন ৪K টোকেন, আর হাইজ্যাকের লক্ষণ আছে কি না আউটপুটে দেখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
