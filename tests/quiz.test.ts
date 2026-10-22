import { test } from "node:test";
import assert from "node:assert/strict";
import type { QuizQuestion } from "../src/lib/content-schema.ts";
import { BOOKMARKS_STORAGE_KEY, PROGRESS_STORAGE_KEY } from "../src/lib/progress.ts";
import { QUIZ_SCORES_STORAGE_KEY, parseScores, recordBest, scoreQuiz } from "../src/lib/quiz.ts";

const mcq = (id: string, answer: number): QuizQuestion => ({
  id,
  kind: "mcq",
  answer,
  en: { q: "Q?", options: ["a", "b", "c"], why: "w" },
  bn: { q: "প্রশ্ন?", options: ["ক", "খ", "গ"], why: "ক" },
});
const questions: QuizQuestion[] = [
  mcq("q1", 1),
  { id: "q2", kind: "tf", answer: true, en: { q: "T?", why: "w" }, bn: { q: "স?", why: "ক" } },
  mcq("q3", 0),
];

test("scoreQuiz counts all right answers", () => {
  assert.deepEqual(scoreQuiz(questions, { q1: 1, q2: true, q3: 0 }), { correct: 3, total: 3 });
});

test("scoreQuiz counts a missing answer as wrong", () => {
  assert.deepEqual(scoreQuiz(questions, { q1: 1, q2: true }), { correct: 2, total: 3 });
});

test("scoreQuiz treats a wrong type as wrong", () => {
  assert.deepEqual(scoreQuiz(questions, { q1: 1, q2: 1, q3: 0 }), { correct: 2, total: 3 });
});

test("parseScores reads a valid entry", () => {
  assert.deepEqual(parseScores('{"inference":{"best":4,"total":5}}'), { inference: { best: 4, total: 5 } });
});

test("parseScores ignores bad JSON and wrong shapes", () => {
  for (const raw of [null, "", "{x", "[]", "null", "5", '"s"']) {
    assert.deepEqual(parseScores(raw), {}, String(raw));
  }
});

test("parseScores drops an entry with best above total, a fraction, or a negative", () => {
  const raw = JSON.stringify({
    ok: { best: 2, total: 3 },
    over: { best: 4, total: 3 },
    fraction: { best: 1.5, total: 3 },
    negative: { best: -1, total: 3 },
    missing: { best: 1 },
  });
  assert.deepEqual(parseScores(raw), { ok: { best: 2, total: 3 } });
});

test("recordBest stores a first score", () => {
  assert.deepEqual(recordBest({}, "inference", 3, 5), { inference: { best: 3, total: 5 } });
});

test("recordBest raises the best", () => {
  assert.deepEqual(recordBest({ inference: { best: 3, total: 5 } }, "inference", 4, 5), { inference: { best: 4, total: 5 } });
});

test("recordBest keeps the higher best", () => {
  assert.deepEqual(recordBest({ inference: { best: 4, total: 5 } }, "inference", 2, 5), { inference: { best: 4, total: 5 } });
});

test("recordBest replaces the entry when the total changed", () => {
  assert.deepEqual(recordBest({ inference: { best: 5, total: 5 } }, "inference", 2, 6), { inference: { best: 2, total: 6 } });
});

test("recordBest does not change its input", () => {
  const scores = { inference: { best: 3, total: 5 } };
  recordBest(scores, "inference", 5, 5);
  recordBest(scores, "rag", 1, 2);
  assert.deepEqual(scores, { inference: { best: 3, total: 5 } });
});

test("the quiz-scores key differs from the progress and bookmarks keys", () => {
  assert.equal(QUIZ_SCORES_STORAGE_KEY, "quiz-scores");
  assert.notEqual(QUIZ_SCORES_STORAGE_KEY, PROGRESS_STORAGE_KEY);
  assert.notEqual(QUIZ_SCORES_STORAGE_KEY, BOOKMARKS_STORAGE_KEY);
});
