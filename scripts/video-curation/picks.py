"""Final picks: KodeKloud (explicit needles, after the transcript review) + the other creators (candidates in candidates_creators.py minus DROP2).

Every pick is resolved by title needle against the crawled catalogs and must match exactly one clip. Writes final_picks.json
(ordered per section) and prints per-section totals, the long-video count and the checks that the site's tests will enforce.
usage: python3 picks.py
"""
import json
import os
import sys

from _paths import WORK  # noqa: E402
D = str(WORK)
sys.path.insert(0, D)
import candidates_kodekloud as kkdraft  # noqa: E402
import candidates_creators as cr  # noqa: E402

# --- KodeKloud: S: = Shorts tab, V: = Videos tab, @N = exact view count to disambiguate ---
KK = {
    "llm-fundamentals/s1": ["S:what actually is an ai token", "S:why should you care about ai tokens", "S:every ai request has a price"],
    "llm-fundamentals/s2": ["S:what are large language models", "V:llm explained | common llm terms", "S:when should you use an llm? (part 1/2)", "S:when should you use an llm? (part 2/2)", "S:training cutoff in llms"],
    "llm-fundamentals/s4": ["S:6 llm settings", "S:why does ai give you a different answer", "V:llm temperature explained", "V:llm settings that every ai developer"],
    "llm-fundamentals/s5": ["S:how llm api calls actually work"],
    "llm-fundamentals/s7": ["S:llm tools explained (part - 1/3)", "S:llm tools explained (part - 2/3)", "S:llm tools explained (part 3/3)", "S:tool calling in rag"],
    "llm-fundamentals/s9": ["S:what is an embedding model", "S:why your ai can"],
    "llm-fundamentals/s10": ["S:how reasoning models actually work"],
    "prompt-engineering/s1": ["S:llm roles and messages (part 1/3)", "S:llm roles and messages (part - 2/3)", "S:llm roles and messages (part 3/3)"],
    "prompt-engineering/s2": ["V:prompt engineering in generative ai"],
    "fine-tuning-roadmap/s2": ["V:neural network explained in 3 minutes", "S:why neural networks took 80 years", "S:how llms actually learn@14000", "V:how machine learning works, end to end"],
    "fine-tuning-roadmap/s3": ["V:llm fine tuning tutorial", "V:stop prompt engineering"],
    "fine-tuning-roadmap/s5": ["S:run powerful ai models locally with docker", "S:stop running models too big for your mac", "V:run llms with docker model runner", "V:docker model runner: your local a"],
    "context-engineering/s1": ["S:what is a context window", "S:the real reason ai loses track", "V:what is context engineering", "S:why context engineering is the future"],
    "context-engineering/s3": ["S:what is prompt caching"],
    "context-engineering/s6": ["S:how anthropic fixed mcp context bloat"],
    "context-engineering/s7": ["S:why more context is killing", "V:why llms forget"],
    "rag-knowledge-systems/s1": ["V:rag explained for beginners", "V:rag crash course for beginners", "S:what is rag? how ai chatbots", "S:rag chunking strategies", "S:poor chunking strategy"],
    "rag-knowledge-systems/s2": ["V:how does a vector database work"],
    "agents-and-agentic-systems/s1": ["S:why do we need ai agents", "S:agent harness explained", "V:what is an ai agent harness", "V:don't learn ai agents without"],
    "agents-and-agentic-systems/s2": ["S:what is loop engineering", "S:how ai workflows really work (part 1/2)", "S:how ai workflows really work (part 2/2)", "S:ai agents vs ai workflows (part - 1/2)", "S:ai agents vs ai workflows (part - 2/2)"],
    "agents-and-agentic-systems/s3": ["S:build ai agents in 60 seconds", "S:adk explained in 60 seconds", "V:google a2a protocol", "V:google adk tutorial"],
    "agents-and-agentic-systems/s4": ["S:when langchain isn", "S:how langgraph makes llm apps", "V:langchain vs langgraph"],
    "agents-and-agentic-systems/s5": ["V:agent memory explained"],
    "agents-and-agentic-systems/s10": ["S:how claude does web search"],
    "tool-use-and-integrations/s2": ["S:why we need mcp when apis", "S:mcp vs utcp", "V:model context protocol (mcp) explained for beginners", "V:mcp vs api explained", "V:mcp tutorial: build your first mcp server"],
    "inference/s3": ["S:how the vllm inference engine works", "V:understanding vllm with a hands on demo", "V:ai training vs inference explained", "S:why your llm is slow despite high gpu", "V:llm quantization explained"],
    "evaluation-engineering/s5": ["S:rag retrieval metrics explained", "V:how swe-bench changed"],
    "cost-and-performance-optimization/s6": ["S:why claude uses 3 different rate limits", "V:the real cost of ai agents in 2026", "V:burning thousands of tokens", "S:why does ai charge you more"],
    "safety-security-and-guardrails/s7": ["S:what is lethal trifecta", "S:what are ai guardrails", "S:ai security: preventing data leaks in rag", "V:what is prompt injection"],
    "multimodal-engineering/s8": ["V:building audio transcription on aws"],
    "ai-application-architecture/s9": ["S:how chatgpt handles 900 million users", "V:how openai serves 800 million users", "S:how to deploy an ai agent in kubernetes"],
}

