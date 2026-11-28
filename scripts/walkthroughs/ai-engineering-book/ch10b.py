"""Part 15 · ch10b AI Engineering Architecture and User Feedback: monitoring and feedback.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Request   "An orchestrator wires all the components together" / "The part that connects all the components and sets the order of the steps." "Starting without [a heavy framework] is often the better default."
  2 Observe   "Being able to work out what is happening inside a system from its logs and metrics, without writing new code just to find a problem." "Logs are an append-only record of events."
  3 Trace     "The full path of one request, step by step, with timing and cost. It shows which step went wrong."
  4 Drift     "An unnoticed change in how the system behaves or is used, such as users slowly changing how they phrase requests." "the underlying model silently changing behind an unchanged API."
  5 Feedback  "Feedback you infer from what a user does, such as regenerating an answer, instead of asking directly." "Good feedback design makes giving feedback nearly free."
  6 Bias      "Leniency bias, position bias, and preference bias all distort it."
  7 Loop      "Popular outputs get shown more, get more clicks, and grow more popular, while outputs that are never shown get no chance."
  8 Remember  The five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ইউজার"), 95, 162),
    node("orch", "service", ("Orchestrator", "অর্কেস্ট্রেটর"), 290, 162),
    node("model", "model", ("Model", "মডেল"), 520, 162),
    node("logs", "database", ("Logs and metrics", "লগ আর মেট্রিক"), 520, 262),
    node("trace", "chart", ("Trace", "ট্রেস"), 290, 262),
    node("drift", "note", ("Drift", "ড্রিফট"), 290, 70),
    node("bias", "note", ("Biased feedback", "পক্ষপাতী ফিডব্যাক"), 520, 70),
    node("pop", "service", ("Popular outputs", "জনপ্রিয় আউটপুট"), 200, 130),
    node("clicks", "user", ("More clicks", "বেশি ক্লিক"), 560, 130),
    node("unseen", "file", ("Outputs never shown", "যা কখনো দেখানো হয় না"), 380, 262),
]

METRICS = [
    ("Feedback", "ফিডব্যাক"),
    ("Shown", "দেখানো"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Request", "রিকোয়েস্ট"),
       ("An orchestrator runs the steps", "অর্কেস্ট্রেটর ধাপগুলো চালায়"),
       [("The orchestrator connects all the components and sets the order of the steps.",
         "অর্কেস্ট্রেটর সব কম্পোনেন্ট জুড়ে দেয় আর ধাপগুলোর ক্রম ঠিক করে।"),
        ("Starting without a heavy orchestration framework is often the better default.",
         "ভারী অর্কেস্ট্রেশন ফ্রেমওয়ার্ক ছাড়া শুরু করাই প্রায়ই ভালো ডিফল্ট।")],
       [sh("user", "hot"), sh("orch", "hot"), sh("model", "hot")],
       [ln("user", "orch", "to", state="hot"), ln("orch", "model", "to", state="hot")],
       [None, None]),

    st(("Observe", "অবজারভ"),
       ("Observability reads logs and metrics", "অবজারভেবিলিটি লগ আর মেট্রিক পড়ে"),
       [("Observability is being able to work out what is happening inside a system from its logs and metrics.",
         "অবজারভেবিলিটি হলো লগ আর মেট্রিক থেকে সিস্টেমের ভেতরে কী হচ্ছে বুঝতে পারা।"),
        ("You do not write new code just to find a problem.",
         "শুধু সমস্যা খুঁজতে নতুন কোড লিখতে হয় না।")],
       [sh("orch", "dim"), sh("model", "hot"), sh("logs", "hot")],
       [ln("model", "logs", "to", state="hot")],
       [None, None]),

    st(("Trace", "ট্রেস"),
       ("A trace shows the failing step", "ট্রেস দেখায় কোন ধাপ ব্যর্থ"),
       [("A trace is the full path of one request, step by step, with timing and cost.",
         "ট্রেস হলো একটি রিকোয়েস্টের পুরো পথ, ধাপে ধাপে, সময় আর খরচসহ।"),
        ("It shows which step went wrong.", "এতে বোঝা যায় কোন ধাপে সমস্যা হয়েছে।")],
       [sh("user", "dim"), sh("orch", "hot"), sh("model", "warn", ("this step went wrong", "এই ধাপে সমস্যা")), sh("trace", "hot")],
       [ln("user", "orch", "to", state="dim"), ln("orch", "model", "to", state="hot"), ln("orch", "trace", "to", state="hot")],
       [None, None]),

    st(("Drift", "ড্রিফট"),
       ("Drift changes things unnoticed", "ড্রিফট চুপচাপ সব বদলায়"),
       [("Drift is an unnoticed change in how the system behaves or is used, such as users slowly changing how they phrase requests.",
         "ড্রিফট হলো সিস্টেমের আচরণ বা ব্যবহারে এমন পরিবর্তন যা কেউ খেয়াল করে না, যেমন ইউজাররা ধীরে ধীরে অনুরোধের ভাষা বদলে ফেলে।"),
        ("The model can also change silently behind an unchanged API.",
         "API একই থাকলেও মডেল চুপচাপ বদলে যেতে পারে।")],
       [sh("user", "hot", ("rephrases", "ভাষা বদলায়")), sh("orch", "dim"), sh("model", "warn", ("changes silently", "চুপচাপ বদলায়")), sh("drift", "warn")],
       [ln("user", "orch", "to", state="dim"), ln("orch", "model", "to", state="dim"), ln("drift", "model", "to", state="warn")],
       [None, None]),

    st(("Feedback", "ফিডব্যাক"),
       ("Users teach it through actions", "ইউজার কাজের মাধ্যমে শেখায়"),
       [("Implicit feedback is what you infer from what a user does, such as regenerating an answer, instead of asking directly.",
         "ইমপ্লিসিট ফিডব্যাক হলো সরাসরি জিজ্ঞেস না করে ইউজারের কাজ থেকে বোঝা ফিডব্যাক, যেমন উত্তর আবার জেনারেট করানো।"),
        ("Good feedback design makes giving feedback nearly free.",
         "ভালো ফিডব্যাক ডিজাইন ফিডব্যাক দেওয়াটা প্রায় বিনা ঝামেলার করে দেয়।")],
       [sh("user", "hot", ("regenerates", "রিজেনারেট করে")), sh("logs", "hot", ("feedback signal", "ফিডব্যাক সংকেত"), x=400)],
       [ln("user", "logs", "to", state="hot")],
       [("nearly free", "প্রায় বিনামূল্যে"), None]),

    st(("Bias", "বায়াস"),
       ("Feedback is biased", "ফিডব্যাকে পক্ষপাত থাকে"),
       [("Leniency bias, position bias, and preference bias all distort feedback.",
         "লেনিয়েন্সি বায়াস (leniency bias), পজিশন বায়াস (position bias) আর প্রেফারেন্স বায়াস (preference bias) সবই ফল বিকৃত করে।"),
        ("So user feedback is valuable but biased and incomplete.",
         "তাই ইউজার ফিডব্যাক মূল্যবান, কিন্তু পক্ষপাতী আর অসম্পূর্ণ।")],
       [sh("user", "hot"), sh("bias", "warn", ("leniency, position, preference", "লেনিয়েন্সি, পজিশন, প্রেফারেন্স")), sh("model", "dim")],
       [ln("user", "bias", "to", state="warn"), ln("bias", "model", "to", state="dim")],
       [("biased", "পক্ষপাতী"), None]),

    st(("Loop", "লুপ"),
       ("Popular outputs get more popular", "জনপ্রিয় আউটপুট আরও জনপ্রিয় হয়"),
       [("Popular outputs get shown more, get more clicks, and grow more popular.",
         "জনপ্রিয় আউটপুট বেশি দেখানো হয়, বেশি ক্লিক পায়, আরও জনপ্রিয় হয়।"),
        ("Outputs that are never shown get no chance. This is a degenerate feedback loop.",
         "যা কখনো দেখানো হয় না, সে সুযোগই পায় না। একে বলে ডিজেনারেট ফিডব্যাক লুপ।")],
       [sh("pop", "hot"), sh("clicks", "hot"), sh("unseen", "dim", ("get no chance", "সুযোগ পায় না"))],
       [ln("pop", "clicks", "to", state="hot", label=("shown more", "বেশি দেখানো")), ln("clicks", "pop", "to", state="hot")],
       [None, ("shown more", "বেশি দেখানো")]),

    st(("Remember", "মনে রাখুন"),
       ("Trace it, watch it, and test the feedback", "ট্রেস করুন, নজর রাখুন, ফিডব্যাক যাচাই করুন"),
       [("Use traces to find exactly which step failed, with metrics and logs to spot and debug problems. Watch for drift.",
         "ঠিক কোন ধাপ ব্যর্থ হয়েছে তা খুঁজতে ট্রেস ব্যবহার করুন, আর সমস্যা ধরতে ও ডিবাগ করতে মেট্রিক ও লগ কাজে লাগান। ড্রিফটের দিকে নজর রাখুন।"),
        ("Make giving feedback nearly free for users, and remember that feedback is biased.",
         "ইউজারের জন্য ফিডব্যাক দেওয়া প্রায় বিনা ঝামেলার করুন, আর মনে রাখুন ফিডব্যাকে পক্ষপাত থাকে।")],
       [sh("trace", "hot"), sh("logs", "hot"), sh("drift", "warn"), sh("bias", "warn")],
       [ln("trace", "logs", "to", state="hot"), ln("drift", "bias", "to", state="dim")],
       [None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
