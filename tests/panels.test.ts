import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { COLLAPSED, PANELS, PANEL_INIT_SCRIPT, isCollapsed, panelAttribute, panelStorageKey } from "../src/lib/panels.ts";
import type { Panel } from "../src/lib/panels.ts";

test("isCollapsed: only the saved word folds a column", () => {
  assert.equal(isCollapsed(COLLAPSED), true);
  for (const stored of [null, "", "expanded", "1", "true", "Collapsed"]) assert.equal(isCollapsed(stored), false, String(stored));
});

test("each column has its own key and its own attribute", () => {
  assert.equal(new Set(PANELS.map(panelStorageKey)).size, PANELS.length);
  assert.equal(new Set(PANELS.map(panelAttribute)).size, PANELS.length);
});

test("the saved keys keep their names: a reader's choice lives under them, and docs/architecture.md lists them", () => {
  assert.equal(panelStorageKey("parts"), "panel-parts");
  assert.equal(panelStorageKey("toc"), "panel-toc");
  const docs = readFileSync(new URL("../docs/architecture.md", import.meta.url), "utf8");
  for (const panel of PANELS) assert.ok(docs.includes(`\`${panelStorageKey(panel)}\``), `docs/architecture.md does not list ${panelStorageKey(panel)}`);
});

test("globals.css selects on the attribute and the value that the script sets", () => {
  const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");
  const lines = css.split("\n").map((line) => line.trim());
  const selector = (panel: Panel) => `[${panelAttribute(panel)}="${COLLAPSED}"]`;
  for (const panel of PANELS) {
    const sel = selector(panel);
    assert.ok(css.includes(`@custom-variant ${panel}-collapsed (&:where(${sel}, ${sel} *));`), `globals.css has no ${panel}-collapsed variant on ${sel}`);
    assert.ok(lines.includes(`${sel} .topic-grid {`), `globals.css has no rule for ${sel} .topic-grid`);
  }
  const both = PANELS.map(selector).join("");
  assert.ok(lines.includes(`${both} .topic-grid {`), `globals.css has no rule for ${both} .topic-grid`);
});

/** Runs the inline head script against a fake browser and returns the attributes it set on <html>. */
function runInitScript(stored: Partial<Record<Panel, string>>, storageThrows = false) {
  const attrs: Record<string, string> = {};
  const context = {
    localStorage: {
      getItem(key: string) {
        if (storageThrows) throw new Error("blocked");
        const panel = PANELS.find((p) => panelStorageKey(p) === key);
        return panel ? (stored[panel] ?? null) : null;
      },
    },
    document: { documentElement: { setAttribute: (name: string, value: string) => (attrs[name] = value) } },
  };
  vm.runInNewContext(PANEL_INIT_SCRIPT, context);
  return attrs;
}

test("PANEL_INIT_SCRIPT agrees with isCollapsed for every pair of saved values", () => {
  const values = [COLLAPSED, "expanded", "", "x", undefined];
  for (const parts of values) {
    for (const toc of values) {
      const stored = { parts, toc };
      const attrs = runInitScript(stored);
      for (const panel of PANELS) {
        const folded = isCollapsed(stored[panel] ?? null);
        assert.equal(attrs[panelAttribute(panel)], folded ? COLLAPSED : undefined, `${panel} saved as ${stored[panel]}`);
      }
    }
  }
});

test("PANEL_INIT_SCRIPT folds one column without touching the other", () => {
  assert.deepEqual(runInitScript({ parts: COLLAPSED }), { "data-parts": COLLAPSED });
  assert.deepEqual(runInitScript({ toc: COLLAPSED }), { "data-toc": COLLAPSED });
  assert.deepEqual(runInitScript({}), {});
});

test("PANEL_INIT_SCRIPT does not throw when storage is blocked, and folds nothing", () => {
  let attrs: Record<string, string> = { before: "x" };
  assert.doesNotThrow(() => (attrs = runInitScript({ parts: COLLAPSED, toc: COLLAPSED }, true)));
  assert.deepEqual(attrs, {});
});
