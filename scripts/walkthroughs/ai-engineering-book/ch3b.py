"""Part 3b · 05 Evaluation Methodology: AI judges and comparative evaluation.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Judge      Start here: "Using one AI model to score or compare the outputs of another AI model, or of itself." Body: "It is fast and cheap relative to human annotation, works without reference data, and can judge on any criteria you describe."
  2 Three ways Body: "scoring a response on its own; comparing a response to a reference answer; comparing two responses against each other to pick a winner."
  3 Prompt     Body: "A judge's prompt should spell out the task, the scoring criteria in detail, and the scoring system: classification labels, discrete numbers such as 1–5, or a continuous scale. Discrete, classification-style scoring tends to work more reliably than open-ended numeric scoring."
  4 Limits     Body, "Limitations of AI judges": Inconsistency, Criteria ambiguity, Bias (self-bias, position bias, verbosity bias), Cost and latency. Talent-show analogy: "AI judges work best alongside other checks, not alone."
  5 Types      Body, "Which models can act as judges": reward models, reference-based judges, preference models. Start here: "Reward model: A special judge that gives a score to a pair made of a prompt and a response."
  6 Head to head Body, "Ranking models with comparative evaluation": "compare two models' outputs for the same prompt side by side and pick a winner ... a rating algorithm (such as Elo or Bradley–Terry) converts win rates into an overall ranking."
  7 Gap        Body: "knowing that model B beats model A doesn't tell you if either is good enough. Nor does it tell you whether the win is worth B's extra cost." Also: "It also never 'saturates' the way fixed benchmarks do."
  8 Remember   The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("ans-a", "file", ("Answer A", "উত্তর A"), 110, 90),
    node("ans-b", "file", ("Answer B", "উত্তর B"), 110, 234),
    node("ref", "file", ("Reference answer", "রেফারেন্স উত্তর"), 335, 50),
    node("judge", "model", ("AI judge", "এআই জাজ"), 335, 162),
    node("score", "chart", ("Score", "স্কোর"), 615, 162),
    node("t1", "model", ("Reward model", "রিওয়ার্ড মডেল"), 615, 60),
    node("t2", "model", ("Reference judge", "রেফারেন্স জাজ"), 615, 162),
    node("t3", "model", ("Preference model", "প্রেফারেন্স মডেল"), 615, 264),
    node("eval", "user", ("Evaluator", "মূল্যায়নকারী"), 335, 162),
    node("rank", "chart", ("One overall ranking", "একটি সামগ্রিক র‍্যাংক"), 615, 162),
    node("m-a", "model", ("Model A", "মডেল A"), 110, 90),
    node("m-b", "model", ("Model B", "মডেল B"), 110, 234),
]

METRICS = [
    ("Judge", "জাজ"),
    ("Compares", "তুলনা"),
    ("Tells you", "জানায়"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Judge", "জাজ"),
       ("One model judges another", "এক মডেল আরেক মডেলকে বিচার করে"),
       [("AI as a judge means using one AI model to score or compare the outputs of another AI model, or of itself.",
         "এআই জাজ মানে একটি AI মডেল দিয়ে অন্য AI মডেলের, বা নিজের, আউটপুট স্কোর করানো বা তুলনা করানো।"),
        ("It is fast and cheap relative to human annotation, and it can judge on any criteria you describe.",
         "মানুষের অ্যানোটেশনের তুলনায় এটা দ্রুত আর সস্তা, আর আপনার বলে দেওয়া যেকোনো মানদণ্ডে বিচার করতে পারে।")],
       [sh("ans-a", "hot"), sh("judge", "hot", ("fast and cheap", "দ্রুত আর সস্তা")), sh("score", "hot")],
       [ln("ans-a", "judge", "to", state="hot"), ln("judge", "score", "to", state="hot")],
       [("AI model", "AI মডেল"), None, None]),

    st(("Three ways", "তিন উপায়"),
       ("Three ways to use a judge", "জাজ ব্যবহারের তিন উপায়"),
       [("A judge can score a response on its own, or compare it to a reference answer.",
         "জাজ একটি উত্তরকে একা স্কোর করতে পারে, বা রেফারেন্স উত্তরের সাথে তুলনা করতে পারে।"),
        ("It can also compare two responses against each other to pick a winner.",
         "অথবা দুটি উত্তরকে একে অপরের সাথে তুলনা করে বিজয়ী বাছতে পারে।")],
       [sh("ans-a", "hot", ("on its own", "একা")), sh("ref", "hot"), sh("ans-b", "hot", ("pick a winner", "বিজয়ী বাছা")),
        sh("judge", "hot"), sh("score", "hot")],
       [ln("ans-a", "judge", "to", state="hot"), ln("ref", "judge", "to", state="hot"),
        ln("ans-b", "judge", "to", state="hot"), ln("judge", "score", "to", state="hot")],
       [None, None, None]),

    st(("Prompt", "প্রম্পট"),
       ("Spell out the judge's prompt", "জাজের প্রম্পট স্পষ্ট করুন"),
       [("A judge's prompt should spell out the task, the scoring criteria in detail, and the scoring system.",
         "জাজের প্রম্পটে কাজ, বিস্তারিত স্কোরিং মানদণ্ড আর স্কোরিং সিস্টেম স্পষ্ট করে লেখা উচিত।"),
        ("The system can be classification labels, discrete numbers such as 1–5, or a continuous scale.",
         "সিস্টেম হতে পারে ক্লাসিফিকেশন লেবেল, ১–৫-এর মতো আলাদা সংখ্যা, বা একটানা স্কেল।")],
       [sh("judge", "hot", ("task, criteria, scoring system", "কাজ, মানদণ্ড, স্কোরিং সিস্টেম")), sh("score", "hot", ("labels, 1–5, or scale", "লেবেল, ১–৫, বা স্কেল"))],
       [ln("judge", "score", "to", state="hot")],
       [None, None, ("Discrete, classification-style", "আলাদা, ক্লাসিফিকেশন-ধরনের")],
       note=("tip", "Discrete, classification-style scoring tends to work more reliably than open-ended numeric scoring.",
             "আলাদা, ক্লাসিফিকেশন-ধরনের স্কোরিং সাধারণত খোলা সংখ্যাভিত্তিক স্কোরিংয়ের চেয়ে বেশি নির্ভরযোগ্য।")),

    st(("Limits", "সীমা"),
       ("Judges have flaws", "জাজের দুর্বলতা আছে"),
       [("The same judge can give different scores for the same input, and different tools define one criterion differently.",
         "একই জাজ একই ইনপুটে আলাদা স্কোর দিতে পারে, আর বিভিন্ন টুল একই মানদণ্ডকে আলাদাভাবে সংজ্ঞায়িত করে।"),
        ("Judges can favor their own outputs, the first option shown, or longer answers, regardless of actual quality.",
         "জাজ নিজের উত্তর, প্রথম দেখানো অপশন বা লম্বা উত্তরের দিকে ঝুঁকতে পারে, আসল মান যা-ই হোক।")],
       [sh("ans-a", "dim"), sh("judge", "warn", ("inconsistent", "অসঙ্গত")), sh("score", "warn", ("biased", "পক্ষপাতদুষ্ট"))],
       [ln("ans-a", "judge", "to", state="dim"), ln("judge", "score", "to", state="warn")],
       [None, None, None],
       points=[("Inconsistency", "অসঙ্গতি"), ("Criteria ambiguity", "মানদণ্ডে অস্পষ্টতা"),
               ("Bias: self-bias, position bias, verbosity bias", "বায়াস: সেলফ-বায়াস, পজিশন বায়াস, ভার্বোসিটি বায়াস"),
               ("Cost and latency", "খরচ ও লেটেন্সি")],
       note=("warn", "AI judges work best alongside other checks, not alone.",
             "এআই জাজ অন্য যাচাইয়ের পাশে সবচেয়ে ভালো কাজ করে, একা নয়।")),

    st(("Types", "ধরন"),
       ("Specialized judges", "বিশেষ ধরনের জাজ"),
       [("Weaker or specialized judges are cheaper and still useful.",
         "দুর্বল বা বিশেষ ধরনের জাজ সস্তা এবং তবুও কাজের।"),
        ("A reward model scores a prompt-response pair. Reference-based judges score a response against reference answers. Preference models pick which of two responses is better.",
         "রিওয়ার্ড মডেল একটি প্রম্পট-উত্তরের জোড়াকে স্কোর দেয়। রেফারেন্স-ভিত্তিক জাজ রেফারেন্স উত্তরের সাথে মিলিয়ে স্কোর দেয়। প্রেফারেন্স মডেল দুটি উত্তরের কোনটি ভালো তা বাছে।")],
       [sh("t1", "hot", ("scores a pair", "জোড়াকে স্কোর দেয়")), sh("t2", "hot", ("vs references", "রেফারেন্সের সাথে")),
        sh("t3", "hot", ("picks the better", "ভালোটা বাছে")), sh("judge", "hot")],
       [ln("judge", "t1", "to", state="hot"), ln("judge", "t2", "to", state="hot"), ln("judge", "t3", "to", state="hot")],
       [None, None, None]),

    st(("Head to head", "মুখোমুখি"),
       ("Compare answers side by side", "উত্তর পাশাপাশি তুলনা"),
       [("Comparative evaluation shows two models' answers to the same prompt side by side and picks a winner, instead of scoring each alone.",
         "কমপ্যারেটিভ ইভ্যালুয়েশনে একই প্রম্পটের জন্য দুই মডেলের উত্তর পাশাপাশি দেখিয়ে বিজয়ী বাছা হয়, প্রতিটিকে আলাদা স্কোর না দিয়ে।"),
        ("From many head-to-head matches, a rating method such as Elo turns the results into one overall ranking.",
         "অনেক মুখোমুখি ম্যাচ থেকে Elo-র মতো রেটিং পদ্ধতি ফলগুলোকে একটি সামগ্রিক র‍্যাংকে বদলে দেয়।")],
       [sh("ans-a", "hot"), sh("ans-b", "hot"), sh("eval", "hot", ("pick a winner", "বিজয়ী বাছা")), sh("rank", "hot", ("Elo", "Elo"))],
       [ln("ans-a", "eval", "to", state="hot"), ln("ans-b", "eval", "to", state="hot"), ln("eval", "rank", "to", state="hot")],
       [None, ("head-to-head wins", "মুখোমুখি জয়"), None],
       note=("tip", "It does not saturate like fixed benchmarks.",
             "এটা নির্দিষ্ট বেঞ্চমার্কের মতো স্যাচুরেট হয়ে পড়ে না।")),

    st(("Gap", "ফাঁক"),
       ("Winning is not the same as good", "জেতা মানেই ভালো নয়"),
       [("Knowing that model B beats model A does not tell you if either one is good enough.",
         "মডেল B মডেল A-কে হারিয়েছে জানলেও বোঝা যায় না, দুটোর কোনোটা যথেষ্ট ভালো কিনা।"),
        ("Nor does it tell you whether the win is worth B's extra cost.",
         "এটাও বোঝা যায় না, জয়টা B-এর বাড়তি খরচের যোগ্য কিনা।")],
       [sh("m-a", "dim"), sh("m-b", "hot", ("beats A", "A-কে হারায়")), sh("rank", "warn", ("good enough?", "যথেষ্ট ভালো?"))],
       [ln("m-a", "rank", "to", state="dim"), ln("m-b", "rank", "to", state="warn")],
       [None, None, ("Not good enough?", "যথেষ্ট ভালো কিনা নয়")]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("AI judges are fast and cheap, and can judge on any criteria you describe. Judges can be inconsistent and biased toward their own answers, the first option, or longer answers.",
         "এআই জাজ দ্রুত আর সস্তা, আর আপনার বলে দেওয়া যেকোনো মানদণ্ডে বিচার করতে পারে। জাজ অসঙ্গত হতে পারে, আর নিজের উত্তর, প্রথম অপশন বা লম্বা উত্তরের দিকে ঝুঁকতে পারে।"),
        ("Comparative evaluation ranks models from many head-to-head wins. Knowing model B beats model A does not tell you if either one is good enough.",
         "কমপ্যারেটিভ ইভ্যালুয়েশন অনেক মুখোমুখি জয় থেকে মডেলদের র‍্যাংক করে। মডেল B মডেল A-কে হারিয়েছে জানলেও বোঝা যায় না, দুটোর কোনোটা যথেষ্ট ভালো কিনা।")],
       [sh("judge", "hot"), sh("eval", "hot", x=335, y=60), sh("rank", "hot")],
       [ln("judge", "rank", "to", state="hot"), ln("eval", "rank", "to", state="hot")],
       [None, None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
