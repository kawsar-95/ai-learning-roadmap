import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { LessonsFileSchema, buildRoadmap, formatDuration, lessonHref, lessonKey, lessonUrl } from "../src/lib/roadmap-schema.ts";
import { ROADMAP_STORAGE_KEY, PROGRESS_STORAGE_KEY, firstUndone, summarize } from "../src/lib/progress.ts";
import { UI, fmtNum, localizedPath, roadmapHref } from "../src/lib/i18n.ts";

const read = (name: string): unknown => JSON.parse(readFileSync(new URL(`../src/data/${name}`, import.meta.url), "utf8"));
const lessonsFile = read("roadmap-lessons.json");
const phasesFile = read("roadmap-phases.json");
const topicSlugs = readFileSync(new URL("../src/lib/topics.ts", import.meta.url), "utf8")
  .match(/^  "([a-z-]+)",$/gm)!
  .map((line) => line.trim().slice(1, -2));

test("the committed roadmap files build", () => {
  const stages = buildRoadmap(lessonsFile, phasesFile);
  const phases = stages.flatMap((stage) => stage.phases);
  assert.equal(phases.length, 20);
  assert.deepEqual(phases.map((p) => p.phase), [...Array(20).keys()], "phases run 0..19 in stage order");
  assert.equal(phases.reduce((sum, p) => sum + p.lessons.length, 0), 542);
});

test("every phase has an English and a Bangla summary, and every stage a Bangla title", () => {
  for (const stage of buildRoadmap(lessonsFile, phasesFile)) {
    assert.ok(stage.bn.title && stage.bn.summary, stage.id);
    for (const phase of stage.phases) assert.ok(phase.summary && phase.bnSummary, String(phase.phase));
  }
});

test("related topics are real Parts", () => {
  assert.equal(topicSlugs.length, 14);
  for (const phase of buildRoadmap(lessonsFile, phasesFile).flatMap((s) => s.phases)) {
    for (const slug of phase.topics) assert.ok(topicSlugs.includes(slug), `phase ${phase.phase}: ${slug}`);
  }
});

test("lesson keys are unique across the roadmap", () => {
  const keys = buildRoadmap(lessonsFile, phasesFile).flatMap((s) => s.phases.flatMap((p) => p.lessons.map((l) => lessonKey(p.phase, l.n))));
  assert.equal(new Set(keys).size, keys.length);
});

test("lessonUrl points at the lesson folder on the curriculum site", () => {
  assert.equal(
    lessonUrl({ folder: "11-llm-engineering" }, { dir: "01-prompt-engineering" }),
    "https://aiengineeringfromscratch.com/lesson?path=phases/11-llm-engineering/01-prompt-engineering",
  );
});

test("lessonHref points at the lesson page on this site, in each language", () => {
  const phase = { folder: "11-llm-engineering" };
  const lesson = { dir: "01-prompt-engineering" };
  assert.equal(lessonHref(phase, lesson, "en"), "/roadmap/11-llm-engineering/01-prompt-engineering/");
  assert.equal(lessonHref(phase, lesson, "bn"), "/bn/roadmap/11-llm-engineering/01-prompt-engineering/");
});

test("buildRoadmap rejects a phase with no summary entry, a duplicate lesson, and a phase in no stage", () => {
  const lessons = { phases: [{ phase: 0, folder: "00-a", title: "A", hours: 1, lessons: [{ n: 1, title: "x", dir: "01-x", minutes: 30 }] }] };
  const meta = {
    stages: [{ id: "s", phases: [0], title: "S", summary: "s", bn: { title: "S", summary: "s" } }],
    phases: [{ phase: 0, core: true, topics: [], summary: "a", bn: "a" }],
  };
  assert.equal(buildRoadmap(lessons, meta)[0].phases[0].minutes, 30);
  assert.throws(() => buildRoadmap(lessons, { ...meta, phases: [] }), /no entry for phase 0/);
  assert.throws(() => buildRoadmap(lessons, { ...meta, stages: [] }), /in no stage/);
  const twice = { phases: [{ ...lessons.phases[0], lessons: [lessons.phases[0].lessons[0], lessons.phases[0].lessons[0]] }] };
  assert.throws(() => buildRoadmap(twice, meta), /two lessons numbered 1/);
});

test("the lessons schema rejects a bad folder name and unknown keys", () => {
  const phase = { phase: 0, folder: "00-a", title: "A", hours: 1, lessons: [{ n: 1, title: "x", dir: "01-x", minutes: 30 }] };
  assert.throws(() => LessonsFileSchema.parse({ phases: [{ ...phase, folder: "A b" }] }));
  assert.throws(() => LessonsFileSchema.parse({ phases: [{ ...phase, extra: 1 }] }));
});

test("roadmap progress keeps its own storage key and works with summarize and firstUndone", () => {
  assert.notEqual(ROADMAP_STORAGE_KEY, PROGRESS_STORAGE_KEY);
  const all = [lessonKey(0, 1), lessonKey(0, 2), lessonKey(1, 1)];
  const done = new Set([lessonKey(0, 1)]);
  assert.deepEqual(summarize(done, all), { done: 1, total: 3, percent: 33 });
  assert.equal(firstUndone(done, all), "0/2");
});

test("formatDuration: minutes under two hours, hours above, in both languages", () => {
  const en = (n: number) => fmtNum("en", n);
  const bn = (n: number) => fmtNum("bn", n);
  assert.equal(formatDuration(75, "en", en), "75 min");
  assert.equal(formatDuration(90, "en", en), "90 min");
  assert.equal(formatDuration(210, "en", en), "3.5 h");
  assert.equal(formatDuration(75, "bn", bn), `${bn(75)} মিনিট`);
  assert.equal(formatDuration(210, "bn", bn), `${bn(3.5)} ঘণ্টা`);
});

test("roadmapHref and the language switch agree", () => {
  assert.equal(roadmapHref("en"), "/roadmap/");
  assert.equal(roadmapHref("bn"), "/bn/roadmap/");
  assert.equal(localizedPath(roadmapHref("en"), "bn"), roadmapHref("bn"));
  assert.equal(localizedPath(roadmapHref("bn"), "en"), roadmapHref("en"));
  assert.ok(UI.en.roadmapTitle && UI.bn.roadmapTitle);
});
