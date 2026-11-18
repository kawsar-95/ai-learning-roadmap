"""Step-by-step walk-throughs for module 01, Foundations.

Each walk-through follows the steps of the course lesson (same order and step
names) with its own words, numbers and diagram. The numbers are worked
examples that match the section text; the section text carries the citations.
"""


def bi(en, bn):
    return {"en": en, "bn": bn}


def node(id, kind, en, bn, x, y):
    return {"id": id, "kind": kind, "label": bi(en, bn), "x": x, "y": y}


def show(id, state=None, sub=None, badge=None, x=None, y=None):
    s = {"id": id}
    if state:
        s["state"] = state
    if sub:
        s["sub"] = bi(*sub)
    if badge:
        s["badge"] = badge
    if x is not None:
        s["x"] = x
    if y is not None:
        s["y"] = y
    return s


def link(a, b, flow=None, ms=None, state=None, label=None):
    l = {"from": a, "to": b}
    if flow:
        l["flow"] = flow
    if ms:
        l["ms"] = ms
    if state:
        l["state"] = state
    if label:
        l["label"] = bi(*label)
    return l


def text(short, title, body, note=None, changes=None, points=None):
    t = {"short": short, "title": title, "body": list(body)}
    if note:
        t["note"] = {"kind": note[0], "html": note[1]}
    if changes:
        t["changes"] = [{"sign": s, "html": h} for s, h in changes]
    if points:
        t["points"] = list(points)
    return t


def step(en, bn, shows, links=(), values=None):
    s = {"en": en, "bn": bn, "show": list(shows), "links": list(links)}
    if values is not None:
        s["values"] = list(values)
    return s


# ---------------------------------------------------------------- 1. How a Request Travels
_ms = lambda n: f"{n} ms"  # noqa: E731
_code = ("code: 5 ms", "কোড: ৫ ms")
_query = ("query: 15 ms", "query: ১৫ ms")
BASE = [_ms(30), _ms(100), _ms(70), _ms(200)]

