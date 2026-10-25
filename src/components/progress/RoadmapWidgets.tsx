"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import { firstUndone, summarize } from "@/lib/progress";
import { formatDuration } from "@/lib/roadmap-schema";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { resetRoadmap, setLessons, toggleLesson, useRoadmapProgress } from "./useProgress";

/** A lesson as the widgets need it: progress key, address on the curriculum site, and minutes. */
export type LessonLink = { key: string; href: string; minutes: number };

/** The thin bar and "done / total" count of one phase. */
export function RoadmapPhaseProgress({ keys, lang }: { keys: string[]; lang: Lang }) {
  const { done, total, percent } = summarize(useRoadmapProgress(), keys);
  return (
    <div className="flex items-center gap-3" aria-label={`${UI[lang].roadmapLessonsDone}: ${done} / ${total}`}>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-bg-raised-2">
        <div
          className="h-full rounded-full bg-linear-to-r from-accent to-accent-2 transition-[width] duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className="font-mono text-[12px] tabular-nums text-text-faint">
        {fmtNum(lang, done)}/{fmtNum(lang, total)}
      </span>
    </div>
  );
}

/** The round toggle at the start of a lesson row. */
export function LessonCheck({ lessonKey, title, lang }: { lessonKey: string; title: string; lang: Lang }) {
  const ui = UI[lang];
  const done = useRoadmapProgress().has(lessonKey);
  return (
    <button
      type="button"
      aria-pressed={done}
      aria-label={done ? ui.roadmapUnmarkLesson(title) : ui.roadmapMarkLesson(title)}
      onClick={() => toggleLesson(lessonKey)}
      className={
        "grid size-6 shrink-0 place-items-center rounded-full border text-[12px] transition-colors " +
        (done
          ? "border-accent bg-accent text-on-accent"
          : "border-border-strong text-transparent hover:border-accent hover:text-accent")
      }
    >
      <span aria-hidden="true">✓</span>
    </button>
  );
}

/** Marks every lesson of a phase done, or clears them. */
export function PhaseDoneButton({ keys, lang }: { keys: string[]; lang: Lang }) {
  const ui = UI[lang];
  const progress = useRoadmapProgress();
  const allDone = keys.every((key) => progress.has(key));
  return (
    <button
      type="button"
      aria-pressed={allDone}
      onClick={() => setLessons(keys, !allDone)}
      className={
        "rounded-lg border px-3 py-1.5 text-[13px] font-medium transition-colors " +
        (allDone
          ? "border-accent bg-bg-raised text-accent hover:opacity-90"
          : "border-border-strong bg-bg-raised text-text-dim hover:border-accent hover:text-text")
      }
    >
      {allDone ? ui.markedRead : ui.markRead}
    </button>
  );
}

/** The counters at the top of the roadmap page: done, total, time left, continue link, and reset. */
export function RoadmapSummary({ lessons, lang }: { lessons: LessonLink[]; lang: Lang }) {
  const ui = UI[lang];
  const doneSet = useRoadmapProgress();
  const keys = lessons.map((lesson) => lesson.key);
  const { done, total, percent } = summarize(doneSet, keys);
  const next = firstUndone(doneSet, keys);
  const nextHref = lessons.find((lesson) => lesson.key === next)?.href;
  const minutesLeft = lessons.reduce((sum, lesson) => sum + (doneSet.has(lesson.key) ? 0 : lesson.minutes), 0);
  const fmt = (n: number) => fmtNum(lang, n);

  const stats: [string, string][] = [
    [fmt(done), ui.roadmapLessonsDone],
    [fmt(total), ui.roadmapLessonsTotal],
    [formatDuration(minutesLeft, lang, fmt), ui.roadmapTimeLeft],
  ];

  return (
    <div className="rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-8">
      <dl className="m-0 grid grid-cols-3 gap-4">
        {stats.map(([value, label]) => (
          <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3 sm:pl-4">
            <dt className="mt-1.5 text-[13px] leading-snug text-text-faint">{label}</dt>
            <dd className="m-0 font-display text-[clamp(1.5rem,4.5vw,2.25rem)] font-bold leading-none text-text">
              {value}
            </dd>
          </div>
        ))}
      </dl>
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-label={ui.percentLabel}
        className="mt-6 h-2 overflow-hidden rounded-full bg-bg-raised-2"
      >
        <div
          className="h-full rounded-full bg-linear-to-r from-accent to-accent-2 transition-[width] duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        {nextHref ? (
          <a
            href={nextHref}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-[10px] bg-accent px-5 py-2.5 text-[15px] font-semibold text-on-accent no-underline shadow-card transition hover:-translate-y-0.5 hover:shadow-card-hover"
          >
            {ui.continueReading}
          </a>
        ) : (
          <p className="m-0 text-[15px] font-medium text-good">{ui.allDone}</p>
        )}
        <button
          type="button"
          disabled={done === 0}
          onClick={() => {
            if (window.confirm(ui.roadmapResetConfirm)) resetRoadmap();
          }}
          className="rounded-[10px] border border-border-strong px-5 py-2.5 text-[15px] font-medium text-text-dim transition-colors hover:border-danger hover:text-danger disabled:pointer-events-none disabled:opacity-40"
        >
          {ui.startOver}
        </button>
      </div>
    </div>
  );
}

/**
 * The "suggested path only" switch. The phases stay server-rendered; a phase
 * marked data-core="false" is hidden while the switch is on.
 */
export function CoreFilter({ lang, children }: { lang: Lang; children: ReactNode }) {
  const ui = UI[lang];
  const [coreOnly, setCoreOnly] = useState(false);
  return (
    <div data-core-only={coreOnly} className="group/filter">
      <label className="mt-8 flex cursor-pointer items-start gap-3 text-[15px] text-text-dim">
        <input
          type="checkbox"
          checked={coreOnly}
          onChange={(event) => setCoreOnly(event.target.checked)}
          className="mt-1 size-4 accent-accent"
        />
        <span>
          <span className="font-medium text-text">{ui.roadmapCoreOnly}</span>
          <span className="mt-0.5 block text-[13px] text-text-faint">{ui.roadmapCoreNote}</span>
        </span>
      </label>
      {children}
    </div>
  );
}
