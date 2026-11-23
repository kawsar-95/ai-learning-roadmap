import { stripTags } from "@/lib/topics";
import type { Topic } from "@/lib/topics";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { basicsBlocks, readingMinutes } from "@/lib/search";
import type { TopicRoadmap } from "@/lib/topic-roadmap";

const LEVEL_STYLE = {
  beginner: "border-good/40 text-good",
  intermediate: "border-accent/40 text-accent",
  advanced: "border-border-strong text-text-dim",
} as const;

/** The title of one stage target: a section, or a heading of a one-section Part. */
function targetTitle(topic: Topic, id: string, lang: Lang): string {
  const section = topic.sections.find((s) => s.id === id);
  if (section) return lang === "bn" ? section.bn.title : section.title;
  for (const s of topic.sections) {
    for (const b of s.body) if (b.type === "heading" && b.id === id) return stripTags(b.html);
  }
  return id;
}

/**
 * The learning roadmap of a Part: its sections in stages from the first step
 * to the last, with what to build in each stage. It is closed to start, so
 * the first screen stays the text to read. Each link opens its section.
 */
export function TopicRoadmapView({
  topic,
  roadmap,
  titleOf,
  lang,
}: {
  topic: Topic;
  roadmap: TopicRoadmap;
  /** The title of any Part, in the page's language, for the links to other Parts. */
  titleOf: (slug: string) => string;
  lang: Lang;
}) {
  const ui = UI[lang];
  const bangla = lang === "bn";

  // Reading time of a stage, from the voice the page shows first. A stage of
  // headings (a one-section Part) has none: a heading is not a section.
  const minutesOf = (targets: string[]): number | null => {
    const sections = targets.map((id) => topic.sections.find((s) => s.id === id));
    if (sections.some((s) => !s)) return null;
    return readingMinutes(
      sections.flatMap((s) => [...basicsBlocks(s!.basics?.[lang]), ...(bangla ? s!.bangla : s!.body)]),
      stripTags,
    );
  };
  const stageMinutes = roadmap.stages.map((stage) => minutesOf(stage.targets));
  const total = stageMinutes.every((m) => m !== null) ? stageMinutes.reduce<number>((a, m) => a + (m ?? 0), 0) : null;
  const stagesLabel = fmtNum(lang, roadmap.stages.length);
  const summary = total === null ? ui.topicRoadmapStages(stagesLabel) : ui.topicRoadmapSummary(stagesLabel, fmtNum(lang, total));

  const partLinks = (slugs: string[], label: string) =>
    slugs.length > 0 && (
      <p className="m-0 flex flex-wrap items-baseline gap-x-2 gap-y-1 text-[14px] text-text-dim">
        <span className="text-text-faint">{label}:</span>
        {slugs.map((slug, i) => (
          <span key={slug}>
            <a href={topicHref(slug, lang)} className="text-accent no-underline hover:underline">
              {titleOf(slug)}
            </a>
            {i < slugs.length - 1 && ","}
          </span>
        ))}
      </p>
    );

  return (
    <details
      lang={lang}
      className={"mb-6 rounded-lg border border-border bg-bg-raised px-4 py-2 " + (bangla ? "font-bengali" : "")}
    >
      <summary className="cursor-pointer text-[14px] text-text">
        <span className="font-medium text-accent">{ui.topicRoadmapTitle}</span>
        <span className="ml-2 text-text-faint">{summary}</span>
      </summary>
      <div className="mt-3 space-y-4 pb-2">
        <p className="m-0 text-[15px] leading-[1.7] text-text-dim">{roadmap[lang].goal}</p>
        {partLinks(roadmap.before, ui.topicRoadmapBefore)}
        <ol className="m-0 list-none space-y-5 p-0">
          {roadmap.stages.map((stage, i) => {
            const text = stage[lang];
            const minutes = stageMinutes[i];
            return (
              <li key={stage.targets[0]} className="border-l-2 border-border pl-4">
                <p className="m-0 flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px] text-text-faint">
                  <span>{ui.topicRoadmapStage(fmtNum(lang, i + 1))}</span>
                  <span className={"rounded-full border px-2 py-px text-[12px] " + LEVEL_STYLE[stage.level]}>
                    {ui.topicRoadmapLevel[stage.level]}
                  </span>
                  {minutes !== null && <span>{ui.minRead(fmtNum(lang, minutes))}</span>}
                </p>
                <h3 className="mt-1 mb-1 font-display text-[18px] leading-snug text-text">{text.title}</h3>
                <p className="m-0 text-[14px] leading-[1.7] text-text-dim">
                  <strong className="font-medium text-text">{ui.topicRoadmapGoal}:</strong> {text.goal}
                </p>
                <ol className="my-2 list-decimal space-y-1 pl-5 text-[14px] leading-snug">
                  {stage.targets.map((id) => (
                    <li key={id}>
                      <a href={`#${id}`} className="text-text no-underline hover:text-accent hover:underline">
                        {targetTitle(topic, id, lang)}
                      </a>
                    </li>
                  ))}
                </ol>
                <p className="m-0 text-[14px] leading-[1.7] text-text-dim">
                  <strong className="font-medium text-text">{ui.topicRoadmapBuild}:</strong> {text.build}
                </p>
              </li>
            );
          })}
        </ol>
        {topic.quiz && (
          <p className="m-0 text-[14px]">
            <a href="#quiz" className="text-accent no-underline hover:underline">
              {ui.topicRoadmapQuiz} →
            </a>
          </p>
        )}
        {partLinks(roadmap.after, ui.topicRoadmapAfter)}
      </div>
    </details>
  );
}
