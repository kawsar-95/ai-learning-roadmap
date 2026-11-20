"""Part 17 · 07 CI/CD and GitOps: a pipeline for an AI service, and Git as the record of what runs.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 CI/CD      Start here: "CI/CD builds and tests every change automatically and ships every change that passes. For an AI system, the tests also check the model's behaviour, and GitOps makes Git the record of what runs." Body: "Continuous integration (CI) builds and tests every change automatically. Continuous delivery or deployment (CD) ships a passing change to an environment."
  2 Pipeline   "A typical pipeline for an AI service has these stages:" and the four bullets: lint and unit tests; build the container image and tag it with the commit; run a small evaluation set ... fail the build when the score drops below a baseline; deploy to staging, check it, then promote it.
  3 Gate       The third bullet, and the word "Baseline": "The score you compare against. A new score below it means things got worse."
  4 Judge      The "warn" callout: "An LLM judge in CI is noisy. Run it on a fixed set, pin the judge model, and compare with a baseline measured on main instead of a single magic number."; word: "LLM judge = A language model that scores answers."
  5 GitOps     Body, "GitOps": "In GitOps the Git repository is the source of truth for what runs. A controller inside the cluster, such as Argo CD or Flux, compares the cluster with the repository and removes the difference."
  6 Merge      "To deploy, you merge a change. To roll back, you revert it."
  7 Secrets    The "good" callout: "Keep secrets out of the repository. Store a reference, or an encrypted value, in Git, and keep the secret itself in a secrets manager."
  8 Remember   The idea and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("change", "file", ("Change", "পরিবর্তন"), 110, 162),
    node("baseline", "chart", ("Baseline", "বেসলাইন"), 110, 162),
    node("git", "storage", ("Git repo", "Git রিপো"), 110, 162),
    node("test", "tool", ("Tests", "টেস্ট"), 380, 162),
    node("evals", "shield", ("Evals", "ইভ্যাল"), 380, 162),
    node("judge", "model", ("LLM judge", "LLM জাজ"), 380, 162),
    node("ctrl", "tool", ("Controller", "কন্ট্রোলার"), 380, 162),
    node("build", "service", ("Image", "ইমেজ"), 650, 162),
    node("staging", "server", ("Staging", "Staging"), 650, 162),
    node("cluster", "server", ("Cluster", "ক্লাস্টার"), 650, 162),
    node("vault", "lock", ("Secrets manager", "সিক্রেটস ম্যানেজার"), 650, 162),
]

METRICS = [
    ("Build", "বিল্ড"),
    ("Deploy", "ডিপ্লয়"),
    ("Roll back", "রোলব্যাক"),
]

CAPTION = (
    "CI/CD builds and tests every change automatically and ships every change that passes. For an AI system, the tests also check the model's behavior, and GitOps makes Git the record of what runs.",
    "CI/CD প্রতিটি পরিবর্তন নিজে নিজে বিল্ড আর টেস্ট করে, আর যে পরিবর্তন পাশ করে তা ডিপ্লয় করে। AI সিস্টেমে টেস্টে মডেলের আচরণও যাচাই হয়, আর GitOps-এ কী চলবে তার রেকর্ড থাকে Git-এ।",
)

STEPS = [
    st(("CI/CD", "CI/CD"),
       ("Build, test, ship", "বিল্ড, টেস্ট, ডিপ্লয়"),
       [("CI/CD builds and tests every change automatically and ships every change that passes. For an AI system, the tests also check the model's behavior, and GitOps makes Git the record of what runs.",
         "CI/CD প্রতিটি পরিবর্তন নিজে নিজে বিল্ড আর টেস্ট করে, আর যে পরিবর্তন পাশ করে তা ডিপ্লয় করে। AI সিস্টেমে টেস্টে মডেলের আচরণও যাচাই হয়, আর GitOps-এ কী চলবে তার রেকর্ড থাকে Git-এ।"),
        ("Continuous integration (CI) builds and tests every change automatically. Continuous delivery or deployment (CD) ships a passing change to an environment.",
         "কন্টিনিউয়াস ইন্টিগ্রেশন (CI) প্রতিটি পরিবর্তন নিজে নিজে বিল্ড আর টেস্ট করে। কন্টিনিউয়াস ডেলিভারি বা ডিপ্লয়মেন্ট (CD) টেস্টে পাশ করা পরিবর্তন কোনো এনভায়রনমেন্টে পাঠিয়ে দেয়।")],
       [sh("change", "hot"), sh("test", "hot", ("builds and tests", "বিল্ড আর টেস্ট")), sh("staging", "hot", ("an environment", "একটি এনভায়রনমেন্ট"))],
       [ln("change", "test", "to", state="hot", label=("CI", "CI")), ln("test", "staging", "to", state="hot", label=("CD", "CD"))],
       [None, None, None]),

    st(("Pipeline", "পাইপলাইন"),
       ("A pipeline for an AI service", "AI সার্ভিসের পাইপলাইন"),
       [("A typical pipeline for an AI service has these stages:",
         "AI সার্ভিসের পাইপলাইনে সাধারণত থাকে:")],
       [sh("change", "hot", y=75), sh("test", "hot", ("lint, unit tests", "লিন্ট, ইউনিট টেস্ট"), y=75), sh("build", "hot", ("tagged with commit", "কমিট ট্যাগ"), y=75),
        sh("evals", "hot", ("a small eval set", "ছোট ইভ্যাল সেট"), x=650, y=250), sh("staging", "hot", ("check, then promote", "দেখে, তারপর তোলা"), x=380, y=250)],
       [ln("change", "test", "to", state="hot"), ln("test", "build", "to", state="hot"), ln("build", "evals", "to", state="hot"), ln("evals", "staging", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Lint and run the unit tests.",
                 "লিন্ট আর ইউনিট টেস্ট চালানো।"),
                ("+", "Build the container image and tag it with the commit.",
                 "কমিট ট্যাগ দিয়ে কনটেইনার ইমেজ বিল্ড করা।"),
                ("+", "Run a small evaluation set against the prompt, the model version and the retrieval settings. Fail the build when the score drops below a baseline.",
                 "প্রম্পট, মডেল ভার্সন আর রিট্রিভাল সেটিংসের ওপর একটা ছোট ইভ্যাল সেট চালানো; স্কোর বেসলাইনের নিচে নামলে বিল্ড ফেল করানো।"),
                ("+", "Deploy to staging, check it, then promote it.",
                 "staging-এ ডিপ্লয় করে দেখে নিয়ে প্রোডাকশনে তোলা।")]),

    st(("Gate", "গেট"),
       ("Fail below the baseline", "বেসলাইনের নিচে ফেল"),
       [("Run a small evaluation set against the prompt, the model version and the retrieval settings.",
         "প্রম্পট, মডেল ভার্সন আর রিট্রিভাল সেটিংসের ওপর একটা ছোট ইভ্যাল সেট চালান।"),
        ("Fail the build when the score drops below the baseline: a new score below it means things got worse.",
         "ইভ্যাল স্কোর বেসলাইনের নিচে নামলে বিল্ড ফেল করান: নতুন স্কোর এর নিচে নামলে বোঝা যায় অবস্থা খারাপ হয়েছে।")],
       [sh("baseline", "hot", ("the score to compare", "তুলনার স্কোর")), sh("evals", "hot", ("a small fixed set", "ছোট নির্দিষ্ট সেট")), sh("build", "warn", ("fails if below", "নিচে নামলে ফেল"))],
       [ln("baseline", "evals", "to", state="hot"), ln("evals", "build", "to", state="warn", label=("fail", "ফেল"))],
       [("Fails below baseline", "বেসলাইনের নিচে ফেল"), None, None]),

    st(("Judge", "জাজ"),
       ("A noisy judge", "এলোমেলো জাজ"),
       [("An LLM judge is a language model that scores answers. In CI it is noisy.",
         "LLM জাজ হলো যে ল্যাঙ্গুয়েজ মডেল উত্তরের স্কোর দেয়। CI-তে সে কিছুটা এলোমেলো ফল দেয়।"),
        ("Run it on a fixed set, pin the judge model, and compare with a baseline measured on main instead of a single magic number.",
         "নির্দিষ্ট একটা সেটে চালান, জাজ মডেল পিন করুন, আর একটা জাদুর সংখ্যার বদলে main-এ মাপা বেসলাইনের সাথে তুলনা করুন।")],
       [sh("evals", "hot", ("a fixed set", "নির্দিষ্ট সেট"), x=110), sh("judge", "warn", ("pin the judge model", "জাজ মডেল পিন করুন")), sh("baseline", "hot", ("measured on main", "main-এ মাপা"), x=650)],
       [ln("evals", "judge", "to", state="hot"), ln("judge", "baseline", "to", state="warn")],
       [None, None, None]),

    st(("GitOps", "GitOps"),
       ("Git is the source of truth", "Git-ই সত্যের উৎস"),
       [("In GitOps the Git repository is the source of truth for what runs.",
         "GitOps-এ Git রিপোজিটরিই সত্যের উৎস: কী চলবে তা সেখানে লেখা থাকে।"),
        ("A controller inside the cluster, such as Argo CD or Flux, compares the cluster with the repository and removes the difference.",
         "ক্লাস্টারের ভেতরের একটা কন্ট্রোলার (Argo CD বা Flux) ক্লাস্টারের সাথে রিপোজিটরি মিলিয়ে তফাত মিটিয়ে দেয়।")],
       [sh("git", "hot", ("source of truth", "সত্যের উৎস")), sh("ctrl", "hot", ("removes the difference", "তফাত মিটিয়ে দেয়")), sh("cluster", "hot", ("what runs", "যা চলছে"))],
       [ln("git", "ctrl", "to", state="hot"), ln("ctrl", "cluster", "to", state="hot")],
       [None, None, None]),

    st(("Merge", "মার্জ"),
       ("Merge to deploy, revert to roll back", "ডিপ্লয় মার্জে, রোলব্যাক revert-এ"),
       [("To deploy, you merge a change. To roll back, you revert it.",
         "ডিপ্লয় করতে পরিবর্তন মার্জ করুন, রোলব্যাক করতে সেটা revert করুন।")],
       [sh("change", "hot", ("a merge", "একটি মার্জ")), sh("git", "hot", x=380), sh("cluster", "hot")],
       [ln("change", "git", "to", state="hot", label=("merge", "মার্জ")), ln("git", "cluster", "to", state="hot")],
       [None, ("Merge a change", "পরিবর্তন মার্জ"), ("Revert it", "revert করুন")]),

    st(("Secrets", "সিক্রেট"),
       ("Secrets stay out of Git", "সিক্রেট Git-এর বাইরে"),
       [("Keep secrets out of the repository. Store a reference, or an encrypted value, in Git, and keep the secret itself in a secrets manager.",
         "সিক্রেট রিপোজিটরিতে রাখবেন না। Git-এ একটি রেফারেন্স বা এনক্রিপ্ট করা মান রাখুন, আর সিক্রেট নিজে রাখুন একটি সিক্রেটস ম্যানেজারে।")],
       [sh("git", "hot", ("a reference", "একটি রেফারেন্স")), sh("vault", "hot", ("the secret itself", "সিক্রেট নিজে"))],
       [ln("git", "vault", "to", state="hot", label=("reference", "রেফারেন্স"))],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("CI/CD builds and tests every change automatically and ships every change that passes. For an AI system, the tests also check the model's behavior, and GitOps makes Git the record of what runs.",
         "CI/CD প্রতিটি পরিবর্তন নিজে নিজে বিল্ড আর টেস্ট করে, আর যে পরিবর্তন পাশ করে তা ডিপ্লয় করে। AI সিস্টেমে টেস্টে মডেলের আচরণও যাচাই হয়, আর GitOps-এ কী চলবে তার রেকর্ড থাকে Git-এ।")],
       [sh("change"), sh("git", x=380), sh("cluster")],
       [ln("change", "git", "to"), ln("git", "cluster", "to")],
       [None, None, None],
       points=[("A pipeline lints, tests, builds an image tagged with the commit, runs evals, then deploys to staging.",
                "পাইপলাইন লিন্ট ও টেস্ট চালায়, কমিট ট্যাগ দিয়ে ইমেজ বানায়, ইভ্যাল চালায়, তারপর staging-এ ডিপ্লয় করে।"),
               ("Fail the build when the eval score drops below the baseline.",
                "ইভ্যাল স্কোর বেসলাইনের নিচে নামলে বিল্ড ফেল করান।"),
               ("In GitOps, you deploy by merging a change and roll back by reverting it.",
                "GitOps-এ পরিবর্তন মার্জ করে ডিপ্লয় করেন, আর revert করে রোলব্যাক করেন।"),
               ("An LLM judge is noisy: use a fixed set, pin the judge model, compare with a baseline measured on main.",
                "LLM জাজ কিছুটা এলোমেলো: নির্দিষ্ট সেট ব্যবহার করুন, জাজ মডেল পিন করুন, আর main-এ মাপা বেসলাইনের সাথে তুলনা করুন।"),
               ("Keep secrets out of the repository.",
                "সিক্রেট রিপোজিটরিতে রাখবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
