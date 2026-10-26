import { isValidElement } from "react";
import type { ReactElement, ReactNode } from "react";
import Link from "next/link";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import { resolveLessonHref, resolveLessonImage } from "@/lib/lesson-links";
import { KNOWN_LESSONS } from "@/lib/lessons";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** The language of a fenced code block, from the class react-markdown puts on its <code>. */
function fenceLang(children: ReactNode): string | null {
  if (!isValidElement(children)) return null;
  const className = (children as ReactElement<{ className?: string }>).props.className ?? "";
  return /language-(\S+)/.exec(className)?.[1] ?? null;
}

/**
 * A lesson's markdown as styled HTML. Raw HTML in the text goes through
 * rehype-sanitize, so a script or an event handler never reaches the page.
 * Mermaid diagrams show their source: the site loads no diagram library.
 */
export function LessonMarkdown({ markdown, folder, dir, lang }: { markdown: string; folder: string; dir: string; lang: Lang }) {
  const ui = UI[lang];
  return (
    <div className="text-[16px] leading-[1.7] text-text">
      <Markdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw, rehypeSanitize]}
        components={{
          h1: ({ children }) => <h1 className="mt-0 mb-4 font-display text-[clamp(2rem,4.5vw,2.75rem)] font-bold leading-[1.15] tracking-[-0.02em]">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-12 mb-3 font-display text-[28px] font-bold leading-tight">{children}</h2>,
          h3: ({ children }) => <h3 className="mt-8 mb-2 font-display text-[22px] font-bold leading-snug">{children}</h3>,
          h4: ({ children }) => <h4 className="mt-6 mb-2 text-[17px] font-semibold">{children}</h4>,
          p: ({ children }) => <p className="my-4">{children}</p>,
          ul: ({ children }) => <ul className="my-4 list-disc space-y-1.5 pl-6">{children}</ul>,
          ol: ({ children, start }) => (
            <ol start={start} className="my-4 list-decimal space-y-1.5 pl-6">
              {children}
            </ol>
          ),
          blockquote: ({ children }) => <blockquote className="my-5 border-l-2 border-accent pl-4 text-text-dim">{children}</blockquote>,
          hr: () => <hr className="my-10 border-border" />,
          table: ({ children }) => (
            <div className="my-5 overflow-x-auto">
              <table className="w-full border-collapse text-[15px]">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="border border-border bg-bg-raised-2 px-3 py-2 text-left font-semibold">{children}</th>,
          td: ({ children }) => <td className="border border-border px-3 py-2 align-top">{children}</td>,
          code: ({ className, children }) => (
            <code className={"rounded bg-bg-raised-2 px-1.5 py-0.5 font-mono text-[0.9em] " + (className ?? "")}>{children}</code>
          ),
          pre: ({ children }) => {
            const language = fenceLang(children);
            return (
              <figure className="my-5">
                {language === "mermaid" && (
                  <figcaption className="mb-1 font-mono text-[12px] text-text-faint">{ui.lessonDiagram}</figcaption>
                )}
                <pre className="overflow-x-auto rounded-xl border border-border bg-bg-raised p-4 text-[14px] leading-relaxed [&_code]:bg-transparent [&_code]:p-0">
                  {children}
                </pre>
              </figure>
            );
          },
          a: ({ href = "", children }) => {
            const link = resolveLessonHref(href, folder, dir, KNOWN_LESSONS);
            const style = "text-accent underline underline-offset-2 hover:opacity-80";
            return link.external ? (
              <a href={link.href} target="_blank" rel="noopener noreferrer" className={style}>
                {children}
              </a>
            ) : (
              <Link href={link.href} className={style}>
                {children}
              </Link>
            );
          },
          img: ({ src, alt }) => (
            // eslint-disable-next-line @next/next/no-img-element -- static export, files in public/
            <img src={resolveLessonImage(typeof src === "string" ? src : "", folder, dir, BASE_PATH)} alt={alt ?? ""} loading="lazy" className="my-5 h-auto max-w-full rounded-lg" />
          ),
        }}
      >
        {markdown}
      </Markdown>
    </div>
  );
}
