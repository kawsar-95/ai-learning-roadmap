import Link from "next/link";
import { TOPICS, sectionText, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { PartProgress } from "@/components/progress/ProgressWidgets";
import { BookmarkList, ContinueCard } from "@/components/progress/DashboardWidgets";
import type { DashboardSection } from "@/components/progress/DashboardWidgets";

const H2 = "mb-5 font-display text-[clamp(1.5rem,3vw,1.875rem)] font-bold leading-tight text-text";

/** The dashboard: where to continue, the progress of each Part, and the bookmarks. */
export function DashboardPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  const sections: DashboardSection[] = TOPICS.flatMap((topic) => {
    const partTitle = topicText(topic, lang).title;
    return topic.sections.map((section) => ({
      key: progressKey(topic.slug, section.id),
      href: `${topicHref(topic.slug, lang)}/#${section.id}`,
      title: sectionText(section, lang).title,
      partTitle,
    }));
  });

  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <header className="mb-10">
        <p className="font-mono text-[12px] font-medium tracking-[0.2em] text-accent uppercase">{ui.dashboard}</p>
        <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-text">
          {ui.dashboardTitle}
        </h1>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.dashboardIntro}</p>
      </header>

      <ContinueCard sections={sections} lang={lang} />

      <section aria-labelledby="parts-heading" className="mt-14">
        <h2 id="parts-heading" className={H2}>
          {ui.partsNav}
        </h2>
        <ol className="m-0 grid list-none gap-4 p-0 sm:grid-cols-2 lg:grid-cols-3">
          {TOPICS.map((topic) => (
            <li key={topic.slug}>
              <Link
                href={topicHref(topic.slug, lang)}
                className="block h-full rounded-2xl border border-border bg-bg-raised p-5 text-text no-underline shadow-card transition hover:-translate-y-0.5 hover:border-accent hover:shadow-card-hover"
              >
                <span aria-hidden="true" className="font-display text-[28px] font-bold leading-none text-accent">
                  {fmtNum(lang, topic.part).padStart(2, fmtNum(lang, 0))}
                </span>
                <span className="mt-2 mb-4 block font-display text-[19px] font-bold leading-snug">
                  {topicText(topic, lang).title}
                </span>
                <PartProgress keys={topic.sections.map((s) => progressKey(topic.slug, s.id))} lang={lang} />
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="bookmarks-heading" className="mt-14">
        <h2 id="bookmarks-heading" className={H2}>
          {ui.bookmarksTitle}
        </h2>
        <BookmarkList sections={sections} lang={lang} />
      </section>
    </div>
  );
}
