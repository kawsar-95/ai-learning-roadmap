"""Resolve the requested creators to channels and list their Shorts and Videos tabs (flat, serial, polite).

usage: python3 crawl_channels.py [slug ...]   (no slug: every creator in CREATORS below)

Writes ch_<slug>_shorts.tsv and ch_<slug>_videos.tsv (id, views, duration, title) and channels_resolved.json.
A handle guess is accepted only if the channel's own title matches the expected name, so a wrong guess cannot
silently list someone else's videos. One YouTube request stream at a time; 4-7 s between tabs.
"""
import json
import os
import random
import re
import subprocess
import sys
import time

from _paths import WORK, YT_DLP  # noqa: E402
D = str(WORK)
YT = YT_DLP

CREATORS = [
    ("colemedin", r"cole medin", ["@ColeMedin"]),
    ("aijason", r"ai jason", ["@AIJasonZ", "@aijason", "@AIJason"]),
    ("krishnaik", r"^krish naik$", ["@krishnaik06"]),
    ("davidondrej", r"david ondrej", ["@DavidOndrej", "@DavidOndrejOfficial", "@davidondrej1"]),
    ("nana", r"techworld with nana", ["@TechWorldwithNana"]),
    ("automata", r"automata learning lab", ["@automatalearninglab", "@AutomataLearningLab"]),
    ("deeplearningai", r"deeplearning\.?ai", ["@Deeplearningai", "@DeepLearningAI"]),
]
LIMIT = {"videos": 1500, "shorts": 600}
FMT = "%(id)s\t%(view_count)s\t%(duration)s\t%(title)s"


def run(args, timeout=600):
    r = subprocess.run([YT, "--no-warnings", "--flat-playlist", *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def resolve(rx, handles):
    for h in handles:
        rc, out, err = run([f"https://www.youtube.com/{h}/videos", "-I", "1:1", "--print", "%(playlist_title)s"], 120)
        title = out.strip().splitlines()[0] if out.strip() else ""
        print(f"  try {h}: rc={rc} title={title!r}", flush=True)
        if rc == 0 and re.search(rx, re.sub(r" - (Videos|Shorts)$", "", title), re.I):
            return h, re.sub(r" - (Videos|Shorts)$", "", title)
        time.sleep(2)
    return None, None


ONLY = set(sys.argv[1:])  # optional: crawl only these creators
CHANNELS_JSON = os.path.join(D, "channels_resolved.json")
resolved = json.load(open(CHANNELS_JSON)) if ONLY and os.path.exists(CHANNELS_JSON) else {}
for slug, rx, handles in CREATORS:
    if ONLY and slug not in ONLY:
        continue
    print(f"== {slug}", flush=True)
    h, name = resolve(rx, handles)
    if not h:
        resolved[slug] = {"error": "no handle matched", "tried": handles}
        print("  UNRESOLVED", flush=True)
        continue
    info = {"handle": h, "channel": name}
    for tab in ("videos", "shorts"):
        time.sleep(random.uniform(4, 7))
        rc, out, err = run([f"https://www.youtube.com/{h}/{tab}", "--playlist-end", str(LIMIT[tab]), "--sleep-requests", "0.7", "--print", FMT])
        rows = [l for l in out.splitlines() if l.count("\t") >= 3]
        open(os.path.join(D, f"ch_{slug}_{tab}.tsv"), "w", encoding="utf-8").write("\n".join(rows) + ("\n" if rows else ""))
        info[tab] = len(rows)
        if rc != 0 and not rows:
            info[f"{tab}_error"] = (err or "").strip().splitlines()[-1][:160] if err.strip() else f"rc={rc}"
        print(f"  {tab}: {len(rows)} rows (rc={rc})", flush=True)
    resolved[slug] = info
    json.dump(resolved, open(os.path.join(D, "channels_resolved.json"), "w"), indent=1)
json.dump(resolved, open(os.path.join(D, "channels_resolved.json"), "w"), indent=1)
print("DONE", json.dumps(resolved), flush=True)
