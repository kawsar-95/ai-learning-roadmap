import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { setBanglaLang, withBanglaLang } from "../scripts/set-html-lang.mjs";

const PAGE = '<!DOCTYPE html><html lang="en" data-theme="dark" class="x"><head><title>t</title></head><body lang="en">hi</body></html>';

test("withBanglaLang changes only the lang of the <html> tag", () => {
  const out = withBanglaLang(PAGE);
  assert.match(out, /^<!DOCTYPE html><html lang="bn" data-theme="dark" class="x">/);
  assert.match(out, /<body lang="en">/);
});

test("withBanglaLang leaves a page that has no lang=en alone", () => {
  const page = '<!DOCTYPE html><html lang="bn"><head></head></html>';
  assert.equal(withBanglaLang(page), page);
});

test("setBanglaLang rewrites the pages under bn/ and nothing else", () => {
  const dir = mkdtempSync(join(tmpdir(), "lang-"));
  const files = ["index.html", "404.html", "topics/a/index.html", "bn/index.html", "bn/topics/a/index.html", "bn/topics/a/index.txt"];
  for (const file of files) {
    mkdirSync(dirname(join(dir, file)), { recursive: true });
    writeFileSync(join(dir, file), PAGE);
  }
  assert.equal(setBanglaLang(dir), 2);
  const lang = (file: string) => readFileSync(join(dir, file), "utf8").match(/<html lang="(\w+)"/)?.[1];
  assert.equal(lang("index.html"), "en");
  assert.equal(lang("404.html"), "en");
  assert.equal(lang("topics/a/index.html"), "en");
  assert.equal(lang("bn/index.html"), "bn");
  assert.equal(lang("bn/topics/a/index.html"), "bn");
  assert.equal(readFileSync(join(dir, "bn/topics/a/index.txt"), "utf8"), PAGE);
});
