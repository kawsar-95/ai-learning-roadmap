// Runs after `next build`, before scripts/precache.mjs. The root layout is one
// layout for both languages, so every page is exported with <html lang="en">,
// including the Bangla pages under /bn/. The head script fixes the attribute
// once it runs, but a crawler, a reader without JavaScript, and a translation
// tool read the static HTML. This sets the language of the files under bn/.
//
// The 404 page is one file for both languages and stays "en".

import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const OPEN_TAG = /^(<!DOCTYPE html>\s*<html[^>]*?\slang=")en(")/i;

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  });
}

/** The page HTML with lang="bn" on <html>, or the same text when it has no lang="en" there. */
export function withBanglaLang(html) {
  return html.replace(OPEN_TAG, "$1bn$2");
}

/** Sets lang="bn" on every .html file under outDir/bn. Returns how many it changed. */
export function setBanglaLang(outDir) {
  let changed = 0;
  for (const path of walk(join(outDir, "bn")).filter((p) => p.endsWith(".html"))) {
    const html = readFileSync(path, "utf8");
    const next = withBanglaLang(html);
    if (next !== html) {
      writeFileSync(path, next);
      changed++;
    }
  }
  return changed;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const count = setBanglaLang(fileURLToPath(new URL("../out/", import.meta.url)));
  console.log(`html lang: ${count} Bangla pages set to "bn"`);
}
