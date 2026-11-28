"""Part 4 · 06 Evaluate AI Systems: from evaluation criteria to a model selection process and your own evaluation pipeline.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Checks first   Body, "Evaluation criteria": "An application should start with a list of evaluation criteria before any heavy building begins ... evaluation-driven development ... write the checks before writing the system."
  2 Four buckets   Body: Domain-specific capability, Generation capability, Instruction-following capability, Cost and latency (the four bullets).
  3 Consistency    Table: "Local consistency: An explicitly provided context"; "Global consistency: Open/world knowledge". Callout: self-verification, knowledge-augmented verification, textual entailment, "asking an AI judge directly".
  4 Build or buy   Body, "Build versus buy": "call a commercial model API or host an open source (strictly: open-weight) model yourself" and the axes data privacy, raw performance, control, deploy on-device.
  5 Workflow       Body, "Model selection workflow": the four iterative steps (filter by hard attributes, narrow with public benchmarks, own experiments, keep monitoring).
  6 Benchmarks     Body, "Navigating public benchmarks": data contamination "inflates scores without reflecting real capability"; "A public benchmark score is a useful filter, never a guarantee."
  7 Pipeline       Body, "Designing your own evaluation pipeline": three steps (evaluate all components, create an evaluation guideline, define evaluation methods and data) and "Evaluating the pipeline itself" (right signal, reproducible, overly correlated metrics, cost and latency added).
  8 Remember       The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("checks", "file", ("Your checks", "আপনার যাচাই"), 140, 162),
    node("app", "service", ("AI application", "AI অ্যাপ্লিকেশন"), 380, 162),
    node("output", "file", ("Output", "আউটপুট"), 140, 162),
    node("ctx", "file", ("Given context", "দেওয়া কনটেক্সট"), 470, 70),
    node("world", "database", ("Real world", "বাস্তব দুনিয়া"), 470, 254),
    node("api", "service", ("Commercial model API", "কমার্শিয়াল মডেল API"), 560, 80),
    node("host", "server", ("Open-weight model", "ওপেন-ওয়েট মডেল"), 560, 244),
    node("hard", "shield", ("Hard attributes", "হার্ড অ্যাট্রিবিউট"), 150, 80),
    node("bench", "chart", ("Public benchmarks", "পাবলিক বেঞ্চমার্ক"), 500, 80),
    node("pipe", "tool", ("Your evaluation pipeline", "আপনার ইভ্যালুয়েশন পাইপলাইন"), 430, 250),
    node("prod", "server", ("Production", "প্রোডাকশন"), 665, 250),
]

METRICS = [
    ("Best model", "সেরা মডেল"),
    ("Benchmark score", "বেঞ্চমার্ক স্কোর"),
    ("Monitoring", "নজরদারি"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Checks first", "আগে যাচাই"),
       ("Write the checks before the system", "সিস্টেমের আগে যাচাই লিখুন"),
       [("An application should start with a list of evaluation criteria before any heavy building begins.",
         "যেকোনো ভারী বানানো শুরুর আগে অ্যাপ্লিকেশনকে ইভ্যালুয়েশন মানদণ্ডের একটি তালিকা দিয়ে শুরু করা উচিত।"),
        ("This is evaluation-driven development, similar to test-driven development: write the checks before writing the system.",
         "একে বলে ইভ্যালুয়েশন-ড্রিভেন ডেভেলপমেন্ট, যা টেস্ট-ড্রিভেন ডেভেলপমেন্টের মতো: সিস্টেম লেখার আগে যাচাই লিখে ফেলুন।")],
       [sh("checks", "hot", ("first", "আগে")), sh("app", "dim", ("then build", "তারপর বানান"))],
       [ln("checks", "app", "to", state="hot")],
       [None, None, None]),

    st(("Four buckets", "চার ভাগ"),
       ("Four kinds of criteria", "চার ধরনের মানদণ্ড"),
       [("The criteria usually fall into four buckets. They are domain-specific capability, generation capability, instruction-following capability, and cost and latency.",
         "মানদণ্ড সাধারণত চার ভাগে পড়ে। ডোমেইন-নির্দিষ্ট সক্ষমতা, জেনারেশন সক্ষমতা, ইনস্ট্রাকশন-ফলো করার সক্ষমতা, আর খরচ ও লেটেন্সি।"),
        ("Each one is a question about your application.",
         "প্রতিটাই আপনার অ্যাপ্লিকেশন নিয়ে একটি প্রশ্ন।")],
       [sh("checks", "hot"), sh("app", "hot")],
       [ln("checks", "app", "to", state="hot")],
       [None, None, None],
       points=[("Domain-specific capability: does the model know enough about the task's subject?",
                "ডোমেইন-নির্দিষ্ট সক্ষমতা: কাজের বিষয়টা মডেল যথেষ্ট জানে কিনা?"),
               ("Generation capability: is the output coherent, factually consistent, and safe?",
                "জেনারেশন সক্ষমতা: আউটপুট সুসংগত, তথ্যে সঙ্গতিপূর্ণ আর নিরাপদ কিনা?"),
               ("Instruction-following capability: does the model do what it was told?",
                "ইনস্ট্রাকশন-ফলো করার সক্ষমতা: মডেল যা বলা হয়েছে তা করছে কিনা?"),
               ("Cost and latency: can the application afford this model's price and speed?",
                "খরচ ও লেটেন্সি: এই মডেলের দাম আর গতি অ্যাপ্লিকেশন সামলাতে পারবে কিনা?")]),

    st(("Consistency", "সঙ্গতি"),
       ("Factual consistency: against what?", "ফ্যাকচুয়াল কনসিস্টেন্সি: কিসের সাথে?"),
       [("Factual consistency asks whether the output matches the given context or the real world.",
         "ফ্যাকচুয়াল কনসিস্টেন্সি দেখে আউটপুট দেওয়া কনটেক্সটের সাথে বা বাস্তব দুনিয়ার সাথে মেলে কিনা।"),
        ("Local consistency checks against an explicitly provided context. Global consistency checks against open or world knowledge.",
         "লোকাল কনসিস্টেন্সি স্পষ্টভাবে দেওয়া কনটেক্সটের সাথে মেলায়। গ্লোবাল কনসিস্টেন্সি উন্মুক্ত বা বিশ্বজ্ঞানের সাথে মেলায়।")],
       [sh("output", "hot"), sh("ctx", "hot", ("local: summarization, RAG", "লোকাল: summarization, RAG")), sh("world", "hot", ("global: chatbots", "গ্লোবাল: চ্যাটবট"))],
       [ln("output", "ctx", "to", state="hot"), ln("output", "world", "to", state="hot")],
       [None, None, None],
       points=[("Asking an AI judge directly", "AI জাজকে সরাসরি জিজ্ঞেস করা"),
               ("Self-verification: generate several answers and see if they agree", "সেলফ-ভেরিফিকেশন: কয়েকটি উত্তর বানিয়ে দেখা সেগুলো মেলে কিনা"),
               ("Knowledge-augmented verification: check each claim against a search engine", "নলেজ-অগমেন্টেড ভেরিফিকেশন: প্রতিটি দাবি সার্চ ইঞ্জিনে যাচাই করা"),
               ("Textual entailment models", "টেক্সচুয়াল এন্টেইলমেন্ট মডেল")]),

    st(("Build or buy", "কিনব না বানাব"),
       ("A model API or self-hosting", "মডেল API নাকি নিজে হোস্টিং"),
       [("A central recurring decision is whether to call a commercial model API or host an open source (strictly: open-weight) model yourself.",
         "একটি বারবার আসা বড় সিদ্ধান্ত হলো কমার্শিয়াল মডেল API ডাকবেন, নাকি একটি ওপেন সোর্স (সঠিকভাবে বললে ওপেন-ওয়েট) মডেল নিজে হোস্ট করবেন।"),
        ("The trade-off spans several axes, such as data privacy, raw performance, control, and the ability to deploy on-device.",
         "এই ট্রেড-অফ কয়েকটি দিকে ছড়ানো, যেমন ডেটা প্রাইভেসি, সরাসরি পারফরম্যান্স, নিয়ন্ত্রণ, আর অন-ডিভাইসে ডিপ্লয় করার সুযোগ।")],
       [sh("app", "hot"), sh("api", "hot", ("a third party", "তৃতীয় পক্ষ")), sh("host", "hot", ("in-house", "নিজেদের হাতে"))],
       [ln("app", "api", "to", state="hot"), ln("app", "host", "to", state="hot")],
       [None, None, None]),

    st(("Workflow", "ধাপ"),
       ("Four steps to choose a model", "মডেল বাছাইয়ের চার ধাপ"),
       [("Choosing a model is really choosing the best model for a specific application, not the best model overall.",
         "মডেল বাছা মানে আসলে একটি নির্দিষ্ট অ্যাপ্লিকেশনের জন্য সেরা মডেল বাছা, পুরো দুনিয়ার সেরা মডেল নয়।"),
        ("The workflow has four iterative steps: filter by hard attributes, narrow with public benchmarks, run your own experiments, and keep monitoring in production.",
         "ওয়ার্কফ্লোতে চারটি পুনরাবৃত্তিমূলক ধাপ: হার্ড অ্যাট্রিবিউট দিয়ে ফিল্টার, পাবলিক বেঞ্চমার্ক দিয়ে ছোট করা, নিজের পরীক্ষা চালানো, আর প্রোডাকশনে নজর রাখা।")],
       [sh("hard", "hot", ("license, privacy", "লাইসেন্স, প্রাইভেসি")), sh("bench", "hot"), sh("pipe", "hot"), sh("prod", "hot")],
       [ln("hard", "bench", "to", state="hot"), ln("bench", "pipe", "to", state="hot"), ln("pipe", "prod", "to", state="hot")],
       [("for your application", "আপনার অ্যাপ্লিকেশনের জন্য"), None, ("keep monitoring", "নজর রাখা")]),

    st(("Benchmarks", "বেঞ্চমার্ক"),
       ("A benchmark score is a filter", "বেঞ্চমার্ক স্কোর একটি ফিল্টার"),
       [("Public leaderboards are useful for filtering out clearly weak models.",
         "পাবলিক লিডারবোর্ড স্পষ্টভাবে দুর্বল মডেল বাদ দিতে কাজে লাগে।"),
        ("Data contamination means a model saw benchmark questions during training, which inflates scores without reflecting real capability.",
         "ডেটা কন্টামিনেশন মানে ট্রেনিংয়ের সময় মডেল বেঞ্চমার্কের প্রশ্ন দেখে ফেলেছে, ফলে আসল দক্ষতা ছাড়াই স্কোর ফুলে যায়।")],
       [sh("bench", "warn", ("data contamination", "ডেটা কন্টামিনেশন")), sh("pipe", "hot")],
       [ln("bench", "pipe", "to", state="warn")],
       [None, ("useful filter, never a guarantee", "কাজের ফিল্টার, গ্যারান্টি নয়"), None],
       note=("warn", "A public benchmark score is a useful filter, never a guarantee.",
             "পাবলিক বেঞ্চমার্কের স্কোর কাজের ফিল্টার, কিন্তু কখনোই গ্যারান্টি নয়।")),

    st(("Pipeline", "পাইপলাইন"),
       ("Build your own pipeline", "নিজের পাইপলাইন বানান"),
       [("Evaluate all components in a system, create an evaluation guideline, and define evaluation methods and data.",
         "সিস্টেমের সব অংশ মূল্যায়ন করুন, একটি ইভ্যালুয়েশন গাইডলাইন বানান, আর ইভ্যালুয়েশন পদ্ধতি ও ডেটা ঠিক করুন।"),
        ("The pipeline itself needs evaluating too.",
         "পাইপলাইনটাকেও মূল্যায়ন করা দরকার।")],
       [sh("app", "hot", ("every part", "প্রতিটি অংশ"), x=130, y=250), sh("pipe", "hot")],
       [ln("app", "pipe", "to", state="hot")],
       [None, None, None],
       points=[("Does it give the right signal: do better outputs score higher?", "এটা সঠিক সংকেত দেয় কিনা: ভালো আউটপুট বেশি স্কোর পায় কিনা?"),
               ("Are repeated runs reproducible?", "বারবার চালালে ফল পুনরুৎপাদনযোগ্য কিনা?"),
               ("Are its metrics overly correlated?", "এর মেট্রিকগুলো অতিরিক্ত পরস্পর-সম্পর্কিত কিনা?"),
               ("How much cost and latency does it add?", "এটা কতটা খরচ আর লেটেন্সি যোগ করে?")]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("Pick the best model for your own application, not the best model overall. A public benchmark score is a useful filter, never a guarantee.",
         "পুরো দুনিয়ার সেরা মডেল নয়, আপনার নিজের অ্যাপ্লিকেশনের জন্য সেরা মডেল বাছুন। পাবলিক বেঞ্চমার্কের স্কোর কাজের ফিল্টার, কিন্তু কখনোই গ্যারান্টি নয়।"),
        ("Build your own evaluation pipeline, and score every part of the system, not only the final output. Keep monitoring the model in production, and evaluate the pipeline itself too.",
         "নিজের ইভ্যালুয়েশন পাইপলাইন বানান, আর শুধু শেষ আউটপুট নয়, সিস্টেমের প্রতিটি অংশ মূল্যায়ন করুন। প্রোডাকশনে মডেলকে নজরে রাখুন, আর পাইপলাইনটাকেও মূল্যায়ন করুন।")],
       [sh("hard", "dim"), sh("bench", "dim"), sh("pipe", "hot"), sh("prod", "hot")],
       [ln("hard", "bench", "to", state="dim"), ln("bench", "pipe", "to", state="dim"), ln("pipe", "prod", "to", state="hot")],
       [None, None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
