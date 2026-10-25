import Link from "next/link";
import { TOPICS, sectionText, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { PartProgress, ProgressSummary, SectionCheck } from "@/components/progress/ProgressWidgets";
import type { SectionLink } from "@/components/progress/ProgressWidgets";
import { QuizBest } from "@/components/progress/DashboardWidgets";

/** Every section in reading order, with its progress key and address. */
function allSections(lang: Lang) {
  return TOPICS.map((topic) => ({
    topic,
    sections: topic.sections.map((section) => ({
      section,
      key: progressKey(topic.slug, section.id),
      href: `${topicHref(topic.slug, lang)}/#${section.id}`,
    })),
  }));
}

/** The table of contents with the reader's progress. */
export function ContentsPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const parts = allSections(lang);
  const links: SectionLink[] = parts.flatMap((p) => p.sections.map(({ key, href }) => ({ key, href })));

  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <header className="mb-10">
        <p className="font-mono text-[12px] font-medium tracking-[0.2em] text-accent uppercase">{ui.contents}</p>
        <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-text">
          {ui.contentsTitle}
        </h1>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.contentsIntro}</p>
      </header>

      <ProgressSummary sections={links} lang={lang} />

      <ol className="m-0 mt-12 list-none space-y-6 p-0">
        {parts.map(({ topic, sections }) => {
          const text = topicText(topic, lang);
          return (
            <li
              key={topic.slug}
              id={`part-${topic.part}`}
              className="scroll-mt-24 rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-7"
            >
              <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                <span aria-hidden="true" className="font-display text-[32px] font-bold leading-none text-accent">
                  {fmtNum(lang, topic.part).padStart(2, fmtNum(lang, 0))}
                </span>
                <h2 className="m-0 min-w-0 flex-1 font-display text-[24px] font-bold leading-snug">
                  <Link href={topicHref(topic.slug, lang)} className="text-text no-underline hover:text-accent">
                    {text.title}
                  </Link>
                </h2>
              </div>
              <div className="mt-4 mb-2 max-w-xs">
                <PartProgress keys={sections.map((s) => s.key)} lang={lang} />
                {topic.quiz && <QuizBest slug={topic.slug} total={topic.quiz.length} lang={lang} />}
              </div>
              <ol className="m-0 list-none divide-y divide-border p-0">
                {sections.map(({ section, key, href }) => (
                  <li key={key}>
                    <Link
                      href={href}
                      className="group flex items-center gap-3 py-2.5 text-text-dim no-underline transition-colors hover:text-text"
                    >
                      <SectionCheck sectionKey={key} lang={lang} />
                      <span className="w-7 shrink-0 font-mono text-[12px] text-text-faint">
                        {section.num.padStart(2, "0")}
                      </span>
                      <span className="min-w-0 text-[15px] leading-snug">{sectionText(section, lang).title}</span>
                      <span aria-hidden="true" className="ml-auto text-text-faint transition group-hover:translate-x-0.5 group-hover:text-accent">
                        →
                      </span>
                    </Link>
                  </li>
                ))}
              </ol>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
