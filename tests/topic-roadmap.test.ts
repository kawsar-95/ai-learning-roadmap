import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { TopicRoadmapsSchema, roadmapProblems } from "../src/lib/topic-roadmap.ts";
import type { TopicRoadmapsFile } from "../src/lib/topic-roadmap.ts";
import type { Block, TopicFile } from "../src/lib/content-schema.ts";

const parts = [
  { slug: "a", sectionIds: ["s1", "s2", "s3"], headingIds: [] },
  { slug: "b", sectionIds: ["s1"], headingIds: ["s1-x", "s1-y"] },
];
const stage = (targets: string[]) => ({
  level: "beginner" as const,
  en: { title: "T", goal: "G", build: "B" },
  bn: { title: "শিরোনাম", goal: "লক্ষ্য", build: "কাজ" },
  targets,
});
const roadmap = (stages: string[][], extra: Record<string, string[]> = {}) => ({
  before: [],
  after: [],
  ...extra,
  en: { goal: "Goal" },
  bn: { goal: "লক্ষ্য" },
  stages: stages.map(stage),
});
const good = (): TopicRoadmapsFile => ({
  path: [
    { en: "First", bn: "প্রথম", parts: ["a"] },
    { en: "Second", bn: "দ্বিতীয়", parts: ["b"] },
  ],
  roadmaps: { a: roadmap([["s1"], ["s3", "s2"]], { after: ["b"] }), b: roadmap([["s1-x"], ["s1-y"]]) },
});

test("a good file has no problems", () => {
  assert.deepEqual(roadmapProblems(good(), parts, true), []);
});

test("a one-section Part points at headings, not at its section", () => {
  const file = good();
  file.roadmaps.b = roadmap([["s1"], ["s1-x", "s1-y"]]);
  assert.match(roadmapProblems(file, parts).join(" "), /unknown target "s1"/);
});

test("it reports a section in no stage, in two stages, or unknown", () => {
  const file = good();
  file.roadmaps.a = roadmap([["s1", "s9"], ["s1"]]);
  const text = roadmapProblems(file, parts).join(" | ");
  assert.match(text, /unknown target "s9"/);
  assert.match(text, /"s1" is in two stages/);
  assert.match(text, /"s2" is in no stage/);
});

test("it reports an unknown Part, a self link, and a missing roadmap", () => {
  const file = good();
  file.roadmaps.a = roadmap([["s1"], ["s2", "s3"]], { before: ["zzz"], after: ["a"] });
  delete (file.roadmaps as Record<string, unknown>).b;
  const text = roadmapProblems(file, parts, true).join(" | ");
  assert.match(text, /unknown Part "zzz"/);
  assert.match(text, /points at itself/);
  assert.match(text, /b: has no roadmap/);
});

test("it reports wrong languages, tags, and Latin digits in Bangla", () => {
  const file = good();
  file.roadmaps.a.stages[0].en.goal = "লক্ষ্য";
  file.roadmaps.a.stages[0].bn.goal = "Goal";
  file.roadmaps.a.stages[1].en.build = "Use <b>this</b>";
  file.roadmaps.a.stages[1].bn.build = "৫টি নয়, 5টি, তবে BM25 চলে";
  const text = roadmapProblems(file, parts).join(" | ");
  assert.match(text, /English text has Bangla letters/);
  assert.match(text, /Bangla text has no Bangla letters/);
  assert.match(text, /has a tag/);
  assert.match(text, /Latin digits/);
  assert.equal(text.match(/Latin digits/g)?.length, 1);
});

test("it reports a Part twice on the path, unknown, or missing", () => {
  const file = good();
  file.path = [
    { en: "First", bn: "প্রথম", parts: ["a", "zzz"] },
    { en: "Second", bn: "দ্বিতীয়", parts: ["a"] },
  ];
  const text = roadmapProblems(file, parts, true).join(" | ");
  assert.match(text, /path: unknown Part "zzz"/);
  assert.match(text, /"a" is in two tracks/);
  assert.match(text, /"b" is in no track/);
});

test("the schema rejects an unknown key and a one-stage roadmap", () => {
  const file = good() as unknown as { roadmaps: { a: Record<string, unknown> } };
  assert.ok(TopicRoadmapsSchema.safeParse(file).success);
  file.roadmaps.a.extra = 1;
  assert.ok(!TopicRoadmapsSchema.safeParse(file).success);
  delete file.roadmaps.a.extra;
  file.roadmaps.a.stages = (file.roadmaps.a.stages as unknown[]).slice(0, 1);
  assert.ok(!TopicRoadmapsSchema.safeParse(file).success);
});

// The real file, against the real Parts.
const dir = new URL("../src/content/", import.meta.url);
const real = readdirSync(dir)
  .filter((name) => name.endsWith(".json") && name !== "interview.json" && name !== "source.json")
  .map((name) => JSON.parse(readFileSync(new URL(name, dir), "utf8")) as TopicFile)
  .filter((t) => Array.isArray(t.sections));
const headings = (blocks: Block[]) => blocks.flatMap((b) => (b.type === "heading" && b.level === 3 ? [b.id] : []));

test("the real roadmaps fit the real Parts", () => {
  const file = TopicRoadmapsSchema.parse(JSON.parse(readFileSync(new URL("../src/data/topic-roadmaps.json", import.meta.url), "utf8")));
  const problems = roadmapProblems(
    file,
    real.map((t) => ({ slug: t.slug, sectionIds: t.sections.map((s) => s.id), headingIds: t.sections.flatMap((s) => headings(s.body)) })),
    true, // every Part has a roadmap
  );
  assert.deepEqual(problems, []);
});
