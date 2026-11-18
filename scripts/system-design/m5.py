from dsl import S, analogy, code, h, note, p, table, ul

SECTIONS = [
    S(
        "redundancy",
        "Redundancy & Failover",
        "Everything fails eventually. Design so that no single failure takes the service down, and practise the failover before you need it.",
        "রিডান্ড্যান্সি আর ফেইলওভার",
        "সবকিছুই একদিন নষ্ট হয়। এমনভাবে ডিজাইন করুন যাতে একটা ব্যর্থতায় পুরো সার্ভিস না থামে, আর দরকার পড়ার আগেই failover অনুশীলন করুন।",
        [
            h("Availability in nines"),
            p("Availability is the share of time a service works. Each extra nine cuts the allowed downtime by ten:"),
            table(
                ["Availability", "Downtime per year", "Per 30 days"],
                ["99%", "3.65 days", "7.2 hours"],
                ["99.9%", "8.8 hours", "43 minutes"],
                ["99.99%", "53 minutes", "4.3 minutes"],
            ),
            p("Google's SRE book treats the target as a product decision. 100% is the wrong goal, and the gap to the target is an error budget that the team can spend on releases and experiments [[sre-risk]]. Parts in a chain multiply: three parts at 99.9% each give about 99.7% together."),
            h("Single points of failure"),
            p("Draw the path of a request and mark every box that exists only once: the load balancer, the database, the network link, the region. Each one is a single point of failure (SPOF). Redundancy means two or more of each, plus a way to switch between them."),
            h("Copies that fail together"),
            p("Two servers in the same rack share power and a network switch, so they can fail together. Cloud providers group data centers into availability zones that do not share points of failure such as generators and cooling equipment, and that are supplied by different power substations [[aws-az]]. Copies in different zones survive the loss of one building. When a zone goes dark, health checks route traffic to the others, and a database standby in another zone takes over."),
            h("How fast, and how much lost?"),
            ul(
                "<strong>Recovery time objective (RTO):</strong> the longest acceptable time from a failure to restored service.",
                "<strong>Recovery point objective (RPO):</strong> the most data, measured in time, that you can afford to lose [[aws-dr]].",
            ),
            p("Synchronous replication gives an RPO near zero, and nightly backups give an RPO of up to a day. A standby that is already running gives a short RTO; restoring from a backup gives a long one."),
            h("Untested failover does not work"),
            p("A failover path that never runs breaks silently: a missing permission, an expired certificate, a script nobody updated. Netflix built Chaos Monkey, which randomly terminates instances in production, so that engineers build services that survive it [[chaos-monkey]]. Start with planned drills in a test environment, then move to small, controlled experiments."),
            h("The bug that is everywhere at once"),
            p("Redundancy protects against hardware failing in one place. It does not help when the same bad release reaches every copy. A canary release sends the new version to a small share of traffic first, compares its errors and latency with the old version, and rolls back if it looks worse [[sre-canary]]."),
            h("Beyond zones: regions"),
            p("A whole region can fail or be cut off. Running in two regions protects against that, but it costs more, and the data must be replicated over a long distance, which brings back the trade-offs of section 16."),
        ],
        [
            p("A hospital cannot close because one generator broke, so it has two, plus batteries, plus a fuel contract. It keeps them in different parts of the building, because one flood should not drown both. And it tests the switch-over every month, because a backup generator that has never run is a hope, not a plan."),
            p("Some failures are not about broken machines. If a bad rule is printed in every ward's handbook at once, spare generators do not help. That is why a hospital tries a new procedure on one ward first."),
            analogy("<strong>Hospital power.</strong> Two generators are redundancy, separate rooms are availability zones, the monthly test is a failover drill, and trying a procedure on one ward is a canary release."),
        ],
        [
            p("Availability মানে সার্ভিস কত শতাংশ সময় চালু থাকে। ৯৯.৯% মানে বছরে প্রায় ৮.৮ ঘণ্টা বন্ধ, ৯৯.৯৯% মানে প্রায় ৫৩ মিনিট। Google-এর SRE বই বলে ১০০% লক্ষ্য রাখা ভুল; লক্ষ্যের বাইরের ফাঁকটুকু error budget, যা রিলিজ আর পরীক্ষায় খরচ করা যায়।"),
            p("রিকোয়েস্টের পথে যে জিনিস মাত্র একটা আছে, যেমন একটা লোড ব্যালান্সার বা একটা ডেটাবেস, সেটাই single point of failure। প্রতিটির অন্তত দুটো রাখুন, আর একটা থেকে অন্যটায় যাওয়ার উপায় রাখুন। একই র‍্যাকের দুটো সার্ভার একসাথে নষ্ট হতে পারে, তাই কপিগুলো আলাদা availability zone-এ রাখুন, যাদের বিদ্যুৎ, ঠান্ডা রাখার ব্যবস্থা আর নেটওয়ার্ক আলাদা।"),
            p("দুটো লক্ষ্য ঠিক করুন: RTO, মানে কত দ্রুত সার্ভিস ফেরাতে হবে, আর RPO, মানে কতটুকু সময়ের ডেটা হারানো চলবে। যে failover কখনো চালানো হয়নি, সেটা দরকারের সময় কাজ করে না; Netflix-এর Chaos Monkey ইচ্ছা করে production-এ সার্ভার বন্ধ করে দুর্বলতা খুঁজে বের করে। আর একই খারাপ রিলিজ সব কপিতে পৌঁছালে redundancy কাজে আসে না, তাই canary release-এ নতুন ভার্সন আগে অল্প কিছু ট্রাফিকে চালিয়ে দেখুন। পুরো region বন্ধ হওয়ার ঝুঁকি থাকলে দুই region-এ চালান, তবে খরচ আর জটিলতা বাড়ে।"),
            analogy("<strong>হাসপাতালের বিদ্যুৎ:</strong> দুটো জেনারেটর হলো redundancy, আলাদা ঘরে রাখা হলো availability zone, প্রতি মাসের পরীক্ষা হলো failover drill, আর একটা ওয়ার্ডে আগে নতুন নিয়ম চালিয়ে দেখা হলো canary release।"),
        ],
    ),
    S(
        "rate-limiting",
        "Rate Limiting",
        "Give every client a fair budget, so that one runaway script cannot take the service down for everyone else.",
        "রেট লিমিটিং",
        "প্রত্যেক client-কে একটা ন্যায্য বাজেট দিন, যাতে একটা লাগামছাড়া script বাকি সবার জন্য সার্ভিস বন্ধ করে দিতে না পারে।",
        [
            h("One script, everyone suffers"),
            p("A customer's buggy script calls your API in a tight loop, 5,000 times a second. The servers spend their capacity on it, and every other user sees timeouts."),
            h("A limiter at the front door"),
            p("A rate limiter counts requests per client, by API key, user or IP address, and rejects the excess before it reaches the expensive parts. A rejected request gets the status code <code>429 Too Many Requests</code> [[rfc6585]], ideally with a <code>Retry-After</code> header that says when to try again [[rfc9110]]."),
            h("The token bucket"),
            p("Each client has a bucket that holds up to B tokens and refills at r tokens per second. Each request takes one token, and a request that finds the bucket empty is rejected. A client can burst up to B requests at once, but its long-run rate is r. Stripe uses a token bucket for its request rate limiter [[stripe-limiters]]."),
            code("python", """import time

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        self.rate, self.capacity = rate, capacity
        self.tokens, self.last = capacity, time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False  # the caller answers 429 with Retry-After"""),
            h("Windows and buckets"),
            ul(
                "<strong>Fixed window:</strong> count requests per calendar minute. It is simple, but a client can send a full minute's budget at 12:00:59 and another one at 12:01:00.",
                "<strong>Sliding window:</strong> weigh the previous window's count by how much of it still overlaps the last minute, and add the current window's count. Cloudflare uses this approximation [[cf-counting]].",
                "<strong>Token bucket:</strong> allows controlled bursts, as above.",
            ),
            h("Many gateways, one budget"),
            p("With twenty gateway servers, each one sees only part of a client's traffic. Keep the counters in a shared store such as Redis, or give each gateway a share of the budget. A little inaccuracy is usually fine: a limit is a guard rail, not an invoice."),
            h("Tenants and overload"),
            p("Limits per user are not enough when one business customer has 10,000 users of its own. Give each customer a quota as well, so one tenant cannot starve the others [[sre-overload]]. When the whole system is overloaded, shed load: reject low-priority work, such as background jobs, before critical requests. Stripe runs load shedders that keep capacity for critical requests [[stripe-limiters]]. Well-behaved clients help by throttling themselves when they see many rejections [[sre-overload]]."),
        ],
        [
            p("A water company gives each household a pipe of a certain width. One house can run every tap at once for a moment, but it cannot drain the town's reservoir, so the neighbours still get water. That is a rate limit."),
            p("A token bucket is like a jar of ride tokens that refills slowly. You can use several at once, but when the jar is empty, you wait. In a drought, the company cuts garden watering before drinking water: that is load shedding."),
            analogy("<strong>Water for a town.</strong> The pipe width is the rate limit, the jar of ride tokens is the token bucket, and cutting garden watering first is load shedding."),
        ],
        [
            p("একজন গ্রাহকের ভুল script সেকেন্ডে ৫,০০০ বার আপনার API কল করছে। সার্ভারের সব ক্ষমতা তাতেই খরচ হচ্ছে, আর বাকি সবাই timeout দেখছে। Rate limiter প্রতিটি client-এর (API key, user বা IP) রিকোয়েস্ট গোনে, আর সীমা ছাড়ালে <code>429 Too Many Requests</code> ফেরত দেয়, আদর্শভাবে সাথে <code>Retry-After</code> দিয়ে জানায় কখন আবার চেষ্টা করা যাবে।"),
            p("সবচেয়ে প্রচলিত পদ্ধতি token bucket। প্রত্যেক client-এর একটা বালতিতে সর্বোচ্চ B-টা token থাকে, আর প্রতি সেকেন্ডে r-টা করে ভরে। প্রতিটি রিকোয়েস্টে একটা token খরচ হয়; বালতি খালি হলে রিকোয়েস্ট বাতিল। তাই অল্প সময়ের জন্য B-টা পর্যন্ত একসাথে পাঠানো যায়, কিন্তু লম্বা সময়ে গড় হার r। Fixed window সহজ, কিন্তু মিনিটের সীমানায় দ্বিগুণ রিকোয়েস্ট ঢুকে যেতে পারে; sliding window এই সমস্যা কমায়।"),
            p("অনেক gateway থাকলে counter Redis-এর মতো শেয়ার করা জায়গায় রাখুন। একজন ব্যবসায়িক গ্রাহকের নিজেরই হাজার হাজার ব্যবহারকারী থাকলে প্রতি গ্রাহকের জন্যও quota দিন। আর পুরো সিস্টেম চাপে পড়লে load shedding করুন: কম গুরুত্বপূর্ণ কাজ আগে বাদ দিন, জরুরি কাজের জন্য জায়গা রাখুন।"),
            analogy("<strong>শহরের পানি সরবরাহ:</strong> পাইপের মাপ হলো rate limit, ধীরে ভরা টোকেনের বয়াম হলো token bucket, আর খরায় আগে বাগানে পানি দেওয়া বন্ধ করা হলো load shedding।"),
        ],
    ),
    S(
        "timeouts-retries",
        "Timeouts & Retries",
        "Calling a struggling service safely: give up in time, retry carefully, and know when to stop calling at all.",
        "টাইমআউট আর রিট্রাই",
        "চাপে থাকা একটা সার্ভিসকে নিরাপদে কল করা: সময়মতো হাল ছাড়ুন, সাবধানে আবার চেষ্টা করুন, আর জানুন কখন কল করাই থামাতে হবে।",
        [
            h("One slow service takes down another"),
            p("Checkout calls a recommendations service that has become slow, and each call now holds a checkout thread for 30 seconds. Soon every thread is waiting, and checkout stops answering, although nothing is wrong with checkout itself. Slowness spreads up the chain."),
            h("Set a timeout, have a fallback"),
            p("Every network call needs a timeout. Choose it from the dependency's measured latency, for example its p99.9, rather than from a round default [[aws-timeouts]]. When a call times out, use a fallback if you have one: a cached answer, a default, or the page without recommendations."),
            h("Retries, and the retry storm"),
            p("Many failures are brief, so one retry often succeeds. But retries add load at the worst moment, and retries at several layers multiply [[aws-timeouts]]. If each of three layers tries three times, one user request can become 27 calls to the service at the bottom. Retry at one layer, cap the attempts, and stop retrying when most calls fail."),
            h("Back off, with jitter"),
            p("Exponential backoff doubles the wait after each failure: 100 ms, 200 ms, 400 ms. If every client backs off on the same schedule, they all retry at the same moments. Random jitter spreads them out. In AWS's simulations, adding \"full jitter\" to the backoff substantially cut both the clients' work and the load on the server [[aws-jitter]]."),
            code("python", """import random, time

def call_with_retries(call, attempts=4, base=0.1, cap=2.0):
    for attempt in range(attempts):
        try:
            return call()
        except TransientError:
            if attempt == attempts - 1:
                raise
            # full jitter: sleep a random time up to the exponential backoff
            time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))"""),
            h("Circuit breaker"),
            p("When a dependency keeps failing, stop calling it for a while. A circuit breaker counts failures, and past a threshold it trips: calls then fail at once without touching the network. After a timeout it lets a trial call through, the half-open state. If the trial succeeds, the breaker closes again; if it fails, it stays open [[fowler-breaker]]."),
            h("Retries must not charge twice"),
            p("A payment can succeed on the server while its response is lost on the way back. Retrying it blindly would charge the customer again. So the client sends an idempotency key, a unique value per operation, with every attempt. The server stores the result under that key and returns the stored result for a repeat. Stripe accepts it in the <code>Idempotency-Key</code> header [[stripe-idem]]."),
            h("Deadlines and bulkheads"),
            ul(
                "<strong>Pass the deadline along.</strong> If the user's request has 2 seconds left, a call three services deep should not wait 10. gRPC propagates a deadline to downstream calls, so the work stops once nobody is waiting for it [[grpc-deadlines]].",
                "<strong>Bulkheads.</strong> Give each dependency its own pool of threads or connections. A slow recommendations service can then use up only its own pool, not the one checkout needs for payments [[azure-bulkhead]].",
            ),
        ],
        [
            p("When you phone a busy office, you do not stay on hold forever: after a few minutes you hang up and try later. If everyone redials at the same second, the lines jam again, so it helps to wait a slightly different, random time. And if the office is clearly closed for the day, you stop calling and try tomorrow."),
            p("When you pay a bill by phone and the line drops, you do not just pay again. You give the reference number from your first attempt, so they can tell you whether it went through."),
            analogy("<strong>Calling a busy office.</strong> Hanging up is a timeout, waiting a random time is jitter, giving up for the day is a circuit breaker, and the reference number is an idempotency key."),
        ],
        [
            p("Checkout একটা ধীর হয়ে যাওয়া recommendation সার্ভিসকে কল করে, আর প্রতিটি কলে checkout-এর একটা thread ৩০ সেকেন্ড আটকে থাকে। একসময় সব thread অপেক্ষায় থাকে, আর checkout-এর নিজের কোনো দোষ না থাকলেও সেটা থেমে যায়। তাই প্রতিটি network কলে timeout দিন, মাপা latency দেখে ঠিক করুন, আর timeout হলে fallback রাখুন, যেমন ক্যাশ করা উত্তর বা recommendation ছাড়াই পেজ।"),
            p("ক্ষণিকের ব্যর্থতায় retry কাজে দেয়, কিন্তু retry সবচেয়ে খারাপ সময়ে লোড বাড়ায়। তিন স্তরের প্রতিটি তিনবার চেষ্টা করলে একটা রিকোয়েস্ট নিচের সার্ভিসে ২৭টি কল হয়ে যায়। তাই exponential backoff দিন, মানে প্রতিবার অপেক্ষা দ্বিগুণ, সাথে jitter, মানে এলোমেলো কিছু সময়, যাতে সবাই একসাথে আবার চেষ্টা না করে। বারবার ব্যর্থ হলে circuit breaker কিছুক্ষণ কল করাই বন্ধ রাখে, তারপর একটা পরীক্ষামূলক কল দিয়ে দেখে।"),
            p("পেমেন্টের মতো কাজে retry যেন দুবার টাকা না কাটে, সেজন্য প্রতিটি চেষ্টায় একই idempotency key পাঠান; সার্ভার আগের ফলাফলটাই ফেরত দেয়। ব্যবহারকারীর রিকোয়েস্টের বাকি সময় (deadline) নিচের কলগুলোতেও পাঠান, যাতে কেউ অপেক্ষা না করলে কাজ থামে। আর প্রতিটি dependency-র জন্য আলাদা thread pool রাখুন (bulkhead), যাতে একটা ধীর সার্ভিস সব thread দখল করতে না পারে।"),
            analogy("<strong>ব্যস্ত অফিসে ফোন:</strong> ফোন রেখে দেওয়া হলো timeout, এলোমেলো সময় পরে আবার ফোন করা jitter, সেদিনের মতো ফোন বন্ধ রাখা circuit breaker, আর আগের রেফারেন্স নম্বর বলা হলো idempotency key।"),
        ],
    ),
    S(
        "observability",
        "Observability",
        "Metrics, logs and traces tell you what is wrong, where and why, fast. Alert on what users feel, then learn from every incident.",
        "অবজার্ভেবিলিটি",
        "Metrics, log আর trace দ্রুত জানায় কী ভুল হয়েছে, কোথায় আর কেন। ব্যবহারকারী যা টের পায় তার ওপর alert দিন, আর প্রতিটি incident থেকে শিখুন।",
        [
            h("\"Checkout is slow.\" Where?"),
            p("A checkout request passes the gateway, the checkout service, payments, inventory, two databases and a cache. A vague complaint gives no hint which one is slow. Observability is the ability to answer such questions from the data the system already emits, without shipping new code."),
            h("Metrics: numbers over time"),
            p("Metrics are cheap counters and histograms recorded over time. For each service, the RED method tracks the request Rate, the Errors and the Duration [[red-method]]. Google's SRE book names four golden signals: latency, traffic, errors and saturation, which means how full the service is [[sre-monitoring]]."),
            h("Alert on what users feel"),
            p("CPU at 90% may be fine; a checkout error rate of 5% is not. Define a service level objective (SLO), such as \"99.9% of checkouts succeed in under 1 second\", and alert when the error budget burns too fast. The burn rate is how quickly the service uses up its allowed failures [[sre-slo-alerts]]."),
            h("Logs and traces"),
            ul(
                "<strong>Logs</strong> tell the story, line by line. Write structured logs, with key-value fields instead of free text, and put a request id in every line so you can find all the lines of one request.",
                "<strong>Traces</strong> follow one request across services. Each step is a span with a start time and a duration, and all the spans of a request share one trace id [[otel-traces]]. Google's Dapper paper showed tracing at the scale of a whole company [[dapper]]. A trace shows at a glance that 900 ms of a 1-second checkout went to inventory, 880 ms of it to a single query.",
            ),
            h("Fix it, then prove it"),
            p("After a fix, the metric that showed the problem must show it gone: p99 back to normal and the error rate down. Until it does, the fix is a guess."),
            h("Incidents and post-mortems"),
            p("At 3 a.m. errors spike after a release. First stop the damage: roll back or switch the feature off. Only then dig for the cause. Afterwards, write a post-mortem: what happened, what the impact was, and what will prevent a repeat. Keep it blameless, so people report what really happened instead of hiding mistakes [[sre-postmortem]]."),
            table(
                ["Signal", "Answers", "Cost"],
                ["Metrics", "Is something wrong, and how much?", "Low"],
                ["Logs", "What exactly happened in this request?", "Medium to high"],
                ["Traces", "Where in the chain did the time go?", "Medium, so traces are often sampled"],
            ),
        ],
        [
            p("A car's dashboard shows a few numbers all the time: speed, fuel and temperature. Those are metrics. A mechanic's notes about every repair are logs. And a GPS track of one journey, showing where you sat in traffic, is a trace."),
            p("A good warning light fires when something affects the drive, like low oil, not every time the engine works hard. After a breakdown, a good garage writes down what failed and how to prevent it, without blaming the driver."),
            analogy("<strong>A car.</strong> The dashboard is metrics, the mechanic's notes are logs, the GPS track of one journey is a trace, and the oil warning light is an SLO alert."),
        ],
        [
            p("একটা checkout রিকোয়েস্ট gateway, checkout সার্ভিস, পেমেন্ট, inventory, দুটো ডেটাবেস আর একটা ক্যাশ পার হয়। “Checkout ধীর” শুনে বোঝা যায় না কোনটা ধীর। Observability মানে সিস্টেম নিজে যে ডেটা দেয়, তা থেকেই এমন প্রশ্নের উত্তর বের করার ক্ষমতা।"),
            p("Metrics হলো সময়ের সাথে সংখ্যা। RED পদ্ধতিতে প্রতিটি সার্ভিসের রিকোয়েস্টের হার (Rate), Error আর সময় (Duration) দেখা হয়। Google-এর SRE বই চারটি golden signal বলে: latency, traffic, error আর saturation। Alert দিন ব্যবহারকারী যা টের পায় তার ওপর, CPU-র ওপর নয়: SLO ঠিক করুন, যেমন “৯৯.৯% checkout ১ সেকেন্ডের মধ্যে সফল”, আর error budget দ্রুত খরচ হলে alert দিন।"),
            p("Log হলো লাইন ধরে ঘটনার বিবরণ; প্রতিটি লাইনে request id রাখুন। Trace একটা রিকোয়েস্টকে সব সার্ভিস জুড়ে অনুসরণ করে: প্রতিটি ধাপ একটা span, আর সবগুলোর একই trace id। এতে এক নজরে দেখা যায় সময় কোথায় গেল। সমস্যা হলে আগে ক্ষতি থামান, যেমন rollback, তারপর কারণ খুঁজুন। পরে দোষারোপ ছাড়া (blameless) post-mortem লিখুন: কী ঘটেছিল, কী প্রভাব পড়েছিল, আর আবার যেন না ঘটে সেজন্য কী করা হবে।"),
            analogy("<strong>গাড়ি:</strong> ড্যাশবোর্ড হলো metrics, মিস্ত্রির নোট হলো log, একটা যাত্রার GPS ট্র্যাক হলো trace, আর তেল কমার সতর্ক বাতি হলো SLO alert।"),
        ],
    ),
]
