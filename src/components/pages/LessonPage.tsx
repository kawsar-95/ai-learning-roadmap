import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import "katex/dist/katex.min.css";
import source from "@/content/lessons/source.json";
import { PHASES } from "@/lib/roadmap";
import { CURRICULUM_URL, formatDuration, lessonHref, lessonKey } from "@/lib/roadmap-schema";
import { renderLesson } from "@/lib/lesson-markdown";
import { UI, fmtNum, roadmapHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { LessonCheck } from "@/components/progress/RoadmapWidgets";

export type LessonParams = { phase: string; lesson: string };

const ORDER = PHASES.flatMap((phase) => phase.lessons.map((lesson) => ({ phase, lesson })));
const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

function indexOf({ phase, lesson }: LessonParams): number {
  return ORDER.findIndex((item) => item.phase.folder === phase && item.lesson.dir === lesson);
}

export function lessonStaticParams(): LessonParams[] {
  return ORDER.map(({ phase, lesson }) => ({ phase: phase.folder, lesson: lesson.dir }));
}

export async function lessonMetadata(params: Promise<LessonParams>): Promise<Metadata> {
  const item = ORDER[indexOf(await params)];
  return item ? { title: item.lesson.title } : {};
}

/** One curriculum lesson, copied into src/content/lessons by scripts/import-lessons.mjs. */
export async function LessonPage({ params, lang }: { params: Promise<LessonParams>; lang: Lang }) {
  const index = indexOf(await params);
  if (index < 0) notFound();
  const { phase, lesson } = ORDER[index];
  const prev = ORDER[index - 1];
  const next = ORDER[index + 1];
  const ui = UI[lang];
  const fmt = (n: number) => fmtNum(lang, n);

  const markdown = readFileSync(join(process.cwd(), "src/content/lessons", phase.folder, `${lesson.dir}.md`), "utf8");
  const html = renderLesson(markdown, { folder: phase.folder, dir: lesson.dir, commit: source.commit, lang, base: BASE });

  return (
    <article className="mx-auto max-w-3xl px-4 pt-10 pb-20 sm:px-6 sm:pt-14">
      <p className="m-0 font-mono text-[12px] tracking-[0.12em] text-text-faint uppercase">
        <Link href={`${roadmapHref(lang)}#phase-${phase.phase}`} className="text-accent no-underline">
          {ui.roadmap}
        </Link>
        {" / "}
        {ui.roadmapPhase(fmt(phase.phase))} · {phase.title}
      </p>
      <h1 className="mt-3 font-display text-[clamp(2rem,4.5vw,2.75rem)] font-bold leading-[1.15] tracking-[-0.01em] text-text">
        {lesson.title}
      </h1>
      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2">
        <LessonCheck lessonKey={lessonKey(phase.phase, lesson.n)} title={lesson.title} lang={lang} />
        <span className="font-mono text-[12px] text-text-faint">{formatDuration(lesson.minutes, lang, fmt)}</span>
        <a
          href={`${CURRICULUM_URL}/tree/${source.commit}/phases/${phase.folder}/${lesson.dir}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[14px] font-medium text-accent no-underline"
        >
          {ui.lessonCode}
        </a>
      </div>

      <div className="lesson-prose mt-8" dangerouslySetInnerHTML={{ __html: html }} />

      <nav aria-label={ui.lessonNav} className="mt-14 grid gap-3 sm:grid-cols-2">
        {prev && (
          <Link
            href={lessonHref(prev.phase, prev.lesson, lang)}
            className="rounded-2xl border border-border bg-bg-raised p-4 no-underline shadow-card hover:border-border-strong"
          >
            <span className="block font-mono text-[12px] text-text-faint uppercase">← {ui.lessonPrev}</span>
            <span className="mt-1 block text-[15px] font-medium text-text">{prev.lesson.title}</span>
          </Link>
        )}
        {next && (
          <Link
            href={lessonHref(next.phase, next.lesson, lang)}
            className="rounded-2xl border border-border bg-bg-raised p-4 text-right no-underline shadow-card hover:border-border-strong sm:col-start-2"
          >
            <span className="block font-mono text-[12px] text-text-faint uppercase">{ui.lessonNext} →</span>
            <span className="mt-1 block text-[15px] font-medium text-text">{next.lesson.title}</span>
          </Link>
        )}
      </nav>

      <p className="mt-10 text-[13px] text-text-faint">
        {ui.lessonCredit}{" "}
        <a href={`${CURRICULUM_URL}/blob/${source.commit}/LICENSE`} target="_blank" rel="noopener noreferrer" className="text-accent">
          MIT ↗
        </a>
      </p>
    </article>
  );
}
