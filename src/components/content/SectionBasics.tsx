import type { BasicsText } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { Inline } from "./Inline";

/**
 * The "Start here" box of a section: the big idea in plain words, the words
 * the section uses, and the points to remember. It sits above every voice,
 * so a reader meets the words before the text uses them.
 */
export function SectionBasics({
  basics,
  sectionId,
  lang,
}: {
  basics: BasicsText | undefined;
  sectionId: string;
  lang: Lang;
}) {
  if (!basics) return null;
  const ui = UI[lang];
  const bangla = lang === "bn";
  // Letter spacing and capitals suit Latin labels only; spaced Bangla breaks the headstroke.
  const label = bangla
    ? "text-[14px] font-semibold"
    : "font-mono text-xs font-medium";
  const headingId = `${sectionId}-basics`;
  return (
    <div
      lang={lang}
      aria-labelledby={headingId}
      role="group"
      className={
        "rounded-2xl border border-border bg-bg-raised px-4 py-4 sm:px-5 sm:py-5 " +
        (bangla ? "font-bengali" : "")
      }
    >
      <h3 id={headingId} className={`${label} text-accent`}>
        {ui.basicsTitle}
      </h3>
      <Inline as="p" html={basics.idea} className="mt-2 text-[16px] leading-[1.7] text-pretty text-text sm:text-[17px]" />

      <h4 className={`${label} mt-5 text-text-faint`}>{ui.basicsWords}</h4>
      <dl className="mt-2 space-y-2.5 text-[15px] leading-relaxed">
        {basics.words.map((word, i) => (
          <div key={i} className="sm:grid sm:grid-cols-[11rem_minmax(0,1fr)] sm:gap-x-4">
            <Inline as="dt" html={word.term} className="inline font-semibold text-text sm:block" />
            <dd className="inline text-text-dim sm:block">
              <span aria-hidden="true" className="sm:hidden">
                {" — "}
              </span>
              <Inline html={word.meaning} />
            </dd>
          </div>
        ))}
      </dl>

      <h4 className={`${label} mt-5 text-text-faint`}>{ui.basicsRemember}</h4>
      <ul className="mt-2 list-disc space-y-1.5 pl-5 text-[15px] leading-relaxed text-text marker:text-accent">
        {basics.remember.map((point, i) => (
          <Inline key={i} as="li" html={point} />
        ))}
      </ul>
    </div>
  );
}
