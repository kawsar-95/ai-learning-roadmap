"""Fine-Tuning Small Models · 05 Phase 5, run it locally and ship it: quantize to GGUF, serve with llama.cpp or Ollama, wrap it, and deploy.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Quantize  Start here: "After fine-tuning, you shrink the model with quantization so it runs on ordinary hardware." "Quantization: Storing the model's numbers with fewer bits so the file gets smaller. Like compressing a video file." List: "Convert the fine-tuned model to GGUF".
  2 GGUF      Start here: "GGUF: A file format for quantized models that tools like llama.cpp and Ollama can run." "llama.cpp: A tool that runs quantized models on ordinary hardware." "Ollama: A tool that runs quantized local models behind a simple API." Body: "so it can run on ordinary hardware without a dedicated GPU server."
  3 Levels    Body: "The number in each quantization level's name is roughly the bits stored per weight." Table Q8, Q5, Q4: "Largest of the common levels" / "Closest to the original model's quality"; "Mid-size" / "A common balance of size and quality"; "Smallest of the common levels" / "Fastest and lightest, with a bit more quality loss".
  4 Test      List: "Quantize it (Q4/Q5/Q8) and test quality against your Phase 4 test set". Start here: "Test the quantized model against your Phase 4 test set."
  5 Wrap      List: "Wrap it behind an API". Start here: "API: A doorway that lets other programs send the model a request and get its answer."
  6 Docker    List: "Put it in a Docker container". Start here: "Docker container: A package that holds your app and everything it needs, so it runs the same way on any machine."
  7 Deploy    List: "Deploy it". Start here: "The steps are: convert, quantize, wrap behind an API, put in Docker, deploy."
  8 Remember  Start here: the quantized GGUF point, the Q8 / Q4 point, the Phase 4 test point, and the steps.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("ft", "model", ("Model", "মডেল"), 100, 162),
    node("gguf", "file", ("GGUF file", "GGUF ফাইল"), 260, 162),
    node("llama", "tool", ("llama.cpp", "llama.cpp"), 470, 90),
    node("ollama", "tool", ("Ollama", "Ollama"), 470, 234),
    node("hw", "server", ("Ordinary hardware", "সাধারণ হার্ডওয়্যার"), 620, 162),
    node("q8", "file", ("Q8", "Q8"), 470, 70),
    node("q5", "file", ("Q5", "Q5"), 470, 162),
    node("q4", "file", ("Q4", "Q4"), 470, 254),
    node("test", "note", ("Phase 4 test set", "Phase ৪-এর টেস্ট সেট"), 330, 162),
    node("api", "service", ("API", "API"), 310, 162),
    node("docker", "storage", ("Docker container", "ডকার কন্টেইনার"), 510, 162),
    node("dep", "server", ("Deploy", "ডিপ্লয়"), 690, 162),
]

METRICS = [
    ("File size", "ফাইলের আকার"),
    ("Quality", "মান"),
    ("Runs on", "যেখানে চলে"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Quantize", "কোয়ান্টাইজ"),
       ("Shrink the model with quantization", "কোয়ান্টাইজেশনে মডেল ছোট করুন"),
       [("After fine-tuning, you shrink the model with quantization so it runs on ordinary hardware.",
         "ফাইন-টিউনিংয়ের পর কোয়ান্টাইজেশন দিয়ে মডেলকে ছোট করা হয়, যাতে সাধারণ হার্ডওয়্যারে চলে।"),
        ("Quantization stores the model's numbers with fewer bits so the file gets smaller, like compressing a video file.",
         "কোয়ান্টাইজেশন মডেলের সংখ্যাগুলো কম বিটে রাখে, যাতে ফাইল ছোট হয়। ভিডিও ফাইল কমপ্রেস করার মতো।")],
       [sh("ft", "hot"), sh("gguf", "hot", ("fewer bits", "কম বিট"))],
       [ln("ft", "gguf", "to", state="hot")],
       [("Smaller", "ছোট"), None, None]),

    st(("GGUF", "GGUF"),
       ("GGUF, llama.cpp and Ollama", "GGUF, llama.cpp আর Ollama"),
       [("GGUF is a file format for quantized models that tools like llama.cpp and Ollama can run.",
         "GGUF কোয়ান্টাইজড মডেলের একটি ফাইল ফরম্যাট, যেটা llama.cpp আর Ollama-র মতো টুল দিয়ে চালানো যায়।"),
        ("llama.cpp runs quantized models on ordinary hardware. Ollama runs them behind a simple API.",
         "llama.cpp কোয়ান্টাইজড মডেলকে সাধারণ হার্ডওয়্যারে চালায়। Ollama একটি সহজ API-র পেছনে চালায়।")],
       [sh("gguf", "hot"), sh("llama", "hot"), sh("ollama", "hot"), sh("hw", "hot", ("no dedicated GPU server", "আলাদা GPU সার্ভার ছাড়া"))],
       [ln("gguf", "llama", "to", state="hot"), ln("gguf", "ollama", "to", state="hot"),
        ln("llama", "hw", "to", state="hot"), ln("ollama", "hw", "to", state="hot")],
       [None, None, ("Ordinary hardware", "সাধারণ হার্ডওয়্যার")]),

    st(("Levels", "স্তর"),
       ("Q8, Q5, Q4: the quantization levels", "Q8, Q5, Q4: কোয়ান্টাইজেশনের স্তর"),
       [("The number in a level's name is roughly the bits stored per weight, so a smaller number means a smaller model.",
         "স্তরের নামের সংখ্যাটা মোটামুটি প্রতিটি ওয়েটের জন্য রাখা বিট, তাই সংখ্যা ছোট মানে মডেল ছোট।"),
        ("Q8 is closest to the original quality. Q4, the smallest and fastest of the common levels, loses a bit more.",
         "Q8 আসল মানের সবচেয়ে কাছে। প্রচলিত স্তরগুলোর মধ্যে Q4 সবচেয়ে ছোট আর দ্রুত, কিন্তু মান একটু বেশি কমে।")],
       [sh("gguf", "hot"), sh("q8", "hot", ("Largest", "সবচেয়ে বড়")), sh("q5", "hot", ("Mid-size", "মাঝারি")), sh("q4", "hot", ("Smallest", "সবচেয়ে ছোট"))],
       [ln("gguf", "q8", "to", state="hot"), ln("gguf", "q5", "to", state="hot"), ln("gguf", "q4", "to", state="hot")],
       [("Q8 largest, Q4 smallest", "Q8 সবচেয়ে বড়, Q4 সবচেয়ে ছোট"), ("Q8 closest to original", "Q8 আসলের সবচেয়ে কাছে"), None],
       note=("tip", "Q5 is a common balance of size and quality.",
             "Q5 হলো আকার আর মানের একটা সাধারণ ভারসাম্য।")),

    st(("Test", "যাচাই"),
       ("Test the quantized model", "কোয়ান্টাইজড মডেল যাচাই করুন"),
       [("After you quantize it, test the quality against your Phase 4 test set.",
         "কোয়ান্টাইজ করার পর Phase ৪-এর টেস্ট সেটে মান যাচাই করুন।")],
       [sh("gguf", "hot", x=100), sh("test", "hot")],
       [ln("gguf", "test", "to", state="hot")],
       [None, ("Test it", "যাচাই করুন"), None]),

    st(("Wrap", "র‍্যাপ"),
       ("Wrap it behind an API", "API-র পেছনে র‍্যাপ করুন"),
       [("An API is a doorway that lets other programs send the model a request and get its answer.",
         "API একটি দরজার মতো, যা দিয়ে অন্য প্রোগ্রাম মডেলকে অনুরোধ পাঠাতে আর তার উত্তর পেতে পারে।")],
       [sh("gguf", "dim", x=100), sh("api", "hot")],
       [ln("api", "gguf", "to", state="hot")],
       [None, None, None]),

    st(("Docker", "Docker"),
       ("Put it in a Docker container", "Docker কন্টেইনারে রাখুন"),
       [("A Docker container is a package that holds your app and everything it needs.",
         "ডকার কন্টেইনার একটি প্যাকেজ, যাতে আপনার অ্যাপ আর তার দরকারি সবকিছু থাকে।"),
        ("So it runs the same way on any machine.",
         "ফলে যেকোনো মেশিনে একইভাবে চলে।")],
       [sh("api", "hot"), sh("docker", "hot")],
       [ln("api", "docker", "to", state="hot")],
       [None, None, None]),

    st(("Deploy", "ডিপ্লয়"),
       ("Deploy it", "ডিপ্লয় করুন"),
       [("The last step is to deploy the container.",
         "শেষ ধাপ হলো কন্টেইনারটা ডিপ্লয় করা।"),
        ("The steps are: convert, quantize, wrap behind an API, put in Docker, deploy.",
         "ধাপগুলো: কনভার্ট, কোয়ান্টাইজ, API-র পেছনে র‍্যাপ, Docker-এ রাখা, ডিপ্লয়।")],
       [sh("api", "dim"), sh("docker", "hot"), sh("dep", "hot")],
       [ln("api", "docker", "to", state="dim"), ln("docker", "dep", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Quantize, serve, wrap, deploy.",
         "কোয়ান্টাইজ, সার্ভ, র‍্যাপ, ডিপ্লয়।")],
       [sh("gguf", x=100), sh("api"), sh("docker"), sh("dep")],
       [ln("gguf", "api", "to"), ln("api", "docker", "to"), ln("docker", "dep", "to")],
       [None, None, None],
       points=[("A quantized GGUF model, run with llama.cpp or Ollama, can run on ordinary hardware without a dedicated GPU server.",
                "কোয়ান্টাইজ করা GGUF মডেল llama.cpp বা Ollama দিয়ে চালালে আলাদা GPU সার্ভার ছাড়াই সাধারণ হার্ডওয়্যারে চলতে পারে।"),
               ("Q8 is closest to the original quality; Q4, the smallest and fastest of the common levels, loses a bit more.",
                "Q8 আসল মানের সবচেয়ে কাছে; প্রচলিত স্তরগুলোর মধ্যে Q4 সবচেয়ে ছোট আর দ্রুত, কিন্তু মান একটু বেশি কমে।"),
               ("Test the quantized model against your Phase 4 test set.",
                "কোয়ান্টাইজড মডেলকে Phase ৪-এর টেস্ট সেটে যাচাই করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
