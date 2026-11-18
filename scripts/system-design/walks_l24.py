"""Walk-through of lesson 24, Redundancy & Failover.

Example numbers (mine, checked by script): one part at 99.9% is down 8.76 h a year; three in a chain = 99.7003% = 26.25 h a year.
A pair that fails independently: 0.001 x 0.001 = 1e-6 -> 99.9999%, 31.5 s a year. Three such pairs = 99.9997%, 1.58 min a year.
All copies in one building that is up 99.9% of the time: the stack is at most 99.9% = 8.76 h a year.
Two zones: the pairs (3e-6) plus both zones down together (1e-6) = 4e-6 -> 99.9996%, 2.1 min a year.
Failover: health check every 5 s, three misses = 15 s, promote about 15 s -> about 30 s. Async follower about 1 s behind: RPO about 1 s.
A bad release with a 5% error rate everywhere: 95% available. A canary at 1% of traffic: 1% x 5% = 0.05% = 1 request in 2,000.
Two far-apart regions: about 90 ms round trip (same figure as lesson 17).
"""
from walkkit import node, sh, ln, st, walk

NODES = [
    node("user", "user", ("Users", "ব্যবহারকারী"), 85, 170),
    node("lb", "balancer", ("Load balancer", "Load balancer"), 290, 90),
    node("lb2", "balancer", ("Load balancer", "Load balancer"), 290, 250),
    node("app", "server", ("App server", "App server"), 480, 90),
    node("app2", "server", ("App server", "App server"), 480, 250),
    node("db", "database", ("Database", "Database"), 665, 90),
    node("db2", "database", ("Database", "Database"), 665, 250),
    node("t-write", "database", ("Last copied write", "শেষ copy-করা write"), 130, 170),
    node("t-fail", "server", ("Failure", "ব্যর্থতা"), 390, 170),
    node("t-back", "service", ("Service back", "সার্ভিস ফেরা"), 650, 170),
    node("drill", "shield", ("Chaos drill", "Chaos drill"), 680, 90),
    node("cmp", "chart", ("Error rate", "Error rate"), 665, 170),
    node("dns", "dns", ("Global routing", "Global routing"), 300, 170),
    node("r1", "server", ("Region 1", "Region 1"), 540, 80),
    node("r2", "server", ("Region 2", "Region 2"), 540, 260),
]
METRICS = [("Availability", "Availability"), ("Downtime", "Downtime"), ("Single points of failure", "Single point of failure"), ("Survives", "টিকে থাকে")]
CAPTION = ("Example numbers: every part is up 99.9% of the time, and failures are independent unless a step says otherwise.",
           "উদাহরণের সংখ্যা: প্রতিটি অংশ ৯৯.৯% সময় চালু থাকে, আর কোনো ধাপ অন্যরকম না বললে ব্যর্থতাগুলো স্বতন্ত্র।")

NOTHING = ("nothing", "কিছুই না")
ONE_BOX = ("one box", "একটা box")
BUILDING = ("a building", "একটা ভবন")
YEAR_26H = ("26 h/yr", "২৬ ঘণ্টা/বছর")
ACTIVE, STANDBY = ("active", "সক্রিয়"), ("standby", "অপেক্ষমাণ")
SHARES = ("shares traffic", "traffic ভাগ")
LEADER, FOLLOWER = ("leader", "leader"), ("follower", "follower")
ONE_COPY = ("one copy", "একটাই কপি")
SAME_BLDG = ("same building", "একই ভবন")
ZA, ZB = ("zone A", "zone A"), ("zone B", "zone B")

# step 1 and 2: a single chain on one row
ROW = dict(y=170)


def chain_links(state, flow=True):
    f = (lambda a, b: ln(a, b, "to", 1200, state)) if flow else (lambda a, b: ln(a, b, None, None, state))
    return [f("user", "lb"), f("lb", "app"), f("app", "db")]


def pairs_links(state="hot"):
    return [ln("user", "lb", "to", 1100, state), ln("lb", "lb2", None, None, "dim"),
            ln("lb", "app", "to", 1100, state), ln("lb", "app2", "to", 1300, state),
            ln("app", "db", "to", 1100, state), ln("app2", "db", "to", 1300, state),
            ln("db", "db2", "to", 1500, state)]


