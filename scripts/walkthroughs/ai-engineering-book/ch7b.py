"""Part ai-engineering-book · ch7b Finetuning: PEFT, LoRA, model merging and tactics.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Memory    Start here: "Updating a whole model takes a lot of memory." / "Finetuning a whole model is memory-hungry."
  2 PEFT      "PEFT methods like LoRA train only a tiny add-on." Definition: "adding small trainable modules (adapters)".
  3 LoRA      "For a weight matrix, LoRA trains only two small matrices ... and leaves the base weights alone." "so far fewer values are trained and memory drops."
  4 QLoRA     "LoRA with the base model stored in 4-bit precision. It lets one consumer-grade GPU finetune very large models."
  5 Share     "Many LoRA adapters can share one base model, for per-customer or per-task models."
  6 Merge     "Training on tasks one after another risks catastrophic forgetting"; "Model merging ... without necessarily needing a GPU"; "Merging lets you finetune each task separately, then combine the results into one multi-skilled model."
  7 Tactics   "learning rate: ... Too high and training destabilizes; too low and it crawls." "number of epochs: watch training vs. validation loss to catch overfitting." Overfitting: "validation error rises while training error falls."
  8 Remember  "Start with an adapter like LoRA. Move to full finetuning only with enough data and a need for extra quality."
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("full", "model", ("Whole model", "পুরো মডেল"), 140, 162),
    node("base", "model", ("Base model", "বেস মডেল"), 140, 162),
    node("adapter", "model", ("Small add-on", "ছোট অ্যাড-অন"), 420, 162),
    node("q4", "model", ("4-bit base model", "৪-বিট বেস মডেল"), 170, 162),
    node("gpu", "server", ("One consumer-grade GPU", "একটি সাধারণ GPU"), 570, 162),
    node("a1", "service", ("Customer adapter", "কাস্টমার অ্যাডাপ্টার"), 450, 70),
    node("a2", "service", ("Task adapter", "কাজের অ্যাডাপ্টার"), 450, 254),
    node("ma", "model", ("Task model", "কাজের মডেল"), 130, 70),
    node("mb", "model", ("Task model", "কাজের মডেল"), 130, 254),
    node("merge", "tool", ("Model merging", "মডেল মার্জিং"), 390, 162),
    node("multi", "model", ("One multi-skilled model", "এক বহুমুখী মডেল"), 630, 162),
]

METRICS = [
    ("Memory", "মেমরি"),
    ("Trained", "ট্রেইন হয়"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Memory", "মেমরি"),
       ("A whole model takes a lot of memory", "পুরো মডেলে অনেক মেমরি লাগে"),
       [("Updating a whole model takes a lot of memory.",
         "পুরো মডেল আপডেট করতে অনেক মেমরি লাগে।"),
        ("Full finetuning updates every parameter.",
         "পুরো ফাইন-টিউনিংয়ে সব প্যারামিটার আপডেট হয়।")],
       [sh("full", "warn", ("every parameter", "সব প্যারামিটার"), x=380)],
       [],
       [("a lot", "অনেক"), ("every parameter", "সব প্যারামিটার")]),

    st(("PEFT", "PEFT"),
       ("Train only a tiny add-on", "শুধু ছোট একটা অ্যাড-অন ট্রেইন করুন"),
       [("PEFT methods like LoRA train only a tiny add-on.",
         "LoRA-র মতো PEFT পদ্ধতি শুধু একটি ছোট অ্যাড-অন ট্রেইন করে।"),
        ("They add small trainable modules (adapters) rather than touching the base weights.",
         "মূল ওয়েট না ছুঁয়ে তারা ছোট ট্রেইনেবল মডিউল (অ্যাডাপ্টার) যোগ করে।")],
       [sh("base", "dim", ("base weights untouched", "মূল ওয়েট ছোঁয়া হয় না")), sh("adapter", "hot", ("adapter", "অ্যাডাপ্টার"))],
       [ln("base", "adapter", "to", state="hot")],
       [None, ("tiny add-on", "ছোট অ্যাড-অন")]),

    st(("LoRA", "LoRA"),
       ("LoRA: two small matrices", "LoRA: দুটি ছোট ম্যাট্রিক্স"),
       [("For a weight matrix, LoRA trains only two small matrices whose product approximates the update.",
         "একটি ওয়েট ম্যাট্রিক্সের জন্য LoRA শুধু দুটি ছোট ম্যাট্রিক্স ট্রেইন করে, যাদের গুণফল বদলের মোটামুটি রূপ দেয়।"),
        ("The base weights are left alone, so far fewer values are trained and memory drops.",
         "মূল ওয়েট ছোঁয়া হয় না, তাই অনেক কম মান ট্রেইন হয় আর মেমরি কমে।")],
       [sh("base", "dim", ("left alone", "ছোঁয়া হয় না")), sh("adapter", "hot", ("two small matrices", "দুটি ছোট ম্যাট্রিক্স"))],
       [ln("base", "adapter", "to", state="hot")],
       [("drops", "কমে"), ("far fewer values", "অনেক কম মান")]),

    st(("QLoRA", "QLoRA"),
       ("QLoRA: a 4-bit base", "QLoRA: ৪-বিট বেস"),
       [("QLoRA is LoRA with the base model stored in 4-bit precision.",
         "QLoRA হলো এমন LoRA, যেখানে বেস মডেল ৪-বিট প্রিসিশনে রাখা হয়।"),
        ("It lets one consumer-grade GPU finetune very large models.",
         "এতে একটি সাধারণ GPU-তে খুব বড় মডেল ফাইন-টিউন করা যায়।")],
       [sh("q4", "hot", ("4-bit precision", "৪-বিট প্রিসিশন")), sh("gpu", "hot", ("very large models", "খুব বড় মডেল"))],
       [ln("q4", "gpu", "to", state="hot")],
       [None, None]),

    st(("Share", "শেয়ার"),
       ("Many adapters share one base", "এক বেসে অনেক অ্যাডাপ্টার"),
       [("Many LoRA adapters can share one base model.",
         "একটি বেস মডেলে অনেক LoRA অ্যাডাপ্টার চলতে পারে।"),
        ("Each one can be a model for a customer or for a task.",
         "প্রতিটি হতে পারে একেকটি কাস্টমার বা কাজের জন্য আলাদা মডেল।")],
       [sh("base", "hot", ("one base model", "একটি বেস মডেল")), sh("a1", "hot", ("per-customer", "প্রতি কাস্টমার")), sh("a2", "hot", ("per-task", "প্রতি কাজ"))],
       [ln("base", "a1", "to", state="hot"), ln("base", "a2", "to", state="hot")],
       [None, None]),

    st(("Merge", "মার্জ"),
       ("Merge models, one skill each", "মডেল মার্জ করুন, প্রতিটিতে একটি কাজ"),
       [("Training on tasks one after another risks catastrophic forgetting, where the model forgets earlier tasks.",
         "একের পর এক কাজে ট্রেনিং করলে ক্যাটাস্ট্রফিক ফরগেটিংয়ের ঝুঁকি থাকে, যেখানে মডেল আগের কাজগুলো ভুলে যায়।"),
        ("Merging lets you finetune each task separately, then combine the results into one multi-skilled model, without necessarily needing a GPU.",
         "মার্জিংয়ে প্রতিটি কাজ আলাদা ফাইন-টিউন করে পরে এক বহুমুখী মডেলে মেলানো যায়, GPU ছাড়াও সম্ভব।")],
       [sh("ma", "hot", ("finetuned separately", "আলাদা ফাইন-টিউন")), sh("mb", "hot", ("finetuned separately", "আলাদা ফাইন-টিউন")), sh("merge", "hot"), sh("multi", "hot", ("multi-skilled", "বহুমুখী"))],
       [ln("ma", "merge", "to", state="hot"), ln("mb", "merge", "to", state="hot"), ln("merge", "multi", "to", state="hot")],
       [None, None],
       note=("warn", "Training tasks one after another can make the model forget the earlier tasks.",
             "একের পর এক কাজে ট্রেনিং করলে মডেল আগের কাজগুলো ভুলে যেতে পারে।")),

    st(("Tactics", "কৌশল"),
       ("Watch the learning rate and the loss", "লার্নিং রেট আর লস দেখুন"),
       [("Learning rate is the step size. Too high and training turns unstable; too low and it crawls.",
         "লার্নিং রেট হলো ধাপের মাপ। বেশি হলে ট্রেনিং অস্থির হয়; কম হলে খুব ধীরে এগোয়।"),
        ("Watch training and validation loss to catch overfitting.",
         "ওভারফিটিং ধরতে ট্রেনিং আর ভ্যালিডেশন লস দেখুন।")],
       [sh("adapter", "hot", ("training", "ট্রেনিং"))],
       [],
       [None, None],
       points=[("Overfitting shows when held-out (validation) error rises while training error falls.",
                "আলাদা রাখা (ভ্যালিডেশন) ডেটায় ভুল বাড়ে অথচ ট্রেনিংয়ের ভুল কমে, তখন ওভারফিটিং ধরা পড়ে।")]),

    st(("Remember", "মনে রাখুন"),
       ("Start with an adapter", "অ্যাডাপ্টার দিয়ে শুরু করুন"),
       [("Start with an adapter like LoRA.",
         "শুরুতে LoRA-র মতো অ্যাডাপ্টার ব্যবহার করুন।"),
        ("Move to full finetuning only with enough data and a need for extra quality.",
         "যথেষ্ট ডেটা থাকলে আর বাড়তি মান লাগলে তবেই পুরো ফাইন-টিউনিং করুন।")],
       [sh("adapter", "hot", ("start here", "এখানে শুরু")), sh("full", "dim", ("later", "পরে"), x=140)],
       [ln("adapter", "full", "to", state="dim")],
       [None, None]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