REQUEST = {
    "width": 760,
    "height": 290,
    "nodes": [
        node("browser", "browser", "Your browser", "আপনার ব্রাউজার", 110, 180),
        node("dns", "dns", "DNS resolver", "DNS resolver", 300, 60),
        node("server", "server", "Web server", "ওয়েব সার্ভার", 430, 180),
        node("db", "database", "Database", "ডেটাবেস", 655, 180),
    ],
    "metrics": [bi("DNS lookup", "DNS খোঁজা"), bi("Connect", "Connection খোলা"),
                bi("Request + response", "রিকোয়েস্ট + রেসপন্স"), bi("Total", "মোট")],
    "caption": bi("Example times, with a 50 ms round trip unless a step says otherwise. Total counts up to the first byte of the page.",
                  "উদাহরণের সময়। অন্য কিছু না বললে একটা round trip ৫০ ms। মোট সময় গোনা হয় পেজের প্রথম বাইট আসা পর্যন্ত।"),
    "steps": [
        step(
            text("Hit Enter", "Where does the time go?", [
                "You type <code>shop.example</code> and press Enter. A moment later the page appears.",
                "To make a page faster, first find out where its time goes. Follow one page load, hop by hop.",
            ], note=("insight", "Each hop is a message between two machines. Each message takes time, and the times add up.")),
            text("Enter চাপুন", "সময় যায় কোথায়?", [
                "আপনি <code>shop.example</code> লিখে Enter চাপলেন। একটু পরেই পেজটা চলে এল।",
                "পেজ দ্রুত করতে হলে আগে জানতে হবে সময় কোথায় যাচ্ছে। তাই একটা পেজ লোডকে ধাপে ধাপে অনুসরণ করুন।",
            ], note=("insight", "প্রতিটি ধাপ দুটো মেশিনের মধ্যে একটা বার্তা। প্রতিটি বার্তায় সময় লাগে, আর সেই সময়গুলো যোগ হয়।")),
            [show("browser", "hot", ("shop.example", "shop.example"))],
            values=[None, None, None, None],
        ),
        step(
            text("Find address", "Find the address: DNS", [
                "Networks route by IP address, not by name. So the browser first asks a DNS resolver for the address behind <code>shop.example</code>.",
                "Here the answer comes back in about 30 ms.",
            ], note=("tip", "The answer comes with a time to live (TTL). Until it runs out, the cached answer is reused, and the lookup costs nothing."),
                changes=[("+", "DNS resolver"), ("+", "Lookup: 30 ms")]),
            text("ঠিকানা খোঁজা", "ঠিকানা খোঁজা: DNS", [
                "নেটওয়ার্ক নাম দেখে নয়, IP address দেখে প্যাকেট পাঠায়। তাই ব্রাউজার প্রথমে DNS resolver-কে জিজ্ঞেস করে, <code>shop.example</code>-এর ঠিকানা কী।",
                "এখানে উত্তর আসে প্রায় ৩০ ms-এ।",
            ], note=("tip", "উত্তরের সাথে একটা time to live (TTL) থাকে। মেয়াদ শেষ না হওয়া পর্যন্ত ক্যাশ করা উত্তরই কাজে লাগে, তখন এই ধাপে কোনো সময় লাগে না।"),
                changes=[("+", "DNS resolver"), ("+", "খোঁজা: ৩০ ms")]),
            [show("browser", sub=("shop.example", "shop.example")), show("dns", "hot", ("answer: 30 ms", "উত্তর: ৩০ ms"))],
            [link("browser", "dns", "both", 1000, "hot")],
            values=[_ms(30), None, None, _ms(30)],
        ),
        step(
            text("Connect", "Open a connection: TCP and TLS", [
                "The browser opens a TCP connection to the server. The handshake costs one round trip: there and back.",
                "HTTPS then runs a TLS handshake to agree on keys, and TLS 1.3 costs one more round trip. At 50 ms each, that is 100 ms before the page is even requested.",
            ], note=("insight", "The round-trip time depends on distance and the network path. A faster server does not shorten it."),
                changes=[("+", "Web server"), ("~", "DNS answer cached for next time"), ("+", "Handshakes: 2 round trips = 100 ms")]),
            text("Connection", "Connection খোলা: TCP আর TLS", [
                "ব্রাউজার সার্ভারের সাথে TCP connection খোলে। এর handshake-এ একটা round trip লাগে: যাওয়া আর ফিরে আসা।",
                "HTTPS হলে এরপর TLS handshake হয়, যাতে দুই পক্ষ key ঠিক করে নেয়। TLS 1.3-এ লাগে আরও একটা round trip। প্রতিটি ৫০ ms হলে পেজ চাওয়ার আগেই ১০০ ms চলে যায়।",
            ], note=("insight", "Round-trip time নির্ভর করে দূরত্ব আর নেটওয়ার্কের পথের ওপর। দ্রুত সার্ভার এটা কমাতে পারে না।"),
                changes=[("+", "ওয়েব সার্ভার"), ("~", "DNS-এর উত্তর পরের বারের জন্য ক্যাশে"), ("+", "Handshake: ২টি round trip = ১০০ ms")]),
            [show("browser"), show("dns", "dim", ("cached", "ক্যাশে আছে")), show("server", "hot", ("TCP + TLS", "TCP + TLS"))],
            [link("browser", "server", "both", 1000, "hot", ("2 round trips", "২টি round trip"))],
            values=[_ms(30), _ms(100), None, _ms(130)],
        ),
        step(
            text("Request", "Send the request", [
                "Over the open connection the browser sends <code>GET /products</code>. The request takes half a round trip to arrive: 25 ms.",
                "The server checks the session and runs the code. That takes about 5 ms.",
            ], changes=[("+", "Request: 25 ms on the way + 5 ms of code")]),
            text("রিকোয়েস্ট", "রিকোয়েস্ট পাঠানো", [
                "খোলা connection দিয়ে ব্রাউজার পাঠায় <code>GET /products</code>। পৌঁছাতে লাগে আধা round trip: ২৫ ms।",
                "সার্ভার session যাচাই করে কোড চালায়। এতে লাগে প্রায় ৫ ms।",
            ], changes=[("+", "রিকোয়েস্ট: পথে ২৫ ms + কোডে ৫ ms")]),
            [show("browser"), show("dns", "dim"), show("server", "hot", _code)],
            [link("browser", "server", "to", 1000, "hot", ("GET /products", "GET /products"))],
            values=[_ms(30), _ms(100), _ms(30), _ms(160)],
        ),
        step(
            text("Fetch data", "The server asks the database", [
                "The products live in a database, not in the web server. The server sends a query and waits for the rows.",
                "Inside one data center that hop is short. Here the query takes 15 ms.",
            ], note=("insight", "A slow query here slows every page that needs it. Step 8 shows how much."),
                changes=[("+", "Database"), ("+", "Query: 15 ms")]),
            text("ডেটা আনা", "সার্ভার ডেটাবেসে জিজ্ঞেস করে", [
                "পণ্যের তথ্য থাকে ডেটাবেসে, ওয়েব সার্ভারে নয়। সার্ভার একটা query পাঠিয়ে সারিগুলোর জন্য অপেক্ষা করে।",
                "একই data center-এর ভেতরে এই পথ ছোট। এখানে query-তে লাগে ১৫ ms।",
            ], note=("insight", "এখানে query ধীর হলে যে পেজেরই এই ডেটা লাগে, সেটাই ধীর হয়। ৮ নম্বর ধাপে দেখুন কতটা।"),
                changes=[("+", "ডেটাবেস"), ("+", "Query: ১৫ ms")]),
            [show("browser"), show("dns", "dim"), show("server", sub=_code), show("db", "hot", _query)],
            [link("browser", "server"), link("server", "db", "both", 800, "hot")],
            values=[_ms(30), _ms(100), _ms(45), _ms(175)],
        ),
        step(
            text("Response", "The response comes back", [
                "The server turns the rows into HTML and sends it back: another 25 ms on the way.",
                "The first byte of the page arrives 200 ms after you pressed Enter. The browser starts reading before the last byte is in.",
            ], note=("insight", "Only 20 ms of the 200 ms was server work: 5 ms of code and 15 ms of query. The rest was the network."),
                changes=[("+", "Response: 25 ms on the way"), ("~", "First byte after 200 ms")]),
            text("রেসপন্স", "রেসপন্স ফিরে আসে", [
                "সার্ভার সারিগুলো দিয়ে HTML বানিয়ে ফেরত পাঠায়: পথে আরও ২৫ ms।",
                "Enter চাপার ২০০ ms পরে পেজের প্রথম বাইট পৌঁছায়। শেষ বাইট আসার আগেই ব্রাউজার পড়া শুরু করে।",
            ], note=("insight", "২০০ ms-এর মধ্যে সার্ভারের কাজ মাত্র ২০ ms: কোডে ৫ ms আর query-তে ১৫ ms। বাকিটা নেটওয়ার্কের।"),
                changes=[("+", "রেসপন্স: পথে ২৫ ms"), ("~", "প্রথম বাইট ২০০ ms-এ")]),
            [show("browser", "hot", ("page arrives", "পেজ এল")), show("dns", "dim"), show("server", sub=_code), show("db", sub=_query)],
            [link("browser", "server", "back", 1000, "hot", ("HTML", "HTML")), link("server", "db")],
            values=BASE,
        ),
        step(
            text("More files", "One page, dozens of requests", [
                "The HTML names more files: stylesheets, scripts, images and fonts. This page needs 40 of them.",
                "The browser reuses the open connection, so it pays the handshakes once per server, not once per file.",
            ], note=("tip", "Each extra server that a page uses, such as a separate image host, pays its own handshakes again."),
                changes=[("+", "40 more requests: CSS, JS, images, fonts"), ("~", "Same connection, no new handshakes")]),
            text("আরও ফাইল", "এক পেজে কয়েক ডজন রিকোয়েস্ট", [
                "HTML-এর ভেতরে আরও ফাইলের নাম থাকে: CSS, script, ছবি আর font। এই পেজে লাগে এমন ৪০টি ফাইল।",
                "ব্রাউজার খোলা connection-টাই আবার ব্যবহার করে। তাই handshake-এর খরচ দিতে হয় প্রতিটি সার্ভারে একবার, প্রতিটি ফাইলে নয়।",
            ], note=("tip", "পেজ যত নতুন সার্ভার ব্যবহার করে, যেমন ছবির আলাদা সার্ভার, প্রতিটির জন্য আবার handshake লাগে।"),
                changes=[("+", "আরও ৪০টি রিকোয়েস্ট: CSS, JS, ছবি, font"), ("~", "একই connection, নতুন handshake নেই")]),
            [show("browser", "hot", badge="+40"), show("dns", "dim"), show("server", "hot", _code), show("db", sub=_query)],
            [link("browser", "server", "both", 700, "hot", ("40 files, 1 connection", "৪০ ফাইল, ১ সংযোগ")), link("server", "db")],
            values=BASE,
        ),
        step(
            text("Slow query", "Case: one slow query", [
                "A new feature adds a query that scans a whole table. The database now takes 900 ms to answer.",
                "Same network, same handshakes, but the first byte now comes after more than a second. Until the query is fixed, nothing else on this page matters.",
            ], note=("insight", "Measure before you optimise. Here the network is fine; the fix is in the database (see Indexes)."),
                changes=[("~", "Query: 15 ms → 900 ms"), ("~", "Total: 200 ms → 1,085 ms")]),
            text("ধীর query", "ঘটনা: একটা ধীর query", [
                "নতুন একটা ফিচারের query পুরো table খুঁজে দেখে। এখন ডেটাবেসের উত্তর দিতে লাগে ৯০০ ms।",
                "নেটওয়ার্ক একই, handshake-ও একই, কিন্তু প্রথম বাইট আসছে এক সেকেন্ডেরও পরে। Query ঠিক না হওয়া পর্যন্ত এই পেজে আর কিছুতে হাত দিয়ে লাভ নেই।",
            ], note=("insight", "অপটিমাইজ করার আগে মাপুন। এখানে নেটওয়ার্ক ঠিক আছে, সমাধান ডেটাবেসে (Indexes অংশ দেখুন)।"),
                changes=[("~", "Query: ১৫ ms → ৯০০ ms"), ("~", "মোট: ২০০ ms → ১,০৮৫ ms")]),
            [show("browser"), show("dns", "dim"), show("server", sub=_code), show("db", "warn", ("query: 900 ms", "query: ৯০০ ms"))],
            [link("browser", "server"), link("server", "db", "both", 3600, "warn")],
            values=[_ms(30), _ms(100), _ms(955), "1,085 ms"],
        ),
        step(
            text("Far away", "Case: a user far away", [
                "Back to the fast query. Now the user is in Europe and the server is in the US. A packet there and back takes about 150 ms, not 50.",
                "The two handshakes and the request cost three round trips: 450 ms before the server does any work. Same server, same code, and the first byte comes 2.5 times later.",
            ], note=("tip", "Cut round trips and shorten the distance: reuse connections, and serve content from close to the users (see Content Delivery)."),
                changes=[("~", "Round trip: 50 ms → 150 ms"), ("~", "Connect: 100 ms → 300 ms"), ("~", "Total: 200 ms → 500 ms")]),
            text("দূরের ব্যবহারকারী", "ঘটনা: দূরের ব্যবহারকারী", [
                "Query আবার দ্রুত। এবার ব্যবহারকারী ইউরোপে, সার্ভার যুক্তরাষ্ট্রে। একটা প্যাকেটের যাওয়া-আসায় লাগে প্রায় ১৫০ ms, ৫০ নয়।",
                "দুটো handshake আর রিকোয়েস্ট মিলে তিনটি round trip: সার্ভার কাজ শুরুর আগেই ৪৫০ ms। একই সার্ভার, একই কোড, অথচ প্রথম বাইট আসে আড়াই গুণ দেরিতে।",
            ], note=("tip", "Round trip কমান আর দূরত্ব কমান: connection আবার ব্যবহার করুন, আর কনটেন্ট রাখুন ব্যবহারকারীর কাছাকাছি (Content Delivery অংশ দেখুন)।"),
                changes=[("~", "Round trip: ৫০ ms → ১৫০ ms"), ("~", "Connection: ১০০ ms → ৩০০ ms"), ("~", "মোট: ২০০ ms → ৫০০ ms")]),
            [show("browser", "warn", ("in Europe", "ইউরোপে")), show("dns", "dim", ("nearby", "কাছেই")),
             show("server", sub=("in the US", "যুক্তরাষ্ট্রে")), show("db", sub=_query)],
            [link("browser", "server", "both", 3000, "warn", ("150 ms round trip", "round trip ১৫০ ms")), link("server", "db")],
            values=[_ms(30), _ms(300), _ms(170), _ms(500)],
        ),
        step(
            text("Recap", "Where the time went", [
                "Of the 200 ms, only 20 ms was the server and the database at work. The rest was messages crossing the network.",
            ], points=[
                "<strong>DNS</strong> turns a name into an address, and the answer is cached.",
                "Every new connection costs <strong>round trips</strong>. Reuse connections.",
                "Server code is often the smallest slice, unless a <strong>slow query</strong> sneaks in.",
                "<strong>Distance</strong> makes every round trip longer.",
            ]),
            text("সারাংশ", "সময় গেল কোথায়", [
                "২০০ ms-এর মধ্যে সার্ভার আর ডেটাবেসের কাজ মাত্র ২০ ms। বাকিটা নেটওয়ার্কে বার্তা আসা-যাওয়ার সময়।",
            ], points=[
                "<strong>DNS</strong> নামকে ঠিকানায় বদলায়, আর উত্তর ক্যাশে থাকে।",
                "প্রতিটি নতুন connection-এ <strong>round trip</strong> লাগে। Connection আবার ব্যবহার করুন।",
                "সার্ভারের কোড প্রায়ই সবচেয়ে ছোট অংশ, যদি না কোনো <strong>ধীর query</strong> ঢুকে পড়ে।",
                "<strong>দূরত্ব</strong> প্রতিটি round trip লম্বা করে।",
            ]),
            [show("browser"), show("dns"), show("server", sub=_code), show("db", sub=_query)],
            [link("browser", "dns"), link("browser", "server"), link("server", "db")],
            values=BASE,
        ),
    ],
}


