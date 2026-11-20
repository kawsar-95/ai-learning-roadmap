"""Part 5 · 06 Hybrid search (BM25 + vector) & reciprocal rank fusion: two searches, merged by rank.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Two       Sub-title: "BM25 needs the query's exact words to appear, while dense vectors can blur rare identifiers, names and codes."; BM25 ("A classic keyword score. It rewards documents that contain the exact words of the query."); Dense retriever ("It matches meaning, not exact words.").
              Layman's voice: "The word-matcher is great at product codes and names but misses rephrased ideas. The meaning-matcher is great at ideas but can fumble exact codes."
  2 Hybrid    Sub-title: "Hybrid search runs both and merges the results." and "The catch is that the two retrievers' scores live on different scales, which is exactly the problem rank-based fusion sidesteps."; body: "Weaviate states that its hybrid search runs the vector and BM25 searches in parallel and then fuses them."
  3 RRF       Start here: Reciprocal rank fusion ("A merge method that ignores raw scores. Each list gives a document points based on its rank, and the points add up."); body: "Cormack, Clarke and Buettcher define a document's score as a sum over every ranking that contains it. Each ranking adds 1 / (k + r(d)), where r(d) is the document's rank in that list."
  4 Doc B     Body: "The ranks in the diagram are invented for the arithmetic."; Bangla voice, the worked example (k = 60): "document B has rank 2 in both lists, so 1/62 + 1/62 = 0.032258".
  5 Doc A     Bangla voice: "document A is first in BM25 (1/61) but fifth in the dense list (1/65), 0.031778 in all, so A comes third"; the diagram: "documents ranked well by both retrievers (B, C) overtake it"; the code's result: ['B', 'C', 'A', 'E', 'D', 'F', 'G'] (D and E tie).
  6 k         Constant k ("A small k gives top ranks much more weight."); the diagram: "a rank-10 hit keeps 87% of a rank-1 hit's weight at k = 60 but only 25% at k = 2".
  7 Engines   Warning callout: "the paper fixed k = 60, and Elasticsearch and OpenSearch default to 60. Qdrant's docs, however, state that RRF's k is "set to 2 by default". Weaviate's rankedFusion uses 1/(RANK+60). The same two lists can therefore fuse differently across engines. Check the default before comparing results, and set k explicitly where the API allows it."
  8 Scores    Body, "Rank-based versus score-based fusion": relativeScoreFusion "normalises each search's scores to 0-1 ..., then weights them with alpha. An alpha of 0 is keyword only, 1 is vector only, and the server default is 0.75."; rankedFusion "is the rank-based alternative"; Qdrant "advise RRF as the default when you have no evaluation set".
  9 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("query", "user", ("Query", "কুয়েরি"), 100, 162),
    node("bm25", "database", ("BM25 search", "BM25 সার্চ"), 335, 75),
    node("dense", "model", ("Vector search", "ভেক্টর সার্চ"), 335, 250),
    node("fusion", "service", ("Fusion", "ফিউশন"), 575, 162),
    node("es", "server", ("Elasticsearch", "Elasticsearch"), 130, 75),
    node("os", "server", ("OpenSearch", "OpenSearch"), 380, 75),
    node("qd", "server", ("Qdrant", "Qdrant"), 630, 75),
    node("wv", "server", ("Weaviate", "Weaviate"), 380, 250),
]

METRICS = [
    ("k", "k"),
    ("Doc B", "ডকুমেন্ট B"),
    ("Doc A", "ডকুমেন্ট A"),
    ("alpha", "alpha"),
]

CAPTION = (
    "Example: two ranked lists of documents A to G, merged by reciprocal rank fusion. The ranks are invented for the arithmetic.",
    "উদাহরণ: A থেকে G পর্যন্ত ডকুমেন্টের দুটি র‍্যাংক করা তালিকা, রেসিপ্রোকাল র‍্যাংক ফিউশনে মেলানো। র‍্যাংকগুলো হিসাবের জন্য বানানো।",
)

K60 = "60"
KS = ("60 or 2", "৬০ বা ২")


def both(state: str | None = "hot"):
    """The query goes to both searches."""
    return [ln("query", "bm25", "to", state=state), ln("query", "dense", "to", state=state)]


def merge(state: str | None = "hot"):
    """Both searches feed the fusion step."""
    return [ln("bm25", "fusion", "to", state=state), ln("dense", "fusion", "to", state=state)]


STEPS = [
    st(("Two", "দুই সার্চ"),
       ("Keyword and meaning fail differently", "কীওয়ার্ড আর অর্থ, ব্যর্থ হয় ভিন্নভাবে"),
       [("BM25 is a classic keyword score. It needs the query's exact words to appear in a document, so it is great at product codes and names but misses rephrased ideas.",
         "BM25 কীওয়ার্ড দিয়ে খোঁজার ক্লাসিক স্কোর। কুয়েরির হুবহু শব্দ ডকুমেন্টে থাকতে হয়, তাই প্রোডাক্ট কোড আর নামে ভালো, কিন্তু অন্যভাবে বলা ধারণা ধরতে পারে না।"),
        ("A dense retriever turns the query into a vector and matches meaning, not exact words. It is great at ideas, but it can blur rare identifiers, names and codes.",
         "ডেন্স রিট্রিভার কুয়েরিকে ভেক্টর বানিয়ে শব্দ নয়, অর্থ মেলায়। ধারণায় সে ভালো, কিন্তু বিরল আইডেন্টিফায়ার, নাম আর কোড ঝাপসা করে ফেলতে পারে।")],
       [sh("query", "hot"), sh("bm25", "hot", ("needs exact words", "হুবহু শব্দ লাগে")), sh("dense", "hot", ("matches meaning", "অর্থ মেলায়"))],
       both(),
       [None, None, None, None]),

    st(("Hybrid", "হাইব্রিড"),
       ("Run both, then merge", "দুটোই চালান, তারপর মেলান"),
       [("Hybrid search runs both searches and merges the results. Weaviate, for one, runs the vector and BM25 searches in parallel and then fuses them.",
         "হাইব্রিড সার্চ দুটোই চালিয়ে ফল মেলায়। যেমন Weaviate ভেক্টর আর BM25 সার্চ সমান্তরালে চালিয়ে তারপর ফিউজ করে।"),
        ("The catch is that the two retrievers' scores live on different scales. Rank-based fusion sidesteps exactly that problem.",
         "সমস্যা হলো, দুই রিট্রিভারের স্কোর আলাদা মাপের। র‍্যাংক-ভিত্তিক ফিউশন ঠিক এই সমস্যাটাই এড়িয়ে যায়।")],
       [sh("query", "hot"), sh("bm25", "hot"), sh("dense", "hot"), sh("fusion", "hot", ("merges the lists", "তালিকা মেলায়"))],
       both() + merge(),
       [None, None, None, None],
       changes=[("+", "Two result lists become one", "দুটি ফলের তালিকা হয়ে যায় একটি")]),

    st(("RRF", "RRF"),
       ("Reciprocal rank fusion: ranks only", "রেসিপ্রোকাল র‍্যাংক ফিউশন: শুধু র‍্যাংক"),
       [("Reciprocal rank fusion (RRF) ignores raw scores. It combines only each document's rank in each list: every list gives a document points based on its rank, and the points add up.",
         "রেসিপ্রোকাল র‍্যাংক ফিউশন (RRF) কাঁচা স্কোর দেখে না। শুধু প্রতিটি তালিকায় ডকুমেন্টের র‍্যাংক মেলায়: প্রতিটি তালিকা র‍্যাংক ধরে পয়েন্ট দেয়, আর পয়েন্ট যোগ হয়।"),
        ("A document's score is a sum over every ranking that contains it. Each ranking adds 1 / (k + r), where r is the document's rank in that list.",
         "ডকুমেন্টের স্কোর হলো যতগুলো তালিকায় সে আছে, সবগুলোর যোগফল। প্রতিটি তালিকা যোগ করে ১ / (k + r), যেখানে r হলো ওই তালিকায় ডকুমেন্টের র‍্যাংক।")],
       [sh("bm25", "hot", ("a ranked list", "র‍্যাংক করা তালিকা")), sh("dense", "hot", ("a ranked list", "র‍্যাংক করা তালিকা")),
        sh("fusion", "hot", ("adds 1 / (k + r)", "যোগ করে ১ / (k + r)"))],
       merge(),
       [None, None, None, None]),

    st(("Doc B", "ডক B"),
       ("Worked by hand: document B", "হাতে কষা: ডকুমেন্ট B"),
       [("Take k = 60, with ranks invented for the arithmetic. Document B is at rank 2 in both lists.",
         "k = ৬০ ধরুন, আর র‍্যাংকগুলো হিসাবের জন্য বানানো। ডকুমেন্ট B দুই তালিকাতেই র‍্যাংক ২-এ।"),
        ("So B scores 1/62 + 1/62 = 0.032258.",
         "তাই B-এর স্কোর ১/৬২ + ১/৬২ = ০.০৩২২৫৮।")],
       [sh("bm25", "hot", ("B at rank 2", "B র‍্যাংক ২-এ")), sh("dense", "hot", ("B at rank 2", "B র‍্যাংক ২-এ")), sh("fusion", "hot", ("B: 0.032258", "B: ০.০৩২২৫৮"))],
       merge(),
       [K60, "0.032258", None, None]),

    st(("Doc A", "ডক A"),
       ("Worked by hand: document A", "হাতে কষা: ডকুমেন্ট A"),
       [("Document A is first in BM25 (1/61) but fifth in the dense list (1/65). That is 0.031778 in all, so A comes third.",
         "ডকুমেন্ট A BM25-তে প্রথম (১/৬১) কিন্তু ডেন্সে পঞ্চম (১/৬৫)। মোট ০.০৩১৭৭৮, তাই A তৃতীয় হয়।"),
        ("Documents that both retrievers rank well, B and C, overtake it.",
         "দুই রিট্রিভারই যে ডকুমেন্টকে ভালো র‍্যাংক দেয়, সেই B আর C, A-কে ছাড়িয়ে যায়।")],
       [sh("bm25", "hot", ("A at rank 1", "A র‍্যাংক ১-এ")), sh("dense", "hot", ("A at rank 5", "A র‍্যাংক ৫-এ")), sh("fusion", "hot", ("A: 0.031778", "A: ০.০৩১৭৭৮"))],
       merge(),
       [K60, "0.032258", "0.031778", None],
       changes=[("+", "Fused order: B, C, A, E, D, F, G", "মেলানো ক্রম: B, C, A, E, D, F, G")]),

    st(("k", "k"),
       ("A small k favors the top", "ছোট k ওপরের র‍্যাংককে বেশি গুরুত্ব দেয়"),
       [("In the formula, k is a constant. A small k gives the top ranks much more weight.",
         "সূত্রে k একটি ধ্রুবক। k ছোট হলে উপরের র‍্যাংক অনেক বেশি গুরুত্ব পায়।"),
        ("At k = 60, a rank-10 hit keeps 87% of a rank-1 hit's weight. At k = 2, it keeps only 25%.",
         "k = ৬০-এ র‍্যাংক ১০ পায় র‍্যাংক ১-এর প্রায় ৮৭%; k = ২-এ মাত্র ২৫%।")],
       [sh("bm25", "dim"), sh("dense", "dim"), sh("fusion", "hot", ("k sets the weight", "k ঠিক করে ওজন"))],
       merge("dim"),
       [KS, None, None, None],
       changes=[("+", "k = 60: rank 10 keeps 87% of rank 1", "k = ৬০: র‍্যাংক ১০ পায় র‍্যাংক ১-এর ৮৭%"),
                ("-", "k = 2: rank 10 keeps only 25%", "k = ২: র‍্যাংক ১০ পায় মাত্র ২৫%")]),

    st(("Engines", "ইঞ্জিন"),
       ("Engines disagree on k", "ইঞ্জিনভেদে k আলাদা"),
       [("The paper fixed k = 60, and Elasticsearch and OpenSearch default to 60. Qdrant's docs state that k is set to 2 by default.",
         "পেপারে k = ৬০ ঠিক করা, আর Elasticsearch ও OpenSearch-এর ডিফল্টও ৬০। Qdrant-এর ডকসে লেখা, k ডিফল্টে ২।"),
        ("Weaviate's rankedFusion uses 1/(RANK+60).",
         "Weaviate-এর rankedFusion ব্যবহার করে 1/(RANK+60)।")],
       [sh("es", "hot", ("k = 60 by default", "ডিফল্ট k = ৬০")), sh("os", "hot", ("k = 60 by default", "ডিফল্ট k = ৬০")),
        sh("qd", "warn", ("k = 2 in its docs", "ডকসে k = ২")), sh("wv", "hot", ("rankedFusion: 1/(RANK+60)", "rankedFusion: 1/(RANK+60)"))],
       [],
       [KS, None, None, None],
       note=("warn",
             "The same two lists can fuse differently across engines. Check the default before comparing results, and set k explicitly where the API allows it.",
             "একই দুটি তালিকা ইঞ্জিনভেদে আলাদাভাবে মিশতে পারে। ফল তুলনার আগে ডিফল্ট দেখুন, আর API দিলে k নিজে ঠিক করে দিন।")),

    st(("Scores", "স্কোর"),
       ("The score-based alternative", "স্কোর-ভিত্তিক বিকল্প"),
       [("Weaviate's default hybrid method is relativeScoreFusion. It scales each search's scores to 0–1, then weights them with alpha: 0 is keyword only, 1 is vector only, and the server default is 0.75.",
         "Weaviate-এর ডিফল্ট হাইব্রিড পদ্ধতি relativeScoreFusion। এটি প্রতিটি সার্চের স্কোর ০–১ স্কেলে আনে, তারপর alpha দিয়ে ওজন দেয়: ০ মানে শুধু কীওয়ার্ড, ১ মানে শুধু ভেক্টর, সার্ভারের ডিফল্ট ০.৭৫।"),
        ("rankedFusion is the rank-based alternative. Qdrant supports RRF and DBSF, and its docs advise RRF as the default when you have no evaluation set.",
         "rankedFusion হলো র‍্যাংক-ভিত্তিক বিকল্প। Qdrant RRF আর DBSF দুটোই দেয়, আর ইভ্যাল সেট না থাকলে ডিফল্ট হিসেবে RRF-কে পরামর্শ দেয়।")],
       [sh("bm25", "hot", ("scaled to 0–1", "০–১ স্কেলে")), sh("dense", "hot", ("scaled to 0–1", "০–১ স্কেলে")), sh("fusion", "hot", ("weighted by alpha", "alpha-র ওজন"))],
       merge(),
       [None, None, None, "0.75"]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Hybrid search runs a keyword search and a vector search, then merges the two lists.",
         "হাইব্রিড সার্চ একটি কীওয়ার্ড সার্চ আর একটি ভেক্টর সার্চ চালিয়ে দুটি তালিকা মেলায়।")],
       [sh("query"), sh("bm25"), sh("dense"), sh("fusion")],
       both(None) + merge(None),
       [None, None, None, None],
       points=[("RRF merges lists using only ranks, so different score scales do not matter.",
                "RRF শুধু র‍্যাংক ব্যবহার করে, তাই আলাদা স্কেলের স্কোর মেশানোর ঝামেলা নেই।"),
               ("The k default differs: 60 in the paper, Elasticsearch and OpenSearch; 2 in Qdrant's docs.",
                "k-এর ডিফল্ট আলাদা: পেপার, Elasticsearch আর OpenSearch-এ ৬০; Qdrant-এর ডকসে ২।"),
               ("Check the engine's default before comparing results, and set k explicitly where the API allows.",
                "ফল তুলনার আগে ইঞ্জিনের ডিফল্ট দেখুন, আর API দিলে k নিজে ঠিক করে দিন।"),
               ("RRF is a fusion method, not a synonym for hybrid search.",
                "RRF একটি ফিউশন পদ্ধতি, হাইব্রিড সার্চের সমার্থক নয়।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
