"""Walk-through of lesson 25, Rate Limiting.

Example numbers (mine, checked by script): the API can serve 5,000 requests/s; everyone else sends 2,000; a runaway script sends 5,000.
Demand 7,000 = 140% of capacity; the script is 71% of the work. A limit of 10/s per client: the API sees 2,010/s (40%), 4,990/s rejected.
Token bucket: capacity 20, refill 10/s. A burst of 25 at once: 20 pass, 5 get 429; after 1 s there are 10 tokens again.
Fixed window of 600 a minute: 600 at 12:00:59 and 600 at 12:01:00 = 1,200 in 2 s (60x the average rate). A sliding window still counts the old 600 at 12:01:00.
Twenty gateways, each counting alone: 20 x 10 = 200/s instead of 10 (API 44%, 4,800/s rejected). Split budget: 0.5/s each.
Retrying at once 100 times a second for 30 s = 3,000 rejected requests; obeying Retry-After: 30 = 1.
A tenant with 10,000 users at 0.5/s each = 5,000/s (100%). Quota 1,000/s: 4,000/s rejected, API at (2,000 + 1,000) / 5,000 = 60%.
Launch day: 8,000/s against 5,000: critical 3,000 + important 1,500 fit, 500 of 3,500 background fit, 3,000 shed.
"""
from walkkit import node, sh, ln, st, walk

NODES = [
    node("script", "service", ("Runaway script", "বেপরোয়া script"), 100, 75),
    node("users", "user", ("Other users", "অন্য ব্যবহারকারী"), 100, 265),
    node("gw", "shield", ("Rate limiter", "Rate limiter"), 350, 170),
    node("api", "server", ("API servers", "API server"), 600, 85),
    node("rej", "lock", ("Rejected", "প্রত্যাখ্যাত"), 600, 265),
    node("client", "user", ("A client", "একজন client"), 90, 170),
    node("bucket", "storage", ("Token bucket", "Token bucket"), 350, 170),
    node("n-fixed", "note", ("Fixed window", "Fixed window"), 130, 170),
    node("n-slide", "note", ("Sliding window", "Sliding window"), 380, 170),
    node("n-bucket", "note", ("Token bucket", "Token bucket"), 630, 170),
    node("lb", "balancer", ("Load balancer", "Load balancer"), 275, 170),
    node("gw1", "service", ("Gateway", "Gateway"), 475, 65),
    node("gw2", "service", ("Gateway", "Gateway"), 475, 170),
    node("gw3", "service", ("Gateway", "Gateway"), 475, 275),
    node("store", "cache", ("Shared counter", "Shared counter"), 665, 170),
    node("bad", "user", ("Impatient client", "অধৈর্য client"), 95, 75),
    node("good", "user", ("Polite client", "ভদ্র client"), 95, 265),
    node("tenant", "user", ("Customer X", "Customer X"), 100, 75),
    node("others", "user", ("Other customers", "অন্য customer"), 100, 265),
    node("c-crit", "user", ("Critical", "জরুরি"), 100, 65),
    node("c-imp", "user", ("Important", "গুরুত্বপূর্ণ"), 100, 170),
    node("c-bg", "user", ("Background jobs", "Background job"), 100, 275),
    node("shed", "shield", ("Load shedder", "Load shedder"), 350, 170),
]
METRICS = [("API load", "API-র load"), ("Served", "সামলানো"), ("Rejected", "প্রত্যাখ্যাত"), ("Budget", "Budget")]
CAPTION = ("Example numbers: the API can serve 5,000 requests a second, and ordinary traffic is 2,000.",
           "উদাহরণের সংখ্যা: API সেকেন্ডে ৫,০০০ request সামলাতে পারে, আর সাধারণ traffic ২,০০০।")

EVERYONE = ("everyone", "সবাই")


def front(state_script="warn", state_all="hot"):
    """The five-box front door: two kinds of traffic, the limiter, the API and the rejected pile."""
    return [sh("script", state_script, ("limited", "সীমিত")), sh("users", state_all), sh("gw", state_all, ("10/s each", "প্রতিটি ১০/s")),
            sh("api", state_all, ("40% busy", "৪০% ব্যস্ত")), sh("rej", "warn", ("429 sent", "৪২৯ পাঠানো"))]


