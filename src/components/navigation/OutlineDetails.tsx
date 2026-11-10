import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

// The same shape as OutlineItem in src/lib/topics.ts and LessonHeading in src/lib/lesson-markdown.ts.
type OutlineEntry = { id: string; title: string; level: 2 | 3 };

/**
 * The closed "On this page" list. It shows below `xl`, where the sticky
 * SectionNav column is hidden, and does the same job.
 */
export function OutlineDetails({ items, lang, className = "" }: { items: OutlineEntry[]; lang: Lang; className?: string }) {
  return (
    <details className={`rounded-lg border border-border px-4 py-2 xl:hidden ${className}`}>
      <summary className="cursor-pointer text-[14px] text-text">{UI[lang].onThisPage}</summary>
      <nav aria-label={UI[lang].onThisPage}>
        <ol className="m-0 mt-2 list-none p-0">
          {items.map((item) => (
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
  );
}
