// Turns a copied curriculum lesson (src/content/lessons) into HTML at build time.
// No server imports besides marked and katex, so `node --test` can load it.

import { Marked } from "marked";
import type { TokenizerAndRendererExtension } from "marked";
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

/**
 * The lesson body as HTML, without its first "# Title" line (the page shows the title).
 * Raw HTML in the source is escaped: the text comes from another repository.
 * `math` blocks become KaTeX; `figure` blocks are animations that only the
 * curriculum site has, so they become a link to the lesson there.
 * shortcut: `mermaid` blocks stay as source code; add a client-side renderer if diagrams matter.
 */
export function renderLesson(markdown: string, source: LessonSource): string {
  const marked = new Marked({
    gfm: true,
    extensions: [inlineMath],
    walkTokens(token) {
      if (token.type === "link" || token.type === "image") token.href = resolveLessonHref(token.href, source);
    },
    renderer: {
      html: ({ text }) => escape(text),
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
  return marked.parse(markdown.replace(/^# .*\n+/, ""), { async: false }) as string;
}
