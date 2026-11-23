import Link from "next/link";
import { TOPICS, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { AUTHOR_GITHUB_URL, UI, contentsHref, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { Inline } from "@/components/content/Inline";
import { PartCount } from "@/components/progress/ProgressWidgets";

const TOTAL_SECTIONS = TOPICS.reduce((sum, t) => sum + t.sections.length, 0);
const TOTAL_SOURCES = TOPICS.reduce((sum, t) => sum + t.sources.length, 0);

const SECTION_TITLE =
  "font-display text-[clamp(1.75rem,4vw,2.5rem)] font-bold leading-[1.1] tracking-[-0.02em] text-balance text-text";
const BUTTON =
  "inline-flex items-center gap-2 rounded-lg px-6 py-3 text-[16px] font-semibold no-underline transition";

function partNum(lang: Lang, n: number): string {
  return fmtNum(lang, n).padStart(2, fmtNum(lang, 0));
}

/**
 * The dark "book cover" card beside the hero text. It is the one card with a
 * shadow (docs/architecture.md, Design rules). It is flat otherwise: no tilt,
 * no gradient, no glows, no network drawing. Its counts are not repeated here,
 * because the stats row beside it already shows them.
 */
function CoverCard({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const [first, accent, last] = ui.coverTitle;
  return (
    <div className="mx-auto flex h-[380px] w-[280px] flex-col justify-between rounded-2xl bg-[#1a1d1f] p-6 text-white shadow-cover sm:h-[460px] sm:w-[350px] sm:p-7 [[data-theme=dark]_&]:border [[data-theme=dark]_&]:border-border [[data-theme=dark]_&]:bg-[#0d1117]">
      <p className="m-0 font-mono text-[12px] text-white/60">{ui.coverTag}</p>
      <div>
        <p lang="en" className="m-0 font-display text-[48px] font-bold leading-none tracking-[-0.03em] sm:text-[60px]">
          <span className="block">{first}</span>
          <span className="block text-[#5eead4] italic">{accent}</span>
          <span className="block">{last}</span>
        </p>
        <p className="mt-4 mb-0 text-[14px] text-white/75">{ui.coverSub}</p>
      </div>
    </div>
  );
}

function Hero({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const stats: [string, string][] = [
    [fmtNum(lang, TOPICS.length), ui.statParts],
    [fmtNum(lang, TOTAL_SECTIONS), ui.statSections],
    [`${fmtNum(lang, TOTAL_SOURCES)}+`, ui.statSources],
    [fmtNum(lang, 3), ui.statVoices],
  ];
  return (
    <section className="relative overflow-hidden pt-12 pb-16 sm:pt-20 sm:pb-20">
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-[1.2fr_1fr] lg:gap-16">
        <div>
          <h1 className="mb-6 font-display text-[clamp(2.5rem,6vw,4.5rem)] font-bold leading-[1.05] tracking-[-0.02em] text-text">
            <span className="block">{ui.heroLine1}</span>
            <span className="block text-text-dim">
              {ui.heroLine2}{" "}
              <em className="relative z-0 text-accent">
                {ui.heroAccent}
                <span
                  aria-hidden="true"
                  className="absolute inset-x-0 bottom-1 -z-10 h-1.5 bg-[color-mix(in_srgb,var(--accent)_22%,transparent)]"
                />
              </em>
            </span>
          </h1>
          <Inline
            as="p"
            html={ui.homeIntro}
            className="mb-9 max-w-xl text-[18px] leading-[1.7] text-pretty text-text-dim"
          />
          <div className="flex flex-wrap gap-3.5 sm:mb-12">
            <Link
              href={topicHref(TOPICS[0].slug, lang)}
              prefetch={false}
              className={`${BUTTON} bg-accent text-on-accent hover:opacity-90`}
            >
              {ui.startReading}
            </Link>
          </div>
          <dl className="m-0 hidden max-w-lg grid-cols-4 gap-6 sm:grid">
            {stats.map(([value, label]) => (
              <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3.5">
                <dt className="mt-1 text-[13px] leading-snug text-text-faint">{label}</dt>
                <dd className="m-0 font-display text-[26px] font-bold leading-none text-text">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
        {/* On narrow screens the cover would push the headline below the fold. */}
        <div className="hidden lg:block">
          <CoverCard lang={lang} />
        </div>
      </div>
    </section>
  );
}

/**
 * The Parts as a numbered index, like the contents of a book: number, title,
 * one line, and the section count (or the reader's progress). Boxed cards
 * were too much to scan once there were this many Parts; a ruled list is not.
 */
function Parts({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  return (
    <section id="parts" aria-labelledby="parts-heading" className="bg-bg-raised-2 py-14 sm:py-16">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <h2 id="parts-heading" className={SECTION_TITLE}>
          {ui.partsTitle}
        </h2>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.partsIntro}</p>
        <ol className="m-0 mt-8 grid list-none gap-x-12 border-b border-border-strong p-0 md:grid-cols-2">
          {TOPICS.map((topic) => {
            const text = topicText(topic, lang);
            return (
              <li
                key={topic.slug}
                className="group relative flex items-baseline gap-4 border-t border-border-strong py-4"
              >
                <span aria-hidden="true" className="w-9 shrink-0 font-display text-[26px] font-bold leading-none text-accent">
                  {partNum(lang, topic.part)}
                </span>
                <div className="min-w-0 flex-1">
                  <h3 className="m-0 font-display text-[20px] font-bold leading-snug text-balance">
                    <Link
                      href={topicHref(topic.slug, lang)}
                      // A Part's payload is over a hundred kilobytes, and
                      // this page has all eighteen Parts in view. See
                      // src/components/layout/SidebarList.tsx.
                      prefetch={false}
                      className="text-text no-underline after:absolute after:inset-0 after:content-[''] group-hover:text-accent"
                    >
                      {text.title}
                    </Link>
                  </h3>
                  {text.tagline && (
                    <p className="m-0 mt-0.5 text-[14px] leading-snug text-text-dim">{text.tagline}</p>
                  )}
                </div>
                <PartCount
                  keys={topic.sections.map((s) => progressKey(topic.slug, s.id))}
                  label={ui.sectionCount(topic.sections.length)}
                  lang={lang}
                />
              </li>
            );
          })}
        </ol>
        <p className="mt-8 mb-0">
          <Link href={contentsHref(lang)} className="text-[16px] font-medium text-accent no-underline hover:underline">
            {ui.seeContents}
          </Link>
        </p>
      </div>
    </section>
  );
}

function Author({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  return (
    <section aria-labelledby="author-heading" className="py-12 sm:py-14">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <h2 id="author-heading" className="m-0 font-display text-[clamp(1.5rem,3vw,1.875rem)] font-bold leading-tight text-text">
          Nuruddin Kawsar
        </h2>
        <p className="mt-1 mb-0 text-[16px] text-text-dim">{ui.authorBy}</p>
        <a
          href={AUTHOR_GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-block text-[16px] font-medium text-accent no-underline hover:underline"
        >
          {ui.authorGithub}
        </a>
      </div>
    </section>
  );
}

/** The landing page: hero, the Parts index, and the author, in one language. */
export function HomePage({ lang }: { lang: Lang }) {
  return (
    <>
      <Hero lang={lang} />
      <Parts lang={lang} />
      <Author lang={lang} />
    </>
  );
}
