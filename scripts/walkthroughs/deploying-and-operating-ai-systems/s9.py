"""Part 14 · 09 Cloud platforms and managed AI services: three levels of renting, and the basics that catch beginners.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Levels    Body: "With AI, you can rent at three levels. Each level is a trade between a fast start and more control." Table: Hosted model API, Managed platform, Rented GPUs.
  2 Hosted    Table row: "The model company's own API", "Your prompts and your data", "The fastest start. You depend on their limits and prices."
  3 Managed   Table row: "Models sit behind your cloud account's identity, private networking and billing.", "Access, quotas, networking and cost".
  4 GPUs      Table row: "Virtual machines or Kubernetes nodes with GPUs", "The whole serving stack", "The most control and the most work".
  5 IAM       "IAM decides who and what may call a model or read a bucket. Give each service its own role with the least access it needs."
  6 Region    "Regions matter for latency, data-residency rules and which models are offered." "Keep the model, the vector database and the app in one region when you can."
  7 Quota     "Quotas cap requests or tokens per minute in each region. Ask for an increase before a launch, not during it."
  8 Egress    "Egress, data that leaves the cloud, is billed."
  9 Remember  Start here: "A hosted API starts fastest. Rented GPUs give the most control and the most work." and the remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("app", "user", ("Your app", "আপনার অ্যাপ"), 100, 162),
    node("api", "service", ("Hosted model API", "হোস্টেড মডেল API"), 340, 60),
    node("plat", "service", ("Managed platform", "ম্যানেজড প্ল্যাটফর্ম"), 340, 162),
    node("gpu", "server", ("Rented GPUs", "ভাড়া করা GPU"), 340, 265),
    node("iam", "shield", ("IAM role", "IAM রোল"), 610, 162),
    node("bucket", "storage", ("Bucket", "বাকেট"), 610, 60),
    node("vdb", "database", ("Vector database", "ভেক্টর ডেটাবেস"), 610, 265),
    node("quota", "clock", ("Quota per minute", "প্রতি মিনিটের কোটা"), 610, 162),
    node("out", "browser", ("Outside the cloud", "ক্লাউডের বাইরে"), 610, 60),
]

METRICS = [
    ("Start", "শুরু"),
    ("Control", "নিয়ন্ত্রণ"),
    ("Work", "কাজ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Levels", "স্তর"),
       ("Three levels of renting", "ভাড়ার তিন স্তর"),
       [("With AI, you can rent at three levels: a hosted model API, a managed platform, or rented GPUs.",
         "AI-এর জন্য তিন স্তরে ভাড়া নেওয়া যায়: হোস্টেড মডেল API, ম্যানেজড প্ল্যাটফর্ম, বা ভাড়া করা GPU।"),
        ("Each level is a trade between a fast start and more control.",
         "প্রতিটি স্তরে দ্রুত শুরু আর বেশি নিয়ন্ত্রণের মধ্যে একটা বেছে নিতে হয়।")],
       [sh("app", "hot"), sh("api", "hot"), sh("plat", "hot"), sh("gpu", "hot")],
       [ln("app", "api", "to", state="hot"), ln("app", "plat", "to", state="hot"), ln("app", "gpu", "to", state="hot")],
       [None, None, None]),

    st(("Hosted", "হোস্টেড"),
       ("Hosted model API", "হোস্টেড মডেল API"),
       [("It is the model company's own service. You send prompts and data.",
         "এটা মডেল কোম্পানির নিজের সার্ভিস। আপনি প্রম্পট আর ডেটা পাঠান।"),
        ("It is the fastest start, but you depend on their limits and prices.",
         "এটা সবচেয়ে দ্রুত শুরু, কিন্তু আপনি তাদের সীমা আর দামের ওপর নির্ভর করেন।")],
       [sh("app", "hot", ("prompts and data", "প্রম্পট আর ডেটা")), sh("api", "hot", ("fastest start", "সবচেয়ে দ্রুত শুরু")), sh("plat", "dim"), sh("gpu", "dim")],
       [ln("app", "api", "to", state="hot")],
       [("fastest", "সবচেয়ে দ্রুত"), None, None]),

    st(("Managed", "ম্যানেজড"),
       ("Managed platform", "ম্যানেজড প্ল্যাটফর্ম"),
       [("A managed platform runs models behind your own cloud account's identity, private networking and billing.",
         "ম্যানেজড প্ল্যাটফর্ম আপনার ক্লাউড অ্যাকাউন্টের পরিচয়, প্রাইভেট নেটওয়ার্ক আর বিলিংয়ের ভেতরে মডেল চালায়।"),
        ("You manage access, quotas, networking and cost.",
         "আপনি অ্যাক্সেস, কোটা, নেটওয়ার্কিং আর খরচ সামলান।")],
       [sh("app", "hot"), sh("plat", "hot", ("your account's identity", "আপনার অ্যাকাউন্টের পরিচয়")), sh("api", "dim"), sh("gpu", "dim")],
       [ln("app", "plat", "to", state="hot")],
       [None, None, None]),

    st(("GPUs", "GPU"),
       ("Rented GPUs", "ভাড়া করা GPU"),
       [("Rented GPUs are virtual machines or Kubernetes nodes with GPUs.",
         "ভাড়া করা GPU মানে GPU সহ ভার্চুয়াল মেশিন বা Kubernetes নোড।"),
        ("You manage the whole serving stack: the most control and the most work.",
         "আপনি পুরো সার্ভিং স্ট্যাক সামলান: নিয়ন্ত্রণ সবচেয়ে বেশি, কাজও সবচেয়ে বেশি।")],
       [sh("app", "hot"), sh("gpu", "hot", ("whole serving stack", "পুরো সার্ভিং স্ট্যাক")), sh("api", "dim"), sh("plat", "dim")],
       [ln("app", "gpu", "to", state="hot")],
       [None, ("most", "সবচেয়ে বেশি"), ("most", "সবচেয়ে বেশি")]),

    st(("IAM", "IAM"),
       ("Identity and access management", "আইডেন্টিটি অ্যান্ড অ্যাক্সেস ম্যানেজমেন্ট"),
       [("IAM decides who and what may call a model or read a storage bucket.",
         "IAM ঠিক করে কে বা কোন সার্ভিস মডেল কল করতে বা স্টোরেজ বাকেট পড়তে পারবে।"),
        ("Give each service its own role with the least access it needs.",
         "প্রতিটি সার্ভিসকে নিজের রোল দিন, ততটুকু অ্যাক্সেস সহ যতটুকু লাগে।")],
       [sh("plat", "hot", ("its own role", "নিজের রোল")), sh("iam", "hot", ("least access", "ন্যূনতম অ্যাক্সেস")), sh("bucket", "hot")],
       [ln("plat", "iam", "to", state="hot"), ln("iam", "bucket", "to", state="hot")],
       [None, None, None]),

    st(("Region", "রিজিয়ন"),
       ("Region: where the machines are", "রিজিয়ন: মেশিনগুলো যেখানে"),
       [("A region is the place where the cloud's machines are. It affects speed, data rules and which models you can use.",
         "রিজিয়ন হলো ক্লাউডের মেশিনগুলো যেখানে আছে সেই জায়গা। এটা গতি, ডেটা রাখার আইন আর কোন মডেল পাওয়া যাবে তাতে প্রভাব ফেলে।"),
        ("Keep the model, the vector database and the app in one region when you can.",
         "পারলে মডেল, ভেক্টর ডেটাবেস আর অ্যাপ এক রিজিয়নে রাখুন।")],
       [sh("app", "hot", ("one region", "এক রিজিয়ন")), sh("plat", "hot", ("one region", "এক রিজিয়ন")), sh("vdb", "hot", ("one region", "এক রিজিয়ন"))],
       [ln("app", "plat", "to", state="hot"), ln("plat", "vdb", "to", state="hot")],
       [None, None, None]),

    st(("Quota", "কোটা"),
       ("Quota: a cap per minute", "কোটা: প্রতি মিনিটের সীমা"),
       [("A quota is a cap on how many requests or tokens you can use per minute in a region.",
         "কোটা হলো কোনো রিজিয়নে প্রতি মিনিটে কত রিকোয়েস্ট বা টোকেন ব্যবহার করা যাবে, তার সীমা।"),
        ("Ask for a quota increase before a launch, not during it.",
         "লঞ্চের আগে কোটা বাড়ানোর অনুরোধ করুন, লঞ্চের সময় নয়।")],
       [sh("app", "hot"), sh("plat", "hot"), sh("quota", "warn", ("cap", "সীমা"))],
       [ln("app", "plat", "to", state="hot"), ln("plat", "quota", "to", state="warn")],
       [None, None, None],
       note=("tip", "Ask before the launch.", "লঞ্চের আগেই অনুরোধ করুন।")),

    st(("Egress", "ইগ্রেস"),
       ("Egress: data that leaves is billed", "ইগ্রেস: বাইরে যাওয়া ডেটার বিল"),
       [("Egress is data that leaves the cloud. The cloud bills you for it.",
         "ইগ্রেস হলো ক্লাউডের বাইরে যাওয়া ডেটা। এর জন্য ক্লাউড আপনাকে বিল করে।")],
       [sh("plat", "hot"), sh("out", "warn", ("billed", "বিল হয়"))],
       [ln("plat", "out", "to", state="warn")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A hosted API starts fastest. Rented GPUs give the most control and the most work.",
         "হোস্টেড API সবচেয়ে দ্রুত শুরু হয়। ভাড়া করা GPU-তে নিয়ন্ত্রণ সবচেয়ে বেশি, কাজও সবচেয়ে বেশি।")],
       [sh("app", "hot"), sh("api", "hot", ("fastest start", "সবচেয়ে দ্রুত শুরু")), sh("plat", "hot"), sh("gpu", "hot", ("most control", "সবচেয়ে বেশি নিয়ন্ত্রণ"))],
       [ln("app", "api", "to"), ln("app", "plat", "to"), ln("app", "gpu", "to")],
       [("fastest", "সবচেয়ে দ্রুত"), ("most", "সবচেয়ে বেশি"), ("most", "সবচেয়ে বেশি")],
       points=[("Give each service its own role with the least access it needs.",
                "প্রতিটি সার্ভিসকে নিজের রোল দিন, ততটুকু অ্যাক্সেস সহ যতটুকু লাগে।"),
               ("Ask for a quota increase before a launch, not during it.",
                "লঞ্চের আগে কোটা বাড়ানোর অনুরোধ করুন, লঞ্চের সময় নয়।"),
               ("Keep the model, the vector database and the app in one region when you can.",
                "পারলে মডেল, ভেক্টর ডেটাবেস আর অ্যাপ এক রিজিয়নে রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
