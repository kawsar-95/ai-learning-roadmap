"""Part 15 · ch10 AI Engineering Architecture and User Feedback: building the platform.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Start      "The simplest possible AI application is just a query sent to a model API and a response returned to the user. It has no context, no safety checks, and no optimization." "A real AI platform grows from a single model call, one layer at a time."
  2 Context    "Feeding the model the information it needs for a query, through retrieval (finding relevant data) and tool use (web search, SQL, APIs)."
  3 Guardrails "Input guardrails stop bad inputs; output guardrails catch bad answers after generation." Warning: "Guardrails add latency, and a system can be too safe. Track wrong refusals of safe requests."
  4 Router     "A small, fast part that decides where each query goes: a cheap model, a specialized model, or a human."
  5 Gateway    "One unified interface between an application and all the models it uses. It centralizes access control, usage monitoring, cost limits, and fallback."
  6 Exact      "Reusing a stored result only when the query is identical." Risk: "Exact caching can serve one user's personalized response to someone else."
  7 Semantic   "Reusing a stored answer when a query is only similar. It compares embeddings ... against a similarity threshold." "A bad semantic threshold returns a plausible wrong answer."
  8 Write      "An action that changes something in the real world, such as sending an email, placing an order, or updating a database." "Write actions make a system more capable but riskier."
  9 Remember   "Layers are added one at a time: context, guardrails, router and gateway, cache, then agent patterns. Each solves a real problem."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("Query", "query"), 80, 162),
    node("model", "model", ("Model", "মডেল"), 640, 162),
    node("ctx", "tool", ("Context", "কনটেক্সট"), 380, 70),
    node("guard", "shield", ("Guardrails", "গার্ডরেইল"), 380, 162),
    node("router", "balancer", ("Router", "রাউটার"), 330, 162),
    node("spec", "model", ("Specialized model", "বিশেষায়িত মডেল"), 600, 162),
    node("human", "user", ("Human", "মানুষ"), 600, 255),
    node("gateway", "service", ("Gateway", "গেটওয়ে"), 380, 162),
    node("ecache", "cache", ("Exact cache", "এক্স্যাক্ট ক্যাশ"), 380, 162),
    node("scache", "cache", ("Semantic cache", "সেমান্টিক ক্যাশ"), 380, 162),
    node("action", "tool", ("Write action", "রাইট অ্যাকশন"), 620, 162),
]

METRICS = [
    ("Layers", "স্তর"),
    ("Latency", "ল্যাটেন্সি"),
    ("Risk", "ঝুঁকি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Start", "শুরু"),
       ("One model call", "একটিমাত্র মডেল কল"),
       [("The simplest AI application is just a query sent to a model API and a response returned to the user. It has no context, no safety checks, and no optimization.",
         "সবচেয়ে সরল AI অ্যাপ্লিকেশন হলো মডেল API-তে একটি query পাঠানো আর ইউজারকে উত্তর ফেরত দেওয়া। এতে কনটেক্সট নেই, নিরাপত্তা চেক নেই, অপ্টিমাইজেশনও নেই।"),
        ("A real AI platform grows from this, one layer at a time.",
         "একটি আসল AI প্ল্যাটফর্ম এখান থেকে একে একে স্তর যোগ করে বড় হয়।")],
       [sh("user", "hot"), sh("model", "hot")],
       [ln("user", "model", "to", state="hot")],
       [None, None, None]),

    st(("Context", "কনটেক্সট"),
       ("Give the model what it needs", "মডেলকে দরকারি তথ্য দিন"),
       [("Context construction feeds the model the information it needs for a query.",
         "কনটেক্সট কনস্ট্রাকশন মডেলকে প্রশ্নের জন্য দরকারি তথ্য দেয়।"),
        ("It uses retrieval (finding relevant data) and tool use (web search, SQL, APIs).",
         "এটা retrieval (দরকারি ডেটা খোঁজা) আর tool use (web search, SQL, API) ব্যবহার করে।")],
       [sh("user", "dim"), sh("ctx", "hot", ("retrieval and tool use", "retrieval আর tool use")), sh("model", "hot")],
       [ln("user", "ctx", "to", state="hot"), ln("ctx", "model", "to", state="hot")],
       [None, None, None]),

    st(("Guardrails", "গার্ডরেইল"),
       ("Guardrails protect the system and the user", "গার্ডরেইল সিস্টেম আর ইউজারকে বাঁচায়"),
       [("Input guardrails stop bad inputs. Output guardrails catch bad answers after generation.",
         "input guardrail খারাপ ইনপুট ঠেকায়। output guardrail তৈরি হওয়ার পর খারাপ উত্তর ধরে।"),
        ("Guardrails add latency, and a system can be too safe.",
         "গার্ডরেইল ল্যাটেন্সি বাড়ায়, আর সিস্টেম অতিরিক্ত নিরাপদও হয়ে যেতে পারে।")],
       [sh("user", "dim"), sh("guard", "hot"), sh("model", "dim")],
       [ln("user", "guard", "to", state="hot"), ln("guard", "model", "to", state="hot")],
       [None, ("adds latency", "ল্যাটেন্সি বাড়ায়"), None],
       note=("warn", "Track wrong refusals of safe requests, not only security failures.",
             "শুধু সিকিউরিটি ব্যর্থতা নয়, নিরাপদ অনুরোধ ভুল করে ফিরিয়ে দেওয়াও মাপুন।")),

    st(("Router", "রাউটার"),
       ("A router decides where a query goes", "রাউটার ঠিক করে query কোথায় যাবে"),
       [("A router is a small, fast part that decides where each query goes.",
         "রাউটার ছোট, দ্রুত একটি অংশ, যে ঠিক করে প্রতিটি query কোথায় যাবে।"),
        ("It can send a query to a cheap model, a specialized model, or a human.",
         "সে query পাঠাতে পারে সস্তা মডেলে, বিশেষায়িত মডেলে, নয়তো মানুষের কাছে।")],
       [sh("user", "dim"), sh("router", "hot", ("small and fast", "ছোট আর দ্রুত")),
        sh("model", "hot", ("a cheap model", "সস্তা মডেল"), x=600, y=70), sh("spec", "hot"), sh("human", "hot")],
       [ln("user", "router", "to", state="hot"), ln("router", "model", "to", state="hot"),
        ln("router", "spec", "to", state="hot"), ln("router", "human", "to", state="hot")],
       [None, None, None]),

    st(("Gateway", "গেটওয়ে"),
       ("One gateway for all the models", "সব মডেলের জন্য একটি গেটওয়ে"),
       [("A gateway is one unified interface between an application and all the models it uses.",
         "গেটওয়ে হলো অ্যাপ্লিকেশন আর তার ব্যবহার করা সব মডেলের মাঝের একটিমাত্র ইন্টারফেস।"),
        ("It centralizes access control, usage monitoring, cost limits, and fallback.",
         "এটা access control, ব্যবহার মনিটরিং, খরচের সীমা আর fallback এক জায়গায় রাখে।")],
       [sh("user", "dim"), sh("gateway", "hot"), sh("model", "hot", ("all the models", "সব মডেল"))],
       [ln("user", "gateway", "to", state="hot"), ln("gateway", "model", "to", state="hot")],
       [None, None, None]),

    st(("Exact cache", "এক্স্যাক্ট ক্যাশ"),
       ("Exact caching: only an identical query", "এক্স্যাক্ট ক্যাশিং: শুধু হুবহু এক query"),
       [("Exact caching reuses a stored result only when the query is identical.",
         "exact caching query হুবহু এক হলেই আগে জমানো ফল আবার ব্যবহার করে।"),
        ("Its risk: it can serve one user's personalized response to someone else.",
         "এর ঝুঁকি: একজনের জন্য বানানো উত্তর অন্যজনকে দিয়ে ফেলতে পারে।")],
       [sh("user", "dim"), sh("ecache", "warn", ("identical query", "হুবহু এক query")), sh("model", "dim")],
       [ln("user", "ecache", "to", state="hot"), ln("ecache", "model", "to", state="dim")],
       [None, None, ("personalized reply", "ব্যক্তিগত উত্তর")]),

    st(("Semantic", "সেমান্টিক"),
       ("Semantic caching: a similar query", "সেমান্টিক ক্যাশিং: কাছাকাছি query"),
       [("Semantic caching reuses a stored answer when a query is only similar. It compares embeddings against a similarity threshold.",
         "semantic caching query শুধু কাছাকাছি হলেও জমানো উত্তর আবার ব্যবহার করে। এটা embedding সিমিলারিটি threshold-এর সাথে মিলিয়ে দেখে।"),
        ("A bad semantic threshold returns a plausible wrong answer.",
         "ভুল semantic threshold বিশ্বাসযোগ্য দেখতে ভুল উত্তর দেয়।")],
       [sh("user", "dim"), sh("scache", "warn", ("similar query", "কাছাকাছি query")), sh("model", "dim")],
       [ln("user", "scache", "to", state="hot"), ln("scache", "model", "to", state="dim")],
       [None, None, ("wrong answer", "ভুল উত্তর")]),

    st(("Write action", "রাইট অ্যাকশন"),
       ("Write actions change the real world", "রাইট অ্যাকশন বাস্তব জগৎ বদলায়"),
       [("A write action changes something in the real world, such as sending an email, placing an order, or updating a database.",
         "রাইট অ্যাকশন বাস্তব জগতে কিছু বদলায়, যেমন ইমেইল পাঠানো, অর্ডার বসানো, বা ডেটাবেস আপডেট করা।"),
        ("It makes a system more capable but riskier: a mistake becomes a real-world side effect.",
         "এটা সিস্টেমকে বেশি সক্ষম করে, কিন্তু ঝুঁকিও বাড়ায়, কারণ ভুল তখন বাস্তব জগতে প্রভাব ফেলে।")],
       [sh("model", "hot", x=380), sh("action", "warn", ("real-world side effect", "বাস্তব জগতে প্রভাব"))],
       [ln("model", "action", "to", state="warn")],
       [None, None, ("riskier", "বেশি ঝুঁকি")]),

    st(("Remember", "মনে রাখুন"),
       ("One layer at a time", "একে একে স্তর"),
       [("Layers are added one at a time: context, guardrails, router and gateway, caches, then agent patterns.",
         "স্তরগুলো একে একে যোগ হয়: context, guardrails, router আর gateway, cache, তারপর agent pattern।"),
        ("Each solves a real problem, not a wish for complexity.",
         "প্রতিটি একটি আসল সমস্যা মেটায়, জটিলতার শখে যোগ হয় না।")],
       [sh("ctx", "hot", x=130, y=90), sh("guard", "hot", x=320, y=90), sh("router", "hot", x=490, y=90), sh("gateway", "hot", x=650, y=90),
        sh("ecache", "hot", x=190, y=230), sh("scache", "hot", x=400, y=230), sh("action", "hot", x=620, y=230)],
       [ln("ctx", "guard", "to", state="hot"), ln("guard", "router", "to", state="hot"), ln("router", "gateway", "to", state="hot"),
        ln("ecache", "scache", "to", state="hot"), ln("scache", "action", "to", state="hot")],
       [("one at a time", "একে একে"), None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
