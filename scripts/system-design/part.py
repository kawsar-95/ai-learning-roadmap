"""Part-level text: title, intro, quiz and interview questions."""

TITLE = "System Design"
TAGLINE = "the building blocks of systems that scale"
LEDE = (
    "An AI feature runs inside an ordinary system, and that system has to stay fast, correct and up as it grows. "
    "These 40 sections cover requests and latency, scaling and caching, databases, messaging, reliability, "
    "architecture, security, shipping, and four complete designs. They follow the lessons of "
    "<a href=\"https://designed-to-scale.vercel.app/\">Dilum Sanjaya's interactive System Design course</a> in its order, "
    "and each section links to its animated lesson."
)
BN = {
    "title": "সিস্টেম ডিজাইন",
    "tagline": "যে বিল্ডিং ব্লকে সিস্টেম বড় হয়",
    "lede": (
        "একটা AI ফিচার একটা সাধারণ সিস্টেমের ভেতরে চলে, আর সিস্টেম বড় হলেও তাকে দ্রুত, নির্ভুল আর চালু থাকতে হয়। "
        "এই ৪০টি সেকশনে আছে রিকোয়েস্ট আর latency, স্কেলিং আর ক্যাশিং, ডেটাবেস, মেসেজিং, নির্ভরযোগ্যতা, আর্কিটেকচার, "
        "নিরাপত্তা, শিপিং, আর চারটি পূর্ণ ডিজাইন। সেকশনগুলো "
        "<a href=\"https://designed-to-scale.vercel.app/\">Dilum Sanjaya-র ইন্টারঅ্যাক্টিভ System Design কোর্সের</a> "
        "লেসনের ক্রম মেনে চলে, আর প্রতিটি সেকশন থেকে তার অ্যানিমেটেড লেসনে যাওয়া যায়।"
    ),
}

QUIZ = [
    {
        "id": "q1",
        "kind": "mcq",
        "answer": 2,
        "en": {
            "q": "A user is 250 ms away from the server (round-trip time). The page needs a TCP handshake, a TLS 1.3 handshake and one request. Ignoring DNS and server time, when does the first byte of the page arrive?",
            "options": ["After about 250 ms", "After about 500 ms", "After about 750 ms"],
            "why": "Each step costs one round trip: the TCP handshake, the TLS 1.3 handshake, and the request with its response. Three round trips of 250 ms are 750 ms.",
        },
        "bn": {
            "q": "একজন ব্যবহারকারী সার্ভার থেকে ২৫০ ms দূরে (round-trip time)। পেজটার জন্য একটা TCP handshake, একটা TLS handshake আর একটা রিকোয়েস্ট লাগে। DNS আর সার্ভারের সময় বাদ দিলে পেজের প্রথম বাইট কখন আসে?",
            "options": ["প্রায় ২৫০ ms পরে", "প্রায় ৫০০ ms পরে", "প্রায় ৭৫০ ms পরে"],
            "why": "প্রতিটি ধাপে একটা করে round trip লাগে: TCP handshake, TLS handshake, আর রিকোয়েস্ট ও তার উত্তর। ২৫০ ms-এর তিনটি round trip মিলে ৭৫০ ms।",
        },
    },
    {
        "id": "q2",
        "kind": "mcq",
        "answer": 2,
        "en": {
            "q": "Cache keys are spread over 10 servers with hash(key) % 10. You add an 11th server and switch to hash(key) % 11. About how many keys now map to a different server?",
            "options": ["About 1 in 11", "About half", "About 10 in 11"],
            "why": "Changing the modulus moves almost every key, so the cache is nearly empty after the change. Consistent hashing moves only about 1 in 11 keys, the arc that the new server takes over.",
        },
        "bn": {
            "q": "hash(key) % ১০ দিয়ে ক্যাশের key-গুলো ১০টি সার্ভারে ছড়ানো। আপনি ১১ নম্বর সার্ভার যোগ করে hash(key) % ১১ ব্যবহার শুরু করলেন। মোটামুটি কত key এখন অন্য সার্ভারে যায়?",
            "options": ["প্রায় ১১টির মধ্যে ১টি", "প্রায় অর্ধেক", "প্রায় ১১টির মধ্যে ১০টি"],
            "why": "Modulus বদলালে প্রায় সব key-ই সরে যায়, তাই বদলের পর ক্যাশ প্রায় খালি হয়ে যায়। Consistent hashing-এ সরে মাত্র প্রায় ১১টির মধ্যে ১টি, নতুন সার্ভার যে অংশটা নেয় সেটুকু।",
        },
    },
    {
        "id": "q3",
        "kind": "tf",
        "answer": True,
        "en": {
            "q": "With 3 replicas, if every write waits for 2 of them and every read asks 2 of them, each read reaches at least one replica that has the latest successful write.",
            "why": "2 + 2 is more than 3, so any set of 2 replicas that took the write and any set of 2 that answer the read share at least one replica. That is the quorum rule R + W > N.",
        },
        "bn": {
            "q": "৩টি replica থাকলে, যদি প্রতিটি write ২টির নিশ্চয়তার অপেক্ষা করে আর প্রতিটি read ২টিকে জিজ্ঞেস করে, তাহলে প্রতিটি read অন্তত এমন একটা replica-তে পৌঁছায় যেখানে শেষ সফল write আছে।",
            "why": "২ + ২ সংখ্যাটা ৩-এর চেয়ে বেশি, তাই write নেওয়া যেকোনো ২টি replica আর read-এর উত্তর দেওয়া যেকোনো ২টির মধ্যে অন্তত একটা মিল থাকে। এটাই quorum-এর নিয়ম R + W > N।",
        },
    },
    {
        "id": "q4",
        "kind": "mcq",
        "answer": 1,
        "en": {
            "q": "A payment call times out, and the client retries it. What stops the customer from being charged twice?",
            "options": [
                "A shorter timeout on the client",
                "An idempotency key that the server stores with the result",
                "A circuit breaker in front of the payment service",
            ],
            "why": "The client sends the same idempotency key with every retry. The server sees that it already handled that key and returns the stored result instead of charging again.",
        },
        "bn": {
            "q": "একটা পেমেন্ট কল timeout হলো, আর client আবার চেষ্টা (retry) করল। গ্রাহকের কাছ থেকে দুবার টাকা কাটা কীসে আটকায়?",
            "options": [
                "Client-এ আরও ছোট timeout",
                "একটা idempotency key, যেটা সার্ভার ফলাফলসহ জমা রাখে",
                "পেমেন্ট সার্ভিসের সামনে একটা circuit breaker",
            ],
            "why": "Client প্রতিটি retry-তে একই idempotency key পাঠায়। সার্ভার দেখে ওই key-র কাজ আগেই হয়ে গেছে, তাই আবার টাকা না কেটে জমা রাখা ফলাফলটাই ফেরত দেয়।",
        },
    },
    {
        "id": "q5",
        "kind": "tf",
        "answer": False,
        "en": {
            "q": "Adding read replicas raises the number of writes per second a database can accept.",
            "why": "Every replica has to apply every write, so replicas add read capacity and copies, not write capacity. To spread writes, split the data across machines with sharding.",
        },
        "bn": {
            "q": "Read replica যোগ করলে ডেটাবেস প্রতি সেকেন্ডে যত write নিতে পারে, সেই সংখ্যা বাড়ে।",
            "why": "প্রতিটি replica-কে প্রতিটি write নিজের মধ্যে লিখতে হয়, তাই replica বাড়ায় read-এর ক্ষমতা আর কপির সংখ্যা, write-এর ক্ষমতা নয়। write ছড়াতে হলে sharding দিয়ে ডেটা কয়েকটি মেশিনে ভাগ করতে হয়।",
        },
    },
]

