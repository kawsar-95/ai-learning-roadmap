import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { renderLesson, resolveLessonHref } from "../src/lib/lesson-markdown.ts";
import type { LessonSource } from "../src/lib/lesson-markdown.ts";

const src: LessonSource = { folder: "01-math", dir: "02-vectors", commit: "abc123", lang: "en" };
const content = (path: string) => new URL(`../src/content/lessons/${path}`, import.meta.url);

test("renderLesson drops the first title line and keeps the rest", () => {
  const html = renderLesson("# Vectors\n\n## Why\n\nSome text.\n", src);
  assert.doesNotMatch(html, /<h1/);
  assert.match(html, /<h2>Why<\/h2>/);
});

test("renderLesson escapes raw HTML and blocks script links", () => {
  const html = renderLesson('<script>alert(1)</script>\n\n[x](javascript:alert(1)) <img src=x onerror=alert(1)>\n', src);
  assert.doesNotMatch(html, /<script|<img src=x|javascript:/);
  assert.match(html, /&lt;script&gt;/);
});

test("renderLesson renders math with KaTeX, figures as a curriculum link, and code escaped", () => {
  const html = renderLesson("```math\nx^2\n```\n\n```figure\ns1-demo\n```\n\n```python\nif a < b: pass\n```\n", src);
  assert.match(html, /class="lesson-math"><span class="katex-display">/);
  assert.match(html, /href="https:\/\/aiengineeringfromscratch\.com\/lesson\?path=phases\/01-math\/02-vectors"/);
  assert.match(html, /code-block-lang">python<\/span><pre class="shiki"><code>if a &lt; b: pass/);
});

test("renderLesson renders $inline$ math but leaves prices and code spans alone", () => {
  const html = renderLesson("An $m \\times n$ matrix costs $5 and $10, see `$x$`.\n", src);
  assert.equal(html.match(/class="katex"/g)?.length, 1);
  assert.match(html, /costs \$5 and \$10/);
  assert.match(html, /<code>\$x\$<\/code>/);
});

test("resolveLessonHref: other lessons stay on this site, images and files pin to the copied commit", () => {
  assert.equal(resolveLessonHref("../../../05-nlp/03-bpe/docs/en.md#step", { ...src, lang: "bn", base: "/site" }), "/site/bn/roadmap/05-nlp/03-bpe/#step");
  assert.equal(
    resolveLessonHref("../assets/plot.png", src),
    "https://raw.githubusercontent.com/rohitg00/ai-engineering-from-scratch/abc123/phases/01-math/02-vectors/assets/plot.png",
  );
  assert.equal(
    resolveLessonHref("../code/main.py", src),
    "https://github.com/rohitg00/ai-engineering-from-scratch/blob/abc123/phases/01-math/02-vectors/code/main.py",
  );
  assert.equal(resolveLessonHref("https://example.com/a", src), "https://example.com/a");
  assert.equal(resolveLessonHref("#top", src), "#top");
});

test("every roadmap lesson has its copied text, renders, and links only to lessons that exist", () => {
  const { phases } = JSON.parse(readFileSync(new URL("../src/data/roadmap-lessons.json", import.meta.url), "utf8"));
  const { commit } = JSON.parse(readFileSync(content("source.json"), "utf8"));
  assert.ok(existsSync(content("LICENSE")), "the curriculum LICENSE travels with the copy");
  const pages = new Set<string>();
  for (const p of phases) for (const l of p.lessons) pages.add(`/roadmap/${p.folder}/${l.dir}/`);

  let count = 0;
  for (const p of phases) {
    for (const l of p.lessons) {
      const html = renderLesson(readFileSync(content(`${p.folder}/${l.dir}.md`), "utf8"), { folder: p.folder, dir: l.dir, commit, lang: "en" });
      assert.ok(html.length > 200, `${p.folder}/${l.dir} renders`);
      for (const [, href] of html.matchAll(/href="(\/roadmap\/[^"#]+)/g)) {
        assert.ok(pages.has(href), `${p.folder}/${l.dir} links to a missing lesson ${href}`);
      }
      count++;
    }
  }
  assert.equal(count, 542);
});
