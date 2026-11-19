"""Build src/content/system-design.json (and its interview entry) from the Python files in this folder.

Usage: python3 scripts/system-design/build.py [--check] [repo_dir]   (default: the repository this file is in)

Validates before writing: citations, sources, inline HTML allowlist, heading ids,
lesson order, titles and walk-through step names (must match course-outline.json),
quiz rules, and the language rules of the walk-throughs.

--check writes nothing. It builds the two files in memory and exits 1 when they differ
from the ones on disk, so a hand edit of the JSON, or an edit of these sources that was
not followed by a build, is caught.

SHIKI_WORK  a directory with `shiki` installed, for a code block that is not in
            code-cache.json yet (default: <temp dir>/system-design-shiki). See README.md.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import importlib
import tempfile

from sources import SOURCES

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
CHECK = "--check" in sys.argv[1:]
REPO = os.path.abspath(ARGS[0]) if ARGS else os.path.dirname(os.path.dirname(HERE))
SHIKI_WORK = os.environ.get("SHIKI_WORK") or os.path.join(tempfile.gettempdir(), "system-design-shiki")
# What the build reads of the course: the order of the lessons, each lesson's title and length,
# and the short name of each of its steps. Nothing else of the course is kept here.
COURSE = json.load(open(os.path.join(HERE, "course-outline.json"), encoding="utf-8"))
COURSE_URL = "https://designed-to-scale.vercel.app/"

MODULE_NAMES = {
    "foundations": ("Foundations", "ভিত্তি"),
    "scaling": ("Scaling", "স্কেলিং"),
    "data": ("Data and storage", "ডেটা ও স্টোরেজ"),
    "communication": ("Communication", "যোগাযোগ"),
    "reliability": ("Reliability", "নির্ভরযোগ্যতা"),
    "architecture": ("Architecture", "আর্কিটেকচার"),
    "security": ("Security", "নিরাপত্তা"),
    "shipping": ("Shipping", "শিপিং"),
    "design": ("Whole systems", "পুরো সিস্টেম"),
}

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn(n) -> str:
    return str(n).translate(BN_DIGITS)


# The checks every walk-through passes, in any Part, are shared with scripts/walkthroughs.
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "walkthroughs"))
import check as walkcheck  # noqa: E402
from check import BANGLA, TAG, check_inline, err, errors, outside_code, plain_numbers, strip_html  # noqa: E402


# ---------------------------------------------------------------- citations
order: list[str] = []


def cite(text: str, where: str, allow: bool = True) -> str:
    def repl(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        out = []
        for key in keys:
            if key not in SOURCES:
                err(f"{where}: unknown source key {key}")
                continue
            if not allow:
                err(f"{where}: citation in a voice that has none ({key})")
            if key not in order:
                order.append(key)
            n = order.index(key) + 1
            out.append(f'<a class="cite" href="#src{n}">[{n}]</a>')
        return "".join(out)

    return re.sub(r"\[\[([a-z0-9,\s-]+)\]\]", repl, text)


def walk(blocks, fn, where):
    """Apply fn to every inline string of a block list, in reading order."""
    out = []
    for i, b in enumerate(blocks):
        b = dict(b)
        w = f"{where}[{i}]"
        t = b["type"]
        if t in ("paragraph", "heading"):
            b["html"] = fn(b["html"], w)
        elif t == "list":
            b["items"] = [fn(x, w) for x in b["items"]]
        elif t == "table":
            b["headers"] = [fn(x, w) for x in b["headers"]]
            b["rows"] = [[fn(x, w) for x in r] for r in b["rows"]]
        elif t in ("callout", "analogy"):
            b["blocks"] = walk(b["blocks"], fn, w)
        elif t == "code":
            pass
        else:
            err(f"{w}: unexpected block type {t}")
        out.append(b)
    return out


# ---------------------------------------------------------------- headings
def slug(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", TAG.sub("", text).lower().replace("&amp;", " "))
    stop = {"a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "it", "is", "its", "with"}
    kept = [w for w in words if w not in stop] or words
    return "-".join(kept[:5])


# ---------------------------------------------------------------- code
CODE_CACHE = os.path.join(HERE, "code-cache.json")


def highlight(blocks_by_ref):
    cache = json.load(open(CODE_CACHE)) if os.path.exists(CODE_CACHE) else {}
    todo = []
    for b in blocks_by_ref:
        k = hashlib.sha1((b["lang"] + "\0" + b["code"]).encode()).hexdigest()
        if k not in cache:
            todo.append((k, b))
    if todo:
        with tempfile.TemporaryDirectory() as tmp:
            inp = os.path.join(tmp, "code-in.json")
            outp = os.path.join(tmp, "code-out.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump([{"lang": b["lang"], "code": b["code"]} for _, b in todo], f)
            if not os.path.isdir(os.path.join(SHIKI_WORK, "node_modules", "shiki")):
                sys.exit(f"{len(todo)} code block(s) are not in code-cache.json, and shiki is not installed in {SHIKI_WORK}.\n"
                         f"Install it there (see README.md), or set SHIKI_WORK to a directory that has it.")
            # The script goes in on stdin, so `import "shiki"` resolves from the working directory.
            with open(os.path.join(HERE, "highlight.mjs"), encoding="utf-8") as script:
                subprocess.run(["node", "--input-type=module", "-"], stdin=script, cwd=SHIKI_WORK, check=True,
                               env={**os.environ, "HL_IN": inp, "HL_OUT": outp})
            with open(outp, encoding="utf-8") as f:
                rendered = json.load(f)
        for (k, _), html in zip(todo, rendered):
            cache[k] = html
        if not CHECK:
            with open(CODE_CACHE, "w", encoding="utf-8") as f:
                json.dump(cache, f)
    for b in blocks_by_ref:
        b["html"] = cache[hashlib.sha1((b["lang"] + "\0" + b["code"]).encode()).hexdigest()]


def find_code(blocks):
    for b in blocks:
        if b["type"] == "code":
            yield b
        elif b["type"] in ("callout", "analogy"):
            yield from find_code(b["blocks"])


# ---------------------------------------------------------------- words
def words(blocks) -> int:
    t = json.dumps(blocks, ensure_ascii=False)
    t = TAG.sub(" ", t)
    return len(re.findall(r"[\w\u0980-\u09FF]+", t))


# ---------------------------------------------------------------- "Start here" boxes
# The same rules as tests/basics-content.test.ts in a tree that has the boxes.
LIMITS = {"en": {"idea": 45, "term": 8, "meaning": 30, "point": 25},
          "bn": {"idea": 60, "term": 10, "meaning": 40, "point": 35}}


def block_text(b) -> str:
    t = b["type"]
    if t in ("paragraph", "heading"):
        return strip_html(b["html"])
    if t == "list":
        return " ".join(strip_html(x) for x in b["items"])
    if t == "code":
        return b["code"]
    if t in ("callout", "analogy"):
        return " ".join(block_text(c) for c in b["blocks"])
    if t == "table":
        return " ".join(strip_html(x) for x in b["headers"] + [c for r in b["rows"] for c in r])
    return ""


def check_basics(sec: dict, box: dict, where: str):
    raw = " ".join([sec["title"], strip_html(sec["sub"])] + [block_text(b) for b in sec["body"] + sec["layman"]])
    low = raw.lower()
    en, bnb = box["en"], box["bn"]
    if not (2 <= len(en["words"]) <= 8 and 2 <= len(en["remember"]) <= 5):
        err(f"{where}: needs 2-8 words and 2-5 points")
    if len(en["words"]) != len(bnb["words"]) or len(en["remember"]) != len(bnb["remember"]):
        err(f"{where}: en and bn differ in the number of words or points")
    for lang, text in (("en", en), ("bn", bnb)):
        fields = [("idea", text["idea"])] + [f for w in text["words"] for f in (("term", w["term"]), ("meaning", w["meaning"]))]
        fields += [("point", x) for x in text["remember"]]
        for kind, html in fields:
            check_inline(html, f"{where}.{lang}.{kind}")
            if "<a" in html:
                err(f"{where}.{lang}.{kind}: a box has no links")
            n = len(strip_html(html).split())
            if n > LIMITS[lang][kind]:
                err(f"{where}.{lang}.{kind}: {n} words > {LIMITS[lang][kind]}: {html[:80]}")
            if lang == "en" and BANGLA.search(html):
                err(f"{where}.en.{kind}: Bangla in the English box")
            if lang == "bn":
                if kind != "term" and not BANGLA.search(outside_code(html)):
                    err(f"{where}.bn.{kind}: no Bangla: {html[:80]}")
                if plain_numbers(outside_code(html)):
                    err(f"{where}.bn.{kind}: Latin digits {plain_numbers(outside_code(html))}: {html[:80]}")
        idea = outside_code(text["idea"])
        if lang == "bn" and len(BANGLA.findall(idea)) < len(re.findall(r"[A-Za-z]", idea)):
            err(f"{where}.bn.idea: mostly Latin")
    for w in en["words"]:
        plain = strip_html(w["term"])
        stems = [re.sub(r"(ies|es|s)$", "", x) for x in re.split(r"[^a-z0-9]+", plain.lower()) if len(x) >= 4]
        abbrs = re.findall(r"\b[A-Z][A-Z0-9]+\b", plain)
        if not stems and not abbrs:
            continue
        if not (any(s in low for s in stems) or any(re.search(rf"\b{a}\b", raw) for a in abbrs)):
            err(f"{where}: term {plain!r} is not used in the section")


# ---------------------------------------------------------------- walk-throughs
def check_walk(w: dict, course: dict | None, where: str):
    """Part 18's own rule: the steps are the course lesson's steps, by number and by name. The rest is scripts/walkthroughs/check.py."""
    steps = w["steps"]
    if course and len(steps) != len(course["steps"]):
        err(f"{where}: {len(steps)} steps, the course lesson has {len(course['steps'])}")
    if course:
        for i, (st, short) in enumerate(zip(steps, course["steps"]), 1):
            if st["en"]["short"] != short:
                err(f"{where}.step{i}: short {st['en']['short']!r} is not the course's {short!r}")
    walkcheck.check_walk(w, where)


# ---------------------------------------------------------------- build
def main():
    sys.path.insert(0, HERE)
    import part
    names = ["m1", "m2", "m3", "m3b", "m4", "m5", "m6", "m7", "m8", "m9"]
    mods = [importlib.import_module(n) for n in names if os.path.exists(os.path.join(HERE, n + ".py"))]
    raw = [s for m in mods for s in m.SECTIONS]

    # "Start here" boxes go in only when the target tree's schema has them (a strict schema rejects extra keys).
    BASICS = {}
    for n in ("basics_a", "basics_b"):
        if os.path.exists(os.path.join(HERE, n + ".py")):
            BASICS.update(importlib.import_module(n).BASICS)
    schema_src = open(os.path.join(REPO, "src", "lib", "content-schema.ts"), encoding="utf-8").read()
    with_basics = "BasicsSchema" in schema_src
    with_walks = "WalkthroughSchema" in schema_src
    if not (with_basics and with_walks):
        # Leaving the boxes or the walk-throughs out would quietly drop part of the Part.
        sys.exit(f"{REPO}/src/lib/content-schema.ts has no BasicsSchema or no WalkthroughSchema: nothing built")
    # The walk-throughs are in walks_*.py, one file for each group of lessons.
    WALKS = {}
    for n in sorted(f[:-3] for f in os.listdir(HERE) if re.fullmatch(r"walks_\w+\.py", f)):
        WALKS.update(importlib.import_module(n).WALKS)
    print(f"{len(WALKS)} walk-throughs written")

    course_order = [(m["id"], lid) for m in COURSE["modules"] for lid in m["lessons"]]
    lessons = COURSE["lessons"]
    if [s["lesson"] for s in raw] != [lid for _, lid in course_order]:
        got = [s["lesson"] for s in raw]
        err(f"lesson order differs from the course: {len(got)} written; first mismatch at "
            f"{next((i for i, (a, b) in enumerate(zip(got, [l for _, l in course_order])) if a != b), len(got))}")

    module_of = {lid: mid for mid, lid in course_order}
    module_count = {}
    for mid, _ in course_order:
        module_count[mid] = module_count.get(mid, 0) + 1
    seen_in_module: dict[str, int] = {}

    sections = []
    heading_ids = set()
    for i, s in enumerate(raw, 1):
        sid = f"s{i}"
        lid = s["lesson"]
        mid = module_of.get(lid, "?")
        seen_in_module[mid] = seen_in_module.get(mid, 0) + 1
        k, n = seen_in_module[mid], module_count.get(mid, 0)
        en_mod, bn_mod = MODULE_NAMES.get(mid, ("?", "?"))
        course = lessons.get(lid)
        if course and s["title"] != course["title"]:
            err(f"{sid}: title {s['title']!r} differs from the course title {course['title']!r}")

        sub = f"<strong>{en_mod}, lesson {k} of {n}.</strong> " + cite(s["sub"], f"{sid}.sub")
        bn_sub = f"<strong>{bn_mod}, লেসন {bn(k)}/{bn(n)}।</strong> " + cite(s["bn"]["sub"], f"{sid}.bn.sub", allow=False)
        body = walk(s["body"], lambda t, w: cite(t, w), f"{sid}.body")
        layman = walk(s["layman"], lambda t, w: cite(t, w, allow=False), f"{sid}.layman")
        bangla = walk(s["bangla"], lambda t, w: cite(t, w, allow=False), f"{sid}.bangla")

        for blocks, voice in ((body, "body"), (layman, "layman"), (bangla, "bangla")):
            for b in blocks:
                if b["type"] == "heading":
                    hid = f"{sid}-{slug(b['html'])}"
                    if hid in heading_ids:
                        err(f"{sid}.{voice}: duplicate heading id {hid}")
                    heading_ids.add(hid)
                    b["id"] = hid
                    # keep the schema's key order: type, level, id, html
                    html = b.pop("html")
                    b["html"] = html
            if not blocks:
                err(f"{sid}: empty voice {voice}")

        steps = len(course["steps"]) if course else 0
        minutes = course["minutes"] if course else 0
        if with_walks and lid in WALKS:
            # The section has its own walk-through above the card: the card is the original.
            title = f"{s['title']} (original animated lesson)"
            note = (f"The original lesson by Dilum Sanjaya, as an animated diagram: {steps} steps, about {minutes} minutes. "
                    f"It is part of his free System Design course and opens on its own site.")
            note_bn = (f"Dilum Sanjaya-র মূল লেসন, অ্যানিমেটেড ডায়াগ্রামে: {bn(steps)}টি ধাপ, প্রায় {bn(minutes)} মিনিট। "
                       f"এটা তাঁর ফ্রি System Design কোর্সের অংশ, আর নিজের সাইটে খোলে।")
        else:
            title = f"{s['title']} (animated lesson)"
            note = (f"Step through this lesson as an animated diagram: {steps} steps, about {minutes} minutes. "
                    f"It is part of Dilum Sanjaya's free System Design course and opens on its own site.")
            note_bn = (f"এই লেসনটা অ্যানিমেটেড ডায়াগ্রামে ধাপে ধাপে দেখুন: {bn(steps)}টি ধাপ, প্রায় {bn(minutes)} মিনিট। "
                       f"এটা Dilum Sanjaya-র ফ্রি System Design কোর্সের অংশ, আর নিজের সাইটে খোলে।")
        embed = {
            "url": f"{COURSE_URL}#/{lid}/1",
            "title": title,
            "note": note,
            "noteBn": note_bn,
            "frame": False,
        }
        section = {
            "id": sid,
            "num": f"{i:02d}",
            "title": s["title"],
            "sub": sub,
            "bn": {"title": s["bn"]["title"], "sub": bn_sub},
        }
        if with_basics:
            if lid not in BASICS:
                err(f"{sid}: no Start here box for {lid}")
            else:
                section["basics"] = BASICS[lid]
        if with_walks and lid in WALKS:
            section["walkthrough"] = WALKS[lid]
            check_walk(WALKS[lid], course, f"{sid}.walkthrough")
        section.update({
            "body": body,
            "layman": layman,
            "bangla": bangla,
            "embeds": [embed],
        })
        if with_basics and "basics" in section:
            check_basics(section, section["basics"], f"{sid}.basics")
        sections.append(section)

    # inline checks everywhere
    for s in sections:
        sid = s["id"]
        check_inline(s["sub"], f"{sid}.sub")
        check_inline(s["bn"]["sub"], f"{sid}.bn.sub")
        for e in s["embeds"]:
            check_inline(e["note"], f"{sid}.embed.note")
            check_inline(e["noteBn"], f"{sid}.embed.noteBn")
        for voice in ("body", "layman", "bangla"):
            walk(s[voice], lambda t, w: (check_inline(t, w), t)[1], f"{sid}.{voice}")
        if "&" in s["bn"]["title"] or not s["bn"]["title"].strip():
            err(f"{sid}: bad bn title")

    lede = cite(part.LEDE, "lede")
    check_inline(lede, "lede")
    check_inline(part.BN["lede"], "bn.lede")

    # code
    code_blocks = [b for s in sections for v in ("body", "layman", "bangla") for b in find_code(s[v])]
    highlight(code_blocks)

    # sources: every listed source is cited, in order of first citation
    used = set(order)
    for key in SOURCES:
        if key not in used:
            print(f"note: source {key} is not cited (left out of the Part)")
    sources = [{"n": i + 1, "url": SOURCES[k][0], "text": SOURCES[k][1]} for i, k in enumerate(order)]

    # quiz
    quiz = part.QUIZ
    ids = [q["id"] for q in quiz]
    if len(quiz) != 5 or len(set(ids)) != 5:
        err("quiz must have 5 questions with unique ids")
    plain = re.compile(r"(?<![A-Za-z0-9_\-/.:#@%+])[0-9]+(?:[.,][0-9]+)*(?![A-Za-z0-9_\-/])")
    for q in quiz:
        texts = [q["bn"]["q"], q["bn"]["why"]] + (q["bn"].get("options") or [])
        for t in texts + [q["en"]["q"], q["en"]["why"]] + (q["en"].get("options") or []):
            if re.search(r"</?[a-zA-Z][^>]*>", t):
                err(f"quiz {q['id']}: HTML in quiz text")
        for t in texts:
            if plain.search(re.sub(r"<code[^>]*>.*?</code>", "", t)):  # the rule of tests/quiz-content.test.ts: Bangla digits, even in a version number
                err(f"quiz {q['id']}: Latin digits in Bangla text: {t}")
            if re.search(r"\b(Text|Topic)\b", t):
                err(f"quiz {q['id']}: Text/Topic in Bangla")
        if q["kind"] == "mcq":
            if len(q["en"]["options"]) != len(q["bn"]["options"]):
                err(f"quiz {q['id']}: option counts differ")
            if not 0 <= q["answer"] < len(q["en"]["options"]):
                err(f"quiz {q['id']}: bad answer index")
    if len({q["answer"] for q in quiz if q["kind"] == "mcq"}) < 2:
        err("quiz: every mcq answer is at the same option")

    topic = {
        "slug": "system-design",
        "title": part.TITLE,
        "tagline": part.TAGLINE,
        "lede": lede,
        "bn": part.BN,
        "sections": sections,
        "sources": sources,
        "quiz": quiz,
    }

    # interview
    lesson_to_sid = {s["lesson"]: f"s{i}" for i, s in enumerate(raw, 1)}
    interview_items = []
    for item in part.INTERVIEW:
        sid = lesson_to_sid.get(item["lesson"])
        if not sid:
            err(f"interview: unknown lesson {item['lesson']}")
        for lang in ("en", "bn"):
            for key in ("q", "a"):
                if re.search(r"</?[a-zA-Z][^>]*>", item[lang][key]):
                    err(f"interview {item['lesson']}: HTML in {lang}.{key}")
        interview_items.append({"section": sid, "en": item["en"], "bn": item["bn"]})
    if len(interview_items) != 3:
        err("interview: need exactly 3 items")

    if errors:
        print("\n".join("ERROR " + e for e in errors))
        print(f"{len(errors)} errors; nothing written")
        sys.exit(1)

    out = os.path.join(REPO, "src", "content", "system-design.json")
    system_text = json.dumps(topic, ensure_ascii=False, indent=2) + "\n"

    ipath = os.path.join(REPO, "src", "content", "interview.json")
    interview = json.load(open(ipath, encoding="utf-8"))
    interview["parts"] = [p_ for p_ in interview["parts"] if p_["topic"] != "system-design"]
    interview["parts"].append({"topic": "system-design", "items": interview_items})
    interview_text = json.dumps(interview, ensure_ascii=False, indent=2) + "\n"

    if CHECK:
        stale = [p_ for p_, text in ((out, system_text), (ipath, interview_text)) if open(p_, encoding="utf-8").read() != text]
        for p_ in stale:
            print(f"DIFFERS {os.path.relpath(p_, REPO)}: it is not what these sources build. Run build.py, or undo the edit.")
        print(f"{len(sections)} sections, {len(sources)} sources: " + ("the two files are up to date" if not stale else f"{len(stale)} of 2 files differ"))
        sys.exit(1 if stale else 0)

    for p_, text in ((out, system_text), (ipath, interview_text)):
        with open(p_, "w", encoding="utf-8") as f:
            f.write(text)

    tw = sum(words(s["body"]) for s in sections)
    lw = sum(words(s["layman"]) for s in sections)
    bw = sum(words(s["bangla"]) for s in sections)
    for s in sections:
        print(f"{s['id']:>4} {s['title'][:34]:34} tech {words(s['body']):4}  lay {words(s['layman']):4}  bn {words(s['bangla']):4}")
    print(f"{len(sections)} sections, {len(sources)} sources, words: tech {tw}, layman {lw}, bangla {bw}")
    print(f"wrote {out} ({os.path.getsize(out)} bytes) and the interview entry")


if __name__ == "__main__":
    main()
