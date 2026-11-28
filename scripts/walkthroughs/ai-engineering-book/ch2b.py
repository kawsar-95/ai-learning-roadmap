"""Part AI Engineering book · 03 Understanding Foundation Models: post-training, sampling and hallucination.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Pre-trained  Body: "A model that only went through pre-training is optimized to predict the next token of internet-like text, not to hold a conversation. It can also reproduce the racism, misinformation, and rudeness present in its training data."
  2 SFT          Body: "Supervised finetuning (SFT): the model is finetuned on curated (prompt, response) pairs written by trained labelers ... It learns to behave like an assistant rather than a text-completion engine."
  3 Preference   Body: "Preference finetuning: the model is further tuned to produce responses humans actually prefer. The classic approach, RLHF ... trains a reward model on human comparisons of response pairs."
  4 Token odds   Body: "At each step it computes a probability distribution over every token in its vocabulary, then samples one." "most systems sample proportionally to probability".
  5 Temperature  Body: "Higher temperature flattens the distribution ... more creative but less predictable. Lower temperature sharpens it toward the most likely token."
  6 Top-k, top-p Body: "Top-k restricts sampling to only the k most likely tokens ... Top-p keeps the smallest set of tokens whose cumulative probability passes a threshold p."
  7 Same prompt  Body: "the same prompt can get different answers on different runs ... fixing temperature, top-p, top-k, and a random seed helps. It can never be fully eliminated".
  8 Hallucinate  Body: "Hallucination, where a model confidently states something false or unverifiable ... techniques like RLHF do not reliably fix it." Start here: "RLHF does not reliably fix hallucination".
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("web", "file", ("Internet-like text", "ইন্টারনেটের মতো লেখা"), 110, 162),
    node("pre", "model", ("Model", "মডেল"), 380, 162),
    node("sft", "file", ("SFT pairs", "SFT জোড়া"), 380, 162),
    node("pref", "key", ("Preference tuning", "প্রেফারেন্স টিউনিং"), 625, 162),
    node("prompt", "user", ("Prompt", "প্রম্পট"), 110, 162),
    node("temp", "tool", ("Temperature", "টেম্পারেচার"), 380, 162),
    node("topp", "tool", ("Top-k, top-p", "top-k, top-p"), 380, 162),
    node("odds", "chart", ("Next-token odds", "পরের টোকেনের সম্ভাবনা"), 625, 162),
    node("ans1", "note", ("Answer 1", "উত্তর ১"), 650, 80),
    node("ans2", "note", ("Answer 2", "উত্তর ২"), 650, 244),
    node("hall", "note", ("Confidently false", "আত্মবিশ্বাসে ভুল"), 650, 162),
]

METRICS = [
    ("Temperature", "টেম্পারেচার"),
    ("Top-k keeps", "top-k রাখে"),
    ("Top-p keeps", "top-p রাখে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Pre-trained", "প্রি-ট্রেনিং"),
       ("Pre-training is not enough", "শুধু প্রি-ট্রেনিং যথেষ্ট নয়"),
       [("A model that only went through pre-training is optimized to predict the next token of internet-like text, not to hold a conversation.",
         "যে মডেল শুধু প্রি-ট্রেনিং পেয়েছে, সে ইন্টারনেটের মতো লেখার পরের টোকেন অনুমান করতে ওপটিমাইজ করা, কথোপকথন চালাতে নয়।"),
        ("It can also reproduce the racism, misinformation, and rudeness present in its training data.",
         "সে ট্রেনিং ডেটার বর্ণবাদ, ভুল তথ্য আর রূঢ়তাও নকল করতে পারে।")],
       [sh("web", "hot"), sh("pre", "warn", ("pre-training only", "শুধু প্রি-ট্রেনিং"))],
       [ln("web", "pre", "to", state="warn")],
       [None, None, None]),

    st(("SFT", "SFT"),
       ("Stage one: supervised finetuning", "প্রথম ধাপ: সুপারভাইজড ফাইনটিউনিং"),
       [("In supervised finetuning (SFT), the model is finetuned on curated (prompt, response) pairs written by trained labelers.",
         "সুপারভাইজড ফাইনটিউনিংয়ে (SFT) প্রশিক্ষিত লেবেলারদের লেখা বাছাই করা (prompt, response) জোড়া দিয়ে মডেলকে ফাইনটিউন করা হয়।"),
        ("It learns to behave like an assistant rather than a text-completion engine.",
         "সে টেক্সট-কমপ্লিশন ইঞ্জিনের বদলে অ্যাসিস্ট্যান্টের মতো আচরণ শেখে।")],
       [sh("pre", "dim", x=110), sh("sft", "hot", ("(prompt, response) pairs", "(prompt, response) জোড়া"))],
       [ln("pre", "sft", "to", state="hot")],
       [None, None, None]),

    st(("Preference", "প্রেফারেন্স"),
       ("Stage two: preference finetuning", "দ্বিতীয় ধাপ: প্রেফারেন্স ফাইনটিউনিং"),
       [("In preference finetuning, the model is further tuned to produce responses humans actually prefer.",
         "প্রেফারেন্স ফাইনটিউনিংয়ে মডেলকে আরও টিউন করা হয়, যাতে মানুষ আসলে যে উত্তর পছন্দ করে সে তা দেয়।"),
        ("The classic approach, RLHF, trains a reward model on human comparisons of response pairs.",
         "প্রচলিত উপায় RLHF উত্তরের জোড়ার ওপর মানুষের তুলনা দিয়ে একটা রিওয়ার্ড মডেল ট্রেইন করে।")],
       [sh("pre", "dim", x=100), sh("sft", "dim", x=340), sh("pref", "hot", ("RLHF", "RLHF"))],
       [ln("pre", "sft", "to", state="dim"), ln("sft", "pref", "to", state="hot")],
       [None, None, None]),

    st(("Token odds", "টোকেনের সম্ভাবনা"),
       ("A probability for every token", "প্রতিটি টোকেনের সম্ভাবনা"),
       [("At each step the model computes a probability distribution over every token in its vocabulary, then samples one.",
         "প্রতিটি ধাপে মডেল তার ভোকাবুলারির প্রতিটি টোকেনের ওপর একটা সম্ভাব্যতার বণ্টন হিসাব করে, তারপর একটা বাছে।"),
        ("Most systems sample proportionally to probability.",
         "বেশিরভাগ সিস্টেম সম্ভাব্যতা অনুযায়ী বাছে।")],
       [sh("prompt", "hot"), sh("pre", "hot"), sh("odds", "hot", ("sampled by probability", "সম্ভাব্যতা অনুযায়ী বাছা"))],
       [ln("prompt", "pre", "to", state="hot"), ln("pre", "odds", "to", state="hot")],
       [None, None, None],
       note=("tip", "Always picking the single most likely token is called greedy sampling. It is safe but tends to produce dull, repetitive text.",
             "সবসময় একটাই সবচেয়ে সম্ভাব্য টোকেন বাছাকে বলে গ্রিডি স্যাম্পলিং। এটা নিরাপদ, কিন্তু একঘেয়ে আর পুনরাবৃত্তিমূলক লেখা বানায়।")),

    st(("Temperature", "টেম্পারেচার"),
       ("Temperature flattens or sharpens", "টেম্পারেচার সমান বা তীক্ষ্ণ করে"),
       [("Temperature rescales the raw scores (logits) before converting them to probabilities. Higher temperature flattens the distribution.",
         "টেম্পারেচার সম্ভাব্যতায় বদলানোর আগে র স্কোর (logits) নতুন করে মাপে। বেশি টেম্পারেচার বণ্টনকে সমান করে দেয়।"),
        ("Rare tokens get more of a chance, so output is more creative but less predictable. Lower temperature sharpens it toward the most likely token.",
         "বিরল টোকেন বেশি সুযোগ পায়, তাই আউটপুট বেশি সৃজনশীল কিন্তু কম অনুমানযোগ্য হয়। কম টেম্পারেচার সবচেয়ে সম্ভাব্য টোকেনের দিকে তীক্ষ্ণ করে।")],
       [sh("temp", "hot"), sh("odds", "hot", ("flatter or sharper", "সমান বা তীক্ষ্ণ"))],
       [ln("temp", "odds", "to", state="hot")],
       [("Higher: flatter", "বেশি: সমান"), None, None]),

    st(("Top-k, top-p", "top-k, top-p"),
       ("Top-k and top-p cut the list", "top-k আর top-p তালিকা ছাঁটে"),
       [("Top-k restricts sampling to only the k most likely tokens, cutting compute and keeping output more focused.",
         "top-k শুধু সবচেয়ে সম্ভাব্য k-টা টোকেন থেকে বাছে, তাই কম্পিউট কমে আর আউটপুট বেশি কেন্দ্রীভূত থাকে।"),
        ("Top-p (nucleus sampling) keeps the smallest set of tokens whose cumulative probability passes a threshold p. The number of candidates then adapts to how confident the model is at each step.",
         "top-p (নিউক্লিয়াস স্যাম্পলিং) সবচেয়ে ছোট টোকেনের সেট রাখে, যার মোট সম্ভাব্যতা একটা সীমা p পার হয়। তাই প্রতি ধাপে মডেল কতটা নিশ্চিত, তার ওপর প্রার্থীর সংখ্যা বদলায়।")],
       [sh("topp", "hot"), sh("odds", "hot", ("fewer tokens left", "কম টোকেন বাকি"))],
       [ln("topp", "odds", "to", state="hot")],
       [None, ("the most likely", "সবচেয়ে সম্ভাব্য"), ("smallest set past p", "সবচেয়ে ছোট সেট, p পার")]),

    st(("Same prompt", "একই প্রম্পট"),
       ("The same prompt, different answers", "একই প্রম্পট, আলাদা উত্তর"),
       [("Because sampling is probabilistic, the same prompt can get different answers on different runs.",
         "স্যাম্পলিং সম্ভাব্যতা-নির্ভর, তাই একই প্রম্পটে প্রতিবার আলাদা উত্তর আসতে পারে।"),
        ("Fixing temperature, top-p, top-k, and a random seed helps. It can never be fully eliminated.",
         "temperature, top-p, top-k আর একটা র‍্যান্ডম সিড ঠিক করলে কমে। কিন্তু পুরোপুরি যায় না।")],
       [sh("prompt", "hot"), sh("pre", "hot"), sh("ans1", "hot"), sh("ans2", "warn")],
       [ln("prompt", "pre", "to", state="hot"), ln("pre", "ans1", "to", state="hot"), ln("pre", "ans2", "to", state="warn")],
       [None, None, None]),

    st(("Hallucinate", "হ্যালুসিনেশন"),
       ("Hallucination is not reliably fixed", "হ্যালুসিনেশন নির্ভরযোগ্যভাবে ঠিক হয় না"),
       [("Hallucination is when a model confidently states something false or unverifiable.",
         "হ্যালুসিনেশন হলো মডেল আত্মবিশ্বাসের সাথে এমন কিছু বলে, যা ভুল বা যাচাই করা যায় না।"),
        ("Techniques like RLHF do not reliably fix it.",
         "RLHF-এর মতো কৌশল এটা নির্ভরযোগ্যভাবে ঠিক করে না।")],
       [sh("pre", "hot", x=110), sh("pref", "dim", ("does not reliably fix it", "নির্ভরযোগ্যভাবে ঠিক করে না"), x=380), sh("hall", "warn")],
       [ln("pre", "pref", "to", state="dim"), ln("pref", "hall", "to", state="warn")],
       [None, None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
