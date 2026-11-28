import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import type { TopicFile } from "../src/lib/content-schema.ts";
import { attachWalkthroughs } from "../src/lib/walkthrough-files.ts";
import { ISO_SCALES, isoPillY, isoScale } from "../src/lib/walkthrough.ts";

const dir = new URL("../src/content/", import.meta.url);
const ownDir = new URL("walkthroughs/", dir);
const readJson = (url: URL) => JSON.parse(readFileSync(url, "utf8"));
const ownFiles = (slug: string): Record<string, unknown> => {
  const folder = new URL(`${slug}/`, ownDir);
  if (!existsSync(folder)) return {};
  return Object.fromEntries(
    readdirSync(folder)
      .filter((n) => n.endsWith(".json"))
      .map((n) => [n.slice(0, -".json".length), readJson(new URL(n, folder))]),
  );
};
const parts = readdirSync(dir)
  .filter((n) => n.endsWith(".json") && n !== "interview.json")
  .map((n) => {
    const part = readJson(new URL(n, dir)) as TopicFile;
    return attachWalkthroughs(part, ownFiles(part.slug));
  });
const walks = parts.flatMap((p) => p.sections.flatMap((s) => (s.walkthrough ? [{ key: `${p.slug}#${s.id}`, walk: s.walkthrough }] : [])));

test("the isometric look: the pilot fits at full size", () => {
  const pilot = walks.find((w) => w.key === "system-design#s1");
  assert.ok(pilot);
  assert.equal(isoScale(pilot.walk), 1);
});

test("the isometric look: the name sits under the object and the second line over it, closer at a smaller scale", () => {
  for (const s of ISO_SCALES) {
    const { name, sub } = isoPillY(s);
    assert.ok(name > 0 && sub < 0);
  }
  assert.ok(isoPillY(0.65).name < isoPillY(1).name);
});

test("the isometric look: every scale it picks is one of the allowed scales", () => {
  for (const { key, walk } of walks) {
    const s = isoScale(walk);
    assert.ok(s === null || (ISO_SCALES as readonly number[]).includes(s), key);
  }
});
