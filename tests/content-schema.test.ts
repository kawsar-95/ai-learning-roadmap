import { test } from "node:test";
import assert from "node:assert/strict";
import { isAllowedInline, TopicFileSchema } from "../src/lib/content-schema.ts";

test("isAllowedInline accepts the allowlist", () => {
  assert.equal(isAllowedInline('a <strong>b</strong> <em>c</em> <code>d</code><br> <a class="cite" href="#src12">[12]</a> <a href="https://arxiv.org/abs/1">x</a>'), true);
});

test("isAllowedInline rejects other tags and attributes", () => {
  for (const bad of ['<div>x</div>', '<span class="kw">x</span>', '<strong style="color:red">x</strong>', '<a href="javascript:alert(1)">x</a>', '<a class="cite" href="#foo">x</a>', '<img src=x>']) {
    assert.equal(isAllowedInline(bad), false, bad);
  }
});

test("isAllowedInline accepts escaped pseudo-tags", () => {
  assert.equal(isAllowedInline("wrap in <code>&lt;document&gt;</code>"), true);
});

test("TopicFileSchema accepts nested callout blocks", () => {
  const file = { slug: "x", title: "X", lede: "L", bn: { title: "X", lede: "L" }, sources: [], sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, layman: [], bangla: [],
    body: [{ type: "callout", variant: "pink", blocks: [{ type: "list", ordered: false, items: ["a"] }] }] }] };
  assert.deepEqual(TopicFileSchema.parse(file), file);
});

test("TopicFileSchema rejects unknown block types and bad variants", () => {
  const base = { slug: "x", title: "X", lede: "L", bn: { title: "X", lede: "L" }, sources: [], sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, layman: [], bangla: [], body: [] as unknown[] }] };
  base.sections[0].body = [{ type: "aside", html: "x" }];
  assert.throws(() => TopicFileSchema.parse(base));
  base.sections[0].body = [{ type: "callout", variant: "blue", blocks: [] }];
  assert.throws(() => TopicFileSchema.parse(base));
});

test("TopicFileSchema rejects an unknown key on a section", () => {
  const file = { slug: "x", title: "X", lede: "L", bn: { title: "X", lede: "L" }, sources: [], sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, layman: [], bangla: [], body: [], tag_line: "oops" }] };
  assert.throws(() => TopicFileSchema.parse(file));
});

test("TopicFileSchema rejects caption_bn on a diagram block", () => {
  const file = { slug: "x", title: "X", lede: "L", bn: { title: "X", lede: "L" }, sources: [], sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, layman: [], bangla: [],
    body: [{ type: "diagram", svg: "<svg/>", caption_bn: "oops" }] }] };
  assert.throws(() => TopicFileSchema.parse(file));
});

const mcq = (id: string, over: Record<string, unknown> = {}) => ({
  id,
  kind: "mcq",
  answer: 1,
  en: { q: "Q?", options: ["a", "b", "c"], why: "Because." },
  bn: { q: "প্রশ্ন?", options: ["ক", "খ", "গ"], why: "কারণ।" },
  ...over,
});
const tf = (id: string, over: Record<string, unknown> = {}) => ({
  id,
  kind: "tf",
  answer: true,
  en: { q: "True?", why: "Yes." },
  bn: { q: "সত্য?", why: "হ্যাঁ।" },
  ...over,
});
const topicWithQuiz = (quiz?: unknown) => ({
  slug: "x",
  title: "X",
  lede: "L",
  bn: { title: "X", lede: "L" },
  sources: [],
  sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, layman: [], bangla: [], body: [] }],
  ...(quiz === undefined ? {} : { quiz }),
});

test("TopicFileSchema accepts a topic with an mcq and a tf question", () => {
  const file = topicWithQuiz([mcq("q1"), tf("q2")]);
  assert.deepEqual(TopicFileSchema.parse(file), file);
});

test("TopicFileSchema accepts a topic with no quiz", () => {
  assert.doesNotThrow(() => TopicFileSchema.parse(topicWithQuiz()));
});

test("TopicFileSchema rejects a bad quiz", () => {
  const bad: [string, unknown][] = [
    ["1 option", [mcq("q1", { en: { q: "Q?", options: ["a"], why: "w" }, bn: { q: "প্রশ্ন?", options: ["ক"], why: "ক" }, answer: 0 })]],
    ["7 options", [mcq("q1", { en: { q: "Q?", options: Array(7).fill("a"), why: "w" }, bn: { q: "প্রশ্ন?", options: Array(7).fill("ক"), why: "ক" } })]],
    ["answer out of range", [mcq("q1", { answer: 3 })]],
    ["option counts differ", [mcq("q1", { bn: { q: "প্রশ্ন?", options: ["ক", "খ"], why: "কারণ।" } })]],
    ["repeated id", [mcq("q1"), tf("q1")]],
    ["empty list", []],
    ["tf with a number answer", [tf("q1", { answer: 1 })]],
    ["unknown key", [mcq("q1", { tag: "oops" })]],
    ["empty question text", [mcq("q1", { en: { q: " ", options: ["a", "b", "c"], why: "w" } })]],
  ];
  for (const [name, quiz] of bad) {
    // The failure must be about the quiz, not a rejected unknown key at the root.
    assert.throws(
      () => TopicFileSchema.parse(topicWithQuiz(quiz)),
      (err: { issues?: { path: unknown[] }[] }) => !!err.issues?.some((issue) => issue.path[0] === "quiz"),
      name,
    );
  }
});
