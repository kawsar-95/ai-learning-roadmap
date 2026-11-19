"""The checks every walk-through must pass, in any Part.

Used by scripts/walkthroughs/build.py (Parts 1 to 17) and by Part 18's generator (scripts/system-design/build.py).
A defect is added to `errors` with `err(...)` and not raised, so one run names every defect, each with its step.
The layout sizes are the same as src/lib/walkthrough.ts, so a bad layout fails here and not in the browser.
"""
import math
import re

errors: list[str] = []


def err(msg: str):
    errors.append(msg)


# ---------------------------------------------------------------- inline HTML
TAG = re.compile(r"<[^>]*>")
ALLOWED = [
    re.compile(r"^</?(strong|em|code)>$"),
    re.compile(r"^<br\s*/?>$"),
    re.compile(r'^<a class="cite" href="#src\d+">$'),
    re.compile(r'^<a href="https?://[^"\s<>]+">$'),
    re.compile(r"^</a>$"),
]


def allowed_inline(html: str) -> bool:
    tags = TAG.findall(html)
    if not all(any(r.match(t) for r in ALLOWED) for t in tags):
        return False
    return "<" not in TAG.sub("", html)


def check_inline(html: str, where: str):
    if not allowed_inline(html):
        bad = [t for t in TAG.findall(html) if not any(r.match(t) for r in ALLOWED)]
        err(f"{where}: inline HTML outside the allowlist {bad[:3]} :: {html[:120]}")
    if "[[" in html or "]]" in html:
        err(f"{where}: unresolved citation :: {html[:120]}")
    if "&" in TAG.sub("", html).replace("&amp;", "").replace("&lt;", "").replace("&gt;", "").replace("&quot;", ""):
        err(f"{where}: bare & in inline HTML :: {html[:120]}")


def check_plain(text: str, where: str):
    """Step labels and titles are drawn as plain text: a bare & is right, and a tag or an entity would show literally."""
    if "<" in text or ">" in text or re.search(r"&(?:[a-zA-Z]+|#\d+);", text):
        err(f"{where}: plain text must not hold a tag or an entity :: {text[:120]}")



# ---------------------------------------------------------------- language
BANGLA = re.compile(r"[\u0980-\u09FF]")


def strip_html(html: str) -> str:
    return re.sub(r"&[a-z#0-9]+;", " ", TAG.sub("", html))


def outside_code(html: str) -> str:
    return strip_html(re.sub(r"<code>.*?</code>", " ", html))


def plain_numbers(text: str) -> list[str]:
    """Latin digits that the Bangla box must write in Bangla digits (a name or code word keeps them)."""
    found = []
    for m in re.finditer(r"[0-9]+(?:[.,][0-9]+)*", text):
        before, after = text[:m.start()], text[m.end():]
        if before and re.match(r"[A-Za-z0-9_\-/.:#@%+]", before[-1]):
            continue
        if after and re.match(r"[A-Za-z0-9_\-/]", after[0]):
            continue
        if re.search(r"[A-Za-z][\w.\-]*\s$", before):
            continue  # a version after a name, such as "Llama 3"
        found.append(m.group(0))
    return found



# ---------------------------------------------------------------- walk-through layout
# The same sizes as src/lib/walkthrough.ts, so a bad layout fails here, with the step named.
NODE_H = 56


def box_width(lines):
    longest = max([0] + [len(x) for x in lines])  # code points, like [...line].length
    return min(240, max(112, math.floor(52 + longest * 7.2 + 0.5)))


def node_lines(w, lang):
    lines = {n["id"]: [n["label"][lang]] for n in w["nodes"]}
    for st in w["steps"]:
        for s in st["show"]:
            if "sub" in s:
                lines[s["id"]].append(s["sub"][lang])
    return lines


def node_widths(w, lang):
    return {i: box_width(l) for i, l in node_lines(w, lang).items()}


def box_exit(b, tx, ty):
    dx, dy = tx - b["x"], ty - b["y"]
    if dx == 0 and dy == 0:
        return b["x"], b["y"]
    sx = math.inf if dx == 0 else b["w"] / 2 / abs(dx)
    sy = math.inf if dy == 0 else b["h"] / 2 / abs(dy)
    s = min(sx, sy)
    return b["x"] + dx * s, b["y"] + dy * s


