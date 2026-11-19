"""Part 1 · 07 Function calling & tool use: the model asks for a tool, your code runs it, the result goes back, the model answers.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Tools      "You supply a list of tools as JSON Schema (function name, parameters, description)." "Tool names and descriptions are inserted verbatim into the prompt."
  2 Ask        The code: messages=[{"role": "user", "content": "Weather in Dhaka?"}], tools=tools.
  3 Decide     Sub-title: "emit a structured request to invoke a tool ... instead of free-form prose. The model doesn't execute: it decides what to call and with what arguments".
  4 Run        The code: result = get_weather(**tool.input)  # your code. Start here: "your code runs the tool".
  5 Result     The code: the tool's result comes back to your code (# feed result back).
  6 Feed back  The code: "# feed result back, model produces final answer". Start here: "the result goes back, and it repeats".
  7 Answer     The same comment: "model produces final answer". Start here: "until the task is done".
  8 In parallel  "Parallel tool calls: ... can emit multiple independent calls per turn: the model decides what can run concurrently."
  9 Remember   The three "remember" points of the Start here box.

The only number-like content is the example question and the two example cities.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("User", "ব্যবহারকারী"), 100, 175),
    node("app", "server", ("Your code", "আপনার কোড"), 345, 175),
    node("tools", "file", ("Tool list", "টুলের তালিকা"), 345, 52),
    node("model", "model", ("Model", "মডেল"), 610, 52),
    node("tool", "tool", ("get_weather", "get_weather"), 455, 300),
    node("tool2", "tool", ("get_weather", "get_weather"), 660, 300),
]

METRICS = [
    ("Model calls", "মডেল কল"),
    ("Tool runs", "টুল চলেছে"),
    ("Who runs the tool", "টুল কে চালায়"),
]

CAPTION = (
    "Example: the question is “Weather in Dhaka?” and the tool is get_weather.",
    "উদাহরণ: প্রশ্ন হলো “Weather in Dhaka?” আর টুল হলো get_weather।",
)

YOUR = ("your code", "আপনার কোড")
DHAKA = ("location: Dhaka", "location: Dhaka")
SYLHET = ("location: Sylhet", "location: Sylhet")

STEPS = [
    st(("Tools", "টুল"),
       ("List the tools", "টুলগুলোর তালিকা বানান"),
       [("Start with a list of tools. Each tool has a name, a description, and its parameters, written as JSON Schema.",
         "শুরুতে টুলের একটা তালিকা বানান। প্রতিটি টুলের থাকে নাম, বর্ণনা আর প্যারামিটার, যা JSON Schema আকারে লেখা হয়।"),
        ("Your code holds this list. The model has not seen it yet.",
         "তালিকাটা থাকে আপনার কোডের কাছে। মডেল এখনো সেটা দেখেনি।")],
       [sh("tools", "hot", ("JSON Schema", "JSON Schema")), sh("app"), sh("tool", "dim")],
       [ln("tools", "app", "to", 1200, "hot")],
       ["0", "0", None],
       note=("tip",
             "Tool names and descriptions go into the prompt as you write them. Give them the care you give a prompt.",
             "টুলের নাম আর বর্ণনা যেমন লিখবেন, প্রম্পটে হুবহু তেমনই বসে যায়। প্রম্পটের মতো যত্ন নিয়ে সেগুলো লিখুন।"),
       changes=[("+", "A tool list with one tool: <code>get_weather</code>",
                 "একটা টুলসহ টুলের তালিকা: <code>get_weather</code>")]),

    st(("Ask", "প্রশ্ন"),
       ("Send the question and the tools", "প্রশ্ন আর টুলের তালিকা পাঠান"),
       [("The user asks, “Weather in Dhaka?” Your code sends the question to the model together with the tool list.",
         "ব্যবহারকারী জিজ্ঞেস করে, “Weather in Dhaka?” আপনার কোড প্রশ্নটা টুলের তালিকাসহ মডেলের কাছে পাঠায়।"),
        ("The model reads the tool names and descriptions as part of its prompt.",
         "মডেল টুলের নাম আর বর্ণনা তার প্রম্পটের অংশ হিসেবেই পড়ে।")],
       [sh("user", "hot", ("Weather in Dhaka?", "Weather in Dhaka?")), sh("app", "hot"), sh("tools"),
        sh("model", "hot", ("reads the tools", "টুলগুলো পড়ে"))],
       [ln("user", "app", "to", 1000, "hot"), ln("tools", "app", "to", 1200),
        ln("app", "model", "to", 1400, "hot", ("question + tools", "প্রশ্ন + টুল"))],
       ["1", "0", None],
       changes=[("+", "The model gets the question and the tool list",
                 "মডেল প্রশ্ন আর টুলের তালিকা পেল")]),

    st(("Decide", "সিদ্ধান্ত"),
       ("The model asks for a tool", "মডেল একটা টুল চায়"),
       [("The model does not answer yet. Instead of plain text, it replies with a structured request: a tool name and its arguments.",
         "মডেল এখনই উত্তর দেয় না। সাধারণ লেখার বদলে সে একটা গোছানো অনুরোধ ফেরত দেয়: টুলের নাম আর তার আর্গুমেন্ট।"),
        ("Here the request is <code>get_weather</code> with the argument <code>location</code> set to <code>Dhaka</code>.",
         "এখানে অনুরোধটা হলো <code>get_weather</code>, আর <code>location</code> আর্গুমেন্টের মান <code>Dhaka</code>।")],
       [sh("user", "dim"), sh("app"), sh("model", "hot", ("asks for a tool", "টুল চায়")), sh("tool", "dim")],
       [ln("model", "app", "to", 1200, "hot", ("tool call", "টুল কল"))],
       ["1", "0", None],
       note=("insight",
             "The model decides what to call and with which arguments. It does not run anything.",
             "কী কল হবে আর কোন আর্গুমেন্ট দিয়ে, সেটা মডেল ঠিক করে। সে নিজে কিছু চালায় না।"),
       changes=[("+", "The reply is a tool call, not text", "উত্তরটা টুল কল, সাধারণ লেখা নয়")]),

    st(("Run", "চালানো"),
       ("Your code runs the tool", "আপনার কোড টুলটা চালায়"),
       [("Your code reads the request and calls the function itself, with the arguments the model gave.",
         "আপনার কোড অনুরোধটা পড়ে, মডেলের দেওয়া আর্গুমেন্ট দিয়ে ফাংশনটা নিজেই কল করে।"),
        ("The model cannot run anything. It only asked.",
         "মডেল কিছুই চালাতে পারে না। সে শুধু চেয়েছে।")],
       [sh("app", "hot", ("runs the tool", "টুলটা চালায়")), sh("tool", "hot", DHAKA), sh("model", "dim")],
       [ln("app", "tool", "to", 1000, "hot", ("call", "কল"))],
       ["1", "1", YOUR],
       note=("insight",
             "This is the whole idea of tool use: the model asks, and your code does the work.",
             "টুল ব্যবহারের মূল কথা এটাই: মডেল চায়, আর কাজটা করে আপনার কোড।"),
       changes=[("+", "The tool ran inside your code", "টুলটা চলল আপনার কোডের ভেতরে")]),

    st(("Result", "ফলাফল"),
       ("The tool returns a result", "টুল একটা ফলাফল ফেরত দেয়"),
       [("The function returns its result to your code. The model has not seen the result yet.",
         "ফাংশনটা তার ফলাফল আপনার কোডকে ফেরত দেয়। মডেল এখনো ফলাফলটা দেখেনি।")],
       [sh("app", "hot"), sh("tool", "hot", DHAKA), sh("model", "dim")],
       [ln("tool", "app", "to", 1000, "hot", ("result", "ফলাফল"))],
       ["1", "1", YOUR],
       changes=[("+", "Your code now holds the result", "ফলাফল এখন আপনার কোডের কাছে")]),

    st(("Feed back", "ফেরত পাঠান"),
       ("Send the result back", "ফলাফল মডেলকে ফেরত পাঠান"),
       [("Your code adds the result to the conversation and calls the model again.",
         "আপনার কোড ফলাফলটা কথোপকথনে যোগ করে আবার মডেলকে কল করে।"),
        ("That is the loop: the model asks, your code runs the tool, and the result goes back.",
         "এটাই লুপ: মডেল টুল চায়, আপনার কোড সেটা চালায়, আর ফলাফল ফিরে যায়।")],
       [sh("app", "hot"), sh("model", "hot", ("second call", "দ্বিতীয় কল")), sh("tool", "dim")],
       [ln("app", "model", "to", 1400, "hot", ("result", "ফলাফল"))],
       ["2", "1", YOUR],
       changes=[("~", "Model calls: 1 → 2", "মডেল কল: ১ → ২")]),

    st(("Answer", "উত্তর"),
       ("The model writes the answer", "মডেল উত্তর লেখে"),
       [("With the result in hand, the model answers in plain text. This time it asks for no tool.",
         "ফলাফল হাতে পেয়ে মডেল এবার সাধারণ লেখায় উত্তর দেয়। এবার সে কোনো টুল চায় না।"),
        ("Your code passes the answer to the user. Had the model asked for another tool, the loop would go round again.",
         "আপনার কোড উত্তরটা ব্যবহারকারীকে দেয়। মডেল আরেকটা টুল চাইলে লুপ আবার ঘুরত।")],
       [sh("user", "hot", ("gets the answer", "উত্তর পায়")), sh("app"), sh("model", "hot", ("final answer", "চূড়ান্ত উত্তর"))],
       [ln("model", "app", "to", 1200, "hot", ("answer", "উত্তর")), ln("app", "user", "to", 1000, "hot")],
       ["2", "1", YOUR],
       changes=[("+", "The user gets the answer", "ব্যবহারকারী উত্তর পেল")]),

    st(("In parallel", "একসাথে"),
       ("Several calls in one turn", "এক টার্নে কয়েকটা কল"),
       [("A model can ask for several independent calls in one reply, such as the weather in two cities.",
         "মডেল এক উত্তরেই কয়েকটা স্বাধীন কল চাইতে পারে, যেমন দুটো শহরের আবহাওয়া।"),
        ("Your code can run them at the same time. The model decides which calls are independent.",
         "আপনার কোড সেগুলো একই সময়ে চালাতে পারে। কোন কলগুলো স্বাধীন, সেটা মডেল ঠিক করে।")],
       [sh("app", "hot"), sh("model", "hot", ("asks for two", "দুটো চায়")), sh("tool", "hot", DHAKA), sh("tool2", "hot", SYLHET)],
       [ln("model", "app", "to", 1200, "hot", ("2 calls", "২টি কল")),
        ln("app", "tool", "to", 1000, "hot"), ln("app", "tool2", "to", 1000, "hot")],
       ["1", "2", YOUR],
       changes=[("+", "Two calls in one reply", "এক উত্তরে দুটো কল"),
                ("+", "Two tool runs at the same time", "একই সময়ে দুটো টুল চলে")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "মনে রাখার কথা"),
       [("Tool use is a loop between the model and your code.",
         "টুল ব্যবহার মানে মডেল আর আপনার কোডের মধ্যে একটা লুপ।")],
       [sh("user"), sh("app", "hot"), sh("model"), sh("tool")],
       [ln("app", "model", "both", 1600), ln("app", "tool", "both", 1400), ln("user", "app", "both", 1200)],
       ["2", "1", YOUR],
       points=[("The model only decides which tool to call and with which arguments. Your code runs the tool.",
                "মডেল শুধু ঠিক করে কোন টুল ডাকবে আর কোন আর্গুমেন্ট দেবে। টুল চালায় আপনার কোড।"),
               ("The loop: the model asks for a tool, your code runs it, the result goes back, and it repeats.",
                "লুপটা এমন: মডেল টুল চায়, আপনার কোড চালায়, ফলাফল ফেরত যায়, তারপর আবার।"),
               ("Clear tool names and descriptions matter as much as the model you pick.",
                "টুলের স্পষ্ট নাম আর বর্ণনা মডেল বাছাইয়ের মতোই জরুরি।")]),
]

WALK = walk(760, 350, NODES, METRICS, CAPTION, STEPS)
