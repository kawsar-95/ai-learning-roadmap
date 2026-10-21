import { topicText } from "@/lib/topics";
import type { Topic } from "@/lib/topics";
import { UI, fmtNum } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { Inline } from "./Inline";

/** The opening of a topic page: Part eyebrow, title, tagline, lede, meta. */
export function TopicHeader({ topic, lang }: { topic: Topic; lang: Lang }) {
  const ui = UI[lang];
  const text = topicText(topic, lang);
  return (
    <header className="mb-10 sm:mb-12">
      <p className="font-mono text-[11px] font-medium uppercase tracking-[0.2em] text-accent">
        {ui.part(fmtNum(lang, topic.part).padStart(2, fmtNum(lang, 0)))}
      </p>
      <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-balance text-text">
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
      <p className="mt-6 inline-flex rounded-full border border-border bg-bg-raised px-3 py-1 font-mono text-xs text-text-faint shadow-card">
        {ui.topicMeta(topic.sections.length, topic.sources.length)}
      </p>
    </header>
  );
}
