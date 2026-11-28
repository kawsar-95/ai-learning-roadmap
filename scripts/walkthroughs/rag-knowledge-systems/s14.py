"""RAG and Knowledge Systems · 14 Self-querying and text-to-SQL: letting the LLM write the filter or the query.

Every English text sits next to its Bangla text. Every claim restates the section's own text (the section carries the citations):

  1 Sentence  Start here: "Users type plain sentences, not filter code. In self-querying, an LLM turns the sentence into a search plus a filter."
  2 Schema    Body: "The LLM must be told the available fields, their types, and the allowed operators." Start here: "Schema: The description of which fields exist, their types and allowed operators."
  3 Split     Body: "A self-querying retriever has an LLM parse the request into a semantic query plus a structured metadata filter. It then runs both." Elastic's example: "science fiction movies released after 2000 with rating above 8". "Metadata filter: A rule on the labels stored with each piece of text, such as year above 2000."
  4 Validate  Body: "Validate its output against that schema before it reaches the database."
  5 Elastic   Remember: "In Elasticsearch, put the filter inside knn so the number of results you asked for (k) comes back."
  6 Counts    Body: "Counts, sums, joins and 'top customer by revenue' are exact computations, not similarity problems. The right tool is text-to-SQL." Spider: "10,181 questions over 200 databases. Its test databases have schemas the model never saw."
  7 Safe SQL  Body: "give the model the schema, validate generated SQL (read-only credentials, allow-listed tables, row limits) and log every query." "Read-only credentials: A database login that can read data but cannot change it."
  8 Remember  The four "remember" points.
"""
from kit import walk, node, sh, ln, st

NODES = [
    node("user", "user", ("Plain sentence", "সাধারণ বাক্য"), 115, 162),
    node("llm", "model", ("LLM", "LLM"), 300, 162),
    node("schema", "file", ("Schema", "স্কিমা"), 300, 50),
    node("query", "note", ("Search query", "সার্চ কুয়েরি"), 460, 95),
    node("filter", "note", ("Metadata filter", "মেটাডেটা ফিল্টার"), 460, 230),
    node("check", "shield", ("Schema check", "স্কিমা যাচাই"), 640, 230),
    node("db", "database", ("Database", "ডেটাবেস"), 640, 95),
    node("sql", "service", ("text-to-SQL", "টেক্সট-টু-SQL"), 460, 162),
    node("ro", "shield", ("Read-only login", "রিড-অনলি লগইন"), 610, 270),
]

METRICS = [
    ("Search", "সার্চ"),
    ("Filter", "ফিল্টার"),
    ("Exact work", "নির্ভুল কাজ"),
]

CAPTION = (
    "Illustrative, not a benchmark: the labels are the section's own words.",
    "উদাহরণমাত্র, বেঞ্চমার্ক নয়: লেবেলগুলো সেকশনের নিজের কথা।",
)

