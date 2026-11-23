import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

// The design scale (docs/architecture.md, Design rules, "Scale"). A page that
// needs a value outside it should use the nearest one, or the scale changes
// here and in the doc together.
const RADIUS = new Set(["", "md", "lg", "2xl", "full"]); // rounded, -md (6), -lg (10), -2xl (16), -full
const RADIUS_PX = new Set(["4px", "6px", "10px", "16px", "50%", "999px", "0"]);
const TEXT_PX = new Set([12, 13, 14, 15, 16, 17, 18, 20, 22, 26, 48, 60]);
const TRACKING = new Set(["-0.03em", "-0.02em", "0.06em", "0.16em"]);

const SRC = fileURLToPath(new URL("../src/", import.meta.url));
function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}
const tsx = walk(SRC).filter((p) => p.endsWith(".tsx"));
const css = readFileSync(join(SRC, "app/globals.css"), "utf8");
const rel = (p: string) => p.replace(SRC, "src/");

test("scale: Tailwind radius classes use only the five radii", () => {
  const bad: string[] = [];
  for (const file of tsx) {
    const text = readFileSync(file, "utf8");
    for (const [match, size] of text.matchAll(/(?<![\w-])rounded(?:-[trblse]{1,2})?(?:-(\[[^\]]+\]|[a-z0-9]+))?(?![\w-])/g)) {
      if (!RADIUS.has(size ?? "")) bad.push(`${rel(file)}: ${match}`);
    }
  }
  assert.deepEqual(bad, []);
});

test("scale: arbitrary text sizes are on the type scale", () => {
  const bad: string[] = [];
  for (const file of tsx) {
    for (const [match, px] of readFileSync(file, "utf8").matchAll(/text-\[(\d+(?:\.\d+)?)px\]/g)) {
      if (!TEXT_PX.has(Number(px))) bad.push(`${rel(file)}: ${match}`);
    }
  }
  assert.deepEqual(bad, []);
});

test("scale: letter-spacing in components is one of four values", () => {
  const bad: string[] = [];
  for (const file of tsx) {
    for (const [match, value] of readFileSync(file, "utf8").matchAll(/tracking-\[([^\]]+)\]/g)) {
      if (!TRACKING.has(value)) bad.push(`${rel(file)}: ${match}`);
    }
  }
  assert.deepEqual(bad, []);
});

/** The rules of globals.css that are not part of the walk-through sketch (`.wk-`). */
function siteRules(): { selector: string; body: string }[] {
  const rules: { selector: string; body: string }[] = [];
  for (const [, selector, body] of css.replace(/\/\*[\s\S]*?\*\//g, "").matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    if (!/\.wk-|\[lang="bn"\] \.wk|^\s*:root|data-theme/.test(selector)) rules.push({ selector: selector.trim(), body });
  }
  return rules;
}

test("scale: site CSS (outside the walk-through) uses the radius and type scale", () => {
  const bad: string[] = [];
  for (const { selector, body } of siteRules()) {
    for (const [, v] of body.matchAll(/border-radius:\s*([^;]+);/g)) if (!RADIUS_PX.has(v.trim())) bad.push(`${selector}: border-radius ${v}`);
    for (const [, v] of body.matchAll(/font-size:\s*(\d+(?:\.\d+)?)px;/g)) if (!TEXT_PX.has(Number(v))) bad.push(`${selector}: font-size ${v}px`);
    for (const [, v] of body.matchAll(/letter-spacing:\s*([^;]+);/g)) if (v.trim() !== "normal" && !TRACKING.has(v.trim())) bad.push(`${selector}: letter-spacing ${v}`);
  }
  assert.deepEqual(bad, []);
});

// --- The walk-through is a documented sketch style, kept apart from the site's flat look ---

test("sketch: hard offset shadows exist only in the walk-through (.wk-) rules", () => {
  const stray: string[] = [];
  for (const { selector, body } of siteRules()) {
    // An offset shadow with no blur: "2px 2.5px 0 color".
    if (/box-shadow:\s*-?[\d.]+px\s+-?[\d.]+px\s+0\s+(?!0)/.test(body)) stray.push(selector);
  }
  assert.deepEqual(stray, []);
});

test("sketch: every --wk- color is defined in both themes", () => {
  const dark = css.match(/:root\[data-theme="dark"\]\s*\{([\s\S]*?)\n\}/)?.[1] ?? "";
  const light = css.match(/:root\[data-theme="light"\]\s*\{([\s\S]*?)\n\}/)?.[1] ?? "";
  const names = (block: string) => new Set([...block.matchAll(/(--wk-[a-z-]+):/g)].map((m) => m[1]));
  const d = names(dark);
  const l = names(light);
  assert.ok(d.size >= 20, `found ${d.size} dark --wk- colors`);
  assert.deepEqual([...d].filter((n) => !l.has(n)), [], "defined in dark only");
  assert.deepEqual([...l].filter((n) => !d.has(n)), [], "defined in light only");
});
