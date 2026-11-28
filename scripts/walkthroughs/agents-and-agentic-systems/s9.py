"""Part 6 · 09 Long-running agents and durable execution: save every step, so a crash resumes instead of restarting.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Problems  Sub-title: "Agents that take minutes or hours face three problems a normal Python loop can't solve: crashes lose state, rate limits force waits, and human approvals force pauses. Durable execution engines help with all three."
  2 State     Body, "Why "just save state" isn't enough": "The naive solution is to checkpoint the agent's state to disk every step. But "the agent's state" is more than the message log: it's the in-flight tool calls, the partial writes to external services, the human approval state, the retry counters. Saving the messages and losing the rest gives you a corrupt resume."
  3 Durable   Body, "Durable execution, defined": "A durable execution engine records every step's intent and result to a durable store (a database, a journal, a queue). On crash, the next process replays the recorded history to rebuild state and resumes from the next un-run step. The engine handles retries and human-in-the-loop pauses natively. The application code is a series of workflow steps; the engine is the runtime that survives crashes."
  4 Resume    Same body: "On crash, the next process replays the recorded history to rebuild state and resumes from the next un-run step."; the diagram: "Finished steps do not run again; no work is lost." and "A crash mid-flight resumes from the next un-run step, not from the beginning."
  5 When      Body, "When you need it": "The agent runs for more than ~30 seconds (anything that might survive a deploy)." "Humans are in the loop and might take hours or days to respond." "The agent makes irreversible side effects (sending money, deleting records) that you want to be able to retry without duplicating." "The agent's work spans multiple services and you want to resume from the failed service."
  6 Engines   Body, "The four durable engines" (takeaway: "Five engines the section lists"): Temporal ("Event-sourced workflows", "Long-running, multi-day, with strong consistency"), Restate ("Journaled workflows", "Same as Temporal, smaller surface area"), Inngest ("Event-driven serverless", "Wake-on-webhook, pay-per-step"), AWS Step Functions / DBOS ("Managed / SQL-based", "AWS-native shops, simplest ops").
  7 Remember  Start here: "Durable execution saves each step, so the agent can pick up where it stopped."; and the four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("loop", "model", ("Agent loop", "এজেন্ট লুপ"), 110, 162),
    node("crash", "note", ("Crash", "ক্র্যাশ"), 650, 75),
    node("limit", "clock", ("Rate limit", "রেট লিমিট"), 650, 162),
    node("human", "user", ("Human approval", "মানুষের অনুমোদন"), 650, 250),
    node("store", "database", ("Durable store", "ডিউরেবল স্টোর"), 380, 250),
    node("st1", "service", ("Step 1", "ধাপ ১"), 110, 75),
    node("st2", "service", ("Step 2", "ধাপ ২"), 380, 75),
    node("st3", "service", ("Step 3", "ধাপ ৩"), 650, 75),
    node("temporal", "service", ("Temporal", "Temporal"), 200, 75),
    node("restate", "service", ("Restate", "Restate"), 560, 75),
    node("inngest", "service", ("Inngest", "Inngest"), 200, 250),
    node("aws", "service", ("Step Functions / DBOS", "Step Functions / DBOS"), 560, 250),
]

METRICS = [
    ("Run time", "চলার সময়"),
    ("Saved", "সেভ করা"),
    ("Engines", "ইঞ্জিন"),
]

CAPTION = (
    "A durable workflow: each step's intent and result is journaled. A crash mid-flight resumes from the next un-run step, not from the beginning.",
    "একটি ডিউরেবল ওয়ার্কফ্লো: প্রতিটি ধাপের উদ্দেশ্য আর ফলাফল জার্নালে লেখা হয়। মাঝপথে ক্র্যাশ হলে শুরু থেকে নয়, যে ধাপ চলেনি সেখান থেকে আবার চলে।",
)


def chain(state=None):
    """Three workflow steps, and each one journals to the store."""
    return [ln("st1", "st2", "to", state=state), ln("st2", "st3", "to", state=state),
            ln("st1", "store", "to", state=state), ln("st2", "store", "to", state=state), ln("st3", "store", "to", state=state)]


STEPS = [
    st(("Problems", "সমস্যা"),
       ("Three problems for long runs", "লম্বা চলায় তিনটি সমস্যা"),
       [("Agents that run for minutes or hours face three problems a normal loop cannot solve: crashes lose state, rate limits force waits, and human approvals force pauses.",
         "যে এজেন্ট কয়েক মিনিট বা ঘণ্টা চলে, তার তিনটি সমস্যা সাধারণ লুপ সামলাতে পারে না: ক্র্যাশ হলে স্টেট হারিয়ে যায়, রেট লিমিটের জন্য অপেক্ষা করতে হয়, আর মানুষের অনুমোদনের জন্য থামতে হয়।"),
        ("Durable execution engines help with all three.",
         "ডিউরেবল এক্সিকিউশন ইঞ্জিন এই তিনটাতেই সাহায্য করে।")],
       [sh("loop", "hot"), sh("crash", "warn", ("loses state", "স্টেট হারায়")), sh("limit", "warn", ("forces waits", "অপেক্ষা করায়")), sh("human", "warn", ("forces pauses", "থামতে হয়"))],
       [ln("loop", "crash", "to", state="warn"), ln("loop", "limit", "to", state="warn"), ln("loop", "human", "to", state="warn")],
       [None, None, None]),

    st(("State", "স্টেট"),
       ("Saving messages is not enough", "শুধু মেসেজ সেভ যথেষ্ট নয়"),
       [("The naive fix is to save the agent's state to disk at every step. But the state is more than the message log.",
         "সহজ সমাধান হলো প্রতিটি ধাপে এজেন্টের স্টেট ডিস্কে সেভ করা। কিন্তু স্টেট মানে শুধু মেসেজ লগ নয়।"),
        ("Saving the messages and losing the rest gives you a corrupt resume.",
         "মেসেজ সেভ করে বাকিটা হারালে রিজিউম হয় নষ্ট।")],
       [sh("loop", "hot"), sh("store", "warn", ("only the messages", "শুধু মেসেজ"))],
       [ln("loop", "store", "to", state="hot")],
       [None, ("messages only", "শুধু মেসেজ"), None],
       changes=[("-", "In-flight tool calls", "চলমান টুল কল"),
                ("-", "Partial writes to external services", "বাইরের সার্ভিসে আংশিক লেখা"),
                ("-", "The human approval state", "মানুষের অনুমোদনের অবস্থা"),
                ("-", "The retry counters", "রিট্রাই কাউন্টার")]),

    st(("Durable", "ডিউরেবল"),
       ("Durable execution", "ডিউরেবল এক্সিকিউশন"),
       [("A durable execution engine records every step's intent and result to a durable store: a database, a journal or a queue.",
         "ডিউরেবল এক্সিকিউশন ইঞ্জিন প্রতিটি ধাপের উদ্দেশ্য আর ফলাফল একটি ডিউরেবল স্টোরে লেখে: ডেটাবেস, জার্নাল বা কিউ।"),
        ("Your code is a series of workflow steps. The engine is the runtime that survives crashes, and it handles retries and human-in-the-loop pauses natively.",
         "আপনার কোড একটি সিরিজ ওয়ার্কফ্লো ধাপ। ইঞ্জিন হলো সেই রানটাইম, যা ক্র্যাশ সামলে টিকে থাকে, আর রিট্রাই ও হিউম্যান-ইন-দ্য-লুপ বিরতি নিজেই সামলায়।")],
       [sh("st1", "hot"), sh("st2", "hot"), sh("st3", "hot"), sh("store", "hot", ("intent and result", "উদ্দেশ্য আর ফলাফল"))],
       chain("hot"),
       [None, ("every step", "প্রতিটি ধাপ"), None]),

    st(("Resume", "রিজিউম"),
       ("Resume after a crash", "ক্র্যাশের পর রিজিউম"),
       [("After a crash, the next process replays the recorded history to rebuild state and resumes from the next step that has not run. Finished steps do not run again.",
         "ক্র্যাশের পর পরের প্রসেস রেকর্ড করা ইতিহাস রিপ্লে করে স্টেট আবার গড়ে, আর যে ধাপ চলেনি সেখান থেকে আবার চলে। শেষ হওয়া ধাপ আর চলে না।")],
       [sh("st1", "hot", ("done", "শেষ")), sh("st2", "hot", ("done", "শেষ")), sh("st3", "warn", ("crashed here", "এখানে ক্র্যাশ")), sh("store", "hot", ("the journal", "জার্নাল"))],
       [ln("st1", "st2", "to", state="hot"), ln("st2", "st3", "to", state="dim"),
        ln("store", "st3", "to", state="hot", label=("resumes here", "এখান থেকে চলে"))],
       [None, None, None]),

    st(("When", "কখন"),
       ("When you need it", "কখন দরকার"),
       [("Use durable execution when any one of these is true.",
         "এর যেকোনো একটি সত্য হলে ডিউরেবল এক্সিকিউশন ব্যবহার করুন।")],
       [sh("loop", "hot"), sh("store", "hot"), sh("human", "hot", ("hours or days", "কয়েক ঘণ্টা বা দিন"))],
       [ln("loop", "store", "to", state="hot"), ln("human", "store", "to", state="hot")],
       [("over ~30 s", "প্রায় ৩০ সে-র বেশি"), None, None],
       changes=[("+", "The agent runs for more than about 30 seconds", "এজেন্ট প্রায় ৩০ সেকেন্ডের বেশি চলে"),
                ("+", "Humans are in the loop and might take hours or days to respond", "মানুষ লুপে আছে, আর উত্তর দিতে কয়েক ঘণ্টা বা দিন লাগতে পারে"),
                ("+", "It makes irreversible side effects, such as sending money or deleting records, that you want to retry without duplicating", "ফেরানো যায় না এমন সাইড ইফেক্ট আছে, যেমন টাকা পাঠানো বা রেকর্ড মোছা, যা দুবার না করে আবার চালাতে চান"),
                ("+", "Its work spans several services, and you want to resume from the failed one", "কাজ কয়েকটি সার্ভিসে ছড়ানো, আর যে সার্ভিস ব্যর্থ হয়েছে সেখান থেকে আবার শুরু করতে চান")]),

    st(("Engines", "ইঞ্জিন"),
       ("Durable engines", "ডিউরেবল ইঞ্জিন"),
       [("Temporal runs event-sourced workflows for long, multi-day work with strong consistency. Restate is journaled workflows, the same idea with a smaller surface area.",
         "Temporal ইভেন্ট-সোর্সড ওয়ার্কফ্লো চালায়, লম্বা, বহু-দিনের কাজে, শক্ত কনসিস্টেন্সিসহ। Restate জার্নাল-ভিত্তিক ওয়ার্কফ্লো, একই ধারণা, কিন্তু ছোট সারফেসে।"),
        ("Inngest is event-driven serverless: it wakes on a webhook, and you pay per step. AWS Step Functions and DBOS are managed or SQL-based, for AWS-native shops and the simplest operations.",
         "Inngest ইভেন্ট-চালিত সার্ভারলেস: ওয়েবহুকে জেগে ওঠে, আর ধাপ ধরে দাম দিতে হয়। AWS Step Functions আর DBOS ম্যানেজড বা SQL-ভিত্তিক, AWS-নির্ভর দলগুলোর জন্য, অপারেশন সবচেয়ে সহজ।")],
       [sh("temporal", "hot", ("event-sourced, multi-day", "ইভেন্ট-সোর্সড, বহু-দিন")), sh("restate", "hot", ("journaled, smaller surface", "জার্নাল-ভিত্তিক, ছোট সারফেস")),
        sh("inngest", "hot", ("event-driven, per step", "ইভেন্ট-চালিত, ধাপ প্রতি দাম")), sh("aws", "hot", ("managed or SQL-based", "ম্যানেজড বা SQL-ভিত্তিক"))],
       [],
       [None, None, ("five", "পাঁচটি")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Durable execution saves each step, so the agent can pick up where it stopped.",
         "ডিউরেবল এক্সিকিউশন প্রতিটি ধাপ সেভ করে রাখে, তাই এজেন্ট যেখানে থেমেছিল সেখান থেকে আবার শুরু করতে পারে।")],
       [sh("st1"), sh("st2"), sh("st3"), sh("store")],
       chain(None),
       [None, None, None],
       points=[("Messages alone are not enough; also save in-flight tool calls, partial writes to external services, approvals, and retry counters.",
                "শুধু মেসেজ সেভ করলে যথেষ্ট নয়; চলমান টুল কল, বাইরের সার্ভিসে আংশিক লেখা, অনুমোদন আর রিট্রাই কাউন্টারও সেভ করুন।"),
               ("After a crash, a durable engine resumes from the next un-run step, not from the beginning.",
                "ক্র্যাশের পর ডিউরেবল ইঞ্জিন শুরু থেকে নয়, যে ধাপ চলেনি সেখান থেকে আবার চলে।"),
               ("Use it if the agent runs over about 30 seconds, waits for humans, or has irreversible side effects.",
                "এজেন্ট প্রায় ৩০ সেকেন্ডের বেশি চললে, মানুষের জন্য অপেক্ষা করলে, বা ফেরানো যায় না এমন সাইড ইফেক্ট থাকলে এটি ব্যবহার করুন।"),
               ("Five engines the section lists: Temporal, Restate, Inngest, and AWS Step Functions / DBOS.",
                "সেকশনে যে পাঁচটি ইঞ্জিনের কথা আছে: Temporal, Restate, Inngest আর AWS Step Functions / DBOS।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
