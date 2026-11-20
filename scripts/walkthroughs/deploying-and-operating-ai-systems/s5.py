"""Part 17 · 05 Docker and containers: what goes into a container, and what AI work adds.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Pack       Start here: "A container packs your code with everything it needs, so it runs the same on a laptop, in CI (automatic build and test) and in production. For AI, also plan for model weights, GPUs and other services."
  2 Image      Body, "Images and containers": "An image is the packed recipe, built in read-only layers. A container is a running copy of an image. A Dockerfile lists the steps that build the image."
  3 Layers     The first bullet: "Put the lines that change least first (dependencies) and the ones that change most last (your code), so a rebuild reuses the cached layers."
  4 Secrets    The second and third bullets: "Add a .dockerignore, so .git, .env and local data are not copied into the image." "Do not bake secrets into an image. Anyone who can pull the image can read its layers."
  5 Weights    Body, "Containers for AI work": "A model of many gigabytes baked into the image makes every pull slow. Mount the weights as a volume or download them at start. Baking them in gives reproducible, offline starts. Choose on purpose."
  6 GPUs       "A container sees a GPU only when the host has the NVIDIA driver and the NVIDIA Container Toolkit. Then docker run --gpus all ... hands it the GPUs."
  7 Not a VM   The "warn" callout: "A container is not a virtual machine. It shares the host's kernel, so it starts in seconds but isolates less. Do not run untrusted agent code in a plain container without further limits."
  8 Remember   The idea and the four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("code", "file", ("Your code", "আপনার কোড"), 110, 162),
    node("deps", "cache", ("Dependencies", "ডিপেন্ডেন্সি"), 110, 162),
    node("dockerfile", "note", ("Dockerfile", "Dockerfile"), 110, 162),
    node("secret", "key", ("Secrets", "সিক্রেট"), 110, 162),
    node("weights", "model", ("Weights", "ওয়েট"), 110, 162),
    node("image", "storage", ("Image", "ইমেজ"), 380, 162),
    node("volume", "database", ("Volume", "ভলিউম"), 380, 250),
    node("toolkit", "tool", ("NVIDIA toolkit", "NVIDIA টুলকিট"), 380, 162),
    node("container", "service", ("Container", "কনটেইনার"), 650, 162),
    node("reader", "user", ("Anyone", "যে কেউ"), 650, 162),
    node("gpu", "server", ("GPU", "GPU"), 650, 162),
    node("host", "server", ("Host kernel", "হোস্ট কার্নেল"), 650, 162),
]

METRICS = [
    ("Rebuild", "রিবিল্ড"),
    ("Image pull", "ইমেজ পুল"),
    ("Start", "চালু হওয়া"),
    ("Isolation", "আইসোলেশন"),
]

CAPTION = (
    "A container packs your code with everything it needs, so it runs the same on a laptop, in CI and in production.",
    "কনটেইনার আপনার কোড আর তার দরকারি সবকিছু একসাথে প্যাক করে, তাই ল্যাপটপ, CI আর প্রোডাকশনে একই ভাবে চলে।",
)

STEPS = [
    st(("Pack", "প্যাক"),
       ("Pack the code with what it needs", "কোড আর তার দরকারি সবকিছু প্যাক করুন"),
       [("A container packs your code with everything it needs, so it runs the same on a laptop, in CI (automatic build and test) and in production.",
         "কনটেইনার আপনার কোড আর তার দরকারি সবকিছু একসাথে প্যাক করে, তাই ল্যাপটপ, CI (স্বয়ংক্রিয় বিল্ড ও টেস্ট) আর প্রোডাকশনে একই ভাবে চলে।"),
        ("For AI, also plan for model weights, GPUs and other services.",
         "AI-র কাজে মডেল ওয়েট, GPU আর অন্য সার্ভিসের কথাও ভাবতে হয়।")],
       [sh("code", "hot", y=75), sh("deps", "hot", ("everything it needs", "দরকারি সবকিছু"), y=250), sh("container", "hot", ("runs the same", "একই ভাবে চলে"), x=650)],
       [ln("code", "container", "to", state="hot"), ln("deps", "container", "to", state="hot")],
       [None, None, None, None]),

    st(("Image", "ইমেজ"),
       ("A recipe and a running copy", "রেসিপি আর চলমান কপি"),
       [("An image is the packed recipe, built in read-only layers. A container is a running copy of an image. A Dockerfile lists the steps that build the image.",
         "ইমেজ হলো প্যাক করা রেসিপি, যা শুধু-পড়া লেয়ার দিয়ে তৈরি। কনটেইনার হলো সেই ইমেজের চলমান কপি। Dockerfile-এ ইমেজ বানানোর ধাপগুলো লেখা থাকে।")],
       [sh("dockerfile", "hot", ("lists the steps", "ধাপগুলো লেখা")), sh("image", "hot", ("read-only layers", "শুধু-পড়া লেয়ার")), sh("container", "hot", ("a running copy", "চলমান কপি"))],
       [ln("dockerfile", "image", "to", state="hot", label=("builds", "বানায়")), ln("image", "container", "to", state="hot")],
       [None, None, None, None]),

    st(("Layers", "লেয়ার"),
       ("Order the lines", "লাইনের ক্রম ঠিক রাখুন"),
       [("Put the lines that change least first (dependencies) and the ones that change most last (your code), so a rebuild reuses the cached layers.",
         "যে লাইন কম বদলায় (ডিপেন্ডেন্সি) আগে রাখুন, আর যেটা বেশি বদলায় (আপনার কোড) পরে, যাতে রিবিল্ডে ক্যাশ করা লেয়ার কাজে লাগে।")],
       [sh("deps", "hot", ("first, changes least", "আগে, কম বদলায়")), sh("code", "hot", ("last, changes most", "পরে, বেশি বদলায়"), x=380),
        sh("image", "hot", ("cached layers reused", "ক্যাশ লেয়ার ব্যবহার"), x=650)],
       [ln("deps", "code", "to", state="hot"), ln("code", "image", "to", state="hot")],
       [("Reuses layers", "লেয়ার কাজে লাগে"), None, None, None]),

    st(("Secrets", "সিক্রেট"),
       ("Keep secrets out of the image", "সিক্রেট ইমেজের বাইরে রাখুন"),
       [("Add a <code>.dockerignore</code>, so <code>.git</code>, <code>.env</code> and local data are not copied into the image.",
         "একটি <code>.dockerignore</code> যোগ করুন, যাতে <code>.git</code>, <code>.env</code> আর লোকাল ডেটা ইমেজে কপি না হয়।"),
        ("Do not bake secrets into an image. Anyone who can pull the image can read its layers.",
         "ইমেজে কখনও সিক্রেট ঢোকাবেন না। ইমেজ পুল করতে পারলেই তার লেয়ার পড়া যায়।")],
       [sh("secret", "warn", ("baked in", "ঢুকিয়ে দেওয়া")), sh("image", "warn", ("layers can be read", "লেয়ার পড়া যায়")), sh("reader", "hot", ("who can pull it", "যে পুল করতে পারে"))],
       [ln("secret", "image", "to", state="warn"), ln("image", "reader", "to", state="warn", label=("pull", "পুল"))],
       [None, None, None, None]),

    st(("Weights", "ওয়েট"),
       ("Weights: baked in or mounted", "ওয়েট: ভেতরে, না মাউন্ট করে"),
       [("A model of many gigabytes baked into the image makes every pull slow. Mount the weights as a volume or download them at start.",
         "অনেক গিগাবাইটের মডেল ওয়েট ইমেজে ঢোকালে প্রতিবার পুল ধীর হয়। ভলিউম মাউন্ট করুন বা চালুর সময় নামান।"),
        ("Baking them in gives reproducible, offline starts. Choose on purpose.",
         "ইমেজে ঢোকালে প্রতিবার একই ভাবে আর অফলাইনে চালু হয়। ইচ্ছা করে বেছে নিন।")],
       [sh("weights", "hot", ("many gigabytes", "অনেক গিগাবাইট")), sh("image", "warn", ("slow pulls", "পুল ধীর"), y=75),
        sh("volume", "hot", ("mount or download", "মাউন্ট বা ডাউনলোড")), sh("container", "hot")],
       [ln("weights", "image", "to", state="warn", label=("baked in", "ঢোকানো")), ln("weights", "volume", "to", state="hot"),
        ln("image", "container", "to", state="warn"), ln("volume", "container", "to", state="hot")],
       [None, ("Slow", "ধীর"), None, None]),

    st(("GPUs", "GPU"),
       ("Hand the GPUs to the container", "কনটেইনারকে GPU দিন"),
       [("A container sees a GPU only when the host has the NVIDIA driver and the NVIDIA Container Toolkit. Then <code>docker run --gpus all ...</code> hands it the GPUs.",
         "কনটেইনার GPU দেখে তখনই, যখন হোস্টে NVIDIA ড্রাইভার আর NVIDIA Container Toolkit আছে। তারপর <code>docker run --gpus all ...</code> তাকে GPU দিয়ে দেয়।")],
       [sh("container", "hot", x=110), sh("toolkit", "hot", ("with the driver", "ড্রাইভারের সাথে")), sh("gpu", "hot", ("on the host", "হোস্টে"))],
       [ln("container", "toolkit", "to", state="hot"), ln("toolkit", "gpu", "to", state="hot")],
       [None, None, None, None]),

    st(("Not a VM", "VM নয়"),
       ("A container is not a VM", "কনটেইনার VM নয়"),
       [("A container is not a virtual machine. It shares the host's kernel, so it starts in seconds but isolates less.",
         "কনটেইনার ভার্চুয়াল মেশিন নয়। এটা হোস্টের কার্নেল ভাগ করে, তাই কয়েক সেকেন্ডে চালু হয় কিন্তু আইসোলেশন কম।")],
       [sh("container", "warn", ("starts in seconds", "সেকেন্ডে চালু"), x=110), sh("host", "hot", ("shared", "ভাগ করা"), x=380)],
       [ln("container", "host", "both", state="warn", label=("shares", "ভাগ করে"))],
       [None, None, ("In seconds", "কয়েক সেকেন্ডে"), ("Less", "কম")],
       note=("warn",
             "Do not run untrusted agent code in a plain container without further limits.",
             "অবিশ্বস্ত এজেন্ট কোড সাধারণ কনটেইনারে বাড়তি সীমা ছাড়া চালাবেন না।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("A container packs your code with everything it needs, so it runs the same on a laptop, in CI (automatic build and test) and in production. For AI, also plan for model weights, GPUs and other services.",
         "কনটেইনার আপনার কোড আর তার দরকারি সবকিছু একসাথে প্যাক করে, তাই ল্যাপটপ, CI (স্বয়ংক্রিয় বিল্ড ও টেস্ট) আর প্রোডাকশনে একই ভাবে চলে। AI-র কাজে মডেল ওয়েট, GPU আর অন্য সার্ভিসের কথাও ভাবতে হয়।")],
       [sh("image", x=110), sh("container", x=380), sh("host", x=650)],
       [ln("image", "container", "to"), ln("container", "host", "to")],
       [None, None, None, None],
       points=[("Put the lines that change least first, so a rebuild reuses the cached layers.",
                "যে লাইন কম বদলায় আগে রাখুন, যাতে রিবিল্ডে ক্যাশ করা লেয়ার কাজে লাগে।"),
               ("Never bake secrets into an image. Anyone who can pull the image can read its layers.",
                "ইমেজে কখনও সিক্রেট ঢোকাবেন না। ইমেজ পুল করতে পারলেই তার লেয়ার পড়া যায়।"),
               ("Baked-in weights give reproducible, offline starts but slow pulls; mounting or downloading avoids that, so choose on purpose.",
                "ওয়েট ইমেজে ঢোকালে প্রতিবার একই ভাবে আর অফলাইনে চালু হয়, কিন্তু পুল ধীর হয়; মাউন্ট করা বা চালুর সময় নামানো এটা এড়ায়, তাই ইচ্ছা করে বেছে নিন।"),
               ("A container is not a virtual machine. It shares the host's kernel, so it isolates less.",
                "কনটেইনার ভার্চুয়াল মেশিন নয়। এটা হোস্টের কার্নেল ভাগ করে, তাই আইসোলেশন কম।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
