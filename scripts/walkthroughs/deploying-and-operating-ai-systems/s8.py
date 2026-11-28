"""Part 14 · 08 Infrastructure as code: files you review and run again replace clicking in a console; plan, then apply.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Files     Body: "IaC describes servers, networks and databases in files that you review and version like code." Start here: "Files that you review, version and run again, instead of clicking in a cloud console. The same files give the same result."
  2 Tools     Table: Terraform "Declarative: you describe the end state", "Creating cloud resources: GPU nodes, networks, buckets, databases"; Ansible "Configuring machines that already exist: drivers, packages, services", "over SSH with no agent on the machine". OpenTofu is its open-source fork.
  3 Plan      Body: "Terraform compares your files with its recorded state and with the real resources, shows a plan". Start here: "Plan shows what would change."
  4 Apply     Body: "changes only the difference when you apply". "terraform apply # make the change, after you approve it".
  5 State     Body: "The state can hold sensitive values and is shared by the team, so keep it in a remote backend with locking, never in Git." Start here: "shared storage, one change at a time".
  6 Drift     Warning: "If someone changes a resource by hand, the files no longer match reality, and terraform plan shows the difference."
  7 Remember  Warning: "GPUs are expensive and terraform destroy is as easy as terraform apply, so tag every resource with an owner and an expiry, and set a budget alert." The remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("files", "file", ("Files in Git", "Git-এর ফাইল"), 110, 162),
    node("tf", "tool", ("Terraform", "Terraform"), 330, 162),
    node("state", "storage", ("State", "স্টেট"), 330, 50),
    node("cloud", "server", ("GPU nodes", "GPU নোড"), 580, 162),
    node("ans", "tool", ("Ansible", "Ansible"), 330, 282),
    node("hand", "user", ("Someone by hand", "হাতে বদল"), 580, 282),
    node("lock", "lock", ("Remote backend", "remote backend"), 580, 50),
    node("tags", "note", ("Owner and expiry tags", "মালিক আর মেয়াদের ট্যাগ"), 140, 282),
]

METRICS = [
    ("Result", "ফল"),
    ("Change", "বদল"),
    ("State", "স্টেট"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Files", "ফাইল"),
       ("Files replace clicking", "ফাইল, ক্লিকের বদলে"),
       [("IaC describes servers, networks and databases in files that you review and version like code.",
         "IaC সার্ভার, নেটওয়ার্ক আর ডেটাবেসকে ফাইলে লিখে রাখে, যা কোডের মতো রিভিউ ও ভার্সন করা যায়।"),
        ("The same files give the same result each time.",
         "একই ফাইল প্রতিবার একই ফল দেয়।")],
       [sh("files", "hot", ("review and version", "রিভিউ আর ভার্সন")), sh("tf", "hot"), sh("cloud", "hot", ("same every time", "প্রতিবার একই"))],
       [ln("files", "tf", "to", state="hot"), ln("tf", "cloud", "to", state="hot")],
       [("same", "একই"), None, None]),

    st(("Tools", "টুল"),
       ("Terraform and Ansible", "Terraform আর Ansible"),
       [("Terraform is declarative: you describe the end state, and it creates cloud resources such as GPU nodes, networks, buckets and databases. OpenTofu is its open-source fork.",
         "Terraform ডিক্লারেটিভ: আপনি শেষ অবস্থাটা বর্ণনা করেন, আর সেটা GPU নোড, নেটওয়ার্ক, বাকেট, ডেটাবেসের মতো ক্লাউড রিসোর্স বানায়। OpenTofu তার ওপেন-সোর্স ফর্ক।"),
        ("Ansible sets up drivers, packages and services on machines that already exist, over SSH, with no agent on the machine.",
         "Ansible আগে থেকে থাকা মেশিনে ড্রাইভার, প্যাকেজ আর সার্ভিস সেট আপ করে, SSH দিয়ে, মেশিনে কোনো এজেন্ট ছাড়া।")],
       [sh("tf", "hot", ("end state", "শেষ অবস্থা")), sh("ans", "hot", ("no agent", "এজেন্ট নেই")), sh("cloud", "hot")],
       [ln("tf", "cloud", "to", state="hot"), ln("ans", "cloud", "to", state="hot")],
       [None, None, None]),

    st(("Plan", "প্ল্যান"),
       ("Plan shows what would change", "প্ল্যান দেখায় কী বদলাবে"),
       [("Terraform compares your files with its recorded state and with the real resources, and shows a plan.",
         "Terraform আপনার ফাইলকে তার রেকর্ড করা স্টেট আর আসল রিসোর্সের সঙ্গে মেলায়, আর একটা প্ল্যান দেখায়।"),
        ("Run terraform plan to see the change.",
         "বদল দেখতে terraform plan চালান।")],
       [sh("files", "hot"), sh("state", "hot", ("recorded", "রেকর্ড করা")), sh("tf", "hot", ("plan", "প্ল্যান")), sh("cloud", "hot", ("real resources", "আসল রিসোর্স"))],
       [ln("files", "tf", "to", state="hot"), ln("state", "tf", "to", state="hot"), ln("cloud", "tf", "to", state="hot")],
       [None, ("plan", "প্ল্যান"), None]),

    st(("Apply", "অ্যাপ্লাই"),
       ("Apply makes the change", "অ্যাপ্লাই বদলটা করে"),
       [("When you apply, Terraform changes only the difference.",
         "অ্যাপ্লাই করলে Terraform শুধু পার্থক্যটুকু বদলায়।"),
        ("Run terraform apply to make the change, after you approve it.",
         "আপনি মেনে নিলে বদলটা করতে terraform apply চালান।")],
       [sh("tf", "hot", ("after you approve", "আপনি মেনে নিলে")), sh("cloud", "hot", ("only the difference", "শুধু পার্থক্য"))],
       [ln("tf", "cloud", "to", state="hot")],
       [None, ("only the difference", "শুধু পার্থক্য"), None]),

    st(("State", "স্টেট"),
       ("Keep state in a remote backend", "স্টেট রাখুন remote backend-এ"),
       [("The state can hold sensitive values, and the team shares it.",
         "স্টেটে সংবেদনশীল মান থাকতে পারে, আর পুরো টিম এটা ভাগ করে।"),
        ("Keep it in a remote backend with locking, shared storage with one change at a time, never in Git.",
         "স্টেট লকিংসহ remote backend-এ, মানে শেয়ার করা স্টোরেজে, যেখানে একবারে একটাই বদল, রাখুন; কখনও Git-এ নয়।")],
       [sh("state", "hot", ("sensitive values", "সংবেদনশীল মান")), sh("lock", "hot", ("one change at a time", "একবারে একটাই বদল")), sh("files", "warn", ("never state in Git", "স্টেট কখনও Git-এ নয়"))],
       [ln("state", "lock", "to", state="hot")],
       [None, None, ("remote, locked", "remote, লকসহ")]),

    st(("Drift", "ড্রিফট"),
       ("Drift: files no longer match", "ড্রিফট: ফাইল আর মেলে না"),
       [("If someone changes a resource by hand, the files no longer match reality. This is drift.",
         "কেউ হাতে কোনো রিসোর্স বদলালে ফাইল আর বাস্তব অবস্থা মেলে না। একে বলে ড্রিফট।"),
        ("terraform plan shows the difference.",
         "terraform plan পার্থক্যটা দেখায়।")],
       [sh("hand", "warn", ("by hand", "হাতে")), sh("cloud", "warn"), sh("tf", "hot", ("plan", "প্ল্যান")), sh("files", "dim")],
       [ln("hand", "cloud", "to", state="warn"), ln("cloud", "tf", "to", state="hot")],
       [None, ("no longer match", "আর মেলে না"), None],
       note=("warn", "Drift is when the files and reality differ.", "ড্রিফট মানে ফাইল আর বাস্তব অবস্থা আলাদা।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("GPUs cost a lot, and terraform destroy is as easy as apply.",
         "GPU দামি, আর terraform destroy চালানো apply-এর মতোই সহজ।")],
       [sh("files", "hot"), sh("tf", "hot"), sh("cloud", "hot", ("tagged", "ট্যাগ দেওয়া")), sh("tags", "hot")],
       [ln("files", "tf", "to"), ln("tf", "cloud", "to")],
       [None, None, None],
       points=[("Files replace clicking in a console, and they give the same result each time.",
                "কনসোলে ক্লিক করার বদলে ফাইল ব্যবহার হয়, আর প্রতিবার একই ফল দেয়।"),
               ("Run terraform plan to see the change, then terraform apply to make it.",
                "বদল দেখতে terraform plan চালান, তারপর বদলটা করতে terraform apply চালান।"),
               ("Keep state in a remote backend with locking, never in Git.",
                "স্টেট লকিংসহ remote backend-এ রাখুন, কখনও Git-এ নয়।"),
               ("Tag every resource with an owner and an expiry.",
                "প্রতিটি রিসোর্সে মালিক আর মেয়াদের ট্যাগ দিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
