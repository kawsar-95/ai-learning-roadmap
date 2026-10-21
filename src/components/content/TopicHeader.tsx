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
      <h1 className="mt-3 font-display text-[clamp(2rem,5.5vw,3rem)] font-medium leading-[1.03] tracking-[-0.025em] text-balance text-text">
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
        className="mt-5 text-base leading-relaxed text-pretty text-text-dim sm:text-lg"
      />
      <p className="mt-6 border-t border-border pt-3 font-mono text-xs text-text-faint">
        {ui.topicMeta(topic.sections.length, topic.sources.length)}
      </p>
    </header>
  );
}
