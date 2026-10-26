import Link from "next/link";
import { notFound } from "next/navigation";
import { LessonMarkdown } from "@/components/content/LessonMarkdown";
import { LessonDoneButton } from "@/components/progress/RoadmapWidgets";
import { LESSON_REFS, getLesson } from "@/lib/lessons";
import type { LessonRef } from "@/lib/lessons";
import { UPSTREAM_BLOB_URL, UPSTREAM_REPO_URL } from "@/lib/lesson-links";
import { formatDuration, lessonKey, lessonPath } from "@/lib/roadmap-schema";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

export type LessonParams = { phase: string; lesson: string };

export function lessonStaticParams(): LessonParams[] {
  return LESSON_REFS.map(({ phase, lesson }) => ({ phase: phase.folder, lesson: lesson.dir }));
}

export async function lessonMetadata(params: Promise<LessonParams>) {
  const { phase, lesson } = await params;
  const found = getLesson(phase, lesson);
  return { title: found ? `${found.lesson.title} · ${found.phase.title}` : undefined };
}

const CARD =
  "group block rounded-2xl border border-border bg-bg-raised px-5 py-4 no-underline shadow-card transition duration-200 hover:-translate-y-0.5 hover:border-accent hover:shadow-card-hover motion-reduce:transition-none";

function Neighbor({ target: neighbor, label, next }: { target: LessonRef; label: string; next?: boolean }) {
  return (
    <Link href={lessonPath(neighbor.phase, neighbor.lesson)} rel={next ? "next" : "prev"} className={CARD + (next ? " sm:col-start-2 sm:text-right" : "")}>
      <span className="block font-mono text-xs uppercase tracking-[0.14em] text-text-faint">
        {next ? `${label} →` : `← ${label}`}
      </span>
      <span className="mt-1 block font-display text-lg leading-snug text-text transition-colors group-hover:text-accent">
        {neighbor.lesson.title}
      </span>
    </Link>
  );
}

/** One lesson of the roadmap: its text, a done toggle, and links to the neighbors. Same page in both languages; only the surrounding text changes. */
export async function LessonPage({ params, lang }: { params: Promise<LessonParams>; lang: Lang }) {
  const { phase: folder, lesson: dir } = await params;
  const found = getLesson(folder, dir);
  if (!found) notFound();
  const { phase, lesson, markdown, prev, next } = found;
  const ui = UI[lang];
  const fmt = (n: number) => fmtNum(lang, n);
  const roadmap = lang === "bn" ? "/bn/roadmap/" : "/roadmap/";

  return (
    <article className="mx-auto max-w-3xl px-4 pt-10 pb-20 sm:px-6 sm:pt-14">
      <Link href={`${roadmap}#phase-${phase.phase}`} className="text-[14px] text-text-dim no-underline hover:text-accent">
        {ui.lessonBack}
      </Link>
      <p className="mt-6 mb-0 font-mono text-[12px] font-medium tracking-[0.16em] text-accent uppercase">
        {ui.lessonOf(fmt(phase.phase), String(lesson.n).padStart(2, "0"))} · {phase.title} · {formatDuration(lesson.minutes, lang, fmt)}
      </p>
      <div className="mt-3 mb-8 flex flex-wrap items-center gap-3">
        <LessonDoneButton lessonKey={lessonKey(phase.phase, lesson.n)} lang={lang} />
        <span className="text-[13px] text-text-faint">{ui.lessonInEnglish}</span>
      </div>

      <LessonMarkdown markdown={markdown} folder={folder} dir={dir} lang={lang} />

      <p className="mt-12 mb-0 text-[13px] text-text-faint">
        {ui.lessonSourceText}{" "}
        <a href={`${UPSTREAM_BLOB_URL}${folder}/${dir}`} target="_blank" rel="noopener noreferrer" className="text-accent">
          {ui.lessonCode}
        </a>{" "}
        <a href={UPSTREAM_REPO_URL} target="_blank" rel="noopener noreferrer" className="text-accent">
          GitHub ↗
        </a>
      </p>

      {(prev || next) && (
        <nav aria-label={ui.lessonNav} className="mt-8 grid gap-3 sm:grid-cols-2">
          {prev && <Neighbor target={prev} label={ui.lessonPrev} />}
          {next && <Neighbor target={next} label={ui.lessonNext} next />}
        </nav>
      )}
    </article>
  );
}
