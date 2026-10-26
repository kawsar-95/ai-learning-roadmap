// Copies the lesson text of the "AI Engineering from Scratch" curriculum into
// this site, for every lesson listed in src/data/roadmap-lessons.json:
//
//   node scripts/build-lessons.mjs <path to the curriculum repo>
//
//   phases/<phase>/<lesson>/docs/en.md  ->  src/data/lessons/<phase>/<lesson>.md
//   phases/<phase>/<lesson>/assets/*    ->  public/lesson-assets/<phase>/<lesson>/assets/*
//
// Run scripts/build-roadmap.mjs first when the lesson list changed, then run
// this, then commit the results. The curriculum is MIT licensed; its notice is
// in src/data/lessons/LICENSE.

import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

if (!process.argv[2]) {
  console.error("usage: node scripts/build-lessons.mjs <path to ai-engineering-from-scratch>");
  process.exit(1);
}
const repo = resolve(process.argv[2]);
const root = fileURLToPath(new URL("../", import.meta.url));
const { phases } = JSON.parse(readFileSync(join(root, "src/data/roadmap-lessons.json"), "utf8"));

const textDir = join(root, "src/data/lessons");
const assetDir = join(root, "public/lesson-assets");
rmSync(textDir, { recursive: true, force: true });
rmSync(assetDir, { recursive: true, force: true });

let lessons = 0;
let assets = 0;
for (const phase of phases) {
  for (const lesson of phase.lessons) {
    const from = join(repo, "phases", phase.folder, lesson.dir);
    const doc = join(from, "docs/en.md");
    if (!existsSync(doc)) throw new Error(`Missing ${doc}`);
    const out = join(textDir, phase.folder, `${lesson.dir}.md`);
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, readFileSync(doc, "utf8"));
    lessons += 1;
    if (existsSync(join(from, "assets"))) {
      cpSync(join(from, "assets"), join(assetDir, phase.folder, lesson.dir, "assets"), { recursive: true });
      assets += 1;
    }
  }
}

writeFileSync(
  join(textDir, "LICENSE"),
  `The lesson text in this folder is copied from
https://github.com/rohitg00/ai-engineering-from-scratch
and is used under the MIT License of that project:

${readFileSync(join(repo, "LICENSE"), "utf8")}`,
);
console.log(`Copied ${lessons} lessons and the assets of ${assets} lessons`);
