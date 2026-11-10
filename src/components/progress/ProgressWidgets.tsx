"use client";

import Link from "next/link";
import { firstUndone, summarize } from "@/lib/progress";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { resetProgress, setDone, toggleBookmark, toggleDone, useBookmarks, useProgress } from "./useProgress";

/** A section key and the page address of that section. */
export type SectionLink = { key: string; href: string };

/**
 * The small flat buttons of the reading pages: a border, no shadow, a fill only when on.
 * The roadmap's "Mark as read" uses them too (RoadmapWidgets), so both pages keep one look.
 */
export const BUTTON = "inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[13px] font-medium transition-colors";
export const BUTTON_IDLE = "border-border-strong text-text-dim hover:border-accent hover:text-text";

/**
 * The reading progress of one Part, for the Part lists. With a `label` (for
 * example "10 sections") it shows the label until the reader finishes a
 * section, then the count "3/10". Without a `label` it always shows the count.
 */
export function PartCount({ keys, label, lang }: { keys: string[]; label?: string; lang: Lang }) {
  const { done, total } = summarize(useProgress(), keys);
  if (label && done === 0) return <span className="shrink-0 text-[13px] text-text-faint">{label}</span>;
  return (
    <span className={"shrink-0 font-mono text-[12px] tabular-nums " + (done > 0 ? "text-accent" : "text-text-faint")}>
      <span aria-hidden="true">
        {fmtNum(lang, done)}/{fmtNum(lang, total)}
      </span>
      <span className="sr-only">
        {UI[lang].doneLabel}: {fmtNum(lang, done)} / {fmtNum(lang, total)}
      </span>
    </span>
  );
}

/** A check mark that shows when the section is done. */
export function SectionCheck({ sectionKey, lang }: { sectionKey: string; lang: Lang }) {
  const done = useProgress().has(sectionKey);
  return (
    <span
      className={
        "grid size-5 shrink-0 place-items-center rounded-full border text-[11px] transition-colors " +
        (done ? "border-accent bg-accent text-on-accent" : "border-border-strong text-transparent")
      }
    >
      <span aria-hidden="true">✓</span>
      {done && <span className="sr-only">{UI[lang].doneMark}</span>}
    </span>
  );
}

/** The toggle at the end of a section on a topic page. */
export function SectionDoneButton({ sectionKey, lang }: { sectionKey: string; lang: Lang }) {
  const ui = UI[lang];
  const done = useProgress().has(sectionKey);
  return (
    <button
      type="button"
      aria-pressed={done}
      onClick={() => toggleDone(sectionKey)}
      className={`${BUTTON} ${done ? "border-accent bg-accent text-on-accent hover:opacity-90" : BUTTON_IDLE}`}
    >
      <span aria-hidden="true">{done ? "✓" : "○"}</span>
      {done ? ui.markedDone : ui.markDone}
    </button>
  );
}

/** The Bookmark toggle at the end of a section. The label stays the same; the state is in aria-pressed. */
export function BookmarkButton({ sectionKey, lang }: { sectionKey: string; lang: Lang }) {
  const on = useBookmarks().has(sectionKey);
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={() => toggleBookmark(sectionKey)}
      className={`${BUTTON} ${on ? "border-accent text-accent hover:opacity-90" : BUTTON_IDLE}`}
    >
      <svg
        aria-hidden="true"
        viewBox="0 0 16 16"
        className="size-3.5"
        fill={on ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      >
        <path d="M4 2.5h8v11l-4-2.8-4 2.8z" />
      </svg>
      {UI[lang].bookmark}
    </button>
  );
}

/** The "Mark as read" toggle in a topic header: sets every section of the topic. */
export function TopicDoneButton({ keys, lang }: { keys: string[]; lang: Lang }) {
  const ui = UI[lang];
  const progress = useProgress();
  const allDone = keys.every((key) => progress.has(key));
  return (
    <button
      type="button"
      aria-pressed={allDone}
      onClick={() => setDone(keys, !allDone)}
      className={`${BUTTON} ${allDone ? "border-accent text-accent hover:opacity-90" : BUTTON_IDLE}`}
    >
      <span aria-hidden="true">✓</span>
      {allDone ? ui.markedRead : ui.markRead}
    </button>
  );
}

/** The summary on the contents page: counts, continue link, and reset. */
export function ProgressSummary({ sections, lang }: { sections: SectionLink[]; lang: Lang }) {
  const ui = UI[lang];
  const doneSet = useProgress();
  const keys = sections.map((s) => s.key);
  const { done, total, percent } = summarize(doneSet, keys);
  const next = firstUndone(doneSet, keys);
  const nextHref = sections.find((s) => s.key === next)?.href;

  const stats: [string, string][] = [
    [fmtNum(lang, done), ui.doneLabel],
    [fmtNum(lang, total), ui.totalLabel],
    [`${fmtNum(lang, percent)}%`, ui.percentLabel],
  ];

  return (
    <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
      <dl className="m-0 grid grid-cols-3 gap-4">
        {stats.map(([value, label]) => (
          <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3 sm:pl-4">
            <dt className="mt-1.5 text-[13px] leading-snug text-text-faint">{label}</dt>
            <dd className="m-0 font-display text-[clamp(1.75rem,5vw,2.25rem)] font-bold leading-none text-text">
              {value}
            </dd>
          </div>
        ))}
      </dl>
      <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-bg-raised-2">
        <div className="h-full rounded-full bg-accent transition-[width] duration-300" style={{ width: `${percent}%` }} />
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-3">
        {nextHref ? (
          <Link
            href={nextHref}
            className="rounded-lg bg-accent px-5 py-2.5 text-[15px] font-semibold text-on-accent no-underline transition-opacity hover:opacity-90"
          >
            {ui.continueReading}
          </Link>
        ) : (
          <p className="m-0 text-[15px] font-medium text-good">{ui.allDone}</p>
        )}
        <button
          type="button"
          disabled={done === 0}
          onClick={() => {
            if (window.confirm(ui.startOverConfirm)) resetProgress();
          }}
          className="rounded-lg border border-border-strong px-5 py-2.5 text-[15px] font-medium text-text-dim transition-colors hover:border-danger hover:text-danger disabled:pointer-events-none disabled:opacity-40"
        >
          {ui.startOver}
        </button>
      </div>
    </div>
  );
}
