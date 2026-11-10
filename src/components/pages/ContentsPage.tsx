import Link from "next/link";
import { TOPICS, sectionText, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { PartCount, ProgressSummary, SectionCheck } from "@/components/progress/ProgressWidgets";
import type { SectionLink } from "@/components/progress/ProgressWidgets";
import { QuizBest } from "@/components/progress/DashboardWidgets";
import { PageHeader } from "@/components/layout/PageHeader";

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

/**
 * The table of contents with the reader's progress. Each Part is a ruled
 * heading with its sections in two columns, not a box of rows.
 */
export function ContentsPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const parts = allSections(lang);
  const links: SectionLink[] = parts.flatMap((p) => p.sections.map(({ key, href }) => ({ key, href })));

  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <PageHeader title={ui.contentsTitle} intro={ui.contentsIntro} />

      <ProgressSummary sections={links} lang={lang} />

      <ol className="m-0 mt-12 list-none space-y-10 p-0">
        {parts.map(({ topic, sections }) => {
          const text = topicText(topic, lang);
          return (
            <li key={topic.slug} id={`part-${topic.part}`} className="border-t border-border-strong pt-5">
              <div className="flex items-baseline gap-4">
                <span aria-hidden="true" className="font-display text-[26px] font-bold leading-none text-accent">
                  {fmtNum(lang, topic.part).padStart(2, fmtNum(lang, 0))}
                </span>
                <h2 className="m-0 min-w-0 flex-1 font-display text-[22px] font-bold leading-snug">
                  <Link href={topicHref(topic.slug, lang)} className="text-text no-underline hover:text-accent">
                    {text.title}
                  </Link>
                </h2>
                <PartCount keys={sections.map((s) => s.key)} lang={lang} />
              </div>
              {topic.quiz && <QuizBest slug={topic.slug} total={topic.quiz.length} lang={lang} />}
              <ol className="m-0 mt-3 grid list-none gap-x-10 p-0 sm:grid-cols-2">
                {sections.map(({ section, key, href }) => (
                  <li key={key}>
                    <Link
                      href={href}
                      className="group flex items-start gap-3 py-1.5 text-text-dim no-underline transition-colors hover:text-text"
                    >
                      <SectionCheck sectionKey={key} lang={lang} />
                      <span className="w-7 shrink-0 font-mono text-[12px] leading-5 text-text-faint">
                        {section.num.padStart(2, "0")}
                      </span>
                      <span className="min-w-0 text-[15px] leading-5">{sectionText(section, lang).title}</span>
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
