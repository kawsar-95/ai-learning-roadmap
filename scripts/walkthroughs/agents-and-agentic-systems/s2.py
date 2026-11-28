"""Part 6 · 02 The four canonical agent loops: ReAct, Plan-and-Execute, Reflexion and ReWOO, and how to pick one.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 ReAct     Sub-title: "Every agent loop you'll meet in production is a variation of one of these four patterns. Pick by the shape of your task, not by hype."; ReAct ("The simplest loop. The model writes a thought, picks an action, sees the result, and repeats.").
  2 Trace     Body: "The thought is in the model's private scratchpad and never shown to the user; only the final answer is."; the code: a thought about the population of Tokyo in 2024, search(...), an observation, "Now I can answer.", Finish(...); the callout: "the interleaved reasoning makes traces human-readable. When something goes wrong, you can read the scratchpad and see why the model picked the action it did."
  3 Plan      Body: "a planner (usually a strong LLM) produces a sequence of steps, then a worker (often a smaller model or a deterministic tool) carries out each step ... If a step fails, the planner re-runs only that step (cheap) rather than the whole loop."
  4 Reflect   Body: "after a ReAct attempt, the model is asked to reflect on what went wrong, and that reflection is appended to the memory for the next attempt. In the paper, Reflexion improves on baseline agents by up to 22 points on AlfWorld, 20 on HotPotQA and 11 on HumanEval."; Start here: "In the paper, Reflexion beats baseline agents by up to 22 points (AlfWorld), but costs extra attempts and reflection calls."
  5 ReWOO     Body: "in many retrieval-heavy tasks, the model doesn't need to see the result of tool #1 to plan tool #2. It plans the entire tool graph upfront, the worker executes everything in parallel, then the solver reads the evidence and answers. In the paper, ReWOO used about 5× fewer tokens on HotpotQA and 64% fewer on average across six benchmarks."; Start here: "In the paper, ReWOO used about 5× fewer tokens on HotpotQA (64% fewer on average over six benchmarks), but is hard to debug."
  6 Pick      Layman's voice: "default to ReAct. If your task is "go look up 5 things in parallel and write a summary," switch to ReWOO. If your task is "do these 6 steps in order, but be ready to replan if step 3 fails," use Plan-and-Execute."; and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("llm", "model", ("LLM", "LLM"), 110, 162),
    node("tool", "tool", ("Tool", "টুল"), 380, 75),
    node("obs", "file", ("Observation", "পর্যবেক্ষণ"), 650, 162),
    node("planner", "model", ("Planner", "প্ল্যানার"), 110, 162),
    node("steps", "file", ("Steps", "ধাপ"), 380, 75),
    node("worker", "service", ("Worker", "ওয়ার্কার"), 650, 162),
    node("reflect", "note", ("Reflection", "রিফ্লেকশন"), 380, 75),
    node("memory", "storage", ("Memory", "মেমরি"), 650, 162),
    node("w1", "service", ("Worker", "ওয়ার্কার"), 380, 75),
    node("w2", "service", ("Worker", "ওয়ার্কার"), 380, 162),
    node("w3", "service", ("Worker", "ওয়ার্কার"), 380, 250),
    node("solver", "model", ("Solver", "সলভার"), 650, 162),
]

METRICS = [
    ("Quality", "মান"),
    ("Cost", "খরচ"),
    ("Tokens", "টোকেন"),
]

CAPTION = (
    "The four canonical agent loops, one at a time. Production systems usually compose them.",
    "চারটি প্রচলিত এজেন্ট লুপ, একটি করে। প্রোডাকশন সিস্টেম সাধারণত এগুলো মিশিয়ে ব্যবহার করে।",
)


def cycle(a, b, c, state=None):
    """A three-box loop: a to b, b to c, and c back to a."""
    return [ln(a, b, "to", state=state), ln(b, c, "to", state=state), ln(c, a, "to", state=state)]


STEPS = [
    st(("ReAct", "ReAct"),
       ("ReAct: think, act, observe", "ReAct: ভাবা, করা, দেখা"),
       [("Every agent loop in production is a version of four patterns. Pick the loop that fits the shape of your task, not the one that is popular.",
         "প্রোডাকশনের প্রতিটি এজেন্ট লুপ চারটি প্যাটার্নের একটির রূপ। যে লুপ আপনার কাজের ধরনের সাথে মেলে তাকে বাছুন, যেটা জনপ্রিয় সেটাকে নয়।"),
        ("ReAct is the simplest loop. The model writes a thought, picks an action, sees the result, and repeats.",
         "ReAct সবচেয়ে সহজ লুপ। মডেল চিন্তা লেখে, অ্যাকশন বাছে, ফল দেখে, আর আবার করে।")],
       [sh("llm", "hot", ("Thought", "চিন্তা")), sh("tool", "hot", ("Action", "অ্যাকশন")), sh("obs", "hot")],
       cycle("llm", "tool", "obs", "hot"),
       [None, None, None]),

    st(("Trace", "ট্রেস"),
       ("Read the scratchpad", "স্ক্র্যাচপ্যাড পড়ুন"),
       [("The thought stays in the model's private scratchpad. The user sees only the final answer.",
         "চিন্তা থাকে মডেলের নিজস্ব স্ক্র্যাচপ্যাডে। ব্যবহারকারী শুধু শেষ উত্তর দেখে।"),
        ("In the section's example, the model thinks it needs the population of Tokyo in 2024, calls <code>search</code>, sees the result, thinks “Now I can answer”, and calls <code>Finish</code>.",
         "সেকশনের উদাহরণে মডেল ভাবে ২০২৪ সালে টোকিওর জনসংখ্যা দরকার, <code>search</code> ডাকে, ফল দেখে, ভাবে “এবার উত্তর দিতে পারি”, আর <code>Finish</code> ডাকে।")],
       [sh("llm", "hot", ("private scratchpad", "গোপন স্ক্র্যাচপ্যাড")), sh("tool", "hot", ("search, Finish", "search, Finish")), sh("obs", "hot", ("the result", "ফল"))],
       cycle("llm", "tool", "obs", "hot"),
       [None, None, None],
       note=("tip",
             "Because the reasoning is interleaved, a trace is readable. When something goes wrong, you can see why the model picked the action it did.",
             "চিন্তা আর কাজ পালা করে চলে বলে ট্রেস পড়া যায়। কিছু ভুল হলে দেখা যায়, মডেল কেন সেই অ্যাকশন বাছল।")),

    st(("Plan", "প্ল্যান"),
       ("Plan-and-Execute: plan, then do", "Plan-and-Execute: আগে প্ল্যান, তারপর কাজ"),
       [("Plan-and-Execute separates planning from execution. A planner, usually a strong LLM, makes a list of steps. A worker, often a smaller model or a deterministic tool, then carries out each step.",
         "Plan-and-Execute পরিকল্পনা আর কাজ আলাদা করে। একজন প্ল্যানার, সাধারণত শক্তিশালী LLM, ধাপের তালিকা বানায়। তারপর একজন ওয়ার্কার, প্রায়ই ছোট মডেল বা নির্ধারিত টুল, প্রতিটি ধাপ করে।"),
        ("If a step fails, the planner re-runs only that step, which is cheap, not the whole loop.",
         "কোনো ধাপ ব্যর্থ হলে প্ল্যানার শুধু সেই ধাপটি আবার চালায়, যা সস্তা; পুরো লুপ নয়।")],
       [sh("planner", "hot", ("writes the steps", "ধাপ লেখে")), sh("steps", "hot"), sh("worker", "hot", ("does each step", "প্রতিটি ধাপ করে"))],
       [ln("planner", "steps", "to", state="hot"), ln("steps", "worker", "to", state="hot"),
        ln("worker", "planner", "to", state="warn", label=("failed step", "ব্যর্থ ধাপ"))],
       [None, None, None]),

    st(("Reflect", "রিফ্লেক্ট"),
       ("Reflexion: learn from the miss", "Reflexion: ভুল থেকে শেখা"),
       [("Reflexion adds a second pass. After an attempt, the model reflects on what went wrong, and the reflection is added to its memory for the next try.",
         "Reflexion একটি দ্বিতীয় পাস যোগ করে। একবার চেষ্টার পর মডেল ভাবে কী ভুল হলো, আর সেই নোট পরের চেষ্টার জন্য তার মেমরিতে যোগ হয়।"),
        ("In the paper, Reflexion improves on baseline agents by up to 22 points on AlfWorld, 20 on HotPotQA and 11 on HumanEval. It costs extra attempts and reflection calls.",
         "পেপারে Reflexion বেসলাইন এজেন্টের চেয়ে AlfWorld-এ সর্বোচ্চ ২২ পয়েন্ট, HotPotQA-তে ২০ আর HumanEval-এ ১১ পয়েন্ট ভালো করেছে। এতে বাড়তি চেষ্টা আর রিফ্লেকশন কলের খরচ লাগে।")],
       [sh("llm", "hot", ("attempt", "চেষ্টা")), sh("reflect", "hot", ("what went wrong", "কী ভুল হলো")), sh("memory", "hot", ("kept for next try", "পরের চেষ্টার জন্য"))],
       cycle("llm", "reflect", "memory", "hot"),
       [("up to +22 points", "সর্বোচ্চ +২২ পয়েন্ট"), ("extra calls", "বাড়তি কল"), None]),

    st(("ReWOO", "ReWOO"),
       ("ReWOO: plan every call first", "ReWOO: আগে সব কল প্ল্যান"),
       [("In many retrieval-heavy tasks, the model does not need to see the result of tool 1 to plan tool 2. So it plans the whole tool graph up front.",
         "অনেক খোঁজাখুঁজি-ভারী কাজে টুল ২ প্ল্যান করতে মডেলের টুল ১-এর ফল দেখার দরকার হয় না। তাই সে পুরো টুল-গ্রাফ আগেই প্ল্যান করে।"),
        ("A worker runs everything in parallel, then a solver reads the evidence and answers. In the paper, ReWOO used about 5× fewer tokens on HotpotQA (64% fewer on average over six benchmarks), but it is hard to debug.",
         "একজন ওয়ার্কার সবগুলো প্যারালালে চালায়, তারপর সলভার প্রমাণ পড়ে উত্তর দেয়। পেপারে ReWOO HotpotQA-তে প্রায় ৫ গুণ কম টোকেন নিয়েছে (ছয়টি বেঞ্চমার্কে গড়ে ৬৪% কম), কিন্তু ডিবাগ করা কঠিন।")],
       [sh("planner", "hot", ("plans every call", "সব কল প্ল্যান করে")), sh("w1", "hot", ("runs a call", "একটি কল চালায়")), sh("w2", "hot", ("runs a call", "একটি কল চালায়")),
        sh("w3", "hot", ("runs a call", "একটি কল চালায়")), sh("solver", "hot", ("reads the evidence", "প্রমাণ পড়ে"))],
       [ln("planner", "w1", "to", state="hot"), ln("planner", "w2", "to", state="hot"), ln("planner", "w3", "to", state="hot"),
        ln("w1", "solver", "to", state="hot"), ln("w2", "solver", "to", state="hot"), ln("w3", "solver", "to", state="hot")],
       [None, None, ("about 5× fewer", "প্রায় ৫ গুণ কম")]),

    st(("Pick", "বাছাই"),
       ("Pick by the shape of the task", "কাজের ধরন দেখে বাছুন"),
       [("Default to ReAct. If the task is “go look up 5 things in parallel and write a summary”, switch to ReWOO. If it is “do these 6 steps in order, but be ready to replan if step 3 fails”, use Plan-and-Execute.",
         "ReAct দিয়ে শুরু করুন। কাজ যদি হয় “প্যারালালে ৫টি জিনিস খুঁজে সারসংক্ষেপ লিখুন”, তবে ReWOO। কাজ যদি হয় “এই ৬টি ধাপ পরপর করুন, তবে ৩ নম্বর ধাপ ব্যর্থ হলে রিপ্ল্যান করতে তৈরি থাকুন”, তবে Plan-and-Execute।")],
       [sh("llm", None, ("the default", "ডিফল্ট")), sh("tool"), sh("obs")],
       cycle("llm", "tool", "obs"),
       [None, None, None],
       points=[("ReAct is the default loop. Its readable scratchpad shows why the model chose each action.",
                "ReAct ডিফল্ট লুপ। এর পড়ার মতো স্ক্র্যাচপ্যাড দেখায় মডেল কেন প্রতিটি অ্যাকশন বাছল।"),
               ("Plan-and-Execute can redo only the failed step, which is cheap.",
                "Plan-and-Execute শুধু ব্যর্থ ধাপটি আবার করতে পারে, যা সস্তা।"),
               ("In the paper, Reflexion beats baseline agents by up to 22 points (AlfWorld), but costs extra attempts and reflection calls.",
                "পেপারে Reflexion বেসলাইন এজেন্টের চেয়ে সর্বোচ্চ ২২ পার্সেন্টেজ পয়েন্ট (AlfWorld) ভালো করে, কিন্তু বাড়তি চেষ্টা আর রিফ্লেকশন কলের খরচ লাগে।"),
               ("In the paper, ReWOO used about 5× fewer tokens on HotpotQA (64% fewer on average over six benchmarks), but is hard to debug.",
                "পেপারে ReWOO HotpotQA-তে প্রায় ৫ গুণ কম টোকেন নিয়েছে (ছয়টি বেঞ্চমার্কে গড়ে ৬৪% কম), কিন্তু ডিবাগ করা কঠিন।"),
               ("Match the task: ReAct for short, tool-heavy tasks; ReWOO for look-up-heavy tasks with many parallel tool calls.",
                "কাজ দেখে বাছুন: ছোট, টুল-নির্ভর কাজে ReAct; অনেক প্যারালাল টুল কলসহ খোঁজাখুঁজি-ভারী কাজে ReWOO।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
