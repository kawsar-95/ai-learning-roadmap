"""Deploying and operating AI systems · 15 AI coding assistants: give the tool context and limits, then review its work like any other change.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Assistant  Body: "Tools such as Claude Code, Cursor, GitHub Copilot, Gemini CLI and Codex CLI read your repository, edit files, run commands and iterate." "Treat it like a fast junior engineer: give it context and limits, and review its work."
  2 Context    Body: "A context file in the repository tells the tool how the project works: the build and test commands, the conventions, and what not to touch." "AGENTS.md is an open convention that several tools read." "Keep it short and true."
  3 Limits     Body: "Permissions. Let the tool run read-only commands freely, and ask before it writes outside the project, installs packages or uses the network."
  4 MCP        Body: "MCP servers let a tool call outside systems, such as files, databases and other tools, through one protocol. Each one is also an attack surface, so install only servers you trust."
  5 Branch     Body: "One task, one branch. Give each agent its own branch, and its own worktree when several run at once." "Small, checkable steps beat one huge request. When a step goes wrong, you throw away a small branch."
  6 Review     Body: "For a large change, ask for a plan first, and read the diff, not only the summary." "Make the tool run the tests, and read what it ran." "Never paste secrets into a prompt, and keep real credentials out of the folder the tool can read."
  7 Remember   Warning: "Speed moves the bottleneck to review. Generated code that nobody understands is a loan you repay during the first outage. Keep the tests, the types and a human reviewer in the loop."; and the four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("repo", "file", ("Repository", "রিপোজিটরি"), 110, 162),
    node("tool", "tool", ("AI assistant", "AI অ্যাসিস্ট্যান্ট"), 380, 162),
    node("ctx", "note", ("Context file", "কনটেক্সট ফাইল"), 380, 60),
    node("mcp", "service", ("MCP server", "MCP সার্ভার"), 650, 60),
    node("branch", "file", ("Branch", "ব্রাঞ্চ"), 650, 162),
    node("tree", "file", ("Worktree", "ওয়ার্কট্রি"), 650, 260),
    node("diff", "file", ("Diff", "ডিফ"), 650, 162),
    node("tests", "shield", ("Tests", "টেস্ট"), 380, 260),
    node("human", "user", ("Human reviewer", "মানুষ রিভিউয়ার"), 650, 260),
    node("secret", "key", ("Secrets", "সিক্রেট"), 110, 260),
]

METRICS = [
    ("Context", "কনটেক্সট"),
    ("Permissions", "অনুমতি"),
    ("Review", "রিভিউ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Assistant", "অ্যাসিস্ট্যান্ট"),
       ("A fast junior engineer", "দ্রুত জুনিয়র ইঞ্জিনিয়ার"),
       [("An AI coding assistant reads your repository, edits files and runs commands.",
         "AI কোডিং অ্যাসিস্ট্যান্ট আপনার রিপোজিটরি পড়ে, ফাইল বদলায় আর কমান্ড চালায়।"),
        ("Treat it like a fast junior engineer: give it context and limits, and review its work.",
         "একে দ্রুত জুনিয়র ইঞ্জিনিয়ারের মতো ধরুন: কনটেক্সট আর সীমা দিন, আর তার কাজ রিভিউ করুন।")],
       [sh("repo", "hot", ("reads", "পড়ে")), sh("tool", "hot", ("edits, runs", "বদলায়, চালায়")), sh("diff", "hot")],
       [ln("repo", "tool", "to", state="hot"), ln("tool", "diff", "to", state="hot")],
       [None, None, None]),

    st(("Context", "কনটেক্সট"),
       ("Give it a context file", "কনটেক্সট ফাইল দিন"),
       [("A context file in the repository tells the tool how the project works: the build and test commands, the conventions, and what not to touch.",
         "রিপোজিটরির একটা context ফাইল টুলকে জানায় প্রজেক্ট কীভাবে চলে: বিল্ড আর টেস্টের কমান্ড, নিয়মকানুন, আর কী ছোঁয়া যাবে না।"),
        ("AGENTS.md is an open convention that several tools read. Keep it short and true.",
         "AGENTS.md একটা খোলা রীতি যা কয়েকটা টুল পড়ে। ফাইলটা ছোট আর সত্য রাখুন।")],
       [sh("ctx", "hot", ("short and true", "ছোট আর সত্য")), sh("tool", "hot"), sh("repo", "dim")],
       [ln("ctx", "tool", "to", state="hot"), ln("repo", "tool", "to", state="dim")],
       [("short, true", "ছোট, সত্য"), None, None]),

    st(("Limits", "সীমা"),
       ("Set the permissions", "অনুমতি ঠিক করুন"),
       [("Let the tool run read-only commands freely.",
         "রিড-অনলি কমান্ড টুলকে স্বাধীনভাবে চালাতে দিন।"),
        ("Ask before it writes outside the project, installs packages or uses the network.",
         "প্রজেক্টের বাইরে লেখা, প্যাকেজ ইনস্টল বা নেটওয়ার্ক ব্যবহারের আগে জিজ্ঞেস করতে বলুন।")],
       [sh("repo", "hot", ("read-only: free", "রিড-অনলি: স্বাধীন")), sh("tool", "hot"), sh("mcp", "warn", ("ask first", "আগে জিজ্ঞেস"))],
       [ln("repo", "tool", "to", state="hot"), ln("tool", "mcp", "to", state="warn")],
       [None, ("ask first", "আগে জিজ্ঞেস"), None]),

    st(("MCP", "MCP"),
       ("MCP servers are an attack surface", "MCP সার্ভার আক্রমণের জায়গা"),
       [("MCP servers let a tool call outside systems, such as files, databases and other tools, through one protocol.",
         "MCP সার্ভার টুলকে একটা প্রটোকলে বাইরের সিস্টেম কল করতে দেয়, যেমন ফাইল, ডেটাবেস আর অন্য টুল।"),
        ("Each one is also an attack surface, so install only servers you trust.",
         "প্রতিটি সার্ভার আক্রমণেরও জায়গা, তাই শুধু বিশ্বস্ত সার্ভার ইনস্টল করুন।")],
       [sh("tool", "hot"), sh("mcp", "warn", ("attack surface", "অ্যাটাক সারফেস"))],
       [ln("tool", "mcp", "to", state="warn")],
       [None, None, None],
       note=("warn", "Install only servers you trust.", "শুধু বিশ্বস্ত সার্ভার ইনস্টল করুন।")),

    st(("Branch", "ব্রাঞ্চ"),
       ("One task, one branch", "একটা কাজ, একটা ব্রাঞ্চ"),
       [("Give each agent its own branch, and its own worktree when several run at once.",
         "প্রতিটি এজেন্টকে আলাদা ব্রাঞ্চ দিন, আর একসাথে অনেকগুলো চালালে আলাদা worktree-ও দিন।"),
        ("Small, checkable steps beat one huge request. When a step goes wrong, you throw away a small branch.",
         "ছোট ছোট যাচাইযোগ্য ধাপ একটা বিশাল অনুরোধের চেয়ে ভালো। কিছু ভুল হলে ছোট ব্রাঞ্চটাই ফেলে দেবেন।")],
       [sh("tool", "hot"), sh("branch", "hot", ("its own", "নিজস্ব")), sh("tree", "hot", ("several at once", "একসাথে অনেক"))],
       [ln("tool", "branch", "to", state="hot"), ln("branch", "tree", "to", state="hot")],
       [None, None, None]),

    st(("Review", "রিভিউ"),
       ("Review it like any other change", "অন্য যেকোনো পরিবর্তনের মতো রিভিউ করুন"),
       [("For a large change, ask for a plan first, and read the diff, not only the summary. Make the tool run the tests, and read what it ran.",
         "বড় পরিবর্তনের আগে পরিকল্পনা চান, আর শুধু সারাংশ নয়, diff পড়ুন। টুলকে টেস্ট চালাতে বলুন আর কী চালিয়েছে তা পড়ুন।"),
        ("Never paste secrets into a prompt, and keep real credentials out of the folder the tool can read.",
         "প্রম্পটে কখনও সিক্রেট দেবেন না।")],
       [sh("tool", "hot"), sh("diff", "hot", ("read it", "পড়ুন")), sh("tests", "hot", ("read what it ran", "কী চালিয়েছে পড়ুন")),
        sh("human", "hot"), sh("secret", "warn", ("never in a prompt", "প্রম্পটে কখনও নয়"))],
       [ln("tool", "diff", "to", state="hot"), ln("tool", "tests", "to", state="hot"), ln("diff", "human", "to", state="hot"),
        ln("tests", "human", "to", state="hot"), ln("secret", "tool", "to", state="warn")],
       [None, None, ("diff and tests", "diff আর টেস্ট")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Speed moves the bottleneck to review. Keep the tests, the types and a human reviewer in the loop.",
         "গতি বাধাটাকে রিভিউয়ে সরিয়ে দেয়। টেস্ট, টাইপ আর একজন মানুষ রিভিউয়ার রাখুন।")],
       [sh("ctx", "hot"), sh("tool", "hot"), sh("branch", "hot"), sh("tests", "hot"), sh("human", "hot")],
       [ln("ctx", "tool", "to", state="hot"), ln("tool", "branch", "to", state="hot"), ln("tool", "tests", "to", state="hot"),
        ln("tests", "human", "to", state="hot"), ln("branch", "human", "to", state="hot")],
       [None, None, None],
       points=[("Give the tool a short, true context file and clear permissions.",
                "টুলকে ছোট ও সত্য কনটেক্সট ফাইল আর পরিষ্কার অনুমতির সীমা দিন।"),
               ("Give each task its own branch, and work in small, checkable steps.",
                "প্রতিটি কাজ আলাদা ব্রাঞ্চে করান, আর ছোট ছোট যাচাইযোগ্য ধাপে এগোন।"),
               ("Read the diff and the tests it ran, not only the summary.",
                "শুধু সারাংশ নয়, ডিফ আর সে যে টেস্ট চালিয়েছে তা পড়ুন।"),
               ("Never paste secrets into a prompt. Keep tests, types and a human reviewer in the loop.",
                "প্রম্পটে কখনও সিক্রেট দেবেন না। টেস্ট, টাইপ আর একজন মানুষ রিভিউয়ার রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
