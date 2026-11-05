"""Candidate placements for the NEW creators (Cole Medin, AI Jason, Krish Naik, David Ondrej, TechWorld with Nana,
Lucas Soares | Automata Learning Lab, DeepLearningAI), resolved by title needle -- ids are never typed by hand.

Needle: "<creator>/<V|S>:<lower-case substring of the published title>[@exact views]"; it must match exactly one clip.
Writes pool2_ids.txt (section picks, for fetch_details.py), draft2_resolved.json, gap2_resolved.json, gap2_ids.txt.
This is a CANDIDATE pool: the transcript review decides what stays.
"""
import json
import os
import sys

from _paths import WORK  # noqa: E402
D = str(WORK)
CH = {}


def load(slug, tab):
    p = os.path.join(D, f"ch_{slug}_{tab}.tsv")
    rows = []
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 4:
                rows.append({"id": f[0], "views": int(f[1]) if f[1].isdigit() else 0, "title": "\t".join(f[3:]), "long": tab == "videos", "creator": slug})
    return rows


for s in ("colemedin", "aijason", "krishnaik", "davidondrej", "nana", "automata", "deeplearningai"):
    CH[s] = {"V": load(s, "videos"), "S": load(s, "shorts")}


def resolve(needle):
    who, _, rest = needle.partition("/")
    kind, _, rest = rest.partition(":")
    text, _, views = rest.partition("@")
    hits = [r for r in CH[who][kind] if text in r["title"].lower().replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')]
    if views:
        hits = [r for r in hits if r["views"] == int(views)]
    return hits


DRAFT2 = {
    "llm-fundamentals/s9": ["aijason/V:knowledge embedding 101", "deeplearningai/S:semantic search starts with embeddings"],
    "llm-fundamentals/s10": ["aijason/V:gpt5 unlocks llm system 2 thinking"],
    "prompt-engineering/s2": ["deeplearningai/V:full ai prompting course with andrew ng", "aijason/V:next level prompts"],
    "prompt-engineering/s5": ["automata/V:organizing your ai prompts with jinja templates"],
    "fine-tuning-roadmap/s3": [
        "aijason/V:easiest way to train llm train w/ unsloth", "davidondrej/V:fine-tune your own llm in 13 minutes",
        "krishnaik/V:part 1-road to learn finetuning llm with custom data", "krishnaik/V:steps by step tutorial to fine tune llama 2",
        "aijason/V:okay, but i want gpt to perform 10x", "krishnaik/V:prompt engineering vs rag vs finetuning explained easily",
    ],
    "fine-tuning-roadmap/s5": ["colemedin/V:run all your ai locally in minutes", "davidondrej/V:if you don't run ai locally you're falling behind", "automata/V:3 ways to set up llama2 locally"],
    "context-engineering/s1": [
        "colemedin/V:context engineering is the new vibe coding", "colemedin/V:context engineering 101", "davidondrej/V:context engineering is the future of ai agents",
        "colemedin/V:build any ai agent with this context engineering blueprint",
    ],
    "context-engineering/s4": ["aijason/V:.agent folder is making claude code 10x better"],
    "context-engineering/s6": ["aijason/V:anthropic killed tool calling"],
    "rag-knowledge-systems/s1": [
        "colemedin/V:every rag strategy explained in 13 minutes", "krishnaik/V:introduction to undertsanding rag", "krishnaik/V:complete rag crash course with langchain in 2 hours",
    ],
    "rag-knowledge-systems/s2": ["krishnaik/V:2-build rag pipeline from scratch-data ingestion to vector db pipeline-part 1"],
    "rag-knowledge-systems/s3": ["krishnaik/V:hybrid search rag with langchain and pinecone vector db"],
    "rag-knowledge-systems/s5": [
        "colemedin/V:the future of rag is agentic", "aijason/V:llama3 to perform 10x with my private knowledge", "colemedin/S:introducing rag 2.0: agentic rag + knowledge graphs",
    ],
    "rag-knowledge-systems/s6": [
        "colemedin/V:make rag 100x better with real-time knowledge graphs", "colemedin/V:the proven solution for unbelievable rag performance", "colemedin/V:introducing rag 2.0: agentic rag + knowledge graphs",
    ],
    "rag-knowledge-systems/s9": [
        "colemedin/V:turn any file into llm knowledge in seconds", "colemedin/S:turn any file into llm knowledge in seconds",
        "colemedin/V:turn any website into llm knowledge in seconds@458000", "colemedin/S:scrape any website in seconds for your llms",
    ],
    "rag-knowledge-systems/s10": ["krishnaik/V:step by step process to build multimodal rag with langchain", "deeplearningai/V:learn how to build multimodal search and rag"],
    "agents-and-agentic-systems/s1": [
        "krishnaik/V:generative ai vs agentic ai vs ai agents", "krishnaik/V:what is agentic ai? important for gen ai in 2025",
        "automata/V:building llm agents in 3 levels of complexity", "colemedin/V:revealing my complete ai agent blueprint",
    ],
    "agents-and-agentic-systems/s2": ["aijason/V:wtf is harness engineer", "colemedin/V:harness engineering: what separates top agentic engineers"],
    "agents-and-agentic-systems/s3": [
        "krishnaik/V:crewai crash course for beginners", "deeplearningai/V:learn multi ai agent systems with crewai: lesson 1", "colemedin/V:this is hands down the best way to build ai agents",
    ],
    "agents-and-agentic-systems/s4": [
        "krishnaik/V:most popular framework-langchain vs langgraph", "krishnaik/V:tutorial 1-getting started with langgraph", "deeplearningai/V:learn how to build an agent from scratch with langgraph",
    ],
    "agents-and-agentic-systems/s5": [
        "aijason/V:unlock ai agent real power", "colemedin/S:what everyone is missing with ai agents - memory + tools that scale",
        "davidondrej/V:infinite local memory", "deeplearningai/V:ai dev 25 | apoorva joshi: building agents that learn",
    ],
    "agents-and-agentic-systems/s7": ["aijason/V:i was using sub-agents wrong"],
    "agents-and-agentic-systems/s10": ["davidondrej/V:browser use: this new ai agent can do anything"],
    "tool-use-and-integrations/s2": [
        "nana/V:mcp explained simply", "krishnaik/V:all you need to know about model context protocol", "colemedin/V:claude mcp has changed ai forever",
        "automata/V:mcp, context & agentic ai", "automata/V:getting started with mcp for llm agents", "davidondrej/V:build anything with mcp agents", "colemedin/S:mcp is insecure",
    ],
    "llmops-and-observability/s4": [
        "nana/V:mlops explained - what it is, why you need it", "krishnaik/V:langsmith llmops platform by langchain", "krishnaik/V:llm evaluation with mlflow and dagshub",
    ],
    "evaluation-engineering/s5": [
        "krishnaik/V:mastering llm chatbots and rag evaluation crash course", "deeplearningai/V:ai dev 26 x sf | ara khan: evals are broken use them anyway",
    ],
    "cost-and-performance-optimization/s6": ["aijason/V:the real cost of llm"],
    "safety-security-and-guardrails/s7": ["krishnaik/V:what is llm hallucination", "krishnaik/V:guardrails with langchain: a complete crash course"],
    "multimodal-engineering/s8": [
        "colemedin/V:build your first voice ai agent in 20 minutes with livekit", "automata/V:building a local voice ai assistant with llama 3.2",
        "automata/V:building an audio transcription app with openai whisper and streamlit", "aijason/V:ai agent + vision = incredible",
    ],
}

# Gap-topic resources from these creators (they go in the coverage doc, not on a section page).
GAPS2 = {
    "Docker & containers": ["nana/V:docker crash course for absolute beginners [new]", "nana/V:docker tutorial for beginners [full course in 3 hours]", "nana/V:what is docker? docker container concept explained"],
    "Kubernetes (and AI on Kubernetes)": [
        "nana/V:kubernetes crash course for absolute beginners [new]", "nana/V:what is kubernetes | kubernetes explained in 15 mins", "nana/V:kubernetes tutorial for beginners [full course in 4 hours]",
        "nana/V:kubernetes services explained", "nana/V:what is helm in kubernetes?", "nana/V:kubernetes operator simply explained",
    ],
    "CI/CD and GitOps": [
        "nana/V:github actions tutorial - basic concepts and ci/cd pipeline with docker", "nana/V:gitlab ci cd tutorial for beginners [crash course]", "nana/V:complete jenkins pipeline tutorial",
        "nana/V:argocd tutorial for beginners", "nana/V:what is gitops, how gitops works", "nana/V:ci/cd explained: the devops skill",
    ],
    "Infrastructure as Code": [
        "nana/V:terraform explained in 15 mins", "nana/V:what is ansible | ansible playbook explained", "nana/V:what is infrastructure as code?", "nana/V:8 terraform best practices", "nana/V:pulumi - iac in your favorite",
    ],
    "Cloud platforms and managed AI services": ["nana/V:aws eks - create kubernetes cluster on amazon eks", "nana/V:containers on aws overview", "nana/V:what is platform engineering"],
    "MLOps": [
        "nana/V:mlops explained - what it is, why you need it", "krishnaik/V:end to end machine learning project implementation with dockers", "krishnaik/V:end to end deep learning project using mlops dvc pipeline",
        "krishnaik/V:end to end machine learning project implementation using aws sagemaker",
    ],
    "Metrics, logs and the observability stack": ["nana/V:how prometheus monitoring works", "nana/V:setup prometheus monitoring on kubernetes using helm and prometheus operator | part 1"],
    "Linux and the shell": ["nana/V:20% of linux commands you'll use 80% of the time", "nana/V:bash scripting tutorial for beginners"],
    "Networking fundamentals": ["nana/V:every networking concept explained in 20 minutes", "nana/V:proxy vs reverse proxy vs load balancer", "nana/V:nginx explained"],
    "DevSecOps and platform security": [
        "nana/V:what is devsecops? devsecops explained in 8 mins", "nana/V:kubernetes security best practices", "nana/V:hashicorp vault tutorial for beginners",
        "nana/V:devsecops tutorial for beginners | ci pipeline with github actions and docker scout",
    ],
    "System design and data infrastructure": ["nana/V:kafka tutorial for beginners", "nana/V:microservices explained", "nana/V:redis crash course", "nana/V:istio & service mesh"],
    "AIOps (AI for IT operations)": ["nana/V:chatgpt tutorial - use chatgpt for devops tasks", "nana/V:github copilot tutorial | how useful is it for cloud and devops?"],
    "AI coding assistants": [
        "krishnaik/V:complete claude code course in 2 hours for developers", "colemedin/V:a complete guide to claude code - here are all the best strategies",
        "aijason/V:i was using claude code wrong", "davidondrej/V:i spent 400+ hours in cursor", "aijason/V:how i reduced 90% errors for my cursor (+ any other ai ide)",
    ],
    "Python and YAML for DevOps/AI work": ["nana/V:yaml tutorial | learn yaml in 18 mins", "nana/V:python tutorial for beginners - learn python in 5 hours [full course]"],
    "DevOps careers and roadmap": ["nana/V:devops roadmap - how to become a devops engineer?", "nana/V:complete devops roadmap 2026"],
}


def run(spec, out_name, ids_name, with_ids_for_deep):
    out, problems, ids = {}, [], []
    for key, needles in spec.items():
        out[key] = []
        for n in needles:
            hits = resolve(n)
            if len(hits) != 1:
                problems.append((key, n, [(h["id"], h["views"], h["title"][:56]) for h in hits]))
                continue
            h = hits[0]
            out[key].append(h)
            tag = h["id"] + (":video" if h["long"] else "")
            if tag not in ids:
                ids.append(tag)
    json.dump(out, open(os.path.join(D, out_name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(D, ids_name), "w").write("\n".join(ids) + "\n")
    print(f"{out_name}: {len(out)} groups | {sum(len(v) for v in out.values())} placements | {len(ids)} unique clips")
    return problems


if __name__ == "__main__":
    probs = run(DRAFT2, "draft2_resolved.json", "pool2_ids.txt", True) + run(GAPS2, "gap2_resolved.json", "gap2_ids.txt", False)
    for key, n, hits in probs:
        print(f"UNRESOLVED [{key}] {n!r} -> {len(hits)} hits {hits}")
    sys.exit(1 if probs else 0)
