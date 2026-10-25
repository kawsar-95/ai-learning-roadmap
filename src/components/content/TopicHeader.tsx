import { stripTags, topicText } from "@/lib/topics";
import type { Topic } from "@/lib/topics";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { progressKey } from "@/lib/progress";
import { readingMinutes } from "@/lib/search";
import { TopicDoneButton } from "@/components/progress/ProgressWidgets";
import { Inline } from "./Inline";

const PILL = "rounded-full bg-bg-raised-2 px-3 py-1 text-[13px] font-medium text-text-dim";

/** The opening of a topic page: Part and reading-time pills, title, tagline, lede, actions. */
export function TopicHeader({ topic, lang }: { topic: Topic; lang: Lang }) {
  const ui = UI[lang];
  const text = topicText(topic, lang);
  // The voice each language shows first: বাংলা on the Bangla site, the technical one in English.
  const minutes = readingMinutes(
    topic.sections.flatMap((s) => (lang === "bn" ? s.bangla : s.body)),
    stripTags,
  );
  return (
    <header className="mb-10 sm:mb-12">
      <div className="flex flex-wrap items-center gap-2">
        <span className={PILL}>
          {ui.part(fmtNum(lang, topic.part))}
        </span>
        <span className={PILL}>
          <span aria-hidden="true">📖</span> {ui.minRead(fmtNum(lang, minutes))}
        </span>
      </div>
      <h1 className="mt-4 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-balance text-text">
        {text.title}
      </h1>
      {text.tagline && (
        <p className="mt-2 font-display text-[clamp(1.125rem,2.5vw,1.375rem)] italic leading-snug text-text-dim">
          {text.tagline}
        </p>
      )}
      <Inline
        as="p"
        html={text.lede}
        className="mt-5 text-[17px] leading-[1.75] text-pretty text-text-dim sm:text-[19px]"
      />
      <div className="mt-6 flex flex-wrap gap-2 border-y border-border py-4">
        <TopicDoneButton keys={topic.sections.map((s) => progressKey(topic.slug, s.id))} lang={lang} />
        {topic.quiz && (
          <a
            href="#quiz"
            className="inline-flex items-center gap-2 rounded-lg border border-border-strong bg-bg-raised px-4 py-2 text-[14px] font-medium text-text-dim no-underline shadow-card transition-colors hover:border-accent hover:text-text"
          >
            <span aria-hidden="true">📝</span>
            {ui.goToQuiz}
          </a>
        )}
      </div>
    </header>
  );
}
