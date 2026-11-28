"""Part 6 · 08 Error recovery, retries, and self-correction: retry, fall back, or reflect, and always bound the retries.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Layers    Sub-title: "Three escalating layers: retry the same call, fall back to a different one, or reflect on the failure and revise. Always bound retries."; Start here: "the key rule is to always bound retries, so a bad input cannot burn your budget."
  2 Retry     Body, "Layer 1: retry": "Transient failures (rate limit, network blip, server overloaded) are best handled with a short retry. Exponential backoff is the default: 1s, 2s, 4s, 8s, with jitter to avoid thundering-herd. Cap at 3–5 attempts; beyond that, the failure is not transient."; Jitter ("A small random extra wait, so many callers do not all retry at the same moment.").
  3 Fallback  Body, "Layer 2: fallback": "When the failure is not transient (the API is permanently down, the JSON schema is rejected because the model can't follow it, the function raised a domain-specific error), retrying the same call is pointless. Fall back to a different tool or model: use a smaller model with a simpler schema, use a different vendor, or skip the tool and let the model answer from its own knowledge."
  4 Reflect   Body, "Layer 3: reflect": "When the failure was caused by a reasoning error (the model called the right tool with the wrong arguments, or made a logical mistake), neither retry nor fallback fixes the root cause. Feed the failure back into the model and ask it to revise. Reflexion is the formal version of this."
  5 Bound     Danger callout: "Unbounded retry is a footgun. A poisoned input that always returns the same transient-looking error will burn your entire budget in a tight retry loop. Always set a hard cap on retries, a wall-clock timeout, and a circuit breaker that opens after N consecutive failures of the same type."
  6 Breaker   Body, "Circuit breakers": "After N consecutive failures of the same kind (say 5), the breaker opens: all calls for a timeout (say 60 seconds) fail fast with a "service unavailable" error, no retries. After the timeout, the breaker half-opens: one test call. If it succeeds, the breaker closes. If it fails, it opens again."
  7 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("agent", "model", ("Agent", "এজেন্ট"), 110, 162),
    node("svc", "server", ("Service", "সার্ভিস"), 650, 162),
    node("retry", "clock", ("Retry", "রিট্রাই"), 380, 75),
    node("fallback", "tool", ("Fallback", "ফলব্যাক"), 380, 250),
    node("reflect", "note", ("Reflect", "রিফ্লেক্ট"), 110, 75),
    node("breaker", "shield", ("Circuit breaker", "সার্কিট ব্রেকার"), 380, 162),
    node("budget", "chart", ("Budget", "বাজেট"), 650, 75),
]

METRICS = [
    ("Backoff", "ব্যাকঅফ"),
    ("Attempts", "চেষ্টা"),
    ("Opens after", "খোলে"),
    ("Open for", "খোলা থাকে"),
]

CAPTION = (
    "When an agent's call to a service fails, there are three layers of response, and every one of them is bounded.",
    "এজেন্টের কল ব্যর্থ হলে সাড়া দেওয়ার তিনটি স্তর আছে, আর প্রতিটিরই একটি সীমা থাকে।",
)

BACKOFF = ("1s, 2s, 4s, 8s", "১ সে, ২ সে, ৪ সে, ৮ সে")

STEPS = [
    st(("Layers", "স্তর"),
       ("Three layers of response", "সাড়া দেওয়ার তিনটি স্তর"),
       [("When an agent's call fails, there are three layers of response: retry the same call, fall back to a different one, or reflect on the failure and revise.",
         "এজেন্টের কল ব্যর্থ হলে সাড়া দেওয়ার তিনটি স্তর: একই কল আবার করা, অন্য একটা উপায়ে যাওয়া, অথবা ব্যর্থতাটা নিয়ে ভেবে ঠিক করে নেওয়া।"),
        ("The key rule is to always bound retries, so a bad input cannot burn your budget.",
         "মূল নিয়ম হলো সবসময় রিট্রাইয়ের সীমা বেঁধে দেওয়া, যাতে একটি খারাপ ইনপুট আপনার বাজেট শেষ করতে না পারে।")],
       [sh("agent", "hot"), sh("svc", "warn", ("call fails", "কল ব্যর্থ")), sh("retry", "hot", ("same call again", "একই কল আবার")),
        sh("fallback", "hot", ("a different one", "অন্য একটি")), sh("reflect", "hot", ("revise", "শুধরে নেওয়া"))],
       [ln("agent", "svc", "to", state="warn"), ln("agent", "retry", "to", state="hot"), ln("agent", "fallback", "to", state="hot"), ln("agent", "reflect", "to", state="hot")],
       [None, None, None, None]),

    st(("Retry", "রিট্রাই"),
       ("Layer 1: retry transient failures", "স্তর ১: ক্ষণস্থায়ী ব্যর্থতায় রিট্রাই"),
       [("Transient failures, such as a rate limit, a network blip or an overloaded server, are best handled with a short retry. Exponential backoff is the default: wait 1s, 2s, 4s, 8s, with a little random jitter so many callers do not retry at the same moment.",
         "ট্রানজিয়েন্ট ব্যর্থতা, যেমন রেট লিমিট, নেটওয়ার্কের ক্ষণিক সমস্যা বা ওভারলোডেড সার্ভার, ছোট রিট্রাইয়ে সবচেয়ে ভালো সামলানো যায়। ডিফল্ট হলো এক্সপোনেনশিয়াল ব্যাকঅফ: ১ সেকেন্ড, ২, ৪, ৮ অপেক্ষা, সঙ্গে সামান্য এলোমেলো জিটার, যাতে অনেক কলার একই মুহূর্তে আবার চেষ্টা না করে।"),
        ("Cap it at 3–5 attempts. Beyond that, the failure is not transient.",
         "চেষ্টা ৩–৫ বারে সীমিত রাখুন। এর পরও ব্যর্থ হলে সেটা ক্ষণস্থায়ী নয়।")],
       [sh("agent", "hot"), sh("retry", "hot", ("backoff and jitter", "ব্যাকঅফ আর জিটার")), sh("svc", "warn", ("transient failure", "ক্ষণস্থায়ী ব্যর্থতা"))],
       [ln("agent", "retry", "to", state="hot"), ln("retry", "svc", "to", state="hot")],
       [BACKOFF, ("3–5", "৩–৫"), None, None]),

    st(("Fallback", "ফলব্যাক"),
       ("Layer 2: fall back", "স্তর ২: ফলব্যাক"),
       [("When the failure is not transient, retrying the same call is pointless. That is the case when the API is permanently down, the JSON schema is rejected because the model cannot follow it, or the function raised a domain-specific error.",
         "ব্যর্থতা ক্ষণস্থায়ী না হলে একই কল আবার করা অর্থহীন। যেমন, API স্থায়ীভাবে বন্ধ, JSON স্কিমা মডেল মানতে পারছে না বলে বাতিল, অথবা ফাংশন কোনো ডোমেইন-নির্দিষ্ট ত্রুটি তুলেছে।"),
        ("Fall back to a different tool or model: a smaller model with a simpler schema, a different vendor, or no tool at all, letting the model answer from its own knowledge.",
         "অন্য টুল বা মডেলে সরে যান: সহজ স্কিমাসহ ছোট মডেল, অন্য ভেন্ডর, অথবা টুল ছেড়ে দিয়ে মডেলকে নিজের জ্ঞান থেকে উত্তর দিতে দেওয়া।")],
       [sh("agent", "hot"), sh("svc", "warn", ("not transient", "ক্ষণস্থায়ী নয়")), sh("fallback", "hot", ("a different tool or model", "অন্য টুল বা মডেল"))],
       [ln("agent", "svc", "to", state="warn"), ln("agent", "fallback", "to", state="hot")],
       [None, None, None, None]),

    st(("Reflect", "রিফ্লেক্ট"),
       ("Layer 3: reflect", "স্তর ৩: রিফ্লেক্ট"),
       [("When the failure came from a reasoning error, such as the right tool called with the wrong arguments, or a logical mistake, neither retry nor fallback fixes the root cause.",
         "ব্যর্থতা যুক্তির ভুল থেকে এলে, যেমন সঠিক টুলে ভুল আর্গুমেন্ট দেওয়া বা যুক্তিগত ভুল, রিট্রাই বা ফলব্যাক কোনোটিই মূল কারণ ঠিক করে না।"),
        ("Feed the failure back into the model and ask it to revise. Reflexion is the formal version of this.",
         "ব্যর্থতাটা মডেলকে ফেরত দিন আর শুধরে নিতে বলুন। Reflexion এর আনুষ্ঠানিক রূপ।")],
       [sh("agent", "hot", ("revises", "শুধরে নেয়")), sh("reflect", "hot", ("failure fed back", "ব্যর্থতা ফেরত যায়")), sh("svc", "warn", ("wrong arguments", "ভুল আর্গুমেন্ট"))],
       [ln("agent", "svc", "to", state="warn"), ln("svc", "reflect", "to", state="warn"), ln("reflect", "agent", "to", state="hot")],
       [None, None, None, None]),

    st(("Bound", "সীমা"),
       ("Always bound retries", "রিট্রাইয়ের সীমা বাঁধুন"),
       [("Unbounded retry is a footgun. A poisoned input that always returns the same transient-looking error will burn your entire budget in a tight retry loop.",
         "সীমাহীন রিট্রাই একটি ফুটগান। যে খারাপ ইনপুট সবসময় একই ক্ষণস্থায়ী-দেখতে ত্রুটি ফেরত দেয়, সে একটি টাইট রিট্রাই লুপে আপনার পুরো বাজেট পুড়িয়ে ফেলবে।")],
       [sh("agent", "hot"), sh("retry", "warn", ("tight loop", "টাইট লুপ")), sh("svc", "warn", ("same error", "একই ত্রুটি")), sh("budget", "warn", ("burned", "পুড়ে যায়"))],
       [ln("agent", "retry", "to", state="warn"), ln("retry", "svc", "to", state="warn"), ln("retry", "budget", "to", state="warn")],
       [None, None, None, None],
       changes=[("+", "A hard cap on retries", "রিট্রাইয়ের কড়া সীমা"),
                ("+", "A wall-clock timeout", "ওয়াল-ক্লক টাইমআউট"),
                ("+", "A circuit breaker that opens after N consecutive failures of the same type", "একই ধরনের পরপর N বার ব্যর্থতার পর খুলে যায়, এমন সার্কিট ব্রেকার")]),

    st(("Breaker", "ব্রেকার"),
       ("The circuit breaker", "সার্কিট ব্রেকার"),
       [("A circuit breaker protects against a service that is failing in a way that looks transient but is not. After N consecutive failures of the same kind (say 5), it opens: for a timeout (say 60 seconds) every call fails fast with “service unavailable”, with no retries.",
         "সার্কিট ব্রেকার এমন সার্ভিস থেকে বাঁচায়, যে ক্ষণস্থায়ী দেখালেও আসলে তা নয়। একই ধরনের পরপর N বার (যেমন ৫) ব্যর্থ হলে সেটি খুলে যায়: একটি নির্দিষ্ট সময় (যেমন ৬০ সেকেন্ড) প্রতিটি কল “service unavailable” ত্রুটিতে সঙ্গে সঙ্গে ব্যর্থ হয়, কোনো রিট্রাই ছাড়াই।"),
        ("After the timeout it half-opens and lets one test call through. If that call succeeds, the breaker closes. If it fails, it opens again.",
         "সময় পেরোলে এটি অর্ধেক খোলে আর একটি পরীক্ষামূলক কল যেতে দেয়। কলটি সফল হলে ব্রেকার বন্ধ হয়। ব্যর্থ হলে এটি আবার খুলে যায়।")],
       [sh("agent", "hot"), sh("breaker", "warn", ("open: fails fast", "খোলা: সঙ্গে সঙ্গে ব্যর্থ")), sh("svc", "dim", ("not called", "ডাকা হয় না"))],
       [ln("agent", "breaker", "to", state="hot"), ln("breaker", "svc", "to", state="dim")],
       [None, None, ("N failures (say 5)", "N বার (যেমন ৫)"), ("say 60 s", "যেমন ৬০ সে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Match the response to the failure: retry what is transient, fall back when it is not, and reflect when the model reasoned badly.",
         "ব্যর্থতার ধরন দেখে সাড়া দিন: ক্ষণস্থায়ী হলে রিট্রাই, না হলে ফলব্যাক, আর মডেল ভুল যুক্তি করলে রিফ্লেক্ট।")],
       [sh("agent"), sh("svc"), sh("retry"), sh("fallback"), sh("reflect")],
       [ln("agent", "svc", "to"), ln("agent", "retry", "to"), ln("agent", "fallback", "to"), ln("agent", "reflect", "to")],
       [None, None, None, None],
       points=[("Retry only transient failures, and cap attempts at 3–5.",
                "শুধু ট্রানজিয়েন্ট ব্যর্থতায় রিট্রাই করুন, আর চেষ্টা ৩–৫ বারে সীমিত রাখুন।"),
               ("Use a fallback when the failure is not transient.",
                "ব্যর্থতা ট্রানজিয়েন্ট না হলে ফলব্যাক ব্যবহার করুন।"),
               ("Use reflection when the model made a reasoning error, like wrong arguments.",
                "মডেল যুক্তিতে ভুল করলে, যেমন ভুল আর্গুমেন্ট দিলে, রিফ্লেক্ট ব্যবহার করুন।"),
               ("Always set a retry cap, a wall-clock timeout, and a circuit breaker.",
                "সবসময় রিট্রাইয়ের সীমা, ওয়াল-ক্লক টাইমআউট আর সার্কিট ব্রেকার রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
