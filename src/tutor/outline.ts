// The curriculum as plain text for the tutor's system prompt. One header line
// per phase and one line per lesson. The lesson folder is included so the
// model can write exact lesson links from the rule in the system prompt.

import type { Stage } from "../lib/roadmap-schema.ts";

export function buildOutline(stages: Stage[]): string {
  return stages
    .flatMap((stage) =>
      stage.phases.map((phase) => {
        const header =
          `## Phase ${phase.phase}: ${phase.title} (${phase.core ? "suggested" : "optional"}, ` +
          `~${Math.round(phase.minutes / 60)} h, folder ${phase.folder})\n${phase.summary}`;
        const lessons = phase.lessons.map((lesson) => `${lesson.dir} | ${lesson.title} | ${lesson.minutes} min`);
        return [header, ...lessons].join("\n");
      }),
    )
    .join("\n\n");
}
