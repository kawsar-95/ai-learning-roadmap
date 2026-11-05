"""Polite deep check: metadata + original-language auto-captions for a list of ids, one at a time.

usage: python3 fetch_details.py <ids.txt> [--jitter 4 7]
Caches per id under aie/deep/<id>.json (metadata subset + transcript text). Skips ids already cached.
Stops at the first 'not a bot' / 'Sign in' challenge and exits 3. One yt-dlp call per id, serial, 4-7 s apart.
"""
import json
import os
import random
import subprocess
import sys
import time

from _paths import WORK, YT_DLP  # noqa: E402
HERE = str(WORK)
YT = YT_DLP
DEEP = os.path.join(HERE, "deep")
SUBS = os.path.join(HERE, "subs")
os.makedirs(DEEP, exist_ok=True)
os.makedirs(SUBS, exist_ok=True)

KEEP = ["id", "title", "channel", "duration", "aspect_ratio", "playable_in_embed", "availability", "live_status",
        "view_count", "like_count", "channel_follower_count", "language", "description", "chapters", "upload_date"]


def transcript(vid):
    for lang in ("en-orig", "en"):
        p = os.path.join(SUBS, f"{vid}.{lang}.json3")
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            text = " ".join("".join(s.get("utf8", "") for s in e.get("segs", [])) for e in d.get("events", []) if e.get("segs"))
            return lang, " ".join(text.split())
    return None, ""


def deep(vid, shorts):
    url = f"https://www.youtube.com/shorts/{vid}" if shorts else f"https://www.youtube.com/watch?v={vid}"
    # en-orig only: the original-language auto-caption (the spoken language). Asking for `en` as well doubles the
    # timedtext requests, and the second one is what drew HTTP 429.
    cmd = [YT, "-j", "--no-simulate", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en-orig",
           "--sub-format", "json3", "--no-warnings", "-o", os.path.join(SUBS, "%(id)s.%(ext)s"), url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    err = (r.stderr or "") + (r.stdout if r.returncode else "")
    if "not a bot" in err or "Sign in" in err:
        return "CHALLENGE", err[:300]
    if "429" in err and "Too Many Requests" in err:
        return "THROTTLED", err[:200]
    if r.returncode != 0 or not r.stdout.strip():
        return "ERROR", err[:300]
    info = json.loads(r.stdout.splitlines()[-1])
    out = {k: info.get(k) for k in KEEP}
    out["auto_caption_langs"] = sorted((info.get("automatic_captions") or {}).keys())[:6]
    lang, text = transcript(vid)
    out["caption_track"] = lang
    out["transcript"] = text
    return "OK", out


def main(argv):
    ids = [l.split()[0] for l in open(os.path.join(HERE, argv[1]), encoding="utf-8") if l.strip() and not l.startswith("#")]
    lo, hi = (4.0, 7.0)
    if "--jitter" in argv:
        i = argv.index("--jitter")
        lo, hi = float(argv[i + 1]), float(argv[i + 2])
    todo = [v for v in ids if not os.path.exists(os.path.join(DEEP, f"{v.partition(':')[0]}.json"))]
    print(f"{len(ids)} ids, {len(todo)} to fetch", flush=True)
    throttled = 0
    for n, spec in enumerate(todo, 1):
        vid, _, kind = spec.partition(":")
        shorts = kind != "video"
        status, data = deep(vid, shorts)
        if status == "CHALLENGE":
            print(f"STOP at {vid}: YouTube asked for a sign-in challenge. {data}", flush=True)
            return 3
        if status == "THROTTLED":
            throttled += 1
            print(f"[{n}/{len(todo)}] {vid} HTTP 429 (throttle #{throttled}); backing off 90 s", flush=True)
            if throttled >= 4:
                print("STOP: four throttles in this run; wait a while before asking again.", flush=True)
                return 4
            time.sleep(90)
            continue
        throttled = 0
        if status == "ERROR":
            print(f"[{n}/{len(todo)}] {vid} ERROR {data[:160]!r}", flush=True)
        else:
            json.dump(data, open(os.path.join(DEEP, f"{vid}.json"), "w", encoding="utf-8"), ensure_ascii=False)
            print(f"[{n}/{len(todo)}] {vid} {data['duration']}s ar={data['aspect_ratio']} embed={data['playable_in_embed']} "
                  f"cap={data['caption_track']} chars={len(data['transcript'])} | {data['title'][:60]}", flush=True)
        time.sleep(random.uniform(lo, hi))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
