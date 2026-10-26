// Access to the lesson text for the tutor. The text comes from a function the
// host passes in, so this module has no file or framework imports.

import type { Stage } from "../lib/roadmap-schema.ts";

/** A lesson is named "<phase folder>/<lesson folder>", as in its page address. */
export const LESSON_KEY = /^\d\d-[a-z0-9-]+\/\d\d-[a-z0-9-]+$/;

/** Longer lessons are cut here (about 30k tokens). The longest one is under half of it. */
const MAX_CHARS = 120_000;

export type TutorLesson = { key: string; title: string; text: string };
export type LessonSource = { find(key: string): TutorLesson | undefined };

/** `readText(phaseFolder, lessonFolder)` returns the markdown of one lesson. */
export function createLessonSource(stages: Stage[], readText: (folder: string, dir: string) => string): LessonSource {
  const index = new Map<string, { folder: string; dir: string; title: string }>();
  for (const phase of stages.flatMap((stage) => stage.phases)) {
    for (const lesson of phase.lessons) {
      index.set(`${phase.folder}/${lesson.dir}`, { folder: phase.folder, dir: lesson.dir, title: lesson.title });
    }
  }
  return {
    find(key) {
      const entry = index.get(key);
      if (!entry) return undefined;
      return { key, title: entry.title, text: readText(entry.folder, entry.dir) };
    },
  };
}

/** The lesson as the model reads it. The tags mark it as reference material. */
export function lessonDocument(lesson: TutorLesson): string {
  const cut = lesson.text.length > MAX_CHARS;
  const text = cut ? `${lesson.text.slice(0, MAX_CHARS)}\n\n[The lesson continues; the rest is cut.]` : lesson.text;
  return `<lesson key="${lesson.key}" title="${lesson.title.replaceAll('"', "'")}">\n${text}\n</lesson>`;
}
