"""Part 6 · 01 What an agent actually is: a loop with five things a production agent needs.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Loop      Start here: "An agent is a loop: the AI looks at the state, decides what to do, acts, and repeats until the job is done."; body: "a loop that takes the current state, asks an LLM what to do next, executes the answer (a tool call, a structured response, or a final answer), and feeds the result back in."
  2 Workflow  Start here: Workflow ("A fixed map of LLM calls and tool calls. Every step and branch is written by a person in advance."); "In an agent, the LLM picks at least one step while it runs."; the rule of thumb: "if a human could write a flowchart of the system's behaviour from the prompt alone, it's a workflow. If the LLM picks the next node at runtime, it's an agent."; "Most shipped systems are a mix — deterministic scaffolding around a few agentic decisions."
  3 Bounds    Body, "What every production agent needs": "A bounded loop with a hard step cap and a wall-clock timeout. Unbounded loops are how agents burn $10k overnight."; the code: max_steps=20 and raise AgentTimeout("loop did not terminate").
  4 Tools     Same list: "A tool surface that's narrow, well-typed, and namespaced (so the model can't accidentally call a destructive tool without going through a guardrail)."
  5 Notes     Same list: "A scratchpad — some persistent state across turns that survives the LLM's context window. Either the model writes to a file, the framework keeps it, or you stuff it into the next prompt."
  6 Exit      Same list: "An exit predicate: at minimum, "I think I have enough; here is the answer." Without one the agent will keep acting forever."
  7 Trace     Same list: "Observability: every step recorded with prompt, tool call, result, cost, and latency. Without it you cannot debug."
  8 Remember  Layman's voice: "Skip any one and you have a hobby project, not a product."; and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("cap", "clock", ("Step cap", "ধাপ-সীমা"), 110, 75),
    node("llm", "model", ("LLM", "LLM"), 380, 75),
    node("answer", "note", ("Answer", "উত্তর"), 650, 75),
    node("guard", "shield", ("Guardrail", "গার্ডরেইল"), 650, 75),
    node("state", "file", ("State", "স্টেট"), 110, 162),
    node("tool", "tool", ("Tools", "টুল"), 650, 162),
    node("goal", "user", ("Goal", "লক্ষ্য"), 110, 250),
    node("flow", "service", ("Workflow", "ওয়ার্কফ্লো"), 380, 250),
    node("scratch", "storage", ("Scratchpad", "স্ক্র্যাচপ্যাড"), 380, 250),
    node("trace", "chart", ("Trace", "ট্রেস"), 380, 250),
]

METRICS = [
    ("Step cap", "ধাপ-সীমা"),
    ("Unbounded", "সীমাহীন লুপ"),
    ("Exit rule", "থামার নিয়ম"),
]

CAPTION = (
    "Example: the loop of a minimal agent, and the parts a production agent adds around it.",
    "উদাহরণ: ন্যূনতম এজেন্টের লুপ, আর প্রোডাকশন এজেন্ট তার চারপাশে যে অংশগুলো যোগ করে।",
)


def loop(state=None):
    """State, LLM, tools and back to the state."""
    return [ln("state", "llm", "to", state=state), ln("llm", "tool", "to", state=state), ln("tool", "state", "to", state=state)]


STEPS = [
    st(("Loop", "লুপ"),
       ("An agent is a loop", "এজেন্ট একটি লুপ"),
       [("An agent is a loop: the AI looks at the state, decides what to do, acts, and repeats until the job is done.",
         "এজেন্ট হলো একটি লুপ: AI স্টেট দেখে, কী করবে ঠিক করে, কাজ করে, আর কাজ শেষ না হওয়া পর্যন্ত আবার করে।"),
        ("The loop takes the current state, asks an LLM what to do next, executes the answer, and feeds the result back in. The answer can be a tool call, a structured response, or a final answer.",
         "লুপটি বর্তমান স্টেট নেয়, LLM-কে জিজ্ঞেস করে পরে কী করবে, উত্তর চালায়, আর ফল আবার ভেতরে ফিরিয়ে দেয়। উত্তর হতে পারে একটি টুল কল, একটি কাঠামোবদ্ধ উত্তর, বা চূড়ান্ত উত্তর।")],
       [sh("goal", "hot"), sh("state", "hot", ("looks at it", "দেখে")), sh("llm", "hot", ("decides", "সিদ্ধান্ত নেয়")), sh("tool", "hot", ("acts", "কাজ করে")), sh("answer", "hot")],
       [ln("goal", "state", "to", state="hot")] + loop("hot") + [ln("llm", "answer", "to", state="hot")],
       [None, None, None]),

    st(("Workflow", "ওয়ার্কফ্লো"),
       ("Workflow or agent?", "ওয়ার্কফ্লো, না এজেন্ট?"),
       [("A workflow is a fixed map of LLM calls and tool calls: every step and branch is written by a person in advance. In an agent, the LLM picks at least one step while it runs.",
         "ওয়ার্কফ্লো হলো LLM কল আর টুল কলের একটি নির্দিষ্ট মানচিত্র: প্রতিটি ধাপ ও শাখা আগে থেকে মানুষ লিখে রাখে। এজেন্টে অন্তত একটি ধাপ LLM চলার সময় নিজেই বাছে।"),
        ("Rule of thumb: if a human could write a flowchart of the system's behavior from the prompt alone, it is a workflow. If the LLM picks the next node at runtime, it is an agent.",
         "সহজ নিয়ম: প্রম্পট দেখেই কোনো মানুষ যদি সিস্টেমের আচরণের ফ্লোচার্ট লিখে ফেলতে পারে, তবে সেটা ওয়ার্কফ্লো। LLM যদি রানটাইমে পরের নোড বাছে, তবে সেটা এজেন্ট।")],
       [sh("llm", "hot", ("picks a step at runtime", "রানটাইমে ধাপ বাছে")), sh("flow", "hot", ("people write every step", "প্রতিটি ধাপ মানুষ লেখে"))],
       [],
       [None, None, None],
       note=("tip",
             "Most shipped systems are a mix: deterministic scaffolding around a few agentic decisions.",
             "বেশিরভাগ চালু সিস্টেমই মিশ্র: কয়েকটি এজেন্টিক সিদ্ধান্তকে ঘিরে নির্ধারিত কাঠামো।")),

    st(("Bounds", "সীমা"),
       ("Bound the loop", "লুপে সীমা দিন"),
       [("Give the loop a hard step cap and a wall-clock timeout. Unbounded loops are how agents burn $10k overnight.",
         "লুপে কড়া ধাপ-সীমা আর ঘড়ির টাইমআউট দিন। সীমাহীন লুপ এক রাতে ১০ হাজার ডলার পুড়িয়ে দিতে পারে।"),
        ("In the section's code, <code>max_steps</code> is 20, and the loop raises an error if it has not stopped by then.",
         "সেকশনের কোডে <code>max_steps</code> হলো ২০, আর তার মধ্যে না থামলে লুপ ত্রুটি তোলে।")],
       [sh("cap", "hot", ("stops the loop", "লুপ থামায়")), sh("state", "dim"), sh("llm", "hot"), sh("tool", "dim")],
       [ln("cap", "llm", "to", state="hot")] + loop("dim"),
       ["20", ("$10k", "১০ হাজার ডলার"), None]),

    st(("Tools", "টুল"),
       ("A narrow tool surface", "সংকীর্ণ টুল সারফেস"),
       [("The tool surface is the set of tools an agent can call. Keep it narrow, well-typed and namespaced.",
         "টুল সারফেস হলো এজেন্ট যে টুলগুলো কল করতে পারে তার সেট। এটি সংকীর্ণ, টাইপ করা আর নেমস্পেস দেওয়া রাখুন।"),
        ("Then the model cannot accidentally call a destructive tool without going through a guardrail.",
         "তাহলে মডেল গার্ডরেইল পার না হয়ে হঠাৎ কোনো ধ্বংসাত্মক টুল কল করতে পারে না।")],
       [sh("state", "dim"), sh("llm", "hot"), sh("guard", "hot", ("checks the call", "কল যাচাই করে")), sh("tool", "hot", ("narrow and typed", "সংকীর্ণ ও টাইপ করা"))],
       [ln("state", "llm", "to", state="dim"), ln("llm", "guard", "to", state="hot"), ln("guard", "tool", "to", state="hot"), ln("tool", "state", "to", state="dim")],
       [None, None, None]),

    st(("Notes", "নোট"),
       ("A scratchpad that survives", "যে স্ক্র্যাচপ্যাড টিকে থাকে"),
       [("A scratchpad keeps notes across turns, so they survive even when the model's context window runs out.",
         "স্ক্র্যাচপ্যাড টার্নের পর টার্ন নোট রাখে, যাতে মডেলের কনটেক্সট উইন্ডো ফুরিয়ে গেলেও নোট থাকে।"),
        ("The model writes to a file, the framework keeps it, or you stuff it into the next prompt.",
         "মডেল ফাইলে লেখে, ফ্রেমওয়ার্ক রাখে, অথবা আপনি পরের প্রম্পটে ঢুকিয়ে দেন।")],
       [sh("llm", "hot"), sh("scratch", "hot", ("survives the window", "উইন্ডো ফুরোলেও থাকে")), sh("state", "dim"), sh("tool", "dim")],
       [ln("llm", "scratch", "both", state="hot")] + loop("dim"),
       [None, None, None]),

    st(("Exit", "থামা"),
       ("Say when it is done", "কখন শেষ, সেটা বলুন"),
       [("An exit predicate is the rule that tells the agent it is done: at minimum, “I think I have enough; here is the answer.”",
         "এগজিট প্রেডিকেট হলো সেই নিয়ম, যা এজেন্টকে বলে কাজ শেষ: অন্তত “আমার যথেষ্ট তথ্য আছে; এই নিন উত্তর”।"),
        ("Without one, the agent will keep acting forever.",
         "এমন নিয়ম না থাকলে এজেন্ট চলতেই থাকবে।")],
       [sh("state", "dim"), sh("llm", "hot", ("I have enough", "যথেষ্ট তথ্য আছে")), sh("tool", "dim"), sh("answer", "hot", ("final answer", "চূড়ান্ত উত্তর"))],
       [ln("llm", "answer", "to", state="hot")] + loop("dim"),
       [None, None, ("“I have enough”", "“যথেষ্ট তথ্য আছে”")]),

    st(("Trace", "ট্রেস"),
       ("Record every step", "প্রতিটি ধাপ রেকর্ড করুন"),
       [("Observability means every step is recorded with its prompt, tool call, result, cost and latency.",
         "অবজারভেবিলিটি মানে প্রতিটি ধাপ প্রম্পট, টুল কল, ফল, খরচ আর লেটেন্সিসহ রেকর্ড করা।"),
        ("Without it, you cannot debug the agent.",
         "এটি না থাকলে এজেন্ট ডিবাগ করা যায় না।")],
       [sh("llm", "hot"), sh("tool", "hot"), sh("trace", "hot", ("every step", "প্রতিটি ধাপ")), sh("state", "dim")],
       [ln("llm", "trace", "to", state="hot"), ln("tool", "trace", "to", state="hot"), ln("state", "llm", "to", state="dim"), ln("llm", "tool", "to", state="dim")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Skip any one of the five parts and you have a hobby project, not a product.",
         "পাঁচটি অংশের যেকোনো একটি বাদ দিলে সেটা প্রোডাক্ট নয়, শখের প্রজেক্ট।")],
       [sh("cap"), sh("llm"), sh("answer"), sh("state"), sh("tool"), sh("scratch")],
       [ln("cap", "llm", "to"), ln("llm", "answer", "to")] + loop(None),
       [None, None, None],
       points=[("Every agent is a loop: take the state, ask the LLM, run the answer, feed the result back.",
                "প্রতিটি এজেন্ট একটি লুপ: স্টেট নিন, LLM-কে জিজ্ঞেস করুন, উত্তর চালান, ফল ফিরিয়ে দিন।"),
               ("In a workflow, people write every step. In an agent, the LLM picks at least one step while it runs.",
                "ওয়ার্কফ্লোতে মানুষ প্রতিটি ধাপ লেখে। এজেন্টে অন্তত একটি ধাপ LLM চলার সময় নিজেই বাছে।"),
               ("Give every loop a hard step cap and a wall-clock timeout. Unbounded loops can burn $10k overnight.",
                "প্রতিটি লুপে কড়া ধাপ-সীমা আর ঘড়ির টাইমআউট দিন। সীমাহীন লুপ এক রাতে ১০ হাজার ডলার পুড়িয়ে দিতে পারে।"),
               ("No exit rule: the agent runs forever. No recorded steps: you cannot debug it.",
                "থামার নিয়ম না থাকলে এজেন্ট চলতেই থাকে। ধাপের রেকর্ড না থাকলে ডিবাগ করা যায় না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
