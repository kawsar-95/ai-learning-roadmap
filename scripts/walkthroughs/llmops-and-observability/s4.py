"""Part 9 · 01 LLMOps & observability: how to watch an LLM app that can return 200 and still be wrong.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Problem   Start here: "A normal app shows a red error when it breaks. An AI app can return 200 (success) and still give wrong or costly answers. LLMOps is the set of habits and tools that watch for this."
  2 Trace     Body, "Tracing": "An LLM trace is a tree of spans: the user request, the system prompt assembly, the LLM call, every tool invocation, the result."; Start here, Span: "One step inside a trace, such as a single model call or a single tool call."
  3 Record    Body, "Token, cost, and latency tracking": "Every request must record: input tokens, output tokens, model, cost ..., latency ..., and cache hit. Tag with user_id, feature, experiment. This data is the substrate for every other LLMOps question".
  4 Version   Body, "Prompt and agent versioning": "Prompts are code ... store in git, version them, review them via PR, deploy via CI. Each prompt version gets a stable ID; every trace carries the prompt ID."
  5 A/B test  Body, "A/B testing prompts and models in production": "Route traffic between two prompt versions (or two models) by user_id hash. Measure: cost, latency, evals run on the output, user feedback. Stop the experiment when one variant wins on the metric you chose".
  6 Replay    Body, "Replay and debugging": "pull the trace, see every prompt and every model reply, identify the failure, and replay the exact request against a different model or prompt to verify the fix. Langfuse and LangSmith let you open a logged call in a playground and re-run it with another model or prompt."
  7 Drift     Body, "Drift detection": "When a vendor's model alias starts pointing to a newer snapshot ..., your outputs can drift in ways your offline evals won't catch. Pin dated model IDs. The fix: run a small fraction of production traffic (1–5%) through both the old and new model, compare evals, alert on delta. Tools such as Braintrust (online scoring with alerts) and Arize Phoenix (embedding drift) cover parts of this."
  8 Feedback  Body, "Feedback loops": "Capture thumbs-up / thumbs-down ... and feed the failures into your eval dataset. After three months you'll have a thousand real failures that's worth more than ten thousand synthetic ones."
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ইউজার"), 110, 162),
    node("git", "storage", ("Git", "Git"), 110, 162),
    node("app", "server", ("LLM app", "LLM অ্যাপ"), 380, 162),
    node("router", "balancer", ("Router", "রাউটার"), 380, 162),
    node("model", "model", ("Model", "মডেল"), 650, 162),
    node("store", "database", ("Trace store", "ট্রেস স্টোর"), 650, 162),
    node("evals", "chart", ("Evals", "ইভ্যাল"), 650, 162),
    node("dataset", "database", ("Eval set", "ইভ্যাল সেট"), 650, 162),
    node("tool", "tool", ("Tool", "টুল"), 650, 250),
    node("other", "model", ("Other model", "অন্য মডেল"), 650, 250),
]

METRICS = [
    ("Status", "স্ট্যাটাস"),
    ("Cost", "খরচ"),
    ("Latency", "ল্যাটেন্সি"),
    ("Traffic sampled", "নমুনা ট্র্যাফিক"),
]

CAPTION = (
    "LLMOps: running and watching an LLM app in real use, to see if answers are right, cheap enough, and safe.",
    "LLMOps: বাস্তব ব্যবহারে একটি LLM অ্যাপ চালানো আর নজরে রাখা, দেখা উত্তর ঠিক, সস্তা আর নিরাপদ কি না।",
)

STEPS = [
    st(("Problem", "সমস্যা"),
       ("A 200 that is still wrong", "২০০ ফেরত দিয়েও ভুল"),
       [("A normal app shows a red error when it breaks. An AI app can return 200 (success) and still give wrong or costly answers.",
         "সাধারণ অ্যাপ ভেঙে গেলে লাল এরর দেখায়। কিন্তু AI অ্যাপ ২০০ (সফল) ফেরত দিয়েও ভুল বা ব্যয়বহুল উত্তর দিতে পারে।"),
        ("LLMOps is the set of habits and tools that watch for this.",
         "LLMOps হলো সেটা নজরে রাখার অভ্যাস আর টুলের সমষ্টি।")],
       [sh("user"), sh("app", "hot"), sh("model", "warn", ("wrong or costly", "ভুল বা ব্যয়বহুল"))],
       [ln("user", "app", "to"), ln("app", "model", "to")],
       [("200 (success)", "২০০ (সফল)"), None, None, None]),

    st(("Trace", "ট্রেস"),
       ("A trace is a tree of spans", "ট্রেস হলো স্প্যানের গাছ"),
       [("An LLM trace is a tree of spans: the user request, the system prompt assembly, the LLM call, every tool invocation, the result.",
         "একটি LLM ট্রেস হলো স্প্যানের গাছ: ইউজার রিকোয়েস্ট, সিস্টেম প্রম্পট তৈরি, LLM কল, প্রতিটি টুল ব্যবহার আর ফলাফল।"),
        ("A span is one step inside a trace, such as a single model call or a single tool call.",
         "স্প্যান হলো ট্রেসের ভেতরের একটি ধাপ, যেমন একটি মডেল কল বা একটি টুল কল।")],
       [sh("user", "hot", ("request", "রিকোয়েস্ট")), sh("app", "hot", ("prompt assembly", "প্রম্পট তৈরি")),
        sh("model", "hot", ("LLM call", "LLM কল")), sh("tool", "hot", ("tool call", "টুল কল"))],
       [ln("user", "app", "to", state="hot"), ln("app", "model", "to", state="hot"), ln("app", "tool", "to", state="hot")],
       [None, None, None, None]),

    st(("Record", "রেকর্ড"),
       ("Record every request", "প্রতিটি রিকোয়েস্ট রেকর্ড করুন"),
       [("Every request must record: input tokens, output tokens, model, cost (computed from the vendor's pricing), latency (time to first token, or TTFT, and total), and cache hit.",
         "প্রতিটি রিকোয়েস্ট রেকর্ড করুক: ইনপুট টোকেন, আউটপুট টোকেন, মডেল, খরচ (ভেন্ডরের প্রাইসিং থেকে হিসাব), ল্যাটেন্সি (TTFT, মোট) ও ক্যাশ হিট।")],
       [sh("app"), sh("store", "hot", ("tokens, cost, time", "টোকেন, খরচ, সময়"))],
       [ln("app", "store", "to", state="hot")],
       [None, ("from pricing", "প্রাইসিং থেকে"), ("TTFT and total", "TTFT আর মোট"), None],
       note=("insight",
             "Tag each request with <code>user_id</code>, <code>feature</code>, and <code>experiment</code>. This data is the substrate for every other LLMOps question.",
             "প্রতিটি রিকোয়েস্ট <code>user_id</code>, <code>feature</code> আর <code>experiment</code> দিয়ে ট্যাগ করুন। এই ডেটাই অন্য প্রতিটি LLMOps প্রশ্নের ভিত্তি।")),

    st(("Version", "ভার্সন"),
       ("Prompts are code", "প্রম্পট মানে কোড"),
       [("Treat prompts like code: store them in git, version them, review them via PR, and deploy them via CI.",
         "প্রম্পট হলো কোড। কোডের মতোই git-এ রাখুন, ভার্সন করুন, PR-এ রিভিউ করুন, CI দিয়ে ডিপ্লয় করুন।"),
        ("Each prompt version gets a stable ID, and every trace carries the prompt ID. When something breaks, you can answer “what prompt version were users on?” instantly.",
         "প্রতিটি প্রম্পট ভার্সনের একটি স্থিত ID থাকবে; প্রতিটি ট্রেস সেই প্রম্পট ID বহন করবে। কিছু ভেঙে গেলে “ইউজাররা কোন প্রম্পট ভার্সনে ছিল?” প্রশ্নের উত্তর সঙ্গে সঙ্গে দেওয়া যায়।")],
       [sh("git", "hot", ("PR review", "PR রিভিউ")), sh("app", "hot", ("CI deploy", "CI ডিপ্লয়")),
        sh("store", "hot", ("prompt ID on trace", "ট্রেসে প্রম্পট ID"))],
       [ln("git", "app", "to", state="hot"), ln("app", "store", "to", state="hot")],
       [None, None, None, None]),

    st(("A/B test", "A/B টেস্ট"),
       ("A/B test by user_id hash", "user_id হ্যাশ দিয়ে A/B টেস্ট"),
       [("Route traffic between two prompt versions (or two models) by user_id hash. Measure cost, latency, evals run on the output, and user feedback.",
         "user_id হ্যাশ দিয়ে দুটি প্রম্পট ভার্সন (বা দুটি মডেল)-এর মধ্যে ট্র্যাফিক রাউট করুন। খরচ, ল্যাটেন্সি, আউটপুটে চালানো ইভ্যাল আর ইউজারের প্রতিক্রিয়া মাপুন।"),
        ("Stop the experiment when one variant wins on the metric you chose, not after one bad afternoon.",
         "নির্বাচিত মেট্রিকে একটি ভ্যারিয়েন্ট জিতলে পরীক্ষা বন্ধ করুন, একটা খারাপ বিকেল দেখে নয়।")],
       [sh("user"), sh("router", "hot", ("by user_id hash", "user_id হ্যাশে")),
        sh("model", "hot", ("version A", "ভার্সন A"), y=75), sh("other", "hot", ("version B", "ভার্সন B"))],
       [ln("user", "router", "to"), ln("router", "model", "to", state="hot"), ln("router", "other", "to", state="hot")],
       [None, None, None, None]),

    st(("Replay", "রিপ্লে"),
       ("Replay and debugging", "রিপ্লে আর ডিবাগিং"),
       [("When a user complains, pull the trace, see every prompt and every model reply, and identify the failure.",
         "ইউজার অভিযোগ করলে ট্রেস টেনে এনে প্রতিটি প্রম্পট ও প্রতিটি মডেল উত্তর দেখুন, আর ব্যর্থতা চিহ্নিত করুন।"),
        ("Then replay the exact request against a different model or prompt to verify the fix. Langfuse and LangSmith let you open a logged call in a playground and re-run it with another model or prompt.",
         "তারপর সেই হুবহু রিকোয়েস্ট ভিন্ন মডেল বা প্রম্পটে রিপ্লে করে ফিক্স যাচাই করুন। Langfuse আর LangSmith-এ লগ করা কল প্লেগ্রাউন্ডে খুলে অন্য মডেল বা প্রম্পট দিয়ে আবার চালানো যায়।")],
       [sh("user", "warn", ("complains", "অভিযোগ করে")), sh("store", "hot", ("pull the trace", "ট্রেস টানুন"), x=380),
        sh("other", "hot", ("same request", "একই রিকোয়েস্ট"), y=162)],
       [ln("user", "store", "to", state="hot"), ln("store", "other", "to", state="hot")],
       [None, None, None, None]),

    st(("Drift", "ড্রিফট"),
       ("Drift detection", "ড্রিফট ডিটেকশন"),
       [("When a vendor's model alias starts pointing to a newer snapshot (for example an unpinned alias that moves to a new dated version), your outputs can drift in ways your offline evals won't catch. Pin dated model IDs.",
         "ভেন্ডরের কোনো মডেল অ্যালিয়াস নতুন স্ন্যাপশটের দিকে ঘুরে গেলে (যেমন পিন না করা অ্যালিয়াস নতুন ডেটেড ভার্সনে চলে যায়), আপনার আউটপুট এমনভাবে ড্রিফট করতে পারে যা অফলাইন ইভ্যাল ধরতে পারে না। ডেটেড মডেল ID পিন করুন।"),
        ("The fix: run a small fraction of production traffic (1–5%) through both the old and the new model, compare evals, and alert on delta. Tools such as Braintrust (online scoring with alerts) and Arize Phoenix (embedding drift) cover parts of this.",
         "সমাধান: প্রোডাকশন ট্র্যাফিকের একটি ছোট অংশ (১–৫%) পুরোনো ও নতুন দুই মডেলের মধ্য দিয়েই চালান, ইভ্যাল তুলনা করুন, আর পার্থক্য হলে সতর্কতা দিন। Braintrust (সতর্কতাসহ অনলাইন স্কোরিং) আর Arize Phoenix (এমবেডিং ড্রিফট) এর কিছু অংশ কভার করে।")],
       [sh("user", "hot", ("live traffic", "লাইভ ট্র্যাফিক")), sh("model", "hot", ("old", "পুরোনো"), x=380, y=75),
        sh("other", "hot", ("new", "নতুন"), x=380), sh("evals", "hot", ("compare, then alert", "তুলনা, তারপর সতর্ক"))],
       [ln("user", "model", "to", state="hot"), ln("user", "other", "to", state="hot"),
        ln("model", "evals", "to", state="hot"), ln("other", "evals", "to", state="hot")],
       [None, None, None, ("1–5%", "১–৫%")]),

    st(("Feedback", "ফিডব্যাক"),
       ("Feedback loops", "ফিডব্যাক লুপ"),
       [("Capture thumbs-up and thumbs-down (or richer signals) and feed the failures into your eval dataset.",
         "থাম্বস-আপ / থাম্বস-ডাউন (বা সমৃদ্ধ সংকেত) ক্যাপচার করুন এবং ব্যর্থতাগুলো আপনার ইভ্যাল ডেটাসেটে ফিড করুন।")],
       [sh("user", "hot", ("thumbs-down", "থাম্বস-ডাউন")), sh("store", "hot", ("the exact trace", "সেই ট্রেস"), x=380),
        sh("dataset", "hot", ("real failures", "বাস্তব ব্যর্থতা"))],
       [ln("user", "store", "to", state="hot"), ln("store", "dataset", "to", state="hot")],
       [None, None, None, None],
       note=("insight",
             "After three months you'll have a thousand real failures, worth more than ten thousand synthetic ones.",
             "তিন মাস পর আপনার কাছে এক হাজার বাস্তব ব্যর্থতা থাকবে, যা দশ হাজার সিনথেটিকের চেয়ে বেশি মূল্যবান।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("LLMOps is the set of habits and tools that watch for wrong or costly answers, even when the request returns 200.",
         "LLMOps হলো সেই অভ্যাস আর টুলের সমষ্টি, যা রিকোয়েস্ট ২০০ ফেরত দিলেও ভুল বা ব্যয়বহুল উত্তর নজরে রাখে।")],
       [sh("git"), sh("app"), sh("store"), sh("dataset", None, None, None, 380, 250)],
       [ln("git", "app", "to"), ln("app", "store", "to"), ln("store", "dataset", "to")],
       [None, None, None, None],
       points=[("Record tokens, cost, latency, and cache hit (a reused saved result) for every request; tag with user_id, feature, and experiment.",
                "প্রতিটি রিকোয়েস্টে টোকেন, খরচ, ল্যাটেন্সি আর ক্যাশ হিট (আগে জমানো ফল আবার কাজে লাগা) রেকর্ড করুন; user_id, feature, experiment দিয়ে ট্যাগ করুন।"),
               ("Treat prompts like code: keep them in git, give each version an ID, and put that ID on every trace.",
                "প্রম্পটকে কোডের মতো দেখুন: git-এ রাখুন, প্রতি ভার্সনে ID দিন, আর প্রতিটি ট্রেসে সেই ID রাখুন।"),
               ("To catch drift, send 1–5% of live traffic through old and new models, compare evals, and alert when they differ.",
                "ড্রিফট ধরতে লাইভ ট্র্যাফিকের ১–৫% পুরোনো ও নতুন দুই মডেলে চালান, ইভ্যাল তুলনা করুন, আর পার্থক্য হলে সতর্কতা দিন।"),
               ("Save thumbs-down failures into your eval set. Real failures are worth more than synthetic, made-up ones.",
                "থাম্বস-ডাউন পাওয়া ব্যর্থতা ইভ্যাল সেটে জমান। সিনথেটিক, মানে বানানো ব্যর্থতার চেয়ে বাস্তব ব্যর্থতার মূল্য বেশি।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
