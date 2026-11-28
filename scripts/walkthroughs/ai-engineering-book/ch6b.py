"""Part ai-engineering-book · 10 RAG and Agents: tools, planning, failure modes and memory.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Agent      Body, "Agent overview": "An agent is anything that perceives an environment and acts on it." "errors compound across steps: a 95% per-step accuracy drops to about 60% after 10 steps."
  2 Tools      Body, "Tools": "knowledge augmentation: retrievers, web search, internal APIs; capability extension: calculators, code interpreters, translators ...; write actions: tools that change something (sending an email, updating a database) rather than just reading data."
  3 Calling    Body: "Invoking a tool through a model API is called function calling. The tool is declared with a name, parameters, and description, and the model decides when and how to call it."
  4 Plan       Body, "Planning": "a plan is the sequence of actions meant to achieve it. Good practice decouples planning from execution. Generate a plan, validate it with heuristics or an AI judge, and only then execute it, so a bad plan never burns time and money."
  5 Reflection Body: "In reflection, the agent or a separate evaluator critiques the plan or the outcome. It is not mandatory, but it sharply improves reliability."
  6 Failures   Body, "Agent failure modes and evaluation": planning failures, tool failures, efficiency; info box "Always log every tool call and its output."
  7 Memory     Body, "Memory": "Short-term memory is the model's context window: fast but limited, and reset between tasks. Long-term memory is external storage ... It persists across sessions" and "commonly with a simple FIFO (first in, first out) strategy".
  8 Remember   The "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("env", "service", ("Environment", "পরিবেশ"), 130, 162),
    node("agent", "model", ("Agent", "এজেন্ট"), 380, 162),
    node("tools", "tool", ("Tools", "টুল"), 650, 162),
    node("know", "database", ("Knowledge augmentation", "জ্ঞান বাড়ানো"), 130, 75),
    node("cap", "tool", ("Capability extension", "সক্ষমতা বাড়ানো"), 130, 162),
    node("write", "tool", ("Write action", "রাইট অ্যাকশন"), 130, 250),
    node("decl", "file", ("Declared tool", "ঘোষণা করা টুল"), 130, 162),
    node("plan", "file", ("Plan", "প্ল্যান"), 130, 162),
    node("check", "shield", ("Validate", "যাচাই"), 380, 162),
    node("refl", "chart", ("Reflection", "রিফ্লেকশন"), 380, 162),
    node("stm", "cache", ("Short-term memory", "শর্ট-টার্ম মেমরি"), 380, 162),
    node("ltm", "storage", ("Long-term memory", "লং-টার্ম মেমরি"), 650, 162),
]

METRICS = [
    ("Accuracy per step", "প্রতি ধাপে নির্ভুলতা"),
    ("After 10 steps", "১০ ধাপ পরে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Agent", "এজেন্ট"),
       ("An agent senses and acts", "এজেন্ট বোঝে আর কাজ করে"),
       [("An agent is anything that perceives an environment and acts on it, using a set of tools.",
         "এজেন্ট হলো যা কোনো পরিবেশ বুঝতে পারে এবং একগুচ্ছ টুল দিয়ে সেখানে কাজ করে।"),
        ("Errors compound across steps: 95% accuracy per step drops to about 60% after 10 steps.",
         "ভুল ধাপে ধাপে জমে: প্রতি ধাপে ৯৫% নির্ভুলতা ১০ ধাপ পরে প্রায় ৬০% হয়ে যায়।")],
       [sh("env", "hot"), sh("agent", "hot"), sh("tools", "hot")],
       [ln("env", "agent", "to", state="hot"), ln("agent", "tools", "to", state="hot")],
       ["95%", ("about 60%", "প্রায় ৬০%")]),

    st(("Tools", "টুল"),
       ("Three kinds of tools", "তিন ধরনের টুল"),
       [("Knowledge augmentation tools are retrievers, web search and internal APIs. Capability extension tools are calculators, code interpreters and translators.",
         "জ্ঞান বাড়ানোর টুল হলো রিট্রিভার, ওয়েব সার্চ আর ইন্টারনাল API। সক্ষমতা বাড়ানোর টুল হলো ক্যালকুলেটর, কোড ইন্টারপ্রেটার আর অনুবাদক।"),
        ("Write actions change something, like sending an email, instead of only reading data.",
         "রাইট অ্যাকশন শুধু ডেটা পড়ে না, কিছু বদলায়, যেমন ইমেইল পাঠানো।")],
       [sh("know", "hot"), sh("cap", "hot"), sh("write", "warn"), sh("tools", "hot", x=380)],
       [ln("know", "tools", "to", state="hot"), ln("cap", "tools", "to", state="hot"), ln("write", "tools", "to", state="warn")],
       [None, None]),

    st(("Calling", "কলিং"),
       ("Function calling", "ফাংশন কলিং"),
       [("Invoking a tool through a model API is called function calling.",
         "মডেল API দিয়ে টুল ব্যবহার করাকে বলে ফাংশন কলিং।"),
        ("The tool is declared with a name, parameters and description, and the model decides when and how to call it.",
         "টুলটি নাম, প্যারামিটার আর বর্ণনাসহ ঘোষণা করা হয়, আর মডেল ঠিক করে কখন ও কীভাবে ডাকবে।")],
       [sh("decl", "hot", ("declared", "ঘোষণা করা")), sh("agent", "hot", ("decides when", "কখন ঠিক করে")), sh("tools", "hot")],
       [ln("decl", "agent", "to", state="hot"), ln("agent", "tools", "to", state="hot")],
       [None, None]),

    st(("Plan", "প্ল্যান"),
       ("Plan, validate, then execute", "প্ল্যান, যাচাই, তারপর চালানো"),
       [("A plan is the sequence of actions meant to achieve a goal. Good practice decouples planning from execution.",
         "প্ল্যান হলো লক্ষ্যে পৌঁছানোর কাজের ধারা। ভালো অভ্যাস হলো প্ল্যান করা আর চালানোকে আলাদা রাখা।"),
        ("Generate a plan, validate it with heuristics or an AI judge, and only then execute it, so a bad plan never burns time and money.",
         "প্ল্যান বানান, heuristic বা AI জাজ দিয়ে যাচাই করুন, তারপরই চালান, যাতে ভুল প্ল্যানে সময় ও টাকা নষ্ট না হয়।")],
       [sh("plan", "hot"), sh("check", "hot", ("AI judge", "AI জাজ")), sh("tools", "hot", ("only then", "তারপরই"))],
       [ln("plan", "check", "to", state="hot"), ln("check", "tools", "to", state="hot")],
       [None, None]),

    st(("Reflection", "রিফ্লেকশন"),
       ("Reflection looks it over", "রিফ্লেকশন দেখে নেয়"),
       [("In reflection, the agent or a separate evaluator critiques the plan or the outcome.",
         "রিফ্লেকশনে এজেন্ট নিজে বা আলাদা মূল্যায়নকারী প্ল্যান বা ফলের সমালোচনা করে।"),
        ("It is not mandatory, but it sharply improves reliability.",
         "এটা বাধ্যতামূলক নয়, কিন্তু নির্ভরযোগ্যতা অনেক বাড়ায়।")],
       [sh("plan", "hot"), sh("refl", "hot", ("not mandatory", "বাধ্যতামূলক নয়")), sh("tools", "hot", ("outcome", "ফল"))],
       [ln("plan", "refl", "to", state="hot"), ln("tools", "refl", "to", state="hot")],
       [None, None]),

    st(("Failures", "ব্যর্থতা"),
       ("How agents fail", "এজেন্ট কীভাবে ব্যর্থ হয়"),
       [("Agents fail in ways beyond ordinary model errors: planning failures, tool failures and poor efficiency.",
         "সাধারণ মডেল-ভুলের বাইরেও এজেন্ট ব্যর্থ হয়: প্ল্যানের ব্যর্থতা, টুলের ব্যর্থতা আর দক্ষতার অভাবে।"),
        ("Evaluation means tracking how often each failure mode occurs and comparing against a baseline.",
         "মূল্যায়ন মানে প্রতিটি ব্যর্থতা কতবার ঘটে তা ট্র্যাক করা আর বেসলাইনের সঙ্গে তুলনা করা।")],
       [sh("plan", "warn", ("wrong parameters", "ভুল প্যারামিটার")), sh("agent", "warn", ("too many steps", "অনেক ধাপ")), sh("tools", "warn", ("wrong result", "ভুল ফল"))],
       [ln("plan", "agent", "to", state="warn"), ln("agent", "tools", "to", state="warn")],
       [None, None],
       note=("insight", "Always log every tool call and its output. It is the single most useful habit for debugging an agent.",
             "প্রতিটি টুল কল আর তার আউটপুট সবসময় লগ করুন। এজেন্ট কেন ভুল করল তা ডিবাগ করতে এটাই সবচেয়ে কাজের অভ্যাস।")),

    st(("Memory", "মেমরি"),
       ("Short-term and long-term memory", "শর্ট-টার্ম আর লং-টার্ম মেমরি"),
       [("Short-term memory is the context window: fast but limited, and reset between tasks. Long-term memory is external storage that persists across sessions.",
         "শর্ট-টার্ম মেমরি হলো কনটেক্সট উইন্ডো: দ্রুত কিন্তু সীমিত, কাজ শেষে মুছে যায়। লং-টার্ম মেমরি বাইরের স্টোরেজ, যা সেশন পেরিয়েও থাকে।"),
        ("What overflows from short-term memory is commonly pushed into long-term storage with a simple FIFO strategy.",
         "শর্ট-টার্ম মেমরি থেকে যা উপচে পড়ে তা সাধারণত সহজ FIFO কৌশলে লং-টার্ম স্টোরেজে ঠেলে দেওয়া হয়।")],
       [sh("stm", "hot", ("fast but limited", "দ্রুত কিন্তু সীমিত")), sh("ltm", "hot", ("persists", "থেকে যায়")), sh("agent", "hot", x=130)],
       [ln("agent", "stm", "to", state="hot"), ln("stm", "ltm", "to", state="hot", label=("FIFO", "FIFO"))],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("An agent does more than talk: it uses tools and takes steps to get a job done.",
         "এজেন্ট শুধু কথা বলে না: কাজ শেষ করতে টুল ব্যবহার করে আর ধাপে ধাপে এগোয়।")],
       [sh("plan"), sh("check"), sh("tools")],
       [ln("plan", "check", "to"), ln("check", "tools", "to")],
       [None, None],
       points=[("Errors add up across steps: 95% accuracy per step drops to about 60% after 10 steps.",
                "ভুল ধাপে ধাপে জমে: প্রতি ধাপে ৯৫% নির্ভুলতা ১০ ধাপ পরে প্রায় ৬০% হয়ে যায়।"),
               ("Make a plan, validate it, and only then run it, so a bad plan wastes nothing.",
                "আগে প্ল্যান বানান, যাচাই করুন, তারপর চালান, যাতে ভুল প্ল্যানে কিছু নষ্ট না হয়।"),
               ("Agents fail through invalid tools, wrong parameters, missed constraints, costly plans, or tools that give wrong results or are missing.",
                "এজেন্ট ব্যর্থ হয় অবৈধ টুল, ভুল প্যারামিটার, শর্ত মিস, অতিরিক্ত খরচের প্ল্যান, বা ভুল ফল দেওয়া কিংবা না-থাকা টুলের কারণে।"),
               ("Log every tool call and its output. It is the best habit for debugging an agent.",
                "প্রতিটি টুল কল আর তার আউটপুট লগ করুন। ডিবাগের জন্য এটাই সবচেয়ে কাজের অভ্যাস।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
