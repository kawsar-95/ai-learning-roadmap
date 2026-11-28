""""Start here" boxes for sections 20-40 (Communication to Whole systems)."""
from dsl import basics

BASICS = {
    "apis": basics(
        "An <strong>API</strong> is a contract between programs. REST exposes resources at URLs, GraphQL lets the client ask for exactly the fields it needs in one request, and RPC makes a remote call look like a local function.",
        [
            ("REST", "An API style where each resource has a URL and HTTP methods such as GET and POST act on it."),
            ("GraphQL", "A query language where the client names the exact fields it wants, across related objects."),
            ("gRPC", "An RPC framework that generates client and server code from a shared Protocol Buffers definition."),
            ("Cursor pagination", "Getting the next page with a pointer to the last item seen, instead of a page number."),
        ],
        [
            "Each round trip and each unused field costs most on a slow phone network.",
            "Limit how deep and costly a GraphQL query may be.",
            "Add new fields instead of renaming old ones; old apps still read the old names.",
        ],
        "<strong>API</strong> হলো প্রোগ্রামগুলোর মাঝের চুক্তি। REST প্রতিটি resource-কে একটা URL দেয়, GraphQL-এ client এক রিকোয়েস্টেই ঠিক যে ফিল্ডগুলো দরকার তা চায়, আর RPC দূরের কলকে লোকাল function-এর মতো দেখায়।",
        [
            ("রেস্ট (REST)", "যে API ধরনে প্রতিটি resource-এর একটা URL থাকে, আর GET বা POST-এর মতো HTTP method তার ওপর কাজ করে।"),
            ("গ্রাফকিউএল (GraphQL)", "এমন query ভাষা, যেখানে client সম্পর্কিত object জুড়ে ঠিক কোন ফিল্ড চায় তা বলে দেয়।"),
            ("জিআরপিসি (gRPC)", "একটা RPC ফ্রেমওয়ার্ক, যা Protocol Buffers-এর শেয়ার করা সংজ্ঞা থেকে client আর সার্ভারের কোড বানায়।"),
            ("কার্সর পেজিনেশন (cursor pagination)", "পেজ নম্বরের বদলে শেষ দেখা আইটেমের একটা নির্দেশক দিয়ে পরের পেজ আনা।"),
        ],
        [
            "ধীর মোবাইল নেটওয়ার্কে প্রতিটি round trip আর প্রতিটি অদরকারি ফিল্ডের দাম সবচেয়ে বেশি।",
            "একটা GraphQL query কতটা গভীর আর দামি হতে পারবে, তার সীমা দিন।",
            "পুরোনো ফিল্ডের নাম না বদলে নতুন ফিল্ড যোগ করুন; পুরোনো অ্যাপ এখনো পুরোনো নাম পড়ে।",
        ],
    ),
    "queues": basics(
        "A <strong>message queue</strong> sits between a request and slow work. The web server puts a job on the queue and answers at once, and workers do the job at their own pace, so a traffic spike becomes a backlog instead of an outage.",
        [
            ("Producer and consumer", "The producer puts messages on the queue; the consumer, or worker, takes them off and does the work."),
            ("Acknowledge", "The consumer's signal that it finished a message. Messages not acknowledged when the consumer fails are delivered again."),
            ("At-least-once delivery", "Every message arrives, but some may arrive twice, so consumers must handle repeats."),
            ("Dead-letter queue", "A side queue for messages that keep failing, so people can inspect them."),
        ],
        [
            "Make every consumer idempotent: doing a job twice must equal doing it once.",
            "Watch the queue depth and the age of the oldest message.",
            "If producers always outrun consumers, bound the queue and slow the producers down.",
        ],
        "<strong>Message queue</strong> রিকোয়েস্ট আর ধীর কাজের মাঝখানে বসে। ওয়েব সার্ভার কাজটা queue-তে রেখে সাথে সাথে উত্তর দেয়, আর worker-রা নিজেদের গতিতে কাজ করে। ফলে হঠাৎ ভিড় সার্ভিস বন্ধ না করে শুধু জমে থাকা কাজ হয়ে যায়।",
        [
            ("প্রোডিউসার আর কনজিউমার (producer and consumer)", "Producer queue-তে message রাখে; consumer বা worker সেটা তুলে নিয়ে কাজ করে।"),
            ("অ্যাকনলেজ (acknowledge)", "Consumer-এর সংকেত যে কাজ শেষ। এটা না পেলে message আবার পাঠানো হয়।"),
            ("অন্তত একবার পৌঁছানো (at-least-once delivery)", "প্রতিটি message পৌঁছায়, কিন্তু কিছু দুবার পৌঁছাতে পারে, তাই consumer-কে পুনরাবৃত্তি সামলাতে হয়।"),
            ("ডেড-লেটার কিউ (dead-letter queue)", "বারবার ব্যর্থ হওয়া message-এর জন্য আলাদা queue, যাতে মানুষ সেগুলো পরীক্ষা করতে পারে।"),
        ],
        [
            "প্রতিটি consumer-কে idempotent বানান: একই কাজ দুবার করা আর একবার করার ফল যেন একই হয়।",
            "Queue-র দৈর্ঘ্য আর সবচেয়ে পুরোনো message-এর বয়স নজরে রাখুন।",
            "Producer সবসময় consumer-এর চেয়ে দ্রুত হলে queue-র সীমা রাখুন আর producer-কে ধীর করুন।",
        ],
    ),
    "pubsub": basics(
        "With <strong>pub/sub</strong>, a service announces that something happened by publishing an event, and every service that cares reacts in its own time. The publisher does not wait for anyone, or even know who is listening.",
        [
            ("Event", "A message that says something happened, such as <code>OrderPlaced</code>."),
            ("Topic", "A named channel that events are published to and that services subscribe to."),
            ("Subscriber", "A service that receives the events of a topic it has subscribed to."),
            ("Transactional outbox", "Saving the event in the same database transaction as the data, then publishing it from there."),
        ],
        [
            "A queue spreads work across workers; a topic tells many services the same news.",
            "Events mean eventual consistency and a flow that no single program shows.",
            "A log such as Kafka keeps events, so a new service can replay history.",
        ],
        "<strong>Pub/sub</strong>-এ একটা সার্ভিস একটা ইভেন্ট publish করে জানায় যে কিছু ঘটেছে, আর যে সার্ভিসের দরকার সে নিজের সময়ে সাড়া দেয়। Publisher কারও জন্য অপেক্ষা করে না, এমনকি কে শুনছে তাও জানে না।",
        [
            ("ইভেন্ট (event)", "যে message জানায় কিছু একটা ঘটেছে, যেমন <code>OrderPlaced</code>।"),
            ("টপিক (topic)", "নাম দেওয়া একটা চ্যানেল, যেখানে ইভেন্ট publish হয় আর সার্ভিসগুলো subscribe করে।"),
            ("সাবস্ক্রাইবার (subscriber)", "যে সার্ভিস নিজের subscribe করা topic-এর ইভেন্টগুলো পায়।"),
            ("ট্রানজ্যাকশনাল আউটবক্স (transactional outbox)", "ডেটার একই transaction-এ ইভেন্টটা ডেটাবেসে রাখা, তারপর সেখান থেকে publish করা।"),
        ],
        [
            "Queue কাজ worker-দের মধ্যে ভাগ করে; topic অনেক সার্ভিসকে একই খবর দেয়।",
            "ইভেন্ট মানে ডেটা পরে গিয়ে মেলে, আর পুরো প্রবাহ কোনো একটা প্রোগ্রামে দেখা যায় না।",
            "Kafka-র মতো log ইভেন্ট জমা রাখে, তাই নতুন সার্ভিস পুরোনো ইতিহাস আবার পড়তে পারে।",
        ],
    ),
    "realtime": basics(
        "Plain HTTP only answers when the client asks. For chat, live scores and notifications, the server needs a way to reach the client: <strong>polling</strong>, long polling, Server-Sent Events or WebSockets.",
        [
            ("Polling", "Asking the server \"anything new?\" again and again, every few seconds."),
            ("Long polling", "The server holds each request open until there is news or a timeout passes."),
            ("Server-Sent Events (SSE)", "One open HTTP response that the server keeps writing events into."),
            ("WebSocket", "A long-lived connection on which both sides can send messages at any time."),
        ],
        [
            "Use SSE for one-way updates and WebSockets for two-way chat or games.",
            "A persistent connection lives on one server, so you must track which one.",
            "Store messages for offline users, and wake their app with a push notification.",
        ],
        "সাধারণ HTTP শুধু client জিজ্ঞেস করলেই উত্তর দেয়। চ্যাট, লাইভ স্কোর আর নোটিফিকেশনের জন্য সার্ভারকে নিজে থেকে client-এর কাছে পৌঁছাতে হয়: <strong>polling</strong>, long polling, Server-Sent Events বা WebSocket দিয়ে।",
        [
            ("পোলিং (polling)", "কয়েক সেকেন্ড পরপর সার্ভারকে বারবার জিজ্ঞেস করা, “নতুন কিছু আছে?”"),
            ("লং পোলিং (long polling)", "খবর আসা বা timeout হওয়া পর্যন্ত সার্ভার প্রতিটি রিকোয়েস্ট খোলা রাখে।"),
            ("সার্ভার-সেন্ট ইভেন্টস (SSE)", "একটা খোলা HTTP উত্তর, যাতে সার্ভার একের পর এক ইভেন্ট লিখতে থাকে।"),
            ("ওয়েবসকেট (WebSocket)", "একটা স্থায়ী connection, যাতে দুই পক্ষই যেকোনো সময় message পাঠাতে পারে।"),
        ],
        [
            "এক দিকের আপডেটে SSE, আর দুই দিকের চ্যাট বা গেমে WebSocket ব্যবহার করুন।",
            "স্থায়ী connection একটা নির্দিষ্ট সার্ভারে থাকে, তাই কোনটায় আছে সেটা মনে রাখতে হয়।",
            "অফলাইন ব্যবহারকারীর message জমা রাখুন, আর push notification দিয়ে তার অ্যাপ জাগান।",
        ],
    ),
    "redundancy": basics(
        "Everything fails eventually. <strong>Redundancy</strong> means two or more of every critical part, in places that do not fail together, plus a tested way to switch over. Availability targets and recovery goals tell you how much of it you need.",
        [
            ("Single point of failure", "A part that exists only once, so its failure stops the whole service."),
            ("Availability zone", "A group of data centers with its own power and cooling, separate from other zones."),
            ("RTO and RPO", "How fast service must come back, and how much recent data you can afford to lose."),
            ("Canary release", "Sending a new version to a small share of traffic first, and rolling back if it is worse."),
        ],
        [
            "Each extra nine of availability cuts the allowed downtime by ten.",
            "A failover that has never been tested probably does not work.",
            "Redundancy does not help when the same bad release reaches every copy.",
        ],
        "সবকিছুই একদিন নষ্ট হয়। <strong>Redundancy</strong> মানে প্রতিটি জরুরি অংশের অন্তত দুটো, এমন জায়গায় যারা একসাথে নষ্ট হয় না, সাথে বদলে নেওয়ার একটা পরীক্ষিত উপায়। কতটা লাগবে, তা বলে availability-র লক্ষ্য আর পুনরুদ্ধারের লক্ষ্য।",
        [
            ("একক ব্যর্থতার বিন্দু (single point of failure)", "যে অংশ মাত্র একটা আছে, তাই সেটা নষ্ট হলে পুরো সার্ভিস থেমে যায়।"),
            ("অ্যাভেইলেবিলিটি জোন (availability zone)", "নিজস্ব বিদ্যুৎ আর ঠান্ডা রাখার ব্যবস্থাসহ ডেটা সেন্টারের একটা দল, অন্য zone থেকে আলাদা।"),
            ("আরটিও আর আরপিও (RTO and RPO)", "কত দ্রুত সার্ভিস ফেরাতে হবে, আর সাম্প্রতিক কতটুকু ডেটা হারানো চলবে।"),
            ("ক্যানারি রিলিজ (canary release)", "নতুন ভার্সন আগে অল্প কিছু ট্রাফিকে পাঠানো, আর খারাপ হলে ফিরিয়ে নেওয়া।"),
        ],
        [
            "Availability-তে প্রতিটি বাড়তি ৯ (নাইন) অনুমোদিত ডাউনটাইমকে দশ ভাগের এক ভাগে নামায়।",
            "যে failover কখনো পরীক্ষা করা হয়নি, সেটা সম্ভবত কাজ করে না।",
            "একই খারাপ রিলিজ সব কপিতে পৌঁছালে redundancy কোনো কাজে আসে না।",
        ],
    ),
    "rate-limiting": basics(
        "A <strong>rate limiter</strong> gives every client a fair budget of requests, so one runaway script cannot take the service down for everyone. Requests over the budget get <code>429 Too Many Requests</code>.",
        [
            ("Rate limit", "The most requests a client may send in a period of time."),
            ("Token bucket", "A bucket of tokens that refills at a steady rate; each request spends one, and bursts use up the stock."),
            ("Sliding window", "Counting requests over the last minute at every moment, not per calendar minute."),
            ("Load shedding", "Rejecting low-priority work first when the whole system is overloaded."),
        ],
        [
            "Tell clients when to retry with a <code>Retry-After</code> header.",
            "Keep shared counters, such as in Redis, when many gateways enforce one limit.",
            "Give each customer a quota too, so one tenant cannot starve the others.",
        ],
        "<strong>Rate limiter</strong> প্রত্যেক client-কে রিকোয়েস্টের একটা ন্যায্য বাজেট দেয়, যাতে একটা লাগামছাড়া script সবার জন্য সার্ভিস বন্ধ করে দিতে না পারে। বাজেটের বেশি রিকোয়েস্ট পায় <code>429 Too Many Requests</code>।",
        [
            ("রেট লিমিট (rate limit)", "নির্দিষ্ট সময়ে একজন client সর্বোচ্চ যতগুলো রিকোয়েস্ট পাঠাতে পারে।"),
            ("টোকেন বাকেট (token bucket)", "স্থির হারে ভরা token-এর বালতি; প্রতিটি রিকোয়েস্ট একটা খরচ করে, আর হঠাৎ ভিড় জমানো token শেষ করে।"),
            ("স্লাইডিং উইন্ডো (sliding window)", "ক্যালেন্ডারের মিনিট ধরে নয়, প্রতিটি মুহূর্তে শেষ এক মিনিটের রিকোয়েস্ট গোনা।"),
            ("লোড শেডিং (load shedding)", "পুরো সিস্টেম চাপে থাকলে আগে কম গুরুত্বপূর্ণ কাজ বাতিল করা।"),
        ],
        [
            "<code>Retry-After</code> হেডার দিয়ে client-কে জানান কখন আবার চেষ্টা করবে।",
            "অনেক gateway একটা সীমা মানলে counter শেয়ার করা জায়গায় রাখুন, যেমন Redis-এ।",
            "প্রতিটি গ্রাহকের জন্যও quota দিন, যাতে একজন বাকিদের বঞ্চিত করতে না পারে।",
        ],
    ),
    "timeouts-retries": basics(
        "When a service you call is struggling, give up in time with a <strong>timeout</strong>, retry carefully with backoff and jitter, and stop calling for a while with a circuit breaker. An idempotency key keeps retries from charging twice.",
        [
            ("Timeout", "The longest you wait for an answer before you give up on a call."),
            ("Exponential backoff with jitter", "Waiting longer after each failure, plus a random amount, so clients do not retry together."),
            ("Circuit breaker", "A switch that stops calls to a failing service for a while, then lets a trial call through."),
            ("Idempotency key", "A unique value sent with every attempt of one operation, so the server does it only once."),
        ],
        [
            "Retry at one layer only; retries at every layer multiply the load.",
            "Pass the remaining deadline to the services you call.",
            "Give each dependency its own pool, so one slow service cannot use up every thread.",
        ],
        "আপনি যে সার্ভিসকে ডাকছেন সেটা চাপে থাকলে <strong>timeout</strong> দিয়ে সময়মতো হাল ছাড়ুন, backoff আর jitter দিয়ে সাবধানে আবার চেষ্টা করুন, আর circuit breaker দিয়ে কিছুক্ষণ ডাকা বন্ধ রাখুন। Idempotency key retry-কে দুবার টাকা কাটা থেকে আটকায়।",
        [
            ("টাইমআউট (timeout)", "একটা কলের উত্তরের জন্য হাল ছাড়ার আগে সর্বোচ্চ যতক্ষণ অপেক্ষা করবেন।"),
            ("এক্সপোনেনশিয়াল ব্যাকঅফ আর জিটার (exponential backoff with jitter)", "প্রতিবার ব্যর্থ হলে আরও বেশি অপেক্ষা, সাথে কিছু এলোমেলো সময়, যাতে সবাই একসাথে আবার চেষ্টা না করে।"),
            ("সার্কিট ব্রেকার (circuit breaker)", "এমন একটা সুইচ, যা ব্যর্থ সার্ভিসে কিছুক্ষণ কল বন্ধ রাখে, তারপর একটা পরীক্ষামূলক কল যেতে দেয়।"),
            ("আইডেমপোটেন্সি কি (idempotency key)", "একটা কাজের প্রতিটি চেষ্টায় পাঠানো একই ইউনিক মান, যাতে সার্ভার কাজটা একবারই করে।"),
        ],
        [
            "শুধু একটা স্তরে retry করুন; প্রতিটি স্তরে retry করলে লোড গুণ হয়ে বাড়ে।",
            "যে সার্ভিসগুলোকে ডাকছেন, তাদের কাছে বাকি সময়টুকু (deadline) পাঠান।",
            "প্রতিটি dependency-কে আলাদা pool দিন, যাতে একটা ধীর সার্ভিস সব thread দখল করতে না পারে।",
        ],
    ),
    "observability": basics(
        "<strong>Observability</strong> lets you find out what is wrong, where and why from the data the system already emits. Metrics show that something is wrong, traces show where the time went, and logs show what exactly happened.",
        [
            ("Metric", "A number recorded over time, such as the request rate, the error rate or the latency."),
            ("Trace", "The path of one request across services, made of timed steps called spans."),
            ("Service level objective (SLO)", "A target for what users feel, such as 99.9% of checkouts succeeding within one second."),
            ("Post-mortem", "A written review after an incident: what happened, the impact, and what will prevent a repeat."),
        ],
        [
            "Alert on what users feel, not on CPU.",
            "Put a request id in every log line.",
            "Stop the damage first, such as by rolling back, then look for the cause.",
        ],
        "<strong>Observability</strong> দিয়ে সিস্টেম নিজে যে ডেটা দেয় তা থেকেই জানা যায় কী ভুল হয়েছে, কোথায় আর কেন। Metrics দেখায় কিছু একটা ভুল, trace দেখায় সময় কোথায় গেল, আর log দেখায় ঠিক কী ঘটেছিল।",
        [
            ("মেট্রিক (metric)", "সময়ের সাথে রেকর্ড করা সংখ্যা, যেমন রিকোয়েস্টের হার, error-এর হার বা latency।"),
            ("ট্রেস (trace)", "একটা রিকোয়েস্টের সার্ভিস জুড়ে পথ, span নামের সময় মাপা ধাপ দিয়ে তৈরি।"),
            ("সার্ভিস লেভেল অবজেক্টিভ (SLO)", "ব্যবহারকারীর অভিজ্ঞতার জন্য একটা লক্ষ্যমাত্রা, যেমন ৯৯.৯% checkout এক সেকেন্ডের মধ্যে সফল হওয়া।"),
            ("পোস্ট-মর্টেম (post-mortem)", "কোনো incident-এর পর লেখা পর্যালোচনা: কী ঘটেছিল, কী প্রভাব পড়েছিল, আর আবার যেন না ঘটে সেজন্য কী করা হবে।"),
        ],
        [
            "CPU নয়, ব্যবহারকারী যা টের পায় তার ওপর alert দিন।",
            "প্রতিটি log লাইনে request id রাখুন।",
            "আগে ক্ষতি থামান, যেমন rollback করে, তারপর কারণ খুঁজুন।",
        ],
    ),
    "microservices": basics(
        "A <strong>monolith</strong> is one codebase deployed as one unit; <strong>microservices</strong> split the system into services that teams deploy on their own. Microservices buy team independence and pay for it with network calls and harder consistency.",
        [
            ("Monolith", "One application, built and deployed as one unit, usually with one database."),
            ("Microservice", "A small service built around one business capability, owned and deployed by one team."),
            ("Distributed monolith", "Services that must be deployed together or share a database, so they keep the costs and lose the benefits."),
            ("Strangler fig", "Replacing an old system piece by piece, routing one capability at a time to new services."),
        ],
        [
            "Start with a monolith until the boundaries are clear.",
            "Each service owns its data; others go through its API.",
            "Never rewrite a whole monolith in one go.",
        ],
        "<strong>Monolith</strong> মানে একটা কোডবেস, যা একসাথে deploy হয়; <strong>microservices</strong> সিস্টেমকে এমন সার্ভিসে ভাগ করে, যা প্রতিটি টিম নিজে deploy করে। Microservices টিমকে স্বাধীনতা দেয়, আর তার দাম দিতে হয় network call আর কঠিন consistency দিয়ে।",
        [
            ("মনোলিথ (monolith)", "একটা অ্যাপ্লিকেশন, যা একসাথে build আর deploy হয়, সাধারণত একটা ডেটাবেস নিয়ে।"),
            ("মাইক্রোসার্ভিস (microservice)", "ব্যবসার একটা কাজ ঘিরে বানানো ছোট সার্ভিস, যা একটা টিমের মালিকানায় চলে আর deploy হয়।"),
            ("ডিস্ট্রিবিউটেড মনোলিথ (distributed monolith)", "যে সার্ভিসগুলো একসাথে deploy করতে হয় বা ডেটাবেস শেয়ার করে, তাই খরচ থাকে কিন্তু সুবিধা থাকে না।"),
            ("স্ট্র্যাংলার ফিগ (strangler fig)", "পুরোনো সিস্টেমকে টুকরো টুকরো করে বদলানো, একবারে একটা কাজ নতুন সার্ভিসে পাঠিয়ে।"),
        ],
        [
            "সীমানা স্পষ্ট না হওয়া পর্যন্ত monolith দিয়ে শুরু করুন।",
            "প্রতিটি সার্ভিস নিজের ডেটার মালিক; অন্যরা তার API দিয়ে যায়।",
            "পুরো monolith কখনো একবারে নতুন করে লিখবেন না।",
        ],
    ),
    "service-discovery": basics(
        "Service instances come and go, so callers cannot rely on fixed addresses. A <strong>service registry</strong> tracks where the healthy instances are, and an <strong>API gateway</strong> gives outside clients one front door.",
        [
            ("Service registry", "A database of services and the network locations of their running instances."),
            ("Readiness probe", "A check that tells Kubernetes when a container is ready to accept traffic."),
            ("Service mesh", "Proxies next to each service that handle retries, encryption and metrics outside the code."),
            ("API gateway", "The single entry point that routes outside requests to the right internal service."),
        ],
        [
            "Instances register on startup and deregister on shutdown.",
            "Send no traffic to an instance until it is ready.",
            "Run the registry as a replicated cluster, because every call depends on it.",
        ],
        "সার্ভিসের instance আসে আর যায়, তাই caller নির্দিষ্ট ঠিকানার ওপর ভরসা করতে পারে না। <strong>Service registry</strong> মনে রাখে সুস্থ instance-গুলো কোথায়, আর <strong>API gateway</strong> বাইরের client-দের জন্য একটা দরজা রাখে।",
        [
            ("সার্ভিস রেজিস্ট্রি (service registry)", "সার্ভিস আর তাদের চালু instance-গুলোর নেটওয়ার্ক ঠিকানার একটা ডেটাবেস।"),
            ("রেডিনেস প্রোব (readiness probe)", "যে পরীক্ষা Kubernetes-কে জানায় একটা container ট্রাফিক নেওয়ার জন্য কখন তৈরি।"),
            ("সার্ভিস মেশ (service mesh)", "প্রতিটি সার্ভিসের পাশে চলা proxy, যা কোডের বাইরে থেকে retry, এনক্রিপশন আর metrics সামলায়।"),
            ("এপিআই গেটওয়ে (API gateway)", "একমাত্র প্রবেশপথ, যা বাইরের রিকোয়েস্ট সঠিক ভেতরের সার্ভিসে পাঠায়।"),
        ],
        [
            "Instance চালু হলে নিজের নাম লেখায়, বন্ধ হলে নাম সরিয়ে নেয়।",
            "তৈরি না হওয়া পর্যন্ত কোনো instance-এ ট্রাফিক পাঠাবেন না।",
            "Registry-কে replicated cluster হিসেবে চালান, কারণ প্রতিটি কল এর ওপর নির্ভর করে।",
        ],
    ),
    "sagas": basics(
        "One action, such as booking a trip, can span several services, each with its own database. A <strong>saga</strong> commits each step locally and, if a later step fails, undoes the finished ones with compensating steps.",
        [
            ("Two-phase commit", "A protocol where a coordinator asks all participants to prepare, then to commit or abort together."),
            ("Saga", "A sequence of local transactions, each in its own service."),
            ("Compensating transaction", "A step that undoes an earlier one, such as cancelling a hotel booking."),
            ("Orchestration and choreography", "Either one orchestrator directs the steps, or each service reacts to the others' events."),
        ],
        [
            "Two-phase commit blocks if the coordinator fails.",
            "Other users can see a saga's half-finished state, so name it, such as <code>PENDING</code>.",
            "A timeout means you do not know the result; check before you compensate.",
        ],
        "ট্রিপ বুক করার মতো একটা কাজ কয়েকটা সার্ভিস জুড়ে চলতে পারে, যাদের প্রত্যেকের নিজের ডেটাবেস। <strong>Saga</strong> প্রতিটি ধাপ নিজের জায়গায় commit করে, আর পরের কোনো ধাপ ব্যর্থ হলে শেষ হওয়া ধাপগুলো উল্টো ধাপ দিয়ে বাতিল করে।",
        [
            ("টু-ফেজ কমিট (two-phase commit)", "যে protocol-এ একজন coordinator সবাইকে আগে প্রস্তুত হতে বলে, তারপর একসাথে commit বা abort করতে বলে।"),
            ("সাগা (saga)", "কয়েকটা local transaction-এর ধারা, প্রতিটি নিজের সার্ভিসে।"),
            ("কমপেনসেটিং ট্রানজ্যাকশন (compensating transaction)", "আগের একটা ধাপকে বাতিল করার ধাপ, যেমন হোটেল বুকিং ক্যানসেল করা।"),
            ("অর্কেস্ট্রেশন আর কোরিওগ্রাফি (orchestration and choreography)", "হয় একজন orchestrator ধাপগুলো চালায়, নয়তো প্রতিটি সার্ভিস অন্যদের ইভেন্ট দেখে কাজ করে।"),
        ],
        [
            "Coordinator বন্ধ হয়ে গেলে two-phase commit আটকে যায়।",
            "অন্যরা saga-র অর্ধেক শেষ অবস্থা দেখতে পারে, তাই <code>PENDING</code>-এর মতো নাম দিয়ে চিহ্নিত করুন।",
            "Timeout মানে ফলাফল জানা নেই; বাতিল করার আগে অবস্থা যাচাই করুন।",
        ],
    ),
    "batch-stream": basics(
        "Large volumes of events are processed in two ways: <strong>batch</strong> jobs compute over a fixed set of data on a schedule, and <strong>stream</strong> processors update results as each event arrives. Most large systems run both.",
        [
            ("Batch processing", "Computing results over a fixed set of data, such as yesterday's events, in one run."),
            ("MapReduce", "A batch model: map emits key-value pairs, the system groups them by key, and reduce combines each group."),
            ("Window", "A slice of time, such as each minute, over which a stream processor counts events."),
            ("Watermark", "A marker that tells the processor how far event time has progressed."),
        ],
        [
            "Count late events by when they happened, not when they arrived.",
            "One very hot key can stall a batch job; pre-aggregate it or split it.",
            "HyperLogLog counts distinct users in a small, fixed amount of memory.",
        ],
        "অনেক ইভেন্ট দুইভাবে প্রসেস করা হয়: <strong>batch</strong> কাজ নির্দিষ্ট সময়ে একটা স্থির ডেটাসেটের ওপর হিসাব করে, আর <strong>stream</strong> প্রসেসর প্রতিটি ইভেন্ট আসার সাথে সাথে ফল আপডেট করে। বেশিরভাগ বড় সিস্টেম দুটোই চালায়।",
        [
            ("ব্যাচ প্রসেসিং (batch processing)", "একটা স্থির ডেটাসেট, যেমন গতকালের সব ইভেন্ট, একবারে হিসাব করা।"),
            ("ম্যাপরিডিউস (MapReduce)", "একটা batch মডেল: map key-value জোড়া বানায়, সিস্টেম key ধরে সাজায়, আর reduce প্রতিটি দল মেলায়।"),
            ("উইন্ডো (window)", "সময়ের একটা টুকরো, যেমন প্রতি মিনিট, যার মধ্যে stream প্রসেসর ইভেন্ট গোনে।"),
            ("ওয়াটারমার্ক (watermark)", "একটা চিহ্ন, যা প্রসেসরকে জানায় ঘটনার সময় কতদূর এগিয়েছে।"),
        ],
        [
            "দেরিতে আসা ইভেন্ট গুনুন ঘটনার সময় ধরে, পৌঁছানোর সময় ধরে নয়।",
            "একটা খুব গরম key পুরো batch কাজ আটকে দিতে পারে; আগেভাগে যোগ করুন বা ভাগ করুন।",
            "HyperLogLog অল্প আর নির্দিষ্ট মেমরিতে আলাদা ব্যবহারকারী গুনতে পারে।",
        ],
    ),
    "authentication": basics(
        "<strong>Authentication</strong> proves who a user is. Store passwords as slow, salted hashes, keep sessions safe, and make stolen or guessed passwords useless with rate limits, a second factor or passkeys.",
        [
            ("Password hash", "A one-way, deliberately slow fingerprint of a password, made with a unique salt, such as Argon2id."),
            ("Session", "What the server remembers after login, found through a random id in a secure cookie."),
            ("Credential stuffing", "Trying username and password pairs leaked from other sites, at scale."),
            ("Passkey", "A login that signs a challenge with a private key on the device, so there is no password to steal."),
        ],
        [
            "Never store passwords in plain text, or with a fast hash.",
            "Reset links must work once and expire soon.",
            "Multi-factor authentication stops most attacks that use stolen passwords.",
        ],
        "<strong>Authentication</strong> প্রমাণ করে ব্যবহারকারী আসলে কে। পাসওয়ার্ড রাখুন ধীর, salt দেওয়া hash হিসেবে, session নিরাপদ রাখুন, আর rate limit, দ্বিতীয় প্রমাণ বা passkey দিয়ে চুরি বা অনুমান করা পাসওয়ার্ডকে অকেজো করুন।",
        [
            ("পাসওয়ার্ড হ্যাশ (password hash)", "পাসওয়ার্ডের এক দিকের, ইচ্ছা করে ধীর একটা ছাপ, আলাদা salt দিয়ে বানানো, যেমন Argon2id।"),
            ("সেশন (session)", "লগইনের পর সার্ভার যা মনে রাখে, নিরাপদ cookie-র একটা random id দিয়ে খুঁজে পাওয়া যায়।"),
            ("ক্রেডেনশিয়াল স্টাফিং (credential stuffing)", "অন্য সাইট থেকে ফাঁস হওয়া ইউজারনেম আর পাসওয়ার্ড বিপুল সংখ্যায় চেষ্টা করা।"),
            ("পাসকি (passkey)", "যে লগইনে ডিভাইসের private key দিয়ে একটা challenge সই করা হয়, তাই চুরি করার মতো কোনো পাসওয়ার্ড নেই।"),
        ],
        [
            "পাসওয়ার্ড কখনো plain text-এ বা দ্রুত hash-এ রাখবেন না।",
            "রিসেট লিংক যেন একবারই কাজ করে আর দ্রুত মেয়াদ শেষ হয়।",
            "Multi-factor authentication চুরি করা পাসওয়ার্ড দিয়ে বেশিরভাগ আক্রমণ ঠেকায়।",
        ],
    ),
    "authorization": basics(
        "<strong>Authorization</strong> decides what a known user may see or do. Check it on every request and for every object, because knowing who someone is does not tell you whether this order is theirs.",
        [
            ("Broken object level authorization", "Letting a user reach another user's object just by changing an id in the request."),
            ("Mass assignment", "Copying every field a client sends into a record, including fields like <code>role</code>."),
            ("Role-based access control (RBAC)", "Granting permissions to roles such as viewer or admin, and roles to users."),
            ("Least privilege", "Giving each person and service only the permissions they need."),
        ],
        [
            "Check ownership on the server for every object id, not only in the user interface.",
            "Copy only an allow-list of fields from a client's request.",
            "Act with the user's rights, not your service's broad rights, and keep an audit log.",
        ],
        "<strong>Authorization</strong> ঠিক করে পরিচিত একজন ব্যবহারকারী কী দেখতে বা করতে পারবে। প্রতিটি রিকোয়েস্টে আর প্রতিটি জিনিসের জন্য এটা যাচাই করুন, কারণ কেউ কে, তা জানলেই জানা যায় না অর্ডারটা তার কি না।",
        [
            ("ব্রোকেন অবজেক্ট লেভেল অথরাইজেশন (broken object level authorization)", "রিকোয়েস্টের একটা id বদলেই অন্য ব্যবহারকারীর জিনিসে পৌঁছে যেতে দেওয়া।"),
            ("মাস অ্যাসাইনমেন্ট (mass assignment)", "Client-এর পাঠানো প্রতিটি ফিল্ড রেকর্ডে কপি করা, <code>role</code>-এর মতো ফিল্ডসহ।"),
            ("রোল-ভিত্তিক অ্যাক্সেস (RBAC)", "Viewer বা admin-এর মতো role-কে অনুমতি দেওয়া, আর ব্যবহারকারীকে role দেওয়া।"),
            ("ন্যূনতম অনুমতি (least privilege)", "প্রত্যেক মানুষ আর সার্ভিসকে শুধু দরকারি অনুমতিটুকু দেওয়া।"),
        ],
        [
            "শুধু ইউজার ইন্টারফেসে নয়, সার্ভারে প্রতিটি object id-র মালিকানা যাচাই করুন।",
            "Client-এর রিকোয়েস্ট থেকে শুধু অনুমোদিত ফিল্ডের তালিকা কপি করুন।",
            "নিজের সার্ভিসের বড় অনুমতি নয়, ব্যবহারকারীর অনুমতি নিয়ে কাজ করুন, আর audit log রাখুন।",
        ],
    ),
    "encryption": basics(
        "Protect data on the wire with <strong>TLS</strong> and on disk with encryption at rest, and keep the keys and passwords your services use out of the code. Many leaks start with a secret in the wrong place.",
        [
            ("TLS", "The protocol that encrypts a connection and proves, with a certificate, which server you reached."),
            ("Encryption at rest", "Keeping stored data encrypted, so a stolen disk or backup is unreadable."),
            ("Envelope encryption", "A data key encrypts the data, and a key in a key management service encrypts the data key."),
            ("Tokenization", "Replacing a card number with a token that is useless on its own."),
        ],
        [
            "Automate certificate renewal; an expired certificate takes the site down.",
            "Encrypt traffic inside the data center too.",
            "Keep secrets in a secrets manager, and if a secret leaks, rotate it first.",
        ],
        "নেটওয়ার্কে ডেটা রক্ষা করুন <strong>TLS</strong> দিয়ে আর ডিস্কে encryption at rest দিয়ে, আর সার্ভিসগুলোর key আর পাসওয়ার্ড কোডের বাইরে রাখুন। অনেক ফাঁস শুরু হয় ভুল জায়গায় রাখা একটা সিক্রেট থেকে।",
        [
            ("টিএলএস (TLS)", "যে protocol connection এনক্রিপ্ট করে, আর certificate দিয়ে প্রমাণ করে আপনি কোন সার্ভারে পৌঁছেছেন।"),
            ("এনক্রিপশন অ্যাট রেস্ট (encryption at rest)", "জমা রাখা ডেটা এনক্রিপ্ট করে রাখা, যাতে চুরি হওয়া ডিস্ক বা backup পড়া না যায়।"),
            ("এনভেলপ এনক্রিপশন (envelope encryption)", "একটা data key ডেটা এনক্রিপ্ট করে, আর key management service-এর একটা key সেই data key-কে এনক্রিপ্ট করে।"),
            ("টোকেনাইজেশন (tokenization)", "কার্ড নম্বরের বদলে এমন একটা token রাখা, যা নিজে থেকে কোনো কাজের নয়।"),
        ],
        [
            "Certificate নবায়ন স্বয়ংক্রিয় করুন; মেয়াদ শেষ হওয়া certificate সাইট বন্ধ করে দেয়।",
            "ডেটা সেন্টারের ভেতরের ট্রাফিকও এনক্রিপ্ট করুন।",
            "সিক্রেট রাখুন secrets manager-এ, আর কোনো সিক্রেট ফাঁস হলে আগে সেটা বদলান।",
        ],
    ),
    "testing": basics(
        "Tests tell you a change is safe before users find out. Write many fast <strong>unit tests</strong> for the logic, fewer integration and contract tests for the parts that talk to others, and a handful of end-to-end tests.",
        [
            ("Unit test", "A test that calls one function with known inputs and checks the result, in milliseconds."),
            ("Test double", "A stand-in for a real dependency in a test, such as a fake, a stub or a mock."),
            ("Contract test", "A test of what one team's service expects from another's API, run in the provider's build."),
            ("Flaky test", "A test that sometimes fails for no real reason, which teaches people to ignore failures."),
        ],
        [
            "Write the test for a bug before you fix it.",
            "Keep the test pyramid the right way up: mostly unit tests.",
            "Fix or remove flaky tests instead of re-running them.",
        ],
        "টেস্ট ব্যবহারকারীরা টের পাওয়ার আগেই জানায় একটা পরিবর্তন নিরাপদ কি না। লজিকের জন্য অনেক দ্রুত <strong>unit test</strong>, অন্যদের সাথে কথা বলা অংশের জন্য কিছু integration আর contract test, আর অল্প কয়েকটা end-to-end test লিখুন।",
        [
            ("ইউনিট টেস্ট (unit test)", "যে টেস্ট জানা input দিয়ে একটা function ডেকে ফল যাচাই করে, মিলিসেকেন্ডে।"),
            ("টেস্ট ডাবল (test double)", "টেস্টে আসল dependency-র জায়গায় বসানো বিকল্প, যেমন fake, stub বা mock।"),
            ("কন্ট্রাক্ট টেস্ট (contract test)", "এক টিমের সার্ভিস অন্যের API থেকে কী আশা করে তার টেস্ট, যা provider-এর build-এ চলে।"),
            ("ফ্লেকি টেস্ট (flaky test)", "যে টেস্ট আসল কারণ ছাড়াই মাঝে মাঝে ফেল করে, ফলে মানুষ ব্যর্থতা উপেক্ষা করতে শেখে।"),
        ],
        [
            "Bug ঠিক করার আগে তার জন্য টেস্ট লিখুন।",
            "Test pyramid সোজা রাখুন: বেশিরভাগই unit test।",
            "Flaky টেস্ট বারবার চালানোর বদলে ঠিক করুন বা সরিয়ে দিন।",
        ],
    ),
    "cicd": basics(
        "<strong>Continuous integration</strong> builds and tests every small change on a clean machine. <strong>Continuous delivery</strong> keeps every passing build ready for production, and careful releases, such as blue-green, canaries and feature flags, make it safe to ship often.",
        [
            ("Continuous integration", "Merging small changes into the mainline often, with every push built and tested automatically."),
            ("Artifact", "The built package, such as a container image, that is tested once and then deployed unchanged."),
            ("Blue-green deployment", "Two identical production environments; the router switches traffic to the new one, and back if needed."),
            ("Feature flag", "A setting that decides who sees a feature, so deploying and releasing are separate."),
        ],
        [
            "Build once and promote the same artifact to every environment.",
            "Every schema change must work with the old and the new code at once.",
            "Speed and stability improve together with small, frequent, reversible changes.",
        ],
        "<strong>Continuous integration</strong> প্রতিটি ছোট পরিবর্তন একটা পরিষ্কার মেশিনে build আর test করে। <strong>Continuous delivery</strong> প্রতিটি সফল build-কে production-এর জন্য তৈরি রাখে, আর blue-green, canary বা feature flag-এর মতো সাবধানী রিলিজ ঘনঘন ship করা নিরাপদ করে।",
        [
            ("কন্টিনিউয়াস ইন্টিগ্রেশন (continuous integration)", "ছোট পরিবর্তন ঘনঘন মূল branch-এ মেলানো, আর প্রতিটি push স্বয়ংক্রিয়ভাবে build আর test হওয়া।"),
            ("আর্টিফ্যাক্ট (artifact)", "তৈরি করা প্যাকেজ, যেমন container image, যা একবার test হয় আর তারপর না বদলে deploy হয়।"),
            ("ব্লু-গ্রিন ডিপ্লয়মেন্ট (blue-green deployment)", "দুটো একই রকম production environment; router নতুনটায় ট্রাফিক পাঠায়, দরকারে আবার পুরোনোটায়।"),
            ("ফিচার ফ্ল্যাগ (feature flag)", "একটা সেটিং, যা ঠিক করে কে একটা ফিচার দেখবে, তাই deploy আর release আলাদা হয়।"),
        ],
        [
            "একবার build করুন, আর সেই একই artifact প্রতিটি environment-এ পাঠান।",
            "প্রতিটি schema পরিবর্তন যেন পুরোনো আর নতুন কোড দুটোর সাথেই একসাথে চলে।",
            "ছোট, ঘনঘন আর ফেরানো যায় এমন পরিবর্তনে গতি আর স্থিতিশীলতা একসাথে বাড়ে।",
        ],
    ),
    "hld-lld": basics(
        "<strong>High-level design (HLD)</strong> is the map of a system: its services, stores and connections. <strong>Low-level design (LLD)</strong> is the inside of one part: its modules, tables, states and edge cases. They meet at contracts.",
        [
            ("High-level design (HLD)", "Deciding which parts exist, what each owns, how they talk and where data lives."),
            ("Low-level design (LLD)", "Deciding how one component is built: modules, interfaces, tables, algorithms and error handling."),
            ("Contract", "What a component promises other teams: its API and the events it publishes."),
            ("Trade-off", "A choice that gains one thing by giving up another, such as speed for consistency."),
        ],
        [
            "Work top-down: requirements, estimates, API, data model, HLD, then deep dives.",
            "Every arrow and store on a diagram is a decision with an alternative.",
            "Changing a contract is an HLD change that other teams must agree to.",
        ],
        "<strong>High-level design (HLD)</strong> হলো সিস্টেমের মানচিত্র: তার সার্ভিস, স্টোর আর সংযোগ। <strong>Low-level design (LLD)</strong> হলো একটা অংশের ভেতরটা: মডিউল, টেবিল, অবস্থা আর বিশেষ ক্ষেত্র। দুটো মেলে contract-এ।",
        [
            ("হাই-লেভেল ডিজাইন (HLD)", "কোন কোন অংশ থাকবে, কে কী দেখবে, তারা কীভাবে কথা বলবে আর ডেটা কোথায় থাকবে, তা ঠিক করা।"),
            ("লো-লেভেল ডিজাইন (LLD)", "একটা অংশ ভেতরে কীভাবে তৈরি হবে: মডিউল, interface, টেবিল, algorithm আর error সামলানো।"),
            ("কন্ট্রাক্ট (contract)", "একটা অংশ অন্য টিমকে যা প্রতিশ্রুতি দেয়: তার API আর যে ইভেন্টগুলো সে publish করে।"),
            ("ট্রেড-অফ (trade-off)", "একটা জিনিস পেতে আরেকটা ছেড়ে দেওয়ার সিদ্ধান্ত, যেমন consistency-র বদলে গতি।"),
        ],
        [
            "ওপর থেকে নিচে কাজ করুন: requirement, হিসাব, API, ডেটা মডেল, HLD, তারপর গভীরে।",
            "ডায়াগ্রামের প্রতিটি তীর আর স্টোর একটা সিদ্ধান্ত, যার একটা বিকল্প ছিল।",
            "Contract বদলানো একটা HLD পরিবর্তন, যাতে অন্য টিমগুলোর সম্মতি লাগে।",
        ],
    ),
    "design-url-shortener": basics(
        "A URL shortener turns a long link into a short code and redirects anyone who opens it. It reads about a hundred times more than it writes, so the design is about <strong>unique codes</strong>, a fast cached read path and simple key-value storage.",
        [
            ("Base 62", "Writing a number with digits, lowercase and uppercase letters, so a big number becomes a short code."),
            ("Birthday problem", "Why random or truncated codes collide much sooner than intuition says."),
            ("<code>301</code> and <code>302</code>", "Permanent and temporary redirects. A 302 brings every click back, so it can be counted."),
            ("Negative caching", "Also caching \"no such code\", so bots asking for random codes do not reach the database."),
        ],
        [
            "Turn a unique counter into a code, and scramble it so codes cannot be counted.",
            "Count clicks with events on a stream, off the redirect path.",
            "Fight abuse with rate limits, destination checks and expiring links.",
        ],
        "URL শর্টেনার লম্বা লিংককে ছোট কোডে বদলায়, আর যে খোলে তাকে আসল ঠিকানায় পাঠায়। এটা লেখার চেয়ে প্রায় একশো গুণ বেশি পড়ে, তাই ডিজাইনের মূল বিষয় <strong>ইউনিক কোড</strong>, দ্রুত ক্যাশ করা read আর সরল key-value স্টোরেজ।",
        [
            ("বেস ৬২ (base 62)", "সংখ্যা, ছোট হাতের আর বড় হাতের অক্ষর দিয়ে একটা সংখ্যা লেখা, যাতে বড় সংখ্যা ছোট কোড হয়।"),
            ("জন্মদিনের সমস্যা (birthday problem)", "এলোমেলো বা কেটে ছোট করা কোড কেন অনুমানের চেয়ে অনেক আগে একই হয়ে যায়।"),
            ("<code>301</code> আর <code>302</code>", "স্থায়ী আর অস্থায়ী redirect। ৩০২ প্রতিটি ক্লিক ফেরত আনে, তাই গোনা যায়।"),
            ("নেগেটিভ ক্যাশিং (negative caching)", "“এমন কোড নেই” উত্তরটাও ক্যাশ করা, যাতে এলোমেলো কোড চাওয়া bot ডেটাবেসে না পৌঁছায়।"),
        ],
        [
            "একটা ইউনিক counter-কে কোডে বদলান, আর এলোমেলো করুন যাতে কোড গোনা না যায়।",
            "ক্লিক গুনুন stream-এর ইভেন্ট দিয়ে, redirect-এর পথের বাইরে।",
            "অপব্যবহার ঠেকান rate limit, গন্তব্য যাচাই আর মেয়াদওয়ালা লিংক দিয়ে।",
        ],
    ),
    "design-news-feed": basics(
        "A news feed shows recent posts from everyone you follow, fast. The key decision is when to do the work: build the feed when it is read (<strong>pull</strong>), or deliver each post to followers when it is written (<strong>push</strong>).",
        [
            ("Fan-out on read (pull)", "Building a feed at read time by fetching the latest posts of every account the user follows."),
            ("Fan-out on write (push)", "Adding each new post to the stored feed of every follower when it is written."),
            ("Hybrid", "Pushing posts from most accounts and pulling posts from the few very large ones at read time."),
            ("Hydration", "Fetching the full posts for the post ids stored in a feed list, in one batch."),
        ],
        [
            "When reads far outnumber writes, move the work to write time.",
            "Store post ids, not posts, so an edit or a delete happens in one place.",
            "Feed lists are derived data that can be rebuilt from posts and follows.",
        ],
        "নিউজ ফিড দ্রুত দেখায় আপনি যাদের ফলো করেন তাদের নতুন পোস্ট। মূল সিদ্ধান্ত হলো কাজটা কখন হবে: পড়ার সময় ফিড বানানো (<strong>pull</strong>), নাকি লেখার সময়ই প্রত্যেক follower-এর কাছে পোস্ট পৌঁছে দেওয়া (<strong>push</strong>)।",
        [
            ("ফ্যান-আউট অন রিড (pull)", "পড়ার সময় ফলো করা প্রতিটি অ্যাকাউন্টের নতুন পোস্ট এনে ফিড বানানো।"),
            ("ফ্যান-আউট অন রাইট (push)", "লেখার সময়ই প্রতিটি নতুন পোস্ট প্রত্যেক follower-এর জমা রাখা ফিডে যোগ করা।"),
            ("হাইব্রিড (hybrid)", "বেশিরভাগ অ্যাকাউন্টের পোস্ট push করা, আর অল্প কয়েকটা বিশাল অ্যাকাউন্টের পোস্ট পড়ার সময় pull করা।"),
            ("হাইড্রেশন (hydration)", "ফিডের তালিকায় রাখা পোস্ট id-গুলোর পুরো পোস্ট একবারে নিয়ে আসা।"),
        ],
        [
            "লেখার চেয়ে পড়া অনেক বেশি হলে কাজটা লেখার সময়ে সরিয়ে নিন।",
            "পোস্ট নয়, পোস্টের id রাখুন, যাতে edit বা delete এক জায়গাতেই হয়।",
            "ফিডের তালিকা বানানো ডেটা, যা পোস্ট আর ফলো থেকে আবার বানানো যায়।",
        ],
    ),
    "design-chat": basics(
        "A chat system keeps millions of connections open and promises that every message arrives, in order, exactly once. It does this by <strong>storing first, then delivering</strong>, with a registry of who is connected where and sync by cursor for anyone who was away.",
        [
            ("Gateway", "A server that only holds open client connections, such as WebSockets."),
            ("Session registry", "A fast store that records which gateway each user is connected to, kept fresh by heartbeats."),
            ("Sequence number", "A number the server gives each message in a conversation, which fixes their order."),
            ("Sync by cursor", "A returning app asks for everything after the last message it has."),
        ],
        [
            "Write each message to durable storage before telling the sender it was sent.",
            "Device-made message ids let the server drop duplicate retries.",
            "Presence is best-effort; messages are durable and ordered.",
        ],
        "চ্যাট সিস্টেম লাখ লাখ connection খোলা রাখে, আর প্রতিশ্রুতি দেয় প্রতিটি message পৌঁছাবে, ক্রম মেনে, ঠিক একবার। এর উপায়: <strong>আগে জমা, তারপর পৌঁছানো</strong>, কে কোথায় যুক্ত তার একটা registry, আর যে দূরে ছিল তার জন্য cursor দিয়ে sync।",
        [
            ("গেটওয়ে (gateway)", "যে সার্ভার শুধু client-দের খোলা connection, যেমন WebSocket, ধরে রাখে।"),
            ("সেশন রেজিস্ট্রি (session registry)", "দ্রুত একটা store, যা লিখে রাখে কোন ব্যবহারকারী কোন gateway-তে যুক্ত, heartbeat দিয়ে তাজা রাখা।"),
            ("সিকোয়েন্স নম্বর (sequence number)", "কথোপকথনের প্রতিটি message-কে সার্ভারের দেওয়া নম্বর, যা তাদের ক্রম ঠিক করে।"),
            ("কার্সর দিয়ে সিঙ্ক (sync by cursor)", "ফিরে আসা অ্যাপ তার কাছে থাকা শেষ message-এর পরের সবকিছু চায়।"),
        ],
        [
            "Sender-কে “sent” জানানোর আগে প্রতিটি message টেকসই স্টোরেজে লিখুন।",
            "ডিভাইসে বানানো message id দিয়ে সার্ভার retry-র কারণে আসা duplicate বাদ দিতে পারে।",
            "Presence যতটা পারা যায় ততটা; message টেকসই আর ক্রম মেনে চলে।",
        ],
    ),
}
