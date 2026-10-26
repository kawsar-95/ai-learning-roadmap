// Runs the tutor as a small HTTP server.
//
//   ANTHROPIC_API_KEY=... TUTOR_ALLOW_ORIGIN=https://you.github.io node scripts/tutor-server.ts
//
// POST /tutor with {"messages":[{"role":"user","content":"..."}],"done":["0/1"]}.
// PORT (default 8787), TUTOR_MODEL and TUTOR_PER_MINUTE (default 20 requests
// per minute per client address) are optional.

import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import { buildRoadmap } from "../src/lib/roadmap-schema.ts";
import { createAnthropicModel, createTutorHandler } from "../src/tutor/index.ts";

const read = (name: string): unknown =>
  JSON.parse(readFileSync(new URL(`../src/data/${name}`, import.meta.url), "utf8"));
const stages = buildRoadmap(read("roadmap-lessons.json"), read("roadmap-phases.json"));

const perMinute = Number(process.env.TUTOR_PER_MINUTE ?? 20);
const hits = new Map<string, number[]>();
function clientOf(request: Request): string {
  return request.headers.get("x-forwarded-for")?.split(",")[0].trim() || "local";
}
function allow(request: Request): boolean {
  const now = Date.now();
  const key = clientOf(request);
  const recent = (hits.get(key) ?? []).filter((t) => now - t < 60_000);
  recent.push(now);
  hits.set(key, recent);
  return recent.length <= perMinute;
}

const handle = createTutorHandler({
  stages,
  model: createAnthropicModel(),
  allowOrigin: process.env.TUTOR_ALLOW_ORIGIN,
  allow,
});

const server = createServer(async (incoming, outgoing) => {
  if (new URL(incoming.url ?? "/", "http://localhost").pathname !== "/tutor") {
    outgoing.writeHead(404).end();
    return;
  }
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of incoming) {
    size += chunk.length;
    if (size > 200_000) {
      outgoing.writeHead(413).end();
      return;
    }
    chunks.push(chunk);
  }
  const headers = new Headers();
  for (const [name, value] of Object.entries(incoming.headers)) {
    if (typeof value === "string") headers.set(name, value);
  }
  const controller = new AbortController();
  outgoing.on("close", () => controller.abort());
  const request = new Request("http://localhost/tutor", {
    method: incoming.method,
    headers,
    body: incoming.method === "POST" ? Buffer.concat(chunks) : undefined,
    signal: controller.signal,
  });
  const response = await handle(request);
  outgoing.writeHead(response.status, Object.fromEntries(response.headers));
  if (!response.body) {
    outgoing.end();
    return;
  }
  const reader = response.body.getReader();
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      outgoing.write(value);
    }
  } finally {
    outgoing.end();
  }
});

const port = Number(process.env.PORT ?? 8787);
server.listen(port, () => console.log(`Tutor listening on http://localhost:${port}/tutor`));
