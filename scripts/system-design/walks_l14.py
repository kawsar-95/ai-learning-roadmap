"""Walk-through of lesson 14, Consistent Hashing.

Example ring (positions are percent of the way round): A 10, B 35, C 55, D 85. Keys: 1 at 22, 2 at 46, 3 at 70, 4 at 94.
Arcs owned (the stretch behind a server): A 25, B 25, C 20, D 30. Key owners: 1 -> B, 2 -> C, 3 -> D, 4 -> A.
E joins at 77: E owns 22 (all taken from D, which keeps 8), key 3 moves D -> E. C dies: D owns 50, key 2 moves C -> D.
Cache fleet: 20,000 requests/s, 95% hit, the database takes 1,000/s and can take 8,000/s.
  hash % N, 4 -> 5: 80% of keys move, hit 19%, database 16,200/s. Consistent hashing: 20% move, hit 76%, database 4,800/s.
Simulated (3 servers, 3000 trials): the biggest server owns 61% with one position each, 36% with 100 positions each.
"""
from walkkit import node, sh, ln, st, walk

P = [(380, 42), (573, 72), (676, 148), (640, 234), (483, 290), (277, 290), (120, 234), (85, 148), (187, 72)]

NODES = [
    node("app", "server", ("App", "অ্যাপ"), 70, 80),
    node("mod", "service", ("hash % N", "hash % N"), 370, 80),
    node("a", "server", ("Server A", "Server A"), *P[0]),
    node("k1", "key", ("Key 1", "Key 1"), *P[1]),
    node("b", "server", ("Server B", "Server B"), *P[2]),
    node("k2", "key", ("Key 2", "Key 2"), *P[3]),
    node("c", "server", ("Server C", "Server C"), *P[4]),
    node("k3", "key", ("Key 3", "Key 3"), *P[5]),
    node("e", "server", ("Server E", "Server E"), *P[6]),
    node("d", "server", ("Server D", "Server D"), *P[7]),
    node("k4", "key", ("Key 4", "Key 4"), *P[8]),
    node("a1", "server", ("A#1", "A#1"), *P[0]),
    node("b1", "server", ("B#1", "B#1"), *P[1]),
    node("d1", "server", ("D#1", "D#1"), *P[2]),
    node("a2", "server", ("A#2", "A#2"), *P[3]),
    node("b2", "server", ("B#2", "B#2"), *P[4]),
    node("d2", "server", ("D#2", "D#2"), *P[5]),
    node("a3", "server", ("A#3", "A#3"), *P[6]),
    node("b3", "server", ("B#3", "B#3"), *P[7]),
    node("d3", "server", ("D#3", "D#3"), *P[8]),
    node("fleet", "cache", ("Cache fleet", "Cache fleet"), 340, 170),
    node("db", "database", ("Database", "Database"), 620, 170),
]
METRICS = [("Servers", "Server"), ("Keys moved", "যে key সরে"), ("Largest share", "সবচেয়ে বড় ভাগ")]
CAPTION = ("Example ring: positions are percent of the way round. The cache numbers are for 20,000 requests a second.",
           "উদাহরণের ring: অবস্থানগুলো ঘুরে আসার শতাংশ। cache-এর সংখ্যাগুলো সেকেন্ডে ২০,০০০ request-এর জন্য।")


def ring(order, hot=(), ms=1500, flow=False):
    """Edges between neighbours around the ring. A hot edge carries a dot; the others are plain lines."""
    out = []
    for i, u in enumerate(order):
        v = order[(i + 1) % len(order)]
        if (u, v) in hot:
            out.append(ln(u, v, "to", ms, "hot"))
        elif flow:
            out.append(ln(u, v, "to", ms))
        else:
            out.append(ln(u, v))
    return out


ROW = {"a": (70, 250), "b": (220, 250), "c": (370, 250), "d": (520, 250), "e": (675, 250)}


def xy(k):
    return {"x": ROW[k][0], "y": ROW[k][1]}

FOUR_ARCS = {"a": ("owns 25%", "২৫% এর মালিক"), "b": ("owns 25%", "২৫% এর মালিক"), "c": ("owns 20%", "২০% এর মালিক"), "d": ("owns 30%", "৩০% এর মালিক")}

