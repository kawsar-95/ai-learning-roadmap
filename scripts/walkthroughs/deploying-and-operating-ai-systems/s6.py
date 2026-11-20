"""Part 17 · 06 Kubernetes: the objects, and what AI adds (GPUs, slow model loads, scaling).

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 State      Start here: "Kubernetes runs containers across many machines and keeps them in the shape you describe." Body, "The objects you meet first": "You describe the state you want, and Kubernetes keeps the cluster in that state: if a container dies it starts another, and if you ask for three copies it keeps three."
  2 Objects    The table: Pod, Deployment, Service, Ingress, ConfigMap and Secret, each with what it is and its example for an LLM service.
  3 GPU        Body, "GPUs, probes and scaling": "A Pod asks for a GPU as a resource limit (nvidia.com/gpu: 1). The cluster needs the GPU vendor's device plugin installed."
  4 Limits     "Set requests and limits for CPU and memory. Without them, one Pod can starve the others on the same node."
  5 Probe      "A model can take minutes to load. A startupProbe gives it that time. Until it passes, the other probes wait and the Pod gets no traffic."
  6 Scale      "A HorizontalPodAutoscaler changes the number of replicas from a metric. CPU is a poor signal for a GPU service, so scale on request rate or queue length, which you export yourself."
  7 Need it    The "info" callout: "Do you need it? One service on one machine rarely does. Kubernetes pays off when you run many services, need rolling updates, or share a costly GPU pool between teams. Projects such as KServe package model serving for it."
  8 Remember   The idea and the five "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("you", "user", ("You", "আপনি"), 110, 162),
    node("metric", "chart", ("Request rate", "রিকোয়েস্ট রেট"), 110, 75),
    node("cpu", "server", ("CPU", "CPU"), 110, 250),
    node("ingress", "balancer", ("Ingress", "Ingress"), 110, 75),
    node("service", "dns", ("Service", "Service"), 380, 75),
    node("kube", "tool", ("Kubernetes", "Kubernetes"), 380, 162),
    node("hpa", "tool", ("Autoscaler", "অটোস্কেলার"), 380, 162),
    node("probe", "clock", ("startupProbe", "startupProbe"), 650, 162),
    node("node", "server", ("Node", "Node"), 380, 162),
    node("pod", "server", ("Pod", "Pod"), 650, 162),
    node("deploy", "service", ("Deployment", "Deployment"), 650, 250),
    node("gpu", "server", ("GPU", "GPU"), 650, 162),
]

METRICS = [
    ("Copies", "কপি"),
    ("GPUs", "GPU"),
    ("Load time", "লোড হতে সময়"),
    ("Scale on", "স্কেল করুন"),
]

CAPTION = (
    "Kubernetes runs containers across many machines and keeps them in the shape you describe. For AI, it must also place GPU work and wait while a large model loads.",
    "Kubernetes অনেক মেশিনে কনটেইনার চালায় আর আপনার বলে দেওয়া অবস্থাটা ধরে রাখে। AI-র জন্য তাকে GPU-র কাজও ঠিক জায়গায় বসাতে হয়, আর বড় মডেল লোড হওয়া পর্যন্ত অপেক্ষা করতে হয়।",
)

STEPS = [
    st(("State", "অবস্থা"),
       ("Describe the state you want", "চাওয়া অবস্থাটা বলে দিন"),
       [("Kubernetes runs containers across many machines and keeps them in the shape you describe.",
         "Kubernetes অনেক মেশিনে কনটেইনার চালায় আর আপনার বলে দেওয়া অবস্থাটা ধরে রাখে।"),
        ("You describe the state you want, and Kubernetes keeps the cluster in that state: if a container dies it starts another, and if you ask for three copies it keeps three.",
         "আপনি চাওয়া অবস্থাটা বলে দেন, আর Kubernetes ক্লাস্টারকে সেই অবস্থায় রাখে: কনটেইনার মরে গেলে নতুন একটা চালু করে, তিনটে কপি চাইলে তিনটেই রাখে।")],
       [sh("you", "hot", ("the state you want", "চাওয়া অবস্থা")), sh("kube", "hot", ("keeps that state", "সেই অবস্থা ধরে রাখে")), sh("pod", "hot", ("three copies", "তিনটে কপি"))],
       [ln("you", "kube", "to", state="hot"), ln("kube", "pod", "to", state="hot")],
       [("three", "তিনটি"), None, None, None]),

    st(("Objects", "অবজেক্ট"),
       ("The objects you meet first", "প্রথমে যে অবজেক্ট দেখবেন"),
       [("The objects you meet first, each with an example for an LLM service:",
         "প্রথমে যে অবজেক্টগুলো দেখবেন, প্রতিটির সাথে একটি LLM সার্ভিসের উদাহরণ:")],
       [sh("ingress", "hot", ("HTTP from outside", "বাইরের HTTP")), sh("service", "hot", ("a stable name", "স্থির নাম")),
        sh("pod", "hot", y=75), sh("deploy", "hot", ("keeps N copies", "N কপি ধরে রাখে"))],
       [ln("ingress", "service", "to", state="hot"), ln("service", "pod", "to", state="hot"), ln("deploy", "pod", "to", state="hot")],
       [("three", "তিনটি"), None, None, None],
       changes=[("+", "Pod: one or more containers that run together, such as a model server container.",
                 "Pod: একসাথে চলা এক বা একাধিক কনটেইনার, যেমন একটি মডেল সার্ভার কনটেইনার।"),
                ("+", "Deployment: keeps N copies of a Pod and rolls out new versions, such as three replicas of the API.",
                 "Deployment: একটি Pod-এর N কপি চালু রাখে আর নতুন ভার্সন ছাড়ে, যেমন API-এর তিনটি রেপ্লিকা।"),
                ("+", "Service: a stable name and address in front of changing Pods, such as llm-api, reached by other services.",
                 "Service: বদলাতে থাকা Pod-গুলোর সামনে একটি স্থির নাম আর ঠিকানা, যেমন llm-api, যাকে অন্য সার্ভিস ডাকে।"),
                ("+", "Ingress: routes HTTP traffic from outside to Services, such as api.example.com to llm-api.",
                 "Ingress: বাইরের HTTP ট্রাফিককে সঠিক Service-এ পাঠায়, যেমন api.example.com থেকে llm-api।"),
                ("+", "ConfigMap and Secret: settings and sensitive values, kept apart from the image, such as the model name and the API key.",
                 "ConfigMap ও Secret: সেটিংস আর সংবেদনশীল মান, ইমেজ থেকে আলাদা রাখা, যেমন মডেলের নাম আর API কী।")]),

    st(("GPU", "GPU"),
       ("Ask for a GPU", "GPU চেয়ে নিন"),
       [("A Pod asks for a GPU as a resource limit (<code>nvidia.com/gpu: 1</code>). The cluster needs the GPU vendor's device plugin installed.",
         "Pod-এ GPU চাইতে হয় resource limit হিসেবে (<code>nvidia.com/gpu: 1</code>), আর ক্লাস্টারে GPU ভেন্ডরের device plugin থাকতে হয়।")],
       [sh("pod", "hot", ("asks for a GPU", "GPU চায়"), x=110), sh("gpu", "hot", ("device plugin needed", "ডিভাইস প্লাগইন লাগে"))],
       [ln("pod", "gpu", "to", state="hot", label=("limit", "limit"))],
       [None, ("1", "১"), None, None]),

    st(("Limits", "লিমিট"),
       ("Set requests and limits", "requests আর limits দিন"),
       [("Set requests and limits for CPU and memory. Without them, one Pod can starve the others on the same node.",
         "CPU আর মেমরির requests ও limits দিন, নইলে একটা Pod পাশের Pod-গুলোকে না খাইয়ে রাখতে পারে।")],
       [sh("pod", "warn", ("no limits set", "limit দেওয়া নেই"), x=110), sh("node", "warn", ("others can starve", "অন্যরা না খেয়ে থাকে"), x=380)],
       [ln("pod", "node", "to", state="warn")],
       [None, None, None, None]),

    st(("Probe", "প্রোব"),
       ("Give a slow model time", "ধীর মডেলকে সময় দিন"),
       [("A model can take minutes to load. A <code>startupProbe</code> gives it that time.",
         "মডেল লোড হতে কয়েক মিনিট লাগতে পারে, তাই <code>startupProbe</code> দিন, সেটা ওই সময় দেয়।"),
        ("Until it passes, the other probes wait and the Pod gets no traffic.",
         "সেটা পাশ না করা পর্যন্ত অন্য probe অপেক্ষা করে আর Pod ট্রাফিক পায় না।")],
       [sh("service", "hot", x=100, y=162), sh("pod", "warn", ("loading a model", "মডেল লোড হচ্ছে"), x=400), sh("probe", "hot", ("gives it time", "সময় দেয়"))],
       [ln("service", "pod", "to", state="warn", label=("no traffic", "ট্রাফিক নেই")), ln("probe", "pod", "to", state="hot")],
       [None, None, ("minutes", "কয়েক মিনিট"), None]),

    st(("Scale", "স্কেল"),
       ("Scale on the right signal", "সঠিক সংকেতে স্কেল করুন"),
       [("A HorizontalPodAutoscaler changes the number of replicas from a metric.",
         "HorizontalPodAutoscaler একটি মেট্রিক দেখে রেপ্লিকার সংখ্যা বদলায়।"),
        ("CPU is a poor signal for a GPU service, so scale on request rate or queue length, which you export yourself.",
         "GPU সার্ভিসে CPU ঠিক সংকেত নয়, তাই রিকোয়েস্ট রেট বা কিউ দৈর্ঘ্য দেখে স্কেল করুন, যা আপনাকে নিজেই এক্সপোর্ট করতে হয়।")],
       [sh("metric", "hot", ("or queue length", "বা কিউ দৈর্ঘ্য")), sh("cpu", "warn", ("a poor signal", "ঠিক সংকেত নয়")), sh("hpa", "hot"),
        sh("pod", "hot", ("more or fewer copies", "কপি বাড়ায় বা কমায়"))],
       [ln("metric", "hpa", "to", state="hot"), ln("cpu", "hpa", "to", state="warn"), ln("hpa", "pod", "to", state="hot")],
       [None, None, None, ("Request rate", "রিকোয়েস্ট রেট")]),

    st(("Need it?", "লাগবে?"),
       ("Do you need it?", "আপনার কি লাগবে?"),
       [("One service on one machine rarely does. Kubernetes pays off when you run many services, need rolling updates, or share a costly GPU pool between teams.",
         "একটা মেশিনে একটা সার্ভিস চালালে সাধারণত Kubernetes লাগে না। অনেক সার্ভিস, রোলিং আপডেট, বা টিমগুলোর মধ্যে দামি GPU ভাগ করে নেওয়ার দরকার হলে এটা কাজে আসে।")],
       [sh("kube", "hot", x=110), sh("pod", "hot", ("many services", "অনেক সার্ভিস"), y=75), sh("gpu", "hot", ("shared by teams", "টিমগুলো ভাগ করে"), y=250)],
       [ln("kube", "pod", "to", state="hot", label=("rolling updates", "রোলিং আপডেট")), ln("kube", "gpu", "to", state="hot")],
       [None, None, None, None],
       note=("insight",
             "Projects such as KServe package model serving for it.",
             "KServe-এর মতো প্রকল্প এর জন্য মডেল সার্ভিং প্যাকেজ করে।")),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Kubernetes runs containers across many machines and keeps them in the shape you describe. For AI, it must also place GPU work and wait while a large model loads.",
         "Kubernetes অনেক মেশিনে কনটেইনার চালায় আর আপনার বলে দেওয়া অবস্থাটা ধরে রাখে। AI-র জন্য তাকে GPU-র কাজও ঠিক জায়গায় বসাতে হয়, আর বড় মডেল লোড হওয়া পর্যন্ত অপেক্ষা করতে হয়।")],
       [sh("you", x=110), sh("kube"), sh("pod")],
       [ln("you", "kube", "to"), ln("kube", "pod", "to")],
       [None, None, None, None],
       points=[("You describe the state you want. If a container dies, Kubernetes starts another.",
                "আপনি চাওয়া অবস্থাটা বলে দেন। কনটেইনার মরে গেলে Kubernetes নতুন একটা চালু করে।"),
               ("Ask for a GPU as a resource limit, and set requests and limits for CPU and memory.",
                "GPU চাইতে হয় resource limit হিসেবে, আর CPU ও মেমরির জন্য requests ও limits দিতে হয়।"),
               ("A model can take minutes to load, so add a <code>startupProbe</code>.",
                "মডেল লোড হতে কয়েক মিনিট লাগতে পারে, তাই <code>startupProbe</code> দিন।"),
               ("CPU is a poor signal for a GPU service. Scale on request rate or queue length.",
                "GPU সার্ভিসে CPU ঠিক সংকেত নয়। রিকোয়েস্ট রেট বা কিউ দৈর্ঘ্য দেখে স্কেল করুন।"),
               ("One service on one machine rarely needs Kubernetes; it pays off with many services, rolling updates, or teams sharing GPUs.",
                "একটা মেশিনে একটা সার্ভিসে সাধারণত Kubernetes লাগে না; অনেক সার্ভিস, রোলিং আপডেট বা টিমগুলোর মধ্যে GPU ভাগ করতে এটা কাজে আসে।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
