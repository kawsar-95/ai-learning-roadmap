"""Verify every section key used by picks.py (KodeKloud + other creators + moves) against the real section ids/titles in src/content/*.json.
Prints, per key, the real title; flags keys that do not exist. Also prints the id->title map of every topic that has picks, so a mismatch is obvious."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import REPO  # noqa: E402
import picks  # noqa: E402
import candidates_creators as cr  # noqa: E402

root = str(REPO / "src" / "content")
keys = list(dict.fromkeys(list(picks.KK) + list(cr.DRAFT2) + list(picks.ADD2)))
topics = {}
bad = 0
for k in keys:
    topic, sid = k.split("/")
    if topic not in topics:
        d = json.load(open(os.path.join(root, f"{topic}.json"), encoding="utf-8"))
        topics[topic] = {s["id"]: s.get("title", "") for s in d["sections"]}
    title = topics[topic].get(sid)
    if title is None:
        bad += 1
    print(f"{'MISSING' if title is None else 'ok     '} {k:<44} {str(title)[:70]}")
print(f"\n{bad} missing of {len(keys)}")
for t in ("rag-knowledge-systems", "agents-and-agentic-systems", "llm-fundamentals", "prompt-engineering", "context-engineering", "fine-tuning-roadmap"):
    print(f"\n{t}: " + " | ".join(f"{sid}={title[:26]}" for sid, title in topics.get(t, {}).items()))
