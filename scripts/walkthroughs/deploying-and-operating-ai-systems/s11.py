"""Part 17 · 11 Metrics, logs and the observability stack: three signals, what to measure, and what to alert on.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Observe    Start here: "Observability means you can ask a running system why it behaves as it does, using the data it sends out. An AI service uses the ordinary tools, plus a few numbers for models and GPUs."
  2 Signals    Body, "Three signals": "The three signals are metrics (numbers over time), logs (events) and traces (the path of one request through the system)."
  3 Metrics    The table, metrics row: "Prometheus scrapes numbers from your services and stores them; Grafana draws dashboards" | "Trends, alerts, capacity"; word: "Metrics = Numbers measured over time. They show that something changed."
  4 Logs       The table, logs and traces rows: "Loki, Elasticsearch" | "The detail of one failure"; "OpenTelemetry produces them; Jaeger and Tempo show them" | "Where one slow request spent its time".
  5 Golden     Body, "What to measure": "The four golden signals: latency, traffic, errors and saturation."; word: "Saturation = How close a part of the system is to its limit, like a road so full that no more cars fit."
  6 LLM        "For an LLM service add time to first token, tokens per second, queue length and cost per request."; word: "Time to first token = How long a user waits before the first piece of the answer appears."
  7 GPUs       "For GPUs, NVIDIA's DCGM exporter publishes utilisation, memory and temperature as Prometheus metrics."
  8 Alerts     "Alert on what users feel (error rate, slow answers), not on every internal cause."
  9 Remember   The four "remember" points of the Start here box, and the "good" callout about Part 9.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("you", "user", ("You", "আপনি"), 110, 162),
    node("app", "service", ("AI service", "AI সার্ভিস"), 110, 162),
    node("gpu", "server", ("GPU", "GPU"), 110, 162),
    node("metrics", "chart", ("Metrics", "মেট্রিক"), 650, 75),
    node("logs", "file", ("Logs", "লগ"), 650, 162),
    node("traces", "clock", ("Traces", "ট্রেস"), 650, 250),
    node("prom", "database", ("Prometheus", "Prometheus"), 380, 162),
    node("grafana", "chart", ("Grafana", "Grafana"), 650, 162),
    node("otel", "tool", ("OpenTelemetry", "OpenTelemetry"), 380, 250),
    node("dcgm", "tool", ("DCGM exporter", "DCGM exporter"), 380, 162),
    node("alert", "shield", ("Alert", "অ্যালার্ট"), 380, 162),
]

METRICS = [
    ("Signals", "সংকেত"),
    ("Golden signals", "golden signal"),
    ("Alert on", "অ্যালার্ট দিন"),
]

CAPTION = (
    "Observability means you can ask a running system why it behaves as it does, using the data it sends out.",
    "অবজার্ভেবিলিটি মানে চলমান সিস্টেম নিজে যে ডেটা পাঠায় তা দিয়ে জিজ্ঞেস করতে পারা যে সে কেন এমন আচরণ করছে।",
)

STEPS = [
    st(("Observe", "পর্যবেক্ষণ"),
       ("Ask the system why", "সিস্টেমকে জিজ্ঞেস করুন কেন"),
       [("Observability means you can ask a running system why it behaves as it does, using the data it sends out.",
         "অবজার্ভেবিলিটি মানে চলমান সিস্টেম নিজে যে ডেটা পাঠায় তা দিয়ে জিজ্ঞেস করতে পারা যে সে কেন এমন আচরণ করছে।"),
        ("An AI service uses the ordinary tools, plus a few numbers for models and GPUs.",
         "AI সার্ভিসে সাধারণ টুলই লাগে, সঙ্গে মডেল আর GPU-র কিছু বিশেষ সংখ্যা।")],
       [sh("you", "hot", ("asks why", "কেন জিজ্ঞেস করে")), sh("app", "hot", ("sends out data", "ডেটা পাঠায়"), x=650)],
       [ln("app", "you", "to", state="hot", label=("data it sends out", "পাঠানো ডেটা"))],
       [None, None, None]),

    st(("Signals", "সংকেত"),
       ("Three signals", "তিনটি সংকেত"),
       [("The three signals are metrics (numbers over time), logs (events) and traces (the path of one request through the system).",
         "তিনটে সংকেত: মেট্রিক (সময়ের সাথে সংখ্যা), লগ (ঘটনা) আর ট্রেস (একটা অনুরোধ সিস্টেমের ভেতর দিয়ে যে পথে যায়)।")],
       [sh("app", "hot"), sh("metrics", "hot", ("numbers over time", "সময়ের সাথে সংখ্যা")), sh("logs", "hot", ("events", "ঘটনা")), sh("traces", "hot", ("path of one request", "একটা অনুরোধের পথ"))],
       [ln("app", "metrics", "to", state="hot"), ln("app", "logs", "to", state="hot"), ln("app", "traces", "to", state="hot")],
       [("three", "তিনটি"), None, None]),

    st(("Metrics", "মেট্রিক"),
       ("Numbers over time", "সময়ের সাথে সংখ্যা"),
       [("Metrics are numbers measured over time. They show that something changed, and they are good for trends, alerts and capacity.",
         "মেট্রিক হলো সময়ের সাথে মাপা সংখ্যা। এগুলো দেখায় কিছু বদলেছে, আর ট্রেন্ড, অ্যালার্ট ও ক্যাপাসিটির জন্য ভালো।"),
        ("Prometheus scrapes numbers from your services and stores them; Grafana draws dashboards.",
         "Prometheus সার্ভিস থেকে সংখ্যা তুলে জমা রাখে, Grafana ড্যাশবোর্ড আঁকে।")],
       [sh("app", "hot"), sh("prom", "hot", ("scrapes and stores", "তুলে জমা রাখে")), sh("grafana", "hot", ("draws dashboards", "ড্যাশবোর্ড আঁকে"))],
       [ln("app", "prom", "to", state="hot"), ln("prom", "grafana", "to", state="hot")],
       [None, None, None]),

    st(("Logs, traces", "লগ, ট্রেস"),
       ("Detail and path", "খুঁটিনাটি আর পথ"),
       [("Logs are records of events, good for the detail of one failure. Loki and Elasticsearch are tools you will meet.",
         "লগ ঘটনার রেকর্ড, একটা ব্যর্থতার খুঁটিনাটির জন্য ভালো। Loki আর Elasticsearch এমন টুল, যা আপনি দেখবেন।"),
        ("Traces follow one request through the system, good for seeing where one slow request spent its time. OpenTelemetry produces them; Jaeger and Tempo show them.",
         "ট্রেস একটা অনুরোধকে সিস্টেমের ভেতর দিয়ে অনুসরণ করে, ধীর অনুরোধ কোথায় সময় কাটিয়েছে তা দেখতে ভালো। OpenTelemetry ট্রেস তৈরি করে; Jaeger আর Tempo সেগুলো দেখায়।")],
       [sh("app", "hot"), sh("logs", "hot", ("Loki, Elasticsearch", "Loki, Elasticsearch"), y=75), sh("otel", "hot", ("produces traces", "ট্রেস তৈরি করে")),
        sh("traces", "hot", ("Jaeger, Tempo", "Jaeger, Tempo"))],
       [ln("app", "logs", "to", state="hot"), ln("app", "otel", "to", state="hot"), ln("otel", "traces", "to", state="hot")],
       [None, None, None]),

    st(("Golden", "গোল্ডেন"),
       ("The four golden signals", "চারটি golden signal"),
       [("Measure the four golden signals: latency, traffic, errors and saturation.",
         "চারটে golden signal মাপুন: latency, traffic, errors আর saturation।"),
        ("Saturation is how close a part of the system is to its limit, like a road so full that no more cars fit.",
         "স্যাচুরেশন হলো সিস্টেমের কোনো অংশ তার সীমার কত কাছে আছে, যেমন রাস্তা এত ভরা যে আর গাড়ি ঢোকার জায়গা নেই।")],
       [sh("app", "hot"), sh("metrics", "hot", ("four golden signals", "চারটি golden signal"), y=162)],
       [ln("app", "metrics", "to", state="hot")],
       [None, ("four", "চারটি"), None]),

    st(("LLM numbers", "LLM সংখ্যা"),
       ("Numbers for an LLM service", "LLM সার্ভিসের সংখ্যা"),
       [("For an LLM service, also track:",
         "LLM সার্ভিসে এগুলোও দেখুন:")],
       [sh("app", "hot"), sh("metrics", "hot", ("plus LLM numbers", "সাথে LLM সংখ্যা"), y=162)],
       [ln("app", "metrics", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Time to first token: how long a user waits before the first piece of the answer appears.",
                 "প্রথম টোকেন আসতে সময়: উত্তরের প্রথম অংশ আসার আগে ব্যবহারকারীকে কতক্ষণ অপেক্ষা করতে হয়।"),
                ("+", "Tokens per second.",
                 "প্রতি সেকেন্ডে টোকেন।"),
                ("+", "Queue length.",
                 "কিউ কত লম্বা।"),
                ("+", "Cost per request.",
                 "প্রতি রিকোয়েস্টে খরচ।")]),

    st(("GPUs", "GPU"),
       ("GPU numbers", "GPU-র সংখ্যা"),
       [("For GPUs, NVIDIA's DCGM exporter publishes utilization, memory and temperature as Prometheus metrics.",
         "GPU-র ব্যবহার, মেমরি আর তাপমাত্রা NVIDIA-র DCGM exporter Prometheus মেট্রিক হিসেবে প্রকাশ করে।")],
       [sh("gpu", "hot"), sh("dcgm", "hot", ("use, memory, temperature", "ব্যবহার, মেমরি, তাপমাত্রা")), sh("prom", "hot", x=650)],
       [ln("gpu", "dcgm", "to", state="hot"), ln("dcgm", "prom", "to", state="hot")],
       [None, None, None]),

    st(("Alerts", "অ্যালার্ট"),
       ("Alert on what users feel", "ব্যবহারকারী যা টের পায় তাতে অ্যালার্ট"),
       [("Alert on what users feel (error rate, slow answers), not on every internal cause.",
         "ব্যবহারকারী যা টের পায় (এরর রেট, ধীর উত্তর) তার ওপর অ্যালার্ট দিন, প্রতিটি ভেতরের কারণে নয়।")],
       [sh("metrics", "hot", x=110, y=162), sh("alert", "hot", ("error rate, slow answers", "এরর রেট, ধীর উত্তর"))],
       [ln("metrics", "alert", "to", state="hot")],
       [None, None, ("What users feel", "যা ব্যবহারকারী টের পায়")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Observability means you can ask a running system why it behaves as it does, using the data it sends out. An AI service uses the ordinary tools, plus a few numbers for models and GPUs.",
         "অবজার্ভেবিলিটি মানে চলমান সিস্টেম নিজে যে ডেটা পাঠায় তা দিয়ে জিজ্ঞেস করতে পারা যে সে কেন এমন আচরণ করছে। AI সার্ভিসে সাধারণ টুলই লাগে, সঙ্গে মডেল আর GPU-র কিছু বিশেষ সংখ্যা।")],
       [sh("app", x=90), sh("metrics", x=345, y=162), sh("alert", x=635)],
       [ln("app", "metrics", "to"), ln("metrics", "alert", "to")],
       [None, None, None],
       points=[("The three signals are metrics, logs and traces.",
                "তিনটে সংকেত হলো মেট্রিক, লগ আর ট্রেস।"),
               ("Measure the four golden signals: latency, traffic, errors and saturation.",
                "চারটে golden signal মাপুন: latency, traffic, errors আর saturation।"),
               ("For an LLM service, also track time to first token, tokens per second, queue length and cost per request.",
                "LLM সার্ভিসে প্রথম টোকেন আসতে সময়, প্রতি সেকেন্ডে টোকেন, কিউ কত লম্বা আর প্রতি রিকোয়েস্টে খরচও দেখুন।"),
               ("Alert on what users feel, such as error rate and slow answers, not on every internal cause.",
                "ব্যবহারকারী যা টের পায় তার ওপর অ্যালার্ট দিন, যেমন এরর রেট আর ধীর উত্তর; প্রতিটি ভেতরের কারণে নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
