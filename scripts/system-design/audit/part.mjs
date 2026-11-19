// Which Part the audits in this folder look at, and the walk-throughs it has.
//   PART  the Part's slug (default system-design, Part 18)
// Part 18 keeps its walk-throughs inside its topic file. Every other Part has a file for each section in
// src/content/walkthroughs/<Part>/<section>.json, built by scripts/walkthroughs/build.py.
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const content = fileURLToPath(new URL("../../../src/content/", import.meta.url));
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

export const slug = process.env.PART || "system-design";

/** The sections of the Part that have a walk-through, in the Part's order: [{ id, walkthrough }]. */
export function partWalks(part = slug) {
  const file = `${content}${part}.json`;
  if (!existsSync(file)) throw new Error(`PART=${part}: there is no ${file}`);
  return readJson(file).sections.flatMap((s) => {
    const own = `${content}walkthroughs/${part}/${s.id}.json`;
    const walkthrough = s.walkthrough ?? (existsSync(own) ? readJson(own) : null);
    return walkthrough ? [{ id: s.id, walkthrough }] : [];
  });
}

/** How many walk-through files the whole site serves: those of every Part, inline or in a file of their own. */
export function siteWalkCount() {
  let n = 0;
  for (const name of readdirSync(content).filter((f) => f.endsWith(".json"))) {
    const sections = readJson(`${content}${name}`).sections;
    if (Array.isArray(sections)) n += sections.filter((s) => s.walkthrough).length;
  }
  const dir = `${content}walkthroughs/`;
  if (existsSync(dir)) {
    for (const part of readdirSync(dir, { withFileTypes: true })) {
      if (part.isDirectory()) n += readdirSync(`${dir}${part.name}`).filter((f) => f.endsWith(".json")).length;
    }
  }
  return n;
}
