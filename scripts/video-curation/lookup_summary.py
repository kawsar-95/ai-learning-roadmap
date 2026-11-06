"""Summarize lookups.json against the picks and the gap lists: oEmbed statuses, Shorts that are not Shorts, title mismatches vs the crawl."""
import collections
import json
import os
import re

from _paths import WORK  # noqa: E402
D = str(WORK)
lk = json.load(open(f"{D}/lookups.json", encoding="utf-8"))
picks = json.load(open(f"{D}/final_picks.json", encoding="utf-8"))
print("oEmbed statuses:", dict(collections.Counter(v["oembed_status"] for v in lk.values())))
print("shorts_status among Shorts looked up:", dict(collections.Counter(v["shorts_status"] for v in lk.values() if v["shorts_status"] is not None)))
bad = 0
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
for sec, items in picks.items():
    for it in items:
        r = lk.get(it["id"])
        problems = []
        if not r:
            problems.append("not looked up")
        else:
            if r["oembed_status"] != 200:
                problems.append(f"oembed {r['oembed_status']}")
            if it["kind"] == "S" and r["shorts_status"] != 200:
                problems.append(f"listed as a Short, /shorts/ answered {r['shorts_status']}")
            if r["title"] and norm(it["title"]) not in norm(r["title"]) and norm(r["title"]) not in norm(it["title"]):
                problems.append(f"title differs: crawl {it['title'][:40]!r} vs oEmbed {r['title'][:40]!r}")
        if problems:
            bad += 1
            print(f"  {sec} {it['id']} ({it['creator']}): {'; '.join(problems)}")
print(f"{bad} picks with a problem out of {sum(len(v) for v in picks.values())}")
# gap lists
for fn in ("gap_resolved.json", "gap2_resolved.json"):
    g = json.load(open(f"{D}/{fn}", encoding="utf-8"))
    miss = [(t, h["id"], h["title"][:50], lk.get(h["id"], {}).get("oembed_status"), lk.get(h["id"], {}).get("shorts_status")) for t, hs in g.items() for h in hs
            if lk.get(h["id"], {}).get("oembed_status") != 200 or (not h["long"] and lk.get(h["id"], {}).get("shorts_status") != 200)]
    print(fn, "unverified:", miss)
