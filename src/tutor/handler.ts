// A fetch-style request handler for the tutor: Request in, streaming
// Response out. It has no framework imports, so it runs in Node, Next route
// handlers, Hono, Cloudflare Workers, and so on.
//
// The response is a Server-Sent Events stream. Each event is one JSON line:
//   {"text":"..."}                         a piece of the answer
//   {"done":true,"stopReason":"end_turn"}  the end; "refusal" means the model declined
//   {"error":"..."}                        a failure; the stream ends after it

import type { Stage } from "../lib/roadmap-schema.ts";
import { buildSystem } from "./prompt.ts";
import type { SystemBlock } from "./prompt.ts";
import { TutorRequestSchema } from "./request.ts";
import type { ChatMessage } from "./request.ts";

export type TutorEvent = { text: string } | { stopReason: string | null };
export type TutorModel = (input: {
  system: SystemBlock[];
  messages: ChatMessage[];
  signal: AbortSignal;
}) => AsyncIterable<TutorEvent>;

export type TutorHandlerOptions = {
  stages: Stage[];
  model: TutorModel;
  /** The origin allowed to call the endpoint from a browser, such as "https://example.com". Unset: same-origin only. */
  allowOrigin?: string;
  /** Return false to answer 429. Use it for per-client limits. */
  allow?: (request: Request) => boolean;
};

const MAX_BODY = 100_000;

export function createTutorHandler({ stages, model, allowOrigin, allow }: TutorHandlerOptions) {
  const cors: Record<string, string> = allowOrigin
    ? {
        "access-control-allow-origin": allowOrigin,
        "access-control-allow-methods": "POST, OPTIONS",
        "access-control-allow-headers": "content-type",
        vary: "origin",
      }
    : {};
  const json = (status: number, body: unknown) =>
    new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", ...cors } });

  return async function handle(request: Request): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "POST") return json(405, { error: "Use POST." });
    if (allow && !allow(request)) return json(429, { error: "Too many requests. Try again in a minute." });

    const raw = await request.text();
    if (raw.length > MAX_BODY) return json(413, { error: "The request is too large." });
    let body: unknown;
    try {
      body = JSON.parse(raw);
    } catch {
      return json(400, { error: "The body is not valid JSON." });
    }
    const parsed = TutorRequestSchema.safeParse(body);
    if (!parsed.success) return json(400, { error: parsed.error.issues[0]?.message ?? "Bad request." });

    const { messages, done } = parsed.data;
    const encoder = new TextEncoder();
    const send = (controller: ReadableStreamDefaultController<Uint8Array>, event: unknown) =>
      controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        try {
          for await (const event of model({ system: buildSystem(stages, done), messages, signal: request.signal })) {
            if ("text" in event) send(controller, { text: event.text });
            else send(controller, { done: true, stopReason: event.stopReason });
          }
        } catch (error) {
          console.error("tutor: model call failed", error);
          send(controller, { error: "The tutor could not answer. Try again." });
        }
        controller.close();
      },
    });
    return new Response(stream, {
      headers: { "content-type": "text/event-stream", "cache-control": "no-store", ...cors },
    });
  };
}
