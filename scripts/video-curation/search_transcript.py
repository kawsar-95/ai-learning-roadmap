"""Show the context around regex matches in a clip's transcript.
usage: python3 search_transcript.py <id> <regex> [--w 120] [--n 6]
"""
import json
import os
import re
import sys

from _paths import WORK  # noqa: E402
D = str(WORK)
vid, pat = sys.argv[1], sys.argv[2]
w = int(sys.argv[sys.argv.index("--w") + 1]) if "--w" in sys.argv else 120
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 6
d = json.load(open(f"{D}/deep/{vid}.json"))
t = d["transcript"]
print(f"### {vid} | {d['title']} | chars {len(t)}")
shown = 0
for m in re.finditer(pat, t, re.I):
    s, e = max(0, m.start() - w), min(len(t), m.end() + w)
    pos = round(100 * m.start() / max(1, len(t)))
    print(f"  @{pos:>3}%  ...{t[s:e]}...")
    shown += 1
    if shown >= n:
        break
if not shown:
    print("  (no match)")
