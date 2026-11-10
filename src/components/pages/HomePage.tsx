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
  "inline-flex items-center gap-2 rounded-[10px] px-6 py-3 text-[16px] font-semibold no-underline transition";

function partNum(lang: Lang, n: number): string {
  return fmtNum(lang, n).padStart(2, fmtNum(lang, 0));
}

/** The dark "book cover" card beside the hero text. */
function CoverCard({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const [first, accent, last] = ui.coverTitle;
  return (
    <div className="relative mx-auto flex h-[380px] w-[280px] rotate-2 flex-col justify-between overflow-hidden rounded-[20px] bg-linear-135 from-[#1a1d1f] to-[#2d3540] p-6 text-white shadow-cover transition-transform duration-400 hover:scale-[1.02] hover:rotate-0 motion-reduce:transition-none sm:h-[460px] sm:w-[350px] sm:p-7 [[data-theme=dark]_&]:border [[data-theme=dark]_&]:border-border [[data-theme=dark]_&]:from-[#1a2025] [[data-theme=dark]_&]:to-[#0d1117]">
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[radial-gradient(circle_at_80%_0%,color-mix(in_srgb,var(--accent)_35%,transparent)_0,transparent_50%),radial-gradient(circle_at_0%_100%,color-mix(in_srgb,var(--accent-2)_25%,transparent)_0,transparent_50%)]"
      />
      {/* A small network: the shape of an agent loop. */}
      <svg
        aria-hidden="true"
        viewBox="0 0 200 200"
        className="absolute top-5 right-5 w-24 opacity-30"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
      >
        <path d="M40 60 100 30 160 60 160 140 100 170 40 140Z M40 60 160 140 M160 60 40 140 M100 30 100 170" />
        {[
          [40, 60],
          [100, 30],
          [160, 60],
          [160, 140],
          [100, 170],
          [40, 140],
          [100, 100],
        ].map(([cx, cy]) => (
          <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="5" fill="currentColor" />
        ))}
      </svg>
      <p className="relative m-0 font-mono text-[10px] tracking-[0.2em] text-white/60">{ui.coverTag}</p>
      <div className="relative">
        <p lang="en" className="m-0 font-display text-[48px] font-bold leading-none tracking-[-0.03em] sm:text-[60px]">
          <span className="block">{first}</span>
          <span className="block text-[#5eead4] italic">{accent}</span>
          <span className="block">{last}</span>
        </p>
        <p className="mt-4 mb-0 text-[14px] text-white/75">{ui.coverSub}</p>
      </div>
      <div className="relative border-t border-white/15 pt-3.5">
        <p className="m-0 font-mono text-[10px] tracking-[0.2em] text-white/50">{ui.coverLabel}</p>
        <p className="m-0 mt-1 font-display text-[22px] font-semibold">
          {ui.coverValue(fmtNum(lang, TOPICS.length), fmtNum(lang, TOTAL_SECTIONS))}
        </p>
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
      {/* Two soft glows and a 64px grid behind the hero. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,color-mix(in_srgb,var(--accent)_12%,transparent)_0,transparent_40%),radial-gradient(circle_at_80%_60%,color-mix(in_srgb,var(--accent-2)_10%,transparent)_0,transparent_40%)]"
      >
        <div className="absolute inset-0 bg-[linear-gradient(var(--border)_1px,transparent_1px),linear-gradient(90deg,var(--border)_1px,transparent_1px)] bg-size-[64px_64px] opacity-60 [mask-image:linear-gradient(to_bottom,black,transparent)]" />
      </div>
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-[1.2fr_1fr] lg:gap-16">
        <div>
          <h1 className="mb-6 font-display text-[clamp(2.5rem,6vw,4.5rem)] font-bold leading-[1.05] tracking-[-0.025em] text-text">
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
              className={`${BUTTON} bg-accent text-on-accent hover:opacity-90`}
            >
              {ui.startReading}
            </Link>
          </div>
          <dl className="m-0 hidden max-w-lg grid-cols-4 gap-6 sm:grid">
            {stats.map(([value, label]) => (
              <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3.5">
                <dt className="mt-1 text-[13px] leading-snug text-text-faint">{label}</dt>
                <dd className="m-0 font-display text-[28px] font-bold leading-none text-text">{value}</dd>
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
 * one line, and the section count (or the reader's progress). Seventeen
 * boxed cards were too much to scan; a ruled list is not.
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
