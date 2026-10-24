import { TOPICS, sectionText, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { BookmarkList, ContinueCard } from "@/components/progress/DashboardWidgets";
import type { DashboardSection } from "@/components/progress/DashboardWidgets";

const H2 = "mb-5 font-display text-[clamp(1.5rem,3vw,1.875rem)] font-bold leading-tight text-text";

/** The dashboard: where to continue, and the bookmarks. */
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

      <section aria-labelledby="bookmarks-heading" className="mt-14">
        <h2 id="bookmarks-heading" className={H2}>
          {ui.bookmarksTitle}
        </h2>
        <BookmarkList sections={sections} lang={lang} />
      </section>
    </div>
  );
}
