// The tutor module. Import from here:
//
//   import { createTutorHandler, createAnthropicModel } from "./tutor/index.ts";
//   const lessons = createLessonSource(stages, (folder, dir) => readLessonMarkdown(folder, dir));
//   const handle = createTutorHandler({ stages, lessons, model: createAnthropicModel() });
//   // handle(request: Request) => Promise<Response>

export { createTutorHandler } from "./handler.ts";
export type { TutorEvent, TutorHandlerOptions, TutorModel } from "./handler.ts";
export { createAnthropicModel } from "./anthropic.ts";
export { createLessonSource, lessonDocument } from "./lessons.ts";
export type { LessonSource, TutorLesson } from "./lessons.ts";
export { buildSystem } from "./prompt.ts";
export { buildOutline } from "./outline.ts";
export { summarizeProgress } from "./progress.ts";
export { TutorRequestSchema } from "./request.ts";
