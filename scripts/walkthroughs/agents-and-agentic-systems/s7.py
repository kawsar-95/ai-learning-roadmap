"""Part 9 · 07 Subagents and delegation patterns: the parent hands one job to a subagent, waits, and gets back one final result.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Too much  Body: "When one agent has too much to do for one context window, it can hand work to a subagent. The parent waits and gets back only a final result."
  2 Subagent  Body: "A subagent is an agent launched by another agent. It has its own system prompt, its own tool surface, its own loop, and its own termination."
  3 Manager   Body: "The mental model is manager -> worker, not fork/join. The parent does not poll the subagent. The parent does not stream the subagent's progress ... receives a single, structured result. The benefit: the parent's context window stays clean."
  4 Agent tool Body: "Claude Code ships an Agent tool that the model can invoke to spawn a subagent ... returns a summary. The parent never sees the intermediate steps — only the summary."
  5 Frameworks Body: "openai-agents-sdk exposes Runner.run(agent, input) returning a final RunResult. CrewAI models multi-agent systems as crews (the team), agents (the roles), tasks (the work), and a process (sequential or hierarchical)."
  6 When      List "When to use a subagent": well-defined and self-contained; different tools; intermediate steps would pollute the parent's context; retried independently; billed to a different cost centre.
  7 Remember  Points: "A subagent returns a final result to the parent, not its intermediate steps." "The parent does not poll or stream the subagent. Its context window stays clean."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("ctx", "file", ("Context window", "কনটেক্সট উইন্ডো"), 110, 50),
    node("parent", "model", ("Parent agent", "প্যারেন্ট এজেন্ট"), 110, 200),
    node("sub", "model", ("Subagent", "সাবএজেন্ট"), 390, 200),
    node("res", "note", ("Final result", "চূড়ান্ত ফলাফল"), 650, 200),
    node("tool", "tool", ("Agent tool", "Agent টুল"), 250, 60),
    node("sdk", "tool", ("openai-agents-sdk", "openai-agents-sdk"), 110, 70),
    node("rr", "note", ("RunResult", "RunResult"), 400, 70),
    node("crew", "service", ("Crew", "ক্রু"), 70, 250),
    node("agents", "model", ("Agents", "এজেন্ট"), 220, 250),
    node("tasks", "file", ("Tasks", "টাস্ক"), 365, 250),
    node("proc", "queue", ("Process", "প্রসেস"), 590, 250),
]

METRICS = [
    ("Parent gets", "প্যারেন্ট পায়"),
    ("Parent window", "প্যারেন্টের উইন্ডো"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Too much", "বেশি কাজ"),
       ("Hand the work to a subagent", "কাজ দিন সাবএজেন্টকে"),
       [("When one agent has too much to do for one context window, it can hand work to a subagent.",
         "একটি এজেন্টের কাজ এক কনটেক্সট উইন্ডোর জন্য বেশি হয়ে গেলে সে কাজ দিতে পারে একটি সাবএজেন্টকে।"),
        ("The parent waits and gets back only a final result.",
         "প্যারেন্ট অপেক্ষা করে আর শুধু চূড়ান্ত ফলাফল ফেরত পায়।")],
       [sh("ctx", "warn", ("too much to do", "কাজ বেশি")), sh("parent", "hot"), sh("sub", "hot"), sh("res", "hot")],
       [ln("parent", "sub", "to", state="hot"), ln("sub", "res", "to", state="hot")],
       [("final result only", "শুধু চূড়ান্ত ফলাফল"), None]),

    st(("Subagent", "সাবএজেন্ট"),
       ("What a subagent is", "সাবএজেন্ট কী"),
       [("A subagent is an agent started by another agent.",
         "সাবএজেন্ট হলো অন্য এজেন্টের চালু করা একটি এজেন্ট।"),
        ("It has its own prompt, its own tools, its own loop, and its own end point.",
         "তার নিজের প্রম্পট, টুল, লুপ আর শেষ করার নিয়ম আছে।")],
       [sh("parent", "dim"), sh("sub", "hot", ("own prompt, tools, loop", "নিজের প্রম্পট, টুল, লুপ")), sh("res", "dim")],
       [ln("parent", "sub", "to", state="dim")],
       [None, None]),

    st(("Manager", "ম্যানেজার"),
       ("Manager–worker, not fork/join", "ম্যানেজার–ওয়ার্কার, ফর্ক/জয়েন নয়"),
       [("The parent gives a job and waits. It does not poll the subagent and does not watch its progress.",
         "প্যারেন্ট কাজ দিয়ে অপেক্ষা করে। সে বারবার খোঁজ নেয় না, অগ্রগতিও দেখে না।"),
        ("It gets a single result, so the parent's context window stays clean.",
         "সে একটিমাত্র ফলাফল পায়, তাই প্যারেন্টের কনটেক্সট উইন্ডো পরিষ্কার থাকে।")],
       [sh("parent", "hot", ("waits", "অপেক্ষা করে")), sh("sub", "hot"), sh("res", "hot", ("one result", "একটিমাত্র ফলাফল")), sh("ctx", "hot", ("stays clean", "পরিষ্কার থাকে"))],
       [ln("parent", "sub", "to", state="hot"), ln("sub", "res", "to", state="hot")],
       [("one result", "একটিমাত্র ফলাফল"), ("clean", "পরিষ্কার")],
       note=("tip", "The section says not to picture subagents as fork/join.",
             "এই সেকশন বলে, সাবএজেন্টকে ফর্ক/জয়েন-এর মতো করে ভাববেন না।")),

    st(("Agent tool", "Agent টুল"),
       ("Claude Code's Agent tool", "Claude Code-এর Agent টুল"),
       [("Claude Code has an Agent tool that the model calls to start a subagent.",
         "Claude Code-এ একটি Agent টুল আছে, যা মডেল ডেকে সাবএজেন্ট চালু করে।"),
        ("The subagent runs in its own loop with its own tools. The parent never sees the intermediate steps, only the summary.",
         "সাবএজেন্ট নিজের লুপে নিজের টুল নিয়ে চলে। প্যারেন্ট মাঝের ধাপ দেখে না, শুধু সারাংশ দেখে।")],
       [sh("parent", "hot"), sh("tool", "hot"), sh("sub", "hot", ("own loop, own tools", "নিজের লুপ, নিজের টুল")), sh("res", "hot", ("summary", "সারাংশ"))],
       [ln("parent", "tool", "to", state="hot"), ln("tool", "sub", "to", state="hot"), ln("sub", "res", "to", state="hot")],
       [("summary", "সারাংশ"), None]),

    st(("Frameworks", "ফ্রেমওয়ার্ক"),
       ("OpenAI's agents-sdk and CrewAI", "OpenAI-র agents-sdk আর CrewAI"),
       [("OpenAI's openai-agents-sdk has Runner.run(agent, input), which returns a final RunResult.",
         "OpenAI-র openai-agents-sdk-তে আছে Runner.run(agent, input), যা একটি চূড়ান্ত RunResult ফেরত দেয়।"),
        ("CrewAI models a multi-agent system as a crew (the team), agents (the roles), tasks (the work), and a process (sequential or hierarchical).",
         "CrewAI মাল্টি-এজেন্ট সিস্টেমকে ভাগ করে ক্রু (দল), এজেন্ট (ভূমিকা), টাস্ক (কাজ) আর প্রসেসে (সিকোয়েন্সিয়াল বা হায়ারার্কিক্যাল)।")],
       [sh("sdk", "hot"), sh("rr", "hot", ("final", "চূড়ান্ত")), sh("crew", "hot", ("the team", "দল")), sh("agents", "hot", ("the roles", "ভূমিকা")),
        sh("tasks", "hot", ("the work", "কাজ")), sh("proc", "hot", ("sequential or hierarchical", "সিকোয়েন্সিয়াল/হায়ারার্কিক্যাল"))],
       [ln("sdk", "rr", "to", state="hot"), ln("crew", "agents", state="hot"), ln("agents", "tasks", state="hot"), ln("tasks", "proc", state="hot")],
       [("final RunResult", "চূড়ান্ত RunResult"), None]),

    st(("When", "কখন"),
       ("When to use a subagent", "কখন সাবএজেন্ট ব্যবহার করবেন"),
       [("Use a subagent when the task is well-defined and self-contained, needs different tools, or has steps that would pollute the parent's context.",
         "কাজটি স্পষ্টভাবে সংজ্ঞায়িত হলে, ভিন্ন টুল লাগলে, বা তার মাঝের ধাপ প্যারেন্টের কনটেক্সট দূষিত করলে সাবএজেন্ট ব্যবহার করুন।"),
        ("Use one also when you want independent retries or a separate cost centre.",
         "আলাদাভাবে রিট্রাই বা আলাদা খরচ-কেন্দ্র চাইলেও এটি ব্যবহার করুন।")],
       [sh("parent", "hot"), sh("sub", "hot"), sh("res", "hot")],
       [ln("parent", "sub", "to", state="hot"), ln("sub", "res", "to", state="hot")],
       [None, None],
       changes=[("+", "The subtask is well-defined and self-contained", "সাবটাস্ক স্পষ্টভাবে সংজ্ঞায়িত আর স্বয়ংসম্পূর্ণ"),
                ("+", "The subtask needs different tools than the parent has", "সাবটাস্কের জন্য প্যারেন্টের চেয়ে ভিন্ন টুল লাগে"),
                ("+", "The subtask's intermediate steps would pollute the parent's context", "সাবটাস্কের মাঝের ধাপ প্যারেন্টের কনটেক্সট দূষিত করবে"),
                ("+", "You want the subtask retried independently of the parent", "প্যারেন্টের থেকে আলাদাভাবে সাবটাস্ক রিট্রাই করতে চান"),
                ("+", "You want to bill the subtask to a different cost centre", "সাবটাস্কের খরচ আলাদা খরচ-কেন্দ্রে ধরতে চান")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A subagent returns a final result to the parent, not its intermediate steps.",
         "সাবএজেন্ট প্যারেন্টকে চূড়ান্ত ফলাফল ফেরত দেয়, মাঝের ধাপ নয়।")],
       [sh("ctx", "hot", ("stays clean", "পরিষ্কার থাকে")), sh("parent", "hot"), sh("sub", "hot"), sh("res", "hot")],
       [ln("parent", "sub", "to", state="hot"), ln("sub", "res", "to", state="hot")],
       [("final result", "চূড়ান্ত ফলাফল"), ("clean", "পরিষ্কার")],
       points=[("A subagent returns a final result to the parent, not its intermediate steps.",
                "সাবএজেন্ট প্যারেন্টকে চূড়ান্ত ফলাফল ফেরত দেয়, মাঝের ধাপ নয়।"),
               ("The parent does not poll or stream the subagent. Its context window stays clean.",
                "প্যারেন্ট সাবএজেন্টকে পোল বা স্ট্রিম করে না। তাই তার কনটেক্সট উইন্ডো পরিষ্কার থাকে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
