"""Deploying and Operating AI Systems · 12 DevSecOps and platform security: security checks in the pipeline, and limits on the keys, model files and agent tools that an AI system adds.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Shift left   Body: "DevSecOps puts security checks into the same pipeline as the tests." "find a security problem when a change is made, not after it ships. The checks run in CI next to the tests."
  2 Secrets      "Keep API keys and passwords in a secrets manager ... and inject them when the service starts. Never in Git, never in an image."
  3 Privilege    "Each service gets its own identity with only the access it needs: IAM roles in the cloud, RBAC in Kubernetes." Glossary: "Least privilege".
  4 Images       "Scan them for known vulnerabilities, keep a software bill of materials (SBOM), pin versions, and pull only from registries you trust."
  5 Network      "Deny traffic by default and open only what a service needs (a Kubernetes NetworkPolicy can do this, with a network plugin that enforces it)." "An agent that can reach the whole internet or your internal network can leak data."
  6 Model file   "Some model file formats, such as Python's pickle, can run code when you load them. Load weights only from sources you trust, and prefer ... safetensors." Glossary: "A model file format that holds only tensors".
  7 Tools        Warning: "Treat an agent's tools as an attack surface. Prompt injection can make a model call a tool you gave it. Limit what each tool can do, log every call, and ask a human before any action that cannot be undone."
  8 Remember     The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("ci", "tool", ("Checks in CI", "CI-তে চেক"), 150, 160),
    node("svc", "service", ("Service", "সার্ভিস"), 620, 160),
    node("vault", "key", ("Secrets manager", "সিক্রেট ম্যানেজার"), 330, 160),
    node("git", "file", ("Git or image", "Git বা ইমেজ"), 330, 60),
    node("lp", "shield", ("Least privilege", "লিস্ট প্রিভিলেজ"), 330, 160),
    node("img", "file", ("Images and dependencies", "ইমেজ আর ডিপেন্ডেন্সি"), 330, 160),
    node("np", "shield", ("NetworkPolicy", "NetworkPolicy"), 330, 160),
    node("pk", "file", ("pickle", "pickle"), 200, 70),
    node("stz", "file", ("safetensors", "safetensors"), 200, 250),
    node("agent", "model", ("Agent", "এজেন্ট"), 150, 160),
    node("tool", "tool", ("Tool", "টুল"), 620, 160),
    node("human", "user", ("Human", "মানুষ"), 380, 260),
]

METRICS = [
    ("Checks", "চেক"),
    ("Keys", "কী"),
    ("Model file", "মডেল ফাইল"),
    ("Undoable action", "যা ফেরানো যায় না"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Shift left", "আগেই চেক"),
       ("Find problems when a change is made", "পরিবর্তনের সময়ই সমস্যা ধরুন"),
       [("DevSecOps puts security checks into the same pipeline as the tests.",
         "DevSecOps নিরাপত্তার চেক টেস্টের একই পাইপলাইনে রাখে।"),
        ("The idea is to find a security problem when a change is made, not after it ships.",
         "ধারণাটা হলো নিরাপত্তার সমস্যা পরিবর্তনের সময়ই ধরা, ডিপ্লয়ের পরে নয়।")],
       [sh("ci", "hot", ("next to the tests", "টেস্টের পাশেই")), sh("svc", "dim", ("after it ships", "ডিপ্লয়ের পরে"))],
       [ln("ci", "svc", "to", state="dim")],
       [("in CI", "CI-তে"), None, None, None]),

    st(("Secrets", "সিক্রেট"),
       ("Keys stay out of Git and images", "key থাকে Git আর ইমেজের বাইরে"),
       [("Keep API keys and passwords in a secrets manager, and inject them when the service starts.",
         "API key আর পাসওয়ার্ড রাখুন সিক্রেট ম্যানেজারে, আর সার্ভিস চালুর সময় সেগুলো দিন।"),
        ("Never in Git, never in an image.",
         "কখনো Git-এ নয়, কখনো ইমেজে নয়।")],
       [sh("vault", "hot"), sh("svc", "hot", ("gets them at start", "চালুর সময় পায়")), sh("git", "warn", ("never", "কখনো নয়"))],
       [ln("vault", "svc", "to", state="hot")],
       [None, ("secrets manager", "সিক্রেট ম্যানেজার"), None, None],
       note=("warn", "A Kubernetes Secret is only base64-encoded unless you turn on encryption at rest, so limit who can read it.",
             "এনক্রিপশন অ্যাট রেস্ট চালু না করলে Kubernetes Secret শুধু base64-এনকোড করা থাকে, তাই কে পড়তে পারে তা সীমিত করুন।")),

    st(("Privilege", "প্রিভিলেজ"),
       ("Each service gets only the access it needs", "প্রতিটি সার্ভিস শুধু দরকারি অ্যাক্সেস পায়"),
       [("Each service gets its own identity with only the access it needs.",
         "প্রতিটি সার্ভিস নিজের আলাদা পরিচয় পায়, শুধু ততটুকু অ্যাক্সেসসহ যতটুকু লাগে।"),
        ("That means IAM roles in the cloud and RBAC in Kubernetes.",
         "ক্লাউডে এর মানে IAM role, আর Kubernetes-এ RBAC।")],
       [sh("lp", "hot", ("nothing more", "তার বেশি নয়")), sh("svc", "hot", ("its own identity", "নিজের পরিচয়"))],
       [ln("lp", "svc", "to", state="hot")],
       [None, None, None, None]),

    st(("Images", "ইমেজ"),
       ("Scan images and dependencies", "ইমেজ আর ডিপেন্ডেন্সি স্ক্যান করুন"),
       [("Scan images and dependencies for known vulnerabilities, and keep a software bill of materials (SBOM).",
         "ইমেজ আর ডিপেন্ডেন্সি স্ক্যান করুন জানা দুর্বলতার জন্য, আর একটা SBOM (software bill of materials) রাখুন।"),
        ("Pin versions, and pull only from registries you trust.",
         "ভার্সন পিন করুন, আর শুধু বিশ্বস্ত রেজিস্ট্রি থেকে নিন।")],
       [sh("img", "hot", ("scan, SBOM, pin", "স্ক্যান, SBOM, পিন")), sh("svc", "hot")],
       [ln("img", "svc", "to", state="hot")],
       [None, None, None, None]),

    st(("Network", "নেটওয়ার্ক"),
       ("Deny traffic by default", "ডিফল্টে ট্রাফিক বন্ধ"),
       [("Deny traffic by default and open only what a service needs. A Kubernetes NetworkPolicy can do this, with a network plugin that enforces it.",
         "ডিফল্টে ট্রাফিক বন্ধ রাখুন আর সার্ভিসের দরকারটুকুই খুলুন। Kubernetes NetworkPolicy এটা পারে, তবে এমন নেটওয়ার্ক প্লাগইন লাগে যা এটা প্রয়োগ করে।"),
        ("An agent that can reach the whole internet or your internal network can leak data.",
         "যে এজেন্ট পুরো ইন্টারনেটে বা আপনার অভ্যন্তরীণ নেটওয়ার্কে পৌঁছাতে পারে, সে ডেটা ফাঁস করতে পারে।")],
       [sh("np", "hot", ("deny by default", "ডিফল্টে বন্ধ")), sh("svc", "hot", ("only what it needs", "শুধু দরকারটুকু"))],
       [ln("np", "svc", "to", state="hot")],
       [None, None, None, None]),

    st(("Model file", "মডেল ফাইল"),
       ("The model file is code too", "মডেল ফাইলও কোড"),
       [("Some model file formats, such as Python's pickle, can run code when you load them.",
         "কিছু মডেল ফাইল ফরম্যাট, যেমন Python-এর pickle, লোড করার সময় কোড চালাতে পারে।"),
        ("Load weights only from sources you trust, and prefer safetensors, which holds only tensors.",
         "ওয়েট শুধু বিশ্বস্ত উৎস থেকে নিন, আর safetensors বেছে নিন, যা শুধু টেন্সর রাখে।")],
       [sh("pk", "warn", ("can run code", "কোড চালাতে পারে")), sh("stz", "hot", ("only tensors", "শুধু টেন্সর")), sh("svc", "hot", ("loads weights", "ওয়েট লোড করে"))],
       [ln("pk", "svc", "to", state="warn"), ln("stz", "svc", "to", state="hot")],
       [None, None, ("safetensors", "safetensors"), None]),

    st(("Tools", "টুল"),
       ("An agent's tools are an attack surface", "এজেন্টের টুল আক্রমণের জায়গা"),
       [("Prompt injection can make a model call a tool you gave it. Limit what each tool can do, and log every call.",
         "প্রম্পট ইনজেকশন মডেলকে আপনার দেওয়া টুল কল করাতে পারে। প্রতিটি টুল কী করতে পারবে তা সীমিত করুন, আর প্রতিটি কল লগ করুন।"),
        ("Ask a human before any action that cannot be undone.",
         "যে কাজ ফেরানো যায় না, তার আগে মানুষের অনুমতি নিন।")],
       [sh("agent", "warn", ("prompt injection", "প্রম্পট ইনজেকশন")), sh("tool", "hot", ("limited, logged", "সীমিত, লগ করা")), sh("human", "hot", ("asked first", "আগে জিজ্ঞাসা"))],
       [ln("agent", "tool", "to", state="warn"), ln("agent", "human", "to", state="hot"), ln("human", "tool", "to", state="hot")],
       [None, None, None, ("ask a human", "মানুষকে জিজ্ঞাসা")],
       note=("warn", "Part 12 covers this in depth.", "Part ১২-তে এটা বিস্তারিত আছে।")),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Four rules cover the section.", "চারটা নিয়মে পুরো সেকশন।")],
       [sh("ci", "hot"), sh("vault", "hot"), sh("stz", "hot"), sh("tool", "hot"), sh("human", "hot")],
       [],
       [("in CI", "CI-তে"), ("not in Git", "Git-এ নয়"), ("safetensors", "safetensors"), ("ask a human", "মানুষকে জিজ্ঞাসা")],
       points=[("Find security problems when a change is made, not after it ships.", "নিরাপত্তার সমস্যা পরিবর্তনের সময়ই ধরুন, ডিপ্লয়ের পরে নয়।"),
               ("Never put API keys in Git or in an image.", "API key কখনো Git-এ বা ইমেজে রাখবেন না।"),
               ("Load model weights only from sources you trust, and prefer safetensors.", "মডেলের ওয়েট শুধু বিশ্বস্ত উৎস থেকে নিন, আর safetensors বেছে নিন।"),
               ("Limit each tool, log every call, and ask a human before any action that cannot be undone.", "প্রতিটি টুল সীমিত করুন, প্রতিটি কল লগ করুন, আর যা ফেরানো যায় না তার আগে মানুষের অনুমতি নিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
