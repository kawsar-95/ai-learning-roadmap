from dsl import S, analogy, code, h, note, p, table, ul

SECTIONS = [
    S(
        "testing",
        "Testing",
        "Knowing a change is safe before your users find out: many fast tests for the logic, and a few slow ones for everything else.",
        "টেস্টিং",
        "ব্যবহারকারীরা টের পাওয়ার আগেই জানা যে একটা পরিবর্তন নিরাপদ: লজিকের জন্য অনেক দ্রুত টেস্ট, আর বাকি সবকিছুর জন্য অল্প কয়েকটা ধীর টেস্ট।",
        [
            h("Is this change safe?"),
            p("A checkout service applies discount codes. It reads and writes an orders database, charges cards through an outside payment provider, and asks another team's inventory service whether items are in stock. A developer changes how discounts are rounded, clicks through a few purchases on a test server, and everything looks fine."),
            h("Clicking around misses things"),
            p("Nobody tried three items at 9.99 with a 10% code. The basket costs 29.97, and 10% off should give 26.973, so 26.97. The new code rounds the discount down to 2.99 first, so customers pay 26.98: one cent too much, on thousands of orders, until support notices. Manual checks are slow, so they run rarely, and they cover only what someone thought to try."),
            h("Unit tests: one piece, in isolation"),
            p("A unit test calls one function with known inputs and checks the result. It needs no database and no network, so it runs in milliseconds, and a project can run thousands of them on every change. The rounding case becomes a test that fails the moment anyone breaks it again:"),
            code("python", """from decimal import Decimal, ROUND_HALF_UP

def total(prices, discount_pct):
    subtotal = sum(prices, Decimal("0"))
    discount = subtotal * Decimal(discount_pct) / 100
    return (subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def test_ten_percent_off_three_items():
    assert total([Decimal("9.99")] * 3, 10) == Decimal("26.97")"""),
            note("good", "<strong>Write the test for a bug before you fix it.</strong> Watch it fail, fix the code, and watch it pass. That bug cannot come back unnoticed."),
            h("Test doubles stand in for the rest"),
            p("Checkout cannot run without its neighbours, so tests swap them for test doubles. Fowler lists five kinds [[fowler-mocks]]:"),
            ul(
                "<strong>Dummy:</strong> passed around but never used, to fill a parameter list.",
                "<strong>Fake:</strong> a working implementation with a shortcut, such as an in-memory database.",
                "<strong>Stub:</strong> gives canned answers, such as a payment provider that always says \"approved\".",
                "<strong>Spy:</strong> a stub that also records how it was called.",
                "<strong>Mock:</strong> pre-programmed with the calls it expects, such as \"charge this card exactly once\".",
            ),
            p("The catch: a double knows only what you told it. If the real provider renames a field, every unit test still passes."),
            h("Integration tests: the real neighbours"),
            p("Integration tests check how your application works with the parts that live outside it [[practical-pyramid]]: here, a real database, started fresh in a container for the test run. They catch SQL mistakes, broken migrations and mismatched types. They take seconds instead of milliseconds. The payment provider stays stubbed, since you cannot charge real cards, but a separate, smaller suite can call its sandbox."),
            h("Contract tests: between teams"),
            p("Checkout depends on the inventory service, which another team deploys on its own schedule. If they rename <code>in_stock</code> to <code>available</code>, checkout's stub never notices. With consumer-driven contract tests, the consumer writes tests for all the data it needs from an interface and publishes them, and the providing team runs them [[practical-pyramid]]. Fowler's article describes these expectations being enforced automatically with each build [[cdc-contracts]], so a breaking change fails in the provider's build before it ships. Pact is a common tool for writing them [[practical-pyramid]]."),
            h("End-to-end tests: the whole journey"),
            p("An end-to-end test drives the real system as a user would: open the shop in a browser, add three items, enter a code, pay with a sandbox card, see the confirmation. It is the only test that proves everything works together, and it is the slowest and most fragile. End-to-end tests are notoriously flaky and often fail for reasons that have nothing to do with the code under test [[practical-pyramid]]. Keep a small number of them for the journeys that make money."),
            h("The test pyramid"),
            p("Together the suites form a test pyramid: many more low-level unit tests than broad tests that drive the whole application through its user interface [[fowler-pyramid]]. Lower layers are fast, precise and cheap; higher ones are slow but closer to what users do. Push each check as low as it can go. An upside-down pyramid, mostly end-to-end tests, means slow runs, random failures, and a team that stops trusting a red build."),
            h("Case: the flaky test"),
            p("One end-to-end test fails about one run in twenty. It waits a fixed two seconds for the confirmation email, and sometimes the email takes three. People learn to press \"re-run\", and when a real bug turns the test red, they re-run that too. This happens at scale: Google reported that about 1.5% of all its test results were flaky, and that almost 16% of its tests had some level of flakiness [[google-flaky]]."),
            p("Fix the cause: wait for a condition instead of a fixed time, control the clock, give each test its own data, and never depend on the order of tests. Track flaky tests and fix or remove them. Google's tooling quarantines a test whose flakiness is too high, which takes it off the critical path and files a bug for the developers [[google-flaky]]."),
            h("Testing for load and for failure"),
            p("Correct is not enough. A load test sends production-like traffic to a copy of the system and finds where latency turns upward (section 2) before users do. Failure tests break things on purpose, such as stopping a database replica or slowing the payment provider, and check that timeouts, retries and failover work as designed (section 26). Chaos engineering takes this into production: it is the discipline of experimenting on a system to build confidence that it can withstand turbulent conditions in production [[chaos-principles]]."),
            table(
                ["Kind", "Checks", "Speed", "How many"],
                ["Unit", "One function, doubles for the rest", "Milliseconds", "Thousands"],
                ["Integration", "Your code with a real database or queue", "Seconds", "Hundreds"],
                ["Contract", "The API between two teams", "Seconds", "One set per consumer"],
                ["End-to-end", "A whole user journey", "Minutes", "A handful"],
            ),
        ],
        [
            p("A car factory does not test a new car only by driving it once around the car park. It tests every bolt and part on a bench, which is quick and cheap, so thousands of these tests run every day. It checks that the engine fits the real gearbox. It agrees on exact measurements with the company that supplies the tyres, so a change on their side is caught at their factory. And finally a driver takes a few finished cars on a full test drive."),
            p("A test that sometimes fails for no reason is like a warning light that flickers: soon everyone ignores it, including on the day it is right."),
            analogy("<strong>A car factory.</strong> Bench tests on parts are unit tests, the engine with the real gearbox is an integration test, the agreed tyre measurements are a contract, and the test drive is an end-to-end test."),
        ],
        [
            p("Checkout সার্ভিস ডিসকাউন্ট কোড প্রয়োগ করে। ডেভেলপার রাউন্ড করার নিয়ম বদলে হাতে কয়েকটা কেনাকাটা করে দেখলেন, সব ঠিক। কিন্তু কেউ ৯.৯৯-এর তিনটি আইটেমে ১০% কোড চেষ্টা করেনি: দাম হওয়া উচিত ২৬.৯৭, অথচ নতুন কোড ডিসকাউন্ট আগে নিচে রাউন্ড করে, তাই গ্রাহক দেন ২৬.৯৮। হাতে পরীক্ষা ধীর, তাই কম হয়, আর শুধু যা কারও মাথায় আসে সেটুকুই দেখে।"),
            p("Unit test একটা function-কে জানা input দিয়ে ডেকে ফল যাচাই করে; ডেটাবেস বা নেটওয়ার্ক লাগে না, তাই মিলিসেকেন্ডে চলে, আর হাজার হাজার চালানো যায়। বাকি অংশের জায়গায় বসে test double: fake (যেমন মেমরির ডেটাবেস), stub (সবসময় “approved” বলা পেমেন্ট), mock (যাচাই করে কার্ড ঠিক একবার চার্জ হলো কি না)। কিন্তু double শুধু ততটুকুই জানে যা আপনি শিখিয়েছেন। Integration test আসল ডেটাবেসের সাথে চলে, তাই SQL-এর ভুল আর ভাঙা migration ধরা পড়ে। Contract test-এ consumer লিখে রাখে সে interface থেকে কী চায়, আর provider টিম নিজের build-এ সেটা চালায়, তাই ভাঙা পরিবর্তন ship হওয়ার আগেই ধরা পড়ে। End-to-end test পুরো যাত্রাটা ব্রাউজারে চালায়: সবচেয়ে বাস্তব, কিন্তু সবচেয়ে ধীর আর ভঙ্গুর।"),
            p("তাই test pyramid: নিচে অনেক unit test, মাঝে কিছু integration আর contract test, ওপরে অল্প কয়েকটা end-to-end। যে টেস্ট কারণ ছাড়াই মাঝে মাঝে ফেল করে (flaky), সেটা দলকে ব্যর্থতা উপেক্ষা করতে শেখায়; Google জানিয়েছিল তাদের প্রায় ১৬% টেস্টে কিছু না কিছু flakiness ছিল। নির্দিষ্ট সময় অপেক্ষা না করে শর্তের জন্য অপেক্ষা করুন, প্রতিটি টেস্টকে নিজের ডেটা দিন, আর flaky টেস্ট ঠিক করুন বা সরান। শুধু সঠিকতা নয়: load test দেখায় কত চাপে latency বাড়ে, আর failure test ইচ্ছা করে কিছু ভেঙে দেখে timeout, retry আর failover ঠিকমতো কাজ করে কি না।"),
            analogy("<strong>গাড়ির কারখানা:</strong> বেঞ্চে প্রতিটি যন্ত্রাংশের পরীক্ষা হলো unit test, আসল গিয়ারবক্সে ইঞ্জিন বসিয়ে দেখা integration test, টায়ার কোম্পানির সাথে ঠিক করা মাপ হলো contract, আর শেষে পুরো টেস্ট ড্রাইভ হলো end-to-end test।"),
        ],
    ),
    S(
        "cicd",
        "CI/CD & Deployments",
        "Getting every change to production quickly and safely, and back out again just as quickly when something goes wrong.",
        "CI/CD আর ডিপ্লয়মেন্ট",
        "প্রতিটি পরিবর্তন দ্রুত আর নিরাপদে production-এ পৌঁছানো, আর কিছু ভুল হলে ঠিক ততটাই দ্রুত ফিরিয়ে নেওয়া।",
        [
            h("Shipping by hand"),
            p("Once a week, on Friday evening, a developer builds the app on a laptop, copies it to the production server and restarts it. A week of everyone's changes goes out at once, so when something breaks, nobody knows which change did it. Big, rare releases feel safe and are the opposite: the more that changes at once, the harder it is to test, to find the cause, and to undo."),
            h("\"It works on my machine\""),
            p("This Friday the laptop had a newer library than the server, and the app will not start. Nobody recorded exactly what was running before, so even going back is guesswork, and the site stays down for hours. Builds that depend on one person's machine, and deploys that nobody can repeat exactly, turn every release into an experiment."),
            h("Continuous integration"),
            p("In continuous integration, everyone pushes small commits to the mainline at least every day, every push triggers an automated build that also runs the tests, and a broken build is fixed immediately [[fowler-ci]]. The build runs on a clean machine, so nothing depends on anyone's laptop, and the mainline always builds and passes. Keep it fast: Fowler calls the XP guideline of a ten-minute build perfectly within reason for most projects [[fowler-ci]]. A slow pipeline makes people batch their changes again."),
            h("Build once, promote the same artifact"),
            p("A deployment pipeline breaks the build into stages, each giving more confidence than the last. Usually the first stage compiles the code and provides the binaries for the later stages [[fowler-pipeline]]. Today that binary is often a container image tagged with its commit, such as <code>checkout:3f9c2a1</code>. That exact image is tested, deployed to staging and then to production; only the configuration differs between environments. Never rebuild for production, because a rebuild can pull different dependencies and produce a program you never tested."),
            h("Continuous delivery"),
            p("Continuous delivery means building software so that it can be released to production at any time [[fowler-cd]]. Every image that passes is deployed to staging automatically, smoke tests check the main journeys there, and production is one button press away. Continuous deployment goes further: every change that passes the pipeline goes into production automatically [[fowler-cd]]. Deploying daily keeps each deploy small: a few changes, easy to review, easy to blame and easy to undo."),
            h("Blue-green: switch, don't replace"),
            p("Blue-green deployment keeps two production environments, as identical as possible. Blue is live. The new version is deployed to green and tested there, then the router switches all incoming requests to green. If anything goes wrong, you switch the router back to blue, which is still running, untouched [[fowler-bluegreen]]. The cost is double capacity during a release; a rolling deploy (section 5) is cheaper but slower to undo."),
            h("Canary: try it on a few users first"),
            p("A canary release rolls the change out to a small subset of users before rolling it out to everyone. If there is a problem, users are rerouted back to the old version [[fowler-canary]]. The pipeline compares the canary's error rate and latency with the old version (section 27), rolls back automatically if it is worse, and otherwise grows the share step by step, for example 5%, 25%, 50%, 100%."),
            h("Case: the migration that breaks the old version"),
            p("A release renames a column from <code>name</code> to <code>full_name</code>. The migration runs and the new version is happy, but during the rollout most servers still run the old version, which asks for <code>name</code> and fails. During any deploy, old and new code run side by side against the same database, so every schema change must work with both."),
            p("The fix is parallel change, also called expand and contract: it splits a backward-incompatible change into three phases, expand, migrate and contract [[fowler-parallel]]. Each phase is its own deploy:"),
            code("sql", """-- 1. expand: add the new column; the app writes both columns
ALTER TABLE users ADD COLUMN full_name text;

-- 2. migrate: backfill old rows, then switch reads to full_name
UPDATE users SET full_name = name WHERE full_name IS NULL;

-- 3. contract: once no running version reads name, drop it
ALTER TABLE users DROP COLUMN name;"""),
            h("Feature flags: deploy is not release"),
            p("A new checkout page can be merged and deployed weeks before launch, switched off. A feature flag decides per request who sees it: first the team, then 1% of users, then everyone. Turning it off is a setting, not a deploy, so a problem is fixed in seconds. Release toggles like this are the most common way to separate feature release from code deployment [[feature-toggles]]. They are debt too: Hodgson notes that release toggles should generally not stay much longer than a week or two [[feature-toggles]]. Remove each one once its feature is fully out."),
            h("Measure the delivery itself"),
            p("DORA's software delivery metrics measure how well a team ships. Throughput is measured by change lead time, deployment frequency and failed deployment recovery time, and instability by the change fail rate and the deployment rework rate [[dora]]. DORA's research has repeatedly found that speed and stability are not trade-offs: top performers do well on all of these metrics, and low performers do poorly [[dora]]. Small, frequent, reversible changes improve both."),
        ],
        [
            p("A restaurant does not invent a new dish on opening night. Each change to the recipe is tasted in the kitchen right away, so a mistake is caught while it is small: that is continuous integration. The dish that passes the tasting is the one that is served, not a fresh copy cooked by someone else."),
            p("A new menu item goes first to a few tables, and the waiters watch the faces: a canary. The chef can keep a dish ready in the kitchen but off the menu until the day it launches, which is a feature flag. And a sign of a good kitchen is that it changes things often and rarely sends back a bad plate."),
            analogy("<strong>A restaurant kitchen.</strong> Tasting every change is CI, serving the dish that was tasted is \"build once\", the few trial tables are a canary, and the dish kept off the menu is behind a feature flag."),
        ],
        [
            p("হাতে ship করা মানে সপ্তাহে একদিন কারও ল্যাপটপে build করে সার্ভারে কপি করা। সপ্তাহের সব পরিবর্তন একসাথে যায়, তাই কিছু ভাঙলে কেউ জানে না কোনটা দায়ী; আর ল্যাপটপের লাইব্রেরি সার্ভারের থেকে আলাদা হলে অ্যাপ চালুই হয় না। বড় আর বিরল রিলিজ নিরাপদ মনে হয়, আসলে উল্টো।"),
            p("Continuous integration-এ সবাই ছোট ছোট পরিবর্তন দিনে অন্তত একবার মূল branch-এ পাঠায়, প্রতিটি push-এ একটা পরিষ্কার মেশিনে build আর test চলে, আর ভাঙা build সাথে সাথে ঠিক করা হয়। একবার build করে একটা অপরিবর্তনীয় artifact (যেমন commit দিয়ে চিহ্নিত container image) বানান, আর সেটাই staging আর production-এ পাঠান; production-এর জন্য আবার build করবেন না। Continuous delivery মানে সফটওয়্যার যেকোনো সময় production-এ যাওয়ার জন্য তৈরি; continuous deployment-এ প্রতিটি সফল পরিবর্তন নিজে থেকেই production-এ চলে যায়।"),
            p("নিরাপদে রিলিজের উপায়: blue-green-এ দুটো একই রকম environment থাকে, আর router এক ধাক্কায় নতুনটায় ট্রাফিক পাঠায়; সমস্যা হলে আবার পুরনোটায় ফিরিয়ে আনে। Canary-তে নতুন ভার্সন আগে অল্প কিছু ব্যবহারকারী পায়। ডেটাবেসের কলাম বদলাতে expand and contract করুন: নতুন কলাম যোগ, পুরনো সারি পূরণ, পড়া বদল, আর শেষে পুরনো কলাম মোছা, কারণ rollout-এর সময় পুরনো আর নতুন কোড একসাথে চলে। Feature flag deploy আর release আলাদা করে: কোড সার্ভারে আছে, কিন্তু কে দেখবে তা একটা সেটিং ঠিক করে। আর DORA-র metrics দিয়ে delivery মাপুন; তাদের গবেষণা বলে গতি আর স্থিতিশীলতা একে অপরের বিপরীত নয়।"),
            analogy("<strong>রেস্টুরেন্টের রান্নাঘর:</strong> প্রতিটি পরিবর্তন সাথে সাথে চেখে দেখা হলো CI, যেটা চাখা হয়েছে ঠিক সেটাই পরিবেশন করা “build once”, অল্প কয়েকটা টেবিলে আগে নতুন পদ দেওয়া canary, আর মেনুর বাইরে তৈরি রাখা পদ হলো feature flag।"),
        ],
    ),
]
