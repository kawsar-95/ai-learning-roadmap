import Link from "next/link";
import interviewData from "@/content/interview.json";
import { TOPICS, topicText } from "@/lib/topics";
import { InterviewFileSchema, interviewProblems } from "@/lib/interview";
import { UI, fmtNum, topicHref } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

// A bad file fails the build here, so a wrong section id never reaches a reader.
const interview = (() => {
  const file = InterviewFileSchema.parse(interviewData);
  const problems = interviewProblems(
    file,
    TOPICS.map((t) => ({ slug: t.slug, sectionIds: t.sections.map((s) => s.id) })),
  );
  if (problems.length) throw new Error(`src/content/interview.json: ${problems.join("; ")}`);
  return file;
})();

/** The interview questions of every Part, each with a short answer and a link to its section. */
export function InterviewPage({ lang }: { lang: Lang }) {
  const ui = UI[lang];
  return (
    <div className="mx-auto max-w-4xl px-4 pt-12 pb-20 sm:px-6 sm:pt-16">
      <header className="mb-10">
        <p className="font-mono text-[12px] font-medium tracking-[0.2em] text-accent uppercase">{ui.interview}</p>
        <h1 className="mt-3 font-display text-[clamp(2.25rem,5vw,3.25rem)] font-bold leading-[1.1] tracking-[-0.02em] text-text">
          {ui.interviewTitle}
        </h1>
        <p className="mt-3 max-w-2xl text-[17px] text-text-dim">{ui.interviewIntro}</p>
      </header>

      <ol className="m-0 list-none space-y-6 p-0">
        {interview.parts.map((part, i) => {
          const topic = TOPICS[i];
          return (
            <li
              key={part.topic}
              className="rounded-2xl border border-border bg-bg-raised p-6 shadow-card sm:p-7"
            >
              <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                <span aria-hidden="true" className="font-display text-[32px] font-bold leading-none text-accent">
                  {fmtNum(lang, topic.part).padStart(2, fmtNum(lang, 0))}
                </span>
                <h2 className="m-0 min-w-0 flex-1 font-display text-[24px] font-bold leading-snug">
                  <Link href={topicHref(topic.slug, lang)} className="text-text no-underline hover:text-accent">
                    {topicText(topic, lang).title}
                  </Link>
                </h2>
              </div>
              <div className="mt-3 divide-y divide-border">
                {part.items.map((item, index) => (
                  <details key={`${item.section}-${index}`}>
                    <summary className="cursor-pointer py-3.5 pr-2 text-[16px] font-medium leading-snug text-text marker:text-accent hover:text-accent">
                      {item[lang].q}
                    </summary>
                    <div className="pr-2 pb-4 pl-5">
                      <p className="m-0 text-[15px] leading-[1.75] text-text-dim">{item[lang].a}</p>
                      <Link
                        href={`${topicHref(topic.slug, lang)}/#${item.section}`}
                        className="mt-3 inline-block text-[14px] font-medium text-accent no-underline hover:underline"
                      >
                        {ui.readSection}
                      </Link>
                    </div>
                  </details>
                ))}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
