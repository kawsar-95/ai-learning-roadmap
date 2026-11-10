import { stripTags, topicText } from "@/lib/topics";
import type { Topic } from "@/lib/topics";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { progressKey } from "@/lib/progress";
import { readingMinutes } from "@/lib/search";
import { TopicDoneButton } from "@/components/progress/ProgressWidgets";
import { PAGE_TITLE } from "@/components/layout/PageHeader";
import { Inline } from "./Inline";

/**
 * The opening of a topic page: one line with the Part, the reading time, and
 * the Part-level actions, then the title, tagline, and lede. Everything
 * else waits below, so the first screen is mostly the text to read.
 */
export function TopicHeader({ topic, lang }: { topic: Topic; lang: Lang }) {
  const ui = UI[lang];
  const text = topicText(topic, lang);
  // The voice each language shows first: বাংলা on the Bangla site, the technical one in English.
  const minutes = readingMinutes(
    topic.sections.flatMap((s) => (lang === "bn" ? s.bangla : s.body)),
    stripTags,
  );
  return (
    <header className="mb-6 sm:mb-8">
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2">
        <p className="m-0 text-[14px] text-text-faint">
          {ui.part(fmtNum(lang, topic.part))}
          <span aria-hidden="true" className="mx-2">
            ·
          </span>
          {ui.minRead(fmtNum(lang, minutes))}
        </p>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <TopicDoneButton keys={topic.sections.map((s) => progressKey(topic.slug, s.id))} lang={lang} />
          {topic.quiz && (
            <a href="#quiz" className="text-[14px] font-medium text-accent no-underline hover:underline">
              {ui.goToQuiz} →
            </a>
          )}
        </div>
      </div>
      <h1 className={`mt-4 ${PAGE_TITLE}`}>{text.title}</h1>
      {text.tagline && (
        <p className="mt-2 font-display text-[clamp(1.125rem,2.5vw,1.375rem)] italic leading-snug text-text-dim">
          {text.tagline}
        </p>
      )}
      <Inline
        as="p"
        html={text.lede}
        className="mt-4 text-[16px] leading-[1.7] text-pretty text-text-dim sm:text-[18px]"
      />
    </header>
  );
}
