import { Suspense } from "react";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { TOPIC_ORDER, getNavItems, getNeighbors, getOutline, getTopic, stripTags, topicText } from "@/lib/topics";
import { progressKey } from "@/lib/progress";
import type { Lang } from "@/lib/i18n";
import { PrevNext } from "@/components/content/PrevNext";
import { SectionView } from "@/components/content/SectionView";
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

  // Three columns like a book chapter: the Parts, the text (720px at most),
  // and "On this page". Below `lg` only the text shows; the Parts are in the
  // header drawer.
  return (
    <>
      <ReadingBar />
      <div className="mx-auto w-full max-w-[1400px] lg:grid lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-10 xl:grid-cols-[240px_minmax(0,1fr)_260px]">
        <aside className="hidden border-r border-border lg:sticky lg:top-16 lg:block lg:h-[calc(100vh-4rem)] lg:self-start lg:overflow-y-auto">
          <Suspense fallback={<SidebarList items={items} lang={lang} activeSlug={null} />}>
            <Sidebar items={items} lang={lang} />
          </Suspense>
        </aside>
        <article className="mx-auto w-full max-w-[720px] min-w-0 px-4 pt-8 pb-20 sm:px-6 sm:pt-12 lg:px-0">
          <TopicHeader topic={topic} lang={lang} />
          <div className="space-y-16 sm:space-y-20">
            {topic.sections.map((s) => (
              <SectionView key={s.id} section={s} lang={lang} doneKey={progressKey(topic.slug, s.id)} />
            ))}
          </div>
          <div className="mt-16 space-y-10">
            <Sources sources={topic.sources} lang={lang} />
            <PrevNext prev={neighbor(prev)} next={neighbor(next)} lang={lang} />
          </div>
        </article>
        <aside className="hidden py-12 pr-6 xl:block">
          <SectionNav items={getOutline(topic, lang)} lang={lang} />
        </aside>
      </div>
    </>
  );
}
