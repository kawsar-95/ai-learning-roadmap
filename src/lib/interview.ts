// The interview questions: the data format and a checker. The data is in
// src/content/interview.json, 3 questions for each Part in Part order. This
// file has no React and no `@/` imports, so `node --test` can use it.

import { z } from "zod";

/** Questions a Part must have. */
export const QUESTIONS_PER_PART = 3;

const Text = z.string().trim().min(1);
const QA = z.strictObject({ q: Text, a: Text });

export const InterviewFileSchema = z.strictObject({
  parts: z.array(
    z.strictObject({
      topic: Text,
      items: z.array(z.strictObject({ section: Text, en: QA, bn: QA })),
    }),
  ),
});

export type InterviewFile = z.infer<typeof InterviewFileSchema>;

/**
 * The problems of an interview file, one message each. `topics` is every
 * topic in Part order with its section ids. An empty list means the file is good.
 */
export function interviewProblems(file: InterviewFile, topics: { slug: string; sectionIds: string[] }[]): string[] {
  const problems: string[] = [];
  const known = new Set(topics.map((t) => t.slug));

  topics.forEach((topic, i) => {
    const part = file.parts[i];
    if (!part) {
      problems.push(`Part ${i + 1} ("${topic.slug}") is missing`);
      return;
    }
    if (part.topic !== topic.slug) {
      problems.push(
        known.has(part.topic)
          ? `Parts are out of order: expected "${topic.slug}" at position ${i + 1}, found "${part.topic}"`
          : `Unknown topic "${part.topic}" at position ${i + 1}`,
      );
      return;
    }
    if (part.items.length !== QUESTIONS_PER_PART) {
      problems.push(`Part "${topic.slug}" has ${part.items.length} questions, expected ${QUESTIONS_PER_PART}`);
    }
    for (const item of part.items) {
      if (!topic.sectionIds.includes(item.section)) {
        problems.push(`Part "${topic.slug}": unknown section "${item.section}"`);
      }
    }
  });

  for (const extra of file.parts.slice(topics.length)) {
    problems.push(`Unknown topic "${extra.topic}" after the last Part`);
  }
  return problems;
}
