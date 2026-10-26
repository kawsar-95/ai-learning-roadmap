import Link from "next/link";
import { PHASES } from "@/lib/roadmap";
import { UI, fmtNum, roadmapHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

type Text = { en: string; bn: string };
type Repo = { repo: string; phase: number; about: Text; bangla?: boolean };

const GROUPS: { id: string; title: Text; repos: Repo[] }[] = [
  {
    id: "courses",
    title: { en: "Courses", bn: "কোর্স" },
    repos: [
      {
        repo: "microsoft/generative-ai-for-beginners",
        phase: 11,
        bangla: true,
        about: {
          en: "A step-by-step course on building generative AI apps: prompts, chat, search, function calling and safety.",
          bn: "জেনারেটিভ AI অ্যাপ বানানোর ধাপে ধাপে কোর্স: prompt, chat, search, function calling আর নিরাপত্তা।",
        },
      },
      {
        repo: "microsoft/ML-For-Beginners",
        phase: 2,
        bangla: true,
        about: {
          en: "Classic machine learning through small projects: regression, classification, clustering, NLP and time series.",
          bn: "ছোট প্রজেক্টের মাধ্যমে ক্লাসিক মেশিন লার্নিং: regression, classification, clustering, NLP আর time series।",
        },
      },
      {
        repo: "microsoft/AI-For-Beginners",
        phase: 3,
        bangla: true,
        about: {
          en: "A broad AI course with notebooks: neural networks, computer vision, NLP and more.",
          bn: "notebook সহ AI-এর বড় পরিসরের কোর্স: neural network, computer vision, NLP আর আরও কিছু।",
        },
      },
      {
        repo: "rasbt/LLMs-from-scratch",
        phase: 10,
        about: {
          en: "Build a GPT-style model from zero in PyTorch, one chapter at a time. It is the code for the book of the same name.",
          bn: "PyTorch-এ শূন্য থেকে GPT ধরনের মডেল বানান, অধ্যায় ধরে ধরে। এটি একই নামের বইয়ের কোড।",
        },
      },
    ],
  },
  {
    id: "cookbooks",
    title: { en: "Cookbooks", bn: "কুকবুক" },
    repos: [
      {
        repo: "openai/openai-cookbook",
        phase: 11,
        about: {
          en: "Runnable examples for the OpenAI API: prompting, embeddings, evals and agents.",
          bn: "OpenAI API-এর চালানো যায় এমন উদাহরণ: prompting, embedding, eval আর agent।",
        },
      },
      {
        repo: "anthropics/claude-cookbooks",
        phase: 14,
        about: {
          en: "Runnable examples for Claude: tool use, RAG, agents and evaluation.",
          bn: "Claude-এর চালানো যায় এমন উদাহরণ: tool use, RAG, agent আর evaluation।",
        },
      },
    ],
  },
  {
    id: "models",
    title: { en: "Models and training", bn: "মডেল আর ট্রেনিং" },
    repos: [
      {
        repo: "pytorch/pytorch",
        phase: 3,
        about: {
          en: "The deep learning framework that most research and courses use: tensors, autograd and training loops.",
          bn: "বেশিরভাগ গবেষণা আর কোর্স যে deep learning framework ব্যবহার করে: tensor, autograd আর training loop।",
        },
      },
      {
        repo: "huggingface/transformers",
        phase: 7,
        about: {
          en: "Load, run and fine-tune pretrained models for text, vision and audio.",
          bn: "text, vision আর audio-এর pretrained মডেল লোড, চালানো আর fine-tune করা।",
        },
      },
      {
        repo: "huggingface/diffusers",
        phase: 8,
        about: {
          en: "Ready pipelines and training tools for diffusion models that make images and audio.",
          bn: "ছবি আর audio তৈরির diffusion মডেলের তৈরি pipeline আর training টুল।",
        },
      },
      {
        repo: "CompVis/stable-diffusion",
        phase: 8,
        about: {
          en: "The original Stable Diffusion code. Read it to see how text-to-image generation works.",
          bn: "Stable Diffusion-এর মূল কোড। text থেকে ছবি কীভাবে তৈরি হয় তা বুঝতে পড়ুন।",
        },
      },
      {
        repo: "facebookresearch/segment-anything",
        phase: 4,
        about: {
          en: "A model that cuts out any object in an image from one click or a box.",
          bn: "একটি ক্লিক বা বক্স দিয়ে ছবির যেকোনো বস্তু আলাদা করার মডেল।",
        },
      },
    ],
  },
  {
    id: "apps",
    title: { en: "LLM apps and agents", bn: "LLM অ্যাপ আর এজেন্ট" },
    repos: [
      {
        repo: "langchain-ai/langchain",
        phase: 11,
        about: {
          en: "Building blocks that connect LLMs to your data, tools and other services.",
          bn: "LLM-কে আপনার data, tool আর অন্য সার্ভিসের সাথে যুক্ত করার building block।",
        },
      },
      {
        repo: "langchain-ai/langgraph",
        phase: 14,
        about: {
          en: "Build agents as graphs, with saved state, loops and human approval steps.",
          bn: "graph আকারে agent বানান, সংরক্ষিত state, loop আর মানুষের অনুমোদনের ধাপ সহ।",
        },
      },
      {
        repo: "run-llama/llama_index",
        phase: 11,
        about: {
          en: "Load your documents, index them, and answer questions about them (RAG).",
          bn: "নিজের ডকুমেন্ট লোড করুন, index করুন, আর সেগুলো নিয়ে প্রশ্নের উত্তর দিন (RAG)।",
        },
      },
      {
        repo: "stanfordnlp/dspy",
        phase: 11,
        about: {
          en: "Write LLM programs as code, and let the tool tune the prompts for you.",
          bn: "LLM প্রোগ্রাম কোড হিসেবে লিখুন, আর prompt ঠিক করার কাজ টুলটিকে দিন।",
        },
      },
      {
        repo: "microsoft/autogen",
        phase: 16,
        about: {
          en: "A framework in which several agents talk to each other to finish a task.",
          bn: "এমন framework, যেখানে কয়েকটি agent একে অপরের সাথে কথা বলে একটি কাজ শেষ করে।",
        },
      },
      {
        repo: "crewAIInc/crewAI",
        phase: 16,
        about: {
          en: "Give each agent a role and a goal, and let them work as a team.",
          bn: "প্রতিটি agent-কে একটি role আর goal দিন, তারপর তারা দল হিসেবে কাজ করবে।",
        },
      },
    ],
  },
  {
    id: "serving",
    title: { en: "Serving and running models", bn: "মডেল সার্ভিং আর চালানো" },
    repos: [
      {
        repo: "vllm-project/vllm",
        phase: 17,
        about: {
          en: "A fast server for LLM inference on GPUs, used in production.",
          bn: "GPU-তে LLM inference-এর দ্রুত সার্ভার, প্রোডাকশনে ব্যবহৃত।",
        },
      },
      {
        repo: "ollama/ollama",
        phase: 17,
        about: {
          en: "Download and run open models on your own computer with one command.",
          bn: "এক কমান্ডে নিজের কম্পিউটারে open মডেল ডাউনলোড করে চালান।",
        },
      },
      {
        repo: "open-webui/open-webui",
        phase: 17,
        about: {
          en: "A chat web app that you host yourself, for local or remote models.",
          bn: "নিজে হোস্ট করা chat ওয়েব অ্যাপ, লোকাল বা রিমোট মডেলের জন্য।",
        },
      },
    ],
  },
];

/** Links to well-known open-source repos, grouped by kind, each tied to a roadmap phase. */
export function ResourcesPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const fmt = (n: number) => fmtNum(lang, n);

  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <header className="mb-10">
        <p className="font-mono text-[12px] font-medium tracking-[0.2em] text-accent uppercase">{ui.resources}</p>
        <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-text">
          {ui.resourcesTitle}
        </h1>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.resourcesIntro}</p>
      </header>

      {GROUPS.map((group) => (
        <section key={group.id} aria-labelledby={`group-${group.id}`} className="mt-12">
          <h2 id={`group-${group.id}`} className="font-display text-[28px] font-bold leading-tight text-text">
            {group.title[lang]}
          </h2>
          <ul className="m-0 mt-5 grid list-none gap-4 p-0 sm:grid-cols-2">
            {group.repos.map((item) => {
              const phase = PHASES.find((p) => p.phase === item.phase);
              return (
                <li key={item.repo} className="flex flex-col rounded-2xl border border-border bg-bg-raised p-5 shadow-card">
                  <a
                    href={`https://github.com/${item.repo}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-mono text-[15px] font-semibold break-all text-text no-underline hover:text-accent"
                  >
                    {item.repo} ↗
                  </a>
                  <p className="mt-2 mb-0 flex-1 text-[15px] text-text-dim">{item.about[lang]}</p>
                  <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[14px] font-medium">
                    {phase && (
                      <Link href={`${roadmapHref(lang)}#phase-${phase.phase}`} className="inline-flex min-h-6 items-center text-accent">
                        {ui.roadmapPhase(fmt(phase.phase))} · {phase.title}
                      </Link>
                    )}
                    {item.bangla && (
                      <a
                        href={`https://github.com/${item.repo}/blob/main/translations/bn/README.md`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex min-h-6 items-center text-text-dim hover:text-text"
                      >
                        {ui.resourcesBangla}
                      </a>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      ))}

      <p className="mt-12 text-[13px] text-text-faint">{ui.resourcesNote}</p>
    </div>
  );
}
