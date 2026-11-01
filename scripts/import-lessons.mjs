// Copies the lesson text of the "AI Engineering from Scratch" curriculum
// (MIT license) into src/content/lessons/, one file per roadmap lesson:
//
//   src/content/lessons/<phase folder>/<lesson dir>.md   from phases/<folder>/<dir>/docs/en.md
//   src/content/lessons/LICENSE                          the curriculum's license, kept with the copy
//   src/content/lessons/source.json                      the repo and commit the copy comes from
//
//   node scripts/import-lessons.mjs <path to the curriculum repo>
//
// Run scripts/build-roadmap.mjs first when the curriculum adds lessons, then
// this script, then commit both outputs.

import { execFileSync } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

if (!process.argv[2]) {
  console.error("usage: node scripts/import-lessons.mjs <path to ai-engineering-from-scratch>");
  process.exit(1);
}
const repo = resolve(process.argv[2]);
const out = fileURLToPath(new URL("../src/content/lessons/", import.meta.url));
const { phases } = JSON.parse(readFileSync(new URL("../src/data/roadmap-lessons.json", import.meta.url), "utf8"));

rmSync(out, { recursive: true, force: true });
let count = 0;
for (const phase of phases) {
  mkdirSync(join(out, phase.folder), { recursive: true });
  for (const lesson of phase.lessons) {
    copyFileSync(join(repo, "phases", phase.folder, lesson.dir, "docs", "en.md"), join(out, phase.folder, `${lesson.dir}.md`));
    count++;
  }
}
copyFileSync(join(repo, "LICENSE"), join(out, "LICENSE"));
const commit = execFileSync("git", ["-C", repo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
writeFileSync(join(out, "source.json"), JSON.stringify({ repo: "rohitg00/ai-engineering-from-scratch", commit }, null, 2) + "\n");
console.log(`Copied ${count} lessons from commit ${commit.slice(0, 7)} to ${out}`);