STEPS = [
    st(("The problem", "সমস্যা"),
       ("hash % N breaks when N changes", "N বদলালে hash % N ভেঙে যায়"),
       [("Last lesson ended badly. With <code>server = hash(key) % N</code>, going from 4 to 5 servers changes the answer for about 80% of the keys, so nearly all the data has to move.",
         "গত পাঠটা খারাপভাবে শেষ হয়েছিল। <code>server = hash(key) % N</code> হলে ৪ থেকে ৫টি server-এ গেলে প্রায় ৮০% key-র উত্তর বদলে যায়, তাই প্রায় সব ডেটা সরাতে হয়।"),
        ("Going from 10 to 11 servers is no better: about 10 keys in 11 move. For a cache that means a sudden flood of misses, and for a database it means moving nearly all the data.",
         "১০ থেকে ১১টি server-এও অবস্থা ভালো নয়: প্রতি ১১টি key-র প্রায় ১০টি সরে। Cache-এর ক্ষেত্রে এর মানে হঠাৎ miss-এর বন্যা, আর ডেটাবেসের ক্ষেত্রে প্রায় সব ডেটা সরানো।")],
       [sh("app"), sh("mod", "warn", ("N: 4 → 5", "N: ৪ → ৫")),
        sh("a", "warn", ("keeps 20%", "২০% রাখে"), **xy("a")), sh("b", "warn", ("keeps 20%", "২০% রাখে"), **xy("b")),
        sh("c", "warn", ("keeps 20%", "২০% রাখে"), **xy("c")), sh("d", "warn", ("keeps 20%", "২০% রাখে"), **xy("d")),
        sh("e", "hot", ("gets 20%", "২০% পায়"), **xy("e"))],
       [ln("app", "mod", "both", 1000, "hot")] + [ln("mod", s, "to", 1300, "warn") for s in ("a", "b", "c", "d")] + [ln("mod", "e", "to", 1300, "hot")],
       ["4 → 5", "80%", "20%"],
       note=("warn",
             "With <code>hash % N</code>, the number of servers is part of every key's address. Change it and nearly every address changes.",
             "<code>hash % N</code>-এ server-এর সংখ্যাই প্রতিটি key-র ঠিকানার অংশ। সেটা বদলালে প্রায় প্রতিটি ঠিকানা বদলায়।"),
       changes=[("~", "4 servers → 5 servers", "৪টি server → ৫টি server"),
                ("-", "About 80% of the keys change servers", "প্রায় ৮০% key server বদলায়")]),

    st(("The ring", "Ring"),
       ("Bend the hash space into a ring", "Hash space-কে বাঁকিয়ে ring বানান"),
       [("Hash values run from 0 up to the largest value. Join the two ends and you get a ring. Hash each server's name onto the ring too: here A sits 10% of the way round, B at 35%, C at 55% and D at 85%.",
         "Hash মান চলে ০ থেকে সবচেয়ে বড় মান পর্যন্ত। দুই প্রান্ত জুড়ে দিলে পাওয়া যায় একটা ring। প্রতিটি server-এর নামও ring-এর ওপর hash করে বসান: এখানে A আছে ঘুরে আসার ১০% পথে, B ৩৫%-এ, C ৫৫%-এ আর D ৮৫%-এ।"),
        ("Every lookup will walk round the ring in one direction, clockwise. After the last position it wraps back to the first.",
         "প্রতিটি খোঁজ ring ধরে এক দিকে হাঁটবে, clockwise-এ। শেষ অবস্থানের পর সে ফিরে যাবে প্রথমটিতে।")],
       [sh("a", sub=("at 10%", "১০%-এ")), sh("b", sub=("at 35%", "৩৫%-এ")), sh("c", sub=("at 55%", "৫৫%-এ")), sh("d", sub=("at 85%", "৮৫%-এ"))],
       ring(["a", "b", "c", "d"], flow=True, ms=2400),
       ["4", None, None],
       note=("tip",
             "The positions come from hashing, so they look random, but the same name always lands in the same place.",
             "অবস্থানগুলো আসে hash থেকে, তাই এলোমেলো দেখায়, কিন্তু একই নাম সবসময় একই জায়গায় পড়ে।")),

    st(("Keys", "Key"),
       ("Each key goes clockwise", "প্রতিটি key যায় clockwise-এ"),
       [("Hash each key onto the ring too. A key belongs to the first server found by walking clockwise from its position. Key 1 sits at 22%, so it belongs to B at 35%. Key 2 (46%) goes to C, key 3 (70%) to D, and key 4 (94%) wraps round to A.",
         "প্রতিটি key-ও ring-এর ওপর hash করে বসান। একটা key-র মালিক সেই server, যাকে তার অবস্থান থেকে clockwise হেঁটে প্রথম পাওয়া যায়। Key 1 আছে ২২%-এ, তাই তার মালিক ৩৫%-এর B। Key 2 (৪৬%) যায় C-তে, key 3 (৭০%) D-তে, আর key 4 (৯৪%) ঘুরে গিয়ে A-তে।"),
        ("Each server owns the stretch behind it: B owns the 25% from A to B, C owns 20%, D owns 30% and A owns 25%.",
         "প্রতিটি server-এর মালিকানায় তার পেছনের অংশ: A থেকে B পর্যন্ত ২৫% B-র, C-র ২০%, D-র ৩০% আর A-র ২৫%।")],
       [sh("a", sub=FOUR_ARCS["a"]), sh("k1", sub=("at 22%", "২২%-এ")), sh("b", sub=FOUR_ARCS["b"]), sh("k2", sub=("at 46%", "৪৬%-এ")),
        sh("c", sub=FOUR_ARCS["c"]), sh("k3", sub=("at 70%", "৭০%-এ")), sh("d", sub=FOUR_ARCS["d"]), sh("k4", sub=("at 94%", "৯৪%-এ"))],
       ring(["a", "k1", "b", "k2", "c", "k3", "d", "k4"], hot={("k1", "b"), ("k2", "c"), ("k3", "d"), ("k4", "a")}, ms=1300),
       ["4", None, "30%"],
       note=("insight",
             "A lookup needs no table of who owns what: hash the key, walk clockwise, and the first server you meet is the owner.",
             "খোঁজার জন্য কে কীসের মালিক তার কোনো table লাগে না: key hash করুন, clockwise হাঁটুন, আর প্রথম যে server পান সে-ই মালিক।")),

    st(("Add a server", "Server যোগ"),
       ("Adding a server moves one arc", "Server যোগ করলে একটা arc সরে"),
       [("Server E joins at 77%, between key 3 and D. It takes over only the arc between itself and the previous server, C at 55%. That is 22% of the keys, and all of them come from one neighbour, D. Key 3 moves from D to E, and every other key stays where it was.",
         "Server E যোগ দেয় ৭৭%-এ, key 3 আর D-র মাঝখানে। সে নেয় শুধু নিজের আর আগের server C (৫৫%)-র মাঝের arc। সেটা ২২% key, আর সবই আসে এক প্রতিবেশী D থেকে। Key 3 D থেকে E-তে যায়, আর বাকি প্রতিটি key আগের জায়গাতেই থাকে।"),
        ("With N servers, about 1/N of the keys move: here close to one in five. Compare that with 80% for <code>hash % N</code>.",
         "N-টি server হলে প্রায় ১/N অংশ key সরে: এখানে প্রায় পাঁচটির একটি। <code>hash % N</code>-এর ৮০%-এর সাথে তুলনা করুন।")],
       [sh("a", sub=("owns 25%", "২৫% এর মালিক")), sh("k1"), sh("b", sub=("owns 25%", "২৫% এর মালিক")), sh("k2"), sh("c", sub=("owns 20%", "২০% এর মালিক")),
        sh("k3", "hot", ("moves to E", "E-তে যায়")), sh("e", "hot", ("owns 22%", "২২% এর মালিক")), sh("d", sub=("owns 8%", "৮% এর মালিক")), sh("k4")],
       ring(["a", "k1", "b", "k2", "c", "k3", "e", "d", "k4"], hot={("k3", "e")}, ms=1300),
       ["5", "22%", "25%"],
       note=("tip",
             "A new server only has to fetch the keys of one neighbour. The other servers are not disturbed.",
             "নতুন server-কে শুধু এক প্রতিবেশীর key আনতে হয়। বাকি server-রা বিঘ্নিত হয় না।"),
       changes=[("+", "Server E joins the ring at 77%", "Server E ring-এ যোগ দেয় ৭৭%-এ"),
                ("~", "Key 3: D → E", "Key 3: D → E"),
                ("~", "22% of the keys move, not 80%", "২২% key সরে, ৮০% নয়")]),

    st(("Remove one", "একটা সরানো"),
       ("Removing a server moves one arc too", "Server সরালেও একটা arc-ই সরে"),
       [("Back to four servers, and now C dies. Its keys simply continue clockwise to the next server, D. Key 2, which belonged to C, now belongs to D.",
         "আবার চারটি server, আর এবার C মারা যায়। তার key-গুলো স্রেফ clockwise-এ পরের server D-তে চলে যায়। Key 2, যেটা C-র ছিল, এখন D-র।"),
        ("Nobody else is affected: A and B keep every key they had. Only the 20% of the keys that lived on C move.",
         "আর কেউ প্রভাবিত হয় না: A আর B তাদের প্রতিটি key রেখে দেয়। শুধু C-তে থাকা ২০% key সরে।")],
       [sh("a", sub=("not affected", "প্রভাবিত নয়")), sh("k1"), sh("b", sub=("not affected", "প্রভাবিত নয়")), sh("k2", "hot", ("moves to D", "D-তে যায়")),
        sh("c", "dim", ("down", "বন্ধ")), sh("k3"), sh("d", "hot", ("takes C's keys", "C-র key নেয়")), sh("k4")],
       ring(["a", "k1", "b", "k2", "c", "k3", "d", "k4"]) + [ln("k2", "d", "to", 1800, "hot", ("next live server", "পরের সচল server"))],
       ["3", "20%", "50%"],
       note=("tip",
             "The same rule handles a crash and a planned shutdown: the keys go to the next server clockwise.",
             "একই নিয়ম ক্র্যাশ আর পরিকল্পিত বন্ধ দুটোই সামলায়: key যায় clockwise-এ পরের server-এ।"),
       changes=[("-", "Server C leaves the ring", "Server C ring ছেড়ে যায়"),
                ("~", "Key 2: C → D", "Key 2: C → D"),
                ("~", "Only C's 20% of the keys move", "শুধু C-র ২০% key সরে")]),

    st(("Uneven", "অসম"),
       ("Random positions, uneven arcs", "এলোমেলো অবস্থান, অসম arc"),
       [("Servers land wherever their hash puts them, so the arcs are uneven. With C gone, D owns the stretch from B at 35% all the way to 85%: half of the ring, so it gets half of the keys and about half of the traffic.",
         "Server গুলো বসে তাদের hash যেখানে ফেলে সেখানেই, তাই arc অসম হয়। C চলে যাওয়ায় D-র মালিকানায় ৩৫%-এর B থেকে ৮৫% পর্যন্ত পুরো অংশ: ring-এর অর্ধেক, তাই সে পায় অর্ধেক key আর প্রায় অর্ধেক traffic।"),
        ("More servers do not fix this by themselves. With a few random positions, some servers always end up with long arcs.",
         "শুধু server বাড়ালে এটা ঠিক হয় না। অল্প কয়েকটা এলোমেলো অবস্থান থাকলে কোনো না কোনো server সবসময় লম্বা arc পায়।")],
       [sh("a", sub=("owns 25%", "২৫% এর মালিক")), sh("b", sub=("owns 25%", "২৫% এর মালিক")), sh("d", "warn", ("owns 50%", "৫০% এর মালিক"))],
       [ln("a", "b"), ln("b", "d", "to", 1500, "warn"), ln("d", "a")],
       ["3", None, "50%"],
       note=("warn",
             "A server that owns half of the ring takes half of the load, and it is the first to fall over. If it fails, its whole half lands on the next server.",
             "যে server ring-এর অর্ধেকের মালিক, সে অর্ধেক load নেয়, আর সবার আগে পড়ে যায়ও সে-ই। সে বিকল হলে তার পুরো অর্ধেকটা গিয়ে পড়ে পরের server-এর ওপর।"),
       changes=[("~", "D owns 50% of the ring, A and B 25% each", "D-র হাতে ring-এর ৫০%, A আর B-র ২৫% করে")]),

    st(("Virtual nodes", "Virtual node"),
       ("Virtual nodes even it out", "Virtual node ভারসাম্য আনে"),
       [("Give each server several positions on the ring by hashing <code>A#1</code>, <code>A#2</code>, <code>A#3</code> and so on. Each server now owns many small arcs instead of one big one, so the random lumps average out. A bigger machine can get more virtual nodes than a small one.",
         "<code>A#1</code>, <code>A#2</code>, <code>A#3</code> এভাবে hash করে প্রতিটি server-কে ring-এ কয়েকটা অবস্থান দিন। এখন প্রতিটি server একটা বড় arc-এর বদলে অনেক ছোট arc-এর মালিক, তাই এলোমেলো ঢিবিগুলো গড়ে মিলিয়ে যায়। বড় মেশিনকে ছোটটির চেয়ে বেশি virtual node দেওয়া যায়।"),
        ("This drawing shows three positions per server to stay readable. In a simulation of three servers, the biggest one held about 61% of the ring with one position each, and about 36% with 100 positions each. A fair share is 33%.",
         "পড়ার সুবিধার জন্য এই ছবিতে প্রতি server-এ তিনটি অবস্থান। তিনটি server-এর একটা simulation-এ প্রতিটির একটা অবস্থান থাকলে সবচেয়ে বড়টি ring-এর প্রায় ৬১% ধরেছে, আর প্রতিটির ১০০টি অবস্থান থাকলে প্রায় ৩৬%। ন্যায্য ভাগ ৩৩%।")],
       [sh("a1", "hot"), sh("b1"), sh("d1"), sh("a2", "hot"), sh("b2"), sh("d2"), sh("a3", "hot"), sh("b3"), sh("d3")],
       ring(["a1", "b1", "d1", "a2", "b2", "d2", "a3", "b3", "d3"]),
       ["3", None, None],
       note=("tip",
             "Virtual nodes also let you weigh the ring: a server with twice the capacity gets twice as many positions.",
             "Virtual node দিয়ে ring-এ ওজনও দেওয়া যায়: দ্বিগুণ সক্ষমতার server পায় দ্বিগুণ অবস্থান।"),
       changes=[("+", "Each server gets several positions", "প্রতিটি server পায় কয়েকটা অবস্থান"),
                ("~", "Many small arcs, so the shares even out", "অনেক ছোট arc, তাই ভাগগুলো সমান হয়ে আসে")]),

    st(("Replicas", "Replica"),
       ("Copies on the next servers clockwise", "পরের server-গুলোতে clockwise কপি"),
       [("One copy per key is not enough: a dead server would lose its data. So each key is stored on the first three distinct servers clockwise from it: its owner, then the next two. Key 1 lives on B, C and D.",
         "প্রতিটি key-র একটা কপি যথেষ্ট নয়: একটা server মরলে তার ডেটা হারাবে। তাই প্রতিটি key রাখা হয় তার থেকে clockwise-এ প্রথম তিনটি আলাদা server-এ: মালিক, তারপর পরের দুটি। Key 1 থাকে B, C আর D-তে।"),
        ("When a server fails, its keys are still on the next servers around the ring. With virtual nodes the walk skips positions that belong to a server it has already used. Dynamo calls this list the preference list.",
         "একটা server বিকল হলে তার key-গুলো ring ধরে পরের server-গুলোতে এখনো আছে। Virtual node থাকলে হাঁটার সময় যে server আগেই নেওয়া হয়েছে, তার অবস্থানগুলো এড়িয়ে যাওয়া হয়। Dynamo এই তালিকাকে বলে preference list।")],
       [sh("a", "dim", ("no copy", "কপি নেই")), sh("k1", "hot"), sh("b", "hot", ("copy 1, owner", "কপি ১, মালিক")), sh("c", "hot", ("copy 2", "কপি ২")), sh("d", "hot", ("copy 3", "কপি ৩"))],
       [ln("a", "k1"), ln("k1", "b", "to", 1300, "hot"), ln("b", "c", "to", 1500, "hot", ("copy", "কপি")),
        ln("c", "d", "to", 1500, "hot", ("copy", "কপি")), ln("d", "a")],
       ["4", None, None],
       note=("tip",
             "Every key now lives on three machines, so one failure loses nothing. The ring decides where the copies go.",
             "প্রতিটি key এখন তিনটি মেশিনে, তাই একটা বিকল হলেও কিছু হারায় না। কপিগুলো কোথায় যাবে, তা ঠিক করে ring।"),
       changes=[("+", "Key 1 is stored on B, C and D", "Key 1 রাখা হয় B, C আর D-তে")]),

    st(("Cache fleet", "Cache fleet"),
       ("Case: growing a cache cluster", "ঘটনা: cache cluster বাড়ানো"),
       [("A fleet of cache servers sits in front of a database, and clients pick a server with <code>hash(key) % N</code>. At 20,000 requests a second and a 95% hit ratio, the database sees about 1,000 reads a second, and it can take about 8,000.",
         "একটা ডেটাবেসের সামনে বসে আছে cache server-এর একটা বহর, আর client <code>hash(key) % N</code> দিয়ে server বাছে। সেকেন্ডে ২০,০০০ request আর ৯৫% hit ratio-তে ডেটাবেস দেখে সেকেন্ডে প্রায় ১,০০০টি read, আর সে সামলাতে পারে প্রায় ৮,০০০টি।"),
        ("Add a fifth server, and about 80% of the keys now map to a server that has never seen them. The hit ratio falls to about 19%, and the database suddenly takes about 16,200 reads a second, twice what it can take. With consistent hashing only about one key in five moves, so the database takes about 4,800 a second and survives.",
         "পঞ্চম server যোগ করলে প্রায় ৮০% key এখন এমন server-এ যায়, যে তাদের কখনো দেখেনি। Hit ratio নেমে আসে প্রায় ১৯%-এ, আর ডেটাবেস হঠাৎ সামলাতে হয় সেকেন্ডে প্রায় ১৬,২০০ read, সে যা পারে তার দ্বিগুণ। Consistent hashing-এ প্রায় পাঁচটির একটি key সরে, তাই ডেটাবেস সামলায় সেকেন্ডে প্রায় ৪,৮০০ আর টিকে যায়।")],
       [sh("app", y=170), sh("fleet", "warn", ("hit ratio 19%", "hit ratio ১৯%")), sh("db", "warn", ("16,200 reads/s", "১৬,২০০ read/s"))],
       [ln("app", "fleet", "both", 900, "warn", ("20,000/s", "২০,০০০/s")), ln("fleet", "db", "to", 700, "warn", ("81% misses", "৮১% miss"))],
       ["4 → 5", "80%", None],
       note=("warn",
             "Adding one cache server with <code>hash % N</code> can empty most of the cache at once, and the database pays for it.",
             "<code>hash % N</code> থাকা অবস্থায় একটা cache server যোগ করলে একসাথে প্রায় পুরো cache খালি হয়ে যেতে পারে, আর দাম দেয় ডেটাবেস।"),
       changes=[("~", "Hit ratio: 95% → about 19%", "Hit ratio: ৯৫% → প্রায় ১৯%"),
                ("~", "Database reads: 1,000 → about 16,200 a second", "ডেটাবেসের read: ১,০০০ → প্রায় ১৬,২০০ প্রতি সেকেন্ড"),
                ("+", "With consistent hashing: about 4,800 a second", "Consistent hashing-এ: প্রায় ৪,৮০০ প্রতি সেকেন্ড")]),

    st(("Recap", "সারাংশ"),
       ("Move one arc, not everything", "সব নয়, একটা arc সরান"),
       [("A hash ring lets servers join and leave while almost every key stays where it is.",
         "Hash ring-এ server যোগ দিতে আর ছাড়তে পারে, অথচ প্রায় প্রতিটি key নিজের জায়গায় থাকে।")],
       [sh("a"), sh("b"), sh("c"), sh("d")],
       ring(["a", "b", "c", "d"], flow=True, ms=2400),
       ["4", None, None],
       points=[("Put servers and keys on a <strong>hash ring</strong>. A key belongs to the next server clockwise.",
                "Server আর key রাখুন একটা <strong>hash ring</strong>-এ। একটা key-র মালিক clockwise-এ পরের server।"),
               ("Adding or removing a server moves only <strong>one arc</strong>: about 1/N of the keys, not nearly all of them.",
                "Server যোগ বা সরালে সরে শুধু <strong>একটা arc</strong>: প্রায় ১/N অংশ key, প্রায় সবগুলো নয়।"),
               ("Random positions make uneven arcs. <strong>Virtual nodes</strong> give each server many positions and even out the load.",
                "এলোমেলো অবস্থান অসম arc বানায়। <strong>Virtual node</strong> প্রতিটি server-কে অনেক অবস্থান দেয় আর load সমান করে।"),
               ("Store each key on the next <strong>N distinct servers</strong> clockwise to keep N copies.",
                "N-টি কপি রাখতে প্রতিটি key রাখুন clockwise-এ পরের <strong>N-টি আলাদা server</strong>-এ।"),
               ("Caches use it so that a new node does not empty the cache. Dynamo and Cassandra place their data on a ring.",
                "Cache এটা ব্যবহার করে যাতে নতুন node cache খালি করে না দেয়। Dynamo আর Cassandra তাদের ডেটা রাখে ring-এ।")]),
]

WALKS = {"consistent-hashing": walk(760, 340, NODES, METRICS, CAPTION, STEPS)}
