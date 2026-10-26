// Server-only access to the lesson text. Never import this module from a
// "use client" file.
//
// The text is read at build time (the site is a static export), one file per
// lesson in src/data/lessons/, written by scripts/build-lessons.mjs.

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { PHASES } from "@/lib/roadmap";
import type { Lesson, Phase } from "@/lib/roadmap-schema";

export type LessonRef = { phase: Phase; lesson: Lesson };

export const LESSON_REFS: LessonRef[] = PHASES.flatMap((phase) => phase.lessons.map((lesson) => ({ phase, lesson })));

/** "<phase folder>/<lesson folder>" for every lesson. */
export const KNOWN_LESSONS: ReadonlySet<string> = new Set(
  LESSON_REFS.map(({ phase, lesson }) => `${phase.folder}/${lesson.dir}`),
);

export function getLesson(folder: string, dir: string): (LessonRef & { markdown: string; prev?: LessonRef; next?: LessonRef }) | undefined {
  const i = LESSON_REFS.findIndex((ref) => ref.phase.folder === folder && ref.lesson.dir === dir);
  if (i < 0) return undefined;
  const markdown = readFileSync(join(process.cwd(), "src/data/lessons", folder, `${dir}.md`), "utf8");
  return { ...LESSON_REFS[i], markdown, prev: LESSON_REFS[i - 1], next: LESSON_REFS[i + 1] };
}
