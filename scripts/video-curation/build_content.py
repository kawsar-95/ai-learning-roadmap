#!/usr/bin/env python3
"""Write the verified picks into src/content/*.json.

usage: python3 build_content.py            dry run: verify everything and print what would change
       python3 build_content.py --write    apply (refuses if any pick failed verification)

Inputs (all produced by earlier steps, none typed by hand):
  final_picks.json  section -> picks (id, kind S|V, creator)       from picks.py
  lookups.json      id -> oEmbed status/title/author + /shorts/ status   from lookup.py
  probe.jsonl       one line per id: {id, duration, playing | error}     from the IFrame-API probe
  deep/<id>.json    yt-dlp metadata (duration) as a second source for the length
Rules: oEmbed must answer 200; the player must not report an error; a Short needs /shorts/<id> = 200 and <= 180 s;
the stored title is storedTitle(oEmbed title) from src/lib/video-check.ts (run through node, so data and code agree);
the channel is oEmbed's author_name; an id that is already anywhere on the site is skipped, never duplicated.
"""
import glob
import json
import os
import subprocess
import sys

from _paths import REPO, SCRIPTS, WORK  # noqa: E402
ROOT = str(REPO)
AIE = str(WORK)
CONTENT = os.path.join(ROOT, "src", "content")
MAX_SHORT = 180


def load_jsonl(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("{"):
                row = json.loads(line)
                out[row["id"]] = row
    return out


def stored_titles(titles):
    r = subprocess.run(["node", "--disable-warning=MODULE_TYPELESS_PACKAGE_JSON", str(SCRIPTS / "stored_titles.mjs")],
                       input=json.dumps(titles), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def site_ids():
    ids = {}
    for f in glob.glob(os.path.join(CONTENT, "*.json")):
        for s in json.load(open(f, encoding="utf-8")).get("sections", []):
            for v in s.get("videos", []) or []:
                ids[v["id"]] = os.path.basename(f)
    return ids


def verify(picks, lookups, probe):
    """Return (video objects per section, problems, warnings)."""
    existing = site_ids()
    flat = [(sec, p) for sec, items in picks.items() for p in items]
    titles = stored_titles([lookups.get(p["id"], {}).get("title") or "" for _, p in flat])
    out, problems, warnings = {}, [], []
    for (sec, p), title in zip(flat, titles):
        vid, lk, pr = p["id"], lookups.get(p["id"]), probe.get(p["id"])
        tag = f"{sec} {vid} ({p['creator']}: {p['title'][:48]})"
        if vid in existing:
            warnings.append(f"SKIP already on the site ({existing[vid]}): {tag}")
            continue
        if not lk or lk.get("oembed_status") != 200:
            problems.append(f"oEmbed {lk and lk.get('oembed_status')}: {tag}")
            continue
        if not pr or "error" in pr or not pr.get("duration"):
            problems.append(f"player {pr and (pr.get('error') or 'no duration')}: {tag}")
            continue
        if not pr.get("playing"):
            warnings.append(f"player did not reach 'playing' (state {pr.get('state')}): {tag}")
        seconds = round(pr["duration"])
        deep_p = os.path.join(AIE, "deep", f"{vid}.json")
        if os.path.exists(deep_p):
            dd = json.load(open(deep_p, encoding="utf-8")).get("duration")
            if dd and abs(dd - seconds) > 2:
                warnings.append(f"length differs: player {seconds}s vs yt-dlp {dd}s: {tag}")
        if not title or "#" in title or title != title.strip():
            problems.append(f"bad stored title {title!r}: {tag}")
            continue
        video = {"id": vid, "title": title, "channel": lk["author"], "lang": "en"}
        if p["kind"] == "S":
            if lk.get("shorts_status") != 200:
                problems.append(f"listed as a Short but /shorts/ answered {lk.get('shorts_status')}: {tag}")
                continue
            if seconds > MAX_SHORT:
                problems.append(f"Short is {seconds}s (> {MAX_SHORT}): {tag}")
                continue
            video["format"] = "short"
        video["seconds"] = seconds
        out.setdefault(sec, []).append(video)
    return out, problems, warnings


def put_videos(section, new):
    """Return the section with the new videos appended; `videos` sits before `practice`, after everything else."""
    have = list(section.get("videos") or [])
    merged = have + new
    out, placed = {}, False
    for k, v in section.items():
        if k == "videos":
            out[k] = merged
            placed = True
            continue
        if k == "practice" and not placed:
            out["videos"] = merged
            placed = True
        out[k] = v
    if not placed:
        out["videos"] = merged
    return out


def write_topic(path, adds, apply):
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
    roundtrip = json.dumps(data, indent=2, ensure_ascii=False) + "\n" == raw
    secs = {s["id"]: i for i, s in enumerate(data["sections"])}
    for sid in adds:
        if sid not in secs:
            raise SystemExit(f"{os.path.basename(path)}: no section {sid}")
    if roundtrip:
        for sid, new in adds.items():
            i = secs[sid]
            data["sections"][i] = put_videos(data["sections"][i], new)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        text = raw
        for sid, new in adds.items():
            if data["sections"][secs[sid]].get("videos"):
                raise SystemExit(f"{os.path.basename(path)}: {sid} already has videos; the hand-formatted insert only handles a section without them")
            start = text.index(f'\n      "id": "{sid}",')
            marker = "\n      ]\n    }"
            at = text.index(marker, start)
            block = json.dumps(new, indent=2, ensure_ascii=False).split("\n")
            block = "\n".join([block[0]] + ["      " + ln for ln in block[1:]])
            text = text[:at] + '\n      ],\n      "videos": ' + block + "\n    }" + text[at + len(marker):]
    after = json.loads(text)  # must still parse
    for sid, new in adds.items():
        got = after["sections"][secs[sid]]["videos"]
        assert got[-len(new):] == new, f"{path} {sid}: the new videos are not at the end"
    if apply:
        open(path, "w", encoding="utf-8").write(text)
    return "round-trip" if roundtrip else "textual insert"


def main(argv):
    apply = "--write" in argv
    picks = json.load(open(os.path.join(AIE, "final_picks.json"), encoding="utf-8"))
    lookups = json.load(open(os.path.join(AIE, "lookups.json"), encoding="utf-8"))
    probe = load_jsonl(os.path.join(AIE, "probe.jsonl"))
    out, problems, warnings = verify(picks, lookups, probe)
    for w in warnings:
        print("WARN", w)
    for p in problems:
        print("FAIL", p)
    by_file = {}
    for sec, vids in out.items():
        topic, sid = sec.split("/")
        by_file.setdefault(topic, {})[sid] = vids
    total = 0
    for topic, adds in by_file.items():
        mode = write_topic(os.path.join(CONTENT, f"{topic}.json"), adds, apply and not problems)
        n = sum(len(v) for v in adds.values())
        total += n
        print(f"{'wrote' if apply and not problems else 'would write'} {n:>3} videos into {topic}.json ({mode}; sections {', '.join(adds)})")
    print(f"total {total} videos; {len(problems)} failures, {len(warnings)} warnings")
    if problems:
        print("nothing written: fix the failures first" if apply else "dry run only")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
