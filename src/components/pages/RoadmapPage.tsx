import Link from "next/link";
import { STAGES } from "@/lib/roadmap";
import { getTopic, topicText } from "@/lib/topics";
import { CURRICULUM_URL, formatDuration, lessonHref, lessonKey } from "@/lib/roadmap-schema";
import { UI, fmtNum, resourcesHref, roadmapHref, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import {
  CoreFilter,
  LessonCheck,
  PhaseDoneButton,
  RoadmapPhaseProgress,
  RoadmapSummary,
} from "@/components/progress/RoadmapWidgets";
import type { LessonLink } from "@/components/progress/RoadmapWidgets";

type PathKind = "start" | "core" | "focused";

const PATHS: {
  id: string;
  kind: PathKind;
  lesson: string;
  github: string;
  en: { title: string; summary: string };
  bn: { title: string; summary: string };
}[] = [
  {
    id: "new-to-ai",
    kind: "start",
    lesson: "00-setup-and-tooling/01-dev-environment",
    github: `${CURRICULUM_URL}/tree/main/phases/00-setup-and-tooling/01-dev-environment`,
    en: { title: "New to AI engineering", summary: "Set up your tools, run the course on your machine, and learn how one lesson works. Then pick a path." },
    bn: { title: "AI engineering-এ নতুন", summary: "টুল সেটআপ করুন, নিজের মেশিনে কোর্স চালান, আর একটি লেসন কীভাবে চলে তা শিখুন। তারপর একটি পাথ বেছে নিন।" },
  },
  {
    id: "building-and-deploying-ai-applications",
    kind: "core",
    lesson: "11-llm-engineering/01-prompt-engineering",
    github: `${CURRICULUM_URL}/blob/main/learning-paths/building-and-deploying-ai-applications.json`,
    en: { title: "Build and ship AI apps", summary: "Prompts, structured output, embeddings and RAG first. Then evals, serving, monitoring and a safe release." },
    bn: { title: "AI অ্যাপ বানানো ও চালু করা", summary: "আগে prompt, structured output, embedding আর RAG। তারপর eval, serving, monitoring আর নিরাপদ রিলিজ।" },
  },
  {
    id: "software-engineering-fundamentals",
    kind: "core",
    lesson: "00-setup-and-tooling/01-dev-environment",
    github: `${CURRICULUM_URL}/blob/main/learning-paths/software-engineering-fundamentals.json`,
    en: { title: "Software engineering basics", summary: "The base every AI system needs: repo and environment, debugging, testing, security and release." },
    bn: { title: "সফটওয়্যার ইঞ্জিনিয়ারিংয়ের ভিত্তি", summary: "প্রতিটি AI সিস্টেমের যে ভিত্তি লাগে: repo আর environment, debugging, testing, security আর release।" },
  },
  {
    id: "using-coding-agents",
    kind: "core",
    lesson: "14-agent-engineering/31-agent-workbench-why-models-fail",
    github: `${CURRICULUM_URL}/blob/main/learning-paths/using-coding-agents.json`,
    en: { title: "Work with coding agents", summary: "Give an agent a clear task, plan from the real code, set up its loop, and check its work before you trust it." },
    bn: { title: "কোডিং এজেন্টের সাথে কাজ", summary: "এজেন্টকে পরিষ্কার কাজ দিন, আসল কোড দেখে প্ল্যান করুন, তার loop সেটআপ করুন, আর বিশ্বাস করার আগে কাজটি যাচাই করুন।" },
  },
  {
    id: "shaping-the-build",
    kind: "core",
    lesson: "14-agent-engineering/47-outcomes-before-output",
    github: `${CURRICULUM_URL}/blob/main/learning-paths/shaping-the-build.json`,
    en: { title: "Product judgment", summary: "Decide what to build: start from the outcome, cut it into small testable slices, measure, and release in steps." },
    bn: { title: "প্রোডাক্ট বিচারবোধ", summary: "কী বানাবেন ঠিক করুন: ফলাফল থেকে শুরু করুন, ছোট টেস্ট করা যায় এমন অংশে ভাগ করুন, মাপুন, ধাপে ধাপে রিলিজ করুন।" },
  },
  {
    id: "model-context-protocol",
    kind: "focused",
    lesson: "13-tools-and-protocols/06-mcp-fundamentals",
    github: `${CURRICULUM_URL}/tree/main/phases/13-tools-and-protocols/06-mcp-fundamentals`,
    en: { title: "Model Context Protocol (MCP)", summary: "Build MCP servers, make them secure, test them, and run them in production." },
    bn: { title: "Model Context Protocol (MCP)", summary: "MCP সার্ভার বানান, নিরাপদ করুন, টেস্ট করুন, আর প্রোডাকশনে চালান।" },
  },
  {
    id: "agent-skills",
    kind: "focused",
    lesson: "13-tools-and-protocols/22-skills-and-agent-sdks",
    github: `${CURRICULUM_URL}/tree/main/phases/13-tools-and-protocols/22-skills-and-agent-sdks`,
    en: { title: "Agent skills", summary: "Write skills that agents can load, then test, secure and package them for real agent tools." },
    bn: { title: "এজেন্ট স্কিল", summary: "এমন স্কিল লিখুন যা এজেন্ট লোড করতে পারে, তারপর আসল এজেন্ট টুলের জন্য টেস্ট, সুরক্ষা আর প্যাকেজ করুন।" },
  },
];

/** The roadmap: stages of phases, each phase a list of lessons with a done toggle. */
export function RoadmapPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const fmt = (n: number) => fmtNum(lang, n);
  const links: LessonLink[] = STAGES.flatMap((stage) =>
    stage.phases.flatMap((phase) =>
      phase.lessons.map((lesson) => ({
        key: lessonKey(phase.phase, lesson.n),
        href: lessonHref(phase, lesson, lang),
        minutes: lesson.minutes,
      })),
    ),
  );

  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <header className="mb-10">
        <p className="font-mono text-[12px] font-medium tracking-[0.2em] text-accent uppercase">{ui.roadmap}</p>
        <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-text">
          {ui.roadmapTitle}
        </h1>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.roadmapIntro}</p>
      </header>

      <section aria-labelledby="learning-paths" className="mb-12">
        <h2 id="learning-paths" className="font-display text-[28px] font-bold leading-tight text-text">
          {ui.pathsTitle}
        </h2>
        <p className="mt-1 max-w-2xl text-[15px] text-text-dim">{ui.pathsIntro}</p>
        <ul className="m-0 mt-5 grid list-none gap-4 p-0 sm:grid-cols-2">
          {PATHS.map((path) => {
            const text = path[lang];
            const label = { start: ui.pathsStartHere, core: ui.pathsCore, focused: ui.pathsFocused }[path.kind];
            return (
              <li
                key={path.id}
                className={
                  "flex flex-col rounded-2xl border bg-bg-raised p-5 shadow-card " +
                  (path.kind === "start" ? "border-accent sm:col-span-2" : "border-border")
                }
              >
                <span className="font-mono text-[12px] tracking-[0.12em] text-accent uppercase">{label}</span>
                <h3 className="m-0 mt-1 font-display text-[20px] font-bold leading-snug text-text">{text.title}</h3>
                <p className="mt-2 mb-0 flex-1 text-[15px] text-text-dim">{text.summary}</p>
                <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[14px] font-medium">
                  <Link href={`${roadmapHref(lang)}${path.lesson}/`} className="inline-flex min-h-6 items-center text-accent">
                    {ui.pathsStart}
                  </Link>
                  <a
                    href={path.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex min-h-6 items-center text-text-dim hover:text-text"
                  >
                    GitHub ↗
                  </a>
                </div>
              </li>
            );
          })}
        </ul>
        <p className="mt-4 mb-0 text-[15px]">
          <Link href={resourcesHref(lang)} className="font-medium text-accent">
            {ui.resourcesTitle} →
          </Link>
        </p>
      </section>

      <RoadmapSummary lessons={links} lang={lang} />

      <CoreFilter lang={lang}>
        {STAGES.map((stage, stageIndex) => {
          const text = lang === "bn" ? stage.bn : stage;
          return (
            <section key={stage.id} aria-labelledby={`stage-${stage.id}`} className="mt-12">
              <p className="font-mono text-[12px] tracking-[0.16em] text-text-faint uppercase">
                {fmt(stageIndex + 1).padStart(2, fmt(0))}
              </p>
              <h2 id={`stage-${stage.id}`} className="mt-1 font-display text-[28px] font-bold leading-tight text-text">
                {text.title}
              </h2>
              <p className="mt-1 max-w-2xl text-[15px] text-text-dim">{text.summary}</p>

              <ol className="m-0 mt-5 list-none space-y-5 p-0">
                {stage.phases.map((phase) => {
                  const keys = phase.lessons.map((lesson) => lessonKey(phase.phase, lesson.n));
                  const topics = phase.topics.flatMap((slug) => {
                    const topic = getTopic(slug);
                    return topic ? [{ slug, title: topicText(topic, lang).title }] : [];
                  });
                  return (
                    <li
                      key={phase.phase}
                      id={`phase-${phase.phase}`}
                      data-core={phase.core}
                      className="scroll-mt-24 rounded-2xl border border-border bg-bg-raised p-6 shadow-card group-data-[core-only=true]/filter:data-[core=false]:hidden sm:p-7"
                    >
                      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                        <span className="font-mono text-[12px] tracking-[0.12em] text-accent uppercase">
                          {ui.roadmapPhase(fmt(phase.phase))}
                        </span>
                        <span
                          className={
                            "rounded-full border px-2 py-0.5 text-[11px] font-medium " +
                            (phase.core ? "border-accent text-accent" : "border-border-strong text-text-faint")
                          }
                        >
                          {phase.core ? ui.roadmapCore : ui.roadmapOptional}
                        </span>
                      </div>
                      <h3 className="m-0 mt-1 font-display text-[22px] font-bold leading-snug text-text">
                        {phase.title}
                      </h3>
                      <p className="mt-2 mb-0 max-w-2xl text-[15px] text-text-dim">
                        {lang === "bn" ? phase.bnSummary : phase.summary}
                      </p>
                      <p className="mt-2 mb-0 font-mono text-[12px] text-text-faint">
                        {ui.roadmapLessons(fmt(phase.lessons.length))} · ~{formatDuration(phase.minutes, lang, fmt)}
                      </p>
                      {topics.length > 0 && (
                        <p className="mt-3 mb-0 text-[14px] text-text-dim">
                          {ui.roadmapRelated}:{" "}
                          {topics.map((topic, i) => (
                            <span key={topic.slug}>
                              {i > 0 && ", "}
                              <Link href={topicHref(topic.slug, lang)} className="text-accent">
                                {topic.title}
                              </Link>
                            </span>
                          ))}
                        </p>
                      )}
                      <div className="mt-4 flex flex-wrap items-center gap-3">
                        <div className="min-w-48 max-w-xs flex-1">
                          <RoadmapPhaseProgress keys={keys} lang={lang} />
                        </div>
                        <PhaseDoneButton keys={keys} lang={lang} />
                      </div>

                      <details className="group mt-4">
                        <summary className="cursor-pointer list-none text-[14px] font-medium text-text-dim hover:text-text">
                          <span aria-hidden="true" className="mr-1.5 inline-block transition-transform group-open:rotate-90">
                            ›
                          </span>
                          {ui.roadmapLessons(fmt(phase.lessons.length))}
                        </summary>
                        <ol className="m-0 mt-2 list-none divide-y divide-border p-0">
                          {phase.lessons.map((lesson) => (
                            <li key={lesson.n} className="flex items-center gap-3 py-2">
                              <LessonCheck lessonKey={lessonKey(phase.phase, lesson.n)} title={lesson.title} lang={lang} />
                              <span className="w-7 shrink-0 font-mono text-[12px] text-text-faint">
                                {String(lesson.n).padStart(2, "0")}
                              </span>
                              <Link
                                href={lessonHref(phase, lesson, lang)}
                                className="min-w-0 flex-1 text-[15px] leading-snug text-text no-underline hover:text-accent"
                              >
                                {lesson.title}
                              </Link>
                              <span className="shrink-0 font-mono text-[12px] text-text-faint">
                                {formatDuration(lesson.minutes, lang, fmt)}
                              </span>
                            </li>
                          ))}
                        </ol>
                      </details>
                    </li>
                  );
                })}
              </ol>
            </section>
          );
        })}
      </CoreFilter>

      <p className="mt-12 text-[13px] text-text-faint">
        {ui.roadmapSource}{" "}
        <a href={CURRICULUM_URL} target="_blank" rel="noopener noreferrer" className="text-accent">
          GitHub ↗
        </a>
      </p>
    </div>
  );
}
