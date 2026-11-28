"""RAG and Knowledge Systems · 08 Multi-query fusion (RAG-Fusion) with RRF, worked through: merge ranked lists by adding 1/(k + rank).

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Variants  Start here: "Search with several versions of the question, then merge the ranked lists." Query variant: "One of several rewordings of the user's question. Each one gets its own search."
  2 Lists     Body, worked diagram: variant 1 list "rank 1: Doc A, rank 2: Doc B, rank 3: Doc C"; variant 2 list "rank 1: Doc B, rank 2: Doc D, rank 3: Doc A".
  3 Formula   Start here: "A document's score is the sum of 1/(k + rank) over all the lists." k: "A number in the RRF formula."
  4 Doc B     Diagram: "Doc B  1/62 + 1/61 = 0.03252".
  5 Doc A     Diagram: "Doc A  1/61 + 1/63 = 0.03227".
  6 Doc D, C  Diagram: "Doc D  1/62 = 0.01613", "Doc C  1/63 = 0.01587".
  7 Winner    Diagram: "Doc B wins: high in both lists beats rank 1 in only one list." "Documents ranked well in several lists rise. Agreement across lists decides the order." "Illustrative numbers computed from the RRF formula."
  8 Check k   Start here: "Defaults for k differ: 60 in the paper and Elasticsearch, 2 in Qdrant's docs. Check yours first." Body: "Qdrant also counts ranks from 0, so its k is not directly comparable to a k used with ranks from 1."
  9 Remember  The same three claims: the score sum, agreement across lists, and the k defaults.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("q", "user", ("Question", "প্রশ্ন"), 68, 160),
    node("vars", "model", ("Variants", "ভ্যারিয়েন্ট"), 215, 160),
    node("v1", "queue", ("List 1", "তালিকা ১"), 345, 90),
    node("v2", "queue", ("List 2", "তালিকা ২"), 345, 230),
    node("rrf", "chart", ("RRF", "RRF"), 480, 160),
    node("k", "note", ("k", "k"), 480, 50),
    node("k60", "note", ("Paper, Elasticsearch", "পেপার, Elasticsearch"), 300, 90),
    node("kq", "note", ("Qdrant's docs", "Qdrant-এর ডকস"), 300, 230),
    node("doc-b", "file", ("Doc B", "ডকুমেন্ট B"), 680, 45),
    node("doc-a", "file", ("Doc A", "ডকুমেন্ট A"), 680, 120),
    node("doc-d", "file", ("Doc D", "ডকুমেন্ট D"), 680, 195),
    node("doc-c", "file", ("Doc C", "ডকুমেন্ট C"), 680, 270),
]

METRICS = [
    ("Doc B", "ডকুমেন্ট B"),
    ("Doc A", "ডকুমেন্ট A"),
    ("Doc D", "ডকুমেন্ট D"),
    ("Doc C", "ডকুমেন্ট C"),
]

CAPTION = (
    "Illustrative numbers computed from the RRF formula, not a benchmark.",
    "RRF সূত্র থেকে হিসাব করা উদাহরণের সংখ্যা, বেঞ্চমার্ক নয়।",
)

STEPS = [
    st(("Variants", "ভ্যারিয়েন্ট"),
       ("Search with several versions", "কয়েকটি রূপ দিয়ে খোঁজা"),
       [("Search with several versions of the question. Each version, a query variant, gets its own search.",
         "প্রশ্নের কয়েকটি রূপ দিয়ে খুঁজুন। প্রতিটি রূপ, মানে কুয়েরি ভ্যারিয়েন্ট, দিয়ে আলাদা সার্চ চলে।"),
        ("Then merge the ranked lists.",
         "তারপর র‍্যাংক করা তালিকাগুলো মেলান।")],
       [sh("q", "hot"), sh("vars", "hot"), sh("v1", "hot"), sh("v2", "hot")],
       [ln("q", "vars", "to", state="hot"), ln("vars", "v1", "to", state="hot"), ln("vars", "v2", "to", state="hot")],
       [None, None, None, None]),

    st(("Lists", "তালিকা"),
       ("Two ranked lists", "দুটি র‍্যাংক করা তালিকা"),
       [("Variant 1 ranks Doc A first, Doc B second and Doc C third.",
         "ভ্যারিয়েন্ট ১ ডকুমেন্ট A-কে এক নম্বরে, B-কে দুই নম্বরে আর C-কে তিন নম্বরে রাখে।"),
        ("Variant 2 ranks Doc B first, Doc D second and Doc A third.",
         "ভ্যারিয়েন্ট ২ ডকুমেন্ট B-কে এক নম্বরে, D-কে দুই নম্বরে আর A-কে তিন নম্বরে রাখে।")],
       [sh("v1", "hot", ("A, B, C", "A, B, C")), sh("v2", "hot", ("B, D, A", "B, D, A")), sh("rrf", "dim")],
       [ln("v1", "rrf", "to", state="dim"), ln("v2", "rrf", "to", state="dim")],
       [None, None, None, None],
       changes=[("+", "Variant 1 list: rank 1 Doc A, rank 2 Doc B, rank 3 Doc C",
                 "ভ্যারিয়েন্ট ১ তালিকা: র‍্যাংক ১ ডকুমেন্ট A, র‍্যাংক ২ ডকুমেন্ট B, র‍্যাংক ৩ ডকুমেন্ট C"),
                ("+", "Variant 2 list: rank 1 Doc B, rank 2 Doc D, rank 3 Doc A",
                 "ভ্যারিয়েন্ট ২ তালিকা: র‍্যাংক ১ ডকুমেন্ট B, র‍্যাংক ২ ডকুমেন্ট D, র‍্যাংক ৩ ডকুমেন্ট A")]),

    st(("Formula", "সূত্র"),
       ("Reciprocal rank fusion", "রেসিপ্রোকাল র‍্যাংক ফিউশন"),
       [("RRF is a merge method. A document gets 1/(k + rank) points from each list, and the points add up.",
         "RRF মেলানোর পদ্ধতি। প্রতিটি তালিকা থেকে ডকুমেন্ট পায় 1/(k + rank) পয়েন্ট, তারপর সব যোগ হয়।"),
        ("k is a number in the RRF formula.",
         "k হলো RRF সূত্রের একটি সংখ্যা।")],
       [sh("v1", "hot"), sh("v2", "hot"), sh("rrf", "hot", ("adds up", "যোগ হয়")), sh("k", "hot")],
       [ln("v1", "rrf", "to", state="hot"), ln("v2", "rrf", "to", state="hot"), ln("k", "rrf", "to", state="hot")],
       [None, None, None, None]),

    st(("Doc B", "ডকুমেন্ট B"),
       ("Score Doc B", "ডকুমেন্ট B-এর স্কোর"),
       [("With k = 60, Doc B gets 1/62 from variant 1 and 1/61 from variant 2.",
         "k = ৬০ ধরলে ডকুমেন্ট B ভ্যারিয়েন্ট ১ থেকে পায় ১/৬২ আর ভ্যারিয়েন্ট ২ থেকে ১/৬১।"),
        ("The sum is 0.03252.",
         "যোগফল ০.০৩২৫২।")],
       [sh("v1", "hot"), sh("v2", "hot"), sh("rrf", "hot"), sh("k", "hot", ("k = 60", "k = ৬০")),
        sh("doc-b", "hot", ("0.03252", "০.০৩২৫২"))],
       [ln("v1", "rrf", "to", state="hot"), ln("v2", "rrf", "to", state="hot"), ln("k", "rrf", "to", state="dim"), ln("rrf", "doc-b", "to", state="hot")],
       [("1/62 + 1/61 = 0.03252", "১/৬২ + ১/৬১ = ০.০৩২৫২"), None, None, None]),

    st(("Doc A", "ডকুমেন্ট A"),
       ("Score Doc A", "ডকুমেন্ট A-এর স্কোর"),
       [("Doc A gets 1/61 from variant 1 and 1/63 from variant 2.",
         "ডকুমেন্ট A ভ্যারিয়েন্ট ১ থেকে পায় ১/৬১ আর ভ্যারিয়েন্ট ২ থেকে ১/৬৩।"),
        ("The sum is 0.03227.",
         "যোগফল ০.০৩২২৭।")],
       [sh("rrf", "hot"), sh("k", "dim", ("k = 60", "k = ৬০")),
        sh("doc-b", "dim", ("0.03252", "০.০৩২৫২")),
        sh("doc-a", "hot", ("0.03227", "০.০৩২২৭"))],
       [ln("k", "rrf", "to", state="dim"), ln("rrf", "doc-b", "to", state="dim"), ln("rrf", "doc-a", "to", state="hot")],
       [("1/62 + 1/61 = 0.03252", "১/৬২ + ১/৬১ = ০.০৩২৫২"), ("1/61 + 1/63 = 0.03227", "১/৬১ + ১/৬৩ = ০.০৩২২৭"), None, None]),

    st(("Doc D, C", "ডকুমেন্ট D, C"),
       ("Score Doc D and Doc C", "ডকুমেন্ট D আর C-এর স্কোর"),
       [("Doc D appears in one list, so it gets 1/62 = 0.01613.",
         "ডকুমেন্ট D একটি তালিকায় আছে, তাই পায় ১/৬২ = ০.০১৬১৩।"),
        ("Doc C also appears in one list, so it gets 1/63 = 0.01587.",
         "ডকুমেন্ট C-ও একটি তালিকায় আছে, তাই পায় ১/৬৩ = ০.০১৫৮৭।")],
       [sh("rrf", "hot"), sh("doc-b", "dim"), sh("doc-a", "dim"),
        sh("doc-d", "hot", ("0.01613", "০.০১৬১৩")), sh("doc-c", "hot", ("0.01587", "০.০১৫৮৭"))],
       [ln("rrf", "doc-d", "to", state="hot"), ln("rrf", "doc-c", "to", state="hot")],
       [("1/62 + 1/61 = 0.03252", "১/৬২ + ১/৬১ = ০.০৩২৫২"), ("1/61 + 1/63 = 0.03227", "১/৬১ + ১/৬৩ = ০.০৩২২৭"), ("1/62 = 0.01613", "১/৬২ = ০.০১৬১৩"), ("1/63 = 0.01587", "১/৬৩ = ০.০১৫৮৭")]),

    st(("Winner", "বিজয়ী"),
       ("Doc B wins", "ডকুমেন্ট B জেতে"),
       [("Doc B wins: high in both lists beats rank 1 in only one list.",
         "ডকুমেন্ট B জেতে: দুই তালিকাতেই ওপরের দিকে থাকা একটিতে এক নম্বরে থাকাকে হারায়।"),
        ("Documents ranked well in several lists rise. Agreement across lists decides the order.",
         "যে ডকুমেন্ট অনেক তালিকায় ভালো র‍্যাংক পায়, সে ওপরে ওঠে। তালিকাগুলোর মিলই ক্রম ঠিক করে।")],
       [sh("rrf", "hot"), sh("doc-b", "hot", ("1.", "১.")), sh("doc-a", "hot", ("2.", "২.")),
        sh("doc-d", "dim", ("3.", "৩.")), sh("doc-c", "dim", ("4.", "৪."))],
       [ln("rrf", "doc-b", "to", state="hot"), ln("rrf", "doc-a", "to", state="hot"), ln("rrf", "doc-d", "to", state="dim"), ln("rrf", "doc-c", "to", state="dim")],
       [("1/62 + 1/61 = 0.03252", "১/৬২ + ১/৬১ = ০.০৩২৫২"), ("1/61 + 1/63 = 0.03227", "১/৬১ + ১/৬৩ = ০.০৩২২৭"), ("1/62 = 0.01613", "১/৬২ = ০.০১৬১৩"), ("1/63 = 0.01587", "১/৬৩ = ০.০১৫৮৭")],
       note=("tip", "Illustrative numbers computed from the RRF formula.",
             "সংখ্যাগুলো RRF সূত্র থেকে হিসাব করা উদাহরণ।")),

    st(("Check k", "k দেখুন"),
       ("The default k differs", "k-এর ডিফল্ট আলাদা"),
       [("Defaults for k differ: 60 in the paper and Elasticsearch, 2 in Qdrant's docs. Check yours first.",
         "k-এর ডিফল্ট আলাদা: পেপার ও Elasticsearch-এ ৬০, Qdrant-এর ডকসে ২। আগে নিজেরটা দেখে নিন।"),
        ("Qdrant also counts ranks from 0, so its k is not directly comparable to a k used with ranks from 1.",
         "Qdrant র‍্যাংকও ০ থেকে গোনে, তাই এর k ১ থেকে গোনা র‍্যাংকের k-এর সাথে সরাসরি তুলনীয় নয়।")],
       [sh("k60", "hot", ("k = 60", "k = ৬০")), sh("kq", "warn", ("k = 2", "k = ২")), sh("rrf", "hot")],
       [ln("k60", "rrf", "to", state="hot"), ln("kq", "rrf", "to", state="warn")],
       [None, None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("RRF adds up 1/(k + rank) over all the lists, and agreement across lists decides the order.",
         "RRF সব তালিকা জুড়ে 1/(k + rank) যোগ করে, আর তালিকাগুলোর মিলই ক্রম ঠিক করে।")],
       [sh("v1", "hot"), sh("v2", "hot"), sh("rrf", "hot"), sh("doc-b", "hot")],
       [ln("v1", "rrf", "to", state="hot"), ln("v2", "rrf", "to", state="hot"), ln("rrf", "doc-b", "to", state="hot")],
       [None, None, None, None],
       points=[("A document's score is the sum of 1/(k + rank) over all the lists.",
                "একটি ডকুমেন্টের স্কোর হলো সব তালিকা জুড়ে 1/(k + rank)-এর যোগফল।"),
               ("Documents ranked well in several lists rise. Agreement across lists decides the order.",
                "যে ডকুমেন্ট অনেক তালিকায় ভালো র‍্যাংক পায়, সে ওপরে ওঠে। তালিকাগুলোর মিলই ক্রম ঠিক করে।"),
               ("Defaults for k differ: 60 in the paper and Elasticsearch, 2 in Qdrant's docs. Check yours first.",
                "k-এর ডিফল্ট আলাদা: পেপার ও Elasticsearch-এ ৬০, Qdrant-এর ডকসে ২। আগে নিজেরটা দেখে নিন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
