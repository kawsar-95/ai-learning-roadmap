import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildRoadmap } from "../src/lib/roadmap-schema.ts";
import { buildOutline } from "../src/tutor/outline.ts";
import { summarizeProgress } from "../src/tutor/progress.ts";
import { buildSystem } from "../src/tutor/prompt.ts";
import { TutorRequestSchema } from "../src/tutor/request.ts";
import { createTutorHandler } from "../src/tutor/handler.ts";
import { createLessonSource, lessonDocument } from "../src/tutor/lessons.ts";
import { createAnthropicModel } from "../src/tutor/anthropic.ts";
import type Anthropic from "@anthropic-ai/sdk";
import type { TutorModel } from "../src/tutor/handler.ts";

const read = (name: string): unknown => JSON.parse(readFileSync(new URL(`../src/data/${name}`, import.meta.url), "utf8"));
const stages = buildRoadmap(read("roadmap-lessons.json"), read("roadmap-phases.json"));
const lessons = createLessonSource(stages, (folder, dir) =>
  readFileSync(new URL(`../src/data/lessons/${folder}/${dir}.md`, import.meta.url), "utf8"),
);
const RAG = "11-llm-engineering/06-rag";

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
  const handle = createTutorHandler({ stages, lessons, model: fakeModel });
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
  const handle = createTutorHandler({ stages, lessons, model: fakeModel });
  assert.equal((await handle(new Request("http://x/tutor"))).status, 405);
  assert.equal((await handle(post("{nope"))).status, 400);
  assert.equal((await handle(post({ messages: [] }))).status, 400);
  assert.equal((await handle(post("x".repeat(100_001)))).status, 413);
});

