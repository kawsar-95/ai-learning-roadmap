import Link from "next/link";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

/** A neighboring Part, with its title already in the page's language. */
export type Neighbor = { slug: string; part: number; title: string };

/** One card of a prev/next pair: the address, a short label, and the title. */
export type NeighborLink = { href: string; label: string; title: string };

const CARD =
  "group block rounded-xl border border-border bg-bg-raised px-4 py-3 no-underline transition-colors hover:border-accent motion-reduce:transition-none";
const LABEL = "block text-[13px] text-text-faint";
const TITLE = "mt-0.5 block font-display text-[17px] leading-snug text-text transition-colors group-hover:text-accent";

/**
 * Cards that link to the previous and the next page: a topic page to the
 * neighboring Parts, a lesson to the neighboring lessons. One component, so
 * both keep one look.
 */
export function PrevNextLinks({ prev, next, label }: { prev?: NeighborLink; next?: NeighborLink; label: string }) {
  if (!prev && !next) return null;
  return (
    <nav aria-label={label} className="grid gap-3 sm:grid-cols-2">
      {prev && (
        <Link href={prev.href} rel="prev" className={CARD}>
          <span className={LABEL}>← {prev.label}</span>
          <span className={TITLE}>{prev.title}</span>
        </Link>
      )}
      {next && (
        <Link href={next.href} rel="next" className={CARD + " sm:col-start-2 sm:text-right"}>
          <span className={LABEL}>{next.label} →</span>
          <span className={TITLE}>{next.title}</span>
        </Link>
      )}
    </nav>
  );
}

/** Cards that link to the previous and the next Part. */
export function PrevNext({ prev, next, lang }: { prev?: Neighbor; next?: Neighbor; lang: Lang }) {
  const ui = UI[lang];
  const link = (n?: Neighbor): NeighborLink | undefined =>
    n && { href: topicHref(n.slug, lang), label: ui.part(fmtNum(lang, n.part).padStart(2, fmtNum(lang, 0))), title: n.title };
  return <PrevNextLinks prev={link(prev)} next={link(next)} label={ui.prevNextNav} />;
}
