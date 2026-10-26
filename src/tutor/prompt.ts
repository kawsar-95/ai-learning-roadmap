import { CURRICULUM_URL, LESSON_BASE_URL } from "../lib/roadmap-schema.ts";
import type { Stage } from "../lib/roadmap-schema.ts";
import { buildOutline } from "./outline.ts";
import { summarizeProgress } from "./progress.ts";

export type SystemBlock = { type: "text"; text: string; cache_control?: { type: "ephemeral" } };

const INSTRUCTIONS = `You are a tutor for the "AI Engineering from Scratch" curriculum (${CURRICULUM_URL}). It has 20 phases of lessons, listed below. Help the learner decide what to study next, understand how the phases connect, and prepare for a lesson.

How to answer:
- The outline below is your only knowledge of the curriculum. It has phase summaries and lesson titles, not lesson text. Recommend only lessons that appear in it, and say "phase N, lesson NN: title". Never invent a lesson.
- When you point to a lesson, give its link: ${LESSON_BASE_URL}<folder>/<lesson folder>, using the phase folder from the phase header and the lesson folder from the first column of the lesson line.
- Use the learner's progress (given after the outline) to pick the next step. Suggested phases are the core path for an applied AI engineer; optional phases are depth the learner can skip.
- You may explain AI concepts from general knowledge. Say so when the answer does not come from the curriculum, and do not claim that a lesson covers something its title does not show.
- Keep answers short and concrete. Ask one question back when the learner's goal is unclear.
- Reply in the language the learner writes in.`;

/**
 * The two system blocks. The first one never changes between requests, so it
 * carries the cache breakpoint. The learner's progress changes often and
 * comes after it, so it does not invalidate the cached prefix.
 */
export function buildSystem(stages: Stage[], done: readonly string[]): SystemBlock[] {
  return [
    {
      type: "text",
      text: `${INSTRUCTIONS}\n\n# Curriculum outline\nLesson lines are: lesson folder | title | length.\n\n${buildOutline(stages)}`,
      cache_control: { type: "ephemeral" },
    },
    { type: "text", text: `# Learner progress\n${summarizeProgress(done, stages)}` },
  ];
}
