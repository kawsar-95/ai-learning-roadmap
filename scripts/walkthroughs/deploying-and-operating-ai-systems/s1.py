"""Deploying and operating AI systems · 01 Linux and the shell: commands and habits to find out what a machine is doing before you fix it.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Shell     Body: "Most AI systems run on Linux servers. When one is slow, full or gone, you use a few shell commands to see what the machine is doing before you try to fix it." Start here: "Shell: A text window where you type instructions to the computer instead of clicking."
  2 Read      Body: "Read the machine first with commands like nvidia-smi, df -h and free -h, then fix it." Table rows for nvidia-smi, "df -h, du -sh *", "free -h".
  3 More      Table rows "ps aux, top", "ss -ltnp", "journalctl -u <name>".
  4 Pipe      Body: "A pipe (|) feeds the output of one command into the next: journalctl -u api | grep ERROR | tail."
  5 Signals   Body: "kill <pid> sends SIGTERM, which asks a process to exit and lets it clean up. kill -9 sends SIGKILL, which the process cannot catch, so use it last."
  6 Memory    Warning: "The out-of-memory killer. When RAM runs out, the kernel may kill a process to free memory. A model server that vanishes without an error in its own log is often such a case. Look for an out-of-memory message in the kernel log (dmesg, or journalctl -k)."
  7 Secrets   Body: "Environment variables pass settings, including secrets, to a process. Do not print them into logs."
  8 Remember  The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("shell", "tool", ("Shell", "শেল"), 110, 162),
    node("srv", "server", ("Linux server", "Linux সার্ভার"), 650, 162),
    node("gpu", "chart", ("nvidia-smi", "nvidia-smi"), 380, 60),
    node("disk", "storage", ("df -h", "df -h"), 380, 162),
    node("ram", "chart", ("free -h", "free -h"), 380, 264),
    node("ps", "service", ("ps aux, top", "ps aux, top"), 380, 60),
    node("port", "service", ("ss -ltnp", "ss -ltnp"), 380, 162),
    node("log", "file", ("journalctl", "journalctl"), 380, 264),
    node("grep", "tool", ("grep ERROR", "grep ERROR"), 560, 162),
    node("proc", "service", ("Process", "প্রসেস"), 650, 162),
    node("oom", "shield", ("Out-of-memory killer", "আউট-অব-মেমোরি কিলার"), 380, 162),
    node("env", "key", ("Environment variables", "এনভায়রনমেন্ট ভেরিয়েবল"), 130, 162),
]

METRICS = [
    ("Command", "কমান্ড"),
    ("Look at", "দেখুন"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Shell", "শেল"),
       ("The shell asks the server", "শেল সার্ভারকে জিজ্ঞেস করে"),
       [("Most AI systems run on Linux servers. When one is slow, full or gone, you use a few shell commands to see what the machine is doing.",
         "বেশিরভাগ AI সিস্টেম Linux সার্ভারে চলে। কিছু ধীর, ভরা বা বন্ধ হয়ে গেলে কয়েকটা শেল কমান্ড দিয়ে দেখুন মেশিন কী করছে।"),
        ("The shell is a text window where you type instructions instead of clicking.",
         "শেল একটি টেক্সট উইন্ডো, যেখানে ক্লিক না করে লিখে নির্দেশ দেওয়া হয়।")],
       [sh("shell", "hot", ("type, not click", "ক্লিক নয়, লেখা")), sh("srv", "hot", ("slow, full or gone", "ধীর, ভরা বা বন্ধ"))],
       [ln("shell", "srv", "to", state="hot")],
       [None, None]),

    st(("Read first", "আগে দেখুন"),
       ("Read the machine first", "আগে মেশিন দেখুন"),
       [("Read the machine first with commands like <code>nvidia-smi</code>, <code>df -h</code> and <code>free -h</code>, then fix it.",
         "আগে <code>nvidia-smi</code>, <code>df -h</code>, <code>free -h</code>-এর মতো কমান্ডে মেশিন দেখুন, তারপর ঠিক করুন।"),
        ("Each answers a question: is the GPU busy, is the disk full, is RAM used up.",
         "প্রতিটি একটা প্রশ্নের উত্তর দেয়: GPU ব্যস্ত কি না, ডিস্ক ভরা কি না, RAM ফুরিয়েছে কি না।")],
       [sh("shell", "hot"), sh("gpu", "hot", ("GPU use and memory", "GPU ব্যবহার আর মেমোরি")),
        sh("disk", "hot", ("free space", "খালি জায়গা")), sh("ram", "hot", ("used and available", "ব্যবহৃত আর বাকি")), sh("srv", "hot")],
       [ln("shell", "gpu", "to", state="hot"), ln("shell", "disk", "to", state="hot"), ln("shell", "ram", "to", state="hot"),
        ln("gpu", "srv", "to", state="hot"), ln("ram", "srv", "to", state="hot")],
       [("nvidia-smi, df -h, free -h", "nvidia-smi, df -h, free -h"), None]),

    st(("More", "আরও"),
       ("What runs, what listens, what the log says", "কী চলছে, কী শুনছে, লগে কী আছে"),
       [("<code>ps aux</code> and <code>top</code> show processes with their CPU and memory use. <code>ss -ltnp</code> shows listening TCP sockets and the process behind each.",
         "<code>ps aux</code> আর <code>top</code> প্রসেস আর তাদের CPU ও মেমোরি ব্যবহার দেখায়। <code>ss -ltnp</code> লিসেনিং TCP সকেট আর প্রতিটির পেছনের প্রসেস দেখায়।"),
        ("<code>journalctl -u &lt;name&gt;</code> shows the service's log under systemd.",
         "<code>journalctl -u &lt;name&gt;</code> systemd-এর অধীনে সার্ভিসের লগ দেখায়।")],
       [sh("shell", "hot"), sh("ps", "hot", ("CPU and memory use", "CPU ও মেমোরি ব্যবহার")),
        sh("port", "hot", ("what listens", "কী শুনছে")), sh("log", "hot", ("why a service stopped", "সার্ভিস কেন থামল")), sh("srv", "hot")],
       [ln("shell", "ps", "to", state="hot"), ln("shell", "port", "to", state="hot"), ln("shell", "log", "to", state="hot"),
        ln("ps", "srv", "to", state="hot"), ln("log", "srv", "to", state="hot")],
       [("ps aux, top, ss -ltnp", "ps aux, top, ss -ltnp"), ("journalctl -u", "journalctl -u")]),

    st(("Pipe", "পাইপ"),
       ("A pipe passes output along", "পাইপ আউটপুট এগিয়ে দেয়"),
       [("A pipe (<code>|</code>) feeds the output of one command into the next, like passing a note along a line.",
         "পাইপ (<code>|</code>) এক কমান্ডের আউটপুট পরের কমান্ডে পাঠায়, লাইনে একটা চিরকুট হাতে হাতে পাঠানোর মতো।"),
        ("For example: <code>journalctl -u api | grep ERROR | tail</code>.",
         "যেমন: <code>journalctl -u api | grep ERROR | tail</code>।")],
       [sh("log", "hot", ("journalctl -u api", "journalctl -u api"), x=200, y=162), sh("grep", "hot", ("then tail", "তারপর tail"), x=560, y=162)],
       [ln("log", "grep", "to", state="hot", label=("|", "|"))],
       [("journalctl -u api | grep ERROR | tail", "journalctl -u api | grep ERROR | tail"), None]),

    st(("Signals", "সংকেত"),
       ("Ask first, force last", "আগে অনুরোধ, জোর শেষে"),
       [("<code>kill &lt;pid&gt;</code> sends SIGTERM, which asks a process to exit and lets it clean up.",
         "<code>kill &lt;pid&gt;</code> SIGTERM পাঠায়, যা প্রসেসকে গুছিয়ে বন্ধ হতে বলে।"),
        ("<code>kill -9</code> sends SIGKILL, which the process cannot catch, so use it last.",
         "<code>kill -9</code> SIGKILL পাঠায়, যা প্রসেস আটকাতে পারে না, তাই শেষে ব্যবহার করুন।")],
       [sh("shell", "hot"), sh("proc", "hot", ("exits and cleans up", "গুছিয়ে বন্ধ হয়"))],
       [ln("shell", "proc", "to", state="hot", label=("SIGTERM first", "আগে SIGTERM"))],
       [("kill first, kill -9 last", "আগে kill, kill -9 শেষে"), None],
       note=("warn", "SIGKILL cannot be caught, so use <code>kill -9</code> last.",
             "SIGKILL আটকানো যায় না, তাই <code>kill -9</code> শেষে ব্যবহার করুন।")),

    st(("Memory", "মেমোরি"),
       ("A process vanishes with no error", "প্রসেস কোনো এরর ছাড়া উধাও"),
       [("When RAM runs out, the kernel may kill a process to free memory. The process can vanish without any error in its own log.",
         "RAM ফুরিয়ে গেলে কার্নেল জায়গা খালি করতে কোনো প্রসেস মেরে ফেলতে পারে। প্রসেসটি নিজের লগে কোনো এরর না রেখেই উধাও হতে পারে।"),
        ("Look for an out-of-memory message with <code>dmesg</code>.",
         "<code>dmesg</code> দিয়ে out-of-memory বার্তা খুঁজুন।")],
       [sh("ram", "warn", ("RAM runs out", "RAM ফুরিয়ে যায়"), x=130, y=162), sh("oom", "warn", ("kills a process", "প্রসেস মারে")),
        sh("proc", "dim", ("gone, no error", "উধাও, এরর নেই"))],
       [ln("ram", "oom", "to", state="warn"), ln("oom", "proc", "to", state="warn")],
       [("dmesg", "dmesg"), None],
       note=("warn", "A model server that vanishes with no error is often such a case.",
             "মডেল সার্ভার কোনো এরর ছাড়া উধাও হলে প্রায়ই এটাই কারণ।")),

    st(("Secrets", "সিক্রেট"),
       ("Keep secrets out of logs", "লগে সিক্রেট নয়"),
       [("Environment variables pass settings, including secrets, to a process.",
         "এনভায়রনমেন্ট ভেরিয়েবল প্রসেসে সেটিংস পাঠায়, সিক্রেটসহ।"),
        ("Never print them into logs.",
         "এগুলো কখনো লগে প্রিন্ট করবেন না।")],
       [sh("env", "hot", ("can hold secrets", "সিক্রেট থাকতে পারে"), x=200, y=162), sh("log", "warn", ("not here", "এখানে নয়"), x=560, y=162)],
       [ln("env", "log", "to", state="warn")],
       [None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Read the machine first, then fix it.",
         "আগে মেশিন দেখুন, তারপর ঠিক করুন।")],
       [sh("shell", "hot"), sh("srv", "hot")],
       [ln("shell", "srv", "to", state="hot")],
       [None, None],
       points=[("Read the machine first with commands like <code>nvidia-smi</code>, <code>df -h</code> and <code>free -h</code>, then fix it.",
                "আগে <code>nvidia-smi</code>, <code>df -h</code>, <code>free -h</code>-এর মতো কমান্ডে মেশিন দেখুন, তারপর ঠিক করুন।"),
               ("Use kill first, which sends SIGTERM. Use <code>kill -9</code> last.",
                "আগে kill দিন, যা SIGTERM পাঠায়। <code>kill -9</code> শেষ উপায়।"),
               ("Never print environment variables into logs, because they can hold secrets.",
                "এনভায়রনমেন্ট ভেরিয়েবল কখনো লগে প্রিন্ট করবেন না, কারণ তাতে সিক্রেট থাকতে পারে।"),
               ("If a model server vanishes with no error, look for an out-of-memory message with <code>dmesg</code>.",
                "মডেল সার্ভার কোনো এরর ছাড়া উধাও হলে <code>dmesg</code> দিয়ে out-of-memory বার্তা খুঁজুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
