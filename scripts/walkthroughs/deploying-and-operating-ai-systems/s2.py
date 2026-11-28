"""Deploying and operating AI systems · 02 Git and GitHub: what goes in Git, how work is reviewed, and how a leaked secret happens.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Git       Body: "Git records every change to your code, prompts and settings. GitHub adds review and automatic checks. AI work also needs care with secrets and large files."
  2 Commit    Body: "A commit is a snapshot of the project with a message. A branch is a movable name for a commit, so creating one is cheap." Start here: "like a save point in a game", "so you can try changes safely".
  3 Pull      Body: "a pull request asks for that branch to be merged into main after review and automatic checks."
  4 Keep      Table: "Put in Git" (code, prompts, eval cases, config files) and "Keep out of Git" (API keys, .env files, passwords; model weights and large datasets: use Git LFS, an object store or a model hub).
  5 Worktree  Body: "git worktree checks out more than one branch of the same repository into separate folders. Coding agents that work in parallel each get their own folder and branch, so they cannot overwrite one another's files."
  6 Rebase    Body: "Rebase tidies your own unpublished branch by rewriting its commits. Never rebase a branch that other people have pulled. Merge keeps shared history as it was."
  7 Secret    Warning: "A secret you commit is a secret you leaked. Deleting the file in a later commit does not remove it from history. Revoke the key at the provider first, then clean up."
  8 Remember  The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("git", "database", ("Git", "Git"), 380, 162),
    node("gh", "server", ("GitHub", "GitHub"), 650, 162),
    node("commit", "file", ("Commit", "কমিট"), 110, 162),
    node("branch", "note", ("Branch", "ব্রাঞ্চ"), 380, 162),
    node("main", "storage", ("main", "main"), 650, 162),
    node("pr", "note", ("Pull request", "পুল রিকোয়েস্ট"), 280, 162),
    node("rc", "shield", ("Review and checks", "রিভিউ আর চেক"), 480, 162),
    node("code", "file", ("Code, prompts, eval cases", "কোড, প্রম্পট, ইভ্যাল কেস"), 130, 162),
    node("secrets", "key", ("API keys, .env files", "API key, .env ফাইল"), 600, 70),
    node("weights", "storage", ("Model weights", "মডেল ওয়েট"), 600, 262),
    node("wta", "file", ("Own folder and branch", "নিজের ফোল্ডার আর ব্রাঞ্চ"), 600, 70),
    node("wtb", "file", ("Own folder and branch", "নিজের ফোল্ডার আর ব্রাঞ্চ"), 600, 262),
]

METRICS = [
    ("In Git", "Git-এ"),
    ("Out of Git", "Git-এর বাইরে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Git", "Git"),
       ("Git records, GitHub reviews", "Git লিখে রাখে, GitHub রিভিউ করে"),
       [("Git records every change to your code, prompts and settings. GitHub adds review and automatic checks.",
         "Git আপনার কোড, প্রম্পট আর সেটিংসের প্রতিটি পরিবর্তন লিখে রাখে। GitHub যোগ করে রিভিউ আর অটোমেটিক চেক।"),
        ("AI work also needs care with secrets and large files.",
         "AI কাজে সিক্রেট আর বড় ফাইল নিয়েও সতর্ক থাকতে হয়।")],
       [sh("git", "hot", ("every change", "প্রতিটি পরিবর্তন"), x=130, y=162), sh("gh", "hot", ("automatic checks", "অটোমেটিক চেক"), x=610, y=162)],
       [ln("git", "gh", "to", state="hot")],
       [None, None]),

    st(("Commit", "কমিট"),
       ("A commit and a branch", "কমিট আর ব্রাঞ্চ"),
       [("A commit is a snapshot of the project with a message, like a save point in a game.",
         "কমিট একটি বার্তাসহ প্রজেক্টের সংরক্ষিত স্ন্যাপশট, খেলার সেভ পয়েন্টের মতো।"),
        ("A branch is a movable name for a commit. Making one is cheap, so you can try changes safely.",
         "ব্রাঞ্চ একটি কমিটের সরানো যায় এমন নাম। বানানো সস্তা, তাই নিরাপদে পরিবর্তন চেষ্টা করা যায়।")],
       [sh("commit", "hot", x=130, y=162, sub=("snapshot with a message", "বার্তাসহ স্ন্যাপশট")), sh("branch", "hot", ("movable name", "সরানো যায় এমন নাম"), x=400, y=162), sh("main", "dim", x=650, y=162)],
       [ln("commit", "branch", "to", state="hot"), ln("branch", "main", "to", state="dim")],
       [None, None]),

    st(("Pull request", "পুল রিকোয়েস্ট"),
       ("A pull request asks to merge", "পুল রিকোয়েস্ট মার্জ চায়"),
       [("Work happens on a branch.",
         "কাজ হয় একটি ব্রাঞ্চে।"),
        ("A pull request asks for that branch to be merged into main after review and automatic checks.",
         "পুল রিকোয়েস্ট রিভিউ আর অটোমেটিক চেকের পর সেই ব্রাঞ্চ main-এ মার্জ করার অনুরোধ জানায়।")],
       [sh("branch", "hot", x=150, y=70), sh("pr", "hot", x=400, y=70), sh("rc", "hot", x=640, y=70), sh("main", "hot", x=640, y=254)],
       [ln("branch", "pr", "to", state="hot"), ln("pr", "rc", "to", state="hot"), ln("rc", "main", "to", state="hot")],
       [None, None]),

    st(("Keep", "রাখুন"),
       ("What goes in Git, what stays out", "Git-এ কী, বাইরে কী"),
       [("Keep code, prompts, eval cases and config in Git.",
         "কোড, প্রম্পট, ইভ্যাল কেস আর কনফিগ Git-এ রাখুন।"),
        ("Keep API keys, .env files and model weights out. For large files use Git LFS, an object store or a model hub.",
         "API key, .env ফাইল আর মডেল ওয়েট রাখবেন না। বড় ফাইলের জন্য Git LFS, অবজেক্ট স্টোর বা মডেল হাব ব্যবহার করুন।")],
       [sh("code", "hot"), sh("git", "hot", x=380, y=162), sh("secrets", "warn", ("keep out", "বাইরে রাখুন")),
        sh("weights", "warn", ("LFS, object store or hub", "LFS, অবজেক্ট স্টোর বা হাব"))],
       [ln("code", "git", "to", state="hot"), ln("git", "secrets", "to", state="warn"), ln("git", "weights", "to", state="warn")],
       [("code, prompts, eval cases, config", "কোড, প্রম্পট, ইভ্যাল কেস, কনফিগ"), ("API keys, .env, weights", "API key, .env, ওয়েট")]),

    st(("Worktree", "worktree"),
       ("Several agents, one repository", "অনেক এজেন্ট, একটি রিপোজিটরি"),
       [("<code>git worktree</code> checks out more than one branch of the same repository into separate folders.",
         "<code>git worktree</code> একই রিপোজিটরির একাধিক ব্রাঞ্চ আলাদা আলাদা ফোল্ডারে চেক আউট করে।"),
        ("Coding agents that work in parallel each get their own folder and branch, so they cannot overwrite one another's files.",
         "সমান্তরালে চলা প্রতিটি কোডিং এজেন্ট নিজের ফোল্ডার আর ব্রাঞ্চ পায়, তাই একে অপরের ফাইল বদলে ফেলতে পারে না।")],
       [sh("git", "hot", ("one repository", "একটি রিপোজিটরি"), x=150, y=162), sh("wta", "hot"), sh("wtb", "hot")],
       [ln("git", "wta", "to", state="hot"), ln("git", "wtb", "to", state="hot")],
       [None, None]),

    st(("Rebase", "রিবেস"),
       ("Rebase only your own branch", "রিবেস শুধু নিজের ব্রাঞ্চে"),
       [("Rebase tidies your own unpublished branch by rewriting its commits. Merge keeps shared history as it was.",
         "রিবেস নিজের অপ্রকাশিত ব্রাঞ্চের কমিট নতুন করে লিখে গুছিয়ে নেয়। মার্জ শেয়ার করা ইতিহাস যেমন ছিল তেমন রাখে।"),
        ("Never rebase a branch that other people have pulled.",
         "অন্যরা যে ব্রাঞ্চ নামিয়ে নিয়েছে, তা কখনো রিবেস করবেন না।")],
       [sh("branch", "hot", ("your own, unpublished", "আপনার নিজের, অপ্রকাশিত"), x=150, y=162), sh("main", "dim", ("shared history", "শেয়ার করা ইতিহাস"), x=610, y=162)],
       [ln("branch", "main", "to", state="dim", label=("merge", "মার্জ"))],
       [None, None],
       note=("warn", "Write commit messages that say why, and keep each commit to one change.",
             "কমিট বার্তায় কেন তা লিখুন, আর প্রতিটি কমিটে একটি পরিবর্তন রাখুন।")),

    st(("Secret", "সিক্রেট"),
       ("A committed secret is leaked", "কমিট করা সিক্রেট ফাঁস"),
       [("A secret you commit is a secret you leaked. Deleting the file in a later commit does not remove it from history.",
         "কমিট করা সিক্রেট মানে ফাঁস হয়ে যাওয়া সিক্রেট। পরের কমিটে ফাইল মুছলে ইতিহাস থেকে তা যায় না।"),
        ("Revoke the key at the provider first, then clean up.",
         "আগে provider-এ key বাতিল করুন, তারপর পরিষ্কার করুন।")],
       [sh("secrets", "warn", ("committed", "কমিট করা"), x=150, y=162), sh("git", "warn", ("stays in history", "ইতিহাসে থেকে যায়"), x=610, y=162)],
       [ln("secrets", "git", "to", state="warn")],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Keep code in Git and secrets out.",
         "কোড Git-এ রাখুন, সিক্রেট বাইরে।")],
       [sh("code", "hot"), sh("git", "hot", x=380, y=162), sh("secrets", "warn")],
       [ln("code", "git", "to", state="hot"), ln("git", "secrets", "to", state="warn")],
       [None, None],
       points=[("Keep code, prompts, eval cases and config in Git. Keep API keys, .env files and model weights out.",
                "কোড, প্রম্পট, ইভ্যাল কেস আর কনফিগ Git-এ রাখুন। API key, .env ফাইল আর মডেল ওয়েট রাখবেন না।"),
               ("Give each parallel coding agent its own worktree and branch, so they cannot overwrite each other's files.",
                "সমান্তরাল প্রতিটি কোডিং এজেন্টকে আলাদা worktree আর ব্রাঞ্চ দিন, যাতে একে অপরের ফাইল বদলে না ফেলে।"),
               ("Never rebase a branch that other people have pulled.",
                "অন্যরা যে ব্রাঞ্চ নামিয়ে নিয়েছে, তা কখনো রিবেস করবেন না।"),
               ("A secret you commit is a secret you leaked. Revoke the key at the provider first.",
                "কমিট করা সিক্রেট মানে ফাঁস হয়ে যাওয়া সিক্রেট। আগে provider-এ key বাতিল করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
