"use client";

import Link from "next/link";
import { firstUndone, summarize } from "@/lib/progress";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { resetProgress, setDone, toggleBookmark, toggleDone, useBookmarks, useProgress } from "./useProgress";

/** A section key and the page address of that section. */
export type SectionLink = { key: string; href: string };

/** The thin bar and "done / total" count of one Part, for the Part cards. */
export function PartProgress({ keys, lang }: { keys: string[]; lang: Lang }) {
  const { done, total, percent } = summarize(useProgress(), keys);
  return (
    <div className="flex items-center gap-3" aria-label={`${UI[lang].doneLabel}: ${done} / ${total}`}>
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
      className={
        "inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-[14px] font-medium transition-colors " +
        (done
          ? "border-accent bg-accent text-on-accent hover:opacity-90"
          : "border-border-strong bg-bg-raised text-text-dim shadow-card hover:border-accent hover:text-text")
      }
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
      className={
        "inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-[14px] font-medium transition-colors " +
        (on
          ? "border-accent bg-bg-raised text-accent hover:opacity-90"
          : "border-border-strong bg-bg-raised text-text-dim shadow-card hover:border-accent hover:text-text")
      }
    >
      <span aria-hidden="true" className={on ? "" : "opacity-40"}>
        🔖
      </span>
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
      className={
        "inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-[14px] font-medium transition-colors " +
        (allDone
          ? "border-accent bg-bg-raised text-accent hover:opacity-90"
          : "border-border-strong bg-bg-raised text-text-dim shadow-card hover:border-accent hover:text-text")
      }
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
    <div className="rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-8">
      <dl className="m-0 grid grid-cols-3 gap-4">
        {stats.map(([value, label]) => (
          <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3 sm:pl-4">
            <dt className="mt-1.5 text-[13px] leading-snug text-text-faint">{label}</dt>
            <dd className="m-0 font-display text-[clamp(1.75rem,5vw,2.5rem)] font-bold leading-none text-text">
              {value}
            </dd>
          </div>
        ))}
      </dl>
      <div className="mt-6 h-2 overflow-hidden rounded-full bg-bg-raised-2">
        <div
          className="h-full rounded-full bg-linear-to-r from-accent to-accent-2 transition-[width] duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        {nextHref ? (
          <Link
            href={nextHref}
            className="rounded-[10px] bg-accent px-5 py-2.5 text-[15px] font-semibold text-on-accent no-underline shadow-card transition hover:-translate-y-0.5 hover:shadow-card-hover"
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
          className="rounded-[10px] border border-border-strong px-5 py-2.5 text-[15px] font-medium text-text-dim transition-colors hover:border-danger hover:text-danger disabled:pointer-events-none disabled:opacity-40"
        >
          {ui.startOver}
        </button>
      </div>
    </div>
  );
}
