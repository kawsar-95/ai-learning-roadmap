"""Coverage evidence for the gap analysis (read-only).

For each candidate topic: keyword hits in the Parts (src/content/<slug>.json, text only) and in the roadmap
lessons (src/content/lessons/**/*.md), with the Parts and phases that carry the most hits and lesson titles whose
TITLE matches. Writes gaps.json for the report.
"""
import glob
import json
import os
import re
from collections import Counter

from _paths import REPO as _REPO, WORK  # noqa: E402
REPO = str(_REPO)
OUT = str(WORK / "gaps.json")

TOPICS = {
    "Docker & containers": r"\bdocker\w*|\bcontainers?\b|containeri[sz]\w*|\bcompose\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b|\bkubectl\b|\bhelm\b|\bkserve\b|\bkubeflow\b|\bpods?\b|\bingress\b|\bllm-d\b",
    "CI/CD & GitOps": r"ci/cd|\bcicd\b|continuous (integration|delivery|deployment)|github actions|\bjenkins\b|gitlab ci|argo ?cd|gitops",
    "Infrastructure as Code": r"\bterraform\b|\bansible\b|infrastructure as code|\bpulumi\b|cloudformation|\biac\b",
    "Cloud platforms (AWS/Azure/GCP)": r"\baws\b|amazon web services|\bazure\b|\bgcp\b|google cloud|\bbedrock\b|\bsagemaker\b|vertex ai|\bec2\b|\blambda\b",
    "MLOps": r"\bmlops\b|\bmlflow\b|feature store|model registry|experiment tracking|\bdvc\b|\bairflow\b|model serving|\bkubeflow\b",
    "Metrics/logs stack (Prometheus, Grafana, OTel)": r"\bprometheus\b|\bgrafana\b|opentelemetry|\botel\b|\bloki\b|\bjaeger\b|\bdatadog\b|\bslos?\b|\bslis?\b",
    "Linux & shell": r"\blinux\b|\bbash\b|shell script|\bsystemd\b|\bssh\b|\bchmod\b|\bcron\b",
    "Git & GitHub": r"\bgit\b|\bgithub\b|pull request|\bbranching\b",
    "Networking (DNS, load balancing, proxies)": r"\bdns\b|load balanc\w*|reverse proxy|\bnginx\b|osi model|\btls\b|\bvpn\b|\bcdn\b",
    "DevSecOps & platform security": r"devsecops|secrets? manag\w*|\bvault\b|\bsbom\b|supply[- ]chain|\biam\b|\brbac\b|zero trust|vulnerability scan\w*|\btrivy\b",
    "System design & scalability": r"system design|scalab\w*|horizontal scaling|\bsharding\b|\breplication\b|message queue|\bkafka\b|\brabbitmq\b|\bredis\b",
    "Databases & data pipelines": r"\bpostgres\w*|\bsql\b|\bmysql\b|\bcdc\b|change data capture|data pipeline|\betl\b|data warehouse|\bmongodb\b",
    "AI coding assistants": r"claude code|\bcursor\b|\bcopilot\b|gemini cli|\bcodex\b|\bwindsurf\b|\baider\b",
    "GPU infrastructure": r"\bgpus?\b|\bcuda\b|\bnvidia\b|tensor cores?|\bh100\b|\ba100\b",
    "Python & scripting": r"\bpython\b|\bpandas\b|\bnumpy\b|\bvenv\b|\bpoetry\b|\bpip\b",
    "AIOps (AI for IT operations)": r"\baiops\b|anomaly detection|root[- ]cause analysis|incident response",
}

strip = lambda s: re.sub(r"<[^>]+>", " ", s)


def texts_of_parts():
    for p in sorted(glob.glob(f"{REPO}/src/content/*.json")):
        slug = os.path.basename(p)[:-5]
        if slug == "interview":
            continue
        d = json.load(open(p, encoding="utf-8"))
        # visible text only: everything except videos (so adding videos cannot change the evidence)
        for s in d["sections"]:
            s = {k: v for k, v in s.items() if k != "videos"}
            yield slug, strip(json.dumps(s, ensure_ascii=False))


part_text = {}
for slug, t in texts_of_parts():
    part_text[slug] = part_text.get(slug, "") + " " + t

lessons = []
for p in sorted(glob.glob(f"{REPO}/src/content/lessons/*/*.md")):
    phase = os.path.basename(os.path.dirname(p))
    body = open(p, encoding="utf-8").read()
    m = re.search(r"^#\s+(.+)$", body, re.M)
    lessons.append((phase, os.path.basename(p), m.group(1).strip() if m else os.path.basename(p), body))
print("Parts:", len(part_text), "| lessons:", len(lessons))

result = {}
for name, pat in TOPICS.items():
    rx = re.compile(pat, re.I)
    per_part = Counter({slug: len(rx.findall(t)) for slug, t in part_text.items()})
    part_hits = sum(per_part.values())
    lesson_hits = Counter()
    lesson_files = 0
    title_hits = []
    for phase, fn, title, body in lessons:
        n = len(rx.findall(body))
        if n:
            lesson_files += 1
            lesson_hits[phase] += n
        if rx.search(title):
            title_hits.append(f"{phase[:2]}/{title[:60]}")
    result[name] = {
        "part_hits": part_hits,
        "parts_with_hits": sum(1 for v in per_part.values() if v),
        "top_parts": [(k, v) for k, v in per_part.most_common(3) if v],
        "lesson_files": lesson_files,
        "lesson_hits": sum(lesson_hits.values()),
        "top_phases": lesson_hits.most_common(3),
        "lesson_title_hits": title_hits,
    }

json.dump(result, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"\n{'topic':<48} {'Part hits':>9} {'in n Parts':>10} {'lesson files':>12} {'title-matching lessons':>24}")
for name, r in result.items():
    print(f"{name:<48} {r['part_hits']:>9} {r['parts_with_hits']:>10} {r['lesson_files']:>12} {len(r['lesson_title_hits']):>24}")
print()
for name, r in result.items():
    print(f"## {name}\n   top Parts: {r['top_parts']}\n   top phases: {r['top_phases']}\n   lesson titles: {r['lesson_title_hits'][:6]}")
