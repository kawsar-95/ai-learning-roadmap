import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MAX_SHORT_SECONDS, TopicFileSchema } from "../src/lib/content-schema.ts";
import { storedTitle } from "../src/lib/video-check.ts";

// The committed videos of every Part, read the same way `next build` reads them. Nothing here touches the network.
const slugs = readFileSync(new URL("../src/lib/topics.ts", import.meta.url), "utf8")
  .match(/^  "([a-z-]+)",$/gm)!
  .map((line) => line.trim().slice(1, -2));

const clips = slugs.flatMap((slug) => {
  const topic = TopicFileSchema.parse(JSON.parse(readFileSync(new URL(`../src/content/${slug}.json`, import.meta.url), "utf8")));
  return topic.sections.flatMap((section) => (section.videos ?? []).map((video) => ({ where: `${slug}#${section.id}`, video })));
});

test("the Parts list their videos", () => {
  assert.ok(slugs.length > 0);
  assert.ok(clips.length > 0);
});

test("a section never lists the same video twice", () => {
  // The book chapters re-list videos of the Parts on purpose, so the same id may sit in two sections. Twice in one is a mistake.
  const seen = new Set<string>();
  for (const { where, video } of clips) {
    assert.ok(!seen.has(`${where}/${video.id}`), `${video.id} is listed twice in ${where}`);
    seen.add(`${where}/${video.id}`);
  }
});

test("a stored title is the published one: no hashtag and no emoji, and the channel has no outer space", () => {
  // Whitespace runs are ignored: a published title can hold a double space, and HTML collapses it anyway.
  const squash = (s: string) => s.replace(/\s+/g, " ").trim();
  const odd = clips
    .filter(({ video }) => squash(video.title) !== squash(storedTitle(video.title)) || video.channel !== video.channel.trim())
    .map(({ where, video }) => `${where} ${video.id} ${JSON.stringify(video.title)}`);
  assert.deepEqual(odd, [], "a title still has a hashtag or an emoji, or a channel has outer space");
});

test("a Short names its length, and the length fits a Short", () => {
  for (const { where, video } of clips) {
    if (video.format !== "short") continue;
    assert.ok(video.seconds !== undefined, `${where} ${video.id}: a Short needs seconds`);
    assert.ok(video.seconds! <= MAX_SHORT_SECONDS, `${where} ${video.id}: ${video.seconds}s is longer than a Short`);
  }
});

test("a video that is not a Short is not shorter than the point of listing it", () => {
  for (const { where, video } of clips) {
    if (video.format === "short" || video.seconds === undefined) continue;
    assert.ok(video.seconds >= 10, `${where} ${video.id}: ${video.seconds}s is too short to be a video`);
  }
});
