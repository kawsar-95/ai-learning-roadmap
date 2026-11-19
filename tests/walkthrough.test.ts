import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { WALK_NODE_KINDS } from "../src/lib/content-schema.ts";
import type { TopicFile, Walkthrough } from "../src/lib/content-schema.ts";
import { NODE_H, NODE_ROLE, boxExit, boxWidth, changedValues, findWalkthrough, focusX, labelPads, linkEnds, localDigits, nodeWidths, roundedRectPath, valueText, walkUses, walkthroughParams, walkthroughPath } from "../src/lib/walkthrough.ts";

test("localDigits writes Bangla digits on the Bangla site only", () => {
  assert.equal(localDigits("1,085 ms", "bn"), "১,০৮৫ ms");
  assert.equal(localDigits("1,085 ms", "en"), "1,085 ms");
});

test("valueText: a shared string gets local digits, a bilingual value picks its language, null is a dash", () => {
  assert.equal(valueText("40%", "bn"), "৪০%");
  assert.equal(valueText({ en: "10 + spares", bn: "১০ + বাড়তি" }, "bn"), "১০ + বাড়তি");
  assert.equal(valueText(null, "en"), null);
  assert.equal(valueText(undefined, "en"), null);
});

test("boxWidth grows with the longest line and stays within its bounds", () => {
  assert.equal(boxWidth(["DB"]), 112);
  assert.ok(boxWidth(["Search front end"]) > boxWidth(["Server"]));
  assert.equal(boxWidth(["x".repeat(200)]), 240);
});

test("boxExit and linkEnds stop at the edges of the boxes", () => {
  const a = { x: 100, y: 100, w: 120, h: 56 };
  const b = { x: 400, y: 100, w: 120, h: 56 };
  assert.deepEqual(boxExit(a, 400, 100), [160, 100]);
  assert.deepEqual(boxExit(a, 100, 300), [100, 128]);
  assert.deepEqual(linkEnds(a, b), { x1: 166, y1: 100, x2: 334, y2: 100 });
  // Boxes that touch give a zero-length line, not a reversed one.
  const c = { x: 220, y: 100, w: 120, h: 56 };
  const ends = linkEnds(a, c);
  assert.equal(ends.x1, 160);
  assert.equal(ends.x2, 160);
});

test("changedValues marks only the readouts that changed since the step before", () => {
  assert.deepEqual(changedValues(undefined, ["1", null]), [false, false]);
  assert.deepEqual(changedValues(["1", null], ["1", "2"]), [false, true]);
  assert.deepEqual(changedValues([{ en: "a", bn: "ক" }], [{ en: "a", bn: "ক" }]), [false]);
});

test("focusX is the middle of the boxes a step is about, with moved boxes at their new place", () => {
  const label = { en: "x", bn: "x" };
  const walk: Walkthrough = {
    width: 760,
    height: 300,
    nodes: [
      { id: "a", kind: "server", label, x: 100, y: 100 },
      { id: "b", kind: "server", label, x: 500, y: 100 },
    ],
    metrics: [],
    steps: [],
  };
  const text = { short: "s", title: "t", body: ["b"] };
  const step = (show: Walkthrough["steps"][number]["show"]) => ({ en: text, bn: text, show, links: [] });
  assert.equal(focusX(walk, step([{ id: "a", state: "hot" }, { id: "b", state: "warn" }])), 300);
  assert.equal(focusX(walk, step([{ id: "a" }, { id: "b", state: "hot", x: 700 }])), 700);
  assert.equal(focusX(walk, step([{ id: "a", state: "dim" }])), null);
});

test("every kind of box has a color role, and a role names no kind that does not exist", () => {
  for (const kind of WALK_NODE_KINDS) assert.ok(NODE_ROLE[kind], `no role for ${kind}`);
  assert.deepEqual(Object.keys(NODE_ROLE).sort(), [...WALK_NODE_KINDS].sort());
  assert.equal(NODE_ROLE.cache, "memory");
  assert.equal(NODE_ROLE.database, "data");
  assert.equal(NODE_ROLE.note, "note");
});

