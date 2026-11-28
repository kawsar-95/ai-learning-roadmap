"""Part 4 · 02 Conversation summarization & rolling memory: old turns shrink into a summary, recent turns stay word for word.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Growth    Sub-title: "A 50-turn chat is 50× the size of a 1-turn chat. Most of those tokens are noise — greetings, "can you clarify," half-finished thoughts."
              Start here: "Long chats use many tokens, and most of them are noise. Summarization squeezes old turns into a short summary, so the model stays on track without the growing cost."
  2 Roll      Start here: Rolling memory ("Old turns are condensed into a summary block, while the recent turns stay word for word.").
              Layman's voice: "The summary gets injected back at the front of the conversation as if it were the first thing you said."
  3 Trigger   Body: "Token-budget triggered: when history > N tokens (e.g. 4K), compress the oldest chunk into a summary block." "Turn-count triggered: every K turns, summarise the earliest K−1 into one block."
              "Semantic triggered: summarise when the topic shifts ... when a new user message is far from recent history." Remember: "There are three triggers to summarise".
  4 Schema    Remember: "A plain request to summarise the chat gives mush. Use a structured schema instead."; the schema keys user_goal, decisions_made, open_questions, key_facts_learned, entities, user_preferences, tool_results_to_remember.
  5 Levels    Start here: Hierarchical summarisation ("a summary of the oldest turns, a medium-detail summary of the middle turns, and recent turns word for word."); callout: "preserves both long-arc continuity and recent detail".
  6 Loss      Start here: Lossy compression ("Making something smaller by losing some detail, like shrinking a photo. Decisions, exact numbers, and quotes vanish first.").
              SVG note: "compression ratio typically 5–20×; information loss is the cost"; Bangla: "কমপ্রেশন রেশিও কাজভেদে আলাদা, তবে এর মূল্য হলো তথ্য হারানো।"
  7 Slot      Start here: Structured slot ("A separate place for key facts, kept outside the summary so they survive summarising."); layman's voice: "If something matters a lot, pull it out separately before you summarise".
  8 Index     Remember: "Treat the summary as an index, not the source of truth. Keep full transcripts for high-stakes chats."; body: "When a detail matters, retrieve from the original log."
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("turns", "queue", ("Old turns", "পুরোনো টার্ন"), 100, 75),
    node("model", "model", ("Model", "মডেল"), 290, 75),
    node("summary", "note", ("Summary block", "সারসংক্ষেপ ব্লক"), 490, 75),
    node("window", "file", ("Prompt", "প্রম্পট"), 680, 75),
    node("log", "storage", ("Full log", "পুরো লগ"), 100, 250),
    node("trigger", "clock", ("Trigger", "ট্রিগার"), 290, 250),
    node("slot", "database", ("Key facts", "মূল তথ্য"), 490, 250),
    node("mid", "note", ("Mid summary", "মাঝারি সারসংক্ষেপ"), 490, 250),
    node("recent", "queue", ("Recent", "সাম্প্রতিক"), 670, 250),
]

METRICS = [
    ("Chat size", "চ্যাটের আকার"),
    ("Compression", "কমপ্রেশন"),
    ("Trigger", "ট্রিগার"),
]

CAPTION = (
    "Example: a 50-turn chat that is summarized as it grows.",
    "উদাহরণ: ৫০ টার্নের একটি চ্যাট, যা বড় হতে হতে সারসংক্ষেপ করা হয়।",
)

WORD = ("word for word", "হুবহু")

STEPS = [
    st(("Growth", "বাড়তে থাকা"),
       ("A long chat costs more and more", "লম্বা চ্যাটের খরচ বাড়তেই থাকে"),
       [("A 50-turn chat is 50× the size of a 1-turn chat. Most of those tokens are noise: greetings, “can you clarify”, half-finished thoughts.",
         "৫০ বার কথা বলা চ্যাটের আকার ১ বারের চ্যাটের ৫০ গুণ। এই টোকেনগুলোর বেশিরভাগই অপ্রয়োজনীয়: শুভেচ্ছা, “একটু বুঝিয়ে বলবেন?”, আধা-শেষ চিন্তা।"),
        ("Summarization squeezes old turns into a short summary, so the model stays on track without the growing cost.",
         "সামারাইজেশন পুরোনো টার্নকে ছোট সারসংক্ষেপে চেপে ফেলে, ফলে মডেল ঠিক পথে থাকে অথচ খরচ বাড়তে থাকে না।")],
       [sh("turns", "warn", ("50 turns", "৫০ টার্ন")), sh("window", "hot")],
       [ln("turns", "window", "to", state="warn")],
       ["50×", None, None]),

    st(("Roll", "রোলিং"),
       ("Rolling memory: summarize the old, keep the new", "রোলিং মেমরি: পুরোনোটা সংক্ষেপ, নতুনটা হুবহু"),
       [("Rolling memory condenses old turns into a summary block, while the recent turns stay word for word.",
         "রোলিং মেমরিতে পুরোনো টার্ন সংক্ষেপ হয়ে একটি সারসংক্ষেপ ব্লকে পরিণত হয়, আর সাম্প্রতিক টার্নগুলো হুবহু থাকে।"),
        ("The summary goes back at the front of the conversation, as if it were the first thing you said.",
         "সারসংক্ষেপটা কথোপকথনের সামনে ফিরে বসে, যেন সেটাই আপনার বলা প্রথম কথা।")],
       [sh("turns", "hot"), sh("model", "hot", ("condenses", "সংক্ষেপ করে")), sh("summary", "hot"), sh("window", "hot"), sh("recent", "hot", WORD)],
       [ln("turns", "model", "to", state="hot"), ln("model", "summary", "to", state="hot"), ln("summary", "window", "to", state="hot"),
        ln("recent", "window", "to", state="hot")],
       [None, None, None],
       changes=[("-", "Old turns shrink into one block", "পুরোনো টার্ন একটি ব্লকে ছোট হয়ে যায়"),
                ("+", "Recent turns stay as they were", "সাম্প্রতিক টার্ন যেমন ছিল তেমনই থাকে")]),

    st(("Trigger", "ট্রিগার"),
       ("Three triggers say when to summarize", "তিনটি ট্রিগার বলে কখন সামারাইজ করবেন"),
       [("A token-budget trigger summarizes when the history is over N tokens, for example 4K. A turn-count trigger summarizes every K turns: the earliest K−1 go into one block.",
         "টোকেন-বাজেট ট্রিগার: হিস্ট্রি N টোকেন, যেমন ৪K, পার হলে সামারাইজ করে। টার্ন-কাউন্ট ট্রিগার: প্রতি K টার্ন পরপর আগের K−১ টার্ন একটি ব্লকে নেয়।"),
        ("A semantic trigger summarizes when the topic shifts, for example when a new message looks far from the recent history.",
         "সেম্যান্টিক ট্রিগার: বিষয় বদলালে সামারাইজ করে, যেমন নতুন বার্তা সাম্প্রতিক কথোপকথন থেকে অনেক দূরের মনে হলে।")],
       [sh("turns", "dim"), sh("trigger", "hot", ("three triggers", "তিনটি ট্রিগার")), sh("model", "hot", ("starts to summarize", "সামারাইজ শুরু করে"))],
       [ln("turns", "model", "to", state="dim"), ln("trigger", "model", "to", state="hot")],
       [None, None, ("4K tokens", "৪K টোকেন")]),

    st(("Schema", "স্কিমা"),
       ("Ask for a structured summary", "সারসংক্ষেপ চান স্ট্রাকচার্ড আকারে"),
       [("A plain request to summarize the chat gives mush. Use a structured schema instead: a fixed template of fields.",
         "শুধু চ্যাট সারসংক্ষেপ করতে বললে ঝাপসা ফল আসে। বদলে স্ট্রাকচার্ড স্কিমা ব্যবহার করুন: ফিল্ডের একটি স্থির ছক।"),
        ("It holds the user goal, the decisions made, the open questions, the facts learned, the entities, the preferences and the tool results to remember.",
         "এতে থাকে ইউজারের লক্ষ্য, নেওয়া সিদ্ধান্ত, খোলা প্রশ্ন, জানা তথ্য, নাম-আইডি, পছন্দ আর মনে রাখার মতো টুলের ফলাফল।")],
       [sh("turns", "dim"), sh("model", "hot", ("fills the schema", "ছক ভরে")), sh("summary", "hot", ("not mush", "ঝাপসা নয়"))],
       [ln("turns", "model", "to", state="dim"), ln("model", "summary", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Goal, decisions and open questions each have a field", "লক্ষ্য, সিদ্ধান্ত আর খোলা প্রশ্নের প্রত্যেকের নিজের ঘর")]),

    st(("Levels", "স্তর"),
       ("Hierarchical summaries keep both", "স্তরভিত্তিক সারসংক্ষেপে দুটোই থাকে"),
       [("Hierarchical summarisation has three levels: a summary of the oldest turns, a medium-detail summary of the middle turns, and the recent turns word for word.",
         "হায়ারার্কিক্যাল সামারাইজেশনে তিন স্তর: সবচেয়ে পুরোনো টার্নের সারসংক্ষেপ, মাঝের টার্নের মাঝারি বিস্তারের সারসংক্ষেপ, আর সাম্প্রতিক টার্ন হুবহু।"),
        ("This keeps both the long arc of the chat and the recent detail.",
         "এতে চ্যাটের দীর্ঘ ধারাবাহিকতা আর সাম্প্রতিক খুঁটিনাটি, দুটোই থাকে।")],
       [sh("summary", "hot", ("oldest turns", "সবচেয়ে পুরোনো")), sh("mid", "hot", ("middle turns", "মাঝের টার্ন")), sh("recent", "hot", WORD), sh("window", "hot")],
       [ln("summary", "window", "to", state="hot"), ln("mid", "window", "to", state="hot"), ln("recent", "window", "to", state="hot")],
       [None, None, None],
       changes=[("+", "Three levels of detail", "তিন স্তরের বিস্তার")]),

    st(("Loss", "হারানো"),
       ("Summaries lose detail", "সারসংক্ষেপে তথ্য হারায়"),
       [("Summarisation is lossy compression, like shrinking a photo. Decisions, exact numbers and quoted text are the first things to disappear.",
         "সামারাইজেশন লসি কমপ্রেশন, ছবি ছোট করার মতো। সিদ্ধান্ত, নির্দিষ্ট সংখ্যা ও উদ্ধৃতি সবার আগে হারায়।"),
        ("The compression ratio varies by task, but the price is lost detail.",
         "কমপ্রেশন রেশিও কাজভেদে আলাদা, তবে এর মূল্য হলো তথ্য হারানো।")],
       [sh("summary", "warn", ("details lost", "খুঁটিনাটি হারায়")), sh("window", "hot")],
       [ln("summary", "window", "to", state="warn")],
       [None, ("varies by task", "কাজভেদে আলাদা"), None],
       note=("warn",
             "Decisions, exact numbers and quoted text vanish first.",
             "সিদ্ধান্ত, নির্দিষ্ট সংখ্যা আর উদ্ধৃতি সবার আগে হারায়।")),

    st(("Slot", "স্লট"),
       ("Keep key facts in a slot of their own", "মূল তথ্য রাখুন আলাদা স্লটে"),
       [("Put the key facts in a separate structured slot, kept outside the summary, so they survive summarizing.",
         "গুরুত্বপূর্ণ তথ্য রাখুন সারসংক্ষেপের বাইরে আলাদা স্ট্রাকচার্ড স্লটে, যাতে সামারাইজ করার পরেও তথ্য টিকে থাকে।"),
        ("If something matters a lot, pull it out before you summarize.",
         "কোনো কিছু খুব জরুরি হলে সামারাইজ করার আগেই সেটা আলাদা করে নিন।")],
       [sh("slot", "hot", ("kept apart", "আলাদা রাখা")), sh("summary", "dim"), sh("window", "hot")],
       [ln("slot", "window", "to", state="hot"), ln("summary", "window", "to", state="dim")],
       [None, None, None],
       changes=[("+", "Key facts survive the summary", "মূল তথ্য সারসংক্ষেপের পরেও টিকে থাকে")]),

    st(("Index", "সূচি"),
       ("The summary is an index, not the truth", "সারসংক্ষেপ সূচির মতো, সত্যের উৎস নয়"),
       [("Treat the summary as an index, not the source of truth. When a detail matters, retrieve it from the original log.",
         "সারসংক্ষেপকে সূচির মতো ভাবুন, সত্যের উৎস নয়। কোনো খুঁটিনাটি জরুরি হলে মূল লগ থেকে ফিরে দেখুন।"),
        ("For high-stakes chats, keep the full transcript, even after summarizing into the prompt.",
         "গুরুত্বপূর্ণ কথোপকথনের পুরো ট্রান্সক্রিপ্ট রাখুন, প্রম্পটে সামারাইজ করার পরেও।")],
       [sh("summary", "hot", ("an index", "সূচি")), sh("log", "hot", ("source of truth", "সত্যের উৎস"))],
       [ln("summary", "log", "to", state="hot", label=("look up", "ফিরে দেখা"))],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Squeeze the old, keep the recent word for word, and keep the truth somewhere you can go back to.",
         "পুরোনোটা চেপে ছোট করুন, সাম্প্রতিকটা হুবহু রাখুন, আর সত্যটা এমন জায়গায় রাখুন যেখানে ফিরে যাওয়া যায়।")],
       [sh("turns"), sh("model"), sh("summary"), sh("window"), sh("recent"), sh("slot"), sh("log")],
       [ln("turns", "model", "to"), ln("model", "summary", "to"), ln("summary", "window", "to"), ln("recent", "window", "to"),
        ln("slot", "window", "to"), ln("summary", "log", "to")],
       [None, None, None],
       points=[("There are three triggers to summarise: a token budget, a turn count, or a topic shift.",
                "সামারাইজ করার তিনটি ট্রিগার: টোকেন-বাজেট, টার্নের সংখ্যা, আর বিষয় বদল।"),
               ("A plain request to summarise the chat gives mush. Use a structured schema instead.",
                "শুধু চ্যাট সারসংক্ষেপ করতে বললে ঝাপসা ফল আসে। বদলে স্ট্রাকচার্ড স্কিমা ব্যবহার করুন।"),
               ("Summaries lose detail: decisions, exact numbers, and quoted text disappear first.",
                "সারসংক্ষেপে তথ্য হারায়: সিদ্ধান্ত, নির্দিষ্ট সংখ্যা আর উদ্ধৃতি সবার আগে যায়।"),
               ("Treat the summary as an index, not the source of truth. Keep full transcripts for high-stakes chats.",
                "সারসংক্ষেপ সূচির মতো, সত্যের উৎস নয়। গুরুত্বপূর্ণ কথোপকথনের পুরো ট্রান্সক্রিপ্ট রাখুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
