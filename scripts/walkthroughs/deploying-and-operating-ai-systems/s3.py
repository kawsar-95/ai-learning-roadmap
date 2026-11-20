"""Part 17 · 03 Networking fundamentals: the path of one call to a model API.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Path       Start here: "One call to a model API passes through several steps in a fixed order. Knowing that request path tells you where to look when a call fails."; remember: "The order is DNS, TCP, TLS, then HTTP ..."
  2 DNS        Body, "The path of one request": "DNS turns the name (api.example.com) into an IP address."; table: "The name does not resolve or points to the wrong place" | "could not resolve host".
  3 TCP        "TCP opens a connection to that address and port."; table: "The port is closed or a firewall drops packets" | "connection refused" or a timeout.
  4 TLS        "TLS encrypts the connection and checks the server's certificate."; table: "An expired or untrusted certificate, a wrong clock" | Certificate errors.
  5 HTTP       "HTTP sends the request and returns a status code."; table: "A bad request, missing credentials, a rate limit" | Status 400, 401, 429.
  6 Proxy      "A proxy or load balancer in between forwards the request to a healthy server."; table: "Buffering, a short idle timeout, no healthy server" | Cut-off streams, 502 or 504.
  7 Streaming  Body, "Streaming, long requests and retries": "A streamed answer arrives as server-sent events, a long-lived HTTP response. A reverse proxy that buffers the response holds the tokens back until the end, and a load balancer with a short idle timeout cuts a long generation in the middle. Turn buffering off for the streaming route (in nginx, proxy_buffering off;) and set timeouts longer than your slowest answer."
  8 Retries    The "good" callout: "Retry with backoff on 429 and 5xx. Wait, then try again with a growing delay and a little randomness. Do not retry in a tight loop, and retry only requests that are safe to repeat."
  9 Remember   The four "remember" points of the Start here box.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("client", "user", ("Client", "ক্লায়েন্ট"), 76, 162),
    node("dns", "dns", ("DNS", "DNS"), 228, 162),
    node("tcp", "server", ("TCP", "TCP"), 380, 162),
    node("tls", "lock", ("TLS", "TLS"), 532, 162),
    node("http", "service", ("HTTP", "HTTP"), 380, 162),
    node("proxy", "balancer", ("Proxy", "প্রক্সি"), 380, 162),
    node("api", "model", ("Model API", "মডেল API"), 682, 162),
]

METRICS = [
    ("Layer", "স্তর"),
    ("What you see", "যা দেখা যায়"),
    ("Retry on", "রিট্রাই করুন"),
]

CAPTION = (
    "One call to a model API passes through several steps in a fixed order. Knowing that request path tells you where to look when a call fails.",
    "একটি মডেল API কল নির্দিষ্ট ক্রমে কয়েকটা ধাপ পেরিয়ে যায়। এই রিকোয়েস্ট পাথ জানলে কল ব্যর্থ হলে কোথায় দেখতে হবে বোঝা যায়।",
)

STEPS = [
    st(("Path", "পথ"),
       ("The path of one request", "একটি রিকোয়েস্টের পথ"),
       [("One call to a model API passes through several steps in a fixed order. Knowing that request path tells you where to look when a call fails.",
         "একটি মডেল API কল নির্দিষ্ট ক্রমে কয়েকটা ধাপ পেরিয়ে যায়। এই রিকোয়েস্ট পাথ জানলে কল ব্যর্থ হলে কোথায় দেখতে হবে বোঝা যায়।"),
        ("The order is DNS, TCP, TLS, then HTTP.",
         "ক্রমটা হলো DNS, TCP, TLS, তারপর HTTP।")],
       [sh("client", "hot"), sh("dns", "hot"), sh("tcp", "hot"), sh("tls", "hot"), sh("api", "hot", ("then HTTP", "তারপর HTTP"))],
       [ln("client", "dns", "to", state="hot"), ln("dns", "tcp", "to", state="hot"), ln("tcp", "tls", "to", state="hot"), ln("tls", "api", "to", state="hot")],
       [None, None, None]),

    st(("DNS", "DNS"),
       ("Look up the name", "নামটা খুঁজে নিন"),
       [("DNS turns the name (api.example.com) into an IP address.",
         "DNS api.example.com-এর মতো নামকে IP ঠিকানায় বদলে দেয়।")],
       [sh("client"), sh("dns", "warn", x=380), sh("api")],
       [ln("client", "dns", "to", state="warn"), ln("dns", "api", "to")],
       [("DNS", "DNS"), ("could not resolve host", "could not resolve host"), None],
       note=("warn",
             "A typical failure: the name does not resolve or points to the wrong place.",
             "সাধারণ ব্যর্থতা: নামটা রিজলভ হয় না, বা ভুল জায়গায় নির্দেশ করে।")),

    st(("TCP", "TCP"),
       ("Open a connection", "সংযোগ খুলুন"),
       [("TCP opens a connection to that address and port.",
         "TCP সেই ঠিকানা আর পোর্টে একটি সংযোগ খোলে।")],
       [sh("client"), sh("tcp", "warn"), sh("api")],
       [ln("client", "tcp", "to", state="warn"), ln("tcp", "api", "to")],
       [("TCP", "TCP"), ("connection refused", "connection refused"), None],
       note=("warn",
             "A typical failure: the port is closed or a firewall drops packets. You see “connection refused” or a timeout.",
             "সাধারণ ব্যর্থতা: পোর্ট বন্ধ, বা ফায়ারওয়াল প্যাকেট ফেলে দেয়। আপনি দেখেন “connection refused” বা একটি টাইমআউট।")),

    st(("TLS", "TLS"),
       ("Encrypt the connection", "সংযোগ এনক্রিপ্ট করুন"),
       [("TLS encrypts the connection and checks the server's certificate.",
         "TLS সংযোগ এনক্রিপ্ট করে আর সার্ভারের সার্টিফিকেট যাচাই করে।")],
       [sh("client"), sh("tls", "warn", x=380), sh("api")],
       [ln("client", "tls", "to", state="warn"), ln("tls", "api", "to")],
       [("TLS", "TLS"), ("Certificate errors", "সার্টিফিকেট এরর"), None],
       note=("warn",
             "A typical failure: an expired or untrusted certificate, or a wrong clock.",
             "সাধারণ ব্যর্থতা: মেয়াদ-উত্তীর্ণ বা অবিশ্বস্ত সার্টিফিকেট, বা ভুল ঘড়ি।")),

    st(("HTTP", "HTTP"),
       ("Send the request", "রিকোয়েস্ট পাঠান"),
       [("HTTP sends the request and returns a status code.",
         "HTTP রিকোয়েস্ট পাঠায় আর একটি স্ট্যাটাস কোড ফেরত দেয়।")],
       [sh("client"), sh("http", "warn"), sh("api")],
       [ln("client", "http", "to", state="warn"), ln("http", "api", "to")],
       [("HTTP", "HTTP"), ("Status 400, 401, 429", "স্ট্যাটাস ৪০০, ৪০১, ৪২৯"), None],
       note=("warn",
             "A typical failure: a bad request, missing credentials, or a rate limit.",
             "সাধারণ ব্যর্থতা: ভুল রিকোয়েস্ট, ক্রেডেনশিয়াল না থাকা, বা রেট লিমিট।")),

    st(("Proxy", "প্রক্সি"),
       ("A machine in the middle", "মাঝখানের মেশিন"),
       [("A proxy or load balancer in between forwards the request to a healthy server.",
         "মাঝখানের প্রক্সি বা লোড ব্যালান্সার অনুরোধটা একটি সুস্থ সার্ভারে পাঠায়।")],
       [sh("client"), sh("proxy", "warn", ("or load balancer", "বা লোড ব্যালান্সার")), sh("api")],
       [ln("client", "proxy", "to", state="warn"), ln("proxy", "api", "to")],
       [("Proxy", "প্রক্সি"), ("502 or 504", "৫০২ বা ৫০৪"), None],
       note=("warn",
             "A typical failure: buffering, a short idle timeout, or no healthy server. You see cut-off streams.",
             "সাধারণ ব্যর্থতা: বাফারিং, ছোট idle timeout, বা কোনো সুস্থ সার্ভার না থাকা। আপনি দেখেন কেটে যাওয়া স্ট্রিম।")),

    st(("Streaming", "স্ট্রিমিং"),
       ("Streaming answers", "স্ট্রিমিং উত্তর"),
       [("A streamed answer arrives as server-sent events, a long-lived HTTP response. A reverse proxy that buffers the response holds the tokens back until the end, and a load balancer with a short idle timeout cuts a long generation in the middle.",
         "স্ট্রিমিং উত্তর আসে server-sent events হয়ে, মানে একটা দীর্ঘ HTTP রেসপন্স। প্রক্সি রেসপন্স বাফার করলে টোকেন শেষে একসাথে আসে, আর লোড ব্যালান্সারের idle timeout ছোট হলে লম্বা উত্তর মাঝপথে কেটে যায়।"),
        ("Turn buffering off for the streaming route (in nginx, <code>proxy_buffering off;</code>) and set timeouts longer than your slowest answer.",
         "স্ট্রিমিং রুটে বাফারিং বন্ধ করুন (nginx-এ <code>proxy_buffering off;</code>) আর timeout সবচেয়ে ধীর উত্তরের চেয়ে বড় রাখুন।")],
       [sh("client"), sh("proxy", "warn", ("holds tokens back", "টোকেন আটকে রাখে")), sh("api", "hot")],
       [ln("api", "proxy", "to", state="hot"), ln("proxy", "client", "to", state="warn")],
       [None, None, None]),

    st(("Retries", "রিট্রাই"),
       ("Retry with backoff", "ব্যাকঅফ দিয়ে রিট্রাই"),
       [("Retry with backoff on 429 and 5xx. Wait, then try again with a growing delay and a little randomness.",
         "৪২৯ বা ৫xx পেলে একটু অপেক্ষা করে আবার চেষ্টা করুন, প্রতিবার অপেক্ষা বাড়িয়ে আর একটু এলোমেলো করে।"),
        ("Do not retry in a tight loop, and retry only requests that are safe to repeat.",
         "ঘন ঘন লুপে চেষ্টা করবেন না, আর শুধু সেই অনুরোধই আবার পাঠান যা দুবার চালালে ক্ষতি নেই।")],
       [sh("client", "hot"), sh("api", "warn")],
       [ln("client", "api", "both", state="warn", label=("backoff", "ব্যাকঅফ"))],
       [None, None, ("429 and 5xx", "৪২৯ ও ৫xx")]),

    st(("Remember", "মনে রাখুন"),
       ("What to remember", "যা মনে রাখবেন"),
       [("One call to a model API passes through several steps in a fixed order. Knowing that request path tells you where to look when a call fails.",
         "একটি মডেল API কল নির্দিষ্ট ক্রমে কয়েকটা ধাপ পেরিয়ে যায়। এই রিকোয়েস্ট পাথ জানলে কল ব্যর্থ হলে কোথায় দেখতে হবে বোঝা যায়।")],
       [sh("client"), sh("proxy"), sh("api")],
       [ln("client", "proxy", "to"), ln("proxy", "api", "to")],
       [None, None, None],
       points=[("The order is DNS, TCP, TLS, then HTTP; a proxy or load balancer sits in between and forwards the request.",
                "ক্রমটা হলো DNS, TCP, TLS, তারপর HTTP; মাঝখানে বসা প্রক্সি বা লোড ব্যালান্সার অনুরোধটা এগিয়ে দেয়।"),
               ("A proxy that buffers (saves up the answer) holds tokens back, and a short idle timeout cuts long answers.",
                "যে প্রক্সি বাফার করে (মানে উত্তর জমিয়ে রাখে), সে টোকেন আটকে রাখে, আর ছোট idle timeout লম্বা উত্তর কেটে দেয়।"),
               ("For streaming, turn buffering off and set timeouts longer than your slowest answer.",
                "স্ট্রিমিংয়ে বাফারিং বন্ধ করুন আর timeout সবচেয়ে ধীর উত্তরের চেয়ে বড় রাখুন।"),
               ("Retry with backoff on 429 (rate limit) and 5xx (server errors), and only for requests that are safe to repeat.",
                "৪২৯ (রেট লিমিট) আর ৫xx (সার্ভার এরর) পেলে ব্যাকঅফ দিয়ে আবার চেষ্টা করুন, শুধু যে অনুরোধ দুবার চালালে ক্ষতি নেই তার জন্য।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
