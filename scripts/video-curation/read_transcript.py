"""Print the full transcript (or a window of it) of given clip ids.
usage: python3 read_transcript.py <id> [<id> ...] [--max 3500]
"""
import json
import os
import sys

from _paths import WORK  # noqa: E402
D = str(WORK)
args = sys.argv[1:]
mx = 3500
if "--max" in args:
    i = args.index("--max")
    mx = int(args[i + 1])
    args = args[:i] + args[i + 2:]
for vid in args:
    p = f"{D}/deep/{vid}.json"
    if not os.path.exists(p):
        print(f"\n### {vid}: not fetched")
        continue
    d = json.load(open(p))
    t = d["transcript"]
    dur = int(float(d["duration"] or 0))
    print(f"\n### {vid} | {d['title']} | {dur // 60}:{dur % 60:02d} | views {d.get('view_count')} | chars {len(t)}")
    desc = (d.get("description") or "").replace("\n", " ")
    print(f"DESC: {desc[:260]}")
    if len(t) <= mx:
        print(t)
    else:
        h = mx // 2
        print(t[:h], "\n   [...]\n", t[-h:])
