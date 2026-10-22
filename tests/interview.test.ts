import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { InterviewFileSchema, interviewProblems } from "../src/lib/interview.ts";
import type { InterviewFile } from "../src/lib/interview.ts";

const topics = [
  { slug: "a", sectionIds: ["s1", "s2"] },
  { slug: "b", sectionIds: ["s1"] },
];

const item = (section: string) => ({
  section,
  en: { q: "Q?", a: "A." },
  bn: { q: "প্রশ্ন?", a: "উত্তর।" },
});
const part = (topic: string, sections: string[]) => ({ topic, items: sections.map(item) });
const good = (): InterviewFile => ({
  parts: [part("a", ["s1", "s1", "s2"]), part("b", ["s1", "s1", "s1"])],
});

test("interviewProblems is empty for a good file", () => {
  assert.deepEqual(interviewProblems(good(), topics), []);
});

test("interviewProblems reports a missing Part", () => {
  const file = good();
  file.parts.pop();
  const problems = interviewProblems(file, topics);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /b/);
});

test("interviewProblems reports a Part out of order", () => {
  const file = good();
  file.parts.reverse();
  const problems = interviewProblems(file, topics);
  assert.ok(problems.length >= 1);
  assert.match(problems.join(" "), /order/);
});

test("interviewProblems reports a Part with 2 items", () => {
  const file = good();
  file.parts[0].items.pop();
  const problems = interviewProblems(file, topics);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /a/);
});

test("interviewProblems reports a Part with 4 items", () => {
  const file = good();
  file.parts[1].items.push(item("s1"));
  const problems = interviewProblems(file, topics);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /b/);
});

test("interviewProblems reports an unknown section", () => {
  const file = good();
  file.parts[1].items[0].section = "s9";
  const problems = interviewProblems(file, topics);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /b.*s9/);
});

test("interviewProblems reports an unknown topic", () => {
  const file = good();
  file.parts[1].topic = "zzz";
  const problems = interviewProblems(file, topics);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /zzz/);
});

test("InterviewFileSchema accepts a good file", () => {
  assert.deepEqual(InterviewFileSchema.parse(good()), good());
});

test("InterviewFileSchema rejects an empty question", () => {
  const file = good();
  file.parts[0].items[0].en.q = " ";
  assert.throws(() => InterviewFileSchema.parse(file));
});

test("InterviewFileSchema rejects an unknown key", () => {
  const file = { ...good(), extra: 1 };
  assert.throws(() => InterviewFileSchema.parse(file));
});

// The Part order of the site (TOPIC_ORDER in src/lib/topics.ts).
const PART_ORDER = [
  "llm-fundamentals",
  "prompt-engineering",
  "context-engineering",
  "rag-knowledge-systems",
  "agents-and-agentic-systems",
  "tool-use-and-integrations",
  "inference",
  "llmops-and-observability",
  "evaluation-engineering",
  "cost-and-performance-optimization",
  "safety-security-and-guardrails",
  "multimodal-engineering",
  "ai-application-architecture",
  "visual-learning-resources",
];

test("the real interview file has no problems", () => {
  const read = (name: string) => JSON.parse(readFileSync(new URL(`../src/content/${name}.json`, import.meta.url), "utf8"));
  const file = InterviewFileSchema.parse(read("interview"));
  const realTopics = PART_ORDER.map((slug) => ({
    slug,
    sectionIds: (read(slug).sections as { id: string }[]).map((s) => s.id),
  }));
  assert.deepEqual(interviewProblems(file, realTopics), []);
});
