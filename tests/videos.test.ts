import { test } from "node:test";
import assert from "node:assert/strict";
import { MAX_SHORT_SECONDS, TopicFileSchema } from "../src/lib/content-schema.ts";
import type { Video } from "../src/lib/content-schema.ts";
import { formatClock, isoDuration, videosForVoice } from "../src/lib/videos.ts";

const en1: Video = { id: "zjkBMFhNj_g", title: "Intro to LLMs", channel: "Andrej Karpathy", lang: "en" };
const en2: Video = { id: "kCc8FmEb1nY", title: "Let's build GPT", channel: "Andrej Karpathy", lang: "en" };
const bn1: Video = { id: "abcdefghijk", title: "এলএলএম কী", channel: "Example", lang: "bn" };

function fileWith(videos: unknown) {
  return { slug: "x", title: "X", lede: "L", bn: { title: "X", lede: "L" }, sources: [], sections: [{ id: "s1", num: "01", title: "T", sub: "", bn: { title: "T", sub: "" }, body: [], layman: [], bangla: [], videos }] };
}

test("TopicFileSchema accepts sections with and without videos", () => {
  assert.doesNotThrow(() => TopicFileSchema.parse(fileWith([en1, bn1])));
  const noVideos = fileWith(undefined);
  delete (noVideos.sections[0] as { videos?: unknown }).videos;
  assert.doesNotThrow(() => TopicFileSchema.parse(noVideos));
});

test("TopicFileSchema rejects a malformed video id", () => {
  for (const id of ["short", "zjkBMFhNj_g1", "zjkBMFhNj g", "https://youtu.be/zjkBMFhNj_g"]) {
    assert.throws(() => TopicFileSchema.parse(fileWith([{ ...en1, id }])), id);
  }
});

test("TopicFileSchema rejects an unknown language, an empty title, and extra keys", () => {
  assert.throws(() => TopicFileSchema.parse(fileWith([{ ...en1, lang: "hi" }])));
  assert.throws(() => TopicFileSchema.parse(fileWith([{ ...en1, title: "" }])));
  assert.throws(() => TopicFileSchema.parse(fileWith([{ ...en1, url: "https://youtube.com" }])));
});

test("videosForVoice: Technical and Layman's show English videos", () => {
  assert.deepEqual(videosForVoice([en1, bn1, en2], "main"), [en1, en2]);
  assert.deepEqual(videosForVoice([en1, bn1, en2], "layman"), [en1, en2]);
});

test("videosForVoice: বাংলা shows Bangla videos first, then English", () => {
  assert.deepEqual(videosForVoice([en1, bn1, en2], "bangla"), [bn1, en1, en2]);
  assert.deepEqual(videosForVoice([en1], "bangla"), [en1]);
});

test("videosForVoice: All three shows English, then Bangla", () => {
  assert.deepEqual(videosForVoice([bn1, en1, en2], "all"), [en1, en2, bn1]);
});

test("videosForVoice: no videos gives an empty list", () => {
  assert.deepEqual(videosForVoice(undefined, "main"), []);
  assert.deepEqual(videosForVoice([], "all"), []);
});

const short: Video = { id: "p7U_98jWqWo", title: "Claude Code Explained in 60 Seconds", channel: "KodeKloud", lang: "en", format: "short", seconds: 78 };

test("TopicFileSchema accepts a Short with its length, and a long video with a length", () => {
  assert.doesNotThrow(() => TopicFileSchema.parse(fileWith([short])));
  assert.doesNotThrow(() => TopicFileSchema.parse(fileWith([{ ...en1, seconds: 3600 }])));
  assert.doesNotThrow(() => TopicFileSchema.parse(fileWith([{ ...short, seconds: MAX_SHORT_SECONDS }])));
  assert.doesNotThrow(() => TopicFileSchema.parse(fileWith([{ ...short, seconds: undefined }])), "a Short may omit its length");
});

test("TopicFileSchema rejects an unknown format, a bad length, and a Short that is too long", () => {
  for (const bad of [
    { ...short, format: "reel" },
    { ...short, format: "video" },
    { ...short, seconds: 0 },
    { ...short, seconds: -5 },
    { ...short, seconds: 12.5 },
    { ...short, seconds: "78" },
    { ...short, seconds: MAX_SHORT_SECONDS + 1 },
  ]) {
    assert.throws(() => TopicFileSchema.parse(fileWith([bad])), JSON.stringify(bad));
  }
});

test("videosForVoice keeps format and length on the videos it returns", () => {
  assert.deepEqual(videosForVoice([en1, short], "main"), [en1, short]);
  assert.equal(videosForVoice([short], "bangla")[0].format, "short");
});

test("formatClock writes m:ss and h:mm:ss, in the digits of the language", () => {
  assert.equal(formatClock(0), "0:00");
  assert.equal(formatClock(5), "0:05");
  assert.equal(formatClock(78), "1:18");
  assert.equal(formatClock(609), "10:09");
  assert.equal(formatClock(3600), "1:00:00");
  assert.equal(formatClock(3661), "1:01:01");
  assert.equal(formatClock(78, "bn"), "১:১৮");
  assert.equal(formatClock(3661, "bn"), "১:০১:০১");
});

test("isoDuration writes an ISO 8601 duration for <time>", () => {
  assert.equal(isoDuration(0), "PT0S");
  assert.equal(isoDuration(45), "PT45S");
  assert.equal(isoDuration(60), "PT1M");
  assert.equal(isoDuration(65), "PT1M5S");
  assert.equal(isoDuration(3600), "PT1H");
  assert.equal(isoDuration(3661), "PT1H1M1S");
});