def front_links():
    return [ln("script", "gw", "to", 500, "warn", ("5,000/s", "৫,০০০/s")), ln("users", "gw", "to", 1400, "hot", ("2,000/s", "২,০০০/s")),
            ln("gw", "api", "to", 1200, "hot", ("2,010/s", "২,০১০/s")), ln("gw", "rej", "to", 600, "warn", ("4,990/s", "৪,৯৯০/s"))]


STEPS = [
    st(("Runaway", "বেলাগাম script"),
       ("One script, everyone suffers", "একটা script, ভোগে সবাই"),
       [("A customer's script has a bug: it calls your API in a tight loop, 5,000 times a second. Your API servers can handle 5,000 requests a second in total, and everyone else sends another 2,000.",
         "এক customer-এর script-এ একটা bug আছে: আপনার API-কে সে ডাকতে থাকে একটা tight loop-এ, সেকেন্ডে ৫,০০০ বার। আপনার API server মোট সেকেন্ডে ৫,০০০ request সামলাতে পারে, আর বাকি সবাই পাঠায় আরও ২,০০০।"),
        ("That is 7,000 requests a second against a capacity of 5,000: 140%. 71% of the work is the script's, queues build up, and every other user sees timeouts.",
         "অর্থাৎ ৫,০০০ সক্ষমতার তুলনায় সেকেন্ডে ৭,০০০ request: ১৪০%। কাজের প্রায় ৭১% script-এর, queue জমে, আর অন্য প্রতিটি ব্যবহারকারী timeout দেখে।")],
       [sh("script", "warn", ("tight loop", "tight loop")), sh("users", "warn", ("timeouts", "timeout")), sh("api", "warn", ("140% busy", "১৪০% ব্যস্ত"))],
       [ln("script", "api", "to", 500, "warn", ("5,000/s", "৫,০০০/s")), ln("users", "api", "to", 1400, "warn", ("2,000/s", "২,০০০/s"))],
       ["140%", ("timeouts", "timeout"), "0", ("none", "নেই")],
       note=("warn",
             "One misbehaving client, buggy or hostile, can take capacity from everyone. Capacity is shared, so it needs a limit per client.",
             "একটা অসদাচারী client, bug-এর কারণে হোক বা শত্রুতায়, সবার কাছ থেকে সক্ষমতা কেড়ে নিতে পারে। সক্ষমতা ভাগ-করা, তাই প্রতি client-এর জন্য একটা সীমা দরকার।"),
       changes=[("-", "The script sends 5,000 requests a second", "Script সেকেন্ডে ৫,০০০ request পাঠায়"),
                ("-", "The API is at 140% of its capacity", "API তার সক্ষমতার ১৪০%-এ"),
                ("-", "Every other user sees timeouts", "অন্য প্রতিটি ব্যবহারকারী timeout দেখে")]),

    st(("Limit", "সীমা"),
       ("A rate limiter at the front door", "সামনের দরজায় একটা rate limiter"),
       [("Put a rate limiter in the gateway in front of the API. It counts requests per client, identified by API key, user or IP address, and gives each one a budget: say 10 requests a second.",
         "API-র সামনের gateway-তে একটা rate limiter বসান। সে প্রতিটি client-এর request গোনে, API key, ব্যবহারকারী বা IP address দিয়ে চিনে, আর প্রত্যেককে দেয় একটা budget: ধরুন সেকেন্ডে ১০টি request।"),
        ("The script's first 10 requests a second go through, and the other 4,990 are rejected at the door with <code>429 Too Many Requests</code>. Rejecting at the door is cheap, because the excess never reaches the expensive parts. The API now sees 2,010 requests a second, 40% of its capacity, and everyone else is fine.",
         "Script-এর সেকেন্ডে প্রথম ১০টি request ঢোকে, আর বাকি ৪,৯৯০টি দরজাতেই <code>429 Too Many Requests</code> দিয়ে ফেরানো হয়। দরজায় ফেরানো সস্তা, কারণ বাড়তি request ব্যয়বহুল অংশে পৌঁছায়ই না। API এখন দেখে সেকেন্ডে ২,০১০ request, তার সক্ষমতার ৪০%, আর বাকি সবাই ভালো আছে।")],
       front(),
       front_links(),
       ["40%", EVERYONE, "4,990/s", "10/s"],
       note=("insight",
             "The limit is per client, so a client that behaves is never touched by the limit that stops one that does not.",
             "সীমাটা প্রতি client-এর, তাই যে client ঠিকমতো চলে, অন্য client-কে থামানো সীমা তাকে কখনো ছোঁয় না।"),
       changes=[("+", "A rate limiter in the gateway", "Gateway-তে একটা rate limiter"),
                ("~", "Each client gets a budget of 10 requests a second", "প্রতিটি client পায় সেকেন্ডে ১০ request-এর budget"),
                ("~", "The API load drops from 140% to about 40%", "API-র load ১৪০% থেকে নেমে আসে প্রায় ৪০%-এ")]),

    st(("Token bucket", "Token bucket"),
       ("How it counts: the token bucket", "কীভাবে গোনে: token bucket"),
       [("The most common algorithm is the token bucket. Each client has a bucket that holds up to 20 tokens and is refilled at 10 tokens a second. Every request takes one token. If the bucket is empty, the request is rejected.",
         "সবচেয়ে প্রচলিত algorithm হলো token bucket। প্রতিটি client-এর একটা bucket আছে, যাতে সর্বোচ্চ ২০টি token ধরে আর সেকেন্ডে ১০টি করে ভরে ওঠে। প্রতিটি request একটা token নেয়। Bucket খালি থাকলে request প্রত্যাখ্যাত হয়।"),
        ("A quiet client has a full bucket, so it can burst: 25 requests at once get 20 through and 5 rejected. A second later 10 tokens are back. The burst is capped at 20, and the long-run rate at 10 a second.",
         "শান্ত একটা client-এর bucket ভরা থাকে, তাই সে burst করতে পারে: একসাথে ২৫টি request এলে ২০টি ঢোকে আর ৫টি ফিরিয়ে দেওয়া হয়। এক সেকেন্ড পরে ১০টি token ফিরে আসে। Burst সীমিত ২০-এ, আর দীর্ঘমেয়াদি হার সেকেন্ডে ১০।")],
       [sh("client", "hot"), sh("bucket", "hot", ("20 → 0 tokens", "২০ → ০ token")), sh("api", "hot", ("20 served", "২০টি সামলানো")), sh("rej", "warn", ("5 rejected", "৫টি প্রত্যাখ্যাত"))],
       [ln("client", "bucket", "to", 1000, "hot", ("25 at once", "একসাথে ২৫")), ln("bucket", "api", "to", 1200, "hot", ("20 pass", "২০টি পাস")), ln("bucket", "rej", "to", 1200, "warn", ("5 get 429", "৫টি ৪২৯"))],
       [None, ("20 of 25", "২৫-এর ২০"), ("5 of 25", "২৫-এর ৫"), ("20 burst, 10/s", "২০ burst, ১০/s")],
       note=("insight",
             "Two numbers tune it: the bucket size sets how big a burst is allowed, and the refill rate sets the average.",
             "দুটো সংখ্যা এটাকে ঠিক করে: bucket-এর মাপ ঠিক করে কত বড় burst চলবে, আর refill-এর হার ঠিক করে গড়।"),
       changes=[("+", "A bucket of up to 20 tokens for each client", "প্রতিটি client-এর জন্য সর্বোচ্চ ২০ token-এর একটা bucket"),
                ("~", "Refill: 10 tokens a second", "Refill: সেকেন্ডে ১০টি token"),
                ("~", "A request takes one token, and an empty bucket means <code>429</code>", "একটা request একটা token নেয়, আর খালি bucket মানে <code>429</code>")]),

    st(("Algorithms", "Algorithm"),
       ("Windows vs buckets", "Window বনাম bucket"),
       [("A fixed window counts requests per calendar minute and resets at the top of the minute. It is simple, but a client can send a full minute's budget at 12:00:59 and another at 12:01:00: 1,200 requests in 2 seconds, with a limit of 600 a minute.",
         "Fixed window প্রতিটি ক্যালেন্ডার-মিনিটে request গোনে আর মিনিটের শুরুতে শূন্য করে। এটা সরল, কিন্তু একজন client ১২:০০:৫৯-এ পুরো মিনিটের budget পাঠাতে পারে আর ১২:০১:০০-তে আরেকটা: মিনিটে ৬০০-র সীমায় ২ সেকেন্ডে ১,২০০ request।"),
        ("A sliding window fixes the edge: it counts the previous window's requests in proportion to how much of it still overlaps the last minute, and adds the current window's. At 12:01:00 the old 600 still count in full, so the second burst is refused. A token bucket also allows bursts, but only as many as the bucket holds.",
         "Sliding window এই কিনারার সমস্যা মেটায়: আগের window-র request-কে গোনে সেটা শেষ এক মিনিটের সাথে যতটা মিলে যায় সেই অনুপাতে, আর যোগ করে বর্তমান window-র request। ১২:০১:০০-তে পুরোনো ৬০০ পুরোটাই গোনা হয়, তাই দ্বিতীয় burst ফেরানো হয়। Token bucket-ও burst দেয়, তবে ততটাই, যতটা bucket ধরে।")],
       [sh("n-fixed", "warn", ("1,200 in 2 s", "২ s-এ ১,২০০")), sh("n-slide", "hot", ("burst refused", "burst ফেরানো")), sh("n-bucket", "hot", ("burst ≤ 20", "burst ≤ ২০"))],
       [],
       [None, None, None, ("600/min", "৬০০/মিনিট")],
       note=("tip",
             "A fixed window is the easiest to build. If edge bursts would hurt you, choose a sliding window or a token bucket.",
             "Fixed window বানানো সবচেয়ে সহজ। কিনারার burst ক্ষতি করলে sliding window বা token bucket বাছুন।"),
       changes=[("-", "Fixed window: 1,200 requests in 2 seconds at the edge", "Fixed window: কিনারায় ২ সেকেন্ডে ১,২০০ request"),
                ("+", "Sliding window: the old minute still counts, so the burst is refused", "Sliding window: পুরোনো মিনিট এখনো গোনা হয়, তাই burst ফেরানো হয়"),
                ("~", "Token bucket: bursts capped by the bucket size", "Token bucket: burst সীমিত bucket-এর মাপে")]),

    st(("Many gateways", "অনেক gateway"),
       ("Many gateways, one budget", "অনেক gateway, একটাই budget"),
       [("One gateway is not enough, so you run twenty behind a load balancer. Each one sees only part of a client's traffic. If every gateway counts on its own, a client spread across all twenty gets twenty times its limit: 200 requests a second instead of 10.",
         "একটা gateway যথেষ্ট নয়, তাই load balancer-এর পেছনে চালান কুড়িটি। প্রতিটি দেখে একটা client-এর traffic-এর একাংশ মাত্র। প্রতিটি gateway নিজে গুনলে, কুড়িটির সবকটিতে ছড়ানো একটা client পায় সীমার কুড়ি গুণ: ১০-এর বদলে সেকেন্ডে ২০০ request।"),
        ("Keep the counters in a shared store such as Redis, or give each gateway a share of the budget, here half a request a second each. A little inaccuracy is usually fine: a limit is a guard rail, not an invoice.",
         "Counter রাখুন Redis-এর মতো একটা shared store-এ, অথবা প্রতিটি gateway-কে budget-এর একটা ভাগ দিন, এখানে প্রতিটিকে সেকেন্ডে আধটি request। সামান্য ভুল সাধারণত চলে: সীমা একটা guard rail, কোনো invoice নয়।")],
       [sh("client", "warn"), sh("lb", "hot"), sh("gw1", "warn", ("one of 20", "২০টির একটা")), sh("gw2", "warn", ("one of 20", "২০টির একটা")), sh("gw3", "warn", ("one of 20", "২০টির একটা")), sh("store", "dim", ("the fix", "সমাধান"))],
       [ln("client", "lb", "to", 1000, "warn"), ln("lb", "gw1", "to", 1200, "warn"), ln("lb", "gw2", "to", 1200, "warn"), ln("lb", "gw3", "to", 1200, "warn"),
        ln("gw1", "store", None, None, "dim"), ln("gw2", "store", None, None, "dim"), ln("gw3", "store", None, None, "dim")],
       ["44%", EVERYONE, "4,800/s", ("10/s → 200/s", "১০/s → ২০০/s")],
       note=("warn",
             "Per-gateway counters multiply the limit by the number of gateways. Share the counter, or divide the budget.",
             "প্রতি-gateway counter সীমাকে gateway-সংখ্যা দিয়ে গুণ করে দেয়। সব gateway একই counter ব্যবহার করুক, নয়তো budget ভাগ করে দিন।"),
       changes=[("-", "20 gateways each count alone: 20 × 10 = 200 a second", "২০টি gateway প্রত্যেকে একা গোনে: ২০ × ১০ = সেকেন্ডে ২০০"),
                ("+", "A shared counter in Redis", "Redis-এ একটা shared counter"),
                ("~", "Or a share of the budget for each gateway: 10 ÷ 20 = 0.5 a second", "অথবা প্রতি gateway-তে budget-এর ভাগ: ১০ ÷ ২০ = সেকেন্ডে ০.৫")]),

    st(("Back off", "পিছিয়ে যান"),
       ("Tell clients how to behave", "client-কে বলে দিন কী করতে হবে"),
       [("A good <code>429</code> says when to come back: a <code>Retry-After: 30</code> header tells the client to wait 30 seconds before it asks again.",
         "একটা ভালো <code>429</code> বলে দেয় কখন ফিরতে হবে: <code>Retry-After: 30</code> header client-কে জানায় আবার চাওয়ার আগে ৩০ সেকেন্ড অপেক্ষা করতে।"),
        ("A client that retries at once, 100 times a second, adds 3,000 rejected requests in those 30 seconds. A well-behaved client that obeys the header waits 30 seconds and sends 1 request. Clients should also slow themselves down when they see many rejections.",
         "যে client সাথে সাথে আবার চেষ্টা করে, সেকেন্ডে ১০০ বার, সেই ৩০ সেকেন্ডে সে আরও ৩,০০০ ফেরানো request যোগ করে। যে client header মানে, সে ৩০ সেকেন্ড অপেক্ষা করে আর ১টি request পাঠায়। অনেক প্রত্যাখ্যান দেখলে client-দের নিজেদেরও ধীর হওয়া উচিত।")],
       [sh("bad", "warn", ("retries at once", "সাথে সাথে retry")), sh("good", "hot", ("waits 30 s", "৩০ s অপেক্ষা")), sh("gw", "hot", ("429, Retry-After: 30", "৪২৯, Retry-After: ৩০"), x=430)],
       [ln("bad", "gw", "to", 400, "warn", ("100 tries/s", "১০০ বার/s")), ln("good", "gw", "to", 2400, "hot", ("1 try in 30 s", "৩০ s-এ ১ বার"))],
       [None, None, ("3,000 → 1", "৩,০০০ → ১"), "10/s"],
       note=("tip",
             "A client that gets a <code>429</code> should wait, ideally for as long as <code>Retry-After</code> says, instead of hammering the door.",
             "<code>429</code> পাওয়া client-এর উচিত অপেক্ষা করা, আদর্শভাবে <code>Retry-After</code> যতক্ষণ বলে ততক্ষণ, দরজায় ঘুষি মারতে থাকার বদলে।"),
       changes=[("+", "<code>Retry-After: 30</code> on the <code>429</code>", "<code>429</code>-এর সাথে <code>Retry-After: 30</code>"),
                ("-", "Retry at once: 3,000 rejected requests in 30 s", "সাথে সাথে retry: ৩০ s-এ ৩,০০০ ফেরানো request"),
                ("+", "Obey the header: 1 request in 30 s", "Header মানা: ৩০ s-এ ১টি request")]),

    st(("Tenants", "Tenant"),
       ("Case: one customer's 10,000 users", "ঘটনা: এক customer-এর ১০,০০০ ব্যবহারকারী"),
       [("You sell your API to companies. One customer runs a nightly import with 10,000 well-behaved users. Each is far under the personal limit of 10 a second, at half a request a second, but together they send 5,000 requests a second: all of your capacity.",
         "আপনি আপনার API কোম্পানিগুলোর কাছে বেচেন। এক customer প্রতি রাতে একটা import চালায় ১০,০০০ ভদ্র ব্যবহারকারী নিয়ে। প্রত্যেকে সেকেন্ডে ১০টির ব্যক্তিগত সীমার অনেক নিচে, সেকেন্ডে আধটি request করে, কিন্তু একসাথে তারা পাঠায় সেকেন্ডে ৫,০০০ request: আপনার পুরো সক্ষমতা।"),
        ("Per-user limits are not enough. Give each customer a quota as well: say 1,000 requests a second. The import is capped at 1,000, 4,000 a second are rejected, and with the other customers' 2,000 the API sits at 60%. One tenant can no longer starve the others.",
         "ব্যবহারকারী-পিছু সীমা যথেষ্ট নয়। প্রতিটি customer-কেও একটা quota দিন: ধরুন সেকেন্ডে ১,০০০ request। Import আটকে যায় ১,০০০-এ, সেকেন্ডে ৪,০০০ ফেরানো হয়, আর অন্য customer-দের ২,০০০ নিয়ে API থাকে ৬০%-এ। একজন tenant আর অন্যদের অভুক্ত রাখতে পারে না।")],
       [sh("tenant", "warn", ("10,000 users", "১০,০০০ জন")), sh("others", "hot"), sh("gw", "hot", ("quota 1,000/s", "quota ১,০০০/s")), sh("api", "hot", ("60% busy", "৬০% ব্যস্ত")), sh("rej", "warn", ("quota hit", "quota শেষ"))],
       [ln("tenant", "gw", "to", 500, "warn", ("5,000/s", "৫,০০০/s")), ln("others", "gw", "to", 1400, "hot", ("2,000/s", "২,০০০/s")), ln("gw", "api", "to", 1200, "hot", ("3,000/s", "৩,০০০/s")), ln("gw", "rej", "to", 600, "warn", ("4,000/s", "৪,০০০/s"))],
       ["60%", EVERYONE, "4,000/s", ("1,000/s each", "প্রতিটি ১,০০০/s")],
       note=("insight",
             "Limit at more than one level: per user, per customer, and for the system as a whole.",
             "একাধিক স্তরে সীমা দিন: ব্যবহারকারী-পিছু, customer-পিছু, আর পুরো সিস্টেমের জন্য।"),
       changes=[("-", "10,000 users × 0.5 a second = 5,000 a second from one customer", "১০,০০০ ব্যবহারকারী × সেকেন্ডে ০.৫ = এক customer থেকে সেকেন্ডে ৫,০০০"),
                ("+", "A quota of 1,000 a second for each customer", "প্রতিটি customer-এর জন্য সেকেন্ডে ১,০০০-এর quota"),
                ("~", "The API load: 140% → 60%", "API-র load: ১৪০% → ৬০%")]),

    st(("Shedding", "Load shed"),
       ("When everyone spikes: shed load", "সবাই একসাথে এলে: load shed করুন"),
       [("Rate limits stop one client from hogging capacity. But on launch day everyone arrives at once and the total is still more than you can serve: 8,000 requests a second against a capacity of 5,000.",
         "Rate limit একজন client-কে সক্ষমতা দখল করা থেকে আটকায়। কিন্তু লঞ্চের দিনে সবাই একসাথে আসে আর মোট তখনও আপনার সামলানোর চেয়ে বেশি: ৫,০০০ সক্ষমতার তুলনায় সেকেন্ডে ৮,০০০ request।"),
        ("Shed load by priority. Reject the low-priority work first, here background jobs, and keep the capacity for critical requests. 3,000 critical and 1,500 important requests fit in, leaving room for 500 of the 3,500 background ones: 3,000 are shed.",
         "অগ্রাধিকার অনুযায়ী load shed করুন। কম-অগ্রাধিকারের কাজ আগে ফেরান, এখানে background job, আর সক্ষমতা রাখুন জরুরি request-এর জন্য। ৩,০০০ জরুরি আর ১,৫০০ গুরুত্বপূর্ণ request ঢুকে যায়, ৩,৫০০ background-এর মধ্যে জায়গা থাকে ৫০০-র: ৩,০০০ shed হয়।")],
       [sh("c-crit", "hot"), sh("c-imp", "hot"), sh("c-bg", "warn", ("shed first", "আগে shed")), sh("shed", "hot", ("by priority", "অগ্রাধিকারে")), sh("api", "hot", ("100% busy", "১০০% ব্যস্ত")), sh("rej", "warn", ("shed", "shed"))],
       [ln("c-crit", "shed", "to", 900, "hot", ("3,000/s", "৩,০০০/s")), ln("c-imp", "shed", "to", 1200, "hot", ("1,500/s", "১,৫০০/s")), ln("c-bg", "shed", "to", 600, "warn", ("3,500/s", "৩,৫০০/s")),
        ln("shed", "api", "to", 1000, "hot", ("5,000/s", "৫,০০০/s")), ln("shed", "rej", "to", 700, "warn", ("3,000/s", "৩,০০০/s"))],
       ["100%", ("5,000/s", "৫,০০০/s"), ("3,000/s", "৩,০০০/s"), ("by priority", "অগ্রাধিকারে")],
       note=("tip",
             "Well-behaved clients help: when they see many rejections, they slow down on their own.",
             "ভদ্র client-রা সাহায্য করে: অনেক প্রত্যাখ্যান দেখলে তারা নিজে থেকেই ধীর হয়।"),
       changes=[("-", "8,000 requests a second against a capacity of 5,000", "৫,০০০ সক্ষমতার তুলনায় সেকেন্ডে ৮,০০০ request"),
                ("+", "Reject low-priority work first", "কম-অগ্রাধিকারের কাজ আগে ফেরান"),
                ("~", "Critical and important requests all get through", "জরুরি আর গুরুত্বপূর্ণ request সবই ঢোকে")]),

    st(("Recap", "সারাংশ"),
       ("A budget for each client, and shed the rest", "প্রতি client-এর budget, আর বাকিটা shed"),
       [("Give every client a budget, protect the whole system, and tell rejected clients how to behave.",
         "প্রতিটি client-কে একটা budget দিন, পুরো সিস্টেমকে রক্ষা করুন, আর প্রত্যাখ্যাত client-কে বলে দিন কী করতে হবে।")],
       front("hot"),
       front_links(),
       [None, None, None, None],
       points=[("Give each client a <strong>budget</strong> and reject the excess early with <code>429</code>.",
                "প্রতিটি client-কে একটা <strong>budget</strong> দিন আর বাড়তিটা আগেই <code>429</code> দিয়ে ফেরান।"),
               ("<strong>Token buckets</strong> allow short bursts and cap the average rate.",
                "<strong>Token bucket</strong> অল্প burst দেয় আর গড় হার সীমিত করে।"),
               ("Across many gateways, share the counters, or <strong>split the budget</strong>.",
                "অনেক gateway থাকলে সবাই একই counter ব্যবহার করুক, নয়তো <strong>budget ভাগ</strong> করে দিন।"),
               ("Send <code>Retry-After</code> so clients know when to <strong>come back</strong>.",
                "<code>Retry-After</code> পাঠান, যাতে client জানে কখন <strong>ফিরতে</strong> হবে।"),
               ("Add <strong>per-customer quotas</strong>, so one tenant cannot starve the rest.",
                "<strong>Customer-পিছু quota</strong> যোগ করুন, যাতে একজন tenant বাকিদের অভুক্ত না রাখে।"),
               ("When everyone spikes, <strong>shed load</strong> by priority.",
                "সবাই একসাথে এলে অগ্রাধিকার অনুযায়ী <strong>load shed</strong> করুন।")]),
]

WALKS = {"rate-limiting": walk(760, 340, NODES, METRICS, CAPTION, STEPS)}
