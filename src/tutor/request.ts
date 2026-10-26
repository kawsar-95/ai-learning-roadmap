import { z } from "zod";
import { LESSON_KEY } from "./lessons.ts";

export const MAX_MESSAGES = 20;
export const MAX_CONTENT = 4000;

export const TutorRequestSchema = z
  .strictObject({
    messages: z
      .array(z.strictObject({ role: z.enum(["user", "assistant"]), content: z.string().min(1).max(MAX_CONTENT) }))
      .min(1)
      .max(MAX_MESSAGES),
    /** Roadmap progress keys: "<phase>/<lesson number>". */
    done: z.array(z.string().regex(/^\d{1,2}\/\d{1,3}$/)).max(600).default([]),
    /** The lesson the learner has open, "<phase folder>/<lesson folder>". */
    lesson: z.string().regex(LESSON_KEY).optional(),
  })
  // zod runs this check even when `messages` failed its own checks, so it must cope with an empty list.
  .refine((body) => body.messages.at(0)?.role === "user" && body.messages.at(-1)?.role === "user", {
    message: "The first and the last message must come from the user",
  });

export type TutorRequest = z.infer<typeof TutorRequestSchema>;
export type ChatMessage = TutorRequest["messages"][number];
