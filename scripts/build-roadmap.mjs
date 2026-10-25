// Reads the ROADMAP.md of the "AI Engineering from Scratch" curriculum and
// writes src/data/roadmap-lessons.json: every phase and lesson, in order.
//
//   node scripts/build-roadmap.mjs <path to the curriculum repo>
//
// ROADMAP.md has one table per phase. Most rows link to the lesson folder;
// the Phase 0 rows do not, so the folder is found by its number prefix under
// phases/<phase folder>/. Run it again to pick up new lessons, then commit
// the JSON.

import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repo = resolve(process.argv[2] ?? "");
if (!process.argv[2]) {
  console.error("usage: node scripts/build-roadmap.mjs <path to ai-engineering-from-scratch>");
  process.exit(1);
}

const phasesDir = join(repo, "phases");
const phaseFolders = readdirSync(phasesDir).filter((name) => /^\d\d-/.test(name));

/** "~75 min" -> 75, "~35 hr" -> 2100. */
function minutes(est) {
  const match = est.match(/~\s*(\d+(?:\.\d+)?)\s*(min|hr)/);
  if (!match) throw new Error(`Cannot read the estimate "${est}"`);
  return Math.round(Number(match[1]) * (match[2] === "hr" ? 60 : 1));
}

const phases = [];
let phase = null;

for (const line of readFileSync(join(repo, "ROADMAP.md"), "utf8").split("\n")) {
  const heading = line.match(/^## Phase (\d+): (.+?) — \S+ \(~(\d+) hours?\)/);
  if (heading) {
    const n = Number(heading[1]);
    const folder = phaseFolders.find((name) => Number(name.slice(0, 2)) === n);
    if (!folder) throw new Error(`No folder under phases/ for Phase ${n}`);
    phase = { phase: n, folder, title: heading[2].replace(/\s+/g, " ").trim(), hours: Number(heading[3]), lessons: [] };
    phases.push(phase);
    continue;
  }
  const row = line.match(/^\| (\d+) \| (.+?) \| \S+ \| (~[^|]+?) \|\s*$/);
  if (!row || !phase) continue;

  const link = row[2].match(/^\[(.+)\]\((.+)\)$/);
  const num = Number(row[1]);
  let dir;
  if (link) {
    dir = link[2].replace(/\/+$/, "").split("/").pop();
  } else {
    const dirs = readdirSync(join(phasesDir, phase.folder)).filter((name) => Number(name.slice(0, 2)) === num && /^\d\d-/.test(name));
    if (dirs.length !== 1) throw new Error(`Phase ${phase.phase} lesson ${num}: found ${dirs.length} folders`);
    dir = dirs[0];
  }
  if (!readdirSync(join(phasesDir, phase.folder)).includes(dir)) {
    throw new Error(`Phase ${phase.phase} lesson ${num}: phases/${phase.folder}/${dir} does not exist`);
  }
  phase.lessons.push({ n: num, title: (link ? link[1] : row[2]).trim(), dir, minutes: minutes(row[3]) });
}

const total = phases.reduce((sum, p) => sum + p.lessons.length, 0);
const out = fileURLToPath(new URL("../src/data/roadmap-lessons.json", import.meta.url));
writeFileSync(out, JSON.stringify({ phases }, null, 2) + "\n");
console.log(`Wrote ${phases.length} phases and ${total} lessons to ${out}`);
