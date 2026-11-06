#!/usr/bin/env python3
"""Generate docs/video-coverage.md and docs/video-review-log.md from the verified data.

usage: python3 build_docs.py            (writes both files into the repo's docs/ folder)

Reads final_picks.json, lookups.json (oEmbed + /shorts/ status), probe.jsonl (player), gaps.json (keyword coverage),
gap_resolved.json / gap2_resolved.json (gap-topic resources), draft_resolved.json (KodeKloud candidates), the crawl TSVs
(views, length) and deep/<id>.json (upload date, promo flags). Nothing here is typed by hand except the reasons below.
"""
import glob
import json
import os
import re
import subprocess
import sys
from datetime import date

from _paths import REPO, SCRIPTS, WORK  # noqa: E402
AIE = str(WORK)
ROOT = str(REPO)
sys.path.insert(0, str(SCRIPTS))
import picks as P  # noqa: E402

TODAY = date.today().isoformat()
lookups = json.load(open(f"{AIE}/lookups.json", encoding="utf-8"))
final = json.load(open(f"{AIE}/final_picks.json", encoding="utf-8"))
gaps_cov = json.load(open(f"{AIE}/gaps.json", encoding="utf-8"))
P17 = "deploying-and-operating-ai-systems"
P17_USED = {it["id"]: sec.split("/")[1] for sec, items in final.items() if sec.startswith(P17 + "/") for it in items}  # clip id -> section id
P17_SECTION = {  # gap topic -> the Part 17 section that covers it
    "Linux and the shell": "s1", "Git and GitHub": "s2", "Networking fundamentals": "s3", "Python and YAML for DevOps/AI work": "s4",
    "Docker & containers": "s5", "Kubernetes (and AI on Kubernetes)": "s6", "CI/CD and GitOps": "s7", "Infrastructure as Code": "s8",
    "Cloud platforms and managed AI services": "s9", "MLOps": "s10", "Metrics, logs and the observability stack": "s11",
    "DevSecOps and platform security": "s12", "System design and data infrastructure": "s13", "AIOps (AI for IT operations)": "s14",
    "AI coding assistants": "s15",
}
probe = {}
for line in open(f"{AIE}/probe.jsonl", encoding="utf-8") if os.path.exists(f"{AIE}/probe.jsonl") else []:
    if line.startswith("{"):
        r = json.loads(line)
        probe[r["id"]] = r

CHANNELS = [  # slug, name on YouTube, handle
    ("kodekloud", "KodeKloud", "@KodeKloud"),
    ("colemedin", "Cole Medin", "@ColeMedin"),
    ("aijason", "AI Jason", "@AIJasonZ"),
    ("krishnaik", "Krish Naik", "@krishnaik06"),
    ("davidondrej", "David Ondrej", "@DavidOndrej"),
    ("nana", "TechWorld with Nana", "@TechWorldwithNana"),
    ("automata", "Lucas Soares | Automata Learning Lab", "@automatalearninglab"),
    ("deeplearningai", "DeepLearningAI", "@Deeplearningai"),
]
NAME = {s: n for s, n, _ in CHANNELS}


def read_tsv(path, with_dur=True):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 4 and with_dur:
                out[f[0]] = (int(f[1]) if f[1].isdigit() else 0, int(float(f[2])) if f[2].replace(".", "", 1).isdigit() else 0, "\t".join(f[3:]))
            elif len(f) >= 3:
                out[f[0]] = (int(f[1]) if f[1].isdigit() else 0, 0, "\t".join(f[2:]))
    return out


CATALOG = {}
for fn, wd in (("kk_shorts_fresh.tsv", False), ("kk_videos_fresh.tsv", True)):
    CATALOG.update(read_tsv(f"{AIE}/{fn}", wd))
for p in glob.glob(f"{AIE}/ch_*_*.tsv"):
    CATALOG.update(read_tsv(p, True))
COUNTS = {}
for slug, _, _ in CHANNELS:
    v = f"{AIE}/ch_{slug}_videos.tsv" if slug != "kodekloud" else f"{AIE}/kk_videos_fresh.tsv"
    s = f"{AIE}/ch_{slug}_shorts.tsv" if slug != "kodekloud" else f"{AIE}/kk_shorts_fresh.tsv"
    COUNTS[slug] = (sum(1 for _ in open(v, encoding="utf-8")) if os.path.exists(v) else 0, sum(1 for _ in open(s, encoding="utf-8")) if os.path.exists(s) else 0)