def step_boxes(w, st, widths):
    """Where each box shown in a step is, and how big: {id: {x, y, w, h}}. A step can move a box with its own x and y."""
    by_id = {n["id"]: n for n in w["nodes"]}
    return {
        s["id"]: {"x": s.get("x", by_id[s["id"]]["x"]), "y": s.get("y", by_id[s["id"]]["y"]), "w": widths[s["id"]], "h": NODE_H}
        for s in st["show"]
    }


def check_layout(w, where):
    """Boxes fit and keep apart, no line runs through a third box, no line label sits on a box."""
    for lang in ("en", "bn"):
        widths = node_widths(w, lang)
        for nid, lines in node_lines(w, lang).items():
            longest = max(lines, key=len)
            if len(longest) > 32:  # the widest box (240) holds about 29 average characters, never 33+
                err(f"{where}.{nid}.{lang}: {longest!r} is too long for any box ({len(longest)} chars, at most 32)")
        for i, st in enumerate(w["steps"], 1):
            at = f"{where}.step{i}.{lang}"
            boxes = step_boxes(w, st, widths)
            for k, b in boxes.items():
                if b["x"] - b["w"] / 2 < 0 or b["x"] + b["w"] / 2 > w["width"]:
                    err(f"{at}: {k} is cut off left or right (x={b['x']}, w={b['w']})")
                if b["y"] - b["h"] / 2 - 9 < 0 or b["y"] + b["h"] / 2 > w["height"]:
                    err(f"{at}: {k} is cut off top or bottom (y={b['y']})")
            ks = list(boxes)
            for p in range(len(ks)):
                for q in range(p + 1, len(ks)):
                    a, b = boxes[ks[p]], boxes[ks[q]]
                    if not (abs(a["x"] - b["x"]) >= (a["w"] + b["w"]) / 2 + 8 or abs(a["y"] - b["y"]) >= (a["h"] + b["h"]) / 2 + 8):
                        err(f"{at}: {ks[p]} and {ks[q]} overlap")
            for l in st["links"]:
                if l["from"] not in boxes or l["to"] not in boxes:
                    continue
                a, b = boxes[l["from"]], boxes[l["to"]]
                x1, y1 = box_exit(a, b["x"], b["y"])
                x2, y2 = box_exit(b, a["x"], a["y"])
                for k, c in boxes.items():
                    if k in (l["from"], l["to"]):
                        continue
                    steps_n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 2))
                    for t in range(steps_n + 1):
                        px, py = x1 + (x2 - x1) * t / steps_n, y1 + (y2 - y1) * t / steps_n
                        if abs(px - c["x"]) < c["w"] / 2 + 4 and abs(py - c["y"]) < c["h"] / 2 + 4:
                            err(f"{at}: the line {l['from']} → {l['to']} runs through {k}")
                            break
                if "label" in l:
                    text = l["label"][lang]
                    lw, mx, my = 6.2 * len(text) + 8, (x1 + x2) / 2, (y1 + y2) / 2 - 8
                    seg = math.hypot(x2 - x1, y2 - y1)
                    if seg < lw + 40:
                        err(f"{at}: the label {text!r} of {l['from']} → {l['to']} needs a longer line ({seg:.0f}px visible, wants {lw + 40:.0f}px)")
                    if mx - lw / 2 < 0 or mx + lw / 2 > w["width"] or my - 12 < 0:
                        err(f"{at}: the label {text!r} of {l['from']} → {l['to']} leaves the diagram")
                    for k, c in boxes.items():
                        if abs(mx - c["x"]) < c["w"] / 2 + lw / 2 and abs((my - 4) - c["y"]) < c["h"] / 2 + 9:
                            err(f"{at}: the label {text!r} of {l['from']} → {l['to']} sits on {k}")


# ---------------------------------------------------------------- walk-throughs
def check_lang(lang: str, html: str, where: str, need_bangla: bool = False):
    if lang == "en" and BANGLA.search(html):
        err(f"{where}: Bangla in English text: {html[:80]}")
    if lang == "bn":
        if plain_numbers(outside_code(html)):
            err(f"{where}: Latin digits {plain_numbers(outside_code(html))}: {html[:80]}")
        if need_bangla and not BANGLA.search(outside_code(html)):
            err(f"{where}: no Bangla: {html[:80]}")


