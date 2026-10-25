import Link from "next/link";
import { TOPICS, getOutline, topicText } from "@/lib/topics";
import type { Topic } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { AUTHOR_GITHUB_URL, UI, contentsHref, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { Inline } from "@/components/content/Inline";
import { PartProgress } from "@/components/progress/ProgressWidgets";

const TOTAL_SECTIONS = TOPICS.reduce((sum, t) => sum + t.sections.length, 0);
const TOTAL_SOURCES = TOPICS.reduce((sum, t) => sum + t.sources.length, 0);

const EYEBROW = "font-mono text-[12px] font-medium uppercase tracking-[0.2em] text-accent";
const SECTION_TITLE =
  "mt-3 font-display text-[clamp(2rem,4.5vw,3rem)] font-bold leading-[1.08] tracking-[-0.02em] text-balance text-text";
const BUTTON =
  "inline-flex items-center gap-2 rounded-[10px] px-6 py-3 text-[16px] font-semibold no-underline transition";

/**
 * The titles to show under a Part. A multi-section topic shows its section
 * titles. A one-section topic shows the h3 titles of that section, because
 * its only section title says nothing new.
 */
function outlineTitles(topic: Topic, lang: Lang): string[] {
  const level = topic.sections.length === 1 ? 3 : 2;
  return getOutline(topic, lang)
    .filter((item) => item.level === level)
    .map((item) => item.title);
}

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
          <p className={EYEBROW}>
            {ui.homeEyebrow(fmtNum(lang, TOPICS.length), fmtNum(lang, TOTAL_SECTIONS))}
          </p>
          <h1 className="mt-5 mb-6 font-display text-[clamp(2.5rem,6vw,4.5rem)] font-bold leading-[1.05] tracking-[-0.025em] text-text">
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
              className={`${BUTTON} bg-accent text-on-accent shadow-card hover:-translate-y-0.5 hover:shadow-card-hover`}
            >
              <span aria-hidden="true">📖</span> {ui.startReading}
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

function Parts({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  return (
    <section id="parts" aria-labelledby="parts-heading" className="scroll-mt-16 bg-bg-raised-2 py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <p className={EYEBROW}>{ui.partsEyebrow}</p>
        <h2 id="parts-heading" className={SECTION_TITLE}>
          {ui.partsTitle}
        </h2>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.partsIntro}</p>
        <ol className="m-0 mt-10 grid list-none gap-5 p-0 sm:grid-cols-2 lg:grid-cols-3">
          {TOPICS.map((topic) => {
            const text = topicText(topic, lang);
            return (
              <li
                key={topic.slug}
                className="group relative flex flex-col gap-3 rounded-2xl border border-border bg-bg-raised p-7 transition duration-200 hover:-translate-y-[3px] hover:border-accent hover:shadow-card-hover motion-reduce:transition-none"
              >
                <span aria-hidden="true" className="font-display text-[36px] font-bold leading-none text-accent">
                  {partNum(lang, topic.part)}
                </span>
                <h3 className="m-0 font-display text-[22px] font-bold leading-snug text-balance">
                  <Link
                    href={topicHref(topic.slug, lang)}
                    className="text-text no-underline after:absolute after:inset-0 after:rounded-2xl after:content-[''] group-hover:text-accent"
                  >
                    {text.title}
                  </Link>
                </h3>
                {text.tagline && (
                  <p className="m-0 font-display text-[17px] leading-snug text-text-dim italic">{text.tagline}</p>
                )}
                <p className="m-0 line-clamp-3 text-[14px] leading-[1.65] text-text-dim">
                  {outlineTitles(topic, lang).join(" · ")}
                </p>
                <div className="mt-auto space-y-2.5 pt-2">
                  <p className="m-0 text-[12px] font-semibold tracking-[0.08em] text-accent uppercase">
                    {ui.sectionCount(topic.sections.length)}
                  </p>
                  {/* Above the card's stretched link, so it stays readable but not clickable. */}
                  <div className="pointer-events-none relative">
                    <PartProgress
                      keys={topic.sections.map((s) => progressKey(topic.slug, s.id))}
                      lang={lang}
                    />
                  </div>
                </div>
              </li>
            );
          })}
        </ol>
        <p className="mt-12 text-center">
          <Link
            href={contentsHref(lang)}
            className={`${BUTTON} border border-border-strong bg-bg-raised text-text hover:border-accent hover:text-accent`}
          >
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
    <section aria-labelledby="author-heading" className="py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <p className={EYEBROW}>{ui.authorEyebrow}</p>
        <h2 id="author-heading" className={SECTION_TITLE}>
          Nuruddin Kawsar
        </h2>
        <p className="mt-3 text-[17px] text-text-dim">{ui.authorBy}</p>
        <a
          href={AUTHOR_GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block text-[16px] font-medium text-accent no-underline hover:underline"
        >
          {ui.authorGithub}
        </a>
      </div>
    </section>
  );
}

/** The landing page: hero, the 14 Parts, and the author, in one language. */
export function HomePage({ lang }: { lang: Lang }) {
  return (
    <>
      <Hero lang={lang} />
      <Parts lang={lang} />
      <Author lang={lang} />
    </>
  );
}
