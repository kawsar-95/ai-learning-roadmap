import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");

function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a: string, b: string): number {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}
const BACKGROUND = css.match(/\.code-block \{[^}]*?background: (#[0-9a-f]{6})/)?.[1] ?? "";

test("code blocks: the language label is at least 4.5:1 and 12 px", () => {
  const rule = css.match(/\.code-block-lang \{[^}]*\}/)?.[0] ?? "";
  const color = rule.match(/color: (#[0-9a-f]{6})/)?.[1] ?? "";
  assert.ok(BACKGROUND && color, "found the rule");
  assert.ok(contrast(color, BACKGROUND) >= 4.5, `label contrast ${contrast(color, BACKGROUND).toFixed(2)}`);
  assert.match(rule, /font-size: 12px/);
});

test("code blocks: comment tokens (#768390 in the Part JSON) are lifted to at least 4.5:1", () => {
  const lifted = css.match(/span\[style\*="color:#768390"\] \{ color: (#[0-9a-f]{6}) !important; \}/)?.[1] ?? "";
  assert.ok(lifted, "found the override");
  assert.ok(contrast(lifted, BACKGROUND) >= 4.5, `comment contrast ${contrast(lifted, BACKGROUND).toFixed(2)}`);
  assert.ok(contrast("#768390", BACKGROUND) < 4.5, "the original color is below AA, so the override is still needed");
});
