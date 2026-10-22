// Quiz scoring and the saved best scores. The scores live in localStorage as
// a JSON object: { "<topic slug>": { best, total } }. This file has no React
// and no server imports, so client components and `node --test` can use it.

import type { QuizQuestion } from "./content-schema.ts";

/** The localStorage key that holds the best quiz score of each topic. */
export const QUIZ_SCORES_STORAGE_KEY = "quiz-scores";

export type QuizScores = Record<string, { best: number; total: number }>;

/** The chosen option index (`mcq`) or boolean (`tf`) for each question id. */
export type QuizAnswers = Record<string, number | boolean>;

/** The number of right answers. A missing answer, or one of the wrong type, is wrong. */
export function scoreQuiz(questions: QuizQuestion[], answers: QuizAnswers): { correct: number; total: number } {
  const correct = questions.filter((q) => answers[q.id] === q.answer).length;
  return { correct, total: questions.length };
}

/** The stored scores. Bad text, a wrong shape, or an invalid entry gives no entry. */
export function parseScores(raw: string | null): QuizScores {
  if (!raw) return {};
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    return {};
  }
  if (typeof value !== "object" || value === null || Array.isArray(value)) return {};
  const scores: QuizScores = {};
  for (const [slug, entry] of Object.entries(value)) {
    const { best, total } = (entry ?? {}) as { best?: unknown; total?: unknown };
    if (Number.isInteger(best) && Number.isInteger(total) && (best as number) >= 0 && (best as number) <= (total as number)) {
      scores[slug] = { best: best as number, total: total as number };
    }
  }
  return scores;
}

/**
 * A new set of scores with this attempt recorded. The best score stays unless
 * this one is higher, or the quiz changed size (then the old best means nothing).
 */
export function recordBest(scores: QuizScores, slug: string, correct: number, total: number): QuizScores {
  const old = scores[slug];
  if (old && old.total === total && old.best >= correct) return scores;
  return { ...scores, [slug]: { best: correct, total } };
}
