import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildRoadmap } from "../src/lib/roadmap-schema.ts";
import { buildOutline } from "../src/tutor/outline.ts";
import { summarizeProgress } from "../src/tutor/progress.ts";
import { buildSystem } from "../src/tutor/prompt.ts";
import { TutorRequestSchema } from "../src/tutor/request.ts";
import { createTutorHandler } from "../src/tutor/handler.ts";
import type { TutorModel } from "../src/tutor/handler.ts";

const read = (name: string): unknown => JSON.parse(readFileSync(new URL(`../src/data/${name}`, import.meta.url), "utf8"));
const stages = buildRoadmap(read("roadmap-lessons.json"), read("roadmap-phases.json"));

test("the outline lists every phase and every lesson folder", () => {
  const outline = buildOutline(stages);
  assert.equal(outline.match(/^## Phase /gm)?.length, 20);
  assert.equal(outline.match(/^\d\d-[a-z0-9-]+ \| .+ \| \d+ min$/gm)?.length, 542);
  assert.match(outline, /folder 11-llm-engineering\)/);
  assert.match(outline, /^01-prompt-engineering \| Prompt Engineering/m);
});

test("summarizeProgress: nothing done, some done, and keys of unknown lessons", () => {
  assert.match(summarizeProgress([], stages), /not marked any of the 542/);
  const text = summarizeProgress(["0/1", "0/2", "99/1"], stages);
  assert.match(text, /2 of 542/);
  assert.match(text, /Phase 0 \(Setup & Tooling\): 2 of 13 done/);
  assert.match(text, /phase 0, 03-gpu-setup-and-cloud/);
});

test("buildSystem: the cached block comes first and holds nothing that changes per learner", () => {
  const a = buildSystem(stages, []);
  const b = buildSystem(stages, ["0/1", "1/1"]);
  assert.deepEqual(a[0].cache_control, { type: "ephemeral" });
  assert.equal(a[1].cache_control, undefined);
  assert.equal(a[0].text, b[0].text, "the cached prefix is the same for every learner");
  assert.notEqual(a[1].text, b[1].text);
  assert.match(a[0].text, /https:\/\/aiengineeringfromscratch\.com\/lesson\?path=phases\//);
});

test("TutorRequestSchema accepts a question and rejects bad shapes", () => {
  const ok = { messages: [{ role: "user", content: "What next?" }], done: ["0/1"] };
  assert.deepEqual(TutorRequestSchema.parse(ok).done, ["0/1"]);
  assert.deepEqual(TutorRequestSchema.parse({ messages: ok.messages }).done, []);
  const bad: unknown[] = [
    {},
    { messages: [] },
    { messages: [{ role: "assistant", content: "hi" }] },
    { messages: [{ role: "user", content: "a" }, { role: "assistant", content: "b" }] },
    { messages: [{ role: "system", content: "x" }] },
    { messages: [{ role: "user", content: "x".repeat(4001) }] },
    { messages: ok.messages, done: ["../x"] },
    { messages: ok.messages, extra: 1 },
  ];
  for (const body of bad) assert.equal(TutorRequestSchema.safeParse(body).success, false, JSON.stringify(body).slice(0, 60));
});

const fakeModel: TutorModel = async function* ({ messages, system }) {
  yield { text: `echo:${messages[messages.length - 1].content}|` };
  yield { text: `blocks:${system.length}` };
  yield { stopReason: "end_turn" };
};
const post = (body: unknown, init: RequestInit = {}) =>
  new Request("http://x/tutor", { method: "POST", body: typeof body === "string" ? body : JSON.stringify(body), ...init });
const question = { messages: [{ role: "user", content: "hi" }] };

async function events(response: Response): Promise<unknown[]> {
  return (await response.text())
    .split("\n\n")
    .filter(Boolean)
    .map((part) => JSON.parse(part.replace(/^data: /, "")));
}

test("the handler streams the model's text and a final done event", async () => {
  const handle = createTutorHandler({ stages, model: fakeModel });
  const response = await handle(post(question));
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("content-type"), "text/event-stream");
  assert.deepEqual(await events(response), [
    { text: "echo:hi|" },
    { text: "blocks:2" },
    { done: true, stopReason: "end_turn" },
  ]);
});

test("the handler rejects a bad method, bad JSON, a bad body and a big body", async () => {
  const handle = createTutorHandler({ stages, model: fakeModel });
  assert.equal((await handle(new Request("http://x/tutor"))).status, 405);
  assert.equal((await handle(post("{nope"))).status, 400);
  assert.equal((await handle(post({ messages: [] }))).status, 400);
  assert.equal((await handle(post("x".repeat(100_001)))).status, 413);
});

test("the handler answers 429 when the limiter says no, and does not call the model", async () => {
  let called = false;
  const handle = createTutorHandler({
    stages,
    allow: () => false,
    model: async function* () {
      called = true;
    },
  });
  assert.equal((await handle(post(question))).status, 429);
  assert.equal(called, false);
});

test("a model failure becomes an error event that does not leak the cause", async () => {
  const handle = createTutorHandler({
    stages,
    model: async function* () {
      throw new Error("secret upstream detail");
    },
  });
  const original = console.error;
  console.error = () => {};
  try {
    const body = JSON.stringify(await events(await handle(post(question))));
    assert.match(body, /could not answer/);
    assert.doesNotMatch(body, /secret/);
  } finally {
    console.error = original;
  }
});

test("CORS headers appear only when an origin is allowed", async () => {
  const closed = createTutorHandler({ stages, model: fakeModel });
  assert.equal((await closed(post(question))).headers.get("access-control-allow-origin"), null);
  const open = createTutorHandler({ stages, model: fakeModel, allowOrigin: "https://a.example" });
  const preflight = await open(new Request("http://x/tutor", { method: "OPTIONS" }));
  assert.equal(preflight.status, 204);
  assert.equal(preflight.headers.get("access-control-allow-origin"), "https://a.example");
});
