// Renders code blocks with Shiki for scripts/system-design/build.py. Not run by hand: build.py pipes this file
// into `node --input-type=module -` with SHIKI_WORK as the working directory (so `shiki` resolves from there),
// and HL_IN / HL_OUT name the JSON files to read and write.
//   HL_IN   [{ "lang": "python", "code": "..." }, ...]
//   HL_OUT  one HTML string for each item, in the same order
import { codeToHtml } from "shiki";
import { readFileSync, writeFileSync } from "node:fs";

const LANGS = ["python", "sql", "http", "bash", "json", "text", "javascript", "typescript", "yaml"];
const items = JSON.parse(readFileSync(process.env.HL_IN, "utf8"));
const out = [];
for (const { lang, code } of items) {
  out.push(await codeToHtml(code, { lang: LANGS.includes(lang) ? lang : "text", theme: "github-dark-dimmed" }));
}
writeFileSync(process.env.HL_OUT, JSON.stringify(out));
