""""Start here" boxes for sections 1-19 (Foundations, Scaling, Data)."""
from dsl import basics

BASICS = {
    "request-lifecycle": basics(
        "Opening one web page takes several trips across the network: find the address, open a connection, send the request, wait for the answer. Most of the time goes to these <strong>round trips</strong>, not to the server.",
        [
            ("DNS", "The internet's phone book. It turns a name like <code>shop.example</code> into the IP address of a server."),
            ("Round-trip time (RTT)", "How long a message takes to reach the server and for the reply to come back."),
            ("TCP and TLS handshakes", "The messages that open a reliable connection and then encrypt it, before any page data is sent."),
            ("First byte", "The moment the first piece of the answer reaches the browser after it sent the request."),
        ],
        [
            "Every round trip costs time, and distance makes each one longer.",
            "One page needs many more requests for its scripts, styles and images.",
            "Measure where the time goes before you optimise. Often it is one slow query or a distant user.",
        ],
        "একটা ওয়েব পেজ খুলতে নেটওয়ার্কে কয়েকবার আসা-যাওয়া লাগে: ঠিকানা খোঁজা, connection খোলা, রিকোয়েস্ট পাঠানো, উত্তরের অপেক্ষা। বেশিরভাগ সময় যায় এই <strong>round trip</strong>-গুলোতে, সার্ভারে নয়।",
        [
            ("ডিএনএস (DNS)", "ইন্টারনেটের ফোনবুক। <code>shop.example</code>-এর মতো নামকে সার্ভারের IP ঠিকানায় বদলে দেয়।"),
            ("রাউন্ড-ট্রিপ টাইম (RTT)", "একটা বার্তা সার্ভারে পৌঁছে উত্তর ফিরে আসতে যত সময় লাগে।"),
            ("TCP আর TLS handshake", "পেজের ডেটা পাঠানোর আগে নির্ভরযোগ্য connection খোলা আর সেটা এনক্রিপ্ট করার বার্তা আদান-প্রদান।"),
            ("প্রথম বাইট (first byte)", "রিকোয়েস্ট পাঠানোর পর উত্তরের প্রথম অংশ ব্রাউজারে পৌঁছানোর মুহূর্ত।"),
        ],
        [
            "প্রতিটি round trip-এ সময় লাগে, আর দূরত্ব বাড়লে প্রতিটি আরও লম্বা হয়।",
            "একটা পেজের জন্য স্ক্রিপ্ট, স্টাইল আর ছবির আরও অনেক রিকোয়েস্ট লাগে।",
            "অপ্টিমাইজ করার আগে মেপে দেখুন সময় কোথায় যায়। প্রায়ই সেটা একটা ধীর query বা দূরের কোনো ব্যবহারকারী।",
        ],
    ),
    "latency-throughput": basics(
        "<strong>Latency</strong> is how long one request takes. <strong>Throughput</strong> is how many requests finish each second. A busy server slows down long before it is fully used, and the slowest requests matter more than the average.",
        [
            ("Latency", "The time one request takes, from start to finish."),
            ("Throughput", "How many requests the system finishes each second."),
            ("Percentile (p99)", "The time that 99% of requests beat. It shows the slow tail that an average hides."),
            ("Little's Law", "Requests in flight equal the arrival rate times the time each one takes."),
        ],
        [
            "Read p95 and p99, not only the average.",
            "Waiting grows fast as a server nears full use, so leave spare capacity.",
            "When one request calls many services, a slow answer from one of them becomes common.",
            "Batching raises throughput but adds latency.",
        ],
        "<strong>Latency</strong> মানে একটা রিকোয়েস্টে কত সময় লাগে। <strong>Throughput</strong> মানে প্রতি সেকেন্ডে কতগুলো রিকোয়েস্ট শেষ হয়। পুরো ব্যস্ত হওয়ার অনেক আগেই সার্ভার ধীর হয়ে যায়, আর গড়ের চেয়ে সবচেয়ে ধীর রিকোয়েস্টগুলো বেশি গুরুত্বপূর্ণ।",
        [
            ("লেটেন্সি (latency)", "শুরু থেকে শেষ পর্যন্ত একটা রিকোয়েস্টে যত সময় লাগে।"),
            ("থ্রুপুট (throughput)", "সিস্টেম প্রতি সেকেন্ডে কতগুলো রিকোয়েস্ট শেষ করে।"),
            ("পার্সেন্টাইল (p99)", "যে সময়ের মধ্যে ৯৯% রিকোয়েস্ট শেষ হয়। গড় যে ধীর অংশটা লুকায়, এটা সেটা দেখায়।"),
            ("লিটলের সূত্র (Little's Law)", "একসাথে চলমান রিকোয়েস্টের সংখ্যা সমান আসার হার গুণ প্রতিটির সময়।"),
        ],
        [
            "শুধু গড় নয়, p95 আর p99 দেখুন।",
            "সার্ভার পুরো ব্যস্ততার কাছে গেলে অপেক্ষা দ্রুত বাড়ে, তাই কিছু ক্ষমতা খালি রাখুন।",
            "একটা রিকোয়েস্ট অনেক সার্ভিসকে ডাকলে তাদের কোনো একটার ধীর উত্তর পাওয়া সাধারণ ঘটনা হয়ে যায়।",
            "Batching-এ throughput বাড়ে, কিন্তু latency-ও বাড়ে।",
        ],
    ),
    "napkin-math": basics(
        "<strong>Napkin math</strong> turns a product idea into rough numbers: requests per second, servers, storage and bandwidth. Aim for the right order of magnitude, so you know early which parts of the design will be hard.",
        [
            ("Daily users", "The number of different people who use the product on one day."),
            ("Requests per second", "Daily requests divided by 86,400, the seconds in a day. Round it to 100,000 for quick sums."),
            ("Peak", "The busiest moments of the day, well above the average. Capacity has to cover the peak."),
            ("Order of magnitude", "A factor of ten. A napkin estimate tries to land within one, not to be exact."),
        ],
        [
            "Write your assumptions down, then multiply them out step by step.",
            "Plan for the peak, not the average.",
            "Memory is far faster than disk, and both are far faster than a trip across the world.",
        ],
        "<strong>Napkin math</strong> একটা প্রোডাক্টের ধারণাকে মোটামুটি সংখ্যায় বদলায়: প্রতি সেকেন্ডে রিকোয়েস্ট, সার্ভার, স্টোরেজ আর ব্যান্ডউইথ। লক্ষ্য সঠিক মাত্রা (order of magnitude), যাতে আগেই বোঝা যায় ডিজাইনের কোন অংশ কঠিন হবে।",
        [
            ("দৈনিক ব্যবহারকারী (daily users)", "একদিনে যতজন আলাদা মানুষ প্রোডাক্টটা ব্যবহার করেন।"),
            ("প্রতি সেকেন্ডে রিকোয়েস্ট", "দিনের মোট রিকোয়েস্টকে ৮৬,৪০০ দিয়ে ভাগ, কারণ দিনে এত সেকেন্ড। দ্রুত হিসাবের জন্য ১,০০,০০০ ধরুন।"),
            ("পিক (peak)", "দিনের সবচেয়ে ব্যস্ত সময়, গড়ের অনেক ওপরে। ক্ষমতা পিক সামলানোর মতো হতে হয়।"),
            ("মাত্রা (order of magnitude)", "দশ গুণের ব্যবধান। এই হিসাবের লক্ষ্য সঠিক মাত্রায় থাকা, একদম নিখুঁত হওয়া নয়।"),
        ],
        [
            "আগে অনুমানগুলো লিখে ফেলুন, তারপর ধাপে ধাপে গুণ করুন।",
            "গড় নয়, পিকের জন্য পরিকল্পনা করুন।",
            "মেমরি ডিস্কের চেয়ে অনেক দ্রুত, আর দুটোই পৃথিবীর অন্য প্রান্তে আসা-যাওয়ার চেয়ে অনেক দ্রুত।",
        ],
    ),
    "vertical-horizontal": basics(
        "When one server cannot keep up, you can buy a bigger server (<strong>vertical scaling</strong>) or add more servers (<strong>horizontal scaling</strong>). A bigger machine is simple but has a ceiling. More machines can keep growing, but the app must be built for it.",
        [
            ("Vertical scaling", "Moving to a bigger machine with more CPU, memory or disk."),
            ("Horizontal scaling", "Adding more machines that share the work behind one front door."),
            ("Single point of failure", "One part whose failure takes everything down, such as the only server."),
            ("Autoscaling", "Adding servers when load rises and removing them when it falls, automatically."),
        ],
        [
            "Scaling up is the quickest fix, until the biggest machine is not big enough.",
            "Scaling out needs servers that keep no user state of their own.",
            "Watch CPU, memory, latency and errors to see when one server is overloaded.",
        ],
        "একটা সার্ভার আর না কুলালে বড় সার্ভার কিনতে পারেন (<strong>vertical scaling</strong>), অথবা আরও সার্ভার যোগ করতে পারেন (<strong>horizontal scaling</strong>)। বড় মেশিন সহজ, কিন্তু তার একটা সীমা আছে। বেশি মেশিন দিয়ে বাড়তে থাকা যায়, তবে অ্যাপকে সেভাবে বানাতে হয়।",
        [
            ("ভার্টিক্যাল স্কেলিং (vertical scaling)", "বেশি CPU, মেমরি বা ডিস্কওয়ালা বড় মেশিনে যাওয়া।"),
            ("হরাইজন্টাল স্কেলিং (horizontal scaling)", "আরও মেশিন যোগ করা, যারা এক দরজার পেছনে কাজ ভাগ করে নেয়।"),
            ("একক ব্যর্থতার বিন্দু (single point of failure)", "এমন একটা অংশ, যেটা নষ্ট হলে সব থেমে যায়, যেমন একমাত্র সার্ভার।"),
            ("অটোস্কেলিং (autoscaling)", "লোড বাড়লে নিজে থেকে সার্ভার যোগ করা, আর কমলে সরিয়ে নেওয়া।"),
        ],
        [
            "বড় মেশিন সবচেয়ে দ্রুত সমাধান, যতক্ষণ না সবচেয়ে বড় মেশিনও অপর্যাপ্ত হয়ে পড়ে।",
            "বেশি সার্ভারে ছড়াতে হলে সার্ভারগুলো যেন নিজের কাছে ব্যবহারকারীর অবস্থা না রাখে।",
            "একটা সার্ভার চাপে আছে কি না বুঝতে CPU, মেমরি, latency আর error দেখুন।",
        ],
    ),
    "load-balancing": basics(
        "A <strong>load balancer</strong> gives many servers one address and decides which server gets each request. It checks the servers' health and stops sending traffic to the ones that fail.",
        [
            ("Load balancer", "The front door that spreads incoming requests across a pool of servers."),
            ("Round robin", "Sending each new request to the next server in turn."),
            ("Least connections", "Sending each request to the server that is handling the fewest requests right now."),
            ("Health check", "A regular test request that tells the balancer whether a server can take traffic."),
        ],
        [
            "Health checks let the balancer route around a failed server.",
            "Run more than one balancer, or it becomes the new single point of failure.",
            "Take servers out of rotation one at a time to deploy without downtime.",
        ],
        "<strong>Load balancer</strong> অনেক সার্ভারকে একটা ঠিকানা দেয়, আর ঠিক করে কোন রিকোয়েস্ট কোন সার্ভারে যাবে। এটা সার্ভারগুলোর স্বাস্থ্য পরীক্ষা করে, আর যেগুলো ব্যর্থ হয় সেগুলোতে ট্রাফিক পাঠানো বন্ধ করে।",
        [
            ("লোড ব্যালান্সার (load balancer)", "সামনের দরজা, যা আসা রিকোয়েস্টগুলো একদল সার্ভারে ভাগ করে দেয়।"),
            ("রাউন্ড রবিন (round robin)", "প্রতিটি নতুন রিকোয়েস্ট পালা করে পরের সার্ভারে পাঠানো।"),
            ("সবচেয়ে কম connection (least connections)", "যে সার্ভার এই মুহূর্তে সবচেয়ে কম রিকোয়েস্ট সামলাচ্ছে, তাকে পরের রিকোয়েস্ট দেওয়া।"),
            ("হেলথ চেক (health check)", "নিয়মিত একটা পরীক্ষামূলক রিকোয়েস্ট, যা জানায় সার্ভার ট্রাফিক নিতে পারবে কি না।"),
        ],
        [
            "হেলথ চেকের কারণে ব্যালান্সার নষ্ট সার্ভার এড়িয়ে চলতে পারে।",
            "একাধিক ব্যালান্সার রাখুন, নইলে সেটাই নতুন একক ব্যর্থতার বিন্দু হয়ে যায়।",
            "ডাউনটাইম ছাড়া deploy করতে একবারে একটা করে সার্ভার সরিয়ে আপডেট করুন।",
        ],
    ),
    "stateless": basics(
        "Behind a load balancer, the next request may land on any server. So a server should not remember users between requests. Keep that <strong>state</strong> in a shared store, or let the request carry it.",
        [
            ("State", "Anything a server remembers between requests, such as a login session or a cart."),
            ("Sticky sessions", "Pinning each user to one server. It breaks when that server restarts or is removed."),
            ("Shared store", "A place every server can read, such as Redis, that holds sessions and other state."),
            ("Object storage", "A service for files that any server can reach, instead of one server's own disk."),
        ],
        [
            "A stateless server can be added, restarted or removed without logging anyone out.",
            "A signed token can carry small facts about the user with each request.",
            "Never keep uploaded files on a server's local disk.",
        ],
        "লোড ব্যালান্সারের পেছনে পরের রিকোয়েস্ট যেকোনো সার্ভারে যেতে পারে। তাই একটা সার্ভার রিকোয়েস্টের মাঝে ব্যবহারকারীকে মনে রাখবে না। সেই <strong>state</strong> একটা শেয়ার করা জায়গায় রাখুন, অথবা রিকোয়েস্টের সাথেই পাঠান।",
        [
            ("স্টেট (state)", "রিকোয়েস্টের মাঝে সার্ভার যা মনে রাখে, যেমন লগইন সেশন বা কার্ট।"),
            ("স্টিকি সেশন (sticky sessions)", "প্রত্যেক ব্যবহারকারীকে একটা সার্ভারে বেঁধে রাখা। সেই সার্ভার রিস্টার্ট হলে বা সরে গেলে এটা ভাঙে।"),
            ("শেয়ার করা স্টোর (shared store)", "Redis-এর মতো জায়গা, যা সব সার্ভার পড়তে পারে, আর যেখানে সেশন আর অন্য অবস্থা থাকে।"),
            ("অবজেক্ট স্টোরেজ (object storage)", "ফাইলের জন্য এমন সার্ভিস, যা যেকোনো সার্ভার থেকে পাওয়া যায়, একটা সার্ভারের নিজের ডিস্কের বদলে।"),
        ],
        [
            "Stateless সার্ভার যোগ, রিস্টার্ট বা সরানো যায়, কাউকে লগআউট না করেই।",
            "সই করা token প্রতিটি রিকোয়েস্টের সাথে ব্যবহারকারীর ছোট তথ্য বহন করতে পারে।",
            "আপলোড করা ফাইল কখনো সার্ভারের নিজের ডিস্কে রাখবেন না।",
        ],
    ),
    "caching": basics(
        "Most reads ask for the same few things. A <strong>cache</strong> keeps those answers in memory, close to the app, so the database does not answer the same question again and again.",
        [
            ("Cache-aside", "The app checks the cache first, and on a miss reads the database and stores the answer."),
            ("Hit rate", "The share of reads the cache answers. A small drop means many more database reads."),
            ("TTL", "Time to live: how long an entry may stay in the cache before it expires."),
            ("Stampede", "Many requests missing the same expired key at once and all hitting the database."),
        ],
        [
            "Delete or expire cached data when the source changes, or users see stale answers.",
            "When memory is full, the cache evicts entries, often the least recently used.",
            "Cache \"not found\" answers too, so repeated misses do not reach the database.",
        ],
        "বেশিরভাগ read একই অল্প কয়েকটা জিনিস চায়। <strong>Cache</strong> সেই উত্তরগুলো অ্যাপের কাছে মেমরিতে রাখে, যাতে ডেটাবেসকে একই প্রশ্নের উত্তর বারবার দিতে না হয়।",
        [
            ("ক্যাশ-অ্যাসাইড (cache-aside)", "অ্যাপ আগে ক্যাশে খোঁজে; না পেলে ডেটাবেস থেকে পড়ে উত্তরটা ক্যাশে রাখে।"),
            ("হিট রেট (hit rate)", "কত ভাগ read ক্যাশ নিজেই সামলায়। এটা একটু কমলেও ডেটাবেসে অনেক বেশি read যায়।"),
            ("টিটিএল (TTL)", "Time to live: মেয়াদ শেষ হওয়ার আগে একটা এন্ট্রি কতক্ষণ ক্যাশে থাকতে পারে।"),
            ("স্ট্যাম্পিড (stampede)", "মেয়াদ শেষ হওয়া একই key অনেক রিকোয়েস্ট একসাথে না পেয়ে সবাই ডেটাবেসে ছুটে যাওয়া।"),
        ],
        [
            "মূল ডেটা বদলালে ক্যাশের কপি মুছুন বা মেয়াদ দিন, নইলে ব্যবহারকারী পুরোনো উত্তর দেখে।",
            "মেমরি ভরে গেলে ক্যাশ কিছু এন্ট্রি সরায়, প্রায়ই যেটা সবচেয়ে কম সাম্প্রতিক ব্যবহার হয়েছে।",
            "“পাওয়া যায়নি” উত্তরও ক্যাশ করুন, যাতে বারবার একই খোঁজ ডেটাবেসে না যায়।",
        ],
    ),
    "cdn": basics(
        "A <strong>content delivery network (CDN)</strong> keeps copies of the files everyone downloads on servers near your users. It cuts the distance that no faster server can fix, and it absorbs traffic spikes.",
        [
            ("Edge", "A CDN server close to the users that answers from its own copy."),
            ("Origin", "Your own server, which the edge asks when it does not have a file yet."),
            ("Cache-Control", "The HTTP header that tells shared caches what they may store and for how long."),
            ("Origin shield", "One extra cache layer that all edges ask before they reach your origin."),
        ],
        [
            "Put a version in file names, so a changed file gets a new name and old copies do not linger.",
            "Never let a shared cache store one user's private data, such as a cart.",
            "Popular files warm the edges quickly, so the hit rate rises with traffic.",
        ],
        "<strong>CDN (content delivery network)</strong> সবার ডাউনলোড করা ফাইলগুলোর কপি ব্যবহারকারীদের কাছের সার্ভারে রাখে। এতে দূরত্ব কমে, যা কোনো দ্রুত সার্ভার কমাতে পারে না, আর হঠাৎ ভিড়ের চাপও এটা সামলায়।",
        [
            ("এজ (edge)", "ব্যবহারকারীদের কাছের CDN সার্ভার, যা নিজের কপি থেকে উত্তর দেয়।"),
            ("অরিজিন (origin)", "আপনার নিজের সার্ভার; এজের কাছে ফাইল না থাকলে এজ একে জিজ্ঞেস করে।"),
            ("Cache-Control", "HTTP হেডার, যা শেয়ার করা ক্যাশকে জানায় কী রাখা যাবে আর কতক্ষণ।"),
            ("অরিজিন শিল্ড (origin shield)", "অতিরিক্ত একটা ক্যাশ স্তর, অরিজিনে যাওয়ার আগে সব এজ যাকে জিজ্ঞেস করে।"),
        ],
        [
            "ফাইলের নামে ভার্সন রাখুন, যাতে বদলানো ফাইল নতুন নাম পায় আর পুরোনো কপি থেকে না যায়।",
            "একজনের ব্যক্তিগত ডেটা, যেমন কার্ট, কখনো শেয়ার করা ক্যাশে রাখতে দেবেন না।",
            "জনপ্রিয় ফাইল দ্রুত এজে পৌঁছে যায়, তাই ট্রাফিক বাড়লে হিট রেটও বাড়ে।",
        ],
    ),
    "sql-nosql": basics(
        "<strong>Relational (SQL) databases</strong> keep data in tables with keys, joins and transactions. Document and key-value stores give up some of that to scale out easily or to fit one access pattern. Choose by how the data is used.",
        [
            ("Relational database", "A database of tables linked by keys, queried with SQL."),
            ("Join", "Combining rows from two tables that share a key, in one query."),
            ("Document store", "A database that stores whole records as documents, such as JSON, and reads one at once."),
            ("Key-value store", "A database that stores a value under a key and fetches it by that key, very fast."),
        ],
        [
            "Start with a relational database unless you have a clear reason not to.",
            "NoSQL stores often give up joins and transactions across records.",
            "Use a specialist, such as a search engine, for one job next to the main database.",
        ],
        "<strong>Relational (SQL) ডেটাবেস</strong> ডেটা রাখে টেবিলে, key, join আর transaction সহ। Document আর key-value store এর কিছুটা ছেড়ে দেয়, সহজে অনেক মেশিনে ছড়ানো বা একটা নির্দিষ্ট ব্যবহারের জন্য। ডেটা কীভাবে ব্যবহার হয়, সেটা দেখে বেছে নিন।",
        [
            ("রিলেশনাল ডেটাবেস (relational database)", "key দিয়ে যুক্ত টেবিলের ডেটাবেস, যেখানে SQL দিয়ে প্রশ্ন করা হয়।"),
            ("জয়েন (join)", "একই key থাকা দুটো টেবিলের সারি একটা query-তেই মিলিয়ে আনা।"),
            ("ডকুমেন্ট স্টোর (document store)", "যে ডেটাবেস পুরো রেকর্ড JSON-এর মতো ডকুমেন্ট হিসেবে রাখে আর একবারে পড়ে।"),
            ("কি-ভ্যালু স্টোর (key-value store)", "যে ডেটাবেস একটা key-র নিচে মান রাখে, আর সেই key দিয়ে খুব দ্রুত ফেরত দেয়।"),
        ],
        [
            "স্পষ্ট কারণ না থাকলে relational ডেটাবেস দিয়ে শুরু করুন।",
            "NoSQL store প্রায়ই রেকর্ড জুড়ে join আর transaction ছেড়ে দেয়।",
            "সার্চের মতো নির্দিষ্ট কাজের জন্য মূল ডেটাবেসের পাশে বিশেষ কোনো সিস্টেম রাখুন।",
        ],
    ),
    "indexes": basics(
        "Without an <strong>index</strong>, the database reads every row to answer a query. An index is a sorted structure that jumps straight to the matching rows, but every index makes writes a little slower.",
        [
            ("Full table scan", "Reading every row of a table to find the ones a query wants."),
            ("B-tree", "The usual index structure: a sorted tree that finds a value in a few steps."),
            ("Composite index", "One index on several columns. The order of the columns decides which queries it helps."),
            ("<code>EXPLAIN</code>", "A command that shows the plan the database will use for a query, including its indexes."),
        ],
        [
            "Index the columns your frequent queries filter and sort on.",
            "A function on the column, a leading wildcard or low selectivity can stop an index from helping.",
            "Check with <code>EXPLAIN</code> instead of guessing.",
        ],
        "<strong>Index</strong> না থাকলে query-র উত্তর দিতে ডেটাবেস প্রতিটি সারি পড়ে। Index হলো সাজানো একটা কাঠামো, যা সরাসরি মিলে যাওয়া সারিতে পৌঁছে দেয়, কিন্তু প্রতিটি index write-কে একটু ধীর করে।",
        [
            ("ফুল টেবিল স্ক্যান (full table scan)", "query যে সারিগুলো চায় সেগুলো খুঁজতে টেবিলের প্রতিটি সারি পড়া।"),
            ("বি-ট্রি (B-tree)", "index-এর সাধারণ কাঠামো: সাজানো একটা গাছ, যা কয়েক ধাপেই একটা মান খুঁজে পায়।"),
            ("কম্পোজিট ইনডেক্স (composite index)", "কয়েকটা কলামের ওপর একটা index। কলামের ক্রম ঠিক করে কোন query-তে এটা কাজে আসবে।"),
            ("<code>EXPLAIN</code>", "যে কমান্ড দেখায় ডেটাবেস একটা query কোন পরিকল্পনায় চালাবে, কোন index সহ।"),
        ],
        [
            "যে কলাম দিয়ে ঘনঘন filter বা sort করেন, সেগুলোতে index দিন।",
            "কলামের ওপর function, শুরুতে wildcard বা কম selectivity থাকলে index কাজে না-ও আসতে পারে।",
            "অনুমান না করে <code>EXPLAIN</code> দিয়ে যাচাই করুন।",
        ],
    ),
    "storage-engines": basics(
        "A database writes every change to a <strong>write-ahead log</strong> on disk before it says \"saved\", so, with the default settings, a crash loses nothing that was confirmed. B-trees update data in place and suit reads; LSM-trees only append and suit heavy writes.",
        [
            ("Write-ahead log (WAL)", "A file on disk where each change is written first, so it can be replayed after a crash."),
            ("Checkpoint", "Writing changed pages from memory to the data files, so the log can be trimmed."),
            ("B-tree", "A sorted tree on disk that is updated in place. Good for reads and ranges."),
            ("LSM-tree", "An engine that buffers writes in memory and writes sorted files, merging them later by compaction."),
        ],
        [
            "\"Saved\" is only as sure as the flush to disk behind it.",
            "Group commit flushes many transactions at once to keep writes fast and safe.",
            "Row stores suit transactions; column stores suit analytics over many rows.",
        ],
        "“Saved” বলার আগে ডেটাবেস প্রতিটি পরিবর্তন ডিস্কের <strong>write-ahead log</strong>-এ লেখে, তাই ডিফল্ট সেটিংসে crash হলেও নিশ্চিত করা কিছু হারায় না। B-tree ডেটা নিজের জায়গায় বদলায় আর read-এর জন্য ভালো; LSM-tree শুধু শেষে যোগ করে আর প্রচুর write-এর জন্য ভালো।",
        [
            ("রাইট-অ্যাহেড লগ (WAL)", "ডিস্কের একটা ফাইল, যেখানে প্রতিটি পরিবর্তন আগে লেখা হয়, যাতে crash-এর পর আবার চালানো যায়।"),
            ("চেকপয়েন্ট (checkpoint)", "মেমরির বদলানো পাতাগুলো ডেটা ফাইলে লিখে ফেলা, যাতে লগ ছোট করা যায়।"),
            ("বি-ট্রি (B-tree)", "ডিস্কে সাজানো একটা গাছ, যা নিজের জায়গায় আপডেট হয়। read আর range-এর জন্য ভালো।"),
            ("এলএসএম-ট্রি (LSM-tree)", "যে engine write প্রথমে মেমরিতে জমায়, তারপর সাজানো ফাইলে লেখে, আর পরে compaction দিয়ে মেলায়।"),
        ],
        [
            "“Saved” ততটাই নিশ্চিত, যতটা তার পেছনের ডিস্কে flush।",
            "Group commit অনেক transaction একসাথে flush করে, তাই write দ্রুত আর নিরাপদ থাকে।",
            "Row store transaction-এর জন্য ভালো; column store অনেক সারির বিশ্লেষণের জন্য।",
        ],
    ),
    "replication": basics(
        "<strong>Replication</strong> keeps copies of the database on several machines. One leader takes the writes and followers copy them, which spreads reads and survives the loss of a machine, at the cost of lag and failover work.",
        [
            ("Leader and followers", "One copy accepts writes; the others apply the same changes after it."),
            ("Read replica", "A follower that serves reads, so the leader has more room for writes."),
            ("Replication lag", "How far a follower is behind the leader, so it may show slightly old data."),
            ("Failover", "Promoting a follower to leader when the old leader dies."),
        ],
        [
            "Asynchronous copies are fast but can lose the last writes if the leader dies.",
            "A replica is not a backup: a mistaken delete reaches every copy.",
            "For a short time after a user writes, read their own data from the leader, so they see their change at once.",
        ],
        "<strong>Replication</strong> ডেটাবেসের কপি কয়েকটা মেশিনে রাখে। একটা leader write নেয়, আর follower-রা সেটা কপি করে। এতে read ছড়ানো যায় আর একটা মেশিন হারালেও চলে, তবে দেরি (lag) আর failover-এর ঝামেলা আছে।",
        [
            ("লিডার আর ফলোয়ার (leader and followers)", "একটা কপি write নেয়; বাকিগুলো পরে একই পরিবর্তন নিজের মধ্যে লেখে।"),
            ("রিড রেপ্লিকা (read replica)", "যে follower read সামলায়, যাতে leader write-এর জন্য বেশি জায়গা পায়।"),
            ("রেপ্লিকেশন ল্যাগ (replication lag)", "একটা follower leader থেকে কতটা পিছিয়ে, তাই সে একটু পুরোনো ডেটা দেখাতে পারে।"),
            ("ফেইলওভার (failover)", "পুরোনো leader বন্ধ হলে একটা follower-কে নতুন leader বানানো।"),
        ],
        [
            "Asynchronous কপি দ্রুত, কিন্তু leader বন্ধ হলে শেষ কয়েকটা write হারাতে পারে।",
            "Replica backup নয়: ভুল করে চালানো delete প্রতিটি কপিতে পৌঁছে যায়।",
            "write করার পর অল্প কিছুক্ষণ ব্যবহারকারীর নিজের লেখা ডেটা leader থেকে পড়ুন, যাতে সে নিজের পরিবর্তন সাথে সাথে দেখে।",
        ],
    ),
    "sharding": basics(
        "When the data or the writes outgrow one machine, <strong>sharding</strong> splits them across many. The <strong>shard key</strong> decides which machine holds each row, and whether the load spreads evenly.",
        [
            ("Shard", "One machine's share of the data, with its own reads and writes."),
            ("Shard key", "The field used to decide which shard a row belongs to."),
            ("Range sharding", "Giving each shard a range of keys. Good for range queries, but new keys can pile on one shard."),
            ("Hash sharding", "Placing rows by a hash of the key, which spreads load evenly but scatters ranges."),
        ],
        [
            "Read replicas add read capacity, not write capacity; sharding adds both.",
            "One very popular key can overload its shard, so split or cache it.",
            "Queries without the shard key must ask every shard.",
        ],
        "ডেটা বা write একটা মেশিনের সীমা ছাড়ালে <strong>sharding</strong> সেগুলো অনেক মেশিনে ভাগ করে। <strong>Shard key</strong> ঠিক করে কোন সারি কোন মেশিনে থাকবে, আর লোড সমানভাবে ছড়াবে কি না।",
        [
            ("শার্ড (shard)", "ডেটার একটা মেশিনের ভাগ, যার নিজের read আর write আছে।"),
            ("শার্ড কি (shard key)", "যে ফিল্ড দেখে ঠিক হয় একটা সারি কোন shard-এ যাবে।"),
            ("রেঞ্জ শার্ডিং (range sharding)", "প্রতিটি shard-কে key-র একটা পরিসর দেওয়া। range query-র জন্য ভালো, কিন্তু নতুন key একটা shard-এ জমতে পারে।"),
            ("হ্যাশ শার্ডিং (hash sharding)", "key-র hash দেখে সারি রাখা; লোড সমানভাবে ছড়ায়, কিন্তু range ছড়িয়ে যায়।"),
        ],
        [
            "Read replica শুধু read-এর ক্ষমতা বাড়ায়, write-এর নয়; sharding দুটোই বাড়ায়।",
            "একটা খুব জনপ্রিয় key তার shard-কে চাপে ফেলতে পারে, তাই সেটা ভাগ করুন বা ক্যাশ করুন।",
            "Shard key ছাড়া query-কে প্রতিটি shard-এ জিজ্ঞেস করতে হয়।",
        ],
    ),
    "consistent-hashing": basics(
        "With <code>hash % N</code>, adding one server moves almost every key. <strong>Consistent hashing</strong> puts servers and keys on a ring, so adding or removing a server moves only a small share of the keys.",
        [
            ("Hash ring", "A circle of hash values. Each key belongs to the next server clockwise from its own position."),
            ("Virtual nodes", "Many points on the ring for each server, so the load spreads more evenly."),
            ("<code>hash % N</code>", "Picking a server by the remainder of a hash. Changing N moves almost every key."),
            ("Preference list", "The first N distinct servers clockwise from a key, which hold its copies."),
        ],
        [
            "Adding a server takes over only the keys between it and its neighbour.",
            "Virtual nodes even out the load, and a bigger machine can take more of them.",
            "Caches and distributed databases use it to place data.",
        ],
        "<code>hash % N</code> দিয়ে একটা সার্ভার যোগ করলে প্রায় সব key সরে যায়। <strong>Consistent hashing</strong> সার্ভার আর key-গুলোকে একটা বৃত্তে রাখে, তাই একটা সার্ভার যোগ বা বাদ দিলে অল্প কিছু key-ই সরে।",
        [
            ("হ্যাশ রিং (hash ring)", "hash মানের একটা বৃত্ত। প্রতিটি key তার অবস্থান থেকে ঘড়ির কাঁটার দিকে পরের সার্ভারের।"),
            ("ভার্চুয়াল নোড (virtual nodes)", "প্রতিটি সার্ভারের জন্য বৃত্তে অনেকগুলো বিন্দু, যাতে লোড আরও সমানভাবে ছড়ায়।"),
            ("<code>hash % N</code>", "হ্যাশের ভাগশেষ দেখে সার্ভার বাছা। N বদলালে প্রায় সব key সরে যায়।"),
            ("প্রেফারেন্স লিস্ট (preference list)", "একটা key থেকে ঘড়ির কাঁটার দিকে প্রথম N-টি আলাদা সার্ভার, যারা তার কপি রাখে।"),
        ],
        [
            "নতুন সার্ভার শুধু তার আর তার প্রতিবেশীর মাঝের key-গুলো নেয়।",
            "Virtual node লোড সমান করে, আর বড় মেশিন বেশি virtual node নিতে পারে।",
            "ক্যাশ আর distributed ডেটাবেস ডেটা রাখার জায়গা ঠিক করতে এটা ব্যবহার করে।",
        ],
    ),
    "unique-ids": basics(
        "Every row needs an id that no other row will ever use. One shared counter cannot keep up with a large system, so ids are handed out in blocks, picked at random, or built from the time plus a machine number.",
        [
            ("Ticket server", "A central counter that hands out ids, often in blocks so servers rarely need to ask."),
            ("UUID", "A 128-bit id that is random or partly random, so servers can make one without asking anyone."),
            ("UUIDv7", "A UUID that starts with the time, so new ids sort after old ones."),
            ("Snowflake", "A 64-bit id made of a timestamp, a machine id and a sequence number."),
        ],
        [
            "Fully random ids scatter inserts across an index; time-first ids keep them together.",
            "A clock that steps back can produce duplicate ids, so guard against it.",
            "An id can give away how many rows exist or when one was made.",
        ],
        "প্রতিটি সারির এমন একটা id লাগে, যা আর কোনো সারি কখনো ব্যবহার করবে না। বড় সিস্টেমে একটা শেয়ার করা counter কুলাতে পারে না, তাই id দেওয়া হয় ব্লকে ব্লকে, এলোমেলোভাবে, অথবা সময় আর মেশিনের নম্বর মিলিয়ে।",
        [
            ("টিকিট সার্ভার (ticket server)", "একটা কেন্দ্রীয় counter, যা id দেয়, প্রায়ই ব্লকে, যাতে সার্ভারদের কম জিজ্ঞেস করতে হয়।"),
            ("ইউইউআইডি (UUID)", "১২৮ বিটের একটা id, পুরো বা আংশিক এলোমেলো, তাই কাউকে না জিজ্ঞেস করেই বানানো যায়।"),
            ("UUIDv7", "যে UUID সময় দিয়ে শুরু হয়, তাই নতুন id পুরোনোগুলোর পরে সাজানো থাকে।"),
            ("স্নোফ্লেক (Snowflake)", "৬৪ বিটের id, যাতে থাকে সময়, মেশিনের id আর একটা ক্রমিক নম্বর।"),
        ],
        [
            "পুরো এলোমেলো id index-এ নতুন সারি ছড়িয়ে দেয়; সময় দিয়ে শুরু হওয়া id সেগুলো একসাথে রাখে।",
            "ঘড়ি পিছিয়ে গেলে একই id দুবার তৈরি হতে পারে, তাই এর বিরুদ্ধে ব্যবস্থা রাখুন।",
            "একটা id ফাঁস করে দিতে পারে কতগুলো সারি আছে বা কখন সেটা বানানো হয়েছিল।",
        ],
    ),
    "cap": basics(
        "When the network between copies of your data breaks, each copy must choose: refuse to answer, or answer with data that may be out of date. That is the heart of <strong>CAP</strong>, and most systems make the choice per operation.",
        [
            ("Network partition", "A break that leaves some servers unable to reach the others, while both sides keep running."),
            ("Consistency", "Every read sees the latest write, as if there were one copy."),
            ("Availability", "Every request gets an answer, even during a partition."),
            ("Quorum", "Asking enough copies for each read and write that the two overlap, as in R + W > N."),
        ],
        [
            "During a partition you cannot have both consistency and availability.",
            "Choose per operation: a payment can require a quorum, while a like counter accepts one copy.",
            "After the split heals, conflicting writes must be merged.",
        ],
        "আপনার ডেটার কপিগুলোর মাঝের নেটওয়ার্ক ভেঙে গেলে প্রতিটি কপিকে বেছে নিতে হয়: উত্তর দেবে না, নাকি এমন উত্তর দেবে যা পুরোনো হতে পারে। এটাই <strong>CAP</strong>-এর মূল কথা, আর বেশিরভাগ সিস্টেম এই সিদ্ধান্ত নেয় প্রতিটি কাজ ধরে।",
        [
            ("নেটওয়ার্ক পার্টিশন (network partition)", "এমন ভাঙন, যাতে কিছু সার্ভার বাকিদের কাছে পৌঁছাতে পারে না, অথচ দুই পাশই চালু থাকে।"),
            ("কনসিস্টেন্সি (consistency)", "প্রতিটি read সর্বশেষ write দেখে, যেন কপি একটাই।"),
            ("অ্যাভেইলেবিলিটি (availability)", "Partition চলার সময়ও প্রতিটি রিকোয়েস্ট উত্তর পায়।"),
            ("কোরাম (quorum)", "প্রতিটি read আর write-এ এত কপিকে জিজ্ঞেস করা, যাতে read-এর দল আর write-এর দল অন্তত একটা কপিতে মিলে যায় (overlap করে), যেমন R + W > N।"),
        ],
        [
            "Partition চলার সময় consistency আর availability দুটো একসাথে পাওয়া যায় না।",
            "প্রতিটি কাজ ধরে বেছে নিন: পেমেন্টে quorum লাগতে পারে, আর লাইকের হিসাবে একটা কপিই যথেষ্ট।",
            "ভাঙন সারার পর পরস্পরবিরোধী write-গুলো মেলাতে হয়।",
        ],
    ),
    "consensus": basics(
        "<strong>Consensus</strong> lets a group of servers agree on one leader and one history even when some cannot be reached. Nothing counts without a majority, so two leaders can never both win.",
        [
            ("Split brain", "Two servers both acting as leader at once, each accepting different writes."),
            ("Majority", "More than half of the nodes. Any two majorities share at least one node."),
            ("Raft", "A consensus algorithm that elects a leader by votes and copies its log to the followers."),
            ("Fencing token", "A number that rises with each new leader, so storage can reject an old leader's writes."),
        ],
        [
            "A write is committed once a majority has stored it.",
            "Use 3 or 5 nodes: 3 survive one failure, 5 survive two.",
            "You rarely write consensus code; you use systems built on it, such as etcd.",
        ],
        "<strong>Consensus</strong> একদল সার্ভারকে একজন leader আর একটা ইতিহাসে একমত হতে দেয়, কয়েকটার সাথে যোগাযোগ না থাকলেও। Majority ছাড়া কিছুই গণ্য হয় না, তাই দুজন leader কখনো একসাথে জিততে পারে না।",
        [
            ("স্প্লিট ব্রেইন (split brain)", "দুটো সার্ভার একসাথে leader হয়ে কাজ করছে, আর প্রত্যেকে আলাদা write নিচ্ছে।"),
            ("মেজরিটি (majority)", "অর্ধেকের বেশি node। যেকোনো দুটো majority-তে অন্তত একটা node মিলে যায়।"),
            ("র‍্যাফট (Raft)", "একটা consensus algorithm, যা ভোটে leader বেছে নেয় আর তার log follower-দের কাছে কপি করে।"),
            ("ফেন্সিং টোকেন (fencing token)", "প্রতিটি নতুন leader-এর সাথে বাড়া একটা নম্বর, যাতে storage পুরোনো leader-এর write বাতিল করতে পারে।"),
        ],
        [
            "Majority কোনো write জমা রাখলে তবেই সেটা committed।",
            "৩ বা ৫টি node রাখুন: ৩টি একটা ব্যর্থতা সহ্য করে, ৫টি দুটো।",
            "Consensus কোড আপনি খুব কমই লিখবেন; etcd-এর মতো এর ওপর বানানো সিস্টেম ব্যবহার করবেন।",
        ],
    ),
    "transactions": basics(
        "Two people try to book the last seat in the same millisecond. A <strong>transaction</strong> alone does not stop both from getting it. Atomic updates, row locks or version checks do, and the isolation level decides what each transaction can see.",
        [
            ("Transaction", "A group of reads and writes that succeeds or fails as one."),
            ("Isolation level", "The rule for how much one running transaction sees of others' changes."),
            ("Optimistic concurrency", "Writing only if the row's version has not changed since you read it."),
            ("Deadlock", "Two transactions each waiting for a lock the other holds. The database cancels one."),
        ],
        [
            "Prefer one atomic statement, such as an update with a condition, over read-then-write.",
            "Let constraints, such as a unique key, be the last line of defence.",
            "Never hold a lock while you wait for a slow outside call, such as a payment.",
        ],
        "দুজন মানুষ একই মিলিসেকেন্ডে শেষ আসনটা বুক করতে চায়। শুধু একটা <strong>transaction</strong> দুজনকেই আসন পাওয়া থেকে আটকায় না। আটকায় atomic আপডেট, row lock বা ভার্সন যাচাই, আর isolation level ঠিক করে প্রতিটি transaction কী দেখতে পায়।",
        [
            ("ট্রানজ্যাকশন (transaction)", "কয়েকটা read আর write-এর একটা দল, যা একসাথে সফল বা ব্যর্থ হয়।"),
            ("আইসোলেশন লেভেল (isolation level)", "চলমান একটা transaction অন্যদের পরিবর্তন কতটা দেখবে, তার নিয়ম।"),
            ("অপটিমিস্টিক কনকারেন্সি (optimistic concurrency)", "পড়ার পর থেকে সারির ভার্সন না বদলালে তবেই লেখা।"),
            ("ডেডলক (deadlock)", "দুটো transaction প্রত্যেকে অন্যের ধরে রাখা lock-এর অপেক্ষায়। ডেটাবেস একটাকে বাতিল করে।"),
        ],
        [
            "আগে পড়ে পরে লেখার বদলে শর্তসহ একটা atomic statement ব্যবহার করুন।",
            "Unique key-এর মতো constraint-কে শেষ প্রতিরক্ষা হিসেবে রাখুন।",
            "পেমেন্টের মতো ধীর বাইরের কলের অপেক্ষায় থাকার সময় কখনো lock ধরে রাখবেন না।",
        ],
    ),
    "files": basics(
        "Photos and videos do not belong in your database. Keep the bytes in <strong>object storage</strong> and the facts about them in the database, and let clients upload and download directly, without passing through your servers.",
        [
            ("Object storage", "A service such as Amazon S3 that stores files as objects in buckets, cheaply and durably."),
            ("Presigned URL", "A short-lived link that lets one client upload or download one object directly."),
            ("Multipart upload", "Sending a large file in parts that can be retried one by one."),
            ("Lifecycle rule", "A rule that moves old files to cheaper storage or deletes them after a time."),
        ],
        [
            "Store the file's key, size and owner in the database, not the bytes.",
            "Serve processed images and videos through a CDN.",
            "Keep buckets private; a bucket anyone can list leaks every file.",
        ],
        "ছবি আর ভিডিও ডেটাবেসে রাখার জিনিস নয়। বাইটগুলো রাখুন <strong>object storage</strong>-এ আর সেগুলোর তথ্য ডেটাবেসে, আর client-কে সরাসরি আপলোড-ডাউনলোড করতে দিন, আপনার সার্ভার দিয়ে না ঘুরিয়ে।",
        [
            ("অবজেক্ট স্টোরেজ (object storage)", "Amazon S3-এর মতো সার্ভিস, যা ফাইলকে bucket-এ object হিসেবে কম খরচে আর টেকসইভাবে রাখে।"),
            ("প্রিসাইনড ইউআরএল (presigned URL)", "স্বল্পমেয়াদি একটা লিংক, যা দিয়ে একজন client একটা object সরাসরি আপলোড বা ডাউনলোড করতে পারে।"),
            ("মাল্টিপার্ট আপলোড (multipart upload)", "বড় ফাইল কয়েক ভাগে পাঠানো, যাতে প্রতিটি ভাগ আলাদাভাবে আবার পাঠানো যায়।"),
            ("লাইফসাইকেল রুল (lifecycle rule)", "যে নিয়ম পুরোনো ফাইলকে সস্তা স্টোরেজে সরায়, বা কিছু সময় পরে মুছে ফেলে।"),
        ],
        [
            "ডেটাবেসে ফাইলের key, আকার আর মালিকের তথ্য রাখুন, বাইট নয়।",
            "প্রসেস করা ছবি আর ভিডিও CDN দিয়ে পরিবেশন করুন।",
            "Bucket প্রাইভেট রাখুন; যে bucket-এর তালিকা যে কেউ দেখতে পারে, তা প্রতিটি ফাইল ফাঁস করে।",
        ],
    ),
}
