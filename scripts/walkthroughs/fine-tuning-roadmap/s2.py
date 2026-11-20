"""Part 3 · 02 Phase 2: How neural nets train: a loop of a guess, a score, and small steps that make the score better.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Guess     Start here: "Training is a loop: the model guesses, a number shows how wrong it was, and small steps shrink that number. You need this picture, not the hard math."
  2 Loss      Start here: Loss function ("A rule that gives one number for how wrong the model's current guess is."); body: "Loss: a single number measuring how wrong a prediction was".
              Layman's voice: "adjusting itself to make the number smaller next time".
  3 Nudge     Start here: Gradient descent ("Repeatedly nudging the model's weights, one small step at a time, to make the loss smaller."), Weights ("The numbers inside a model that it adjusts while it learns.").
              Layman's voice: "finding the bottom of a valley while blindfolded: you feel which way the ground slopes down and take a small step that way, then repeat."
  4 Repeat    Layman's voice: "over and over, thousands of times". Start here: Epoch / batch / learning rate ("An epoch is one pass over the training data. A batch is a small group of examples. The learning rate is the step size.").
  5 Overfit   Start here: Overfitting ("When a model memorizes its training examples instead of learning the subject. It looks perfect on practice and fails on new cases.");
              Layman's voice: "memorizing the answers to practice questions instead of learning the subject". Remember: "Overfitting means memorizing training examples instead of generalizing."
  6 Validate  Start here: Validation curves ("Charts of the model's score on held-back validation data as training goes on. They give an early warning that overfitting has started.").
  7 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("data", "storage", ("Training data", "ট্রেইনিং ডেটা"), 100, 75),
    node("model", "model", ("Model", "মডেল"), 290, 75),
    node("loss", "chart", ("Loss", "লস"), 500, 75),
    node("new", "file", ("New cases", "নতুন ক্ষেত্র"), 670, 75),
    node("valid", "storage", ("Validation data", "ভ্যালিডেশন ডেটা"), 100, 250),
    node("curve", "chart", ("Validation curve", "ভ্যালিডেশন কার্ভ"), 290, 250),
    node("gd", "service", ("Gradient descent", "গ্রেডিয়েন্ট ডিসেন্ট"), 500, 250),
]

METRICS = [
    ("Loss", "লস"),
    ("Practice score", "প্র্যাকটিসের স্কোর"),
    ("New cases", "নতুন ক্ষেত্র"),
]

CAPTION = (
    "An example of the training loop. The readouts say in words what happens.",
    "ট্রেইনিং চক্রের একটি উদাহরণ। রিডআউট কথায় বলে কী ঘটছে।",
)

SMALLER = ("smaller", "ছোট হয়")

STEPS = [
    st(("Guess", "অনুমান"),
       ("Training is a loop that starts with a guess", "ট্রেইনিং একটা চক্র, শুরু হয় অনুমান দিয়ে"),
       [("Training is a loop. First, the model makes a guess.",
         "ট্রেইনিং একটা চক্র। প্রথমে মডেল একটা অনুমান করে।"),
        ("A number then shows how wrong the guess was, and small steps shrink that number. You need this picture, not the hard math.",
         "তারপর একটা সংখ্যা দেখায় অনুমান কতটা ভুল ছিল, আর ছোট ছোট ধাপে সেই সংখ্যা কমানো হয়। কঠিন ম্যাথ নয়, এই ছবিটা দরকার।")],
       [sh("data", "hot", ("examples", "উদাহরণ")), sh("model", "hot", ("makes a guess", "অনুমান করে"))],
       [ln("data", "model", "to", state="hot")],
       [None, None, None]),

    st(("Loss", "লস"),
       ("A loss function scores the guess", "লস ফাংশন অনুমানের নম্বর দেয়"),
       [("A loss function is a rule that gives one number for how wrong the model's current guess is.",
         "লস ফাংশন একটা নিয়ম, যা মডেলের এই মুহূর্তের অনুমান কতটা ভুল তা একটা সংখ্যায় দেয়।"),
        ("Training tries to make this number smaller.",
         "ট্রেইনিং এই সংখ্যাটা ছোট করার চেষ্টা করে।")],
       [sh("data", "dim"), sh("model", "hot", ("the guess", "অনুমান")), sh("loss", "hot", ("how wrong", "কতটা ভুল"))],
       [ln("data", "model", "to", state="dim"), ln("model", "loss", "to", state="hot")],
       [("one number", "একটা সংখ্যা"), None, None],
       note=("insight",
             "Loss is a single number measuring how wrong a prediction was.",
             "লস হলো অনুমান কতটা ভুল তার একটা সংখ্যা।")),

    st(("Nudge", "সামান্য বদল"),
       ("Gradient descent nudges the weights", "গ্রেডিয়েন্ট ডিসেন্ট ওয়েট বদলায়"),
       [("Gradient descent nudges the model's weights, one small step at a time, to make the loss smaller. The weights are the numbers inside the model that it adjusts while it learns.",
         "গ্রেডিয়েন্ট ডিসেন্ট মডেলের ওয়েট ছোট ছোট ধাপে সামান্য বদলায়, যাতে লস কমে। ওয়েট হলো মডেলের ভেতরের সংখ্যা, যা সে শেখার সময় বদলায়।"),
        ("It is like finding the bottom of a valley while blindfolded: you feel which way the ground slopes down and take a small step that way.",
         "এটা চোখ বাঁধা অবস্থায় উপত্যকার তলা খোঁজার মতো: মাটি কোন দিকে ঢালু হয়ে নেমেছে তা অনুভব করে সেদিকে একটা ছোট পা ফেলা।")],
       [sh("model", "hot", ("weights change", "ওয়েট বদলায়")), sh("loss", "dim"), sh("gd", "hot", ("small steps", "ছোট ছোট ধাপ"))],
       [ln("loss", "gd", "to", state="hot"), ln("gd", "model", "to", state="hot", label=("small step", "ছোট ধাপ"))],
       [SMALLER, None, None],
       changes=[("-", "The loss gets smaller", "লস ছোট হয়")]),

    st(("Repeat", "বারবার"),
       ("The loop repeats, again and again", "চক্রটা বারবার চলে"),
       [("The loop repeats over and over, thousands of times. An epoch is one pass over the training data. A batch is a small group of examples.",
         "চক্রটা বারবার চলে, হাজার হাজার বার। এপক মানে ট্রেইনিং ডেটার ওপর একবার পুরো ঘোরা। ব্যাচ হলো উদাহরণের ছোট দল।"),
        ("The learning rate is the step size.",
         "লার্নিং রেট হলো ধাপের মাপ।")],
       [sh("data", "hot", ("epoch, batch", "এপক, ব্যাচ")), sh("model", "hot"), sh("loss", "hot"), sh("gd", "hot", ("learning rate", "লার্নিং রেট"))],
       [ln("data", "model", "to", state="hot"), ln("model", "loss", "to", state="hot"), ln("loss", "gd", "to", state="hot"), ln("gd", "model", "to", state="hot")],
       [SMALLER, None, None]),

    st(("Overfit", "ওভারফিট"),
       ("Overfitting: memorizing instead of learning", "ওভারফিটিং: শেখার বদলে মুখস্থ করা"),
       [("Overfitting is when a model memorizes its training examples instead of learning the subject.",
         "ওভারফিটিং হলো মডেল বিষয়টা না শিখে ট্রেইনিং উদাহরণ মুখস্থ করে ফেলা।"),
        ("It looks perfect on practice and fails on new cases, like memorizing the answers to practice questions.",
         "প্র্যাকটিসে সেটা নিখুঁত দেখায়, কিন্তু নতুন ক্ষেত্রে আটকে যায়, যেমন প্র্যাকটিস প্রশ্নের উত্তর মুখস্থ করা।")],
       [sh("data", "hot", ("practice", "প্র্যাকটিস")), sh("model", "warn", ("memorizes", "মুখস্থ করে")), sh("new", "warn", ("fails", "আটকে যায়"))],
       [ln("data", "model", "to", state="dim"), ln("model", "new", "to", state="warn", label=("new cases", "নতুন ক্ষেত্র"))],
       [None, ("perfect", "নিখুঁত"), ("fails", "আটকে যায়")],
       note=("warn",
             "Overfitting means memorizing training examples instead of generalizing.",
             "ওভারফিটিং মানে সাধারণভাবে শেখার বদলে ট্রেইনিং উদাহরণ মুখস্থ করা।")),

    st(("Validate", "যাচাই"),
       ("Validation curves warn you early", "ভ্যালিডেশন কার্ভ আগেভাগে সতর্ক করে"),
       [("A validation curve charts the model's score on held-back validation data as training goes on.",
         "ভ্যালিডেশন কার্ভ হলো ট্রেইনিং চলার সময় আলাদা করে রাখা ভ্যালিডেশন ডেটায় মডেলের স্কোরের চার্ট।"),
        ("It gives an early warning that overfitting has started.",
         "ওভারফিটিং শুরু হলে এটা আগেভাগে সতর্ক করে।")],
       [sh("valid", "hot", ("held back", "আলাদা করে রাখা")), sh("model", "dim"), sh("curve", "hot", ("early warning", "আগাম সতর্কতা"))],
       [ln("valid", "model", "to", state="dim"), ln("model", "curve", "to", state="hot", label=("score", "স্কোর"))],
       [None, None, None],
       changes=[("+", "An early warning that overfitting has started", "ওভারফিটিং শুরু হলে আগেভাগে সতর্কতা")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Training is a loop of a guess, a score, and small steps. Watch for overfitting.",
         "ট্রেইনিং হলো অনুমান, নম্বর আর ছোট ছোট ধাপের চক্র। ওভারফিটিং নিয়ে সাবধান থাকুন।")],
       [sh("data"), sh("model"), sh("loss"), sh("gd"), sh("curve")],
       [ln("data", "model", "to"), ln("model", "loss", "to"), ln("loss", "gd", "to"), ln("gd", "model", "to"), ln("model", "curve", "to")],
       [None, None, None],
       points=[("Loss is one number for how wrong a guess was. Gradient descent nudges weights to shrink it.",
                "লস হলো অনুমান কতটা ভুল তার একটা সংখ্যা। গ্রেডিয়েন্ট ডিসেন্ট ওয়েট বদলে সেটা কমায়।"),
               ("Overfitting means memorizing training examples instead of generalizing.",
                "ওভারফিটিং মানে সাধারণভাবে শেখার বদলে ট্রেইনিং উদাহরণ মুখস্থ করা।"),
               ("Validation curves warn you early that overfitting has started.",
                "ভ্যালিডেশন কার্ভ আগেভাগে জানায় যে ওভারফিটিং শুরু হয়েছে।"),
               ("Do small PyTorch exercises: train a tiny model on a toy dataset end to end.",
                "ছোট PyTorch অনুশীলন করুন: খেলনা ডেটাসেটে একটা ছোট মডেল শুরু থেকে শেষ পর্যন্ত ট্রেইন করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