def check_walk(w: dict, where: str, kinds=None):
    """The rules of the walk-through schema that zod does not say clearly, plus the language and layout rules.

    `kinds` is the list of box kinds the site draws (WALK_NODE_KINDS in src/lib/content-schema.ts). With it, a
    misspelt kind is named here, with its box, and not by zod at `next build`.
    """
    steps = w["steps"]
    ids = {n["id"] for n in w["nodes"]}
    if kinds is not None:
        for n in w["nodes"]:
            if n["kind"] not in kinds:
                err(f"{where}: box {n['id']!r} has the unknown kind {n['kind']!r}")
    for n in w["nodes"]:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", n["id"]):
            err(f"{where}: node id {n['id']!r} must match [a-z][a-z0-9-]* (no underscores)")
    if len(ids) != len(w["nodes"]):
        err(f"{where}: duplicate node ids")
    if len(w["metrics"]) > 6:
        err(f"{where}: more than 6 readouts")
    for i, st in enumerate(steps, 1):
        for l in st["links"]:
            if "ms" in l and not (200 <= l["ms"] <= 10000):
                err(f"{where}.step{i}: dot time {l['ms']} ms is outside 200..10000")
    labels = [("node", n["label"]) for n in w["nodes"]] + [("metric", m) for m in w["metrics"]]
    if "caption" in w:
        labels.append(("caption", w["caption"]))
    for i, st in enumerate(steps, 1):
        at = f"{where}.step{i}"
        en, bnt = st["en"], st["bn"]
        for k in ("body", "changes", "points"):
            if len(en.get(k, [])) != len(bnt.get(k, [])):
                err(f"{at}: en and bn differ in {k}")
        if en.get("note", {}).get("kind") != bnt.get("note", {}).get("kind"):
            err(f"{at}: en and bn notes differ")
        if [c["sign"] for c in en.get("changes", [])] != [c["sign"] for c in bnt.get("changes", [])]:
            err(f"{at}: en and bn change signs differ")
        if len(st.get("values", [])) != len(w["metrics"]):
            err(f"{at}: needs one value per readout")
        shown = set()
        for s in st["show"]:
            if s["id"] not in ids or s["id"] in shown:
                err(f"{at}: bad or repeated node {s['id']}")
            shown.add(s["id"])
            if "sub" in s:
                labels.append((f"step{i}.sub", s["sub"]))
        for l in st["links"]:
            if l["from"] not in shown or l["to"] not in shown:
                err(f"{at}: link {l['from']} → {l['to']} joins a hidden box")
            if "label" in l:
                labels.append((f"step{i}.link", l["label"]))
        for v in st.get("values", []):
            if isinstance(v, dict):
                labels.append((f"step{i}.value", v))
            elif isinstance(v, str) and BANGLA.search(v):
                err(f"{at}: a shared value has Bangla: {v}")
        for lang, t in (("en", en), ("bn", bnt)):
            if len(t["short"]) > 24:
                err(f"{at}.{lang}: step label too long: {t['short']}")
            fields = [("short", t["short"], False), ("title", t["title"], True)] + [("body", x, True) for x in t["body"]]
            if "note" in t:
                fields.append(("note", t["note"]["html"], True))
            fields += [("change", c["html"], False) for c in t.get("changes", [])]
            fields += [("point", p, True) for p in t.get("points", [])]
            for kind, html, need in fields:
                (check_plain if kind in ("short", "title") else check_inline)(html, f"{at}.{lang}.{kind}")
                if "<a" in html:
                    err(f"{at}.{lang}.{kind}: a walk-through step has no links")
                check_lang(lang, html, f"{at}.{lang}.{kind}", need_bangla=need)
    for kind, b in labels:
        check_lang("en", b["en"], f"{where}.{kind}.en")
        check_lang("bn", b["bn"], f"{where}.{kind}.bn")
    if all(s["id"] in ids for st in steps for s in st["show"]):
        check_layout(w, where)