test("walkUses says what a whole walk-through draws, so the key under the diagram does not change from step to step", () => {
  const label = { en: "x", bn: "x" };
  const text = { short: "s", title: "t", body: ["b"] };
  type Step = Walkthrough["steps"][number];
  const step = (show: Step["show"], links: Step["links"]): Step => ({ en: text, bn: text, show, links });
  const walk = (steps: Step[]): Walkthrough => ({ width: 760, height: 300, nodes: [{ id: "a", kind: "server", label, x: 100, y: 100 }], metrics: [], steps });
  assert.deepEqual(walkUses(walk([step([{ id: "a" }], [])])), { warn: false, out: false, back: false });
  assert.deepEqual(
    walkUses(walk([step([{ id: "a" }], [{ from: "a", to: "a", flow: "to" }]), step([{ id: "a", state: "warn" }], [])])),
    { warn: true, out: true, back: false },
  );
  assert.deepEqual(walkUses(walk([step([], [{ from: "a", to: "a", flow: "both", state: "warn" }])])), { warn: true, out: true, back: true });
  assert.deepEqual(walkUses(walk([step([], [{ from: "a", to: "a", flow: "back" }])])), { warn: false, out: false, back: true });
});

test("labelPads keeps a line label's pill off the boxes beside it, and never asks the text to move", () => {
  const label = { x: 100, y: 50, w: 40, h: 13 }; // the text spans x 100 to 140
  const box = (x: number, y: number) => ({ x, y, w: 100, h: 56 });
  assert.deepEqual(labelPads(label, []), { left: 4, right: 4 });
  // A box whose edge is 2 units from the text leaves 0.5 for the pill, after 1.5 of clearance.
  assert.deepEqual(labelPads(label, [box(192, 56)]), { left: 4, right: 0.5 });
  assert.deepEqual(labelPads(label, [box(48, 56)]), { left: 0.5, right: 4 });
  // A box that leaves exactly the clearance takes the whole padding of that side.
  assert.deepEqual(labelPads(label, [box(191.5, 56)]), { left: 4, right: 0 });
  // A box far to the side, or above or below the label, changes nothing.
  assert.deepEqual(labelPads(label, [box(400, 56)]), { left: 4, right: 4 });
  assert.deepEqual(labelPads(label, [box(192, 200)]), { left: 4, right: 4 });
});

test("roundedRectPath is a closed path that starts on the top edge", () => {
  const d = roundedRectPath(3, 4, 100, 56, 14);
  assert.ok(d.startsWith("M17 4H89A14 14 0 0 1 103 18"));
  assert.ok(d.endsWith("Z"));
});

// Rules for the real walk-throughs, read from disk like the quiz rules.
const dir = new URL("../src/content/", import.meta.url);
const walks = readdirSync(dir)
  .filter((name) => name.endsWith(".json") && name !== "interview.json")
  .map((name) => JSON.parse(readFileSync(new URL(name, dir), "utf8")) as TopicFile)
  .flatMap((part) =>
    part.sections.flatMap((section) =>
      section.walkthrough ? [{ key: `${part.slug}#${section.id}`, walk: section.walkthrough }] : [],
    ),
  );

