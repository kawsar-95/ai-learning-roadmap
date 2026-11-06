"""Catalog of the site's sections and existing videos (read-only).

Writes aie/catalog.json: {sections: [{topic, part, sid, num, title, sub, nvideos, nembeds}], videos: {id: [topic/sid, ...]}}
and prints a compact outline. Run from anywhere.
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

from _paths import REPO as _REPO, WORK  # noqa: E402
REPO = str(_REPO)
OUT = str(WORK / "catalog.json")

# TOPIC_ORDER from src/lib/topics.ts (parsed, not retyped)
ts = open(f"{REPO}/src/lib/topics.ts", encoding="utf-8").read()
order = re.search(r"TOPIC_ORDER: readonly string\[\] = \[(.*?)\];", ts, re.S).group(1)
order = re.findall(r'"([^"]+)"', order)

strip = lambda s: re.sub(r"<[^>]+>", "", s or "")
sections, videos = [], defaultdict(list)
for part, slug in enumerate(order, 1):
    d = json.load(open(f"{REPO}/src/content/{slug}.json", encoding="utf-8"))
    for s in d["sections"]:
        vids = s.get("videos", [])
        for v in vids:
            videos[v["id"]].append(f"{slug}/{s['id']}")
        sections.append({
            "topic": slug, "part": part, "sid": s["id"], "num": s["num"], "title": s["title"],
            "sub": strip(s["sub"]), "nvideos": len(vids), "nembeds": len(s.get("embeds", [])),
            "videos": [(v["id"], v["channel"], v["title"], v["lang"]) for v in vids],
        })

json.dump({"order": order, "sections": sections, "videos": videos}, open(OUT, "w"), ensure_ascii=False, indent=1)

print("TOPIC_ORDER:", len(order), order)
print("sections:", len(sections), "| videos total:", sum(len(v) for v in videos.values()), "| unique ids:", len(videos))
dups = {k: v for k, v in videos.items() if len(v) > 1}
print("ids used in more than one section:", len(dups))
for k, v in list(dups.items())[:10]:
    print("  ", k, v)
ch = Counter(c for s in sections for (_, c, _, _) in s["videos"])
print("KodeKloud already:", [(s["topic"], s["sid"], t) for s in sections for (i, c, t, l) in s["videos"] if "kodekloud" in c.lower()])
print()
for s in sections:
    print(f"P{s['part']:>2} {s['topic'][:22]:<22} {s['sid']:<12} v={s['nvideos']} | {s['title'][:70]}")
