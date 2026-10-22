import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import type { QuizQuestion } from "../src/lib/content-schema.ts";

// The quiz text of every topic file, read from disk (topics.ts uses `@/` imports that node:test cannot load).
const dir = new URL("../src/content/", import.meta.url);
const topics = readdirSync(dir)
  .filter((name) => name.endsWith(".json") && name !== "interview.json")
  .map((name) => {
    const file = JSON.parse(readFileSync(new URL(name, dir), "utf8")) as { slug: string; quiz?: QuizQuestion[] };
    return { slug: file.slug, quiz: file.quiz ?? [] };
  });

/** Every Bangla string of a question: the question, the options, and the explanation. */
function banglaText(q: QuizQuestion): string[] {
  return [q.bn.q, q.bn.why, ...(q.kind === "mcq" ? q.bn.options : [])];
}

test("every topic has a quiz of 5 questions", () => {
  for (const { slug, quiz } of topics) assert.equal(quiz.length, 5, slug);
});

test("Bangla quiz text uses Latin digits", () => {
  for (const { slug, quiz } of topics) {
    for (const q of quiz) {
      for (const text of banglaText(q)) assert.doesNotMatch(text, /[০-৯]/, `${slug} ${q.id}: ${text}`);
    }
  }
});

test("Bangla quiz text has no leftover Latin 'Text' or 'Topic' for the page", () => {
  // The English says "this Part"; the Bangla says "এই Part".
  for (const { slug, quiz } of topics) {
    for (const q of quiz) {
      for (const text of banglaText(q)) assert.doesNotMatch(text, /\b(Text|Topic)\b/, `${slug} ${q.id}: ${text}`);
    }
  }
});

test("Bangla quiz text has none of the word-for-word phrases found in review", () => {
  const calques = ["বাক্সের বাইরেই", "ফাঁপিয়ে", "আন্তঃপ্রবিষ্ট"];
  for (const { slug, quiz } of topics) {
    for (const q of quiz) {
      for (const text of banglaText(q)) {
        for (const calque of calques) assert.ok(!text.includes(calque), `${slug} ${q.id}: ${calque}`);
      }
    }
  }
});

test("the right answers of a topic do not all sit at the same option", () => {
  for (const { slug, quiz } of topics) {
    const positions = new Set(quiz.filter((q) => q.kind === "mcq").map((q) => q.answer));
    assert.ok(positions.size > 1, `${slug}: every mcq answer is option ${[...positions][0]}`);
  }
});

test("the two true or false questions of a topic are not always false then true", () => {
  const order = topics
    .map(({ quiz }) => quiz.filter((q) => q.kind === "tf").map((q) => q.answer))
    .filter((answers) => answers.length === 2)
    .map(([first, second]) => `${first}-${second}`);
  const falseThenTrue = order.filter((o) => o === "false-true").length;
  assert.ok(falseThenTrue <= Math.ceil(order.length / 2), `${falseThenTrue} of ${order.length} topics are false then true`);
});