STEPS = [
    st(("Nines", "Nines"),
       ("How available is one of everything?", "সবকিছু একটা করে থাকলে কতটা available?"),
       [("Take a plain stack: one load balancer, one app server, one database. Each part is up 99.9% of the time, which sounds excellent.",
         "একটা সাধারণ stack ধরুন: একটা load balancer, একটা app server, একটা database। প্রতিটি অংশ ৯৯.৯% সময় চালু থাকে, শুনতে চমৎকার।"),
        ("Availability is the share of time a service works. A single part at 99.9% is down about 8.8 hours a year. But a request needs all three, so the availabilities multiply: 0.999 × 0.999 × 0.999 ≈ 0.997. The stack is 99.7% available, which is about 26 hours of downtime a year.",
         "Availability হলো একটা সার্ভিস কত শতাংশ সময় কাজ করে। ৯৯.৯% চালু একটা অংশ বছরে প্রায় ৮.৮ ঘণ্টা বন্ধ থাকে। কিন্তু একটা request-এর তিনটি অংশই লাগে, তাই availability গুণ হয়: ০.৯৯৯ × ০.৯৯৯ × ০.৯৯৯ ≈ ০.৯৯৭। Stack-টি ৯৯.৭% available, মানে বছরে প্রায় ২৬ ঘণ্টা downtime।")],
       [sh("user"), sh("lb", "hot", ("99.9% up", "৯৯.৯% চালু"), **ROW), sh("app", "hot", ("99.9% up", "৯৯.৯% চালু"), **ROW), sh("db", "hot", ("99.9% up", "৯৯.৯% চালু"), **ROW)],
       [ln("user", "lb", "to", 1100, "hot"), ln("lb", "app", "to", 1100, "hot"), ln("app", "db", "to", 1100, "hot")],
       ["99.7%", YEAR_26H, None, NOTHING],
       note=("insight",
             "A chain is less available than its weakest part. Every part you add to the request path takes something off the total.",
             "একটা chain তার সবচেয়ে দুর্বল অংশের চেয়েও কম available। Request-এর পথে প্রতিটি নতুন অংশ মোট availability থেকে কিছু কেটে নেয়।")),

    st(("SPOFs", "SPOF"),
       ("Every box is a single point of failure", "প্রতিটি box একটা single point of failure"),
       [("A single point of failure (SPOF) is any part whose failure alone takes the whole system down. Trace one request and mark every box that exists only once: here, that is all three.",
         "Single point of failure (SPOF) হলো এমন যেকোনো অংশ, যার একার ব্যর্থতায় পুরো সিস্টেম বন্ধ হয়ে যায়। একটা request-এর পথ ধরে এগোন আর যে box শুধু একটাই আছে তা চিহ্নিত করুন: এখানে তিনটিই।"),
        ("Look wider, too. The network link, the data center and the region also exist once. Redundancy means two or more of each, plus a way to switch between them.",
         "আরও বড় করে দেখুন। Network link, data center আর region-ও আছে একটাই। Redundancy মানে প্রতিটির দুই বা তার বেশি, সাথে তাদের মধ্যে বদলে নেওয়ার একটা উপায়।")],
       [sh("user"), sh("lb", "warn", ONE_COPY, **ROW), sh("app", "warn", ONE_COPY, **ROW), sh("db", "warn", ONE_COPY, **ROW)],
       [ln("user", "lb", "to", 1100, "warn"), ln("lb", "app", "to", 1100, "warn"), ln("app", "db", "to", 1100, "warn")],
       ["99.7%", YEAR_26H, "3", NOTHING],
       note=("warn",
             "If any one of these boxes stops, every request fails, and nothing else in the picture can step in.",
             "এই box-গুলোর যেকোনো একটা থেমে গেলে প্রতিটি request ব্যর্থ হয়, আর ছবির আর কিছুই তার জায়গা নিতে পারে না।"),
       changes=[("-", "Load balancer: one copy", "Load balancer: একটাই কপি"),
                ("-", "App server: one copy", "App server: একটাই কপি"),
                ("-", "Database: one copy", "Database: একটাই কপি")]),

    st(("Two of each", "দুটো করে"),
       ("Redundancy: two of everything", "Redundancy: সবকিছু দুটো করে"),
       [("Add a spare for every part. The load balancer becomes an active–passive pair, two app servers share the traffic, and the database gets a follower ready to take over.",
         "প্রতিটি অংশের জন্য একটা spare যোগ করুন। Load balancer হয় একটা active–passive জোড়া, দুটো app server traffic ভাগ করে নেয়, আর database পায় একটা follower, যে দায়িত্ব নিতে তৈরি।"),
        ("If each part fails independently of its twin, a pair is down only when both are down: 0.001 × 0.001, one time in a million. That is 99.9999%, about 32 seconds a year. Chain three such pairs and you get about 99.9997%, or 1.6 minutes of downtime a year. That is the paper number, and the next step shows what “independently” is hiding.",
         "প্রতিটি অংশ যদি তার জুড়ির থেকে স্বতন্ত্রভাবে ব্যর্থ হয়, তাহলে একটা জোড়া বন্ধ থাকে শুধু যখন দুটোই বন্ধ: ০.০০১ × ০.০০১, দশ লাখে একবার। সেটা ৯৯.৯৯৯৯%, বছরে প্রায় ৩২ সেকেন্ড। এমন তিনটি জোড়া chain করলে পাওয়া যায় প্রায় ৯৯.৯৯৯৭%, মানে বছরে ১.৬ মিনিট downtime। এটা কাগজের হিসাব, আর পরের ধাপ দেখায় “স্বতন্ত্রভাবে” কথাটা কী লুকিয়ে রাখছে।")],
       [sh("user"), sh("lb", "hot", ACTIVE), sh("lb2", "dim", STANDBY), sh("app", "hot", SHARES), sh("app2", "hot", SHARES), sh("db", "hot", LEADER), sh("db2", "hot", FOLLOWER)],
       pairs_links(),
       ["99.9997%", ("1.6 min/yr", "১.৬ মিনিট/বছর"), "0", ONE_BOX],
       note=("tip",
             "Redundancy needs a switch-over path as well as a spare: a health check to notice the failure, and a rule for who takes over.",
             "Redundancy-তে spare-এর পাশাপাশি দরকার একটা বদলে নেওয়ার পথ: ব্যর্থতা ধরার জন্য health check আর কে দায়িত্ব নেবে তার নিয়ম।"),
       changes=[("+", "A standby load balancer", "একটা standby load balancer"),
                ("+", "A second app server", "দ্বিতীয় একটা app server"),
                ("+", "A database follower", "একটা database follower"),
                ("~", "On paper: 99.7% → 99.9997%", "কাগজে: ৯৯.৭% → ৯৯.৯৯৯৭%")]),

    st(("One building", "একই বিল্ডিং"),
       ("Copies that fail together", "যে copy একসাথে ব্যর্থ হয়"),
       [("All those copies sit in one data center. A power outage, a flood, a fibre cut or a cooling failure takes out the whole building, and every “redundant” copy goes with it.",
         "সেই সব copy আছে একই data center-এ। Power outage, বন্যা, fibre কাটা বা cooling ব্যর্থতা পুরো ভবন বন্ধ করে দেয়, আর প্রতিটি “redundant” copy তার সাথে যায়।"),
        ("The 99.9999% assumed independent failures. Two servers in one rack share power and a network switch, so they are not independent. If the building is up 99.9% of the time, the whole stack is at most 99.9%: about 8.8 hours a year, however many copies it holds.",
         "৯৯.৯৯৯৯%-এর হিসাবে ধরা হয়েছিল ব্যর্থতাগুলো স্বতন্ত্র। একই rack-এর দুটো server একই power আর network switch ভাগ করে, তাই তারা স্বতন্ত্র নয়। ভবন ৯৯.৯% সময় চালু থাকলে পুরো stack-ও সর্বোচ্চ ৯৯.৯%: বছরে প্রায় ৮.৮ ঘণ্টা বন্ধ, যত copy-ই থাকুক।")],
       [sh("user"), sh("lb", "warn", SAME_BLDG), sh("lb2", "warn", SAME_BLDG), sh("app", "warn", SAME_BLDG), sh("app2", "warn", SAME_BLDG), sh("db", "warn", SAME_BLDG), sh("db2", "warn", SAME_BLDG)],
       pairs_links("warn"),
       [("≤ 99.9%", "≤ ৯৯.৯%"), ("8.8 h/yr", "৮.৮ ঘণ্টা/বছর"), "1", ONE_BOX],
       note=("warn",
             "Copies only help if they do not share a cause of failure. Power, cooling and the network are shared causes.",
             "Copy তখনই কাজে লাগে, যখন তারা ব্যর্থতার কারণ ভাগ করে না। Power, cooling আর network ভাগ-করা কারণ।"),
       changes=[("-", "Every copy sits in one building", "প্রতিটি copy একই ভবনে"),
                ("-", "One outage takes out all of them", "একটা outage সবগুলোকে নিয়ে যায়"),
                ("~", "Availability is capped at the building's 99.9%", "Availability আটকে যায় ভবনের ৯৯.৯%-এ")]),

    st(("Zones", "Zone"),
       ("Spread across availability zones", "Availability zone জুড়ে ছড়িয়ে দিন"),
       [("Cloud providers split a region into availability zones: separate data centers that do not share generators or cooling equipment and are supplied by different power substations. Put one of each part in zone A and its twin in zone B.",
         "Cloud provider একটা region-কে ভাগ করে availability zone-এ: আলাদা data center, যারা generator বা cooling equipment ভাগ করে না এবং ভিন্ন power substation থেকে বিদ্যুৎ পায়। প্রতিটি অংশের একটা কপি zone A-তে রাখুন আর তার জুড়ি zone B-তে।"),
        ("Now losing a building takes out half the copies, not all of them. If the zones fail independently, both are down together about one time in a million, which brings the stack to about 99.9996%: roughly 2 minutes a year.",
         "এখন একটা ভবন হারালে অর্ধেক copy যায়, সব নয়। Zone দুটো স্বতন্ত্রভাবে ব্যর্থ হলে দুটো একসাথে বন্ধ থাকে প্রায় দশ লাখে একবার, ফলে stack দাঁড়ায় প্রায় ৯৯.৯৯৯৬%-এ: বছরে মোটামুটি ২ মিনিট।")],
       [sh("user"), sh("lb", "hot", ZA), sh("lb2", "hot", ZB), sh("app", "hot", ZA), sh("app2", "hot", ZB), sh("db", "hot", ZA), sh("db2", "hot", ZB)],
       pairs_links(),
       ["99.9996%", ("2.1 min/yr", "২.১ মিনিট/বছর"), "0", BUILDING],
       note=("tip",
             "Spread the copies across zones, and keep the follower in a different zone from the leader.",
             "Copy-গুলো zone জুড়ে ছড়ান, আর follower রাখুন leader-এর থেকে ভিন্ন zone-এ।"),
       changes=[("+", "Zone A: balancer, app server, database leader", "Zone A: balancer, app server, database leader"),
                ("+", "Zone B: standby balancer, app server, follower", "Zone B: standby balancer, app server, follower"),
                ("~", "A building failure takes out half, not all", "একটা ভবনের ব্যর্থতায় যায় অর্ধেক, সব নয়")]),

    st(("Zone fails", "Zone বন্ধ"),
       ("Zone A goes dark: failover", "Zone A অন্ধকার: failover"),
       [("Zone A loses power. Health checks to its servers fail, the standby load balancer in zone B takes over and sends traffic only to zone B, and the follower in zone B is promoted to leader.",
         "Zone A-তে বিদ্যুৎ চলে যায়। তার server-গুলোর health check ব্যর্থ হয়, zone B-র standby load balancer দায়িত্ব নিয়ে শুধু zone B-তে traffic পাঠায়, আর zone B-র follower-কে leader বানানো হয়।"),
        ("Users see errors only while this happens. Say health checks run every 5 seconds and three misses in a row mean “down”: 15 seconds to notice, about 15 more to promote the follower. That is about 30 seconds of errors, once, instead of a long outage.",
         "এটা ঘটার সময়টুকুতেই শুধু ব্যবহারকারীরা error দেখে। ধরুন health check চলে প্রতি ৫ সেকেন্ডে আর পরপর তিনবার ব্যর্থ মানে “বন্ধ”: বুঝতে ১৫ সেকেন্ড, follower-কে promote করতে আরও প্রায় ১৫। মোট প্রায় ৩০ সেকেন্ডের error, একবার, দীর্ঘ outage-এর বদলে।")],
       [sh("user"), sh("lb", "warn", ("dark", "অন্ধকার")), sh("app", "warn", ("dark", "অন্ধকার")), sh("db", "warn", ("dark", "অন্ধকার")),
        sh("lb2", "hot", ("takes over", "দায়িত্ব নেয়")), sh("app2", "hot", ("takes all", "সবটা সামলায়")), sh("db2", "hot", ("new leader", "নতুন leader"))],
       [ln("user", "lb", None, None, "warn"), ln("user", "lb2", "to", 1200, "hot"), ln("lb2", "app2", "to", 1100, "hot"), ln("app2", "db2", "to", 1100, "hot")],
       ["99.9996%", ("30 s/event", "৩০ s/ঘটনা"), "0", BUILDING],
       note=("insight",
             "Failover is not instant. The gap between the failure and the switch is exactly the downtime you still have.",
             "Failover তাৎক্ষণিক নয়। ব্যর্থতা আর বদলের মধ্যবর্তী ফাঁকটুকুই আপনার তখনও থাকা downtime।"),
       changes=[("-", "Zone A loses power", "Zone A-র বিদ্যুৎ যায়"),
                ("~", "Health checks fail, and traffic moves to zone B", "Health check ব্যর্থ হয়, traffic চলে যায় zone B-তে"),
                ("~", "The follower is promoted to leader", "Follower পদোন্নত হয় leader-এ"),
                ("~", "About 30 seconds of errors in all", "মোট প্রায় ৩০ সেকেন্ডের error")]),

    st(("RTO & RPO", "RTO ও RPO"),
       ("How fast, and how much lost?", "কত দ্রুত, আর কতটা হারাল?"),
       [("Two numbers describe a failover. The recovery time objective (RTO) is the longest acceptable time from a failure to restored service. The recovery point objective (RPO) is the most data, measured in time, that you can afford to lose.",
         "দুটি সংখ্যা একটা failover-কে বর্ণনা করে। Recovery time objective (RTO) হলো ব্যর্থতা থেকে সার্ভিস ফিরে আসা পর্যন্ত সবচেয়ে বেশি যে সময় মেনে নেওয়া যায়। Recovery point objective (RPO) হলো সময়ের হিসাবে সবচেয়ে বেশি যে পরিমাণ ডেটা হারানো মেনে নেওয়া যায়।"),
        ("Here the follower is a running standby, so the RTO is about 30 seconds. It copies asynchronously, so it may be a second behind: the RPO is about 1 second. Synchronous replication brings the RPO near zero but makes writes wait for the copy. Restoring from a nightly backup would mean an RTO of hours and an RPO of up to a day.",
         "এখানে follower একটা চালু standby, তাই RTO প্রায় ৩০ সেকেন্ড। সে asynchronous-ভাবে copy করে, তাই এক সেকেন্ড পিছিয়ে থাকতে পারে: RPO প্রায় ১ সেকেন্ড। Synchronous replication RPO প্রায় শূন্যে নামায়, কিন্তু write-কে copy-র জন্য অপেক্ষা করায়। প্রতি রাতের backup থেকে ফেরালে RTO হবে কয়েক ঘণ্টা আর RPO এক দিন পর্যন্ত।")],
       [sh("t-write", "hot", ("later writes lost", "পরের write হারায়")), sh("t-fail", "warn"), sh("t-back", "hot", ("on the follower", "follower-এ"))],
       [ln("t-write", "t-fail", "to", 1300, "warn", ("RPO 1 s", "RPO ১ s")), ln("t-fail", "t-back", "to", 1500, "hot", ("RTO 30 s", "RTO ৩০ s"))],
       ["99.9996%", ("30 s/event", "৩০ s/ঘটনা"), "0", BUILDING],
       note=("tip",
             "Choose the RTO and RPO from what the business can bear, then pick the cheapest design that meets them.",
             "ব্যবসা কী সইতে পারে তা থেকে RTO আর RPO ঠিক করুন, তারপর যে সবচেয়ে সস্তা নকশা তা পূরণ করে সেটা বাছুন।"),
       changes=[("~", "Asynchronous follower: RPO about 1 s, RTO about 30 s", "Asynchronous follower: RPO প্রায় ১ s, RTO প্রায় ৩০ s"),
                ("~", "Synchronous replication: RPO near zero, slower writes", "Synchronous replication: RPO প্রায় শূন্য, ধীর write"),
                ("~", "Nightly backup: RPO up to a day, RTO hours", "প্রতি রাতের backup: RPO এক দিন পর্যন্ত, RTO কয়েক ঘণ্টা")]),

    st(("Chaos", "Chaos"),
       ("Untested failover does not work", "যে failover পরীক্ষা হয়নি তা কাজ করে না"),
       [("A failover path that never runs quietly rots: a permission goes missing, a certificate expires, a spare is too small, a script has a typo. You find out during the real outage.",
         "যে failover পথ কখনো চলে না, সেটা নীরবে পচে যায়: একটা permission হারায়, একটা certificate-এর মেয়াদ ফুরায়, একটা spare ছোট পড়ে, একটা script-এ বানান ভুল থাকে। আপনি জানতে পারেন আসল outage-এর সময়।"),
        ("Netflix built Chaos Monkey, which randomly terminates instances in production, so that engineers build services that survive it. Start with planned drills in a test environment, then move to small, controlled experiments.",
         "Netflix বানিয়েছে Chaos Monkey, যা production-এ এলোমেলোভাবে instance বন্ধ করে দেয়, যাতে প্রকৌশলীরা এমন সার্ভিস বানান, যা instance বন্ধ হয়ে গেলেও টিকে থাকে। শুরু করুন test environment-এ পরিকল্পিত drill দিয়ে, তারপর যান ছোট, নিয়ন্ত্রিত পরীক্ষায়।")],
       [sh("user"), sh("lb", "hot", ("reroutes", "পথ বদলায়"), y=170), sh("app", "warn", ("killed", "বন্ধ করা")), sh("app2", "hot", ("takes all", "সবটা সামলায়")), sh("db", "hot", ("fine", "ঠিক আছে"), y=250), sh("drill", "warn", ("on purpose", "ইচ্ছে করে"))],
       [ln("user", "lb", "to", 1100, "hot"), ln("lb", "app", None, None, "warn"), ln("lb", "app2", "to", 1200, "hot"), ln("app2", "db", "to", 1200, "hot"), ln("drill", "app", "to", 1000, "warn")],
       ["99.9996%", ("30 s/event", "৩০ s/ঘটনা"), "0", BUILDING],
       note=("tip",
             "Kill one app server on purpose and watch what happens. If you are surprised, you found a bug on a quiet afternoon instead of during an outage.",
             "ইচ্ছে করে একটা app server বন্ধ করে দেখুন কী হয়। অবাক হলে আপনি একটা bug পেলেন শান্ত এক বিকেলে, outage-এর সময় নয়।"),
       changes=[("+", "Planned drills in a test environment", "Test environment-এ পরিকল্পিত drill"),
                ("+", "Then small, controlled experiments", "তারপর ছোট, নিয়ন্ত্রিত পরীক্ষা")]),

    st(("Bad deploy", "খারাপ deploy"),
       ("Case: the bug that is everywhere at once", "ঘটনা: যে bug একসাথে সর্বত্র"),
       [("A new release, <code>v2.4</code>, has a bug, and it goes out to every app server in both zones at the same moment. Five requests in a hundred hit the bug and fail, on every copy.",
         "নতুন release <code>v2.4</code>-এ একটা bug আছে, আর সেটা একই মুহূর্তে দুই zone-এর প্রতিটি app server-এ পৌঁছে যায়। প্রতি একশো request-এ পাঁচটি bug-এ পড়ে ব্যর্থ হয়, প্রতিটি copy-তেই।"),
        ("Redundancy does not help: the copies are identical, so they fail together. A 5% error rate means 95% availability for as long as it lasts, far below the 99.7% of step 1. Redundancy protects against hardware failing in one place, not against the same mistake reaching every copy.",
         "Redundancy এখানে কাজে আসে না: copy-গুলো একই, তাই তারা একসাথে ব্যর্থ হয়। ৫% error মানে যতক্ষণ থাকে ততক্ষণ ৯৫% availability, ধাপ ১-এর ৯৯.৭%-এর চেয়ে অনেক নিচে। Redundancy রক্ষা করে এক জায়গায় hardware ব্যর্থ হওয়া থেকে, প্রতিটি copy-তে একই ভুল পৌঁছানো থেকে নয়।")],
       [sh("user", "warn", ("5% errors", "৫% error")), sh("lb", "hot", y=170), sh("app", "warn", ("v2.4 bug", "v২.৪ bug")), sh("app2", "warn", ("v2.4 bug", "v২.৪ bug")), sh("db", "hot", ("fine", "ঠিক আছে"), y=170)],
       [ln("user", "lb", "both", 1100, "warn"), ln("lb", "app", "to", 1200, "warn"), ln("lb", "app2", "to", 1200, "warn"), ln("app", "db", None, None, "dim"), ln("app2", "db", None, None, "dim")],
       ["95%", ("until rollback", "rollback পর্যন্ত"), "0", ("hardware only", "শুধু hardware")],
       note=("warn",
             "Identical copies share every software bug. That is a shared cause of failure too.",
             "একই রকম copy-গুলো সফটওয়্যারের প্রতিটি bug ভাগ করে। এটাও ব্যর্থতার একটা ভাগ-করা কারণ।"),
       changes=[("-", "<code>v2.4</code> reaches every app server at once", "<code>v2.4</code> একসাথে প্রতিটি app server-এ পৌঁছায়"),
                ("-", "5% of all requests fail", "সব request-এর ৫% ব্যর্থ হয়"),
                ("-", "Availability: about 95% until the rollback", "Availability: rollback পর্যন্ত প্রায় ৯৫%")]),

    st(("Canary", "Canary"),
       ("Canary releases", "Canary release: আগে অল্প traffic-এ"),
       [("Roll out in stages. First a canary: 1% of traffic goes to <code>v2.4</code> while 99% stays on <code>v2.3</code>. Compare the canary's error rate and latency with the old version's for a while.",
         "ধাপে ধাপে ছাড়ুন। প্রথমে একটা canary: traffic-এর ১% যায় <code>v2.4</code>-এ, ৯৯% থাকে <code>v2.3</code>-এ। কিছুক্ষণ canary-র error rate আর latency পুরোনো সংস্করণের সাথে তুলনা করুন।"),
        ("Here the canary shows 5% errors against 0.1%, so you roll back. Only 1% of users saw the bug, and about 1 request in 2,000 failed, instead of 1 in 20.",
         "এখানে canary দেখায় ৫% error, পুরোনোটার ০.১%-এর তুলনায়, তাই আপনি rollback করেন। মাত্র ১% ব্যবহারকারী bug দেখেছে, আর প্রতি ২০টিতে ১টির বদলে প্রতি ২,০০০টিতে প্রায় ১টি request ব্যর্থ হয়েছে।")],
       [sh("user"), sh("lb", "hot", x=270, y=170), sh("app", "hot", ("v2.3", "v২.৩"), x=500), sh("app2", "warn", ("v2.4 canary", "v২.৪ canary"), x=500), sh("cmp", "warn", ("5% vs 0.1%", "৫% বনাম ০.১%"))],
       [ln("user", "lb", "to", 1100, "hot"), ln("lb", "app", "to", 1100, "hot", ("99%", "৯৯%")), ln("lb", "app2", "to", 2400, "warn", ("1%", "১%")), ln("app", "cmp", "to", 1200, "hot"), ln("app2", "cmp", "to", 1200, "warn")],
       ["99.95%", None, "0", ("a bad release", "খারাপ release")],
       note=("tip",
             "Automate the comparison: if the canary's errors or latency are worse than the old version's, roll back without waiting for a person.",
             "তুলনাটা স্বয়ংক্রিয় করুন: canary-র error বা latency পুরোনোটার চেয়ে খারাপ হলে কোনো মানুষের জন্য অপেক্ষা না করে rollback করুন।"),
       changes=[("+", "1% of traffic goes to <code>v2.4</code> first", "প্রথমে traffic-এর ১% যায় <code>v2.4</code>-এ"),
                ("~", "Errors and latency are compared with <code>v2.3</code>", "Error আর latency তুলনা করা হয় <code>v2.3</code>-এর সাথে"),
                ("~", "Roll back: 1 request in 2,000 failed, not 1 in 20", "Rollback: প্রতি ২০টিতে ১টি নয়, প্রতি ২,০০০টিতে ১টি request ব্যর্থ")]),

    st(("Regions", "Region"),
       ("Beyond zones: multiple regions", "Zone-এর বাইরে: একাধিক region"),
       [("Zones protect against a building failing. A whole region can still fail or be cut off, for example by a regional network failure or a problem in the cloud's control plane.",
         "Zone রক্ষা করে একটা ভবন ব্যর্থ হওয়া থেকে। তবু একটা গোটা region ব্যর্থ বা বিচ্ছিন্ন হতে পারে, যেমন কোনো আঞ্চলিক network ব্যর্থতা বা cloud-এর control plane-এর সমস্যায়।"),
        ("Running in two regions protects against that, but it costs more, and the data must be replicated over a long distance: about 90 ms round trip between far-apart regions. That brings back the trade-offs of the CAP lesson: wait for the far copy and every write is slower, or do not wait and risk losing the latest writes.",
         "দুটো region-এ চালালে তা থেকে রক্ষা মেলে, কিন্তু খরচ বেশি, আর ডেটা অনেক দূরত্বে replicate করতে হয়: দূরের দুটো region-এর মধ্যে round trip প্রায় ৯০ ms। এতে ফিরে আসে CAP পাঠের লাভ-ক্ষতি: দূরের copy-র জন্য অপেক্ষা করলে প্রতিটি write ধীর হয়, অপেক্ষা না করলে সর্বশেষ write হারানোর ঝুঁকি।")],
       [sh("user"), sh("dns", "hot", ("sends users", "ব্যবহারকারী পাঠায়")), sh("r1", "hot", ("2 zones", "২টি zone")), sh("r2", "hot", ("2 zones", "২টি zone"))],
       [ln("user", "dns", "to", 1100, "hot"), ln("dns", "r1", "to", 1200, "hot"), ln("dns", "r2", "to", 1200, "hot"), ln("r1", "r2", "both", 2400, "hot", ("90 ms apart", "৯০ ms দূরে"))],
       ["99.9996%", ("30 s/event", "৩০ s/ঘটনা"), "0", ("a region", "একটা region")],
       note=("insight",
             "Each step up, from zone to region, costs more and adds trade-offs. Pick the level that matches what an outage would cost you.",
             "প্রতিটি ধাপ উপরে, zone থেকে region, খরচ বাড়ে আর লাভ-ক্ষতি যোগ হয়। বেছে নিন সেই স্তর, যা একটা outage-এ আপনার খরচের সাথে মেলে।"),
       changes=[("+", "A second region", "দ্বিতীয় একটা region"),
                ("~", "Data replicated over a long distance: about 90 ms away", "ডেটা বহু দূরত্বে replicate হয়: প্রায় ৯০ ms দূরে"),
                ("~", "Survives the loss of a whole region", "একটা গোটা region হারালেও টিকে থাকে")]),

    st(("Recap", "সারাংশ"),
       ("Remove single points, and keep failures apart", "Single point সরান, আর ব্যর্থতাগুলো আলাদা রাখুন"),
       [("Redundancy is only as good as the independence of the copies and the practice of the switch-over.",
         "Redundancy ততটাই ভালো, যতটা copy-গুলো স্বতন্ত্র আর যতটা বদলে নেওয়ার অনুশীলন হয়েছে।")],
       [sh("user"), sh("lb", "hot", ZA), sh("lb2", "hot", ZB), sh("app", "hot", ZA), sh("app2", "hot", ZB), sh("db", "hot", ZA), sh("db2", "hot", ZB)],
       pairs_links(),
       [None, None, None, None],
       points=[("Components in a chain <strong>multiply</strong> their availability: three at 99.9% give about 99.7%.",
                "Chain-এর অংশগুলোর availability <strong>গুণ</strong> হয়: ৯৯.৯%-এর তিনটি মিলে প্রায় ৯৯.৭%।"),
               ("Remove <strong>single points of failure</strong> with redundant copies.",
                "Redundant copy দিয়ে <strong>single point of failure</strong> সরান।"),
               ("Copies must fail <strong>independently</strong>: spread them across availability zones.",
                "Copy-গুলোকে ব্যর্থ হতে হবে <strong>স্বতন্ত্রভাবে</strong>: তাদের availability zone জুড়ে ছড়ান।"),
               ("<strong>RTO</strong> is how long you are down. <strong>RPO</strong> is how much recent data you lose.",
                "<strong>RTO</strong> মানে কতক্ষণ বন্ধ থাকবেন। <strong>RPO</strong> মানে সাম্প্রতিক কতটা ডেটা হারাবেন।"),
               ("<strong>Practise</strong> failover. A path that never runs is probably broken.",
                "Failover <strong>অনুশীলন</strong> করুন। যে পথ কখনো চলে না সেটা সম্ভবত ভাঙা।"),
               ("Roll out with <strong>canaries</strong>, and add <strong>regions</strong> when a regional outage would cost too much.",
                "<strong>Canary</strong> দিয়ে ছাড়ুন, আর region-ব্যাপী outage-এর খরচ বেশি হলে <strong>region</strong> বাড়ান।")]),
]

WALKS = {"redundancy": walk(760, 340, NODES, METRICS, CAPTION, STEPS)}
