"""Part 9 · 04 State machines and workflow graphs: draw the agent's steps as a graph of nodes and edges instead of hiding them in one loop.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Loop      Words: "Implicit loop: A plain loop where the path is hidden. After 30 tool calls, you cannot tell which path the model took."
  2 Graph     Words: "Graph: A map of nodes (steps) joined by edges (moves). Each edge can have a condition." Body: "every node has a name, every edge has a condition, every transition is recorded."
  3 LangGraph Words: "LangGraph: LangChain's graph framework. It lets the agent go back to an earlier step." Body: "Cycles are first-class (an agent can loop back to an earlier node)".
  4 Resume    Words: "Checkpointer: A LangGraph feature that lets you resume from any past state."
  5 Durable   Words: "Durable: Able to survive crashes, retries, and pauses for a human, which long-running agents need." "Agents that run for minutes to hours need a durable graph."
  6 Engines   Words: "Temporal and Restate: Workflow engines adapted to run long agents." Table: "Restate: Same as Temporal, smaller surface".
  7 Pick      Table "Picking a graph framework": LangGraph, Temporal, Mastra, Inngest and each "Best for" line. Body: "Inngest ... pay-per-step pricing."
  8 Remember  Words: "An implicit loop is fast to write but impossible to debug. An explicit graph shows every path." and the other points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("loop", "model", ("One hidden loop", "একটি লুকানো লুপ"), 130, 162),
    node("llm", "model", ("llm", "llm"), 130, 162),
    node("tools", "tool", ("tools", "tools"), 400, 75),
    node("end", "note", ("END", "END"), 400, 250),
    node("ck", "storage", ("Checkpointer", "চেকপয়েন্টার"), 650, 162),
    node("dur", "shield", ("Durable graph", "ডিউরেবল গ্রাফ"), 130, 162),
    node("tmp", "service", ("Temporal", "Temporal"), 400, 100),
    node("rst", "service", ("Restate", "Restate"), 400, 230),
    node("lg", "service", ("LangGraph", "LangGraph"), 200, 100),
    node("mas", "service", ("Mastra", "Mastra"), 200, 230),
    node("inn", "service", ("Inngest", "Inngest"), 560, 230),
]

METRICS = [
    ("Writing", "লেখা"),
    ("Debugging", "ডিবাগ"),
    ("Runs for", "চলে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Loop", "লুপ"),
       ("The implicit loop hides the path", "ইমপ্লিসিট লুপ পথ লুকায়"),
       [("An implicit loop is a plain loop where the path is hidden.",
         "ইমপ্লিসিট লুপ সাধারণ লুপ, যেখানে পথ লুকানো থাকে।"),
        ("After 30 tool calls, you cannot tell which path the model took.",
         "৩০টি টুল কলের পর বোঝা যায় না মডেল কোন পথে গেছে।")],
       [sh("loop", "warn", ("path hidden", "পথ লুকানো")), sh("tools", "dim")],
       [ln("loop", "tools", "to", state="warn")],
       [("fast to write", "লেখা দ্রুত"), ("impossible", "অসম্ভব"), None]),

    st(("Graph", "গ্রাফ"),
       ("A graph of nodes and edges", "নোড আর এজের গ্রাফ"),
       [("A graph is a map of nodes (steps) joined by edges (moves). Each edge can have a condition.",
         "গ্রাফ হলো নোড (ধাপ) আর এজ (চলন) দিয়ে জোড়া মানচিত্র। প্রতিটি এজে শর্ত থাকতে পারে।"),
        ("Every node has a name, and every transition is recorded.",
         "প্রতিটি ধাপের নাম থাকে আর প্রতিটি চলন রেকর্ড হয়।")],
       [sh("llm", "hot"), sh("tools", "hot"), sh("end", "hot")],
       [ln("llm", "tools", "to", state="hot", label=("tool", "tool")), ln("llm", "end", "to", state="hot", label=("END", "END"))],
       [None, ("shows every path", "প্রতিটি পথ দেখায়"), None]),

    st(("LangGraph", "LangGraph"),
       ("LangGraph can go back", "LangGraph ফিরে যেতে পারে"),
       [("LangGraph is LangChain's graph framework, a widely used Python or TypeScript option.",
         "LangGraph হলো LangChain-এর গ্রাফ ফ্রেমওয়ার্ক।"),
        ("Cycles are first-class: the agent can go back to an earlier step.",
         "এটি এজেন্টকে আগের ধাপে ফিরে যেতে দেয়।")],
       [sh("llm", "hot"), sh("tools", "hot"), sh("end", "dim")],
       [ln("tools", "llm", "to", state="hot", label=("back", "ফিরে"))],
       [None, None, None]),

    st(("Resume", "রিজিউম"),
       ("The checkpointer resumes", "চেকপয়েন্টার আবার শুরু করে"),
       [("The checkpointer is a LangGraph feature.",
         "চেকপয়েন্টার LangGraph-এর একটি ফিচার।"),
        ("It lets you resume from any past state.",
         "এটি দিয়ে যেকোনো আগের স্টেট থেকে আবার শুরু করা যায়।")],
       [sh("llm", "hot"), sh("tools", "dim"), sh("ck", "hot", ("any past state", "যেকোনো আগের স্টেট"))],
       [ln("ck", "llm", "to", state="hot", label=("resume", "রিজিউম"))],
       [None, None, None]),

    st(("Durable", "ডিউরেবল"),
       ("Long agents need a durable graph", "দীর্ঘ এজেন্টের ডিউরেবল গ্রাফ লাগে"),
       [("Agents that run for minutes to hours need a durable graph.",
         "কয়েক মিনিট থেকে কয়েক ঘণ্টা চলা এজেন্টের জন্য ডিউরেবল গ্রাফ দরকার।"),
        ("Durable means able to survive crashes, retries, and pauses for a human.",
         "ডিউরেবল মানে ক্র্যাশ, রিট্রাই আর মানুষের জন্য থামা সামলে টিকে থাকতে পারা।")],
       [sh("dur", "hot", ("survives crashes", "ক্র্যাশ সামলায়")), sh("llm", "dim", x=400, y=75), sh("tools", "dim", x=400, y=250)],
       [ln("dur", "llm", "to", state="hot"), ln("dur", "tools", "to", state="hot")],
       [None, None, ("minutes to hours", "কয়েক মিনিট থেকে কয়েক ঘণ্টা")]),

    st(("Engines", "ইঞ্জিন"),
       ("Temporal and Restate", "Temporal আর Restate"),
       [("Temporal and Restate are workflow engines adapted to run long agents.",
         "Temporal আর Restate ওয়ার্কফ্লো ইঞ্জিন, যা দীর্ঘ এজেন্ট চালাতে মানিয়ে নেওয়া হয়েছে।"),
        ("Restate is the same as Temporal, with a smaller surface.",
         "Restate হলো Temporal-এর মতোই, ছোট পরিসরে।")],
       [sh("dur", "hot"), sh("tmp", "hot", ("multi-day workflows", "কয়েক দিনের ওয়ার্কফ্লো")), sh("rst", "hot", ("smaller surface", "ছোট পরিসর"))],
       [ln("tmp", "dur", "to", state="hot"), ln("rst", "dur", "to", state="hot")],
       [None, None, ("multi-day", "কয়েক দিনের")]),

    st(("Pick", "বাছাই"),
       ("Picking one", "একটা বেছে নেওয়া"),
       [("LangGraph suits Python or TypeScript teams already using LangChain. Temporal fits multi-day workflows, and Mastra suits teams who write TypeScript.",
         "যে Python বা TypeScript টিম আগে থেকেই LangChain ব্যবহার করে, LangGraph তাদের জন্য ভালো। Temporal কয়েক দিনের ওয়ার্কফ্লোর জন্য, আর TypeScript-এ কাজ করা টিমের জন্য Mastra ভালো।"),
        ("Inngest starts work when an event happens, and you pay for each step.",
         "Inngest কোনো ইভেন্ট ঘটলে কাজ শুরু করে, আর প্রতি ধাপের জন্য দাম দিতে হয়।")],
       [sh("lg", "hot", ("already using LangChain", "আগে থেকে LangChain")), sh("tmp", "hot", ("multi-day", "কয়েক দিনের"), x=560, y=100),
        sh("mas", "hot", ("TypeScript", "TypeScript")), sh("inn", "hot", ("event, pay per step", "ইভেন্ট, প্রতি ধাপে দাম"))],
       [],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("An implicit loop is fast to write but impossible to debug. An explicit graph shows every path.",
         "ইমপ্লিসিট লুপ লেখা দ্রুত, কিন্তু ডিবাগ অসম্ভব। এক্সপ্লিসিট গ্রাফ প্রতিটি পথ দেখায়।")],
       [sh("llm", "hot"), sh("tools", "hot"), sh("end", "hot")],
       [ln("llm", "tools", "to", state="hot"), ln("llm", "end", "to", state="hot")],
       [("fast to write", "লেখা দ্রুত"), ("shows every path", "প্রতিটি পথ দেখায়"), None],
       points=[("Agents that run for minutes to hours need a durable graph.",
                "কয়েক মিনিট থেকে কয়েক ঘণ্টা চলা এজেন্টের জন্য ডিউরেবল গ্রাফ দরকার।"),
               ("Temporal fits multi-day workflows, and Mastra suits teams who write TypeScript.",
                "Temporal কয়েক দিনের ওয়ার্কফ্লোর জন্য, আর TypeScript-এ কাজ করা টিমের জন্য Mastra ভালো।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