# --- Other creators: candidates from candidates_creators.DRAFT2 minus these needles (decided after the transcript review) ---
DROP2 = {
    "llm-fundamentals/s10": ["aijason/V:gpt5 unlocks llm system 2 thinking"],  # 2024 prompting talk, not about reasoning models
    "prompt-engineering/s2": ["deeplearningai/V:full ai prompting course with andrew ng",  # prompting for general users, not engineers
                              "aijason/V:next level prompts"],  # 2023, a niche library (guidance)
    "fine-tuning-roadmap/s3": ["krishnaik/V:steps by step tutorial to fine tune llama 2",  # Llama 2 era
                               "aijason/V:okay, but i want gpt to perform 10x"],  # 2023 GPT-3.5 fine-tuning
    "fine-tuning-roadmap/s5": ["automata/V:3 ways to set up llama2 locally"],  # Llama 2 era, low views
    "context-engineering/s1": ["colemedin/V:context engineering 101",  # near-duplicate of the first, sponsored
                               "davidondrej/V:context engineering is the future of ai agents",  # moved to agents/s3
                               "colemedin/V:build any ai agent with this context engineering blueprint"],  # sponsored, overlap
    "context-engineering/s4": ["aijason/V:.agent folder is making claude code 10x better"],  # a coding workflow, not a memory hierarchy
    "rag-knowledge-systems/s5": ["colemedin/S:introducing rag 2.0: agentic rag + knowledge graphs"],  # moved to rag/s8
    "rag-knowledge-systems/s6": ["colemedin/V:introducing rag 2.0: agentic rag + knowledge graphs"],  # mostly a template and community pitch; its Short stays
    "rag-knowledge-systems/s9": ["colemedin/S:scrape any website in seconds for your llms"],  # repeats the long video's opening
    "rag-knowledge-systems/s10": ["deeplearningai/V:learn how to build multimodal search and rag"],  # a lesson fragment, 12K views
    "agents-and-agentic-systems/s1": ["krishnaik/V:what is agentic ai? important for gen ai in 2025",  # overlaps the clearer explainer
                                      "automata/V:building llm agents in 3 levels of complexity",  # Dec 2023, legacy LangChain agents
                                      "colemedin/V:revealing my complete ai agent blueprint"],  # sponsored workflow overview
    "agents-and-agentic-systems/s2": ["aijason/V:wtf is harness engineer"],  # HubSpot-sponsored detour; Cole Medin's covers the loop itself
    "agents-and-agentic-systems/s3": ["deeplearningai/V:learn multi ai agent systems with crewai: lesson 1",  # a course intro fragment
                                      "colemedin/V:this is hands down the best way to build ai agents"],  # hype title, 51 min, promotes his own project
    "agents-and-agentic-systems/s4": ["deeplearningai/V:learn how to build an agent from scratch with langgraph"],  # a raw-API ReAct loop; moved to agents/s2
    "agents-and-agentic-systems/s5": ["colemedin/S:what everyone is missing with ai agents - memory + tools that scale",  # about multi-user agents, not memory
                                      "davidondrej/V:infinite local memory"],  # a product walkthrough with a promo code
    "agents-and-agentic-systems/s10": ["davidondrej/V:browser use: this new ai agent can do anything"],  # mostly a pitch for his own product
    "tool-use-and-integrations/s2": ["automata/V:mcp, context & agentic ai",  # sponsored opinion piece
                                     "automata/V:getting started with mcp for llm agents",  # a third long video; the section is capped at two
                                     "davidondrej/V:build anything with mcp agents",  # Cursor usage plus a product plug, not MCP itself
                                     "colemedin/V:claude mcp has changed ai forever"],  # Claude Desktop walkthrough from early 2025
    "llmops-and-observability/s4": ["nana/V:mlops explained - what it is, why you need it",  # classic MLOps: goes in the gap list
                                    "krishnaik/V:llm evaluation with mlflow and dagshub"],  # moved to evaluation-engineering/s5
    "multimodal-engineering/s8": ["automata/V:building an audio transcription app with openai whisper and streamlit",  # Nov 2022, Whisper's release era
                                  "aijason/V:ai agent + vision = incredible"],  # sponsored (SceneXplain), GPT-4V era
    "llm-fundamentals/s9": ["aijason/V:knowledge embedding 101"],  # 2023 code-along tied to the old OpenAI embedding model
    "safety-security-and-guardrails/s7": ["krishnaik/V:what is llm hallucination"],  # the section does not cover hallucination
}
# Creator clips added to a section other than the one drafted in candidates_creators.py.
ADD2 = {
    "evaluation-engineering/s5": ["krishnaik/V:llm evaluation with mlflow and dagshub"],
    "agents-and-agentic-systems/s2": ["deeplearningai/V:learn how to build an agent from scratch with langgraph"],
    "agents-and-agentic-systems/s3": ["davidondrej/V:context engineering is the future of ai agents"],
    "rag-knowledge-systems/s6": ["colemedin/S:introducing rag 2.0: agentic rag + knowledge graphs"],
}