INTERVIEW = [
    {
        "lesson": "caching",
        "en": {
            "q": "What is the cache-aside pattern, and how do you stop it from serving stale data?",
            "a": "The application reads the cache first. On a miss it reads the database and stores the result in the cache with an expiry time. On a write it updates the database and deletes the cached key, and the expiry time limits how long a missed delete can serve old data.",
        },
        "bn": {
            "q": "Cache-aside প্যাটার্ন কী, আর এটা যেন পুরনো (stale) ডেটা না দেখায় সেজন্য কী করবেন?",
            "a": "অ্যাপ্লিকেশন আগে ক্যাশে খোঁজে। না পেলে ডেটাবেস থেকে পড়ে, আর ফলাফলটা মেয়াদসহ ক্যাশে রাখে। Write-এর সময় ডেটাবেস আপডেট করে ক্যাশের key মুছে দেয়, আর কোনো delete বাদ পড়লে মেয়াদ (TTL) ঠিক করে দেয় পুরনো ডেটা কতক্ষণ দেখা যেতে পারে।",
        },
    },
    {
        "lesson": "consensus",
        "en": {
            "q": "Why does a consensus protocol such as Raft need a majority, and why do clusters usually have 3 or 5 nodes?",
            "a": "Any two majorities of the same cluster share at least one node, so two candidates cannot both win the same term, and an entry counts as committed only once a majority stores it. A cluster of 3 keeps working with 1 node down and a cluster of 5 with 2 down. An even size adds a node without adding failure tolerance, so clusters use odd sizes.",
        },
        "bn": {
            "q": "Raft-এর মতো consensus protocol-এ majority কেন লাগে, আর cluster-এ সাধারণত ৩ বা ৫টি node কেন থাকে?",
            "a": "একই cluster-এর যেকোনো দুটি majority-তে অন্তত একটা node মিলে যায়, তাই একই term-এ দুজন candidate জিততে পারে না, আর কোনো entry তখনই committed হয় যখন majority সেটা জমা রাখে। ৩টি node-এর cluster একটা node বন্ধ থাকলেও চলে, আর ৫টির cluster দুটি বন্ধ থাকলেও। জোড় সংখ্যায় একটা node বাড়ে কিন্তু ব্যর্থতা সহ্য করার ক্ষমতা বাড়ে না, তাই বিজোড় সংখ্যা রাখা হয়।",
        },
    },
    {
        "lesson": "design-news-feed",
        "en": {
            "q": "In a news feed, when do you fan out on write, and when on read?",
            "a": "Fan-out on write pushes each new post id into every follower's stored feed, so reading a feed is one cheap lookup. It breaks for accounts with millions of followers, because one post becomes millions of writes. A hybrid pushes posts from most accounts and pulls posts from the few very large accounts when the feed is read.",
        },
        "bn": {
            "q": "নিউজ ফিডে কখন fan-out on write করবেন, আর কখন fan-out on read?",
            "a": "Fan-out on write প্রতিটি নতুন পোস্টের id প্রত্যেক follower-এর জমা রাখা ফিডে ঢুকিয়ে দেয়, তাই ফিড পড়া একটা সস্তা lookup। লাখ লাখ follower-ওয়ালা অ্যাকাউন্টে এটা ভেঙে পড়ে, কারণ একটা পোস্ট লাখ লাখ write হয়ে যায়। Hybrid পদ্ধতিতে বেশিরভাগ অ্যাকাউন্টের পোস্ট push করা হয়, আর অল্প কয়েকটি বিশাল অ্যাকাউন্টের পোস্ট ফিড পড়ার সময় pull করা হয়।",
        },
    },
]
