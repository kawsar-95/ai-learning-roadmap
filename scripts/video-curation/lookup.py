"""Polite lookup of oEmbed (title, channel, status) and the /shorts/ status for a list of ids. Resumable.

usage: python3 lookup.py <ids.txt>        (ids as in pool_ids.txt: 'id' for a Short, 'id:video' for a long video)
Writes/extends lookups.json: {id: {oembed_status, title, author, shorts_status}}.
A control id (a long, stable video) must redirect on /shorts/ first; if it answers 200 nothing is judged.
One request at a time, 0.8-1.6 s apart, stops at the first HTTP 429. No cookies, no login.
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from _paths import WORK  # noqa: E402
D = str(WORK)
OUT = os.path.join(D, "lookups.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CONTROL = "dQw4w9WgXcQ"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class Throttled(Exception):
    pass


def shorts_status(vid):
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        return opener.open(req, timeout=25).status
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise Throttled()
        return e.code


def oembed(vid):
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
            d = json.load(r)
            return 200, d.get("title"), d.get("author_name")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise Throttled()
        return e.code, None, None


def main(argv):
    specs = [l.strip() for l in open(os.path.join(D, argv[1]), encoding="utf-8") if l.strip() and not l.startswith("#")]
    have = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [s for s in specs if s.partition(":")[0] not in have or have[s.partition(":")[0]].get("oembed_status") in (None, 429, 0)]
    print(f"{len(specs)} ids, {len(todo)} to look up", flush=True)
    try:
        control = shorts_status(CONTROL)
        if not 300 <= control < 400:
            print(f"CANNOT CHECK: control answered HTTP {control}")
            return 2
        for n, spec in enumerate(todo, 1):
            vid, _, kind = spec.partition(":")
            code, title, author = oembed(vid)
            row = {"oembed_status": code, "title": title, "author": author, "shorts_status": None}
            if kind != "video":
                st = shorts_status(vid)
                if 300 <= st < 400:
                    time.sleep(3)
                    st = shorts_status(vid)
                row["shorts_status"] = st
            have[vid] = row
            json.dump(have, open(OUT, "w"), ensure_ascii=False, indent=1)
            print(f"[{n}/{len(todo)}] {vid} oembed={code} shorts={row['shorts_status']} | {author} | {(title or '')[:60]}", flush=True)
            time.sleep(random.uniform(0.8, 1.6))
    except Throttled:
        print("STOPPED: HTTP 429. Wait a while before asking again.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
