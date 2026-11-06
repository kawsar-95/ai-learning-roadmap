"""Draft placement of KodeKloud clips onto the site's sections (a CANDIDATE pool, not the final picks).

Needles are lower-case substrings of the published title, prefixed S: (Shorts tab) or V: (Videos tab), with an
optional @views suffix to disambiguate. Every needle must resolve to exactly one clip, so a typo fails loudly and an id
is never typed by hand. Output: pool_ids.txt (one id per line, ':video' marks a long-form video) and draft_resolved.json.
Alternates are listed too, so a rejection after the transcript review has a replacement ready.
"""
import json
import os
import re
import sys

from _paths import WORK  # noqa: E402
D = str(WORK)


def load(path, long_form):
    rows = []
    for line in open(os.path.join(D, path), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if long_form:
            if len(p) < 4:
                continue
            rows.append({"id": p[0], "views": int(p[1]) if p[1].isdigit() else 0, "dur": int(float(p[2])) if p[2] not in ("", "NA", "None") else 0, "title": "\t".join(p[3:]), "long": True})
        else:
            if len(p) < 3:
                continue
            rows.append({"id": p[0], "views": int(p[1]) if p[1].isdigit() else 0, "dur": 0, "title": "\t".join(p[2:]), "long": False})
    return rows


SHORTS = load("kk_shorts_fresh.tsv", False)
VIDEOS = load("kk_videos_fresh.tsv", True)

# section -> needles
DRAFT = {
    "llm-fundamentals/s1": ["S:what actually is an ai token", "S:why should you care about ai tokens", "V:burning thousands of tokens", "S:every ai request has a price", "S:why does ai charge you more"],
    "llm-fundamentals/s2": ["S:what are large language models", "S:when should you use an llm? (part 1/2)", "S:when should you use an llm? (part 2/2)", "V:llm explained | common llm terms", "V:model size and hyperparameters", "S:llms limitations explained", "S:training cutoff in llms", "V:ai vs ml vs dl vs gen ai"],
    "llm-fundamentals/s3": ["S:open vs closed ai models explained", "V:the truth about closed ai models"],
    "llm-fundamentals/s4": ["S:6 llm settings", "S:why does ai give you a different answer", "V:llm temperature explained", "V:llm settings that every ai developer"],
    "llm-fundamentals/s5": ["S:how llm api calls actually work", "S:openai api python code walkthrough"],
    "llm-fundamentals/s7": ["S:llm tools explained (part - 1/3)", "S:llm tools explained (part - 2/3)", "S:llm tools explained (part 3/3)", "S:tool calling in rag"],
    "llm-fundamentals/s9": ["S:what is an embedding model", "S:why your ai can", "V:how does a vector database work"],
    "llm-fundamentals/s10": ["S:how reasoning models actually work"],
    "prompt-engineering/s1": ["S:llm roles and messages (part 1/3)", "S:llm roles and messages (part - 2/3)", "S:llm roles and messages (part 3/3)"],
    "prompt-engineering/s2": ["V:prompt engineering in generative ai", "V:master prompt engineering for beginners"],
    "prompt-engineering/s_alt": ["S:why prompt engineering is dead", "S:prompt engineering is a lie", "V:stop prompt engineering"],
    "prompt-engineering/s8": ["V:what is prompt injection", "S:what is lethal trifecta"],
    "fine-tuning-roadmap/s2": ["V:neural network explained in 3 minutes", "S:why neural networks took 80 years", "S:how llms actually learn@14000", "S:how llms actually learn@5400", "V:how machine learning works, end to end", "S:what do gpus actually do", "S:why cpus and gpus are so different", "V:ai & machine learning fundamentals"],
    "fine-tuning-roadmap/s3": ["V:llm fine tuning tutorial", "V:stop prompt engineering"],
    "fine-tuning-roadmap/s5": ["S:run powerful ai models locally with docker", "S:stop running models too big for your mac", "V:run llms with docker model runner", "V:docker model runner: your local ai solution", "V:llm quantization explained"],
    "context-engineering/s1": ["S:what is a context window", "S:the real reason ai loses track", "V:what is context engineering", "S:why context engineering is the future"],
    "context-engineering/s3": ["S:what is prompt caching"],
    "context-engineering/s6": ["S:how anthropic fixed mcp context bloat"],
    "context-engineering/s7": ["S:why more context is killing", "V:why llms forget"],
    "rag-knowledge-systems/s1": ["V:rag explained for beginners", "V:rag crash course for beginners", "V:complete rag tutorial 2026", "S:rag explained: how retrieval", "S:the simplest rag explanation", "S:what is rag? how ai chatbots", "S:what is rag in under 90", "S:rag explained in 60 seconds", "S:the 4 rag blocks", "S:why do rag exists", "S:rag chunking strategies", "S:poor chunking strategy"],
    "rag-knowledge-systems/s2": ["V:how does a vector database work"],
    "rag-knowledge-systems/misc": ["S:ai security: preventing data leaks in rag", "S:rag retrieval metrics explained", "S:tool calling in rag"],
    "agents-and-agentic-systems/s1": ["S:why do we need ai agents", "S:agent harness explained", "V:don't learn ai agents without", "V:ai agents for beginners – part 1", "S:ai agents for beginners course - part 1", "V:what is an ai agent harness", "S:claude code explained in 60 seconds", "V:claude code explained for beginners"],
    "agents-and-agentic-systems/s2": ["S:what is loop engineering", "S:how ai workflows really work (part 1/2)", "S:how ai workflows really work (part 2/2)", "S:ai agents vs ai workflows (part - 1/2)", "S:ai agents vs ai workflows (part - 2/2)", "S:(part 1/2) agent vs workflow", "S:(part 2/2) agent vs workflow", "S:why ai agents are killing workflows", "V:ai agents vs workflows: what changed"],
    "agents-and-agentic-systems/s3": ["V:google adk tutorial", "S:build ai agents in 60 seconds", "S:adk explained in 60 seconds", "S:new agent development kit", "S:a2a protocol works", "V:google a2a protocol"],
    "agents-and-agentic-systems/s4": ["S:when langchain isn", "S:how langgraph makes llm apps", "V:langchain vs langgraph", "V:langchain explained in 10 minutes"],
    "agents-and-agentic-systems/s5": ["V:agent memory explained"],
    "agents-and-agentic-systems/s10": ["S:how claude does web search", "S:what is openclaw", "V:what is openclaw", "S:what is claude managed agents", "V:what is claude managed agents", "V:pi agent explained"],
    "tool-use-and-integrations/s2": ["S:why we need mcp when apis", "S:mcp vs utcp", "S:model context protocol (mcp) explained in 60", "S:model context protocol upgrade", "S:mcp explained: the protocol every developer", "S:how does mcp actually work", "S:quitting mcp", "V:model context protocol (mcp) explained for beginners", "V:mcp tutorial: build your first mcp server", "V:mcp vs api explained", "V:mcp in 10 minutes", "V:build a fully functional mcp server"],
    "inference/s3": ["S:how the vllm inference engine works", "V:ai infrastructure explained", "V:understanding vllm with a hands on demo", "V:ai training vs inference explained", "S:why your llm is slow despite high gpu", "V:llm quantization explained"],
    "llmops-and-observability/s4": ["S:what is mlops?@35000", "S:best observability tools ranked", "V:complete guide to mlops", "V:how mlops works", "V:kubeflow explained for beginners", "S:what is kubeflow?", "V:what is mlops?"],
    "evaluation-engineering/s5": ["S:rag retrieval metrics explained", "V:how swe-bench changed", "S:can ai pass humanity", "V:the $2 million ai puzzle"],
    "cost-and-performance-optimization/s6": ["S:why claude uses 3 different rate limits", "V:the real cost of ai agents in 2026", "S:what is prompt caching", "V:burning thousands of tokens", "S:why does ai charge you more", "S:every ai request has a price"],
    "safety-security-and-guardrails/s7": ["S:what is lethal trifecta", "S:what are ai guardrails", "S:ai security: preventing data leaks in rag", "V:what is prompt injection", "S:claude fable 5: anthropic", "S:anthropic's ai accidentally hacked", "S:unbelievable abuse of claude"],
    "multimodal-engineering/s8": ["V:building audio transcription on aws"],
    "ai-application-architecture/s9": ["S:how chatgpt handles 900 million users", "S:how openai saved 30,000 cpu cores", "V:how openai serves 800 million users", "S:how to deploy an ai agent in kubernetes", "S:why git wasn", "S:build an ai chatbot in seconds"],
}


def resolve(needle):
    kind, _, rest = needle.partition(":")
    text, _, views = rest.partition("@")
    pool = SHORTS if kind == "S" else VIDEOS
    hits = [r for r in pool if text in r["title"].lower().replace("’", "'")]
    if views:
        hits = [r for r in hits if r["views"] == int(views)]
    return hits


def main():
    problems, resolved, order = [], {}, []
    for section, needles in DRAFT.items():
        resolved[section] = []
        for n in needles:
            hits = resolve(n)
            if len(hits) != 1:
                problems.append((section, n, [(h["id"], h["views"], h["title"][:60]) for h in hits]))
                continue
            h = hits[0]
            resolved[section].append({"id": h["id"], "long": h["long"], "views": h["views"], "dur": h["dur"], "title": h["title"]})
            key = h["id"] + (":video" if h["long"] else "")
            if key not in order:
                order.append(key)

    json.dump(resolved, open(os.path.join(D, "draft_resolved.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(D, "pool_ids.txt"), "w").write("\n".join(order) + "\n")
    print(f"sections: {len(resolved)} | resolved placements: {sum(len(v) for v in resolved.values())} | unique clips in pool: {len(order)}")
    print(f"  of which long-form: {sum(1 for o in order if o.endswith(':video'))}, Shorts: {sum(1 for o in order if not o.endswith(':video'))}")
    if problems:
        print("\nUNRESOLVED (fix the needle):")
        for s, n, h in problems:
            print(f"  {s}: {n!r} -> {len(h)} hits {h}")
        sys.exit(1)


if __name__ == "__main__":
    main()
