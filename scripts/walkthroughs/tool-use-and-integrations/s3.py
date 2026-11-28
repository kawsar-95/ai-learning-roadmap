"""Part 7 · 02 MCP (Model Context Protocol) and sandboxed code execution: one server for many clients, and a locked space for model-written code.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Before    Callout: "before MCP, every IDE / agent app wrote custom integrations for every data source."; layman's voice: "no glue code".
  2 MCP       Body: "MCP is an open standard (introduced by Anthropic in late 2024, now adopted by OpenAI, Google, and the major IDE vendors) for connecting models to data and tools."; callout: "Now you write one MCP server (e.g. for Postgres) and every MCP-compatible client — Claude Code, Cursor, VS Code, custom agents — can use it."
  3 Primitives Body: "The model is the client; the data/tool provider runs an MCP server. The server exposes three primitives: Tools — functions the model can call (the action surface). Resources — read-only data the client can fetch on demand (files, DB rows, web pages). The host application decides how to surface and include them. Prompts — named prompt templates the server offers; the host can list them and let the user invoke by name."
  4 Code      Body: "Many agent tasks are easiest to express as code ("compute the average of column X"). Letting the model generate and execute code in a sandbox avoids tool explosion and gives you correctness on arithmetic."; remember: "(a separate tool per small task)".
  5 Sandbox   Start here: Sandbox ("A locked space where code can run without touching your real files or network."); "Run model-written code in a sandbox".
  6 Options   Table, "The four production options in 2025": E2B (hosted Firecracker microVMs; sub-second Python, easy REST API), Modal (hosted containers + GPU; long-running compute, ML inference), Daytona (hosted isolated sandboxes (dedicated kernel, filesystem, network) for AI-generated code; AI agent code execution, full-computer workflows), Cloudflare Workers / Sandbox (edge isolates; low-latency, cold-start-fast JS/Wasm).
  7 Remember  The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("c1", "browser", ("Claude Code", "Claude Code"), 110, 75),
    node("c2", "browser", ("Cursor", "Cursor"), 110, 250),
    node("mcp", "server", ("MCP server", "MCP সার্ভার"), 380, 162),
    node("d1", "database", ("Postgres", "Postgres"), 650, 162),
    node("tools", "tool", ("Tools", "টুলস"), 650, 75),
    node("resources", "file", ("Resources", "রিসোর্সেস"), 650, 162),
    node("prompts", "note", ("Prompts", "প্রম্পটস"), 650, 250),
    node("model", "model", ("Model", "মডেল"), 110, 162),
    node("sandbox", "lock", ("Sandbox", "স্যান্ডবক্স"), 380, 162),
    node("files", "storage", ("Files, network", "ফাইল, নেটওয়ার্ক"), 650, 162),
]

METRICS = [
    ("Servers", "সার্ভার"),
    ("Clients", "ক্লায়েন্ট"),
    ("Primitives", "প্রিমিটিভ"),
]

CAPTION = (
    "Example: MCP clients and one MCP server for Postgres, and a model that writes code to run in a sandbox.",
    "উদাহরণ: MCP ক্লায়েন্ট আর Postgres-এর জন্য একটি MCP সার্ভার, এবং স্যান্ডবক্সে চালানোর কোড লেখা একটি মডেল।",
)

ONE = ("one", "একটি")
MANY = ("many", "অনেক")

STEPS = [
    st(("Before", "আগে"),
       ("Custom code for every pair", "প্রতিটি জোড়ার জন্য আলাদা কোড"),
       [("Before MCP, every IDE and agent app wrote custom integrations for every data source.",
         "MCP-এর আগে প্রতিটি IDE আর এজেন্ট অ্যাপ প্রতিটি ডেটা সোর্সের জন্য কাস্টম ইন্টিগ্রেশন লিখত।")],
       [sh("c1", "hot", ("own glue code", "নিজের গ্লু কোড")), sh("c2", "hot", ("own glue code", "নিজের গ্লু কোড")), sh("d1", "hot")],
       [ln("c1", "d1", "to", state="warn"), ln("c2", "d1", "to", state="warn")],
       [None, None, None]),

    st(("MCP", "MCP"),
       ("One server, many clients", "একটি সার্ভার, অনেক ক্লায়েন্ট"),
       [("MCP, the Model Context Protocol, is an open standard for connecting models to data and tools. Anthropic introduced it in late 2024, and OpenAI, Google and the major IDE vendors have adopted it.",
         "MCP (Model Context Protocol) মডেলকে ডেটা আর টুলের সাথে জোড়ার একটি খোলা মানদণ্ড। Anthropic এটি ২০২৪-এর শেষে চালু করে, আর এখন OpenAI, Google ও প্রধান IDE ভেন্ডররা এটি গ্রহণ করেছে।"),
        ("Now you write one MCP server, for Postgres say, and every MCP-compatible client can use it: Claude Code, Cursor, VS Code, or a custom agent.",
         "এখন একটি MCP সার্ভার লিখলে, ধরুন Postgres-এর জন্য, সব MCP-কম্প্যাটিবল ক্লায়েন্ট সেটা ব্যবহার করতে পারে: Claude Code, Cursor, VS Code, বা কাস্টম এজেন্ট।")],
       [sh("c1", "hot"), sh("c2", "hot"), sh("mcp", "hot", ("written once", "একবারই লেখা")), sh("d1", "hot")],
       [ln("c1", "mcp", "to", state="hot"), ln("c2", "mcp", "to", state="hot"), ln("mcp", "d1", "to", state="hot")],
       [ONE, MANY, None]),

    st(("Primitives", "প্রিমিটিভ"),
       ("A server offers three things", "সার্ভার তিনটি জিনিস দেয়"),
       [("The model is the client, and the data or tool provider runs the MCP server. The server exposes three primitives.",
         "মডেল হলো ক্লায়েন্ট, আর ডেটা বা টুল প্রদানকারী MCP সার্ভার চালায়। সার্ভার তিনটি প্রিমিটিভ প্রকাশ করে।"),
        ("Tools are functions the model can call. Resources are read-only data the client can fetch on demand. Prompts are named templates the host can list, so the user can invoke one by name.",
         "টুলস হলো মডেল যে ফাংশন কল করতে পারে। রিসোর্সেস হলো শুধু-পড়ার তথ্য, যা ক্লায়েন্ট দরকারমতো আনতে পারে। প্রম্পটস হলো নাম দেওয়া টেমপ্লেট, যা হোস্ট তালিকা করতে পারে, যাতে ব্যবহারকারী নাম ধরে ব্যবহার করে।")],
       [sh("model", "hot", ("the client", "ক্লায়েন্ট")), sh("mcp", "hot"), sh("tools", "hot", ("functions to call", "কল করার ফাংশন")),
        sh("resources", "hot", ("read-only data", "শুধু-পড়ার তথ্য")), sh("prompts", "hot", ("named templates", "নাম দেওয়া টেমপ্লেট"))],
       [ln("model", "mcp", "to", state="hot"), ln("mcp", "tools", "to", state="hot"), ln("mcp", "resources", "to", state="hot"), ln("mcp", "prompts", "to", state="hot")],
       [ONE, MANY, ("three", "তিনটি")]),

    st(("Code", "কোড"),
       ("Let the model write code", "মডেলকে কোড লিখতে দিন"),
       [("Many agent tasks are easiest to express as code, such as “compute the average of column X”.",
         "অনেক এজেন্ট কাজ সবচেয়ে সহজে কোড দিয়ে প্রকাশ করা যায়, যেমন “কলাম X-এর গড় বের করো”।"),
        ("Letting the model write and run code avoids tool explosion, a separate tool for every small task, and gives correct arithmetic.",
         "মডেলকে কোড লিখে চালাতে দিলে টুলের বিস্ফোরণ (প্রতিটি ছোট কাজের জন্য আলাদা টুল) এড়ানো যায়, আর গাণিতিক হিসাব নির্ভুল হয়।")],
       [sh("model", "hot", ("writes the code", "কোড লেখে")), sh("sandbox", "hot", ("runs the code", "কোড চালায়"))],
       [ln("model", "sandbox", "to", state="hot")],
       [None, None, None]),

    st(("Sandbox", "স্যান্ডবক্স"),
       ("Run it in a sandbox", "স্যান্ডবক্সে চালান"),
       [("A sandbox is a locked space where code can run without touching your real files or network. Run model-written code in a sandbox.",
         "স্যান্ডবক্স একটি তালাবদ্ধ জায়গা, যেখানে কোড চলে কিন্তু আপনার আসল ফাইল বা নেটওয়ার্কে পৌঁছাতে পারে না। মডেলের লেখা কোড স্যান্ডবক্সে চালান।")],
       [sh("model", "hot"), sh("sandbox", "hot", ("locked space", "তালাবদ্ধ জায়গা")), sh("files", "dim", ("out of reach", "নাগালের বাইরে"))],
       [ln("model", "sandbox", "to", state="hot")],
       [None, None, None]),

    st(("Options", "বিকল্প"),
       ("Four sandbox options", "চারটি স্যান্ডবক্স বিকল্প"),
       [("The section lists four production options in 2025, each with its own best use.",
         "সেকশনে ২০২৫-এর চারটি প্রোডাকশন বিকল্প আছে, প্রতিটির নিজস্ব সেরা ব্যবহার আছে।")],
       [sh("model", "hot"), sh("sandbox", "hot", ("one of four", "চারটির একটি"))],
       [ln("model", "sandbox", "to", state="hot")],
       [None, None, None],
       changes=[("+", "E2B: hosted Firecracker microVMs, for sub-second Python and an easy REST API",
                 "E2B: হোস্টেড Firecracker microVM, সাব-সেকেন্ড Python আর সহজ REST API-র জন্য"),
                ("+", "Modal: hosted containers and GPUs, for long-running compute and ML inference",
                 "Modal: হোস্টেড কনটেইনার আর GPU, দীর্ঘ কম্পিউট আর ML ইনফারেন্সের জন্য"),
                ("+", "Daytona: hosted isolated sandboxes (dedicated kernel, filesystem, network) for AI-generated code, for AI agent code execution and full-computer workflows",
                 "Daytona: AI-জেনারেটেড কোডের জন্য হোস্টেড আইসোলেটেড স্যান্ডবক্স (আলাদা কার্নেল, ফাইলসিস্টেম, নেটওয়ার্ক), AI এজেন্টের কোড চালানো আর পুরো-কম্পিউটার ওয়ার্কফ্লোর জন্য"),
                ("+", "Cloudflare Workers / Sandbox: edge isolates, for low-latency JS and Wasm with fast cold starts",
                 "Cloudflare Workers / Sandbox: এজ আইসোলেট, কম দেরির JS ও Wasm আর দ্রুত কোল্ড-স্টার্টের জন্য")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("Write one MCP server and many clients can use it. Run the code a model writes in a sandbox.",
         "একটি MCP সার্ভার লিখুন, অনেক ক্লায়েন্ট তা ব্যবহার করবে। মডেলের লেখা কোড চালান স্যান্ডবক্সে।")],
       [sh("c1"), sh("c2"), sh("mcp"), sh("d1")],
       [ln("c1", "mcp", "to"), ln("c2", "mcp", "to"), ln("mcp", "d1", "to")],
       [None, None, None],
       points=[("Before MCP, every app needed custom code for every data source. Now one MCP server works with many clients.",
                "MCP-এর আগে প্রতিটি ডেটা সোর্সের জন্য প্রতিটি অ্যাপে কাস্টম কোড লাগত। এখন একটি MCP সার্ভার অনেক ক্লায়েন্টে চলে।"),
               ("An MCP server offers three things: tools, resources, and prompts.",
                "MCP সার্ভার তিনটি জিনিস দেয়: টুলস, রিসোর্সেস আর প্রম্পটস।"),
               ("Letting the model write and run code avoids tool explosion (a separate tool per small task) and gives correct arithmetic.",
                "মডেলকে কোড লিখে চালাতে দিলে টুলের বিস্ফোরণ (প্রতিটি ছোট কাজের জন্য আলাদা টুল) এড়ানো যায় আর গাণিতিক হিসাব নির্ভুল হয়।"),
               ("Run model-written code in a sandbox, such as E2B, Modal, Daytona, or Cloudflare Workers.",
                "মডেলের লেখা কোড স্যান্ডবক্সে চালান, যেমন E2B, Modal, Daytona বা Cloudflare Workers।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
