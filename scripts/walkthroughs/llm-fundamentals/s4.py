"""LLM Fundamentals · 04 Sampling parameters: how one list of next-token chances becomes text, and which knobs change the pick.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Logits     Body: "A model outputs a probability distribution over every token in its vocabulary." Table: "Logits: The raw scores the model gives each token before they are turned into chances."
  2 Chances    Start here: "At each step, the model gives every possible next token a chance of being picked." "All the chances add up to 100%." "Sampling: Picking the next token from that list of chances."
  3 Temperature Table: "The randomness dial. Low (0) makes answers predictable; above 1 makes them more varied."
  4 Keep       Table: top_k "Keep only the k most likely tokens ... k=1 always takes the top one."; top_p "Keep the fewest top tokens whose chances add up to at least p, such as 0.9"; min_p "Drop tokens whose chance is below min_p times the top token's chance."
  5 Penalties  Table: "frequency_penalty discourages repeating the same tokens; presence_penalty pushes toward new topics."
  6 Settings   "Use temperature 0 for code, JSON, classification, and math, and about 0.7–1.0 for chat." "Raise temperature to 1.0–2.0 for creative writing and brainstorming."
  7 Remember   "Change temperature or top_p, usually not both (min_p is mainly found in open-source stacks). Do not stack tight top_k and top_p values."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("logits", "model", ("Logits", "লজিট"), 120, 90),
    node("probs", "chart", ("Chances", "সম্ভাবনা"), 380, 90),
    node("temp", "tool", ("temperature", "temperature"), 640, 90),
    node("topk", "tool", ("top_k", "top_k"), 110, 250),
    node("topp", "tool", ("top_p / min_p", "top_p / min_p"), 300, 250),
    node("pen", "tool", ("Penalties", "পেনাল্টি"), 500, 250),
    node("pick", "note", ("Picked token", "বাছা টোকেন"), 650, 250),
]

METRICS = [
    ("Temperature", "temperature"),
    ("Tokens kept", "রাখা টোকেন"),
    ("Pick", "বাছাই"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Logits", "লজিট"),
       ("The model gives raw scores", "মডেল কাঁচা স্কোর দেয়"),
       [("A model outputs a probability distribution over every token in its vocabulary.",
         "মডেল তার ভোকাবুলারির প্রতিটি টোকেনের ওপর একটা প্রোবাবিলিটি ডিস্ট্রিবিউশন দেয়।"),
        ("Logits are the raw scores the model gives each token before they are turned into chances.",
         "লজিট হলো সম্ভাবনায় বদলানোর আগে মডেল প্রতিটি টোকেনকে যে কাঁচা স্কোর দেয়।")],
       [sh("logits", "hot", ("raw scores", "কাঁচা স্কোর")), sh("probs", "dim")],
       [ln("logits", "probs", "to", state="hot")],
       [None, None, None]),

    st(("Chances", "সম্ভাবনা"),
       ("Chances, then a pick", "সম্ভাবনা, তারপর বাছাই"),
       [("At each step, the model gives every possible next token a chance of being picked. All the chances add up to 100%.",
         "প্রতিটি ধাপে মডেল সম্ভাব্য প্রতিটি পরের টোকেনকে বাছাই হওয়ার একটা সম্ভাবনা দেয়। সব সম্ভাবনা যোগ করলে ১০০% হয়।"),
        ("Sampling is picking the next token from that list of chances.",
         "স্যাম্পলিং মানে সম্ভাবনার সেই তালিকা থেকে পরের টোকেন বেছে নেওয়া।")],
       [sh("logits", "dim"), sh("probs", "hot", ("adds up to 100%", "যোগফল ১০০%")), sh("pick", "hot")],
       [ln("logits", "probs", "to", state="dim"), ln("probs", "pick", "to", state="hot")],
       [None, None, None]),

    st(("Temperature", "temperature"),
       ("temperature is the randomness dial", "temperature হলো র‍্যান্ডমনেসের নব"),
       [("Low (0) makes answers predictable. Above 1 makes them more varied.",
         "কম (০) দিলে উত্তর আগে থেকে আন্দাজ করা যায়। ১-এর বেশি দিলে উত্তরে বৈচিত্র্য বাড়ে।")],
       [sh("probs", "dim"), sh("temp", "hot", ("0 = predictable", "০ = আন্দাজ করা যায়")), sh("pick", "hot")],
       [ln("probs", "temp", "to", state="dim"), ln("temp", "pick", "to", state="hot")],
       [(("0"), ("০")), None, (("predictable at 0"), ("০ হলে আন্দাজ করা যায়"))]),

    st(("Keep", "রাখা"),
       ("top_k, top_p and min_p keep some tokens", "top_k, top_p, min_p কিছু টোকেন রাখে"),
       [("top_k keeps only the k most likely tokens. k=1 always takes the top one.",
         "top_k শুধু সবচেয়ে সম্ভাব্য k-টি টোকেন রাখে। k=১ মানে সবসময় সবার উপরেরটা।"),
        ("top_p keeps the fewest top tokens whose chances add up to at least p, such as 0.9. min_p drops tokens whose chance is below min_p times the top token's chance.",
         "top_p উপরের দিকের সবচেয়ে কম সংখ্যক টোকেন রাখে, যাদের সম্ভাবনা যোগ করলে অন্তত p হয়, যেমন ০.৯। min_p সেই টোকেনগুলো বাদ দেয়, যাদের সম্ভাবনা শীর্ষ টোকেনের সম্ভাবনার min_p গুণের চেয়ে কম।")],
       [sh("probs", "dim"), sh("topk", "hot", ("k=1: the top one", "k=১: সবার উপরেরটা")), sh("topp", "hot", ("p such as 0.9", "p যেমন ০.৯")), sh("pick", "hot")],
       [ln("topk", "topp", "to", state="hot"), ln("topp", "pick", "to", state="hot")],
       [None, (("fewest top tokens"), ("সবচেয়ে কম সংখ্যক টোকেন")), None]),

    st(("Penalties", "পেনাল্টি"),
       ("Penalties push away from repeats", "পেনাল্টি পুনরাবৃত্তি থেকে সরায়"),
       [("frequency_penalty discourages repeating the same tokens.",
         "frequency_penalty একই টোকেন বারবার বলা কমায়।"),
        ("presence_penalty pushes toward new topics.",
         "presence_penalty নতুন বিষয়ের দিকে ঠেলে দেয়।")],
       [sh("topp", "dim"), sh("pen", "hot"), sh("pick", "hot")],
       [ln("topp", "pen", "to", state="dim"), ln("pen", "pick", "to", state="hot")],
       [None, None, None]),

    st(("Settings", "সেটিংস"),
       ("Which temperature for which job", "কোন কাজে কোন temperature"),
       [("Use temperature 0 for code, JSON, classification, and math, and about 0.7–1.0 for chat.",
         "কোড, JSON, ক্লাসিফিকেশন আর গণিতে temperature ০ দিন; চ্যাটে মোটামুটি ০.৭–১.০।"),
        ("Raise temperature to 1.0–2.0 for creative writing and brainstorming.",
         "সৃজনশীল লেখা আর ব্রেইনস্টর্মিংয়ে temperature বাড়িয়ে ১.০–২.০ করুন।")],
       [sh("temp", "hot"), sh("pick", "hot")],
       [ln("temp", "pick", "to", state="hot")],
       [("0 · about 0.7–1.0 · 1.0–2.0", "০ · মোটামুটি ০.৭–১.০ · ১.০–২.০"), None, None],
       changes=[("+", "0: code, JSON, classification, math", "০: কোড, JSON, ক্লাসিফিকেশন, গণিত"),
                ("+", "About 0.7–1.0: chat", "মোটামুটি ০.৭–১.০: চ্যাট"),
                ("+", "1.0–2.0: creative writing, brainstorming", "১.০–২.০: সৃজনশীল লেখা, ব্রেইনস্টর্মিং")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Change temperature or top_p, usually not both. Do not stack tight top_k and top_p values.",
         "temperature অথবা top_p-এর যেকোনো একটি বদলান, সাধারণত দুটো একসাথে নয়। কড়া top_k আর top_p একসাথে চাপাবেন না।")],
       [sh("temp", "hot"), sh("topk", "warn"), sh("topp", "warn"), sh("pick", "hot")],
       [ln("temp", "pick", "to", state="hot"), ln("topk", "topp", "to", state="warn")],
       [None, None, None],
       points=[("Change temperature or top_p, usually not both.",
                "temperature অথবা top_p-এর যেকোনো একটি বদলান, সাধারণত দুটো একসাথে নয়।"),
               ("min_p is mainly found in open-source stacks.",
                "min_p মূলত ওপেন-সোর্স স্ট্যাকে মেলে।"),
               ("Do not stack tight top_k and top_p values.",
                "কড়া top_k আর top_p একসাথে চাপাবেন না।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
