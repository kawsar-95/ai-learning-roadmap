"""Part 14 · 01 AI application architecture: the plumbing around one LLM call.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Plumbing    Start here: "An AI product is more than one model call. It needs extra building blocks, like streaming, safe retries, and fallbacks, so users get fast and reliable answers."; sub-title: "An LLM call is just one HTTP request."
  2 Streaming   Body, "Streaming over SSE / WebSockets / HTTP chunked": "Users expect words to appear as the model writes them, not after a 3-second pause. Three transports:" SSE, WebSockets, HTTP chunked transfer.
  3 Queue       Body, "Background jobs and queues for long agent runs": "Anything over ~10 seconds should not block an HTTP request. Push it to a queue ... and return a job_id. Client polls or subscribes via SSE/WebSocket for updates. This is the single biggest UX win for 'the agent took 4 minutes' tasks."
  4 Retries     Body, "Idempotency and resumability": "LLM calls fail. Networks drop. Users refresh. Always: Generate an idempotency key per request; reject duplicates. Store checkpoints of agent state so a resume replays only the failed steps. Use durable execution (Temporal/Restate) for anything longer than a minute."
  5 Tenants     Body, "Multi-tenant prompt and key management": "Per-tenant prompt overrides, per-tenant API keys, per-tenant rate limits, per-tenant tracing. ... store all of these in a tenant_config row, fetch at the edge of every request, attach to the trace. Never hard-code a tenant's prompt in their codebase."
  6 Fallbacks   Body, "Fallback chains across providers": "OpenAI 503s? Route to Anthropic. Anthropic 429s? Route to Together. With degraded prompts per provider ... a model gateway is essentially a fallback router plus cost tracking."
  7 Flags       Body, "Feature flags for prompts and models": "Treat every prompt and every model as a flag. Roll out 'use GPT-5 for premium users only' to 1%, then 10%, then 100%. Roll back instantly when evals regress."
  8 API rules   Body, "API design patterns for AI features": "Five rules that distinguish an AI API from a normal REST API:" cancel mid-flight, retry idempotently, return partial results, structured confidence, cost/latency budget in the request.
  9 Remember    The sub-title and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("client", "user", ("Client", "ক্লায়েন্ট"), 110, 162),
    node("api", "server", ("API", "API"), 380, 162),
    node("gateway", "balancer", ("Gateway", "গেটওয়ে"), 380, 162),
    node("flag", "lock", ("Feature flag", "ফিচার ফ্ল্যাগ"), 380, 162),
    node("queue", "queue", ("Queue", "কিউ"), 650, 75),
    node("p1", "service", ("OpenAI", "OpenAI"), 650, 75),
    node("llm", "model", ("Model", "মডেল"), 650, 162),
    node("p2", "service", ("Anthropic", "Anthropic"), 650, 162),
    node("store", "database", ("Database", "ডেটাবেস"), 650, 250),
    node("p3", "service", ("Together", "Together"), 650, 250),
]

METRICS = [
    ("Block limit", "ব্লক সীমা"),
    ("Rollout", "রোলআউট"),
    ("Budget", "বাজেট"),
]

CAPTION = (
    "An LLM call is just one HTTP request. A product around it needs the same plumbing any modern app needs, plus a few new building blocks.",
    "একটি LLM কল আসলে শুধু একটি HTTP রিকোয়েস্ট। এর চারপাশে একটি প্রোডাক্টে আধুনিক যেকোনো অ্যাপের মতো একই কাঠামো লাগে, সঙ্গে কয়েকটি নতুন অংশ।",
)

STEPS = [
    st(("Plumbing", "কাঠামো"),
       ("More than one model call", "শুধু একটি মডেল কল নয়"),
       [("An AI product is more than one model call. It needs extra building blocks, like streaming, safe retries, and fallbacks, so users get fast and reliable answers.",
         "একটি AI প্রোডাক্ট মানে শুধু একটি মডেল কল নয়। এতে স্ট্রিমিং, নিরাপদ রিট্রাই আর ফলব্যাকের মতো বাড়তি অংশ লাগে, যাতে ইউজার দ্রুত আর নির্ভরযোগ্য উত্তর পায়।"),
        ("An LLM call is just one HTTP request.",
         "একটি LLM কল হলো একটি HTTP রিকোয়েস্ট।")],
       [sh("client"), sh("api", "hot"), sh("llm", "hot", ("the LLM call", "LLM কল"))],
       [ln("client", "api", "to"), ln("api", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Streaming", "স্ট্রিমিং"),
       ("Stream the words", "শব্দ স্ট্রিম করুন"),
       [("Users expect words to appear as the model writes them, not after a 3-second pause. Three transports:",
         "ইউজাররা ৩ সেকেন্ডের বিরতির পরে নয়, মডেল যেভাবে লেখে সেভাবে শব্দ দেখতে চায়। তিনটি ট্রান্সপোর্ট:")],
       [sh("client", "hot", ("sees words now", "শব্দ সাথে সাথে")), sh("api", "hot"), sh("llm", "hot", ("writes words", "শব্দ লেখে"))],
       [ln("llm", "api", "to", state="hot"), ln("api", "client", "to", state="hot")],
       [None, None, None],
       changes=[("+", "SSE (Server-Sent Events): the simplest; it is plain HTTP, so it usually passes through proxies (some legacy proxies drop long-lived connections); one-way (server to client)",
                 "SSE (Server-Sent Events): সবচেয়ে সহজ; এটি সাধারণ HTTP, তাই সাধারণত প্রক্সির মধ্য দিয়ে কাজ করে (কিছু পুরনো প্রক্সি দীর্ঘ কানেকশন কেটে দেয়); একমুখী (সার্ভার থেকে ক্লায়েন্ট)"),
                ("+", "WebSockets: bidirectional; needed for voice and collaborative UIs; heavier handshake",
                 "ওয়েবসকেট: দ্বিমুখী; ভয়েস ও সহযোগী UI-এর জন্য দরকার; ভারী হ্যান্ডশেক"),
                ("+", "HTTP chunked transfer: a fallback for proxies that strip SSE headers",
                 "HTTP চাঙ্কড ট্রান্সফার: SSE হেডার স্ট্রিপ করে দেয় এমন প্রক্সির জন্য ফলব্যাক")]),

    st(("Queue", "কিউ"),
       ("Long jobs go to a queue", "লম্বা কাজ যায় কিউতে"),
       [("Anything over ~10 seconds should not block an HTTP request. Push it to a queue (BullMQ, Celery, Inngest, Cloud Tasks, Temporal) and return a <code>job_id</code>.",
         "~১০ সেকেন্ডের বেশি যেকোনো কিছুতে HTTP রিকোয়েস্ট ব্লক করা উচিত নয়। একটি কিউতে (BullMQ, Celery, Inngest, Cloud Tasks, Temporal) পুশ করুন এবং একটি <code>job_id</code> ফেরত দিন।"),
        ("The client polls or subscribes via SSE or WebSocket for updates.",
         "ক্লায়েন্ট পোল করে বা SSE/ওয়েবসকেট দিয়ে আপডেট সাবস্ক্রাইব করে।")],
       [sh("client", "hot"), sh("api", "hot"), sh("queue", "hot", ("long jobs wait here", "লম্বা কাজ এখানে")), sh("llm", "hot", ("runs the agent", "এজেন্ট চালায়"), y=250)],
       [ln("client", "api", "both", state="hot", label=("job_id", "job_id")), ln("api", "queue", "to", state="hot"), ln("queue", "llm", "to", state="hot")],
       [("over ~10 s", "~১০ সেকেন্ডের বেশি"), None, None],
       note=("insight",
             "This is the single biggest UX win for “the agent took 4 minutes” tasks.",
             "“এজেন্ট ৪ মিনিট নিয়েছে” ধরনের কাজের জন্য এটাই একমাত্র সবচেয়ে বড় UX জয়।")),

    st(("Retries", "রিট্রাই"),
       ("Retry safely, resume cheaply", "নিরাপদে রিট্রাই, সস্তায় রিজিউম"),
       [("LLM calls fail. Networks drop. Users refresh. Always generate an idempotency key per request, and reject duplicates.",
         "LLM কল ব্যর্থ হয়। নেটওয়ার্ক ড্রপ হয়। ইউজার রিফ্রেশ করে। সবসময়: প্রতিটি রিকোয়েস্টের জন্য একটি আইডেমপোটেন্সি কী তৈরি করুন; ডুপ্লিকেট প্রত্যাখ্যান করুন।"),
        ("Store checkpoints of agent state so a resume replays only the failed steps. Use durable execution (Temporal or Restate) for anything longer than a minute.",
         "এজেন্ট স্টেটের চেকপয়েন্ট সংরক্ষণ করুন, যাতে রিজিউম করলে শুধু ব্যর্থ ধাপগুলো রিপ্লে হয়। এক মিনিটের বেশি যেকোনো কিছুর জন্য ডিউরেবল এক্সিকিউশন (Temporal/Restate) ব্যবহার করুন।")],
       [sh("client", "hot", ("idempotency key", "আইডেমপোটেন্সি কী")), sh("api", "hot", ("rejects duplicates", "ডুপ্লিকেট ফেরায়")),
        sh("llm", "hot", ("the agent", "এজেন্ট"), y=75), sh("store", "hot", ("checkpoints", "চেকপয়েন্ট"))],
       [ln("client", "api", "to", state="hot"), ln("api", "llm", "to", state="hot"), ln("llm", "store", "to", state="hot")],
       [None, None, None]),

    st(("Tenants", "টেন্যান্ট"),
       ("One config row per tenant", "প্রতি টেন্যান্টের একটি কনফিগ রো"),
       [("Per-tenant prompt overrides, per-tenant API keys, per-tenant rate limits, per-tenant tracing. Store all of these in a <code>tenant_config</code> row, fetch it at the edge of every request, and attach it to the trace.",
         "প্রতি-টেন্যান্ট প্রম্পট ওভাররাইড, প্রতি-টেন্যান্ট API কী, প্রতি-টেন্যান্ট রেট লিমিট, প্রতি-টেন্যান্ট ট্রেসিং। এগুলো সব একটি <code>tenant_config</code> রো-তে রাখুন, প্রতিটি রিকোয়েস্টের এজে ফেচ করুন, ট্রেসে যুক্ত করুন।"),
        ("Never hard-code a tenant's prompt in their codebase.",
         "কখনোই একটি টেন্যান্টের প্রম্পট তাদের কোডবেসে হার্ড-কোড করবেন না।")],
       [sh("client", "hot", ("a tenant", "একজন টেন্যান্ট")), sh("api", "hot", ("fetches its config", "কনফিগ ফেচ করে")),
        sh("store", "hot", ("tenant_config", "tenant_config"), y=162), sh("llm", "hot", ("its own prompt", "নিজের প্রম্পট"), y=75)],
       [ln("client", "api", "to", state="hot"), ln("api", "store", "to", state="hot"), ln("api", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Fallbacks", "ফলব্যাক"),
       ("Fallback chains across providers", "প্রোভাইডার জুড়ে ফলব্যাক চেইন"),
       [("OpenAI 503s? Route to Anthropic. Anthropic 429s? Route to Together. With degraded prompts per provider (“you have no tool use; just answer”).",
         "OpenAI ৫০৩ দিলে? Anthropic-এ রাউট করুন। Anthropic ৪২৯ দিলে? Together-এ রাউট করুন। প্রতি প্রোভাইডারের জন্য ডিগ্রেডেড প্রম্পট সহ (“আপনার tool use নেই; শুধু উত্তর দিন”)।"),
        ("LiteLLM and Portkey do this out of the box; a model gateway is essentially a fallback router plus cost tracking.",
         "LiteLLM ও Portkey এটি বাক্সের বাইরে করে; একটি মডেল গেটওয়ে মূলত একটি ফলব্যাক রাউটার ও খরচ ট্র্যাকিং।")],
       [sh("client"), sh("gateway", "hot", ("tries in order", "পর পর চেষ্টা করে")), sh("p1", "warn", ("503", "৫০৩")),
        sh("p2", "warn", ("429", "৪২৯")), sh("p3", "hot", ("answers", "উত্তর দেয়"))],
       [ln("client", "gateway", "to"), ln("gateway", "p1", "to", state="warn"), ln("gateway", "p2", "to", state="warn"), ln("gateway", "p3", "to", state="hot")],
       [None, None, None]),

    st(("Flags", "ফ্ল্যাগ"),
       ("Feature flags for prompts and models", "প্রম্পট আর মডেলের ফিচার ফ্ল্যাগ"),
       [("Treat every prompt and every model as a flag. Roll out “use GPT-5 for premium users only” to 1%, then 10%, then 100%.",
         "প্রতিটি প্রম্পট ও প্রতিটি মডেলকে ফ্ল্যাগ হিসেবে দেখুন। “শুধু প্রিমিয়াম ইউজারদের জন্য GPT-5 ব্যবহার করুন” ১%, তারপর ১০%, তারপর ১০০%-এ রোল আউট করুন।"),
        ("Roll back instantly when evals regress. LaunchDarkly, Statsig, PostHog, or a simple DB column: pick one and use it for prompts.",
         "ইভ্যাল রিগ্রেস করলে তাৎক্ষণিকভাবে রোল ব্যাক করুন। LaunchDarkly, Statsig, PostHog বা একটি সাধারণ DB কলাম: একটি বেছে নিন এবং প্রম্পটের জন্য ব্যবহার করুন।")],
       [sh("client", "hot", ("some users", "কিছু ইউজার")), sh("flag", "hot", ("a switch per user", "ইউজারভেদে সুইচ")), sh("llm", "hot", ("the new prompt", "নতুন প্রম্পট"))],
       [ln("client", "flag", "to", state="hot"), ln("flag", "llm", "to", state="hot")],
       [None, ("1% → 10% → 100%", "১% → ১০% → ১০০%"), None]),

    st(("API rules", "API নিয়ম"),
       ("Rules for an AI API", "AI API-এর নিয়ম"),
       [("Five rules that distinguish an AI API from a normal REST API:",
         "পাঁচটি নিয়ম একটি AI API-কে সাধারণ REST API থেকে আলাদা করে:")],
       [sh("client", "hot"), sh("api", "hot"), sh("llm")],
       [ln("client", "api", "both", state="hot"), ln("api", "llm", "to")],
       [None, None, ("$0.05 and 8s", "$০.০৫ ও ৮s")],
       changes=[("+", "Cancel mid-flight: the client should be able to abort the request and stop the bill",
                 "মাঝপথে ক্যানসেল: ক্লায়েন্ট রিকোয়েস্ট অ্যাবর্ট করতে এবং বিল বন্ধ করতে পারবে"),
                ("+", "Retry idempotently: same request plus idempotency key gives the same response, with no double billing",
                 "আইডেমপোটেন্টলি রিট্রাই: একই রিকোয়েস্ট আর আইডেমপোটেন্সি কী মানে একই রেসপন্স, দ্বিগুণ বিলিং নয়"),
                ("+", "Return partial results: stream tokens, return intermediate tool states, never make the client wait until completion",
                 "পার্শিয়াল রেজাল্ট ফেরত দিন: টোকেন স্ট্রিম করুন, মধ্যবর্তী টুল স্টেট ফেরত দিন, ক্লায়েন্টকে কখনো সম্পূর্ণ হওয়া পর্যন্ত অপেক্ষা করাবেন না"),
                ("+", "Structured confidence: include a self-reported confidence, logprobs, or a “would I retry this?” field",
                 "স্ট্রাকচার্ড কনফিডেন্স: সেলফ-রিপোর্টেড কনফিডেন্স, লগপ্রব বা “আমি কি এটি রিট্রাই করব?” ফিল্ড রাখুন"),
                ("+", "Cost and latency budget in the request: let the client say “spend up to $0.05 and 8s”; the server respects it",
                 "রিকোয়েস্টে খরচ/ল্যাটেন্সি বাজেট: ক্লায়েন্টকে বলতে দিন “সর্বোচ্চ $০.০৫ ও ৮s খরচ করুন”; সার্ভার সেটি মানে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("An LLM call is just one HTTP request. A product around it needs the same plumbing any modern app needs, plus a few new building blocks.",
         "একটি LLM কল আসলে শুধু একটি HTTP রিকোয়েস্ট। এর চারপাশে একটি প্রোডাক্টে আধুনিক যেকোনো অ্যাপের মতো একই কাঠামো লাগে, সঙ্গে কয়েকটি নতুন অংশ।")],
       [sh("client"), sh("api"), sh("llm"), sh("store")],
       [ln("client", "api", "to"), ln("api", "llm", "to"), ln("api", "store", "to")],
       [None, None, None],
       points=[("Stream the answer so users see words as the model writes them, not after a pause.",
                "উত্তর স্ট্রিম করুন, যাতে ইউজার বিরতির পরে নয়, মডেল লেখার সাথে সাথে শব্দ দেখে।"),
               ("Push any task over ~10 seconds to a queue and return a <code>job_id</code>.",
                "~১০ সেকেন্ডের বেশি লাগে এমন কাজ কিউতে পাঠান আর একটি <code>job_id</code> ফেরত দিন।"),
               ("Use an idempotency key and checkpoints so retries do not double the work or the bill.",
                "আইডেমপোটেন্সি কী আর চেকপয়েন্ট ব্যবহার করুন, যাতে রিট্রাইয়ে কাজ বা বিল দ্বিগুণ না হয়।"),
               ("Never hard-code a tenant's prompt in their codebase; store it in a <code>tenant_config</code> row.",
                "টেন্যান্টের প্রম্পট কখনো তাদের কোডবেসে হার্ড-কোড করবেন না; <code>tenant_config</code> রো-তে রাখুন।"),
               ("Route to a backup provider when one fails; roll out new prompts to 1% first, and roll back instantly.",
                "একটি প্রোভাইডার ব্যর্থ হলে ব্যাকআপ প্রোভাইডারে রাউট করুন; নতুন প্রম্পট আগে ১%-এ রোল আউট করুন, আর দরকারে সাথে সাথে রোল ব্যাক করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
