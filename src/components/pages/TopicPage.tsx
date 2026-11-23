import { Suspense } from "react";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { TOPIC_ORDER, getNavItems, getNeighbors, getOutline, getTopic, sectionText, stripTags, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { walkthroughPath } from "@/lib/walkthrough";
import { PrevNext } from "@/components/content/PrevNext";
import { SectionPager } from "@/components/content/SectionPager";
import type { Step } from "@/components/content/SectionPager";
import { SectionView } from "@/components/content/SectionView";
import { QuizSection } from "@/components/content/QuizSection";
import { Sources } from "@/components/content/Sources";
import { TopicHeader } from "@/components/content/TopicHeader";
import { TopicRoadmapView } from "@/components/content/TopicRoadmap";
import { getTopicRoadmap } from "@/lib/topic-roadmap-data";
import { OutlineDetails } from "@/components/navigation/OutlineDetails";
import { SectionNav } from "@/components/navigation/SectionNav";
import { Sidebar } from "@/components/layout/Sidebar";
import { SidebarList } from "@/components/layout/SidebarList";
import { PanelToggle } from "@/components/layout/PanelToggle";
import { ReadingBar } from "@/components/progress/ReadingBar";

export type TopicParams = { slug: string };

/** One static page per topic, for each language route. */
export function topicStaticParams(): TopicParams[] {
  return TOPIC_ORDER.map((slug) => ({ slug }));
}

export async function topicMetadata(params: Promise<TopicParams>, lang: Lang): Promise<Metadata> {
  const { slug } = await params;
  const topic = getTopic(slug);
  if (!topic) return {};
  const text = topicText(topic, lang);
  return {
    title: text.title,
    description: stripTags(text.lede).trim().slice(0, 200),
  };
}

/** A topic page in one language. */
export async function TopicPage({ params, lang }: { params: Promise<TopicParams>; lang: Lang }) {
  const { slug } = await params;
  const topic = getTopic(slug);
  if (!topic) notFound();

  const { prev, next } = getNeighbors(slug);
  const neighbor = (t?: typeof topic) => t && { slug: t.slug, part: t.part, title: topicText(t, lang).title };

  const items = getNavItems(lang);
  const roadmap = getTopicRoadmap(slug);
  const titleOf = (s: string) => items.find((i) => i.slug === s)?.title ?? s;
  const outline = getOutline(topic, lang);

  // A walk-through is not sent with its section: the section gets the path of
  // its JSON file and the player loads it when the section is shown. That keeps
  // the data out of the page's HTML and RSC payload.
  const sectionViews = topic.sections.map(({ walkthrough, ...s }) => (
    <SectionView
      key={s.id}
      section={s}
      lang={lang}
      doneKey={progressKey(topic.slug, s.id)}
      walkthroughPath={walkthrough ? walkthroughPath(topic.slug, s.id) : undefined}
    />
  ));
  const quizSection = topic.quiz && <QuizSection slug={topic.slug} questions={topic.quiz} lang={lang} />;
  // Below the sections, a rule sets the quiz apart. As a pager step it opens under the step bar, like a section.
  const quiz = quizSection && <div className="mt-6 border-t border-border pt-12 sm:pt-14">{quizSection}</div>;
  const tail = (
    <div className="mt-16 space-y-10">
      <Sources sources={topic.sources} lang={lang} />
      <PrevNext prev={neighbor(prev)} next={neighbor(next)} lang={lang} />
    </div>
  );
  // A Part with several sections shows one at a time, and the quiz last. The
  // Sources and the next-Part links go on the last step.
  const total = fmtNum(lang, topic.sections.length);
  const steps: Step[] =
    topic.sections.length > 1
      ? [
          ...topic.sections.map((s, i) => ({
            id: s.id,
            title: sectionText(s, lang).title,
            label: UI[lang].stepOf(fmtNum(lang, i + 1), total),
            node: <div className="[&>section]:pt-0 [&>section]:pb-8 sm:[&>section]:pb-10">{sectionViews[i]}</div>,
          })),
          ...(topic.quiz
            ? [{ id: "quiz", title: UI[lang].quizTitle, label: UI[lang].quizTitle, node: <>{quizSection}{tail}</> }]
            : []),
        ]
      : [];
  if (steps.length && !topic.quiz) {
    const last = steps[steps.length - 1];
    last.node = <>{last.node}{tail}</>;
  }

  // Three columns like a book chapter: the Parts, the text (720px at most),
  // and "On this page". Below `lg` only the text shows; the Parts are in the
  // header drawer. A reader can fold each side column to a rail, and the text
  // then grows to use the room (.topic-grid in globals.css, src/lib/panels.ts).
  return (
    <>
      {/* A Part with steps shows its own progress bar. */}
      {steps.length === 0 && <ReadingBar />}
      <div className="topic-grid mx-auto w-full max-w-[1400px] lg:grid lg:grid-cols-[var(--parts-w)_minmax(0,1fr)] lg:gap-10 xl:grid-cols-[var(--parts-w)_minmax(0,1fr)_var(--toc-w)]">
        <aside className="hidden lg:sticky lg:top-16 lg:block lg:h-[calc(100vh-4rem)] lg:self-start">
          {/* The button stays when the list is folded, so it sits outside the part that scrolls and hides. top-2 centres it on the "Parts" label and stops it above the first row. */}
          <PanelToggle panel="parts" lang={lang} controls="parts-panel" className="absolute top-2 right-2 z-10 bg-bg" />
          <div id="parts-panel" className="h-full overflow-y-auto parts-collapsed:hidden">
            <Suspense fallback={<SidebarList items={items} lang={lang} activeSlug={null} />}>
              <Sidebar items={items} lang={lang} />
            </Suspense>
          </div>
        </aside>
        <article className="mx-auto w-full max-w-[var(--text-w)] min-w-0 px-4 pt-6 pb-20 sm:px-6 sm:pt-10 lg:px-0">
          <TopicHeader topic={topic} lang={lang} />
          {roadmap && <TopicRoadmapView topic={topic} roadmap={roadmap} titleOf={titleOf} lang={lang} />}
          {/* The "On this page" column shows from `xl`. Below it, this closed list does the same job. */}
          {outline.length > 1 && <OutlineDetails items={outline} lang={lang} className="mb-6" />}
          {steps.length > 0 ? <SectionPager steps={steps} lang={lang} /> : (
            <>
              {sectionViews}
              {quiz}
              {tail}
            </>
          )}
        </article>
        <aside className="hidden py-12 pr-6 toc-collapsed:pr-0 xl:block">
          <SectionNav items={outline} lang={lang} />
        </aside>
      </div>
    </>
  );
}
