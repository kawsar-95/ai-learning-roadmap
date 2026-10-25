import { Suspense } from "react";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { TOPIC_ORDER, getNavItems, getNeighbors, getOutline, getTopic, sectionText, stripTags, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { PrevNext } from "@/components/content/PrevNext";
import { SectionPager } from "@/components/content/SectionPager";
import type { Step } from "@/components/content/SectionPager";
import { SectionView } from "@/components/content/SectionView";
import { QuizSection } from "@/components/content/QuizSection";
import { Sources } from "@/components/content/Sources";
import { TopicHeader } from "@/components/content/TopicHeader";
import { SectionNav } from "@/components/navigation/SectionNav";
import { Sidebar } from "@/components/layout/Sidebar";
import { SidebarList } from "@/components/layout/SidebarList";
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
  const outline = getOutline(topic, lang);

  const sectionViews = topic.sections.map((s) => (
    <SectionView key={s.id} section={s} lang={lang} doneKey={progressKey(topic.slug, s.id)} />
  ));
  const quiz = topic.quiz && (
    <div className="mt-6 border-t border-border pt-12 sm:pt-14">
      <QuizSection slug={topic.slug} questions={topic.quiz} lang={lang} />
    </div>
  );
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
            node: <div className="[&>section]:py-8 [&>section]:pt-0 sm:[&>section]:py-10">{sectionViews[i]}</div>,
          })),
          ...(topic.quiz
            ? [{ id: "quiz", title: UI[lang].quizTitle, label: UI[lang].quizTitle, node: <>{quiz}{tail}</> }]
            : []),
        ]
      : [];
  if (steps.length && !topic.quiz) {
    const last = steps[steps.length - 1];
    last.node = <>{last.node}{tail}</>;
  }

  // Three columns like a book chapter: the Parts, the text (720px at most),
  // and "On this page". Below `lg` only the text shows; the Parts are in the
  // header drawer.
  return (
    <>
      {/* A Part with steps shows its own progress bar. */}
      {steps.length === 0 && <ReadingBar />}
      <div className="mx-auto w-full max-w-[1400px] lg:grid lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-10 xl:grid-cols-[240px_minmax(0,1fr)_260px]">
        <aside className="hidden lg:sticky lg:top-16 lg:block lg:h-[calc(100vh-4rem)] lg:self-start lg:overflow-y-auto">
          <Suspense fallback={<SidebarList items={items} lang={lang} activeSlug={null} />}>
            <Sidebar items={items} lang={lang} />
          </Suspense>
        </aside>
        <article className="mx-auto w-full max-w-[720px] min-w-0 px-4 pt-8 pb-20 sm:px-6 sm:pt-12 lg:px-0">
          <TopicHeader topic={topic} lang={lang} />
          {/* The "On this page" column shows from `xl`. Below it, this closed list does the same job. */}
          {outline.length > 1 && (
            <details className="mb-10 rounded-lg border border-border px-4 py-2.5 xl:hidden">
              <summary className="cursor-pointer text-[14px] text-text">{UI[lang].onThisPage}</summary>
              <nav aria-label={UI[lang].onThisPage}>
                <ol className="m-0 mt-2 list-none p-0">
                  {outline.map((item) => (
                    <li key={item.id}>
                      <a
                        href={`#${item.id}`}
                        className={
                          "block py-1.5 leading-snug text-text-dim no-underline hover:text-text " +
                          (item.level === 3 ? "pl-4 text-[13px]" : "text-[14px]")
                        }
                      >
                        {item.title}
                      </a>
                    </li>
                  ))}
                </ol>
              </nav>
            </details>
          )}
          {steps.length > 0 ? <SectionPager steps={steps} lang={lang} /> : (
            <>
              {sectionViews}
              {quiz}
              {tail}
            </>
          )}
        </article>
        <aside className="hidden py-12 pr-6 xl:block">
          <SectionNav items={outline} lang={lang} />
        </aside>
      </div>
    </>
  );
}
