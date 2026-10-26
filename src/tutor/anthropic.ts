import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { LESSON_KEY, lessonDocument } from "./lessons.ts";
import type { TutorModel } from "./handler.ts";

export type AnthropicModelOptions = {
  /** Defaults to a client that reads ANTHROPIC_API_KEY from the environment. */
  client?: Anthropic;
  /** Defaults to the TUTOR_MODEL environment variable, then to claude-opus-5-5. */
  model?: string;
  maxTokens?: number;
  /** Requests per question: the last one runs without tools, so the tutor always answers. */
  maxRounds?: number;
};

const READ_LESSON = "read_lesson";

const readLessonTool = {
  name: READ_LESSON,
  description:
    "Returns the full text of one lesson of the curriculum. Use it when the learner asks what a lesson teaches or needs an explanation from it.",
  strict: true,
  eager_input_streaming: true,
  input_schema: {
    type: "object" as const,
    properties: {
      lesson: {
        type: "string",
        description: 'The lesson key: "<phase folder>/<lesson folder>", for example "11-llm-engineering/06-rag".',
      },
    },
    required: ["lesson"],
    additionalProperties: false,
  },
};

// With eager input streaming the API does not validate the input, so it is checked here.
const ReadLessonInput = z.object({ lesson: z.string().regex(LESSON_KEY) });

/**
 * The tutor model on the Claude API. Thinking runs adaptive (the default on
 * this model) at medium effort. The server-side fallback re-runs a request on
 * another model if the first one declines it, so the learner sees an answer
 * instead of a refusal. The model may call read_lesson; each round streams
 * its text as it arrives.
 */
export function createAnthropicModel({
  client = new Anthropic(),
  model = process.env.TUTOR_MODEL ?? "claude-opus-5-5",
  maxTokens = 16000,
  maxRounds = 4,
}: AnthropicModelOptions = {}): TutorModel {
  return async function* ({ system, messages, signal, lessons }) {
    const conversation: Anthropic.Beta.BetaMessageParam[] = [...messages];

    for (let round = 1; ; round++) {
      const stream = client.beta.messages.stream(
        {
          model,
          max_tokens: maxTokens,
          betas: ["server-side-fallback-2026-07-01"],
          fallbacks: "default",
          output_config: { effort: "medium" },
          system,
          tools: [readLessonTool],
          tool_choice: { type: round >= maxRounds ? "none" : "auto" },
          messages: conversation,
        },
        { signal },
      );
      for await (const event of stream) {
        if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
          yield { text: event.delta.text };
        }
      }
      const final = await stream.finalMessage();
      if (final.stop_reason !== "tool_use") {
        yield { stopReason: final.stop_reason };
        return;
      }

      // The whole assistant turn goes back unchanged, thinking blocks included.
      conversation.push({ role: "assistant", content: final.content });
      const results: Anthropic.Beta.BetaToolResultBlockParam[] = [];
      for (const block of final.content) {
        if (block.type !== "tool_use") continue;
        const input = block.name === READ_LESSON ? ReadLessonInput.safeParse(block.input) : undefined;
        const lesson = input?.success ? lessons.find(input.data.lesson) : undefined;
        if (!lesson) {
          results.push({
            type: "tool_result",
            tool_use_id: block.id,
            is_error: true,
            content: "No such lesson. Use a key from the curriculum outline.",
          });
          continue;
        }
        yield { reading: lesson.title };
        results.push({ type: "tool_result", tool_use_id: block.id, content: lessonDocument(lesson) });
      }
      // All results of one assistant turn go back in a single user message.
      conversation.push({ role: "user", content: results });
    }
  };
}
