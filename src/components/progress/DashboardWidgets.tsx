"use client";

import Link from "next/link";
import { firstUndone, resolveBookmarks } from "@/lib/progress";
import { UI, contentsHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { toggleBookmark, useBookmarks, useProgress } from "./useProgress";

/** One section as the dashboard shows it, in reading order. */
export type DashboardSection = { key: string; href: string; title: string; partTitle: string };

const CARD = "rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-7";

/** Where to read next: the first section that is not done. */
export function ContinueCard({ sections, lang }: { sections: DashboardSection[]; lang: Lang }) {
  const ui = UI[lang];
  const done = useProgress();
  const nextKey = firstUndone(
    done,
    sections.map((s) => s.key),
  );
  const next = sections.find((s) => s.key === nextKey);

  if (!next) {
    return (
      <div className={CARD}>
        <p className="m-0 text-[17px] text-text">{ui.allDone}</p>
        <Link
          href={contentsHref(lang)}
          className="mt-4 inline-block text-[15px] font-medium text-accent no-underline hover:underline"
        >
          {ui.contentsTitle} →
        </Link>
      </div>
    );
  }

  const started = sections.some((s) => done.has(s.key));
  return (
    <div className={CARD}>
      <p className="m-0 font-mono text-[12px] tracking-[0.16em] text-text-faint uppercase">{next.partTitle}</p>
      <p className="mt-2 mb-5 font-display text-[clamp(1.375rem,3vw,1.75rem)] font-bold leading-snug text-text">
        {next.title}
      </p>
      <Link
        href={next.href}
        className="inline-block rounded-[10px] bg-accent px-5 py-2.5 text-[15px] font-semibold text-on-accent no-underline shadow-card transition hover:-translate-y-0.5 hover:shadow-card-hover"
      >
        {started ? ui.continueReading : ui.startReading}
      </Link>
    </div>
  );
}

/** The bookmarked sections in reading order, each with a Remove button. */
export function BookmarkList({ sections, lang }: { sections: DashboardSection[]; lang: Lang }) {
  const ui = UI[lang];
  const byKey = new Map(sections.map((s) => [s.key, s]));
  const keys = resolveBookmarks(
    useBookmarks(),
    sections.map((s) => s.key),
  );

  if (!keys.length) return <p className="m-0 text-[16px] text-text-dim">{ui.bookmarksEmpty}</p>;

  return (
    <ul className="m-0 list-none divide-y divide-border rounded-2xl border border-border bg-bg-raised px-6 py-2 shadow-card sm:px-7 sm:py-3">
      {keys.map((key) => {
        const section = byKey.get(key)!;
        return (
          <li key={key} className="flex items-center gap-4 py-3">
            <Link href={section.href} className="min-w-0 flex-1 text-text no-underline hover:text-accent">
              <span className="block text-[15px] leading-snug">{section.title}</span>
              <span className="block text-[13px] text-text-faint">{section.partTitle}</span>
            </Link>
            <button
              type="button"
              onClick={() => toggleBookmark(key)}
              className="shrink-0 rounded-md border border-border-strong px-3 py-1.5 text-[13px] text-text-dim transition-colors hover:border-accent hover:text-text"
            >
              {ui.removeBookmark}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
