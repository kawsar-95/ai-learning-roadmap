#!/usr/bin/env python3
"""Writes one plain-text file for each section of Part 18, for a person who checks the text.

Each file holds what a reader sees for the section, English and Bangla side by side:
the title and intro, the Technical, Layman's and Bangla voices, the Start here box,
and the whole walk-through (every step, both languages). One more file holds the
Part's lede and quiz. Nothing in it needs the site to be built.

Usage: python3 review_packets.py [system-design.json] [out-dir]
Defaults: src/content/system-design.json, and ./review-packets next to this file.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "src", "content", "system-design.json")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "review-packets")
os.makedirs(out, exist_ok=True)
d = json.load(open(src, encoding="utf-8"))


def plain(h) -> str:
    h = re.sub(r"<code>(.*?)</code>", r"`\1`", h, flags=re.S)
    h = re.sub(r"</?(?:p|li|ul|ol|br|div|tr)[^>]*>", " ", h)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def blocks(bs, indent="") -> list[str]:
    lines = []
    for b in bs:
        t = b["type"]
        if t == "heading":
            lines.append(f"{indent}## {plain(b['html'])}")
        elif t == "paragraph":
            lines.append(f"{indent}{plain(b['html'])}")
        elif t == "list":
            for i, it in enumerate(b["items"], 1):
                lines.append(f"{indent}{i}. {plain(it)}" if b.get("ordered") else f"{indent}- {plain(it)}")
        elif t == "table":
            lines.append(indent + " | ".join(plain(h) for h in b["headers"]))
            lines += [indent + " | ".join(plain(c) for c in row) for row in b["rows"]]
        elif t in ("callout", "analogy"):
            lines.append(f"{indent}[{t}{' ' + b['variant'] if b.get('variant') else ''}]")
            lines += blocks(b["blocks"], indent + "  ")
        elif t == "code":
            lines.append(f"{indent}```{b['lang']}\n{b['code']}\n```")
    return lines


def walk_lines(w) -> list[str]:
    nodes = {n["id"]: n for n in w["nodes"]}
    lab = lambda i: f"{nodes[i]['label']['en']} | {nodes[i]['label']['bn']}"
    out_lines = ["Boxes of the diagram (English | Bangla):"] + [f"  {n['id']}: {lab(n['id'])}" for n in w["nodes"]]
    out_lines.append("Readout labels: " + "; ".join(f"{m['en']} | {m['bn']}" for m in w["metrics"]))
    if w.get("caption"):
        out_lines.append(f"Caption: {w['caption']['en']} | {w['caption']['bn']}")
    for i, st in enumerate(w["steps"], 1):
        out_lines.append(f"\n--- Walk-through step {i} ---")
        for lang in ("en", "bn"):
            t = st[lang]
            tag = lang.upper()
            out_lines.append(f"{tag} short: {t['short']}")
            out_lines.append(f"{tag} title: {t['title']}")
            for k, p in enumerate(t["body"], 1):
                out_lines.append(f"{tag} body {k}: {plain(p)}")
            if t.get("note"):
                out_lines.append(f"{tag} note ({t['note']['kind']}): {plain(t['note']['html'])}")
            for c in t.get("changes", []):
                out_lines.append(f"{tag} change [{c['sign']}]: {plain(c['html'])}")
            for p in t.get("points", []):
                out_lines.append(f"{tag} point: {plain(p)}")
        subs = [f"{s['id']}: {s['sub']['en']} | {s['sub']['bn']}" for s in st["show"] if s.get("sub")]
        if subs:
            out_lines.append("Box sub-lines (English | Bangla): " + "; ".join(subs))
        links = [f"{l['from']}->{l['to']}: {l['label']['en']} | {l['label']['bn']}" for l in st["links"] if l.get("label")]
        if links:
            out_lines.append("Arrow labels (English | Bangla): " + "; ".join(links))
        vals = []
        for m, v in zip(w["metrics"], st.get("values") or []):
            if v is None:
                continue
            vals.append(f"{m['en']}: {v['en']} | {v['bn']}" if isinstance(v, dict) else f"{m['en']}: {v}")
        if vals:
            out_lines.append("Readouts (English | Bangla): " + "; ".join(vals))
    return out_lines


for s in d["sections"]:
    lines = [f"SECTION {s['id']} of Part 18 (System Design)", ""]
    lines += [f"EN title: {s['title']}", f"BN title: {s['bn']['title']}", f"EN intro: {plain(s['sub'])}", f"BN intro: {plain(s['bn']['sub'])}", ""]
    lines += ["=== EN: Technical voice ==="] + blocks(s["body"])
    lines += ["", "=== EN: Layman's voice ==="] + blocks(s["layman"])
    lines += ["", "=== BN: Bangla voice ==="] + blocks(s["bangla"])
    for lang in ("en", "bn"):
        b = s["basics"][lang]
        lines += ["", f"=== {lang.upper()}: Start here box ===", f"idea: {plain(b['idea'])}"]
        lines += [f"word: {plain(w['term'])} = {plain(w['meaning'])}" for w in b["words"]]
        lines += [f"remember: {plain(r)}" for r in b["remember"]]
    lines += ["", "=== WALK-THROUGH (both languages, every step) ==="] + walk_lines(s["walkthrough"])
    with open(os.path.join(out, f"{s['id']}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

part = ["PART 18 (System Design): front matter and quiz", ""]
part += [f"EN title: {d['title']}", f"BN title: {d['bn']['title']}", f"EN tagline: {plain(d.get('tagline', ''))}", f"BN tagline: {plain(d['bn'].get('tagline', ''))}"]
part += [f"EN lede: {plain(d['lede'])}", f"BN lede: {plain(d['bn']['lede'])}", "", "=== Quiz (both languages) ==="]
for q in d["quiz"]:
    part.append(f"\nQuestion {q['id']} ({q['kind']}), correct answer: {q['answer']}")
    for lang in ("en", "bn"):
        part.append(f"{lang.upper()}: " + json.dumps(q[lang], ensure_ascii=False))
with open(os.path.join(out, "part.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(part) + "\n")
print(f"wrote {len(d['sections']) + 1} files to {os.path.abspath(out)}")
