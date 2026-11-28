"""Part ai-engineering-book · 08 Prompt Engineering: best practices and defensive prompting.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Habits     Body: "Write clear instructions, give enough context, split big tasks into subtasks, and let the model think." "Give the model time to think — chain-of-thought (CoT) prompting ("think step by step") and self-critique nudge the model toward more systematic reasoning and fewer hallucinations. Both can add latency."
  2 Over time  Body: "Keep prompts out of application code, and version them so teams can reuse and test them." "That allows reuse, independent testing, and safer rollout across teams."
  3 Attacks    Body: "A deployed application faces users who are not always well-intentioned." Table "Attack type": prompt extraction, jailbreaking, prompt injection, information extraction, each with "What it does".
  4 Indirect   Body: "A particularly dangerous evolution is indirect prompt injection ... When an agent with tool access reads that content, it can mistake the planted text for a legitimate instruction."
  5 Hierarchy  Body: "model-level: training the model to prioritize system prompts over user prompts, and user prompts over tool outputs, via an instruction hierarchy".
  6 Levels     Body: "Defenses operate at three levels:" model-level, prompt-level, system-level.
  7 Metrics    Body: "No single layer is foolproof. Track two metrics together: the violation rate (successful attacks) and the false refusal rate (safe requests wrongly blocked)."
  8 Remember   The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("clear", "note", ("Clear instructions", "স্পষ্ট নির্দেশ"), 120, 50),
    node("ctx", "note", ("Enough context", "যথেষ্ট কনটেক্সট"), 120, 125),
    node("split", "note", ("Subtasks", "subtask"), 120, 200),
    node("think", "note", ("Time to think", "ভাবার সুযোগ"), 120, 275),
    node("model", "model", ("Model", "মডেল"), 380, 162),
    node("catalog", "storage", ("Prompt catalog", "প্রম্পট ক্যাটালগ"), 130, 162),
    node("app", "service", ("Application", "অ্যাপ"), 650, 162),
    node("attacker", "user", ("Attacker", "আক্রমণকারী"), 130, 162),
    node("planted", "file", ("Planted text", "লুকানো লেখা"), 130, 162),
    node("sys", "note", ("System prompt", "সিস্টেম প্রম্পট"), 130, 75),
    node("usr", "user", ("User prompt", "ইউজার প্রম্পট"), 130, 162),
    node("tout", "tool", ("Tool output", "টুল আউটপুট"), 130, 250),
]

METRICS = [
    ("Violation rate", "ভায়োলেশন রেট"),
    ("False refusal rate", "ফলস রিফিউজাল রেট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Habits", "অভ্যাস"),
       ("Habits that make prompts reliable", "যে অভ্যাসে প্রম্পট ভরসাযোগ্য হয়"),
       [("Write clear instructions, give enough context, split big tasks into subtasks, and let the model think.",
         "স্পষ্ট নির্দেশ লিখুন, যথেষ্ট কনটেক্সট দিন, বড় কাজ ছোট subtask-এ ভাঙুন, আর মডেলকে ভাবার সুযোগ দিন।"),
        ("Chain-of-thought (\"think step by step\") and self-critique nudge the model toward more systematic reasoning. Both can add latency.",
         "চেইন-অফ-থট (ধাপে ধাপে ভাবতে বলা) আর self-critique মডেলকে আরও গুছিয়ে যুক্তি করার দিকে ঠেলে। দুটোতেই latency বাড়তে পারে।")],
       [sh("clear", "hot"), sh("ctx", "hot"), sh("split", "hot"), sh("think", "hot"), sh("model", "hot")],
       [ln("clear", "model", "to", state="hot"), ln("ctx", "model", "to", state="hot"),
        ln("split", "model", "to", state="hot"), ln("think", "model", "to", state="hot")],
       [None, None]),

    st(("Over time", "সময়ের সাথে"),
       ("Keep prompts out of the code", "প্রম্পট কোড থেকে আলাদা রাখুন"),
       [("Keep prompts out of application code, for example in a dedicated file or a prompt catalog, and version them.",
         "প্রম্পট অ্যাপের কোড থেকে আলাদা রাখুন, যেমন আলাদা ফাইলে বা প্রম্পট ক্যাটালগে, আর version করুন।"),
        ("That allows reuse, independent testing, and safer rollout across teams.",
         "এতে আবার ব্যবহার, আলাদাভাবে পরীক্ষা, আর টিমগুলোর মধ্যে নিরাপদ রোলআউট সম্ভব হয়।")],
       [sh("catalog", "hot", ("versioned", "version করা")), sh("app", "hot", ("code only", "শুধু কোড"))],
       [ln("catalog", "app", "to", state="hot")],
       [None, None]),

    st(("Attacks", "আক্রমণ"),
       ("A deployed app faces bad users", "চালু অ্যাপে খারাপ ব্যবহারকারী আসে"),
       [("A deployed application faces users who are not always well-intentioned.",
         "চালু অ্যাপের সামনে এমন ব্যবহারকারীও আসে যাদের উদ্দেশ্য সবসময় ভালো নয়।"),
        ("Attacks come in three groups, listed below.",
         "আক্রমণ তিন ধরনের, নিচে দেওয়া আছে।")],
       [sh("attacker", "warn"), sh("app", "warn"), sh("model", "dim", x=650, y=270)],
       [ln("attacker", "app", "to", state="warn"), ln("app", "model", "to", state="dim")],
       [None, None],
       changes=[("+", "Prompt extraction: recovers the hidden system prompt to copy or exploit an app",
                 "প্রম্পট এক্সট্রাকশন: লুকানো সিস্টেম প্রম্পট বের করে অ্যাপ কপি বা কাজে লাগানো"),
                ("+", "Jailbreaking and prompt injection: bypasses the model's safety behavior, or smuggles malicious instructions inside data the model processes",
                 "জেইলব্রেকিং ও প্রম্পট ইনজেকশন: মডেলের নিরাপত্তা-আচরণ এড়ানো, বা মডেলের পড়া ডেটার ভেতরে ক্ষতিকর নির্দেশ ঢুকিয়ে দেওয়া"),
                ("+", "Information extraction: pulls training data, private context, or copyrighted material out of the model",
                 "ইনফরমেশন এক্সট্রাকশন: মডেল থেকে ট্রেনিং ডেটা, প্রাইভেট কনটেক্সট বা কপিরাইট করা উপাদান বের করা")]),

    st(("Indirect", "পরোক্ষ"),
       ("Indirect prompt injection", "ইনডাইরেক্ট প্রম্পট ইনজেকশন"),
       [("Attackers plant bad instructions in content the model will later retrieve: a web page, a GitHub repo, an email, even a database field like a username.",
         "আক্রমণকারী এমন কনটেন্টে খারাপ নির্দেশ রেখে দেয় যা মডেল পরে আনে: ওয়েব পেজ, GitHub রিপো, ইমেইল, এমনকি ইউজারনেমের মতো ডেটাবেস ফিল্ড।"),
        ("When an agent with tool access reads it, it can mistake the planted text for a legitimate instruction.",
         "টুল-অ্যাক্সেসওয়ালা এজেন্ট সেটা পড়লে লুকানো লেখাকে আসল নির্দেশ ভেবে ভুল করতে পারে।")],
       [sh("planted", "warn", ("planted", "রাখা আছে")), sh("tout", "warn"), sh("model", "warn", ("mistakes it for real", "আসল ভেবে ভুল করে"))],
       [ln("planted", "tout", "to", state="warn"), ln("tout", "model", "to", state="warn")],
       [None, None],
       note=("warn", "The model reads the planted text later and mistakes it for a real instruction.",
             "মডেল লুকানো লেখা পরে পড়ে আর সেটাকে আসল নির্দেশ ভেবে ভুল করে।")),

    st(("Hierarchy", "হায়ারার্কি"),
       ("Trust system over user over tool", "সিস্টেম, তারপর ইউজার, তারপর টুল"),
       [("A model-level defense trains the model to prioritize system prompts over user prompts, and user prompts over tool outputs.",
         "মডেল-স্তরের সুরক্ষায় মডেলকে এমনভাবে ট্রেইন করা হয় যাতে সে ইউজার প্রম্পটের চেয়ে সিস্টেম প্রম্পটকে, আর টুল আউটপুটের চেয়ে ইউজার প্রম্পটকে বেশি গুরুত্ব দেয়।"),
        ("This is called an instruction hierarchy.",
         "একে বলে ইনস্ট্রাকশন হায়ারার্কি।")],
       [sh("sys", "hot", ("most trusted", "সবচেয়ে বেশি গুরুত্ব")), sh("usr", "hot"), sh("tout", "dim", ("least trusted", "সবচেয়ে কম গুরুত্ব")), sh("model", "hot")],
       [ln("sys", "model", "to", state="hot"), ln("usr", "model", "to", state="hot"), ln("tout", "model", "to", state="dim")],
       [None, None]),

    st(("Levels", "স্তর"),
       ("Defenses at three levels", "তিন স্তরে সুরক্ষা"),
       [("Defenses operate at three levels: the model, the prompt and the system.",
         "সুরক্ষা তিন স্তরে কাজ করে: মডেল, প্রম্পট আর সিস্টেম।"),
        ("Prompt-level means stating what must never be revealed, repeating key instructions, or pre-warning the model about known attack patterns.",
         "প্রম্পট-স্তরে স্পষ্ট বলা হয় কী কখনো প্রকাশ করা যাবে না, মূল নির্দেশ বারবার লেখা হয়, বা পরিচিত আক্রমণের ধরন নিয়ে মডেলকে আগে থেকে সতর্ক করা হয়।")],
       [sh("model", "hot", ("model-level", "মডেল-স্তর")), sh("sys", "hot", ("prompt-level", "প্রম্পট-স্তর")), sh("app", "hot", ("system-level", "সিস্টেম-স্তর"))],
       [ln("sys", "model", "to", state="hot"), ln("model", "app", "to", state="hot")],
       [None, None],
       note=("info", "System-level means input/output guardrails and anomaly detection on usage patterns.",
             "সিস্টেম-স্তর মানে input/output guardrail আর ব্যবহারের ধরনে anomaly detection।")),

    st(("Metrics", "মেট্রিক"),
       ("No layer is foolproof", "কোনো স্তরই নিশ্চিত নয়"),
       [("No single layer is foolproof.",
         "কোনো একটি স্তরই নিশ্চিত নয়।"),
        ("Track two metrics together: the violation rate, which counts successful attacks, and the false refusal rate, which counts safe requests wrongly blocked.",
         "দুটো মেট্রিক একসাথে নজরে রাখুন: ভায়োলেশন রেট, মানে সফল আক্রমণ, আর ফলস রিফিউজাল রেট, মানে ভুলে আটকানো নিরাপদ অনুরোধ।")],
       [sh("attacker", "warn", ("successful attacks", "সফল আক্রমণ"), y=75), sh("usr", "hot", ("safe requests", "নিরাপদ অনুরোধ"), y=250), sh("app", "hot")],
       [ln("attacker", "app", "to", state="warn"), ln("usr", "app", "to", state="hot")],
       [("successful attacks", "সফল আক্রমণ"), ("safe requests wrongly blocked", "ভুলে আটকানো নিরাপদ অনুরোধ")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Good habits make prompts reliable, and a deployed app must also defend against bad users.",
         "ভালো অভ্যাস প্রম্পটকে ভরসাযোগ্য করে, আর চালু অ্যাপকে খারাপ ব্যবহারকারীর হাত থেকেও বাঁচাতে হয়।")],
       [sh("catalog"), sh("app"), sh("model", x=650, y=270)],
       [ln("catalog", "app", "to"), ln("app", "model", "to")],
       [None, None],
       points=[("Write clear instructions, give enough context, split big tasks into subtasks, and let the model think.",
                "স্পষ্ট নির্দেশ লিখুন, যথেষ্ট কনটেক্সট দিন, বড় কাজ ছোট subtask-এ ভাঙুন, আর মডেলকে ভাবার সুযোগ দিন।"),
               ("Keep prompts out of application code, and version them so teams can reuse and test them.",
                "প্রম্পট অ্যাপের কোড থেকে আলাদা রাখুন আর version করুন, যাতে টিমগুলো আবার ব্যবহার ও পরীক্ষা করতে পারে।"),
               ("Attacks come in three groups: prompt extraction, jailbreaking and prompt injection, and information extraction.",
                "আক্রমণ তিন ধরনের: প্রম্পট এক্সট্রাকশন, জেইলব্রেকিং ও প্রম্পট ইনজেকশন, আর ইনফরমেশন এক্সট্রাকশন।"),
               ("No single defense layer is foolproof. Track the violation rate and the false refusal rate together.",
                "কোনো একটি সুরক্ষা স্তরই নিশ্চিত নয়। violation rate আর false refusal rate একসাথে নজরে রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
