import Link from "next/link";
import { STAGES } from "@/lib/roadmap";
import { getTopic, topicText } from "@/lib/topics";
import { CURRICULUM_URL, formatDuration, lessonKey, lessonUrl } from "@/lib/roadmap-schema";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import {
  CoreFilter,
  LessonCheck,
  PhaseDoneButton,
  RoadmapPhaseProgress,
  RoadmapSummary,
} from "@/components/progress/RoadmapWidgets";
import type { LessonLink } from "@/components/progress/RoadmapWidgets";

/** The roadmap: stages of phases, each phase a list of lessons with a done toggle. */
export function RoadmapPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const fmt = (n: number) => fmtNum(lang, n);
  const links: LessonLink[] = STAGES.flatMap((stage) =>
    stage.phases.flatMap((phase) =>
      phase.lessons.map((lesson) => ({
        key: lessonKey(phase.phase, lesson.n),
        href: lessonUrl(phase, lesson),
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
                              <a
                                href={lessonUrl(phase, lesson)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="min-w-0 flex-1 text-[15px] leading-snug text-text no-underline hover:text-accent"
                              >
                                {lesson.title}
                                <span className="sr-only"> ({ui.roadmapOpenLesson})</span>
                              </a>
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
