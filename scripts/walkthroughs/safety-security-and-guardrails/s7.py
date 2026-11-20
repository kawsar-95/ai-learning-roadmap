"""Part 12 · 01 Safety, security & guardrails: the new attack surface of an LLM app, and the checks that bound it.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Surface     Start here: "An AI app can be attacked in new ways: through the prompt, the tool calls, and the output. Safety is the work of limiting those risks."; sub-title: "the prompt is now user-influenced input, the tool calls are now an exfiltration channel, and the rendered output is now a script-execution context."
  2 Injection   Body, "Prompt injection": "Prompt injection is when user-controlled text hijacks the model's behaviour. Direct: the user types ... Indirect: the user plants malicious text in a document the model will read ... Indirect injection is the harder one because the user doesn't even need to interact with your system."
  3 Jailbreak   Body, "Jailbreak resistance": "Jailbreaks are creative rewrites of forbidden prompts that slip past safety training ... a moving target: red-teams find new ones monthly. Defences: Constitutional AI fine-tuning, output classifiers, robust system prompts, and accepting that 100% safety is unachievable."
  4 Exfiltrate  Body, "Data exfiltration via tool calls and rendered links": "a prompt-injected output can call a tool with attacker-chosen arguments ... or render a Markdown image whose src URL encodes the user's session. The OWASP LLM Top 10 ranks prompt injection, the cause of this attack, #1 in 2025."
  5 Screens     Body, "Content moderation" and "PII redaction in inputs and outputs": a table of moderation tools; "Before sending user text to the model (and before rendering the model's reply), run a PII detector".
  6 Rails       Body, "Guardrail frameworks" and "Output validation against schemas": NeMo Guardrails, Guardrails AI; "Never trust an LLM to emit valid JSON. Parse with a strict schema (Pydantic, Zod); on failure, retry once, then refuse. Treat malformed output as a security event, not just a bug."
  7 Limits      Body, "Rate limiting and abuse prevention": "Per-user token budgets per day, per-IP request limits, jailbreak-attempt counters, cost-based alarms. Without these, a single user ... can burn budget or trigger a bill spike."
  8 Audit log   Body, "Audit logging for compliance": "Log every prompt, every model output, every tool call, every approval decision, every redacted PII. SOC 2, HIPAA, and EU AI Act conformance all require this."
  9 Remember    The five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ইউজার"), 110, 162),
    node("doc", "file", ("Document", "ডকুমেন্ট"), 380, 75),
    node("model", "model", ("Model", "মডেল"), 380, 162),
    node("schema", "lock", ("Strict schema", "কড়া স্কিমা"), 380, 162),
    node("limit", "clock", ("Rate limit", "রেট লিমিট"), 380, 162),
    node("tool", "tool", ("Tool calls", "টুল কল"), 650, 75),
    node("out", "browser", ("Output", "আউটপুট"), 650, 250),
    node("guard", "shield", ("Guard", "গার্ড"), 650, 162),
    node("evil", "server", ("Attacker", "আক্রমণকারী"), 650, 162),
    node("log", "storage", ("Audit log", "অডিট লগ"), 650, 162),
]

METRICS = [
    ("OWASP 2025", "OWASP ২০২৫"),
    ("100% safety", "১০০% সেফটি"),
    ("Retries", "রিট্রাই"),
]

CAPTION = (
    "An AI app can be attacked through the prompt, the tool calls, and the output. Safety is the work of limiting those risks.",
    "AI অ্যাপকে প্রম্পট, টুল কল আর আউটপুটের মধ্য দিয়ে আক্রমণ করা যায়। সেফটি হলো সেই ঝুঁকিগুলো সীমার মধ্যে রাখার কাজ।",
)

STEPS = [
    st(("Surface", "ঝুঁকির জায়গা"),
       ("A new attack surface", "আক্রমণের নতুন জায়গা"),
       [("An AI app can be attacked in new ways: through the prompt, the tool calls, and the output. Safety is the work of limiting those risks.",
         "AI অ্যাপকে নতুন উপায়ে আক্রমণ করা যায়: প্রম্পট, টুল কল আর আউটপুটের মধ্য দিয়ে। সেফটি হলো সেই ঝুঁকিগুলো সীমার মধ্যে রাখার কাজ।"),
        ("The prompt is now user-influenced input, the tool calls are now an exfiltration channel, and the rendered output is now a script-execution context.",
         "প্রম্পট এখন ইউজারের প্রভাবে বদলায়, টুল কল এখন ডেটা বের করে নেওয়ার পথ, আর রেন্ডার করা আউটপুট এখন স্ক্রিপ্ট চলার জায়গা।")],
       [sh("user", "warn", ("the prompt", "প্রম্পট")), sh("model", "hot"), sh("tool", "warn", ("data can leave", "ডেটা বেরোয়")),
        sh("out", "warn", ("runs scripts", "স্ক্রিপ্ট চলে"))],
       [ln("user", "model", "to"), ln("model", "tool", "to"), ln("model", "out", "to")],
       [None, None, None]),

    st(("Injection", "ইনজেকশন"),
       ("Prompt injection", "প্রম্পট ইনজেকশন"),
       [("Prompt injection is when user-controlled text hijacks the model's behavior. Direct: the user types the attack. Indirect: the user plants malicious text in a document the model will read.",
         "প্রম্পট ইনজেকশন হলো ইউজারের নিয়ন্ত্রণে থাকা টেক্সট মডেলের আচরণ দখল করে নেওয়া। প্রত্যক্ষ: ইউজার নিজেই আক্রমণ টাইপ করে। পরোক্ষ: ইউজার মডেলের পড়া ডকুমেন্টে ক্ষতিকর টেক্সট রোপণ করে।")],
       [sh("user", "warn", ("attacker", "আক্রমণকারী")), sh("doc", "warn", ("planted text", "রোপণ করা টেক্সট")), sh("model", "hot")],
       [ln("user", "model", "to", state="warn"), ln("user", "doc", "to", state="warn"), ln("doc", "model", "to", state="warn")],
       [None, None, None],
       note=("insight",
             "Indirect injection is the harder one because the user doesn't even need to interact with your system.",
             "পরোক্ষ ইনজেকশন বেশি কঠিন, কারণ আক্রমণকারীকে আপনার সিস্টেম ব্যবহারই করতে হয় না।")),

    st(("Jailbreak", "জেইলব্রেক"),
       ("Jailbreaks", "জেইলব্রেক"),
       [("Jailbreaks are creative rewrites of forbidden prompts that slip past safety training. They're a moving target: red teams find new ones monthly.",
         "জেইলব্রেক হলো নিষিদ্ধ প্রম্পটের এমন সৃজনশীল পুনর্লিখন, যা সেফটি ট্রেনিংয়ের পাশ কাটিয়ে যায়। এগুলো একটি চলমান লক্ষ্য: রেড-টিম প্রতি মাসে নতুন জেইলব্রেক খুঁজে পায়।"),
        ("Defenses: Constitutional AI fine-tuning, output classifiers, robust system prompts, and accepting that 100% safety is unachievable.",
         "প্রতিরক্ষা: Constitutional AI ফাইন-টিউনিং, আউটপুট ক্লাসিফায়ার, মজবুত সিস্টেম প্রম্পট। ১০০% সেফটি অর্জনযোগ্য নয়, এটি মেনে নিন।")],
       [sh("user", "warn", ("creative rewrite", "সৃজনশীল পুনর্লিখন")), sh("model", "hot", ("safety training", "সেফটি ট্রেনিং")),
        sh("guard", "hot", ("output classifier", "আউটপুট ক্লাসিফায়ার"))],
       [ln("user", "model", "to", state="warn"), ln("model", "guard", "to", state="hot")],
       [None, ("unachievable", "অর্জনযোগ্য নয়"), None]),

    st(("Exfiltrate", "ডেটা বেরোনো"),
       ("Data leaves through tools and links", "টুল আর লিংক দিয়ে ডেটা বেরোয়"),
       [("Once the model can call tools or render Markdown, a prompt-injected output can call a tool with attacker-chosen arguments, or render a Markdown image whose src URL encodes the user's session.",
         "মডেল একবার টুল কল করতে বা Markdown রেন্ডার করতে পারলে প্রম্পট-ইনজেক্টেড আউটপুট আক্রমণকারীর বেছে দেওয়া আর্গুমেন্ট সহ টুল কল করতে পারে, অথবা এমন Markdown ছবি রেন্ডার করতে পারে, যার src URL ইউজারের সেশন এনকোড করে।"),
        ("The OWASP LLM Top 10 ranks prompt injection, the cause of this attack, #1 in 2025.",
         "এই আক্রমণের মূলে আছে প্রম্পট ইনজেকশন, আর OWASP LLM Top ১০ সেটিকে ২০২৫-এ #১ হিসেবে তালিকাভুক্ত করেছে।")],
       [sh("model", "hot", None, None, 110, 162), sh("tool", "warn", ("attacker's choice", "আক্রমণকারীর পছন্দ"), None, 380, 75),
        sh("out", "warn", ("session in URL", "URL-এ সেশন"), None, 380, 250), sh("evil", "warn", ("gets the data", "ডেটা পায়"))],
       [ln("model", "tool", "to", state="warn"), ln("model", "out", "to", state="warn"),
        ln("tool", "evil", "to", state="warn"), ln("out", "evil", "to", state="warn")],
       [("#1", "#১"), None, None]),

    st(("Screens", "যাচাই"),
       ("Screen the text in and out", "ঢোকা আর বেরোনো লেখা যাচাই"),
       [("Content moderation checks text for harmful content, such as hate, sexual content, violence, and self-harm. Run it on both the input and the output.",
         "কনটেন্ট মডারেশন টেক্সটে ক্ষতিকর বিষয় আছে কি না যাচাই করে, যেমন ঘৃণা, যৌনতা, সহিংসতা, আত্মক্ষতি। ইনপুট আর আউটপুট দুটোতেই চালান।"),
        ("PII redaction removes personal details from the text before the model sees it, and again before the reply is shown.",
         "PII রিড্যাকশন মডেল দেখার আগে, আর উত্তর দেখানোর আগেও, লেখা থেকে ব্যক্তিগত তথ্য সরিয়ে ফেলে।")],
       [sh("user"), sh("guard", "hot", ("moderation, PII", "মডারেশন, PII"), None, 380, 162), sh("model", "hot", None, None, 650, 162)],
       [ln("user", "guard", "both", state="hot"), ln("guard", "model", "both", state="hot")],
       [None, None, None],
       changes=[("+", "OpenAI moderation endpoint: a free, fast, multi-category classifier",
                 "OpenAI মডারেশন এন্ডপয়েন্ট: ফ্রি, দ্রুত, বহু-বিভাগীয় ক্লাসিফায়ার"),
                ("+", "Llama Guard: an open-weight guard model, a drop-in classifier for input and output",
                 "Llama Guard: ওপেন-ওয়েট গার্ড মডেল, ইনপুট আর আউটপুটের জন্য সরাসরি বসানো ক্লাসিফায়ার"),
                ("+", "Microsoft Presidio and spaCy: PII detectors",
                 "Microsoft Presidio আর spaCy: PII ডিটেক্টর")]),

    st(("Rails", "রেইল"),
       ("Rails and strict schemas", "রেইল আর কড়া স্কিমা"),
       [("Never trust an LLM to emit valid JSON. Parse with a strict schema (Pydantic, Zod); on failure, retry once, then refuse.",
         "ভ্যালিড JSON দেওয়ার জন্য LLM-কে কখনো বিশ্বাস করবেন না। একটি কড়া স্কিমা (Pydantic, Zod) দিয়ে পার্স করুন; ব্যর্থ হলে একবার রিট্রাই, তারপর রিফিউজ।"),
        ("Treat malformed output as a security event, not just a bug.",
         "ম্যালফর্মড আউটপুটকে শুধু বাগ নয়, সিকিউরিটি ইভেন্ট হিসেবে দেখুন।")],
       [sh("model", "hot", None, None, 110, 162), sh("schema", "hot", ("parse strictly", "কড়া পার্স")), sh("out", "hot", ("valid output", "বৈধ আউটপুট"), None, 650, 162)],
       [ln("model", "schema", "both", state="hot", label=("retry once", "আরেকবার")), ln("schema", "out", "to", state="hot")],
       [None, None, ("once", "একবার")],
       changes=[("+", "NeMo Guardrails (NVIDIA): programmable rails for topics, actions, and structured output",
                 "NeMo Guardrails (NVIDIA): বিষয়, অ্যাকশন আর কাঠামোবদ্ধ আউটপুটের জন্য প্রোগ্রামযোগ্য রেইল"),
                ("+", "Guardrails AI: validators (PII regex, profanity, factuality, JSON schema) you compose around any LLM call",
                 "Guardrails AI: যেকোনো LLM কলের চারপাশে বসানোর ভ্যালিডেটর (PII রেজেক্স, প্রোফেনিটি, ফ্যাক্চুয়ালিটি, JSON স্কিমা)")]),

    st(("Limits", "সীমা"),
       ("Rate limits against abuse", "অপব্যবহার ঠেকাতে রেট লিমিট"),
       [("Set per-user token budgets per day, per-IP request limits, jailbreak-attempt counters, and cost-based alarms.",
         "প্রতি-ইউজার দৈনিক টোকেন বাজেট, প্রতি-IP রিকোয়েস্ট সীমা, জেইলব্রেক-চেষ্টার কাউন্টার আর খরচ-ভিত্তিক অ্যালার্ম রাখুন।"),
        ("Without these, a single user (or a single prompt-injection botnet) can burn budget or trigger a bill spike.",
         "এগুলো না থাকলে একজন ইউজার (বা একটি প্রম্পট-ইনজেকশন বটনেট) বাজেট পুড়িয়ে ফেলতে বা বিল হঠাৎ বাড়িয়ে দিতে পারে।")],
       [sh("user", "warn", ("one bot", "একটি বট")), sh("limit", "hot", ("token budgets", "টোকেন বাজেট")), sh("model", None, None, None, 650, 162)],
       [ln("user", "limit", "to", state="warn"), ln("limit", "model", "to", state="hot")],
       [None, None, None]),

    st(("Audit log", "অডিট লগ"),
       ("Audit logging", "অডিট লগিং"),
       [("Log every prompt, every model output, every tool call, every approval decision, and every redacted PII.",
         "প্রতিটি প্রম্পট, প্রতিটি মডেল আউটপুট, প্রতিটি টুল কল, প্রতিটি অনুমোদনের সিদ্ধান্ত আর প্রতিটি রিড্যাক্ট করা PII লগ করুন।")],
       [sh("user", "hot", ("every prompt", "প্রতিটি প্রম্পট"), None, 110, 75), sh("model", "hot", ("every output", "প্রতিটি আউটপুট"), None, 110, 162),
        sh("tool", "hot", ("every call", "প্রতিটি কল"), None, 110, 250), sh("log", "hot")],
       [ln("user", "log", "to", state="hot"), ln("model", "log", "to", state="hot"), ln("tool", "log", "to", state="hot")],
       [None, None, None],
       note=("insight",
             "SOC 2, HIPAA, and EU AI Act conformance all require this. Treat your LLM as a regulated component.",
             "SOC ২, HIPAA, EU AI Act-এর সম্মতি সবকিছুর জন্য এটি দরকার। আপনার LLM-কে একটি রেগুলেটেড কম্পোনেন্ট হিসেবে দেখুন।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("An AI app can be attacked in new ways, through the prompt, the tool calls, and the output. Safety is the work of limiting those risks.",
         "AI অ্যাপকে নতুন উপায়ে আক্রমণ করা যায়: প্রম্পট, টুল কল আর আউটপুটের মধ্য দিয়ে। সেফটি হলো সেই ঝুঁকিগুলো সীমার মধ্যে রাখার কাজ।")],
       [sh("user"), sh("guard", None, None, None, 380, 162), sh("model", None, None, None, 650, 162), sh("log", None, None, None, 380, 250)],
       [ln("user", "guard", "both"), ln("guard", "model", "both"), ln("model", "log", "to")],
       [None, None, None],
       points=[("Indirect injection is the harder kind, because the attacker never needs to use your system.",
                "পরোক্ষ ইনজেকশন বেশি কঠিন, কারণ আক্রমণকারীকে আপনার সিস্টেম ব্যবহারই করতে হয় না।"),
               ("Prompt injection, ranked #1 in the OWASP LLM Top 10 for 2025, can make tools or Markdown leak user data.",
                "২০২৫-এর OWASP LLM Top 10-এ #১ স্থানে থাকা প্রম্পট ইনজেকশন টুল বা Markdown দিয়ে ইউজারের ডেটা বাইরে পাঠাতে পারে।"),
               ("Accept that 100% safety is unachievable. Jailbreaks are a moving target.",
                "১০০% সেফটি অর্জনযোগ্য নয়, এটা মেনে নিন। জেইলব্রেক একটি চলমান লক্ষ্য।"),
               ("Never trust an LLM to emit valid JSON. Parse with a strict schema; if it fails, retry once, then refuse.",
                "LLM-এর ভ্যালিড JSON দেওয়ার ওপর কখনো ভরসা করবেন না। কড়া স্কিমা দিয়ে পার্স করুন; ব্যর্থ হলে একবার রিট্রাই করুন, তারপর রিফিউজ করুন।"),
               ("Log every prompt, output, and tool call. SOC 2, HIPAA, and the EU AI Act require it.",
                "প্রতিটি প্রম্পট, আউটপুট আর টুল কল লগ করুন। SOC ২, HIPAA আর EU AI Act-এ এটা দরকার।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
