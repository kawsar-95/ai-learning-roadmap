"""Write the id lists for the live checks: verify_ids.txt (every pick + every gap resource, 'id' for a Short or 'id:video' for a long video)
and probe_ids.txt (the picks only: these are the ones that get embedded on the site, so they also go through the real player)."""
import json
import os

from _paths import WORK  # noqa: E402
D = str(WORK)
picks = json.load(open(f"{D}/final_picks.json", encoding="utf-8"))
specs, probe = [], []
for items in picks.values():
    for it in items:
        s = it["id"] + (":video" if it["kind"] == "V" else "")
        if s not in specs:
            specs.append(s)
        if it["id"] not in probe:
            probe.append(it["id"])
n_picks = len(specs)
for fn in ("gap_resolved.json", "gap2_resolved.json"):
    for group in json.load(open(f"{D}/{fn}", encoding="utf-8")).values():
        for h in group:
            s = h["id"] + (":video" if h["long"] else "")
            if not any(x.split(":")[0] == h["id"] for x in specs):
                specs.append(s)
open(f"{D}/verify_ids.txt", "w").write("\n".join(specs) + "\n")
open(f"{D}/probe_ids.txt", "w").write("\n".join(probe) + "\n")
print(f"verify_ids: {len(specs)} ({n_picks} picks + {len(specs) - n_picks} gap-list only) | probe_ids: {len(probe)}")
