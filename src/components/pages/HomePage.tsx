import Link from "next/link";
import { TOPICS, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { AUTHOR_GITHUB_URL, AUTHOR_LINKS, UI, contentsHref, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { Inline } from "@/components/content/Inline";
import { PartCount } from "@/components/progress/ProgressWidgets";

const TOTAL_SECTIONS = TOPICS.reduce((sum, t) => sum + t.sections.length, 0);
const TOTAL_SOURCES = TOPICS.reduce((sum, t) => sum + t.sources.length, 0);

const SECTION_TITLE =
  "font-display text-[clamp(1.75rem,4vw,2.5rem)] font-medium leading-[1.1] tracking-[-0.015em] text-balance text-text";
const BUTTON =
  "inline-flex items-center gap-2 rounded-lg px-6 py-3 text-[16px] font-semibold no-underline transition";

function partNum(lang: Lang, n: number): string {
  return fmtNum(lang, n).padStart(2, fmtNum(lang, 0));
}

/**
 * The terminal card beside the hero text: a small window showing what a Part
 * teaches, the way the Agentic QA guide shows a command. It is flat (a border
 * and no shadow) and still, and it is decoration, so it is hidden from
 * assistive tech. The dark ground is the code-block color in both themes.
 */
function CoverCard({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const part = TOPICS.find((t) => t.slug === "rag-knowledge-systems");
  return (
    <div
      aria-hidden="true"
      lang="en"
      className="mx-auto w-full max-w-[440px] overflow-hidden rounded-lg border border-[#3a424d] bg-[#22272e] font-mono text-[13px] leading-[1.65] text-[#adbac7]"
    >
      <div className="flex items-center gap-2 border-b border-[#3a424d] px-4 py-3 text-[12px] text-[#8b939e]">
        <span className="size-2.5 rounded-full bg-[#4a525d]" />
        <span className="size-2.5 rounded-full bg-[#4a525d]" />
        <span className="size-2.5 rounded-full bg-[#4a525d]" />
        {part && (
          <span className="ms-2">
            {ui.part(partNum(lang, part.part))} · {topicText(part, "en").title}
          </span>
        )}
      </div>
      <pre className="m-0 overflow-x-auto px-6 py-5 font-[inherit] text-[inherit]">
        <span className="text-[#2dd4bf]">&gt;</span> <span className="text-[#e6e6e6]">python ask.py &quot;why did my bill double?&quot;</span>
        {"\n"}retrieve  hybrid search, top 20 chunks
        {"\n"}rerank    cross-encoder, keep 3
        {"\n"}answer    cited [1] [2] [3], or &quot;not found&quot;
      </pre>
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
          <p className="m-0 mb-5 font-mono text-[12px] text-accent">{ui.coverTag}</p>
          <h1 className="mb-6 font-display text-[clamp(2.5rem,6vw,4.5rem)] font-medium leading-[1.05] tracking-[-0.025em] text-text">
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
            <a
              href="#parts"
              className={`${BUTTON} border border-border-strong bg-bg-raised text-text hover:border-accent hover:text-accent`}
            >
              {ui.seeAllParts}
              <span aria-hidden="true">→</span>
            </a>
          </div>
          <dl className="m-0 hidden max-w-lg grid-cols-4 gap-6 sm:grid">
            {stats.map(([value, label]) => (
              <div key={label} className="flex flex-col-reverse border-l-2 border-accent pl-3.5">
                <dt className="mt-1 text-[13px] leading-snug text-text-faint">{label}</dt>
                <dd className="m-0 font-display text-[26px] font-medium leading-none text-text">{value}</dd>
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
    <section id="parts" aria-labelledby="parts-heading" className="border-t border-border py-14 sm:py-16">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <p className="m-0 mb-3 font-mono text-[12px] text-accent">{ui.partsEyebrow}</p>
        <h2 id="parts-heading" className={SECTION_TITLE}>
          {ui.partsTitle}
        </h2>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.partsIntro}</p>
        <ol className="m-0 mt-8 grid list-none gap-x-12 border-b border-border p-0 md:grid-cols-2">
          {TOPICS.map((topic) => {
            const text = topicText(topic, lang);
            return (
              <li
                key={topic.slug}
                className="group relative flex items-baseline gap-4 border-t border-border py-4"
              >
                <span aria-hidden="true" className="w-9 shrink-0 font-display text-[26px] font-medium leading-none text-accent-2">
                  {partNum(lang, topic.part)}
                </span>
                <div className="min-w-0 flex-1">
                  <h3 className="m-0 font-display text-[20px] font-medium leading-snug text-balance">
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
  const links: [string, string][] = [
    [AUTHOR_LINKS.portfolio, ui.authorPortfolio],
    [AUTHOR_LINKS.linkedin, ui.authorLinkedin],
    [AUTHOR_GITHUB_URL, "GitHub"],
    [AUTHOR_LINKS.x, ui.authorX],
    [AUTHOR_LINKS.resume, ui.authorResume],
  ];
  return (
    <section aria-labelledby="author-heading" className="py-12 sm:py-14">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <h2 id="author-heading" className="m-0 border-b border-border pb-3 font-mono text-[14px] font-normal text-text-dim">
          {ui.authorHeading}
        </h2>
        <div className="mt-8 flex flex-col gap-6 sm:flex-row sm:items-start sm:gap-8">
          {/* eslint-disable-next-line @next/next/no-img-element -- static export, no image optimizer */}
          <img
            src={`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/author.jpg`}
            alt="Nuruddin Kawsar"
            width={140}
            height={140}
            className="size-[140px] shrink-0 rounded-full border border-border object-cover"
          />
          <div className="min-w-0 max-w-3xl">
            <h3 className="m-0 font-display text-[clamp(1.5rem,3vw,1.875rem)] font-semibold leading-tight text-text">
              Nuruddin Kawsar
            </h3>
            <p className="mt-2 mb-0 text-[16px] text-text-dim">{ui.authorRole}</p>
            <p className="mt-4 mb-0 text-[16px] leading-relaxed text-text-dim">{ui.authorBio}</p>
            <ul className="m-0 mt-5 flex list-none flex-wrap gap-3 p-0">
              {links
                .filter(([href]) => href)
                .map(([href, label]) => (
                  <li key={label}>
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex min-h-11 items-center rounded-lg border border-border bg-bg-raised-2 px-4 text-[15px] font-semibold text-text no-underline hover:border-accent"
                    >
                      {label}
                    </a>
                  </li>
                ))}
            </ul>
          </div>
        </div>
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
