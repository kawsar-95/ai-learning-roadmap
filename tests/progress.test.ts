import { test } from "node:test";
import assert from "node:assert/strict";
import {
  firstUndone,
  parseProgress,
  progressKey,
  serializeProgress,
  summarize,
  toggleKey,
} from "../src/lib/progress.ts";

test("progressKey joins the topic slug and the section id", () => {
  assert.equal(progressKey("inference", "s3"), "inference/s3");
});

test("parseProgress: a JSON list of strings gives a set", () => {
  assert.deepEqual([...parseProgress('["a/s1","b/s2"]')], ["a/s1", "b/s2"]);
});

test("parseProgress: missing or bad data gives an empty set", () => {
  for (const raw of [null, "", "not json", "{}", '"a/s1"', "[1,2]", "null"]) {
    assert.equal(parseProgress(raw).size, 0, String(raw));
  }
});

test("parseProgress keeps the strings of a mixed list", () => {
  assert.deepEqual([...parseProgress('["a/s1",3,null]')], ["a/s1"]);
});

test("serializeProgress writes a sorted list that parseProgress reads back", () => {
  const raw = serializeProgress(new Set(["b/s1", "a/s2"]));
  assert.equal(raw, '["a/s2","b/s1"]');
  assert.deepEqual([...parseProgress(raw)].sort(), ["a/s2", "b/s1"]);
});

test("toggleKey adds a missing key and removes a present key, without changing the input", () => {
  const start = new Set(["a/s1"]);
  const added = toggleKey(start, "a/s2");
  assert.deepEqual([...added].sort(), ["a/s1", "a/s2"]);
  assert.deepEqual([...toggleKey(added, "a/s1")], ["a/s2"]);
  assert.deepEqual([...start], ["a/s1"]);
});

test("summarize counts only keys of sections that exist", () => {
  const all = ["a/s1", "a/s2", "b/s1", "b/s2"];
  const done = new Set(["a/s1", "b/s2", "gone/s9"]);
  assert.deepEqual(summarize(done, all), { done: 2, total: 4, percent: 50 });
});

test("summarize rounds the percent and handles an empty list", () => {
  assert.equal(summarize(new Set(["a"]), ["a", "b", "c"]).percent, 33);
  assert.deepEqual(summarize(new Set(), []), { done: 0, total: 0, percent: 0 });
});

test("firstUndone gives the first key in order that is not done, or null", () => {
  const all = ["a/s1", "a/s2", "b/s1"];
  assert.equal(firstUndone(new Set(), all), "a/s1");
  assert.equal(firstUndone(new Set(["a/s1"]), all), "a/s2");
  assert.equal(firstUndone(new Set(all), all), null);
});