CAPS = {"kodekloud_per_section": 5, "long_over_30min_per_section": 2}


def build():
    problems, out, seen = [], {}, {}
    sections = list(dict.fromkeys(list(KK) + list(cr.DRAFT2) + list(ADD2)))
    for sec in sections:
        out[sec] = []
        for n in KK.get(sec, []):
            hits = kkdraft.resolve(n)
            if len(hits) != 1:
                problems.append((sec, n, [(h["id"], h["views"], h["title"][:50]) for h in hits]))
                continue
            h = hits[0]
            out[sec].append({"id": h["id"], "kind": "V" if h["long"] else "S", "creator": "kodekloud", "views": h["views"], "title": h["title"], "needle": n})
        for n in cr.DRAFT2.get(sec, []) + ADD2.get(sec, []):
            if n in DROP2.get(sec, []):
                continue
            hits = cr.resolve(n)
            if len(hits) != 1:
                problems.append((sec, n, [(h["id"], h["views"], h["title"][:50]) for h in hits]))
                continue
            h = hits[0]
            out[sec].append({"id": h["id"], "kind": "V" if h["long"] else "S", "creator": h["creator"], "views": h["views"], "title": h["title"], "needle": n})
    for sec, items in out.items():
        for it in items:
            if it["id"] in seen:
                problems.append((sec, it["needle"], f"duplicate of {seen[it['id']]}"))
            seen[it["id"]] = sec
    return out, problems


def caps_report(out):
    """Check the per-section limits against the real lengths cached by fetch_details.py."""
    bad = []
    for sec, items in out.items():
        n_long, per_creator = 0, {}
        for it in items:
            p = os.path.join(D, "deep", f"{it['id']}.json")
            dur = json.load(open(p, encoding="utf-8")).get("duration") or 0 if os.path.exists(p) else 0
            it["seconds"] = dur
            if dur > 1800:
                n_long += 1
            per_creator[it["creator"]] = per_creator.get(it["creator"], 0) + 1
        new = sum(v for k, v in per_creator.items() if k != "kodekloud")
        if per_creator.get("kodekloud", 0) > CAPS["kodekloud_per_section"]:
            bad.append(f"{sec}: {per_creator['kodekloud']} KodeKloud clips")
        if new > 4:
            bad.append(f"{sec}: {new} clips from the other creators (max 4)")
        for k, v in per_creator.items():
            if k != "kodekloud" and v > 3:
                bad.append(f"{sec}: {v} clips from {k} (max 3)")
        if n_long > CAPS["long_over_30min_per_section"]:
            bad.append(f"{sec}: {n_long} videos over 30 minutes (max {CAPS['long_over_30min_per_section']})")
    return bad


if __name__ == "__main__":
    out, problems = build()
    problems += [(s, "cap", m) for s, m in ((m.split(":")[0], m) for m in caps_report(out))]
    json.dump(out, open(os.path.join(D, "final_picks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = {"kodekloud": 0}
    print(f"{'section':<42} {'kk':>3} {'new':>3} {'S':>3} {'V':>3}")
    for sec, items in out.items():
        kk = sum(1 for i in items if i["creator"] == "kodekloud")
        for i in items:
            tot[i["creator"]] = tot.get(i["creator"], 0) + (0 if i["creator"] == "kodekloud" else 1)
        print(f"{sec:<42} {kk:>3} {len(items) - kk:>3} {sum(1 for i in items if i['kind'] == 'S'):>3} {sum(1 for i in items if i['kind'] == 'V'):>3}")
    kk_total = sum(1 for items in out.values() for i in items if i["creator"] == "kodekloud")
    print(f"\nKodeKloud: {kk_total}   others: {json.dumps({k: v for k, v in tot.items() if k != 'kodekloud'})}   total: {sum(len(v) for v in out.values())}")
    for sec, n, h in problems:
        print(f"PROBLEM [{sec}] {n!r} -> {h}")
    sys.exit(1 if problems else 0)
