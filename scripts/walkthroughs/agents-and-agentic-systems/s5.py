"""Part 9 · 05 Agent memory: scratchpad, semantic, procedural: three main memory types, two more, and where memory breaks.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Scratchpad  Words: "Scratchpad (working memory): The model's private notes for the current run. When the run ends, they are thrown away." "Context window ... A scratchpad can live there."
  2 Semantic    Words: "Semantic memory: Long-term facts the agent has learned about the user, the project, or the world." "Vector store: A database that finds items by meaning, not by exact words."
  3 Procedural  Words: "Procedural memory: The agent's playbook of how to do a task. It is kept as versioned prompt templates or Markdown checklists."
  4 More        Words: "Episodic memory: A record of past runs and what happened in them." Table: "Identity: Who the agent is".
  5 Breaks      Body, "Where memory breaks": too much, too little, conflicting.
  6 Conflict    Practice: "When two facts disagree, the agent needs a rule, for example the newer date wins." Facts: Dhaka and Chattogram.
  7 Remember    The three "Where memory breaks" lines and "The scratchpad is thrown away when the run ends."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("agent", "model", ("Agent", "এজেন্ট"), 120, 162),
    node("pad", "file", ("Scratchpad", "স্ক্র্যাচপ্যাড"), 400, 162),
    node("ctx", "cache", ("Context window", "কনটেক্সট উইন্ডো"), 650, 162),
    node("sem", "database", ("Semantic memory", "সেম্যান্টিক মেমরি"), 400, 162),
    node("vec", "database", ("Vector store", "ভেক্টর স্টোর"), 650, 162),
    node("proc", "file", ("Procedural memory", "প্রসিডিউরাল মেমরি"), 400, 162),
    node("epi", "storage", ("Episodic memory", "এপিসোডিক মেমরি"), 400, 100),
    node("ident", "note", ("Identity", "আইডেন্টিটি"), 400, 230),
    node("much", "note", ("Too much", "খুব বেশি"), 450, 75),
    node("little", "note", ("Too little", "খুব কম"), 450, 162),
    node("conf", "note", ("Conflicting", "পরস্পরবিরোধী"), 450, 250),
    node("old", "note", ("User lives in Dhaka", "User Dhaka-য় থাকে"), 560, 75),
]

METRICS = [
    ("Lasts", "টেকে"),
    ("Found by", "খোঁজা হয়"),
    ("Kept as", "রাখা হয়"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Scratchpad", "স্ক্র্যাচপ্যাড"),
       ("The scratchpad: notes for one run", "স্ক্র্যাচপ্যাড: একটি রানের নোট"),
       [("The scratchpad, or working memory, is the model's private notes for the current run.",
         "স্ক্র্যাচপ্যাড (working memory) বর্তমান রানের জন্য মডেলের নিজস্ব নোট।"),
        ("When the run ends, the notes are thrown away. A scratchpad can live in the context window.",
         "রান শেষ হলে এগুলো ফেলে দেওয়া হয়। স্ক্র্যাচপ্যাড কনটেক্সট উইন্ডোতে থাকতে পারে।")],
       [sh("agent", "hot"), sh("pad", "hot", ("thrown away", "ফেলে দেওয়া হয়")), sh("ctx", "hot", ("can live there", "সেখানে থাকতে পারে"))],
       [ln("agent", "pad", "to", state="hot"), ln("pad", "ctx", "to", state="hot")],
       [("until the run ends", "রান শেষ হওয়া পর্যন্ত"), None, None]),

    st(("Semantic", "সেম্যান্টিক"),
       ("Semantic memory: long-term facts", "সেম্যান্টিক মেমরি: দীর্ঘমেয়াদি তথ্য"),
       [("Semantic memory holds long-term facts the agent has learned about the user, the project, or the world.",
         "সেম্যান্টিক মেমরি হলো ব্যবহারকারী, প্রজেক্ট বা দুনিয়া সম্পর্কে এজেন্ট যে দীর্ঘমেয়াদি তথ্য শিখেছে।"),
        ("A vector store is a database that finds items by meaning, not by exact words.",
         "ভেক্টর স্টোর এমন ডেটাবেস, যা হুবহু শব্দ দিয়ে নয়, অর্থ দিয়ে জিনিস খুঁজে বের করে।")],
       [sh("agent", "hot"), sh("sem", "hot", ("long-term facts", "দীর্ঘমেয়াদি তথ্য")), sh("vec", "hot", ("by meaning", "অর্থ দিয়ে"))],
       [ln("agent", "sem", "to", state="hot"), ln("sem", "vec", "to", state="hot")],
       [("long-term", "দীর্ঘমেয়াদি"), ("meaning", "অর্থ"), None]),

    st(("Procedural", "প্রসিডিউরাল"),
       ("Procedural memory: the playbook", "প্রসিডিউরাল মেমরি: প্লেবুক"),
       [("Procedural memory is the agent's playbook of how to do a task.",
         "প্রসিডিউরাল মেমরি হলো কোনো কাজ কীভাবে করতে হয়, তার প্লেবুক।"),
        ("It is kept as versioned prompt templates or Markdown checklists.",
         "ভার্সন করা প্রম্পট টেমপ্লেট বা Markdown চেকলিস্ট হিসেবে রাখা হয়।")],
       [sh("agent", "hot"), sh("proc", "hot", ("how to do a task", "কাজ কীভাবে করতে হয়"))],
       [ln("agent", "proc", "to", state="hot")],
       [None, None, ("versioned prompt templates", "ভার্সন করা প্রম্পট টেমপ্লেট")]),

    st(("More", "আরও"),
       ("Two more memory types", "আরও দুই ধরনের মেমরি"),
       [("Episodic memory is a record of past runs and what happened in them.",
         "এপিসোডিক মেমরি হলো আগের রানগুলো আর সেগুলোতে কী ঘটেছিল, তার রেকর্ড।"),
        ("Identity is who the agent is.",
         "আইডেন্টিটি হলো এজেন্ট কে।")],
       [sh("agent", "hot"), sh("epi", "hot", ("past runs", "আগের রান")), sh("ident", "hot", ("who the agent is", "এজেন্ট কে"))],
       [ln("agent", "epi", "to", state="hot"), ln("agent", "ident", "to", state="hot")],
       [None, None, None]),

    st(("Breaks", "ভাঙে"),
       ("Where memory breaks", "মেমরি কোথায় ভেঙে পড়ে"),
       [("Too much memory makes the agent trust stale facts. Too little makes it re-derive the same conclusion every turn.",
         "খুব বেশি মেমরি থাকলে এজেন্ট পুরোনো তথ্যের ওপর ভরসা করে। খুব কম থাকলে প্রতিবার একই সিদ্ধান্ত নতুন করে বের করে।"),
        ("Conflicting memory means two facts disagree.",
         "মেমরি পরস্পরবিরোধী হলে দুটি তথ্য একে অপরের সাথে মেলে না।")],
       [sh("agent", "hot"), sh("much", "warn", ("trusts stale facts", "পুরোনো তথ্যে ভরসা")),
        sh("little", "warn", ("re-derives every turn", "প্রতিবার নতুন করে বের করে")), sh("conf", "warn", ("two facts disagree", "দুটি তথ্য মেলে না"))],
       [ln("agent", "much", "to", state="warn"), ln("agent", "little", "to", state="warn"), ln("agent", "conf", "to", state="warn")],
       [None, None, None]),

    st(("Conflict", "গরমিল"),
       ("Two facts disagree", "দুটি তথ্য মেলে না"),
       [("Say the memory holds two facts: the user lives in Dhaka, and the user lives in Chattogram.",
         "ধরুন মেমরিতে দুটি তথ্য: User Dhaka-য় থাকে, আর User Chattogram-এ থাকে।"),
        ("The agent needs a rule for this, for example the newer date wins.",
         "এজেন্টের এর জন্য একটা নিয়ম লাগে, যেমন নতুন তারিখেরটাই জেতে।")],
       [sh("sem", "hot", x=120, y=162), sh("old", "dim", ("older", "পুরোনো"), x=450, y=75),
        sh("conf", "hot", ("newer date wins", "নতুন তারিখেরটাই জেতে"), x=450, y=250)],
       [ln("sem", "old", "to", state="dim"), ln("sem", "conf", "to", state="hot")],
       [None, None, None],
       note=("warn", "An old saved fact is a risk: stale facts cause confidently wrong answers.",
             "পুরোনো সংরক্ষিত তথ্য ঝুঁকির: পুরোনো তথ্য আত্মবিশ্বাসী ভুল উত্তর দেয়।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("The scratchpad is thrown away when the run ends.",
         "রান শেষ হলে স্ক্র্যাচপ্যাড ফেলে দেওয়া হয়।")],
       [sh("pad", "hot", x=130, y=162), sh("sem", "hot", x=400, y=162), sh("proc", "hot", x=650, y=162)],
       [],
       [None, None, None],
       points=[("Too much memory makes the agent trust stale facts.",
                "খুব বেশি মেমরি থাকলে এজেন্ট পুরোনো তথ্যের ওপর ভরসা করে।"),
               ("Too little memory makes the agent re-derive the same conclusion every turn.",
                "খুব কম মেমরি থাকলে এজেন্ট প্রতিবার একই সিদ্ধান্ত নতুন করে বের করে।"),
               ("Conflicting memory means two facts disagree.",
                "মেমরি পরস্পরবিরোধী হলে দুটি তথ্য একে অপরের সাথে মেলে না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