def stored(titles):
    r = subprocess.run(["node", "--disable-warning=MODULE_TYPELESS_PACKAGE_JSON", f"{SCRIPTS}/stored_titles.mjs"], input=json.dumps(titles), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def views(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else (f"{n // 1000}K" if n >= 1000 else str(n))


def length(sec):
    if not sec:
        return "?"
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def dur_of(vid):
    p = f"{AIE}/deep/{vid}.json"
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8")).get("duration")
        if d:
            return int(d)
    pr = probe.get(vid)
    if pr and pr.get("duration"):
        return round(pr["duration"])
    return CATALOG.get(vid, (0, 0, ""))[1]


def link(vid, title, short):
    return f"[{title}](https://www.youtube.com/{'shorts/' if short else 'watch?v='}{vid})"


def esc(s):
    return s.replace("|", "\\|")


# ---------------------------------------------------------------- gap topics
GAP_INFO = {  # topic -> (keys in gaps.json, suggested addition)
    "Docker & containers": (["Docker & containers"], "Packaging models and apps in containers: images, volumes, GPU passthrough, Compose for a RAG stack."),
    "Kubernetes (and AI on Kubernetes)": (["Kubernetes", "GPU infrastructure"], "Serving LLMs on a cluster: Deployments and Services, GPU scheduling, autoscaling, operators."),
    "CI/CD and GitOps": (["CI/CD & GitOps"], "Gate prompt, model and eval changes in a pipeline, and deploy with GitOps."),
    "Infrastructure as Code": (["Infrastructure as Code"], "Provision GPU nodes, vector databases and networks with Terraform or Pulumi; configure with Ansible."),
    "Cloud platforms and managed AI services": (["Cloud platforms (AWS/Azure/GCP)"], "Bedrock, Vertex AI and Azure OpenAI side by side, plus IAM, networking and cost basics."),
    "MLOps": (["MLOps"], "Pipelines, registries, feature stores and drift. It explains how LLMOps (Part 9) differs from classic MLOps."),
    "Metrics, logs and the observability stack": (["Metrics/logs stack (Prometheus, Grafana, OTel)"], "Prometheus, Grafana, Loki and OpenTelemetry underneath LLM tracing."),
    "Linux and the shell": (["Linux & shell"], "The shell, processes, permissions and networking commands used when running models and agents."),
    "Git and GitHub": (["Git & GitHub"], "Branching, pull requests and Actions, and versioning prompts and datasets the same way as code."),
    "Networking fundamentals": (["Networking (DNS, load balancing, proxies)"], "DNS, TLS, proxies and load balancers: the path of one LLM API request."),
    "DevSecOps and platform security": (["DevSecOps & platform security"], "Secrets, IAM, supply-chain, container and cluster security around AI workloads."),
    "System design and data infrastructure": (["System design & scalability", "Databases & data pipelines"], "Queues, caches, databases and scaling patterns around an AI application."),
    "AIOps (AI for IT operations)": (["AIOps (AI for IT operations)"], "Using LLMs for incident response, anomaly detection and runbooks."),
    "AI coding assistants": (["AI coding assistants"], "Claude Code, Cursor, Copilot and Gemini CLI: workflows, context files and MCP servers."),
    "Python and YAML for DevOps/AI work": (["Python & scripting"], "Python tooling and YAML/config literacy for the pipeline files above."),
}


def gap_section():
    P17_TITLES = {sec["id"]: sec["title"] for sec in json.load(open(f"{ROOT}/src/content/{P17}.json", encoding="utf-8"))["sections"]}
    kk = json.load(open(f"{AIE}/gap_resolved.json", encoding="utf-8"))
    cr = json.load(open(f"{AIE}/gap2_resolved.json", encoding="utf-8"))
    lines, excluded = [], 0
    for topic, (keys, _scope) in GAP_INFO.items():
        rows = []
        for src in (kk.get(topic, []), cr.get(topic, [])):
            for h in src:
                lk = lookups.get(h["id"])
                is_short = not h.get("long")
                if not lk or lk.get("oembed_status") != 200 or (is_short and lk.get("shorts_status") != 200):
                    excluded += 1
                    continue
                channel = h.get("creator") or "kodekloud"
                rows.append((h["id"], is_short, channel, lk["title"], lk["author"], CATALOG.get(h["id"], (h["views"], 0, ""))[0], dur_of(h["id"])))
        if not rows:
            continue
        titles = stored([r[3] for r in rows])
        cov = [gaps_cov[k] for k in keys if k in gaps_cov]
        part_hits = sum(c["part_hits"] for c in cov)
        parts = sum(c["parts_with_hits"] for c in cov)
        lessons = sum(c["lesson_files"] for c in cov)
        lines.append(f"### {topic}\n")
        sec_id = P17_SECTION[topic]
        lines.append(f"**Before Part 17:** {part_hits} keyword hits in {parts} of the 16 Parts, and {lessons} roadmap lessons mentioned it. **Now:** Part 17, section {sec_id[1:]}, {P17_TITLES[sec_id]}.\n")
        lines.append("| Resource | Channel | Length | Views | In Part 17 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for (vid, is_short, _, _, author, v, dur), title in sorted(zip(rows, titles), key=lambda x: -x[0][5]):
            used = f"section {P17_USED[vid][1:]}" if vid in P17_USED else ""
            lines.append(f"| {esc(link(vid, title, is_short))} | {esc(author)} | {'Short, ' + length(dur) if is_short and dur else ('Short' if is_short else length(dur))} | {views(v)} | {used} |")
        lines.append("")
    return "\n".join(lines), excluded


# ---------------------------------------------------------------- reasons for the review log
KK_WHY = [  # title substring (lower case) -> reason
    ("why git wasn't enough", "news about one company's internal tool; its claims cannot be checked from the clip"),
    ("claude code explained in 60 seconds", "the same script as the kept 9-minute video"),
    ("what is aiops and how does it differ", "the same script as the kept video"),
    ("model size and hyperparameters", "conflates parameters with hyperparameters and says DeepSeek V3 has 82b parameters"),
    ("rag explained: how retrieval", "dates RAG to early 2021; the paper is from May 2020"),
    ("open vs closed ai models explained", "says ChatGPT launched \"in 2019\" (probably a caption garble of GPT-2, not confirmed)"),
    ("the truth about closed ai models", "says ChatGPT launched \"in 2019\" (probably a caption garble of GPT-2, not confirmed)"),
    ("ai agents for beginners course", "a trailer for a KodeKloud course"),
    ("ai agents for beginners – part 1", "a 67-minute course lesson built around enrolment and lab sign-up"),
    ("how google's a2a protocol works", "stops at \"let's break it down\" before explaining anything"),
    ("new agent development kit", "hype title; nothing the ADK Shorts kept does not already say"),
    ("why ai agents are killing workflows", "hype title; the two-part workflow series covers the same ground"),
    ("model context protocol upgrade", "news about a specification update, not a lasting explanation"),
    ("openclaw", "a product explainer that is already dated"),
    ("claude managed agents", "a product explainer that is already dated"),
    ("pi agent explained", "a product explainer that is already dated"),
    ("claude code explained", "an AI coding assistant, not a topic of any Part: listed under \"AI coding assistants\" in video-coverage.md"),
    ("claude fable 5", "model-launch news"),
    ("accidentally hacked 3 real companies", "news about one report, not engineering education"),
    ("unbelievable abuse of claude", "news about one report, not engineering education"),
    ("saved 30,000 cpu cores", "a log-collector configuration story, not AI application architecture"),
    ("why git wasn", "about version control at one company, tangential to the Part"),
    ("build an ai chatbot in seconds", "a vague pitch for pre-built modules"),
    ("humanity's last exam", "a benchmark explainer with few views, tangential to application evals"),
    ("$2 million ai puzzle", "a benchmark explainer with few views, tangential to application evals"),
    ("mlops", "classic MLOps or infrastructure observability, not LLMOps: listed under \"MLOps\" in video-coverage.md"),
    ("kubeflow", "classic MLOps or infrastructure observability, not LLMOps: listed under \"MLOps\" in video-coverage.md"),
    ("best observability tools ranked", "infrastructure observability, not LLM tracing: listed under the observability stack in video-coverage.md"),
    ("ai infrastructure explained", "a 51-minute course-style video with lab pitches: listed under \"Kubernetes (and AI on Kubernetes)\" in video-coverage.md"),
    ("master prompt engineering for beginners", "few views, and the section already has a stronger overview"),
    ("why prompt engineering is dead", "hype title that contradicts the Part's own advice"),
    ("prompt engineering is a lie", "hype title that contradicts the Part's own advice"),
    ("openai api python code walkthrough", "a code walk-through that never touches streaming, the section's topic"),
    ("llms limitations explained", "over the section limit; the kept clips say it more clearly"),
    ("ai vs ml vs dl vs gen ai", "generic and only loosely about model trade-offs"),
    ("how llms actually learn", "a second clip with the same title; the more viewed one is kept"),
    ("what do gpus actually do", "hardware, tangential to how a network trains"),
    ("why cpus and gpus are so different", "hardware, tangential to how a network trains"),
    ("ai & machine learning fundamentals", "overlaps the full end-to-end ML video that is kept"),
    ("complete rag tutorial 2026", "the same course as the kept RAG crash course"),
    ("langchain explained in 10 minutes", "about LangChain components, not graph workflows"),
    ("tool calling in rag", "kept once, in Function calling & tool use"),
]
CR_WHY = {  # needle in DROP2 -> reason (the comments of picks.py, kept as data so the log can print them)
    "nana/V:what is docker? docker container concept explained": "opens by welcoming viewers to a Kubernetes tutorial",
    "nana/V:what is helm in kubernetes?": "the section does not cover Helm",
    "nana/V:microservices explained - the what, why and how": "sponsored by HashiCorp, and about architecture styles rather than the section's topics",
    "aijason/V:i was using claude code wrong": "a sponsored 2025 workflow video that ends in a community pitch",
    "aijason/V:gpt5 unlocks llm system 2 thinking": "a 2024 prompting talk, not about reasoning models",
    "deeplearningai/V:full ai prompting course with andrew ng": "a 2.5-hour course for general users, not engineers' prompt design",
    "aijason/V:next level prompts": "2023, built on one niche library",
    "krishnaik/V:steps by step tutorial to fine tune llama 2": "Llama 2 era code-along",
    "aijason/V:okay, but i want gpt to perform 10x": "2023 GPT-3.5 fine-tuning walkthrough",
    "automata/V:3 ways to set up llama2 locally": "Llama 2 era, few views",
    "colemedin/V:context engineering 101": "near-duplicate of the kept video, with a sponsor segment",
    "colemedin/V:build any ai agent with this context engineering blueprint": "sponsored, overlaps the kept video",
    "davidondrej/V:context engineering is the future of ai agents": "kept under Single-agent vs multi-agent: its argument is \"do not build multi-agent systems\"",
    "aijason/V:.agent folder is making claude code 10x better": "a coding-assistant workflow, not a memory hierarchy",
    "colemedin/V:introducing rag 2.0: agentic rag + knowledge graphs": "mostly a template and community pitch; its Short is kept",
    "colemedin/S:scrape any website in seconds for your llms": "repeats the opening of the long Crawl4AI video word for word",
    "deeplearningai/V:learn how to build multimodal search and rag": "a course-lesson fragment with few views",
    "krishnaik/V:what is agentic ai? important for gen ai in 2025": "overlaps the clearer explainer that is kept",
    "automata/V:building llm agents in 3 levels of complexity": "December 2023, legacy LangChain agents",
    "colemedin/V:revealing my complete ai agent blueprint": "a sponsored workflow overview",
    "aijason/V:wtf is harness engineer": "a mid-roll sponsor detour; Cole Medin's video covers the loop itself",
    "deeplearningai/V:learn multi ai agent systems with crewai: lesson 1": "a course introduction fragment",
    "colemedin/V:this is hands down the best way to build ai agents": "hype title, 51 minutes, promotes his own project",
    "deeplearningai/V:learn how to build an agent from scratch with langgraph": "kept under The four canonical agent loops: it is a raw-API ReAct loop",
    "colemedin/S:what everyone is missing with ai agents - memory + tools that scale": "about multi-user agents, not memory",
    "davidondrej/V:infinite local memory": "a product walkthrough with a promo code",
    "davidondrej/V:browser use: this new ai agent can do anything": "mostly a pitch for his own product",
    "automata/V:mcp, context & agentic ai": "a sponsored opinion piece",
    "automata/V:getting started with mcp for llm agents": "a third video over 30 minutes; the section keeps two",
    "davidondrej/V:build anything with mcp agents": "Cursor usage plus a product plug, not MCP itself",
    "colemedin/V:claude mcp has changed ai forever": "a Claude Desktop walkthrough from early 2025",
    "nana/V:mlops explained - what it is, why you need it": "classic MLOps: listed under \"MLOps\" in video-coverage.md",
    "krishnaik/V:llm evaluation with mlflow and dagshub": "kept under Evaluation engineering",
    "automata/V:building an audio transcription app with openai whisper and streamlit": "November 2022, Whisper's release era",
    "aijason/V:ai agent + vision = incredible": "sponsored (SceneXplain), GPT-4V era",
    "aijason/V:knowledge embedding 101": "2023 code-along tied to the old OpenAI embedding model",
    "krishnaik/V:what is llm hallucination": "the safety section does not cover hallucination",
}


def notes_for(vid, creator):
    """Short factual notes read from the cached transcript and metadata (sponsor segments, lab pitches, upload month)."""
    p = f"{AIE}/deep/{vid}.json"
    if not os.path.exists(p):
        return ""
    d = json.load(open(p, encoding="utf-8"))
    t = d.get("transcript") or ""
    notes = []
    up = d.get("upload_date") or ""
    if len(up) == 8:
        notes.append(f"uploaded {up[:4]}-{up[4:6]}")
    if re.search(r"sponsor\w*|brought to you by|thanks to \w+ for", t, re.I):
        notes.append("mentions a sponsor")
    if re.search(r"free labs?|our labs|click on enroll|our platform", t, re.I):
        notes.append("mentions KodeKloud's labs or platform")
    if re.search(r"vectal|dynamous|skool|my community|join the community|ai builder club", t + " " + (d.get("description") or ""), re.I):
        notes.append("mentions the creator's community or product")
    return "; ".join(notes)


def log_section():
    flat = [(sec, it) for sec, items in final.items() for it in items]
    titles = {it["id"]: lookups.get(it["id"], {}).get("title") or it["title"] for _, it in flat}
    st = dict(zip(titles.keys(), stored(list(titles.values()))))
    lines = []
    by_topic = {}
    for sec, items in final.items():
        by_topic.setdefault(sec.split("/")[0], []).append((sec, items))
    cat = json.load(open(f"{AIE}/catalog.json", encoding="utf-8"))
    sec_title = {f"{s['topic']}/{s['sid']}": s["title"] for s in cat["sections"]}
    kk_kept = {it["id"] for items in final.values() for it in items}
    for topic in cat["order"]:
        groups = by_topic.get(topic)
        if not groups:
            continue
        lines.append(f"## {topic}\n")
        for sec, items in groups:
            if not items:
                continue
            lines.append(f"### {sec_title.get(sec, sec)} (`{sec}`)\n")
            lines.append("| Clip | Channel | Length | Views | Notes |")
            lines.append("| --- | --- | --- | --- | --- |")
            for it in items:
                short = it["kind"] == "S"
                n = notes_for(it["id"], it["creator"])
                lines.append(f"| {esc(link(it['id'], st[it['id']], short))} | {esc(lookups.get(it['id'], {}).get('author', NAME[it['creator']]))} | {'Short, ' if short else ''}{length(dur_of(it['id']))} | {views(CATALOG.get(it['id'], (it['views'], 0, ''))[0])} | {n} |")
            lines.append("")
    # dropped candidates
    drafts = json.load(open(f"{AIE}/draft_resolved.json", encoding="utf-8"))
    dropped = []
    seen = set()
    for sec, items in drafts.items():
        for it in items:
            if it["id"] in kk_kept or it["id"] in seen:
                continue
            seen.add(it["id"])
            reason = next((r for k, r in KK_WHY if k in it["title"].lower().replace("\u2019", "'")), "over the section limit or covered by a clearer pick")
            dropped.append((sec, "kodekloud", it["id"], it["title"], not it["long"], reason))
    import candidates_creators as D2
    for sec, needles in P.DROP2.items():
        for n in needles:
            hits = D2.resolve(n)
            if len(hits) == 1:
                h = hits[0]
                if h["id"] in kk_kept:
                    continue  # moved, not dropped
                dropped.append((sec, h["creator"], h["id"], h["title"], not h["long"], CR_WHY.get(n, "")))
    lines.append("## Candidates that were read and not used\n")
    lines.append("| Clip | Channel | Drafted for | Why not |")
    lines.append("| --- | --- | --- | --- |")
    for sec, creator, vid, title, short, reason in dropped:
        lines.append(f"| {esc(link(vid, title, short))} | {esc(NAME[creator])} | `{sec}` | {reason} |")
    return "\n".join(lines) + "\n", len(dropped)


def main():
    n_added = sum(len(v) for v in final.values())
    by_ch = {}
    for items in final.values():
        for it in items:
            c = by_ch.setdefault(it["creator"], [0, 0])
            c[0 if it["kind"] == "V" else 1] += 1
    gap_md, gap_excluded = gap_section()
    log_md, n_dropped = log_section()

    cov = [f"# Video coverage\n",
           f"Which YouTube videos the Parts list, which technical topics Part 17 was added to cover, and where each clip came from. Generated {TODAY} from the same data the site reads. Every id was found from a published title, never typed. Each clip on a page was checked live against YouTube before it went into `src/content/`: oEmbed (public and embeddable), the Shorts redirect (a Short really is one), and the IFrame player (it starts, and its length is the real one). The resources below that Part 17 does not list got the first two checks, because the site does not embed them. Views are rounded and were read from each channel's listing on that day.\n",
           "## Channels\n",
           "| Channel | Handle | Listed (videos / Shorts) | Added to the Parts (videos / Shorts) |", "| --- | --- | --- | --- |"]
    for slug, name, handle in CHANNELS:
        v, s = COUNTS[slug]
        a = by_ch.get(slug, [0, 0])
        cov.append(f"| {esc(name)} | `{handle}` | {v:,}{'+' if v >= 1500 else ''} / {s:,} | {a[0]} / {a[1]} |")
    cov.append("\nKrish Naik's list stops at the newest 1,500 videos, a cap set for the crawl, so his older videos were not searched.")
    n_sections = sum(1 for v in final.values() if v)
    cov.append(f"\n{n_added} clips were added to {n_sections} sections; {n_dropped} more were read and left out, each with its reason in [video-review-log.md](video-review-log.md).\n")
    cov.append("## Topics Part 17 covers\n")
    cov.append("KodeKloud and TechWorld with Nana publish courses on all of these, which is where the lists below come from. The first 16 Parts had little or no reference page for them, so Part 17, Deploying and Operating AI Systems, has one section for each. The counts are rough keyword hits taken before Part 17 existed, not a judgement of quality, and they are kept as they were: running gaps.py now would count Part 17 itself. The lists put the most viewed first. The last column names the Part 17 section that lists a clip. The other resources were found and link-checked but are not used on the site, and the review log gives the reason for each one that was read.\n")
    cov.append(gap_md)
    cov.append("## How the clips were chosen\n")
    cov.append("- On topic for the section it sits in, taken from the section's own text, then read in the transcript: the opening, the ending, and a sample of the middle for long videos.")
    cov.append("- Left out: factual errors, hype or news titles, trailers and enrolment pitches, product launches that are already dated, code-alongs tied to a model or library version that has since changed, and clips that repeat another clip.")
    cov.append("- At most 5 KodeKloud clips and 4 clips from the other creators per section, at most 3 from one creator, and at most 2 videos over 30 minutes.")
    cov.append("- A Short is at most 180 seconds, and `seconds` comes from the player.")
    cov.append("- Sponsor segments and community plugs are not a reason to leave a good clip out. The review log notes them.\n")
    cov.append("## Keeping it true\n")
    cov.append("`npm run check:videos` asks YouTube whether every listed video is still public and embeddable, still has its stored title and channel, and whether a Short is still a Short. `npm run check:videos -- --channel \"Cole Medin\"` checks one channel. Run it by hand: `npm test` and the deploy never touch the network.\n")
    open(f"{ROOT}/docs/video-coverage.md", "w", encoding="utf-8").write("\n".join(cov))

    head = f"# Video review log\n\nEvery clip added to a section, with its length, views, and what was noticed in the transcript, followed by the candidates that were read and not used. Generated {TODAY}. The lengths come from the player; views are from each channel's listing on that day.\n\n"
    open(f"{ROOT}/docs/video-review-log.md", "w", encoding="utf-8").write(head + log_md)
    print(f"coverage: {len(cov)} blocks, {gap_excluded} gap resources not verified and left out | log: {n_added} kept, {n_dropped} not used")


if __name__ == "__main__":
    main()
