import Anthropic from "@anthropic-ai/sdk";
import type { TutorModel } from "./handler.ts";

export type AnthropicModelOptions = {
  /** Defaults to a client that reads ANTHROPIC_API_KEY from the environment. */
  client?: Anthropic;
  /** Defaults to the TUTOR_MODEL environment variable, then to claude-opus-5-5. */
  model?: string;
  maxTokens?: number;
};

/**
 * The tutor model on the Claude API. Thinking runs adaptive (the default on
 * this model) at medium effort. The server-side fallback re-runs a request on
 * another model if the first one declines it, so the learner sees an answer
 * instead of a refusal.
 */
export function createAnthropicModel({
  client = new Anthropic(),
  model = process.env.TUTOR_MODEL ?? "claude-opus-5-5",
  maxTokens = 16000,
}: AnthropicModelOptions = {}): TutorModel {
  return async function* ({ system, messages, signal }) {
    const stream = client.beta.messages.stream(
      {
        model,
        max_tokens: maxTokens,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        output_config: { effort: "medium" },
        system,
        messages,
      },
      { signal },
    );
    for await (const event of stream) {
      if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
        yield { text: event.delta.text };
      }
    }
    const final = await stream.finalMessage();
    yield { stopReason: final.stop_reason };
  };
}