STEPS = [
    st(("Sentence", "বাক্য"),
       ("Users type sentences, not filters", "ব্যবহারকারী বাক্য লেখে, ফিল্টার নয়"),
       [("Users type plain sentences, not filter code.",
         "ব্যবহারকারী সাধারণ বাক্য লেখে, ফিল্টার কোড নয়।"),
        ("In self-querying, an LLM turns the sentence into a search plus a filter.",
         "সেলফ-কুয়েরিতে LLM সেই বাক্যকে একটি সার্চ আর একটি ফিল্টারে ভাঙে।")],
       [sh("user", "hot"), sh("llm", "hot")],
       [ln("user", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Schema", "স্কিমা"),
       ("Tell the LLM the schema", "LLM-কে স্কিমা জানান"),
       [("The LLM must be told the available fields, their types, and the allowed operators.",
         "LLM-কে জানাতে হয় কোন ফিল্ড আছে, তাদের ধরন কী, আর কোন অপারেটর চলবে।"),
        ("For a database, the schema is its tables and columns.",
         "ডেটাবেসের ক্ষেত্রে স্কিমা হলো তার টেবিল ও কলাম।")],
       [sh("schema", "hot", ("fields, types, operators", "ফিল্ড, ধরন, অপারেটর")), sh("llm", "hot")],
       [ln("schema", "llm", "to", state="hot")],
       [None, None, None]),

    st(("Split", "ভাগ"),
       ("A search plus a filter", "একটি সার্চ আর একটি ফিল্টার"),
       [("The LLM parses the request into a semantic query plus a structured metadata filter. It then runs both.",
         "LLM অনুরোধটিকে একটি সার্চ কুয়েরি আর একটি স্ট্রাকচার্ড মেটাডেটা ফিল্টারে ভাগ করে, তারপর দুটোই চালায়।"),
        ("A metadata filter is a rule on the labels stored with each piece of text, such as year above 2000.",
         "মেটাডেটা ফিল্টার হলো প্রতিটি লেখার টুকরোর সাথে রাখা লেবেলের ওপর শর্ত, যেমন সাল ২০০০-এর বেশি।")],
       [sh("llm", "hot"), sh("query", "hot"), sh("filter", "hot", ("year above 2000", "সাল ২০০০-এর বেশি"))],
       [ln("llm", "query", "to", state="hot"), ln("llm", "filter", "to", state="hot")],
       [("a semantic query", "সেমান্টিক কুয়েরি"), ("a metadata filter", "মেটাডেটা ফিল্টার"), None],
       note=("tip", 'Elastic\'s example: "science fiction movies released after 2000 with rating above 8".',
             'Elastic-এর উদাহরণ: "science fiction movies released after 2000 with rating above 8"।')),

    st(("Validate", "যাচাই"),
       ("Check the filter first", "আগে ফিল্টার যাচাই করুন"),
       [("Validate the LLM's output against the schema before it reaches the database.",
         "LLM-এর লেখা ফিল্টার ডেটাবেসে যাওয়ার আগে স্কিমার সাথে মিলিয়ে যাচাই করুন।")],
       [sh("filter", "hot"), sh("check", "hot"), sh("db", "dim")],
       [ln("filter", "check", "to", state="hot"), ln("check", "db", "to", state="hot")],
       [None, ("checked against the schema", "স্কিমার সাথে যাচাই করা"), None]),

    st(("Elastic", "Elasticsearch"),
       ("In Elasticsearch, the filter goes inside knn", "Elasticsearch-এ ফিল্টার থাকে knn-এর ভেতরে"),
       [("In Elasticsearch, put the filter inside knn.",
         "Elasticsearch-এ ফিল্টার knn-এর ভেতরে দিন।"),
        ("Then the number of results you asked for (k) comes back.",
         "তাহলে যতগুলো ফল চেয়েছেন (k), ততগুলোই আসে।")],
       [sh("query", "hot"), sh("filter", "hot", ("inside knn", "knn-এর ভেতরে")), sh("db", "hot", ("k results", "k সংখ্যক ফল"))],
       [ln("query", "db", "to", state="hot"), ln("filter", "db", "to", state="hot")],
       [("inside knn", "knn-এর ভেতরে"), ("inside knn", "knn-এর ভেতরে"), None]),

    st(("Counts", "গণনা"),
       ("Counts and sums go to a database", "গণনা আর যোগফল যায় ডেটাবেসে"),
       [("Counts, sums and joins are exact computations, not similarity problems. Use text-to-SQL, not similarity search.",
         "গণনা, যোগফল, জয়েন নির্ভুল হিসাব। এতে টেক্সট-টু-SQL লাগে, সিমিলারিটি সার্চ নয়।"),
        ("Spider is the standard test for text-to-SQL: 10,181 questions over 200 databases.",
         "Spider টেক্সট-টু-SQL-এর প্রচলিত পরীক্ষা: ২০০টি ডেটাবেসে ১০,১৮১টি প্রশ্ন।")],
       [sh("user", "hot", ("counts, sums, joins", "গণনা, যোগফল, জয়েন")), sh("sql", "hot"), sh("db", "hot", ("exact", "নির্ভুল"))],
       [ln("user", "sql", "to", state="hot"), ln("sql", "db", "to", state="hot")],
       [None, None, ("exact", "নির্ভুল")],
       note=("tip", "Its test databases have schemas the model never saw.",
             "এর টেস্ট ডেটাবেসের স্কিমা মডেল আগে দেখেনি।")),

    st(("Safe SQL", "নিরাপদ SQL"),
       ("Check the SQL it writes", "যে SQL লেখে তা যাচাই করুন"),
       [("Give the model the schema, and check generated SQL: read-only credentials, allow-listed tables, row limits.",
         "মডেলকে স্কিমা দিন, আর বানানো SQL যাচাই করুন: রিড-অনলি অধিকার, অনুমোদিত টেবিল, সারির সীমা।"),
        ("Log every query. Read-only credentials are a login that can read data but cannot change it.",
         "প্রতিটি কুয়েরি লগ করুন। রিড-অনলি অধিকার মানে এমন লগইন, যা দিয়ে ডেটা পড়া যায় কিন্তু বদলানো যায় না।")],
       [sh("sql", "hot"), sh("ro", "hot", ("read, not change", "পড়া যায়, বদলানো যায় না")), sh("db", "hot")],
       [ln("sql", "ro", "to", state="hot"), ln("ro", "db", "to", state="hot")],
       [None, None, None]),

    st(("Remember", "মনে রাখুন"),
       ("Remember", "মনে রাখুন"),
       [("An LLM can write the filter or the query, so check it before it runs.",
         "LLM ফিল্টার বা কুয়েরি লিখতে পারে, তাই চালানোর আগে যাচাই করুন।")],
       [sh("llm", "hot"), sh("check", "hot"), sh("db", "hot")],
       [ln("llm", "check", "to", state="hot"), ln("check", "db", "to", state="hot")],
       [None, None, None],
       points=[("Check the filter the LLM writes against the schema before it reaches the database.",
                "LLM-এর লেখা ফিল্টার ডেটাবেসে যাওয়ার আগে স্কিমার সাথে মিলিয়ে যাচাই করুন।"),
               ("Counts, sums and joins are exact computations. Use text-to-SQL, not similarity search.",
                "গণনা, যোগফল, জয়েন নির্ভুল হিসাব। এতে টেক্সট-টু-SQL লাগে, সিমিলারিটি সার্চ নয়।"),
               ("In Elasticsearch, put the filter inside knn so the number of results you asked for (k) comes back.",
                "Elasticsearch-এ ফিল্টার knn-এর ভেতরে দিলে যতগুলো ফল চেয়েছেন (k), ততগুলোই আসে।"),
               ("Check generated SQL: read-only credentials, allow-listed tables, row limits. Log every query.",
                "বানানো SQL যাচাই করুন: রিড-অনলি অধিকার, অনুমোদিত টেবিল, সারির সীমা। প্রতিটি কুয়েরি লগ করুন।")]),
]

WALK = walk(760, 320, NODES, METRICS, CAPTION, STEPS)
