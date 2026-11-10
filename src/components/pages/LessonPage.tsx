import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import "katex/dist/katex.min.css";
import source from "@/content/lessons/source.json";
import { PHASES } from "@/lib/roadmap";
import { CURRICULUM_URL, formatDuration, lessonHref, lessonKey } from "@/lib/roadmap-schema";
import { renderLessonWithOutline } from "@/lib/lesson-markdown";
import { UI, fmtNum, roadmapHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { LessonCheck } from "@/components/progress/RoadmapWidgets";
import { PrevNextLinks } from "@/components/content/PrevNext";
import { PAGE_TITLE } from "@/components/layout/PageHeader";
import { OutlineDetails } from "@/components/navigation/OutlineDetails";
import { SectionNav } from "@/components/navigation/SectionNav";

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
  const { html, outline } = renderLessonWithOutline(markdown, { folder: phase.folder, dir: lesson.dir, commit: source.commit, lang, base: BASE });
  // A lesson has about nine h2 parts, some over twenty: list them so a long lesson can be read part by part.
  const showOutline = outline.length >= 3;

  // From `xl` the lesson keeps its centred column, and "On this page" sits to its right as on a topic page.
  return (
    <div className="mx-auto w-full xl:grid xl:max-w-[1400px] xl:grid-cols-[minmax(0,1fr)_48rem_minmax(0,1fr)] xl:gap-8">
      <article className="mx-auto w-full max-w-3xl min-w-0 px-4 pt-10 pb-20 sm:px-6 sm:pt-14 xl:col-start-2">
        {/* It opens like a topic page (TopicHeader): one meta line with the actions on the right, then the title. */}
        <header>
          <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2">
            <p className="m-0 text-[14px] text-text-faint">
              <Link href={`${roadmapHref(lang)}#phase-${phase.phase}`} className="text-accent no-underline hover:underline">
                {ui.roadmap}
              </Link>
              <span aria-hidden="true" className="mx-2">
                /
              </span>
              {ui.roadmapPhase(fmt(phase.phase))} · {phase.title}
              <span aria-hidden="true" className="mx-2">
                ·
              </span>
              {formatDuration(lesson.minutes, lang, fmt)}
            </p>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
              <LessonCheck lessonKey={lessonKey(phase.phase, lesson.n)} title={lesson.title} lang={lang} />
              <a
                href={`${CURRICULUM_URL}/tree/${source.commit}/phases/${phase.folder}/${lesson.dir}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[14px] font-medium text-accent no-underline hover:underline"
              >
                {ui.lessonCode}
              </a>
            </div>
          </div>
          <h1 className={`mt-4 ${PAGE_TITLE}`}>{lesson.title}</h1>
        </header>

        {showOutline && <OutlineDetails items={outline} lang={lang} className="mt-8" />}

        <div className="lesson-prose mt-8" dangerouslySetInnerHTML={{ __html: html }} />

        <div className="mt-14">
          <PrevNextLinks
            prev={prev && { href: lessonHref(prev.phase, prev.lesson, lang), label: ui.lessonPrev, title: prev.lesson.title }}
            next={next && { href: lessonHref(next.phase, next.lesson, lang), label: ui.lessonNext, title: next.lesson.title }}
            label={ui.lessonNav}
          />
        </div>

        <p className="mt-10 text-[13px] text-text-faint">
          {ui.lessonCredit}{" "}
          <a href={`${CURRICULUM_URL}/blob/${source.commit}/LICENSE`} target="_blank" rel="noopener noreferrer" className="text-accent">
            MIT ↗
          </a>
        </p>
      </article>
      {showOutline && (
        <aside className="hidden pt-14 pr-6 xl:block">
          <SectionNav items={outline} lang={lang} />
        </aside>
      )}
    </div>
  );
}