# ---------------------------------------------------------------- 2. Latency & Throughput
_rps = lambda n: f"{n} req/s"  # noqa: E731
_each10 = ("10 ms each", "প্রতিটিতে ১০ ms")
_each5 = ("5 ms each", "প্রতিটিতে ৫ ms")
_u80 = ("80 req/s", "৮০ req/s")
HEALTHY = [_rps(80), "40%", _ms(6), _ms(38), "0.7"]
BUSY80 = [_rps(80), "80%", _ms(35), _ms(230), "4"]

LATENCY = {
    "width": 760,
    "height": 340,
    "nodes": [
        node("users", "user", "Users", "ব্যবহারকারী", 100, 170),
        node("queue", "queue", "Queue", "Queue", 330, 170),
        node("server", "server", "Server", "সার্ভার", 575, 170),
        node("api", "service", "API", "API", 340, 170),
        node("db", "database", "Database", "ডেটাবেস", 625, 170),
        node("front", "service", "Search front end", "সার্চ front end", 320, 170),
        node("idx1", "server", "Index server 1", "Index সার্ভার ১", 620, 50),
        node("idx2", "server", "Index server 2", "Index সার্ভার ২", 620, 130),
        node("idx3", "server", "Index server 3", "Index সার্ভার ৩", 620, 210),
        node("idx100", "server", "Index server 100", "Index সার্ভার ১০০", 620, 290),
        node("app", "service", "App", "অ্যাপ", 110, 170),
        node("batch", "queue", "Batch", "Batch", 355, 170),
    ],
    "metrics": [bi("Throughput", "থ্রুপুট"), bi("Server busy", "সার্ভার ব্যস্ত"), bi("p50", "p50"),
                bi("p99", "p99"), bi("In flight", "চলমান")],
    "caption": bi("Example numbers. Steps 1 to 5 use the simplest queueing model: one server, random arrivals, 10 ms of work per request.",
                  "উদাহরণের সংখ্যা। ধাপ ১ থেকে ৫-এ সবচেয়ে সরল queueing model: একটা সার্ভার, এলোমেলো সময়ে আসা রিকোয়েস্ট, প্রতিটিতে ১০ ms কাজ।"),
    "steps": [
        step(
            text("Two numbers", "Two different questions", [
                "<strong>Latency</strong>: how long does one request take, from sending it to getting the answer?",
                "<strong>Throughput</strong>: how many requests does the system finish each second?",
            ], note=("insight", "Think of a road. The time for one car to cross the city is latency. Cars per hour is throughput.")),
            text("দুটো সংখ্যা", "দুটো আলাদা প্রশ্ন", [
                "<strong>Latency</strong>: একটা রিকোয়েস্ট পাঠানো থেকে উত্তর পাওয়া পর্যন্ত কত সময় লাগে?",
                "<strong>Throughput</strong>: সিস্টেম প্রতি সেকেন্ডে কতগুলো রিকোয়েস্ট শেষ করে?",
            ], note=("insight", "একটা রাস্তার কথা ভাবুন। একটা গাড়ির শহর পার হতে যে সময় লাগে, সেটা latency। ঘণ্টায় কতগুলো গাড়ি যায়, সেটা throughput।")),
            [show("users", sub=("20 req/s", "২০ req/s")), show("server", "hot", _each10)],
            [link("users", "server", "both", 1400, "hot")],
            values=[_rps(20), "20%", _ms(9), _ms(58), "0.25"],
        ),
        step(
            text("Busier", "More users, same server", [
                "Traffic grows four times, to 80 requests a second. The server keeps up, so throughput grows with it. The server is now busy 80% of the time.",
                "But requests arrive at uneven moments. Some find the server busy and wait in a queue, and waiting is latency too.",
            ], note=("tip", "Utilisation is the share of time the server is busy. At 80%, a new request often finds it already at work."),
                changes=[("~", "Traffic: 20 → 80 req/s"), ("+", "A queue forms: about 3 waiting"), ("~", "p99: 58 ms → 230 ms")]),
            text("ভিড় বাড়ে", "ব্যবহারকারী বেশি, সার্ভার একই", [
                "Traffic চার গুণ বেড়ে হলো সেকেন্ডে ৮০টি রিকোয়েস্ট। সার্ভার সামলে নিচ্ছে, তাই throughput-ও বাড়ছে। সার্ভার এখন ৮০% সময় ব্যস্ত।",
                "কিন্তু রিকোয়েস্ট আসে এলোমেলো সময়ে। কিছু রিকোয়েস্ট এসে দেখে সার্ভার ব্যস্ত, তাই queue-তে অপেক্ষা করে। অপেক্ষাও latency।",
            ], note=("tip", "Utilisation মানে সার্ভার কত ভাগ সময় ব্যস্ত। ৮০%-এ নতুন রিকোয়েস্ট প্রায়ই এসে দেখে সার্ভার আগে থেকেই কাজে।"),
                changes=[("~", "Traffic: ২০ → ৮০ req/s"), ("+", "Queue তৈরি হলো: গড়ে প্রায় ৩টি অপেক্ষায়"), ("~", "p99: ৫৮ ms → ২৩০ ms")]),
            [show("users", sub=_u80), show("queue", "hot", badge="3"), show("server", sub=_each10)],
            [link("users", "queue", "to", 900, "hot"), link("queue", "server", "to", 900)],
            values=BUSY80,
        ),
        step(
            text("Hockey stick", "The hockey stick", [
                "Traffic grows to 99 requests a second, and the server is 99% busy. Throughput rises only a little, from 80 to 99.",
                "But the queue explodes. The average time per request goes from 50 ms to a full second: 20 times longer.",
            ], note=("warn", "Latency stays flat for a long time, then shoots up near full load. Keep headroom at the peak."),
                changes=[("~", "Busy: 80% → 99%"), ("~", "Waiting: about 3 → about 98"), ("~", "p99: 230 ms → 4.6 s")]),
            text("হকি স্টিক", "হকি স্টিক", [
                "Traffic বেড়ে হলো সেকেন্ডে ৯৯টি রিকোয়েস্ট, সার্ভার ৯৯% ব্যস্ত। Throughput বাড়ল সামান্যই, ৮০ থেকে ৯৯।",
                "কিন্তু queue ফুলে ওঠে। একটা রিকোয়েস্টের গড় সময় ৫০ ms থেকে হয়ে যায় পুরো এক সেকেন্ড: ২০ গুণ।",
            ], note=("warn", "Latency অনেকক্ষণ প্রায় একই থাকে, তারপর পুরো লোডের কাছে গিয়ে হঠাৎ লাফিয়ে বাড়ে। পিকের সময়ও হাতে কিছুটা ফাঁকা capacity রাখুন।"),
                changes=[("~", "ব্যস্ত: ৮০% → ৯৯%"), ("~", "অপেক্ষায়: প্রায় ৩ → প্রায় ৯৮"), ("~", "p99: ২৩০ ms → ৪.৬ s")]),
            [show("users", sub=("99 req/s", "৯৯ req/s")), show("queue", "warn", badge="98"), show("server", "warn", _each10)],
            [link("users", "queue", "to", 900, "warn"), link("queue", "server", "to", 900, "warn")],
            values=[_rps(99), "99%", _ms(690), "4.6 s", "99"],
        ),
        step(
            text("Averages lie", "Averages hide the slow requests", [
                "Back to 80 requests a second. The average is 50 ms, and that looks fine.",
                "Percentiles tell more. Half the requests beat 35 ms: that is the p50. But 1 request in 100 takes longer than 230 ms: that is the p99. Users feel that tail.",
            ], note=("warn", "A page that makes many requests often hits the slow tail. Watch the p99, not only the average."),
                changes=[("~", "Back to 80 req/s"), ("~", "Average 50 ms, p50 35 ms, p99 230 ms")]),
            text("গড়ের ফাঁকি", "গড় ধীর রিকোয়েস্টগুলো লুকিয়ে ফেলে", [
                "আবার সেকেন্ডে ৮০টি রিকোয়েস্ট। গড় সময় ৫০ ms, দেখতে ভালোই লাগে।",
                "Percentile বেশি কিছু বলে। অর্ধেক রিকোয়েস্ট ৩৫ ms-এর মধ্যে শেষ হয়: এটা p50। কিন্তু প্রতি ১০০টিতে ১টি নেয় ২৩০ ms-এরও বেশি: এটা p99। ব্যবহারকারী এই ধীর অংশটাই টের পান।",
            ], note=("warn", "যে পেজ অনেকগুলো রিকোয়েস্ট করে, সেটা প্রায়ই এই ধীর অংশে পড়ে। শুধু গড় নয়, p99 দেখুন।"),
                changes=[("~", "আবার ৮০ req/s"), ("~", "গড় ৫০ ms, p50 ৩৫ ms, p99 ২৩০ ms")]),
            [show("users", sub=_u80), show("queue", badge="3"), show("server", "hot", _each10)],
            [link("users", "queue", "to", 900), link("queue", "server", "to", 900)],
            values=BUSY80,
        ),
        step(
            text("Add capacity", "Add capacity, buy back latency", [
                "Give the server twice the capacity: each request now needs 5 ms of work. The same 80 requests a second keep it only 40% busy.",
                "The queue drains and the p99 falls from 230 ms to 38 ms. Throughput did not change, because demand did not change.",
            ], note=("tip", "To lower latency under load, lower the utilisation: add capacity or do less work per request."),
                changes=[("~", "Work per request: 10 ms → 5 ms"), ("~", "Busy: 80% → 40%"), ("-", "The queue is empty most of the time")]),
            text("Capacity বাড়ান", "Capacity বাড়ালে latency ফেরত আসে", [
                "সার্ভারের capacity দ্বিগুণ করুন: এখন প্রতিটি রিকোয়েস্টে ৫ ms কাজ। সেকেন্ডে সেই একই ৮০টি রিকোয়েস্টে সার্ভার মাত্র ৪০% ব্যস্ত।",
                "Queue খালি হয়ে যায়, p99 নামে ২৩০ ms থেকে ৩৮ ms-এ। Throughput বদলায়নি, কারণ চাহিদা বদলায়নি।",
            ], note=("tip", "লোডের মধ্যে latency কমাতে utilisation কমান: capacity বাড়ান, নয়তো প্রতি রিকোয়েস্টে কাজ কমান।"),
                changes=[("~", "প্রতি রিকোয়েস্টে কাজ: ১০ ms → ৫ ms"), ("~", "ব্যস্ত: ৮০% → ৪০%"), ("-", "Queue বেশিরভাগ সময় খালি")]),
            [show("users", sub=_u80), show("queue", "dim"), show("server", "hot", _each5)],
            [link("users", "queue", "to", 900), link("queue", "server", "to", 900)],
            values=HEALTHY,
        ),
        step(
            text("Distance", "Distance is latency too", [
                "Now the users are in Europe and the server is in the US. The server is just as fast, but a packet there and back takes about 150 ms.",
                "Every request pays that before the server even starts, so the p50 goes from 6 ms to 156 ms.",
            ], note=("insight", "No server upgrade beats distance. Put the data closer to the users: caches, CDNs, more regions."),
                changes=[("+", "150 ms round trip"), ("~", "p50: 6 ms → 156 ms"), ("~", "In flight: 0.7 → 13, most of them on the wire")]),
            text("দূরত্ব", "দূরত্বও latency", [
                "এবার ব্যবহারকারীরা ইউরোপে, সার্ভার যুক্তরাষ্ট্রে। সার্ভার আগের মতোই দ্রুত, কিন্তু একটা প্যাকেটের যাওয়া-আসায় লাগে প্রায় ১৫০ ms।",
                "সার্ভার কাজ শুরুর আগেই প্রতিটি রিকোয়েস্টকে এই সময় দিতে হয়, তাই p50 ৬ ms থেকে হয় ১৫৬ ms।",
            ], note=("insight", "কোনো সার্ভার আপগ্রেড দূরত্বকে হারাতে পারে না। ডেটা রাখুন ব্যবহারকারীর কাছাকাছি: cache, CDN, আরও region।"),
                changes=[("+", "১৫০ ms round trip"), ("~", "p50: ৬ ms → ১৫৬ ms"), ("~", "চলমান: ০.৭ → ১৩, বেশিরভাগই পথে")]),
            [show("users", "warn", ("in Europe", "ইউরোপে")), show("server", sub=("in the US", "যুক্তরাষ্ট্রে"))],
            [link("users", "server", "both", 3000, "warn", ("150 ms round trip", "round trip ১৫০ ms"))],
            values=[_rps(80), "40%", _ms(156), _ms(188), "13"],
        ),
        step(
            text("In flight", "Little's Law: how much is in flight", [
                "One rule ties the numbers together: in flight = throughput × time per request. In step 2, 80 requests a second × 50 ms = 4 in flight.",
                "Each request in flight holds a thread, a connection or some memory. An API at 2,000 requests a second and 50 ms holds 100. If a slow database doubles the time, it holds 200, and a pool of 150 connections runs out.",
            ], note=("tip", "Use it to size thread pools and connection pools, and to see why a slow dependency drains them."),
                changes=[("+", "API: 2,000 req/s × 50 ms = 100 in flight"), ("~", "Time per request: 50 ms → 100 ms (slow database), so 200 in flight"),
                         ("-", "The pool of 150 connections runs out")]),
            text("চলমান", "Little's Law: একসাথে কতগুলো চলছে", [
                "একটা নিয়ম সংখ্যাগুলোকে জুড়ে দেয়: চলমান = throughput × প্রতি রিকোয়েস্টের সময়। ধাপ ২-এ সেকেন্ডে ৮০টি × ৫০ ms = ৪টি চলমান।",
                "প্রতিটি চলমান রিকোয়েস্ট একটা thread, connection বা কিছু memory ধরে রাখে। সেকেন্ডে ২,০০০ রিকোয়েস্ট আর ৫০ ms হলে একটা API ধরে রাখে ১০০টি। ধীর ডেটাবেস সময় দ্বিগুণ করলে হয় ২০০টি, আর ১৫০টি connection-এর pool ফুরিয়ে যায়।",
            ], note=("tip", "এটা দিয়ে thread pool আর connection pool-এর মাপ ঠিক করুন, আর বুঝুন ধীর dependency কেন এগুলো খালি করে দেয়।"),
                changes=[("+", "API: ২,০০০ req/s × ৫০ ms = ১০০টি চলমান"), ("~", "প্রতি রিকোয়েস্টের সময়: ৫০ ms → ১০০ ms (ধীর ডেটাবেস), তাই ২০০টি চলমান"),
                         ("-", "১৫০টি connection-এর pool ফুরিয়ে যায়")]),
            [show("users", sub=("2,000 req/s", "২,০০০ req/s")), show("api", "hot", ("100 ms each", "প্রতিটিতে ১০০ ms"), badge="200"),
             show("db", "warn", ("pool: 150 connections", "pool: ১৫০টি connection"))],
            [link("users", "api", "to", 700), link("api", "db", "both", 2400, "warn")],
            values=[_rps("2,000"), None, None, None, "200"],
        ),
        step(
            text("Fan-out", "One request, many servers", [
                "A search asks 100 index servers at once and waits for the slowest. Each server is slow on only 1 request in 100.",
                "But with 100 servers, <code>1 − 0.99^100 ≈ 0.63</code>: about 63% of searches wait on at least one slow server. A rare tail becomes the common case.",
            ], note=("tip", "A hedged request cuts the tail: if a server has not answered after a short delay, ask a second copy and use whichever answers first."),
                changes=[("+", "100 index servers, 4 shown"), ("~", "Each search waits for the slowest one")]),
            text("Fan-out", "এক রিকোয়েস্ট, অনেক সার্ভার", [
                "একটা সার্চ একসাথে ১০০টি index সার্ভারে যায় আর সবচেয়ে ধীরটার জন্য অপেক্ষা করে। প্রতিটি সার্ভার ধীর হয় ১০০টি রিকোয়েস্টে মাত্র ১টিতে।",
                "কিন্তু ১০০টি সার্ভার হলে <code>1 − 0.99^100 ≈ 0.63</code>: প্রায় ৬৩% সার্চকে অন্তত একটা ধীর সার্ভারের জন্য অপেক্ষা করতে হয়। বিরল ধীরগতি হয়ে যায় সাধারণ ঘটনা।",
            ], note=("tip", "Hedged request এই ধীর অংশ কমায়: কোনো সার্ভার অল্প সময়ের মধ্যে উত্তর না দিলে আরেকটা কপিকে জিজ্ঞেস করুন, যে আগে উত্তর দেয় সেটাই নিন।"),
                changes=[("+", "১০০টি index সার্ভার, দেখানো হয়েছে ৪টি"), ("~", "প্রতিটি সার্চ সবচেয়ে ধীরটার জন্য অপেক্ষা করে")]),
            [show("users", sub=("1 search", "১টি সার্চ")), show("front", "hot", ("waits for all 100", "১০০টিরই অপেক্ষায়")),
             show("idx1", sub=("fast", "দ্রুত")), show("idx2", sub=("fast", "দ্রুত")), show("idx3", sub=("fast", "দ্রুত")),
             show("idx100", "warn", ("slow this time", "এবার ধীর"))],
            [link("users", "front", "to", 1000), link("front", "idx1", "both", 900), link("front", "idx2", "both", 900),
             link("front", "idx3", "both", 900), link("front", "idx100", "both", 3600, "warn")],
            values=[None, None, None, None, None],
        ),
        step(
            text("Batching", "Batching: more throughput, a little more latency", [
                "An app writes events to a database one row at a time. Say each write costs 1 ms, plus 0.01 ms per row. That caps it near 1,000 rows a second.",
                "Now group the rows: wait up to 10 ms, then write 100 rows at once. The 1 ms is paid once per batch, so throughput rises to about 50,000 rows a second. Each row waits up to 10 ms longer.",
            ], note=("insight", "Batching trades latency for throughput. A Kafka producer does this: it can wait up to <code>linger.ms</code> to fill a batch."),
                changes=[("~", "Rows per write: 1 → 100"), ("~", "Throughput: about 1,000 → 50,000 rows/s"), ("+", "Each row waits up to 10 ms")]),
            text("Batching", "Batching: throughput বেশি, latency একটু বেশি", [
                "একটা অ্যাপ ডেটাবেসে একটা একটা করে সারি লেখে। ধরুন প্রতিটি write-এ লাগে ১ ms, আর প্রতি সারিতে আরও ০.০১ ms। তাহলে সেকেন্ডে প্রায় ১,০০০ সারির বেশি লেখা যায় না।",
                "এবার সারিগুলো জমিয়ে নিন: বড়জোর ১০ ms অপেক্ষা করে একবারে ১০০টি সারি লিখুন। ১ ms-এর খরচ এখন প্রতি batch-এ একবার, তাই throughput বেড়ে হয় সেকেন্ডে প্রায় ৫০,০০০ সারি। প্রতিটি সারি বড়জোর ১০ ms বেশি অপেক্ষা করে।",
            ], note=("insight", "Batching latency দিয়ে throughput কেনে। Kafka producer এভাবেই কাজ করে: batch ভরতে সে <code>linger.ms</code> পর্যন্ত অপেক্ষা করতে পারে।"),
                changes=[("~", "প্রতি write-এ সারি: ১ → ১০০"), ("~", "Throughput: প্রায় ১,০০০ → ৫০,০০০ সারি/সেকেন্ড"), ("+", "প্রতিটি সারি বড়জোর ১০ ms অপেক্ষা করে")]),
            [show("app", sub=("events", "event")), show("batch", "hot", ("100 rows or 10 ms", "১০০ সারি বা ১০ ms")),
             show("db", sub=("1 write per batch", "প্রতি batch-এ ১টি write"))],
            [link("app", "batch", "to", 500), link("batch", "db", "to", 1800, "hot")],
            values=[bi("50,000 rows/s", "৫০,০০০ সারি/সে"), None, None, None, None],
        ),
        step(
            text("Recap", "Recap", [
                "Two numbers describe speed, and they move differently.",
            ], points=[
                "<strong>Latency</strong> is the time for one request. <strong>Throughput</strong> is requests per second.",
                "Latency shoots up as a server nears 100% busy. Keep <strong>headroom</strong>.",
                "Watch the <strong>p99</strong>, not only the average.",
                "<strong>Distance</strong> adds latency that no server can remove.",
                "<strong>In flight = throughput × latency</strong>. Fan-out turns a rare tail into a common one.",
            ]),
            text("সারাংশ", "সারাংশ", [
                "গতির দুটো সংখ্যা আছে, আর সেগুলো আলাদাভাবে বদলায়।",
            ], points=[
                "<strong>Latency</strong> হলো একটা রিকোয়েস্টের সময়। <strong>Throughput</strong> হলো সেকেন্ডে কতগুলো রিকোয়েস্ট।",
                "সার্ভার ১০০% ব্যস্ততার কাছে গেলে latency লাফিয়ে বাড়ে। হাতে <strong>ফাঁকা capacity</strong> রাখুন।",
                "শুধু গড় নয়, <strong>p99</strong> দেখুন।",
                "<strong>দূরত্ব</strong> এমন latency যোগ করে, যা কোনো সার্ভার সরাতে পারে না।",
                "<strong>চলমান = throughput × latency</strong>। Fan-out বিরল ধীরগতিকে সাধারণ ঘটনা বানায়।",
            ]),
            [show("users", sub=_u80), show("queue", "dim"), show("server", sub=_each5)],
            [link("users", "queue", "to", 900), link("queue", "server", "to", 900)],
            values=HEALTHY,
        ),
    ],
}


