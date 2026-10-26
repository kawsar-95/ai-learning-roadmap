import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { buildRoadmap, lessonPath } from "../src/lib/roadmap-schema.ts";
import { UPSTREAM_BLOB_URL, UPSTREAM_REPO_URL, resolveLessonHref, resolveLessonImage } from "../src/lib/lesson-links.ts";

const root = new URL("../", import.meta.url);
const read = (name: string): unknown => JSON.parse(readFileSync(new URL(`src/data/${name}`, root), "utf8"));
const phases = buildRoadmap(read("roadmap-lessons.json"), read("roadmap-phases.json")).flatMap((s) => s.phases);
const refs = phases.flatMap((phase) => phase.lessons.map((lesson) => ({ phase, lesson })));
const known = new Set(refs.map(({ phase, lesson }) => `${phase.folder}/${lesson.dir}`));
const text = (folder: string, dir: string) => readFileSync(new URL(`src/data/lessons/${folder}/${dir}.md`, root), "utf8");

test("every lesson of the roadmap has its text, and it starts with a title", () => {
  assert.equal(refs.length, 542);
  for (const { phase, lesson } of refs) {
    const markdown = text(phase.folder, lesson.dir);
    assert.match(markdown, /^# \S/, `${phase.folder}/${lesson.dir}`);
    assert.ok(markdown.length > 500, `${phase.folder}/${lesson.dir} is nearly empty`);
  }
});

test("every image a lesson uses was copied to public/lesson-assets", () => {
  let images = 0;
  for (const { phase, lesson } of refs) {
    for (const [, src] of text(phase.folder, lesson.dir).matchAll(/!\[[^\]]*\]\(([^)\s]+)\)/g)) {
      const url = resolveLessonImage(src, phase.folder, lesson.dir, "");
      assert.ok(url.startsWith("/lesson-assets/"), `${phase.folder}/${lesson.dir}: ${src}`);
      assert.ok(existsSync(new URL(`public${url}`, root)), `missing public${url}`);
      images += 1;
    }
  }
  assert.ok(images >= 80);
});

test("every relative link in a lesson resolves to a page of the site or to GitHub", () => {
  let internal = 0;
  for (const { phase, lesson } of refs) {
    for (const [, href] of text(phase.folder, lesson.dir).matchAll(/(?<!!)\[[^\]]*\]\(([^)\s]+)\)/g)) {
      const link = resolveLessonHref(href, phase.folder, lesson.dir, known);
      if (!link.external) {
        if (href.startsWith("#")) continue;
        internal += 1;
        const [, a, b] = link.href.match(/^\/roadmap\/([^/]+)\/([^/]+)\//)!;
        assert.ok(known.has(`${a}/${b}`), `${phase.folder}/${lesson.dir}: ${href} -> ${link.href}`);
      }
    }
  }
  assert.ok(internal > 20, "the cross-lesson links become internal links");
});

test("resolveLessonHref: pages, files, outside paths, absolute URLs and anchors", () => {
  const k = new Set(["11-llm-engineering/05-context-engineering", "11-llm-engineering/06-rag"]);
  const at = (href: string) => resolveLessonHref(href, "11-llm-engineering", "06-rag", k);
  assert.deepEqual(at("../../05-context-engineering/docs/en.md"), { href: "/roadmap/11-llm-engineering/05-context-engineering/", external: false });
  assert.deepEqual(at("../../05-context-engineering/"), { href: "/roadmap/11-llm-engineering/05-context-engineering/", external: false });
  assert.deepEqual(at("../../../11-llm-engineering/05-context-engineering/"), { href: "/roadmap/11-llm-engineering/05-context-engineering/", external: false });
  assert.deepEqual(at("../../05-context-engineering/docs/en.md#chunks"), { href: "/roadmap/11-llm-engineering/05-context-engineering/#chunks", external: false });
  assert.deepEqual(at("../code/main.py"), { href: `${UPSTREAM_BLOB_URL}11-llm-engineering/06-rag/code/main.py`, external: true });
  assert.deepEqual(at("../../../README.md"), { href: `${UPSTREAM_BLOB_URL}README.md`, external: true });
  assert.deepEqual(at("../../../../README.md"), { href: UPSTREAM_REPO_URL, external: true });
  assert.deepEqual(at("https://arxiv.org/abs/1"), { href: "https://arxiv.org/abs/1", external: true });
  assert.deepEqual(at("#section"), { href: "#section", external: false });
});

test("resolveLessonImage maps ../assets to the copied files and keeps the base path", () => {
  assert.equal(resolveLessonImage("../assets/a.svg", "05-nlp", "01-x", "/ai-learning-roadmap"), "/ai-learning-roadmap/lesson-assets/05-nlp/01-x/assets/a.svg");
  assert.equal(resolveLessonImage("https://x.test/a.png", "05-nlp", "01-x", "/b"), "https://x.test/a.png");
  assert.equal(resolveLessonImage("../../../../secret.png", "05-nlp", "01-x", ""), "");
});

test("lessonPath is the page of a lesson", () => {
  assert.equal(lessonPath({ folder: "11-llm-engineering" }, { dir: "01-prompt-engineering" }), "/roadmap/11-llm-engineering/01-prompt-engineering/");
});
