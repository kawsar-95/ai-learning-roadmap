"""Fetch every source and check that its page contains the phrases it is cited for.

Usage: python3 check_sources.py [key ...]
Caches page text in ./cache/<key>.txt; delete a file to refetch it.
"""
import concurrent.futures as cf
import html
import os
import re
import subprocess
import sys

import requests

from sources import SOURCES

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")


def norm(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u00ad", "").replace("\ufb01", "fi").replace("\ufb02", "fl")
    text = re.sub(r"-\s*\n\s*", "-", text)
    return re.sub(r"\s+", " ", text).lower()


def html_text(raw: str) -> str:
    # Blogger keeps the post body in <script type='text/template'>; keep that text.
    raw = re.sub(r"(?is)<script[^>]*type=['\"]text/template['\"][^>]*>(.*?)</script>", r" \1 ", raw)
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return html.unescape(raw)


def fetch(key: str):
    url = SOURCES[key][0]
    path = os.path.join(CACHE, key + ".txt")
    if os.path.exists(path):
        return key, "cached", url, open(path, encoding="utf-8").read()
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en"}, timeout=40, allow_redirects=True)
    except Exception as exc:  # noqa: BLE001
        return key, f"ERR {type(exc).__name__}", url, ""
    status = f"{r.status_code}"
    final = r.url
    ctype = r.headers.get("content-type", "")
    if "pdf" in ctype or r.content[:4] == b"%PDF":
        pdf = path[:-4] + ".pdf"
        open(pdf, "wb").write(r.content)
        text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    else:
        try:
            raw = r.content.decode("utf-8")  # many servers omit the charset; requests then guesses Latin-1
        except UnicodeDecodeError:
            raw = r.text
        text = html_text(raw)
    if r.status_code == 200 and len(text) > 500:
        open(path, "w", encoding="utf-8").write(text)
    return key, status + ("" if final == url else f" -> {final}"), url, text


def main():
    keys = sys.argv[1:] or list(SOURCES)
    bad = 0
    with cf.ThreadPoolExecutor(12) as pool:
        for key, status, url, text in pool.map(fetch, keys):
            body = norm(text)
            missing = [p for p in SOURCES[key][2] if norm(p) not in body]
            ok = (status.startswith("200") or status.startswith("cached")) and not missing and (len(body) > 500 or key == "dts")
            if not ok:
                bad += 1
                print(f"FAIL {key}: {status} len={len(body)} missing={missing} {url}")
            elif "->" in status:
                print(f"ok   {key}: {status}")
    print(f"{len(keys) - bad}/{len(keys)} ok")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
