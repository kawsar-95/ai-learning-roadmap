#!/usr/bin/env python3
"""Writes course-outline.json from the course's lesson data.

Usage: python3 extract_outline.py <lessons.json>

build.py keeps only this much of Dilum Sanjaya's course (https://designed-to-scale.vercel.app/):
the modules and the order of their lessons, and for each lesson its title, its length in minutes
and the short name of each step. That is all the Part follows the course in. The lessons' own text,
figures and code are not copied, so <lessons.json> itself is not committed. It is the `modules`
and `lessons` of the course's data, and the lesson `steps` carry a `short` each.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
course = json.load(open(sys.argv[1], encoding="utf-8"))
by_id = {lesson["id"]: lesson for lesson in course["lessons"]}
outline = {
    "source": "https://designed-to-scale.vercel.app/ by Dilum Sanjaya: lesson order, titles, lengths and step names only",
    "modules": [{"id": m["id"], "lessons": [ref["id"] for ref in m["lessons"]]} for m in course["modules"]],
    "lessons": {
        lid: {"title": l["title"], "minutes": l["minutes"], "steps": [s["short"] for s in l["steps"]]}
        for lid, l in by_id.items()
    },
}
with open(os.path.join(HERE, "course-outline.json"), "w", encoding="utf-8") as f:
    json.dump(outline, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(f"{len(outline['modules'])} modules, {len(outline['lessons'])} lessons, {sum(len(l['steps']) for l in outline['lessons'].values())} steps")
