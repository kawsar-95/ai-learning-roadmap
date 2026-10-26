// A short text summary of what the learner has finished. The progress keys
// are the ones the roadmap page stores: "<phase>/<lesson number>".

import { lessonKey } from "../lib/roadmap-schema.ts";
import type { Stage } from "../lib/roadmap-schema.ts";

export function summarizeProgress(done: readonly string[], stages: Stage[]): string {
  const doneSet = new Set(done);
  const phases = stages.flatMap((stage) => stage.phases);
  const total = phases.reduce((sum, phase) => sum + phase.lessons.length, 0);
  const finished = phases.reduce(
    (sum, phase) => sum + phase.lessons.filter((lesson) => doneSet.has(lessonKey(phase.phase, lesson.n))).length,
    0,
  );
  if (finished === 0) return `The learner has not marked any of the ${total} lessons as done yet.`;

  const lines = [`The learner has marked ${finished} of ${total} lessons as done.`];
  for (const phase of phases) {
    const count = phase.lessons.filter((lesson) => doneSet.has(lessonKey(phase.phase, lesson.n))).length;
    if (count > 0) lines.push(`Phase ${phase.phase} (${phase.title}): ${count} of ${phase.lessons.length} done.`);
  }
  for (const phase of phases) {
    const next = phase.lessons.find((lesson) => !doneSet.has(lessonKey(phase.phase, lesson.n)));
    if (next) {
      lines.push(`First lesson not done, in curriculum order: phase ${phase.phase}, ${next.dir} (${next.title}).`);
      break;
    }
  }
  return lines.join("\n");
}
