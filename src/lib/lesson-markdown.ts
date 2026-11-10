// Turns a copied curriculum lesson (src/content/lessons) into HTML at build time.
// No server imports besides marked and katex, so `node --test` can load it.

import { Marked } from "marked";
import type { Token, TokenizerAndRendererExtension } from "marked";
import katex from "katex";
import { CURRICULUM_URL, lessonHref, lessonUrl } from "./roadmap-schema.ts";
import type { Lang } from "./i18n.ts";

const RAW_URL = CURRICULUM_URL.replace("https://github.com/", "https://raw.githubusercontent.com/");
const IMAGE = /\.(png|jpe?g|gif|svg|webp|avif)$/i;
const ESCAPES: Record<string, string> = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

function escape(text: string): string {
  return text.replace(/[&<>"']/g, (c) => ESCAPES[c]);
}

// "$x^2$" in text. No space just inside the dollars and no digit after the closing one,
// so "$5 and $10" stays text.
const inlineMath: TokenizerAndRendererExtension = {
  name: "inlineMath",
  level: "inline",
  start: (src) => src.indexOf("$"),
  tokenizer(src) {
    const match = /^\$(?=\S)([^$\n`]+?)(?<=\S)\$(?![\d$])/.exec(src);
    if (match) return { type: "inlineMath", raw: match[0], text: match[1] };
  },
  renderer: (token) => katex.renderToString(token.text, { throwOnError: false }),
};

export type LessonSource = {
  folder: string;
  dir: string;
  /** The curriculum commit the copy comes from; images and code links point at it. */
  commit: string;
  lang: Lang;
  /** The site's basePath, for links to other lesson pages. */
  base?: string;
};

/** Where a link or image in the lesson points to, from the lesson's own docs/en.md. */
export function resolveLessonHref(href: string, { folder, dir, commit, lang, base = "" }: LessonSource): string {
  if (/^\s*(javascript|data|vbscript):/i.test(href)) return "#";
  if (/^([a-z][a-z0-9+.-]*:|#|\/)/i.test(href)) return href;
  const url = new URL(href, `https://repo.invalid/phases/${folder}/${dir}/docs/en.md`);
  const lesson = url.pathname.match(/^\/phases\/([^/]+)\/([^/]+)\/docs\/en\.md$/);
  if (lesson) return base + lessonHref({ folder: lesson[1] }, { dir: lesson[2] }, lang) + url.hash;
  return IMAGE.test(url.pathname) ? `${RAW_URL}/${commit}${url.pathname}` : `${CURRICULUM_URL}/blob/${commit}${url.pathname}${url.hash}`;
}

/** An h2 of a lesson, for its "On this page" list. */
export type LessonHeading = { id: string; title: string; level: 2 };

/**
 * GitHub-style heading ids: lower case, punctuation dropped, each space a
 * hyphen, and "-1", "-2" on a repeat. Use one slugger per lesson.
 */
export function headingSlugger(): (text: string) => string {
  const seen = new Map<string, number>();
  return (text) => {
    const base = text.toLowerCase().trim().replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]/gu, "").replace(/ /g, "-") || "section";
    let slug = base;
    if (seen.has(base)) {
      let n = seen.get(base) ?? 0;
      do {
        n++;
        slug = `${base}-${n}`;
      } while (seen.has(slug));
      seen.set(base, n);
    }
    if (!seen.has(slug)) seen.set(slug, 0);
    return slug;
  };
}

/** The text of inline tokens, without markup. Raw HTML adds nothing. */
function plainText(tokens: Token[]): string {
  return tokens
    .map((token) => {
      if (token.type === "html") return "";
      if ("tokens" in token && token.tokens?.length) return plainText(token.tokens);
      return "text" in token && typeof token.text === "string" ? token.text : "";
    })
    .join("");
}

/**
 * The lesson body as HTML, without its first "# Title" line (the page shows the title),
 * and the list of its h2 headings. Every heading gets an id.
 * Raw HTML in the source is escaped: the text comes from another repository.
 * `math` blocks become KaTeX; `figure` blocks are animations that only the
 * curriculum site has, so they become a link to the lesson there.
 * shortcut: `mermaid` blocks stay as source code; add a client-side renderer if diagrams matter.
 */
export function renderLessonWithOutline(markdown: string, source: LessonSource): { html: string; outline: LessonHeading[] } {
  const slug = headingSlugger();
  const outline: LessonHeading[] = [];
  const marked = new Marked({
    gfm: true,
    extensions: [inlineMath],
    walkTokens(token) {
      if (token.type === "link" || token.type === "image") token.href = resolveLessonHref(token.href, source);
    },
    renderer: {
      html: ({ text }) => escape(text),
      heading({ tokens, depth }) {
        const title = plainText(tokens).trim();
        const id = slug(title);
        if (depth === 2) outline.push({ id, title, level: 2 });
        return `<h${depth} id="${escape(id)}">${this.parser.parseInline(tokens)}</h${depth}>\n`;
      },
      code({ text, lang }) {
        const kind = (lang ?? "").trim().split(/\s/)[0];
        if (kind === "math") {
          return `<div class="lesson-math">${katex.renderToString(text, { displayMode: true, throwOnError: false })}</div>\n`;
        }
        if (kind === "figure") {
          const href = escape(lessonUrl({ folder: source.folder }, { dir: source.dir }));
          return `<p class="lesson-figure"><a href="${href}" target="_blank" rel="noopener noreferrer">Interactive figure “${escape(text.trim())}”: open it on the curriculum site ↗</a></p>\n`;
        }
        const label = kind ? `<span class="code-block-lang">${escape(kind)}</span>` : "";
        return `<div class="code-block">${label}<pre class="shiki"><code>${escape(text)}</code></pre></div>\n`;
      },
    },
  });
  const html = marked.parse(markdown.replace(/^# .*\n+/, ""), { async: false }) as string;
  return { html, outline };
}

/** The lesson body as HTML (see renderLessonWithOutline). */
export function renderLesson(markdown: string, source: LessonSource): string {
  return renderLessonWithOutline(markdown, source).html;
}
