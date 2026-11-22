import { test } from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import { initScript } from "../src/lib/init-script.ts";
import { THEME_INIT_SCRIPT, THEME_STORAGE_KEY } from "../src/lib/theme.ts";
import { PANEL_INIT_SCRIPT, panelStorageKey } from "../src/lib/panels.ts";
import { LANG_STORAGE_KEY, langInitScript } from "../src/lib/i18n.ts";

type Case = { storage: Record<string, string>; path: string; prefersLight: boolean; throws?: boolean };

/** Runs a head script against a fake browser; returns what it set on <html> and where it sent the page. */
function run(script: string, { storage, path, prefersLight, throws }: Case) {
  const attrs: Record<string, string> = {};
  let replaced: string | null = null;
  const context = {
    localStorage: {
      getItem(key: string) {
        if (throws) throw new Error("blocked");
        return storage[key] ?? null;
      },
    },
    location: { pathname: path, search: "?q=1", hash: "#h", replace: (url: string) => (replaced = url) },
    window: { matchMedia: (q: string) => ({ matches: q === "(prefers-color-scheme: light)" && prefersLight }) },
    document: { documentElement: { setAttribute: (name: string, value: string) => (attrs[name] = value) } },
  };
  vm.runInNewContext(script, context);
  return { attrs, replaced };
}

const CASES: Case[] = [
  { storage: {}, path: "/topics/inference/", prefersLight: false },
  { storage: {}, path: "/topics/inference/", prefersLight: true },
  { storage: { [THEME_STORAGE_KEY]: "light" }, path: "/bn/topics/inference/", prefersLight: false },
  { storage: { [panelStorageKey("parts")]: "collapsed" }, path: "/topics/inference/", prefersLight: false },
  { storage: { [panelStorageKey("toc")]: "collapsed", [panelStorageKey("parts")]: "collapsed" }, path: "/", prefersLight: true },
  { storage: { [LANG_STORAGE_KEY]: "bn" }, path: "/topics/inference/", prefersLight: false },
  { storage: { [LANG_STORAGE_KEY]: "en" }, path: "/bn/topics/inference/", prefersLight: false },
  { storage: { [LANG_STORAGE_KEY]: "bn" }, path: "/repo/topics/inference/", prefersLight: false },
  { storage: {}, path: "/topics/inference/", prefersLight: false, throws: true },
];

for (const base of ["", "/repo"]) {
  test(`initScript does what the theme, panel, and language scripts do together (base "${base}")`, () => {
    const separate = [THEME_INIT_SCRIPT, PANEL_INIT_SCRIPT, langInitScript(base)];
    for (const c of CASES) {
      // The separate scripts all write to one <html>; run them against one shared fake.
      const attrs: Record<string, string> = {};
      let replaced: string | null = null;
      for (const script of separate) {
        const r = run(script, c);
        Object.assign(attrs, r.attrs);
        replaced = r.replaced ?? replaced;
      }
      const combined = run(initScript(base), c);
      assert.deepEqual(combined.attrs, attrs, JSON.stringify(c));
      assert.equal(combined.replaced, replaced, JSON.stringify(c));
    }
  });
}

test("initScript is one script, and one failing storage read does not throw", () => {
  const script = initScript("");
  assert.doesNotThrow(() => run(script, { storage: {}, path: "/", prefersLight: false, throws: true }));
  assert.equal(script.startsWith("(function(){try{"), true);
  assert.equal((script.match(/\(function\(\)\{/g) ?? []).length, 1);
});