test("the handler answers 429 when the limiter says no, and does not call the model", async () => {
  let called = false;
  const handle = createTutorHandler({
    stages,
    lessons,
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
    lessons,
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
  const closed = createTutorHandler({ stages, lessons, model: fakeModel });
  assert.equal((await closed(post(question))).headers.get("access-control-allow-origin"), null);
  const open = createTutorHandler({ stages, lessons, model: fakeModel, allowOrigin: "https://a.example" });
  const preflight = await open(new Request("http://x/tutor", { method: "OPTIONS" }));
  assert.equal(preflight.status, 204);
  assert.equal(preflight.headers.get("access-control-allow-origin"), "https://a.example");
});

test("the lesson source finds a lesson by key and knows nothing else", () => {
  const lesson = lessons.find(RAG)!;
  assert.equal(lesson.key, RAG);
  assert.match(lesson.title, /RAG/);
  assert.match(lesson.text, /^# /);
  assert.equal(lessons.find("11-llm-engineering/99-nope"), undefined);
  assert.equal(lessons.find("../../etc/passwd"), undefined);
});

test("lessonDocument wraps the text in tags and cuts a very long lesson", () => {
  const doc = lessonDocument({ key: "a/b", title: 'Say "hi"', text: "body" });
  assert.equal(doc, `<lesson key="a/b" title="Say 'hi'">\nbody\n</lesson>`);
  const long = lessonDocument({ key: "a/b", title: "T", text: "x".repeat(130_000) });
  assert.ok(long.length < 121_000);
  assert.match(long, /the rest is cut/);
});

test("buildSystem adds the open lesson as a third block with its own cache breakpoint", () => {
  const lesson = lessons.find(RAG)!;
  const blocks = buildSystem(stages, [], lesson);
  assert.equal(blocks.length, 3);
  assert.deepEqual(blocks[2].cache_control, { type: "ephemeral" });
  assert.ok(blocks[2].text.includes(lesson.text));
  assert.equal(blocks[0].text, buildSystem(stages, [])[0].text, "the first block does not depend on the lesson");
  assert.equal(buildSystem(stages, []).length, 2);
});

test("TutorRequestSchema checks the lesson key", () => {
  const messages = [{ role: "user", content: "hi" }];
  assert.equal(TutorRequestSchema.parse({ messages, lesson: RAG }).lesson, RAG);
  assert.equal(TutorRequestSchema.safeParse({ messages, lesson: "../x" }).success, false);
  assert.equal(TutorRequestSchema.safeParse({ messages, lesson: "11-llm-engineering" }).success, false);
});

test("the handler puts the open lesson into the system prompt and rejects an unknown lesson", async () => {
  const handle = createTutorHandler({ stages, lessons, model: fakeModel });
  const ok = await events(await handle(post({ ...question, lesson: RAG })));
  assert.deepEqual(ok[1], { text: "blocks:3" });
  const missing = await handle(post({ ...question, lesson: "11-llm-engineering/99-nope" }));
  assert.equal(missing.status, 400);
});

// --- The model call, with a fake client ---

// The tests read nested fields of the request the fake client saw, so the messages are loosely typed.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Call = { messages: any[]; tool_choice: { type: string }; tools: { name: string }[] };
function fakeClient(rounds: { text?: string; content: unknown[]; stop: string }[]) {
  const calls: Call[] = [];
  const client = {
    beta: {
      messages: {
        stream(params: Call) {
          calls.push(JSON.parse(JSON.stringify(params)));
          const round = rounds[calls.length - 1];
          return {
            async *[Symbol.asyncIterator]() {
              if (round.text) yield { type: "content_block_delta", delta: { type: "text_delta", text: round.text } };
            },
            finalMessage: async () => ({ stop_reason: round.stop, content: round.content }),
          };
        },
      },
    },
  } as unknown as Anthropic;
  return { client, calls };
}
const run = async (model: TutorModel) => {
  const out = [];
  for await (const event of model({ system: [], messages: [{ role: "user", content: "What is RAG?" }], signal: new AbortController().signal, lessons })) out.push(event);
  return out;
};
const toolTurn = (input: unknown) => ({
  stop: "tool_use",
  content: [{ type: "thinking", thinking: "", signature: "sig" }, { type: "tool_use", id: "t1", name: "read_lesson", input }],
});

test("the model call reads a lesson when asked to, then streams the answer", async () => {
  const { client, calls } = fakeClient([toolTurn({ lesson: RAG }), { text: "RAG is...", content: [], stop: "end_turn" }]);
  const out = await run(createAnthropicModel({ client }));
  assert.deepEqual(out, [{ reading: lessons.find(RAG)!.title }, { text: "RAG is..." }, { stopReason: "end_turn" }]);
  assert.equal(calls.length, 2);
  assert.equal(calls[0].tools[0].name, "read_lesson");
  assert.equal(calls[0].tool_choice.type, "auto");
  const [first, assistant, user] = calls[1].messages;
  assert.equal(first.content, "What is RAG?");
  assert.equal(assistant.role, "assistant");
  assert.equal(assistant.content[0].type, "thinking", "the assistant turn goes back unchanged");
  assert.equal(user.role, "user");
  assert.equal(user.content.length, 1);
  assert.equal(user.content[0].tool_use_id, "t1");
  assert.ok(user.content[0].content.includes(lessons.find(RAG)!.text));
  assert.equal(user.content[0].is_error, undefined);
});

test("the model call answers a bad lesson key with an error result, and runs the last round without tools", async () => {
  const { client, calls } = fakeClient([toolTurn({ lesson: "nope" }), { text: "Sorry.", content: [], stop: "end_turn" }]);
  const out = await run(createAnthropicModel({ client, maxRounds: 2 }));
  assert.deepEqual(out, [{ text: "Sorry." }, { stopReason: "end_turn" }]);
  assert.equal(calls[1].messages[2].content[0].is_error, true);
  assert.equal(calls[1].tool_choice.type, "none");
});

test("the model call passes a refusal on without looping", async () => {
  const { client, calls } = fakeClient([{ content: [], stop: "refusal" }]);
  assert.deepEqual(await run(createAnthropicModel({ client })), [{ stopReason: "refusal" }]);
  assert.equal(calls.length, 1);
});
