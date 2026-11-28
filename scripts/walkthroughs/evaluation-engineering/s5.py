"""Part 10 · 01 Evaluation engineering: turning "the model feels worse today" into numbers that gate every change.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Golden set  Start here: "Evaluation engineering turns the feeling that a model got worse into numbers. Those numbers then act as a signal in CI that checks every prompt or model change before it ships."; body, "Offline evals": "A golden dataset is a fixed set of (input, expected_output) pairs the model is run against on every change. Build it once, grow it from real failures, never let it decay. Run it in CI; block the release if accuracy drops below threshold."
  2 Pairwise    Body, "LLM-as-judge": "Many qualities ... can't be checked with regex. The trick is to use a strong LLM as a judge ... Pairwise comparison: show the judge A and B, ask which is better. It can pick up subtle differences, but cost grows with the number of pairs and the judge can show position bias; swap the order to check."
  3 Rubric      Same part: "Rubric-based scoring: define 4–6 criteria, ask the judge to rate each 0–5 with reasoning. Aggregate weighted score." and "Best practice: avoid judging a model with itself (judges can favour their own answers); swap answer positions; periodically check the judge against human labels."
  4 RAG         Body, "RAG metrics": "The Ragas paper defines three reference-free metrics (faithfulness, answer relevance, context relevance). The Ragas library also offers context precision and context recall. These four metrics are worth tracking in every RAG system:", and its table: Faithfulness, Answer relevance, Context precision, Context recall.
  5 Agents      Body, "Agent evals": "For agents, "the right answer" is necessary but not sufficient — you also need to check how it got there. Track:" task success rate, trajectory match, tool-call accuracy, step efficiency.
  6 Synthetic   Body, "Synthetic data generation for evals": "When your golden set is too small, use an LLM to synthesise plausible (input, expected_output) pairs from your docs and seed examples. Always include a contamination check".
  7 Online      Body, "Online evals on production traffic": "Sample a small share of live requests (for example 1–5%), run cheap judges (heuristics, regex, small LLM), record the eval score alongside the trace. This catches real failures your offline set misses".
  8 Red team    Body, "Red teaming and adversarial testing": "Build a set of attacks: prompt injection, jailbreaks, PII elicitation, hallucination bait. Run them on a regular schedule, for example monthly. Track the failure rate; treat any new failure as a bug to fix in the system prompt or guardrail."
  9 Remember    The sub-title, and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("golden", "database", ("Golden set", "গোল্ডেন সেট"), 110, 162),
    node("user", "user", ("User", "ইউজার"), 110, 162),
    node("attacks", "note", ("Attack set", "আক্রমণের সেট"), 110, 162),
    node("second", "note", ("Answer", "উত্তর"), 110, 250),
    node("model", "model", ("Model", "মডেল"), 380, 162),
    node("judge", "model", ("Judge", "জাজ"), 380, 162),
    node("chunks", "database", ("Chunks", "লেখার অংশ"), 380, 162),
    node("tool", "tool", ("Tool call", "টুল কল"), 380, 162),
    node("ci", "shield", ("CI gate", "CI গেট"), 650, 162),
    node("answer", "note", ("Answer", "উত্তর"), 650, 162),
    node("result", "chart", ("Result", "ফলাফল"), 650, 162),
    node("trace", "file", ("Trace", "ট্রেস"), 650, 162),
]

METRICS = [
    ("Criteria", "মানদণ্ড"),
    ("Score each", "প্রতিটির স্কোর"),
    ("Live sample", "লাইভ নমুনা"),
    ("Red team", "রেড টিম"),
]

CAPTION = (
    "If you can't measure it, you can't improve it: evaluation turns “the model feels worse today” into numbers.",
    "মাপতে না পারলে উন্নতি করা যায় না: ইভ্যালুয়েশন “মডেল আজ খারাপ লাগছে” কথাটাকে সংখ্যায় বদলে দেয়।",
)

STEPS = [
    st(("Golden set", "গোল্ডেন সেট"),
       ("From a feeling to numbers", "অনুভূতি থেকে সংখ্যা"),
       [("Evaluation engineering turns the feeling that a model got worse into numbers. Those numbers then act as a signal in CI that checks every prompt or model change before it ships.",
         "ইভ্যালুয়েশন ইঞ্জিনিয়ারিং মডেল খারাপ হয়েছে এমন অনুভূতিকে সংখ্যায় বদলে দেয়। সেই সংখ্যা CI-তে সংকেতের কাজ করে, আর প্রতিটি প্রম্পট বা মডেল পরিবর্তন শিপ হওয়ার আগে যাচাই করে।"),
        ("Run the golden dataset in CI, and block the release if accuracy drops below the threshold.",
         "গোল্ডেন ডেটাসেট CI-তে চালান, আর অ্যাকুরেসি সীমার নিচে নামলে রিলিজ আটকে দিন।")],
       [sh("golden", "hot", ("fixed pairs", "নির্দিষ্ট জোড়া")), sh("model", "hot", ("after every change", "প্রতি পরিবর্তনের পর")),
        sh("ci", "hot", ("blocks the release", "রিলিজ আটকায়"))],
       [ln("golden", "model", "to", state="hot"), ln("model", "ci", "to", state="hot")],
       [None, None, None, None],
       note=("insight",
             "A golden dataset is a fixed set of <code>(input, expected_output)</code> pairs. Build it once, grow it from real failures, and never let it decay.",
             "গোল্ডেন ডেটাসেট হলো <code>(input, expected_output)</code> জোড়ার একটি নির্দিষ্ট সেট। একবার বানান, বাস্তব ব্যর্থতা থেকে বাড়ান, আর কখনো ক্ষয় হতে দেবেন না।")),

    st(("Pairwise", "পেয়ারওয়াইজ"),
       ("A judge picks the better answer", "জাজ ভালো উত্তরটি বেছে নেয়"),
       [("Many qualities, such as “does this answer sound helpful?”, can't be checked with regex. The trick is to use a strong LLM as a judge.",
         "“এই উত্তর কি সহায়ক শোনায়?” এমন অনেক গুণ regex দিয়ে যাচাই করা যায় না। কৌশল হলো একটি শক্তিশালী LLM-কে জাজ বানানো।"),
        ("Pairwise comparison shows the judge A and B and asks which is better. It can pick up subtle differences, but cost grows with the number of pairs and the judge can show position bias; swap the order to check.",
         "পেয়ারওয়াইজ তুলনায় জাজকে A ও B দেখিয়ে জিজ্ঞেস করা হয় কোনটি ভালো। এটি দুই উত্তরের সূক্ষ্ম পার্থক্য ধরতে পারে, তবে জোড়ার সংখ্যা বাড়লে খরচ বাড়ে, আর জাজের পজিশন বায়াস দেখা দিতে পারে; ক্রম অদলবদল করে যাচাই করুন।")],
       [sh("answer", "hot", ("A", "A"), x=110, y=75), sh("second", "hot", ("B", "B")), sh("judge", "hot", ("a strong LLM", "শক্তিশালী LLM")),
        sh("result", "hot", ("the better one", "যেটি ভালো"))],
       [ln("answer", "judge", "to", state="hot"), ln("second", "judge", "to", state="hot"), ln("judge", "result", "to", state="hot")],
       [None, None, None, None]),

    st(("Rubric", "রুব্রিক"),
       ("A judge scores against a rubric", "জাজ রুব্রিক ধরে স্কোর দেয়"),
       [("Rubric-based scoring defines 4–6 criteria and asks the judge to rate each 0–5 with reasoning. The scores aggregate into a weighted score.",
         "রুব্রিক-ভিত্তিক স্কোরিংয়ে ৪–৬টি মানদণ্ড ঠিক করা হয়, আর জাজকে যুক্তিসহ প্রতিটিতে ০–৫ দিতে বলা হয়। স্কোরগুলো মিলিয়ে একটি ওজনযুক্ত স্কোর হয়।")],
       [sh("answer", "hot", None, None, 110, 162), sh("judge", "hot", ("reasons, then rates", "যুক্তি দিয়ে স্কোর")), sh("result", "hot", ("weighted score", "ওজনযুক্ত স্কোর"))],
       [ln("answer", "judge", "to", state="hot"), ln("judge", "result", "to", state="hot")],
       [("4–6", "৪–৬"), ("0–5", "০–৫"), None, None],
       note=("tip",
             "Avoid judging a model with itself (judges can favour their own answers), swap answer positions, and periodically check the judge against human labels.",
             "একটি মডেলকে তার নিজের দিয়ে জাজ করাবেন না (জাজ নিজের উত্তরকে বেশি পছন্দ করতে পারে), উত্তরের অবস্থান অদলবদল করুন, আর মাঝে মাঝে মানুষের লেবেলের সঙ্গে জাজকে মিলিয়ে দেখুন।")),

    st(("RAG", "RAG"),
       ("Four numbers for a RAG system", "RAG সিস্টেমের চারটি সংখ্যা"),
       [("The Ragas paper defines three reference-free metrics (faithfulness, answer relevance, context relevance). The Ragas library also offers context precision and context recall. These four metrics are worth tracking in every RAG system:",
         "Ragas পেপার তিনটি রেফারেন্স-ছাড়া মেট্রিক সংজ্ঞায়িত করেছে (ফেইথফুলনেস, আনসার রিলেভেন্স, কনটেক্সট রিলেভেন্স)। Ragas লাইব্রেরি কনটেক্সট প্রিসিশন আর কনটেক্সট রিকলও দেয়। প্রতিটি RAG সিস্টেমে এই চারটি মেট্রিক ট্র্যাক করা উচিত:")],
       [sh("user", "hot", ("question", "প্রশ্ন")), sh("chunks", "hot", ("retrieved", "খুঁজে আনা")), sh("answer", "hot")],
       [ln("user", "chunks", "to", state="hot"), ln("chunks", "answer", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "Faithfulness: does the answer stick to the retrieved chunks, or does it hallucinate?",
                 "ফেইথফুলনেস: উত্তর কি খুঁজে আনা অংশের সঙ্গে মেলে, নাকি বানিয়ে বলছে?"),
                ("+", "Answer relevance: does the answer address the user's question?",
                 "আনসার রিলেভেন্স: উত্তর কি ইউজারের প্রশ্নের সঙ্গে সম্পর্কিত?"),
                ("+", "Context precision: are the retrieved chunks mostly relevant (not noise)?",
                 "কনটেক্সট প্রিসিশন: খুঁজে আনা অংশগুলো কি বেশিরভাগই প্রাসঙ্গিক (অবান্তর নয়)?"),
                ("+", "Context recall: were all the chunks needed to answer actually retrieved?",
                 "কনটেক্সট রিকল: উত্তর দিতে দরকারি সব অংশ কি সত্যিই খুঁজে আনা হয়েছে?")]),

    st(("Agents", "এজেন্ট"),
       ("Check the path, not only the answer", "শুধু উত্তর নয়, পথটাও দেখুন"),
       [("For agents, “the right answer” is necessary but not sufficient: you also need to check how it got there. Track:",
         "এজেন্টের জন্য “সঠিক উত্তর” দরকার, কিন্তু যথেষ্ট নয়: উত্তরে কীভাবে পৌঁছেছে সেটাও যাচাই করতে হয়। ট্র্যাক করুন:")],
       [sh("model", "hot", ("the agent", "এজেন্ট"), x=110), sh("tool", "hot", ("right arguments?", "সঠিক আর্গুমেন্ট?")), sh("answer", "hot", ("right answer?", "সঠিক উত্তর?"))],
       [ln("model", "tool", "to", state="hot"), ln("tool", "answer", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "Task success rate: is the final outcome correct?",
                 "টাস্ক সাফল্যের হার: চূড়ান্ত ফলাফল কি ঠিক?"),
                ("+", "Trajectory match: did the agent take a reasonable path, with the same tools and a similar number of steps?",
                 "ট্রাজেক্টরি ম্যাচ: এজেন্ট কি যুক্তিসংগত পথে গেছে, একই টুল আর কাছাকাছি ধাপ সংখ্যা নিয়ে?"),
                ("+", "Tool-call accuracy: did each individual tool call have the right arguments?",
                 "টুল-কল অ্যাকুরেসি: প্রতিটি টুল কলে কি সঠিক আর্গুমেন্ট ছিল?"),
                ("+", "Step efficiency: how many steps compared with the minimum needed?",
                 "স্টেপ এফিশিয়েন্সি: দরকারি সর্বনিম্ন ধাপের তুলনায় কয় ধাপ লেগেছে?")]),

    st(("Synthetic", "সিনথেটিক"),
       ("Grow the set with synthetic data", "সিনথেটিক ডেটায় সেট বাড়ান"),
       [("When your golden set is too small, use an LLM to synthesize plausible <code>(input, expected_output)</code> pairs from your docs and seed examples.",
         "গোল্ডেন সেট খুব ছোট হলে LLM দিয়ে আপনার ডক আর শুরুর উদাহরণ থেকে সম্ভাব্য <code>(input, expected_output)</code> জোড়া বানান।")],
       [sh("model", "hot", ("writes pairs", "জোড়া লেখে")), sh("golden", "hot", ("grows", "বাড়ে"), x=650)],
       [ln("model", "golden", "to", state="hot")],
       [None, None, None, None],
       note=("warn",
             "Always include a contamination check: make sure synthetic questions aren't paraphrases of training data, otherwise you're testing memorization, not capability.",
             "সবসময় কন্টামিনেশন যাচাই রাখুন: সিনথেটিক প্রশ্ন যেন ট্রেনিং ডেটার নকল না হয়, নইলে আপনি সক্ষমতার বদলে মুখস্থ বিদ্যা পরীক্ষা করছেন।")),

    st(("Online", "অনলাইন"),
       ("Online evals on live traffic", "লাইভ ট্র্যাফিকে অনলাইন ইভ্যাল"),
       [("Sample a small share of live requests (for example 1–5%), run cheap judges (heuristics, regex, a small LLM), and record the eval score alongside the trace.",
         "লাইভ রিকোয়েস্টের একটি ছোট অংশ (যেমন ১–৫%) স্যাম্পল করুন, সস্তা জাজ (হিউরিস্টিক, regex, ছোট LLM) চালান, আর ইভ্যাল স্কোর ট্রেসের সাথে রেকর্ড করুন।"),
        ("This catches real failures your offline set misses: distribution shifts, prompt-template copy-paste errors, and fresh prompt injections.",
         "এটি আপনার অফলাইন সেট মিস করা বাস্তব ব্যর্থতা ধরে: ডিস্ট্রিবিউশন শিফট, প্রম্পট-টেমপ্লেট কপি-পেস্ট এরর, নতুন প্রম্পট ইনজেকশন।")],
       [sh("user", "hot", ("live requests", "লাইভ রিকোয়েস্ট")), sh("judge", "hot", ("cheap judge", "সস্তা জাজ")), sh("trace", "hot", ("with its score", "স্কোরসহ"))],
       [ln("user", "judge", "to", state="hot"), ln("judge", "trace", "to", state="hot")],
       [None, None, ("1–5%", "১–৫%"), None]),

    st(("Red team", "রেড টিম"),
       ("Red teaming", "রেড টিমিং"),
       [("Build a set of attacks: prompt injection, jailbreaks, PII elicitation, hallucination bait. Run them on a regular schedule, for example monthly. Track the failure rate.",
         "আক্রমণের একটি সেট তৈরি করুন: প্রম্পট ইনজেকশন, জেইলব্রেক, PII এলিসিটেশন, হ্যালুসিনেশন বেইট। নিয়মিত চালান, যেমন মাসে একবার।  ব্যর্থতার হার ট্র্যাক করুন।")],
       [sh("attacks", "hot", ("run monthly", "মাসে একবার")), sh("model", "hot", ("under attack", "আক্রমণের মুখে")), sh("result", "hot", ("failure rate", "ব্যর্থতার হার"))],
       [ln("attacks", "model", "to", state="hot"), ln("model", "result", "to", state="hot")],
       [None, None, None, ("monthly", "মাসিক")],
       note=("warn",
             "Treat any new failure as a bug to fix in the system prompt or guardrail.",
             "যেকোনো নতুন ব্যর্থতা সিস্টেম প্রম্পট বা গার্ডরেইলে ঠিক করার বাগ হিসেবে দেখুন।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Evaluation engineering turns the feeling that a model got worse into numbers. Those numbers then act as a signal in CI that checks every prompt or model change before it ships.",
         "ইভ্যালুয়েশন ইঞ্জিনিয়ারিং মডেল খারাপ হয়েছে এমন অনুভূতিকে সংখ্যায় বদলে দেয়। সেই সংখ্যা CI-তে সংকেতের কাজ করে, আর প্রতিটি প্রম্পট বা মডেল পরিবর্তন শিপ হওয়ার আগে যাচাই করে।")],
       [sh("golden"), sh("model"), sh("ci")],
       [ln("golden", "model", "to"), ln("model", "ci", "to")],
       [None, None, None, None],
       points=[("Build a golden dataset, grow it from real failures, and block the release if accuracy drops below the threshold.",
                "গোল্ডেন ডেটাসেট বানান, বাস্তব ব্যর্থতা থেকে বাড়ান, আর অ্যাকুরেসি (accuracy) সীমার নিচে নামলে রিলিজ আটকে দিন।"),
               ("Pairwise judging can pick up subtle differences between two answers, but watch for position bias: swap the order to check.",
                "পেয়ারওয়াইজ বিচার দুই উত্তরের সূক্ষ্ম পার্থক্য ধরতে পারে, তবে পজিশন বায়াস থেকে সাবধান: ক্রম অদলবদল করে যাচাই করুন।"),
               ("For agents, check how the answer was reached, not only whether the final answer is right.",
                "এজেন্টের ক্ষেত্রে শুধু চূড়ান্ত উত্তর নয়, উত্তরে কীভাবে পৌঁছেছে সেটাও দেখুন।"),
               ("Always check synthetic questions for contamination (questions that copy the training data), or you test memorization instead of capability.",
                "সিনথেটিক প্রশ্নে কন্টামিনেশন (contamination) (ট্রেনিং ডেটার নকল প্রশ্ন) সবসময় যাচাই করুন, নইলে সক্ষমতার বদলে মুখস্থ বিদ্যার পরীক্ষা হয়ে যায়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
