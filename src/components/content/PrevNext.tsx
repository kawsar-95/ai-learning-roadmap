import Link from "next/link";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

/** A neighboring Part, with its title already in the page's language. */
export type Neighbor = { slug: string; part: number; title: string };

const CARD =
  "group block rounded-2xl border border-border bg-bg-raised px-5 py-4 no-underline shadow-card transition duration-200 hover:-translate-y-0.5 hover:border-accent hover:shadow-card-hover motion-reduce:transition-none";

/** Cards that link to the previous and the next Part. */
export function PrevNext({ prev, next, lang }: { prev?: Neighbor; next?: Neighbor; lang: Lang }) {
  if (!prev && !next) return null;
  const ui = UI[lang];
  const partLabel = (part: number) => ui.part(fmtNum(lang, part).padStart(2, fmtNum(lang, 0)));
  return (
    <nav aria-label={ui.prevNextNav} className="grid gap-3 sm:grid-cols-2">
      {prev && (
        <Link href={topicHref(prev.slug, lang)} rel="prev" className={CARD}>
          <span className="block font-mono text-xs uppercase tracking-[0.14em] text-text-faint">
            ← {partLabel(prev.part)}
          </span>
          <span className="mt-1 block font-display text-lg leading-snug text-text transition-colors group-hover:text-accent">
            {prev.title}
          </span>
        </Link>
      )}
      {next && (
        <Link
          href={topicHref(next.slug, lang)}
          rel="next"
          className={CARD + " sm:col-start-2 sm:text-right"}
        >
          <span className="block font-mono text-xs uppercase tracking-[0.14em] text-text-faint">
            {partLabel(next.part)} →
          </span>
          <span className="mt-1 block font-display text-lg leading-snug text-text transition-colors group-hover:text-accent">
            {next.title}
          </span>
        </Link>
      )}
    </nav>
  );
}
