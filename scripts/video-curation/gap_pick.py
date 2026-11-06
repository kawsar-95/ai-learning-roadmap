"""Resolve the curated gap-topic resources (title needles -> ids). They go in the coverage doc, not on the site.

Same rule as candidates_kodekloud.py: S:/V: prefix, lower-case substring of the published title, optional @views, exactly one hit.
Writes gap_resolved.json and gap_ids.txt (for lookup.py).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from candidates_kodekloud import resolve  # noqa: E402  (candidates_kodekloud.py resolves its own DRAFT at import; harmless, it only prints)

from _paths import WORK  # noqa: E402
D = str(WORK)

GAPS = {
    "Docker & containers": [
        "V:learn docker in 2 hours", "V:docker 101: a beginner", "S:containers vs virtual machines", "S:docker vs podman", "S:how to use a .dockerignore",
    ],
    "Kubernetes (and AI on Kubernetes)": [
        "V:kubernetes crash course: learn the basics", "V:what is kubernetes - the engine", "V:kubernetes architecture simplified", "V:ai infrastructure explained",
        "S:how to deploy an ai agent in kubernetes", "S:kubernetes explained without the jargon", "S:how to upgrade kubernetes without downtime",
    ],
    "CI/CD and GitOps": [
        "V:devops: ci/cd introduction", "V:demystifying gitops", "V:complete jenkins pipeline tutorial", "V:what is github actions?", "V:github actions tutorial: advanced concepts@35000",
        "S:best ci/cd tools in 2026", "S:6 gitops advantages",
    ],
    "Infrastructure as Code": [
        "V:terraform tutorial for beginners + labs", "V:ansible playbook for beginners", "V:what is terraform?", "V:pulumi tutorial",
        "S:crossplane vs terraform", "S:the best infrastructure as code tool",
    ],
    "Cloud platforms and managed AI services": [
        "V:stop watching aws tutorials", "V:aws certified ai practitioner (aif-c01) exam questions 2026", "V:aws certified ai practitioner (aif-c01): don", "V:aws eks tutorial",
        "S:aws ai practitioner question of the day | question 6 of 65", "S:aws lambda explained in 60 seconds",
    ],
    "MLOps": [
        "V:complete guide to mlops", "V:how mlops works", "V:what is mlops?", "V:kubeflow explained for beginners", "V:devops vs mlops",
        "S:what is mlops?@35000", "S:mlops roadmap for 2026", "S:what is kubeflow?", "S:6 mlops skills",
    ],
    "Metrics, logs and the observability stack": [
        "V:kubernetes monitoring made easy with prometheus", "V:how prometheus monitoring works", "V:mastering grafana loki", "V:prometheus tutorial for beginners",
        "S:best observability tools ranked", "S:what is grafana loki", "S:how distributed tracing works across microservices",
    ],
    "Linux and the shell": [
        "V:linux crash course for beginners", "V:linux tutorial for beginners", "V:dns in linux for the absolute beginners",
        "S:linux explained: what is linux", "S:3 bash tricks every developer", "S:linux command every engineer should use",
    ],
    "Git and GitHub": [
        "V:what is git? | git basics for devops", "V:git introduction for beginners!", "S:learn git worktrees", "S:why git wasn",
    ],
    "Networking fundamentals": [
        "V:network namespaces basics", "V:container network interface (cni) explained", "S:the osi model: 7 layers explained", "S:interview: how tcp, tls and http", "S:interview: how dns finds", "S:system design: designing load balancer",
    ],
    "DevSecOps and platform security": [
        "V:zero trust explained in 5 minutes", "V:secret store csi driver tutorial", "V:hashicorp vault + terraform", "S:shift left explained with sql injection", "S:stop storing kubernetes secrets", "S:aws iam explained in 60 seconds@17000",
    ],
    "System design and data infrastructure": [
        "V:system design for beginners (2026)", "V:change data capture (cdc) explained", "V:database sharding explained", "V:apache kafka crash course",
        "S:postgres hit the connection limit", "S:consistent hashing explained", "S:system design: notifying 50 million",
    ],
    "AIOps (AI for IT operations)": [
        "V:what is aiops? how it differs", "V:every devops engineer should know aiops", "S:what is aiops and how does it differ", "S:the complete aiops roadmap",
    ],
    "AI coding assistants": [
        "V:claude code explained for beginners", "V:claude code tutorial for beginners", "V:gemini cli: the open source tool", "V:cursor cli tutorial", "V:github copilot crash course",
        "S:claude code explained in 60 seconds", "S:gemini cli: open-source ai in your terminal",
    ],
    "Python and YAML for DevOps/AI work": [
        "V:yaml explained: a beginner", "S:meet uv", "S:why is python slow compared",
    ],
}

out, problems, ids = {}, [], []
for topic, needles in GAPS.items():
    out[topic] = []
    for n in needles:
        hits = resolve(n)
        if len(hits) != 1:
            problems.append((topic, n, [(h["id"], h["views"], h["title"][:60]) for h in hits]))
            continue
        h = hits[0]
        out[topic].append(h)
        key = h["id"] + (":video" if h["long"] else "")
        if key not in ids:
            ids.append(key)
json.dump(out, open(f"{D}/gap_resolved.json", "w"), ensure_ascii=False, indent=1)
open(f"{D}/gap_ids.txt", "w").write("\n".join(ids) + "\n")
print(f"topics: {len(out)} | resources: {sum(len(v) for v in out.values())} | unique clips: {len(ids)}")
for t, n, h in problems:
    print(f"UNRESOLVED {t}: {n!r} -> {len(h)} hits {h}")
sys.exit(1 if problems else 0)
