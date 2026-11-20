"""Part 2 · 03 Chain-of-thought, ReAct & reflection patterns: three ways to let a model think out loud before it answers.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Question  Sub-title: "Without them, a model guesses at hard multi-step problems; with them, it can plan, look things up, and correct its own mistakes."
              Start here: "These patterns let a model think out loud before it answers."
  2 Steps     Start here: Chain-of-Thought (CoT) ("Making the model write its reasoning steps before the final answer. The extra tokens give the hard part more computation.").
              Body: "Q: 17×24 → A: 17×20=340, 17×4=68, 340+68=408"; "forcing the model to emit intermediate tokens allocates more computation to the hard part".
  3 Phrase    Start here: Zero-shot CoT ("Adding the phrase Let's think step by step to the prompt, with no examples at all."); "Showing worked steps, or adding Let's think step by step, improves math, logic, and multi-step answers."
  4 Vote      Start here: Self-consistency ("Asking for N separate reasoning chains and taking the answer that most of them give."); Body: "Self-consistency: sample N independent CoT chains, take the majority answer. ~+10% on GSM8K."
  5 Act       Start here: ReAct ("Reason plus act. The model loops: a thought, an action like a search, then an observation of the result.").
              Body, the ReAct trace: "Thought 1: I need the current weather in Dhaka to answer." and "Action 1: get_weather("Dhaka")".
  6 Observe   The trace: "Obs 1: "32°C, partly cloudy, humidity 78%"", "Thought 2: Now I can answer the user's question directly.", "finish("It's 32°C and humid in Dhaka right now.")".
              Start here: "ReAct loops think, act, observe. It is the pattern behind every modern AI agent."
  7 Reflect   Start here: Reflexion ("After each try, the model writes down what went wrong in memory, so the next try learns from it.");
              "On a task benchmark, Reflexion scored ~91% where plain ReAct scored ~40%."
  8 Cost      "A reasoning trace can be 10–50× longer than a direct answer. Use it only for hard tasks."; the callout: "Use it only when the task justifies it: math, planning, debugging, multi-hop reasoning. For extraction or simple Q&A, direct answers are faster and cheaper."
              Layman's voice: "all three techniques cost way more tokens (and therefore money and time)".
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ব্যবহারকারী"), 90, 75),
    node("model", "model", ("Model", "মডেল"), 280, 75),
    node("steps", "note", ("Reasoning steps", "যুক্তির ধাপ"), 490, 75),
    node("answer", "file", ("Answer", "উত্তর"), 680, 75),
    node("memory", "database", ("Memory", "মেমরি"), 280, 250),
    node("tool", "tool", ("get_weather", "get_weather"), 490, 250),
    node("vote", "chart", ("Majority answer", "বেশিরভাগের উত্তর"), 660, 250),
]

METRICS = [
    ("17 × 24", "১৭ × ২৪"),
    ("ReAct score", "ReAct স্কোর"),
    ("Reflexion score", "Reflexion স্কোর"),
    ("Trace vs direct answer", "ট্রেস বনাম সরাসরি উত্তর"),
]

CAPTION = (
    "Example: a weather question, and a few numbers from this section.",
    "উদাহরণ: একটি আবহাওয়ার প্রশ্ন, আর এই সেকশনের কয়েকটি সংখ্যা।",
)

STEPS = [
    st(("Question", "প্রশ্ন"),
       ("A hard question with several steps", "কয়েক ধাপের একটি কঠিন প্রশ্ন"),
       [("A user asks a hard question that takes several steps. Without help, the model guesses at the answer.",
         "ব্যবহারকারী এমন একটি কঠিন প্রশ্ন করে, যার উত্তরে কয়েক ধাপ লাগে। সাহায্য ছাড়া মডেল আন্দাজে উত্তর দেয়।"),
        ("Three patterns fix this. They let the model think out loud before it answers.",
         "তিনটি প্যাটার্ন এর সমাধান দেয়। এগুলো মডেলকে উত্তরের আগে জোরে জোরে ভাবতে দেয়।")],
       [sh("user", "hot", ("asks", "প্রশ্ন করে")), sh("model"), sh("answer", "warn", ("a guess", "আন্দাজ"))],
       [ln("user", "model", "to", state="hot"), ln("model", "answer", "to", state="warn")],
       [None, None, None, None]),

    st(("Steps", "ধাপ"),
       ("Chain-of-thought: write the steps first", "চেইন-অফ-থট: আগে ধাপগুলো লেখা"),
       [("Chain-of-thought makes the model write its reasoning steps before the final answer. The extra tokens give the hard part more computation.",
         "চেইন-অফ-থট মডেলকে চূড়ান্ত উত্তরের আগে যুক্তির ধাপ লিখতে বলে। বাড়তি টোকেন কঠিন অংশের জন্য বেশি কম্পিউটেশন দেয়।"),
        ("A worked example: 17 × 24 is 17 × 20 = 340, then 17 × 4 = 68, then 340 + 68 = 408.",
         "একটা ওয়ার্কড উদাহরণ: ১৭ × ২৪ হলো ১৭ × ২০ = ৩৪০, তারপর ১৭ × ৪ = ৬৮, তারপর ৩৪০ + ৬৮ = ৪০৮।")],
       [sh("user", "dim"), sh("model", "hot", ("writes steps", "ধাপ লেখে")),
        sh("steps", "hot", ("17×20=340, 17×4=68", "১৭×২০=৩৪০, ১৭×৪=৬৮")), sh("answer", "hot", ("408", "৪০৮"))],
       [ln("user", "model", "to", state="dim"), ln("model", "steps", "to", state="hot"), ln("steps", "answer", "to", state="hot")],
       ["408", None, None, None],
       note=("insight",
             "The model must write these steps as tokens. That is what gives the hard part more computation.",
             "মডেলকে এই ধাপগুলো টোকেন হিসেবে লিখতে হয়। তাতেই কঠিন অংশ বেশি কম্পিউটেশন পায়।"),
       changes=[("+", "Reasoning steps come before the answer", "উত্তরের আগে যুক্তির ধাপ আসে")]),

    st(("Phrase", "বাক্য"),
       ("One phrase can ask for the steps", "একটি বাক্যেই ধাপ চাওয়া যায়"),
       [("Zero-shot chain-of-thought adds the phrase <em>Let's think step by step</em> to the prompt, with no examples at all.",
         "জিরো-শট CoT প্রম্পটে শুধু <em>Let's think step by step</em> বাক্যটা যোগ করে, কোনো উদাহরণ ছাড়াই।"),
        ("Showing worked steps, or adding this phrase, improves math, logic and multi-step answers.",
         "কাজের ধাপ দেখালে বা এই বাক্য যোগ করলে অঙ্ক, যুক্তি আর মাল্টি-স্টেপ উত্তর ভালো হয়।")],
       [sh("user", "hot", ("adds a phrase", "বাক্য যোগ করে")), sh("model", "hot"), sh("steps", "hot")],
       [ln("user", "model", "to", state="hot"), ln("model", "steps", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "No examples are needed", "কোনো উদাহরণ লাগে না")]),

    st(("Vote", "ভোট"),
       ("Self-consistency: take the majority answer", "সেলফ-কনসিস্টেন্সি: বেশিরভাগের উত্তর নেওয়া"),
       [("Self-consistency asks for N separate reasoning chains and takes the answer that most of them give.",
         "সেলফ-কনসিস্টেন্সি N-টা আলাদা যুক্তির চেইন চায় আর যে উত্তরটা বেশিরভাগ চেইনে আসে সেটা নেয়।"),
        ("On GSM8K this gives about +10%.",
         "GSM8K-তে এতে প্রায় +১০% পাওয়া যায়।")],
       [sh("model", "hot"), sh("steps", "hot", ("N separate chains", "N-টা আলাদা চেইন")), sh("vote", "hot"), sh("answer", "hot")],
       [ln("model", "steps", "to", state="hot"), ln("steps", "vote", "to", state="hot"), ln("vote", "answer", "to", state="hot")],
       [None, None, None, None],
       changes=[("+", "About +10% on GSM8K", "GSM8K-তে প্রায় +১০%")]),

    st(("Act", "অ্যাকশন"),
       ("ReAct: think, then act", "ReAct: আগে ভাবা, তারপর করা"),
       [("ReAct stands for reason plus act. The model loops: a thought, an action like a search, then an observation of the result.",
         "ReAct মানে Reason আর Act মিলিয়ে। মডেল পালা করে চলে: একটা ভাবনা, একটা অ্যাকশন যেমন সার্চ, তারপর ফলাফলের পর্যবেক্ষণ।"),
        ("Thought 1: I need the current weather in Dhaka to answer. Action 1: <code>get_weather(\"Dhaka\")</code>.",
         "ভাবনা ১: উত্তর দিতে ঢাকার এখনকার আবহাওয়া দরকার। অ্যাকশন ১: <code>get_weather(\"Dhaka\")</code>।")],
       [sh("model", "hot", ("Thought 1", "ভাবনা ১")), sh("tool", "hot", ("location: Dhaka", "location: Dhaka"))],
       [ln("model", "tool", "to", state="hot", label=("Action 1", "অ্যাকশন ১"))],
       [None, "~40%", None, None],
       changes=[("+", "The model asked a tool for the weather", "মডেল একটা টুলের কাছে আবহাওয়া চাইল")]),

    st(("Observe", "পর্যবেক্ষণ"),
       ("The result comes back and the model finishes", "ফলাফল ফিরে আসে, আর মডেল শেষ করে"),
       [("The tool's result returns as an observation: 32°C, partly cloudy, humidity 78%. The second thought is: now I can answer.",
         "টুলের ফলাফল পর্যবেক্ষণ হয়ে ফিরে আসে: ৩২°C, আংশিক মেঘলা, আর্দ্রতা ৭৮%। দ্বিতীয় ভাবনা: এখন সরাসরি উত্তর দেওয়া যায়।"),
        ("The model finishes with the answer: it’s 32°C and humid in Dhaka right now.",
         "মডেল উত্তর দিয়ে শেষ করে: ঢাকায় এখন ৩২°C আর আর্দ্র আবহাওয়া।")],
       [sh("tool", "hot", ("32°C, partly cloudy", "৩২°C, আংশিক মেঘলা")), sh("model", "hot", ("Thought 2", "ভাবনা ২")), sh("answer", "hot", ("finish", "finish"))],
       [ln("tool", "model", "to", state="hot", label=("Observation 1", "পর্যবেক্ষণ ১")), ln("model", "answer", "to", state="hot", label=("finish", "finish"))],
       [None, "~40%", None, None],
       note=("insight",
             "ReAct loops think, act, observe. It is the pattern behind every modern AI agent.",
             "ReAct-এ ভাবা, করা, দেখা চক্রাকারে চলে। আজকের প্রতিটি AI এজেন্টের পেছনে এই প্যাটার্ন।")),

    st(("Reflect", "রিফ্লেকশন"),
       ("Reflexion: write down what went wrong", "রিফ্লেকশন: কোথায় ভুল হলো তা লিখে রাখা"),
       [("After each try, the model writes down what went wrong in memory. The next try learns from it.",
         "প্রতিটি চেষ্টার পর মডেল কোথায় ভুল হলো তা মেমরিতে লিখে রাখে, যাতে পরের চেষ্টা সেখান থেকে শেখে।"),
        ("On a task benchmark, Reflexion scored about 91% where plain ReAct scored about 40%.",
         "একটা টাস্ক বেঞ্চমার্কে Reflexion প্রায় ৯১% পেয়েছে, যেখানে সাধারণ ReAct পেয়েছে প্রায় ৪০%।")],
       [sh("model", "hot", ("reflects", "ভেবে দেখে")), sh("memory", "hot", ("what went wrong", "কোথায় ভুল হলো")), sh("tool", "dim")],
       [ln("model", "memory", "both", state="hot", label=("reflection", "রিফ্লেকশন")), ln("model", "tool", "to", state="dim")],
       [None, "~40%", "~91%", None],
       changes=[("+", "The next try starts from what went wrong", "পরের চেষ্টা শুরু হয় ভুলের শিক্ষা থেকে")]),

    st(("Cost", "খরচ"),
       ("Thinking costs tokens", "ভাবনার খরচ আছে"),
       [("A reasoning trace can be 10–50× longer than a direct answer. All three patterns cost more tokens, and so more money and time.",
         "রিজনিং ট্রেস সরাসরি উত্তরের ১০–৫০ গুণ লম্বা হতে পারে। তিনটি প্যাটার্নেই টোকেন বেশি লাগে, তাই খরচ আর সময়ও বেশি।"),
        ("Use them for hard tasks: math, planning, debugging, multi-hop reasoning. For extraction or simple Q&amp;A, a direct answer is faster and cheaper.",
         "কঠিন কাজেই এগুলো ব্যবহার করুন: অঙ্ক, প্ল্যানিং, ডিবাগিং, মাল্টি-হপ রিজনিং। এক্সট্রাকশন বা সহজ Q&amp;A-তে সরাসরি উত্তরই দ্রুত ও সস্তা।")],
       [sh("user"), sh("model"), sh("steps", "warn", ("10–50× longer", "১০–৫০ গুণ লম্বা")), sh("answer")],
       [ln("user", "model", "to"), ln("model", "steps", "to", state="warn"), ln("steps", "answer", "to", state="warn")],
       [None, None, None, "10–50×"],
       note=("warn",
             "Use it only when the task justifies it. For simple questions, a direct answer is faster and cheaper.",
             "কাজটা দাবি করলে তবেই ব্যবহার করুন। সহজ প্রশ্নে সরাসরি উত্তরই দ্রুত ও সস্তা।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Three patterns, one idea: let the model think out loud before it answers.",
         "তিনটি প্যাটার্ন, একটাই কথা: উত্তরের আগে মডেলকে জোরে জোরে ভাবতে দিন।")],
       [sh("user"), sh("model"), sh("steps"), sh("answer"), sh("tool"), sh("memory")],
       [ln("user", "model", "to"), ln("model", "steps", "to"), ln("steps", "answer", "to"), ln("model", "tool", "to"), ln("model", "memory", "to")],
       [None, None, None, None],
       points=[("Showing worked steps, or adding Let's think step by step, improves math, logic, and multi-step answers.",
                "কাজের ধাপ দেখালে বা Let's think step by step যোগ করলে অঙ্ক, যুক্তি আর মাল্টি-স্টেপ উত্তর ভালো হয়।"),
               ("ReAct loops think, act, observe. It is the pattern behind every modern AI agent.",
                "ReAct-এ ভাবা, করা, দেখা চক্রাকারে চলে। আজকের প্রতিটি AI এজেন্টের পেছনে এই প্যাটার্ন।"),
               ("On a task benchmark, Reflexion scored about 91% where plain ReAct scored about 40%.",
                "একটা টাস্ক বেঞ্চমার্কে Reflexion প্রায় ৯১% পেয়েছে, যেখানে সাধারণ ReAct পেয়েছে প্রায় ৪০%।"),
               ("A reasoning trace can be 10–50× longer than a direct answer. Use it only for hard tasks.",
                "রিজনিং ট্রেস সরাসরি উত্তরের ১০–৫০ গুণ লম্বা হতে পারে। শুধু কঠিন কাজে ব্যবহার করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