# ---------------------------------------------------------------- 3. Napkin Math
_users = ("5 million a day", "দিনে ৫০ লাখ")
_dau = bi("5 million", "৫০ লাখ")
_spares = bi("10 + spares", "১০ + বাড়তি")
_store = "3.6 TB × 3"
FULL = [_dau, "1,000/s", "5,000/s", _spares, _store]

NAPKIN = {
    "width": 760,
    "height": 320,
    "nodes": [
        node("users", "user", "Users", "ব্যবহারকারী", 100, 170),
        node("app", "server", "App server", "অ্যাপ সার্ভার", 385, 170),
        node("db", "database", "Database", "ডেটাবেস", 650, 170),
        node("cdn", "cdn", "CDN", "CDN", 385, 50),
        node("cache", "cache", "Cache", "Cache", 650, 280),
        node("n1", "note", "Read from memory", "মেমোরি থেকে পড়া", 135, 100),
        node("n2", "note", "Read 1 MB from memory", "মেমোরি থেকে ১ MB পড়া", 380, 100),
        node("n3", "note", "Disk seek", "ডিস্ক seek", 625, 100),
        node("n4", "note", "Read 1 MB from disk", "ডিস্ক থেকে ১ MB পড়া", 255, 225),
        node("n5", "note", "US to Europe and back", "যুক্তরাষ্ট্র-ইউরোপ যাওয়া-আসা", 515, 225),
    ],
    "metrics": [bi("Daily users", "দৈনিক ব্যবহারকারী"), bi("Average reads", "গড় read"), bi("Peak reads", "পিকে read"),
                bi("App servers", "অ্যাপ সার্ভার"), bi("Storage a year", "বছরে স্টোরেজ")],
    "caption": bi("A recipe site with 5 million daily users. Every number is rounded on purpose.",
                  "৫০ লাখ দৈনিক ব্যবহারকারীর একটা রেসিপি সাইট। প্রতিটি সংখ্যা ইচ্ছে করেই গোল করা।"),
    "steps": [
        step(
            text("The question", "Will one server do?", [
                "You are designing a recipe site. Before you pick any technology, you need a sense of scale: is this one server or a hundred?",
                "You do not need exact numbers, only the right order of magnitude. Rough arithmetic gets you there in minutes.",
            ], note=("insight", "Rough numbers first, then a design that fits them.")),
            text("প্রশ্ন", "একটা সার্ভারে চলবে?", [
                "আপনি একটা রেসিপি সাইট ডিজাইন করছেন। কোনো প্রযুক্তি বাছার আগে আকারটা বোঝা দরকার: একটা সার্ভার, নাকি একশোটা?",
                "ঠিক সংখ্যা লাগবে না, লাগবে সঠিক মাত্রা (order of magnitude)। মোটা দাগের হিসাবেই কয়েক মিনিটে সেটা পাওয়া যায়।",
            ], note=("insight", "আগে মোটা হিসাব, তারপর সেই হিসাবে মানানসই ডিজাইন।")),
            [show("users", sub=_users), show("app", "hot", ("enough?", "যথেষ্ট?"))],
            [link("users", "app", "to", 1200)],
            values=[_dau, None, None, None, None],
        ),
        step(
            text("Requests / s", "Daily users to requests per second", [
                "Start from what you know. 5 million users view 20 pages each a day: 100 million views.",
                "A day has 86,400 seconds; round it to 100,000. 100 million ÷ 100,000 = about 1,000 reads a second. The 5 million saves a day add about 50 writes a second.",
            ], note=("tip", "Rounding 86,400 to 100,000 makes the division easy, and the answer keeps the right size."),
                changes=[("+", "Average: about 1,000 reads/s"), ("+", "About 50 writes/s")]),
            text("রিকোয়েস্ট/সে", "দৈনিক ব্যবহারকারী থেকে সেকেন্ডে রিকোয়েস্ট", [
                "যা জানেন, সেখান থেকে শুরু করুন। ৫০ লাখ ব্যবহারকারী দিনে ২০টি করে পেজ দেখেন: ১০ কোটি view।",
                "এক দিনে ৮৬,৪০০ সেকেন্ড; গোল করে ধরুন ১,০০,০০০। ১০ কোটি ÷ ১,০০,০০০ = সেকেন্ডে প্রায় ১,০০০ read। দিনে ৫০ লাখ রেসিপি সেভ মানে সেকেন্ডে প্রায় ৫০টি write।",
            ], note=("tip", "৮৬,৪০০-কে ১,০০,০০০ ধরলে ভাগটা সহজ হয়, আর উত্তরের মাত্রা ঠিকই থাকে।"),
                changes=[("+", "গড়: সেকেন্ডে প্রায় ১,০০০ read"), ("+", "সেকেন্ডে প্রায় ৫০টি write")]),
            [show("users", sub=_users), show("app", "hot", ("1,000 reads/s", "১,০০০ read/সে"))],
            [link("users", "app", "to", 1000, "hot")],
            values=[_dau, "1,000/s", None, None, None],
        ),
        step(
            text("Peak", "Plan for the peak, not the average", [
                "Traffic is not flat. Evenings, launches and news bring several times the average.",
                "Size for a peak of 3 to 5 times the average: up to 5,000 reads a second. One server will not keep up.",
            ], note=("warn", "Size for the average, and the site slows down exactly when the most people are on it."),
                changes=[("+", "Peak: up to 5,000 reads/s"), ("~", "One server: overloaded")]),
            text("পিক", "গড় নয়, পিকের জন্য পরিকল্পনা", [
                "Traffic সমান থাকে না। সন্ধ্যা, নতুন লঞ্চ আর খবরের সময় গড়ের কয়েক গুণ চাপ আসে।",
                "গড়ের ৩ থেকে ৫ গুণ পিক ধরে মাপ ঠিক করুন: সেকেন্ডে ৫,০০০ read পর্যন্ত। একটা সার্ভার এটা সামলাতে পারবে না।",
            ], note=("warn", "গড় ধরে মাপ ঠিক করলে, ঠিক যখন সবচেয়ে বেশি মানুষ সাইটে, তখনই সাইট ধীর হয়ে যায়।"),
                changes=[("+", "পিক: সেকেন্ডে ৫,০০০ read পর্যন্ত"), ("~", "একটা সার্ভার: সামলাতে পারছে না")]),
            [show("users", sub=("evening rush", "সন্ধ্যার ভিড়")), show("app", "warn", ("5,000 reads/s", "৫,০০০ read/সে"))],
            [link("users", "app", "to", 600, "warn")],
            values=[_dau, "1,000/s", "5,000/s", None, None],
        ),
        step(
            text("Servers", "How many servers?", [
                "A load test shows that one server handles 500 requests a second at the target latency.",
                "5,000 ÷ 500 = 10 servers at the peak. Add spares for spikes and for a server that fails.",
            ], note=("tip", "Use a measured number for one server, not a guess."),
                changes=[("+", "App tier: 10 servers, plus spares")]),
            text("সার্ভার", "কয়টা সার্ভার?", [
                "Load test দেখায়, কাঙ্ক্ষিত latency-তে একটা সার্ভার সেকেন্ডে ৫০০টি রিকোয়েস্ট সামলায়।",
                "৫,০০০ ÷ ৫০০ = পিকে ১০টি সার্ভার। হঠাৎ চাপ আর কোনো সার্ভার বিকল হওয়ার জন্য কয়েকটা বাড়তি রাখুন।",
            ], note=("tip", "একটা সার্ভারের ক্ষমতা অনুমান নয়, মেপে নিন।"),
                changes=[("+", "অ্যাপ স্তর: ১০টি সার্ভার, সাথে বাড়তি")]),
            [show("users", sub=_users), show("app", "hot", ("500 reads/s each", "প্রতিটি ৫০০ read/সে"), badge="×10")],
            [link("users", "app", "to", 900)],
            values=[_dau, "1,000/s", "5,000/s", _spares, None],
        ),
        step(
            text("Storage", "How much storage?", [
                "A saved recipe is about 2 KB. 5 million saves a day × 2 KB = 10 GB a day.",
                "Over a year that is about 3.6 TB. Keep three copies so that a dead disk loses nothing: about 11 TB.",
            ], note=("insight", "Requests rise and fall during the day. Stored bytes only grow."),
                changes=[("+", "Database"), ("+", "10 GB a day → about 3.6 TB a year"), ("~", "× 3 copies → about 11 TB")]),
            text("স্টোরেজ", "কতটা স্টোরেজ?", [
                "একটা সেভ করা রেসিপি প্রায় ২ KB। দিনে ৫০ লাখ সেভ × ২ KB = দিনে ১০ GB।",
                "বছরে সেটা প্রায় ৩.৬ TB। একটা ডিস্ক নষ্ট হলেও যাতে কিছু না হারায়, তাই তিনটি কপি রাখুন: প্রায় ১১ TB।",
            ], note=("insight", "দিনের মধ্যে রিকোয়েস্ট বাড়ে-কমে। জমানো বাইট শুধু বাড়তেই থাকে।"),
                changes=[("+", "ডেটাবেস"), ("+", "দিনে ১০ GB → বছরে প্রায় ৩.৬ TB"), ("~", "× ৩ কপি → প্রায় ১১ TB")]),
            [show("users", sub=_users), show("app", badge="×10"), show("db", "hot", ("10 GB a day", "দিনে ১০ GB"))],
            [link("users", "app", "to", 900), link("app", "db", "to", 1100, "hot")],
            values=FULL,
        ),
        step(
            text("Bandwidth", "How much network?", [
                "A page is about 100 KB. At the peak, 5,000 pages a second × 100 KB = 500 MB a second, about 4 Gbit/s.",
                "That is a job for a CDN: it serves copies of the pages from servers near the users.",
            ], note=("insight", "Count bytes, not only requests. Here the network, not the CPU, is the big number."),
                changes=[("+", "CDN"), ("+", "About 4 Gbit/s out at the peak")]),
            text("নেটওয়ার্ক", "কতটা নেটওয়ার্ক?", [
                "একটা পেজ প্রায় ১০০ KB। পিকে সেকেন্ডে ৫,০০০ পেজ × ১০০ KB = সেকেন্ডে ৫০০ MB, প্রায় ৪ Gbit/s।",
                "এই কাজ CDN-এর: ব্যবহারকারীর কাছের সার্ভার থেকে সে পেজের কপি পাঠায়।",
            ], note=("insight", "শুধু রিকোয়েস্ট নয়, বাইটও গুনুন। এখানে বড় সংখ্যাটা CPU নয়, নেটওয়ার্ক।"),
                changes=[("+", "CDN"), ("+", "পিকে প্রায় ৪ Gbit/s বাইরে যায়")]),
            [show("users", sub=_users), show("cdn", "hot", ("4 Gbit/s at peak", "পিকে ৪ Gbit/s")), show("app", badge="×10"),
             show("db", sub=("10 GB a day", "দিনে ১০ GB"))],
            [link("users", "cdn", "both", 700, "hot"), link("cdn", "app", "to", 1600, "dim"), link("app", "db")],
            values=FULL,
        ),
        step(
            text("Cache size", "Does the hot data fit in memory?", [
                "The site reads its popular recipes again and again. Could a cache hold them? 1 million recipes × 5 KB = 5 GB.",
                "That fits in the memory of one cache server. No exotic design needed.",
            ], note=("tip", "Sometimes the estimate says that a part is small. Then keep that part simple."),
                changes=[("+", "Cache: about 5 GB of hot data")]),
            text("Cache-এর মাপ", "বারবার পড়া ডেটা কি মেমোরিতে ধরবে?", [
                "সাইট জনপ্রিয় রেসিপিগুলো বারবার পড়ে। একটা cache কি সেগুলো রাখতে পারে? ১০ লাখ রেসিপি × ৫ KB = ৫ GB।",
                "এটা একটা cache সার্ভারের মেমোরিতেই ধরে যায়। জটিল কোনো ডিজাইন লাগে না।",
            ], note=("tip", "কখনো হিসাব বলে, কোনো অংশ আসলে ছোট। তখন সেই অংশটা সহজ রাখুন।"),
                changes=[("+", "Cache: প্রায় ৫ GB বারবার পড়া ডেটা")]),
            [show("users", sub=_users), show("cdn", sub=("4 Gbit/s at peak", "পিকে ৪ Gbit/s")), show("app", badge="×10"),
             show("db", "dim", ("10 GB a day", "দিনে ১০ GB")), show("cache", "hot", ("5 GB", "৫ GB"))],
            [link("users", "cdn", "both", 1000), link("cdn", "app", "to", 1600, "dim"), link("app", "cache", "both", 800, "hot"),
             link("app", "db", state="dim")],
            values=FULL,
        ),
        step(
            text("Numbers", "Numbers worth remembering", [
                "A few numbers make most estimates possible. Learn their size, not their decimals.",
            ], note=("insight", "Memory is much faster than disk, and disk is much faster than a long network round trip.")),
            text("সংখ্যা", "যে সংখ্যাগুলো মনে রাখার মতো", [
                "অল্প কয়েকটা সংখ্যা জানলেই বেশিরভাগ হিসাব করা যায়। দশমিক নয়, মাত্রাটা মনে রাখুন।",
            ], note=("insight", "মেমোরি ডিস্কের চেয়ে অনেক দ্রুত, আর ডিস্ক দূরের নেটওয়ার্ক round trip-এর চেয়ে অনেক দ্রুত।")),
            [show("n1", "hot", ("100 ns", "১০০ ns")), show("n2", sub=("250 µs", "২৫০ µs")), show("n3", sub=("8 ms", "৮ ms")),
             show("n4", sub=("20 ms", "২০ ms")), show("n5", "warn", ("150 ms", "১৫০ ms"))],
            values=FULL,
        ),
        step(
            text("Recap", "Recap", [
                "Five quick sums sized the whole site.",
            ], points=[
                "<strong>Users × actions ÷ 100,000 seconds</strong> = average requests per second.",
                "Multiply by <strong>3 to 5</strong> for the peak, and size for that.",
                "<strong>Servers</strong> = peak ÷ what one server handles, plus spares.",
                "<strong>Storage</strong> = items a day × size × 365 × copies.",
                "Estimate <strong>network</strong> and <strong>memory</strong> too. They often decide the design.",
            ]),
            text("সারাংশ", "সারাংশ", [
                "পাঁচটা ছোট হিসাবেই পুরো সাইটের মাপ পাওয়া গেল।",
            ], points=[
                "<strong>ব্যবহারকারী × কাজ ÷ ১,০০,০০০ সেকেন্ড</strong> = সেকেন্ডে গড় রিকোয়েস্ট।",
                "পিকের জন্য <strong>৩ থেকে ৫</strong> দিয়ে গুণ করুন, আর সেই মাপে সাজান।",
                "<strong>সার্ভার</strong> = পিক ÷ একটা সার্ভারের ক্ষমতা, সাথে বাড়তি।",
                "<strong>স্টোরেজ</strong> = দিনে কতগুলো × আকার × ৩৬৫ × কপি।",
                "<strong>নেটওয়ার্ক</strong> আর <strong>মেমোরি</strong>-ও হিসাব করুন। প্রায়ই এরাই ডিজাইন ঠিক করে দেয়।",
            ]),
            [show("users", sub=_users), show("cdn", sub=("4 Gbit/s at peak", "পিকে ৪ Gbit/s")), show("app", badge="×10"),
             show("db", sub=("10 GB a day", "দিনে ১০ GB")), show("cache", sub=("5 GB", "৫ GB"))],
            [link("users", "cdn"), link("cdn", "app"), link("app", "cache"), link("app", "db")],
            values=FULL,
        ),
    ],
}

WALKS = {
    "request-lifecycle": REQUEST,
    "latency-throughput": LATENCY,
    "napkin-math": NAPKIN,
}
