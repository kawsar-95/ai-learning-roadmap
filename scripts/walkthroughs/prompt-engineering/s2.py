"""Prompt Engineering · 02 Few-shot, role prompting & personas: show examples, give a role, add detail, and remember a persona is style, not knowledge.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Shape     Start here: "You can shape a model by showing it examples, giving it a role, or both."
  2 Few-shot  Glossary "Few-shot examples": "A few sample input and output pairs, 2–8, placed in the prompt. The model finds the pattern and follows it." Remember: "Examples are the spec".
  3 Not prose Remember: "2–8 pairs work better than describing the task in prose." Start here: "Few-shot examples are often more reliable than a long description".
  4 Cover     Remember: "Cover the common case, tricky edge cases, and format traps like multi-line input in your examples." Glossary "Edge case".
  5 Role      Glossary "Role prompting": "Telling the model who to be, for example a senior copyeditor. It changes style, how much it hedges ..., and depth."
  6 Persona   Glossary "Persona": "A detailed role with level, vocabulary, and tone. It works best in the system message." Start here: "a detailed persona tends to beat a vague one".
  7 Not brain Remember: "A persona gives style, not knowledge. When expertise matters, add retrieved knowledge (RAG)." Warning: "Personas alone risk confident hallucination."
  8 Remember  The four remember points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("role", "note", ("Role", "রোল"), 130, 70),
    node("prose", "note", ("Long description", "লম্বা বর্ণনা"), 130, 70),
    node("common", "file", ("Common case", "সাধারণ কেস"), 130, 70),
    node("ex", "file", ("Examples", "উদাহরণ"), 130, 162),
    node("edge", "file", ("Edge cases", "এজ কেস"), 130, 162),
    node("persona", "note", ("Detailed persona", "বিস্তারিত পারসোনা"), 130, 254),
    node("trap", "file", ("Format traps", "ফরম্যাট ট্র্যাপ"), 130, 254),
    node("know", "database", ("Retrieved knowledge (RAG)", "রিট্রিভ করা জ্ঞান (RAG)"), 410, 70),
    node("model", "model", ("Model", "মডেল"), 610, 162),
]

METRICS = [
    ("Examples", "উদাহরণ"),
    ("Gives", "দেয়"),
    ("Lives in", "থাকে"),
]

CAPTION = (
    "Illustrative: the labels are the section's own words.",
    "উদাহরণমাত্র: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Shape", "গড়া"),
       ("Show it, or give it a role", "দেখান, বা রোল দিন"),
       [("You can shape a model by showing it examples, giving it a role, or both.",
         "উদাহরণ দেখিয়ে, রোল দিয়ে বা দুটোই করে মডেলের আচরণ গড়া যায়।")],
       [sh("ex", "hot", y=254), sh("role", "hot"), sh("model", "hot")],
       [ln("ex", "model", "to", state="hot"), ln("role", "model", "to", state="hot")],
       [None, None, None]),

    st(("Few-shot", "ফিউ-শট"),
       ("Few-shot: the examples are the spec", "ফিউ-শট: উদাহরণই স্পেক"),
       [("Few-shot examples are a few sample input and output pairs, 2–8, placed in the prompt.",
         "ফিউ-শট উদাহরণ হলো প্রম্পটে দেওয়া কয়েকটি নমুনা ইনপুট ও আউটপুটের জোড়া, ২–৮টি।"),
        ("The model finds the pattern and follows it.",
         "মডেল প্যাটার্ন ধরে নিয়ে সেটা মেনে চলে।")],
       [sh("ex", "hot", ("input and output pairs", "ইনপুট ও আউটপুটের জোড়া")), sh("model", "hot", ("follows the pattern", "প্যাটার্ন মানে"))],
       [ln("ex", "model", "to", state="hot")],
       [("2–8 pairs", "২–৮টি জোড়া"), ("a pattern to follow", "মানার প্যাটার্ন"), None]),

    st(("Not prose", "বর্ণনা নয়"),
       ("Examples beat a description", "বর্ণনার চেয়ে উদাহরণ ভালো"),
       [("Examples are often more reliable than a long description.",
         "লম্বা বর্ণনার চেয়ে উদাহরণ প্রায়ই বেশি নির্ভরযোগ্য।"),
        ("2–8 pairs work better than describing the task in prose.",
         "কথায় বর্ণনার চেয়ে ২–৮টি জোড়া বেশি ভালো কাজ করে।")],
       [sh("prose", "dim", ("describes in prose", "কথায় বর্ণনা")), sh("ex", "hot", ("2–8 pairs", "২–৮টি জোড়া")), sh("model", "hot")],
       [ln("prose", "model", "to", state="dim"), ln("ex", "model", "to", state="hot")],
       [("2–8 pairs", "২–৮টি জোড়া"), None, None]),

    st(("Cover", "কভার"),
       ("Cover the tricky cases", "কঠিন কেস কভার করুন"),
       [("Cover the common case, tricky edge cases, and format traps like multi-line input in your examples.",
         "উদাহরণে সাধারণ কেস, কঠিন এজ কেস আর মাল্টি-লাইন ইনপুটের মতো ফরম্যাট ট্র্যাপ রাখুন।"),
        ("An edge case is a tricky input, like sarcasm or mixed feelings, that the easy pattern does not cover.",
         "এজ কেস হলো কঠিন ইনপুট, যেমন স্যারকাজম বা মিশ্র অনুভূতি, যা সহজ প্যাটার্নে ধরা পড়ে না।")],
       [sh("common", "hot"), sh("edge", "hot", ("sarcasm, mixed feelings", "স্যারকাজম, মিশ্র অনুভূতি")),
        sh("trap", "hot", ("multi-line input", "মাল্টি-লাইন ইনপুট")), sh("model", "hot")],
       [ln("common", "model", "to", state="hot"), ln("edge", "model", "to", state="hot"), ln("trap", "model", "to", state="hot")],
       [None, None, None]),

    st(("Role", "রোল"),
       ("Role prompting: who to be", "রোল প্রম্পটিং: কী সাজবে"),
       [("Role prompting tells the model who to be, for example a senior copyeditor.",
         "রোল প্রম্পটিং মডেলকে বলে দেয় সে কী সাজবে, যেমন সিনিয়র কপিএডিটর।"),
        ("It changes style, how much it hedges, and depth.",
         "এতে স্টাইল, সে কতটা দাবি নরম করে, আর গভীরতা বদলে যায়।")],
       [sh("role", "hot", ("a senior copyeditor", "সিনিয়র কপিএডিটর")), sh("model", "hot", ("style, hedging, depth", "স্টাইল, দাবি নরম করা, গভীরতা"))],
       [ln("role", "model", "to", state="hot")],
       [None, ("style, hedging, depth", "স্টাইল, দাবি নরম করা, গভীরতা"), None]),

    st(("Persona", "পারসোনা"),
       ("A detailed persona beats a vague one", "বিস্তারিত পারসোনা ঝাপসার চেয়ে ভালো"),
       [("A persona is a detailed role with level, vocabulary, and tone.",
         "পারসোনা হলো স্তর, শব্দভান্ডার আর সুরসহ বিস্তারিত রোল।"),
        ("A detailed persona tends to beat a vague one, and it works best in the system message.",
         "বিস্তারিত পারসোনা ঝাপসা পারসোনার চেয়ে ভালো, আর সিস্টেম মেসেজে এটা সবচেয়ে ভালো কাজ করে।")],
       [sh("role", "dim", ("vague", "ঝাপসা")), sh("persona", "hot", ("level, vocabulary, tone", "স্তর, শব্দভান্ডার, সুর")), sh("model", "hot")],
       [ln("role", "model", "to", state="dim"), ln("persona", "model", "to", state="hot")],
       [None, None, ("system message", "সিস্টেম মেসেজ")]),

    st(("Not brain", "জ্ঞান নয়"),
       ("A persona is style, not knowledge", "পারসোনা স্টাইল, জ্ঞান নয়"),
       [("A persona gives style, not knowledge.",
         "পারসোনা স্টাইল দেয়, জ্ঞান দেয় না।"),
        ("When expertise matters, add retrieved knowledge (RAG): find the relevant text first and give it to the model.",
         "বিশেষজ্ঞতা দরকার হলে রিট্রিভ করা জ্ঞান (RAG) যোগ করুন: আগে দরকারি লেখা খুঁজে মডেলকে দিন।")],
       [sh("persona", "warn", ("style only", "শুধু স্টাইল")), sh("know", "hot", ("answers from that text", "সেই লেখা থেকে উত্তর")), sh("model", "hot")],
       [ln("persona", "model", "to", state="warn"), ln("know", "model", "to", state="hot")],
       [None, ("style, not knowledge", "স্টাইল, জ্ঞান নয়"), None],
       note=("warn", "Personas alone risk confident hallucination.",
             "শুধু পারসোনা থাকলে আত্মবিশ্বাসী হ্যালুসিনেশনের ঝুঁকি থাকে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Show examples, give a role, and add retrieved knowledge when expertise matters.",
         "উদাহরণ দেখান, রোল দিন, আর বিশেষজ্ঞতা দরকার হলে রিট্রিভ করা জ্ঞান যোগ করুন।")],
       [sh("ex"), sh("persona"), sh("know"), sh("model")],
       [ln("ex", "model", "to"), ln("persona", "model", "to"), ln("know", "model", "to")],
       [None, None, None],
       points=[("Examples are the spec: 2–8 pairs work better than describing the task in prose.",
                "উদাহরণই স্পেক: কথায় বর্ণনার চেয়ে ২–৮টি জোড়া বেশি ভালো কাজ করে।"),
               ("Cover the common case, tricky edge cases, and format traps like multi-line input in your examples.",
                "উদাহরণে সাধারণ কেস, কঠিন এজ কেস আর মাল্টি-লাইন ইনপুটের মতো ফরম্যাট ট্র্যাপ রাখুন।"),
               ("A detailed persona tends to beat a vague one, and it belongs in the system message.",
                "বিস্তারিত পারসোনা ঝাপসা পারসোনার চেয়ে ভালো, আর তা থাকবে সিস্টেম মেসেজে।"),
               ("A persona gives style, not knowledge. When expertise matters, add retrieved knowledge (RAG).",
                "পারসোনা স্টাইল দেয়, জ্ঞান দেয় না। বিশেষজ্ঞতা দরকার হলে রিট্রিভ করা জ্ঞান (RAG) যোগ করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
