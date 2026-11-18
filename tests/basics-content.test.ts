import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import type { Block, Section, TopicFile } from "../src/lib/content-schema.ts";
import { blockText } from "../src/lib/search.ts";

// Rules for the real "Start here" boxes, read from disk like the quiz rules.
const dir = new URL("../src/content/", import.meta.url);
const parts = readdirSync(dir)
  .filter((name) => name.endsWith(".json") && name !== "interview.json")
  .map((name) => JSON.parse(readFileSync(new URL(name, dir), "utf8")) as TopicFile);

const boxes = parts.flatMap((part) =>
  part.sections.flatMap((section) => (section.basics ? [{ key: `${part.slug}#${section.id}`, section, basics: section.basics }] : [])),
);

const strip = (html: string) => html.replace(/<[^>]*>/g, "").replace(/&[a-z#0-9]+;/g, " ");
const outsideCode = (html: string) => strip(html.replace(/<code>.*?<\/code>/g, " "));
const words = (html: string) => strip(html).match(/\S+/g)?.length ?? 0;
const BANGLA = /[\u0980-\u09FF]/u;

/** Every text field of one language of a box, with its kind. */
function fields(text: NonNullable<Section["basics"]>["en"]): { kind: "idea" | "term" | "meaning" | "point"; html: string }[] {
  return [
    { kind: "idea", html: text.idea },
    ...text.words.flatMap((w) => [
      { kind: "term" as const, html: w.term },
      { kind: "meaning" as const, html: w.meaning },
    ]),
    ...text.remember.map((html) => ({ kind: "point" as const, html })),
  ];
}

test("the Start here boxes are checked", () => {
  assert.ok(boxes.length > 0);
});

test("every section has a Start here box", () => {
  const missing = parts.flatMap((part) => part.sections.filter((s) => !s.basics).map((s) => `${part.slug}#${s.id}`));
  assert.deepEqual(missing, []);
});

test("the English box is in English", () => {
  for (const { key, basics } of boxes) {
    for (const { kind, html } of fields(basics.en)) assert.doesNotMatch(html, BANGLA, `${key} ${kind}: ${html}`);
  }
});

test("the Bangla box is in Bangla", () => {
  for (const { key, basics } of boxes) {
    const idea = outsideCode(basics.bn.idea);
    const bangla = idea.match(/[\u0980-\u09FF]/gu)?.length ?? 0;
    const latin = idea.match(/[A-Za-z]/g)?.length ?? 0;
    assert.ok(bangla >= latin, `${key} idea is mostly Latin: ${idea}`);
    // A term may stay English (BM25, JSON); its meaning and the points may not.
    for (const { kind, html } of fields(basics.bn)) {
      if (kind !== "term") assert.match(outsideCode(html), BANGLA, `${key} ${kind}: ${html}`);
    }
  }
});

test("the Bangla box writes plain numbers in Bangla digits", () => {
  // The quiz rule: digits inside a name or a code word (GPT-4o, H100, top_p) stay Latin. So does a
  // version after a name (Llama 3, YAML 1.1).
  const plainNumber = /(?<![A-Za-z0-9_\-/.:#@%+])(?<![A-Za-z][\w.\-]*\s)[0-9]+(?:[.,][0-9]+)*(?![A-Za-z0-9_\-/])/;
  for (const { key, basics } of boxes) {
    for (const { kind, html } of fields(basics.bn)) assert.doesNotMatch(outsideCode(html), plainNumber, `${key} ${kind}: ${html}`);
  }
});

test("the box stays short", () => {
  const limits = {
    en: { idea: 45, term: 8, meaning: 30, point: 25 },
    bn: { idea: 60, term: 10, meaning: 40, point: 35 },
  };
  for (const { key, basics } of boxes) {
    for (const lang of ["en", "bn"] as const) {
      for (const { kind, html } of fields(basics[lang])) {
        assert.ok(words(html) <= limits[lang][kind], `${key} ${lang} ${kind} has ${words(html)} words: ${html}`);
      }
    }
  }
});

/** The English a reader sees in a section: title, intro, Technical and Layman's text, and diagram labels. */
function sectionText(section: Section): string {
  const svg = (blocks: Block[]): string[] =>
    blocks.flatMap((b) =>
      b.type === "diagram"
        ? [b.svg.replace(/<[^>]*>/g, " ")]
        : b.type === "callout" || b.type === "analogy"
          ? svg(b.blocks)
          : b.type === "panels"
            ? b.panels.flatMap((p) => svg(p.blocks))
            : [],
    );
  return [section.title, strip(section.sub), ...[...section.body, ...section.layman].map((b) => blockText(b, strip)), ...svg(section.body)].join(
    " ",
  );
}

test("every word to know comes from its section", () => {
  for (const { key, section, basics } of boxes) {
    const raw = sectionText(section);
    const text = raw.toLowerCase();
    for (const { term } of basics.en.words) {
      // A word of 4+ letters (plural ending dropped), or an abbreviation in capitals, must appear in the section.
      const plain = strip(term);
      const stems = plain
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter((w) => w.length >= 4)
        .map((w) => w.replace(/(ies|es|s)$/, ""));
      const abbreviations = plain.match(/\b[A-Z][A-Z0-9]+\b/g) ?? [];
      if (stems.length === 0 && abbreviations.length === 0) continue;
      const found = stems.some((s) => text.includes(s)) || abbreviations.some((a) => new RegExp(`\\b${a}\\b`).test(raw));
      assert.ok(found, `${key}: "${plain}" is not used in the section`);
    }
  }
});