const BANGLA = /[\u0980-\u09FF]/u;
// The quiz rule: digits inside a name or a code word (TLS 1.3, H100, top_p) stay Latin.
const plainNumber = /(?<![A-Za-z0-9_\-/.:#@%+])(?<![A-Za-z][\w.\-]*\s)[0-9]+(?:[.,][0-9]+)*(?![A-Za-z0-9_\-/])/;
const outsideCode = (html: string) => html.replace(/<code>.*?<\/code>/g, " ").replace(/<[^>]*>/g, "");

/** Every text of one language of a walk-through. */
function texts(walk: Walkthrough, lang: "en" | "bn"): string[] {
  const out = [...walk.nodes.map((n) => n.label[lang]), ...walk.metrics.map((m) => m[lang])];
  if (walk.caption) out.push(walk.caption[lang]);
  for (const step of walk.steps) {
    const t = step[lang];
    out.push(t.short, t.title, ...t.body, ...(t.points ?? []), ...(t.changes ?? []).map((c) => c.html));
    if (t.note) out.push(t.note.html);
    for (const s of step.show) if (s.sub) out.push(s.sub[lang]);
    for (const l of step.links) if (l.label) out.push(l.label[lang]);
    for (const v of step.values ?? []) if (v && typeof v !== "string") out.push(v[lang]);
  }
  return out;
}

test("there are walk-throughs to check", () => {
  assert.ok(walks.length > 0);
});

// The walk-throughs are not in the page: each is a JSON file that the player loads (src/app/walkthroughs).
const parts = readdirSync(dir)
  .filter((name) => name.endsWith(".json") && name !== "interview.json")
  .map((name) => JSON.parse(readFileSync(new URL(name, dir), "utf8")) as TopicFile);

test("every walk-through is served at the path its section is given, and nothing else is", () => {
  const params = walkthroughParams(parts);
  assert.equal(params.length, walks.length, "one file for each walk-through");
  assert.equal(new Set(params.map((p) => `${p.slug}/${p.file}`)).size, params.length, "no file is listed twice");
  for (const { slug, file } of params) {
    assert.match(file, /^[A-Za-z0-9_-]+\.json$/);
    const section = parts.find((p) => p.slug === slug)?.sections.find((s) => `${s.id}.json` === file);
    assert.ok(section?.walkthrough, `${slug}/${file} is a section with a walk-through`);
    assert.equal(findWalkthrough(parts, slug, file), section.walkthrough);
    assert.equal(walkthroughPath(slug, section.id), `/walkthroughs/${slug}/${file}`);
  }
  assert.equal(findWalkthrough(parts, "system-design", "s999.json"), undefined);
  assert.equal(findWalkthrough(parts, "system-design", "s1"), undefined, "the extension is required");
  assert.equal(findWalkthrough(parts, "no-such-part", "s1.json"), undefined);
});

test("a walk-through says the same thing in English and Bangla", () => {
  for (const { key, walk } of walks) {
    walk.steps.forEach((step, i) => {
      const { en, bn } = step;
      const where = `${key} step ${i + 1}`;
      assert.equal(en.body.length, bn.body.length, `${where}: paragraphs`);
      assert.equal(en.points?.length ?? 0, bn.points?.length ?? 0, `${where}: points`);
      assert.deepEqual(en.changes?.map((c) => c.sign), bn.changes?.map((c) => c.sign), `${where}: changes`);
      assert.equal(en.note?.kind, bn.note?.kind, `${where}: note`);
    });
    for (const text of texts(walk, "en")) assert.ok(!BANGLA.test(text), `${key}: Bangla in English: ${text}`);
    for (const text of texts(walk, "bn")) {
      assert.ok(!plainNumber.test(outsideCode(text)), `${key}: Latin digits in Bangla: ${text}`);
    }
  }
});

test("shared readout values have no Bangla, so both sites can show them", () => {
  for (const { key, walk } of walks) {
    for (const step of walk.steps) {
      for (const v of step.values ?? []) {
        if (typeof v === "string") assert.ok(!BANGLA.test(v), `${key}: ${v}`);
      }
    }
  }
});

test("in every step, in both languages, the shown boxes fit the diagram and do not overlap", () => {
  for (const { key, walk } of walks) {
    for (const lang of ["en", "bn"] as const) {
      const widths = nodeWidths(walk, lang);
      walk.steps.forEach((step, i) => {
        const boxes = step.show.map((s) => {
          const node = walk.nodes.find((n) => n.id === s.id);
          assert.ok(node, `${key}: unknown node ${s.id}`);
          return { id: s.id, x: s.x ?? node.x, y: s.y ?? node.y, w: widths.get(s.id) ?? 0, h: NODE_H };
        });
        for (const b of boxes) {
          const where = `${key} step ${i + 1} (${lang}): ${b.id}`;
          // Badges stick out 9 units above a box.
          assert.ok(b.x - b.w / 2 >= 0 && b.x + b.w / 2 <= walk.width, `${where} is cut off left or right`);
          assert.ok(b.y - b.h / 2 - 9 >= 0 && b.y + b.h / 2 <= walk.height, `${where} is cut off top or bottom`);
        }
        for (let p = 0; p < boxes.length; p++) {
          for (let q = p + 1; q < boxes.length; q++) {
            const a = boxes[p];
            const b = boxes[q];
            const apart = Math.abs(a.x - b.x) >= (a.w + b.w) / 2 + 8 || Math.abs(a.y - b.y) >= (a.h + b.h) / 2 + 8;
            assert.ok(apart, `${key} step ${i + 1} (${lang}): ${a.id} and ${b.id} overlap`);
          }
        }
      });
    }
  }
});
