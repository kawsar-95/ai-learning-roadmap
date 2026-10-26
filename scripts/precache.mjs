// Runs after `next build`. It writes the list of files to save for offline
// use into out/sw.js, so the service worker saves the whole site at install.
//
// Each entry has a revision (a hash of the file). A new build changes sw.js
// only where files changed, and the worker downloads only those files.

import { createHash } from "node:crypto";
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

export const PLACEHOLDER = "/* PRECACHE_MANIFEST */ []";

// Pages and the files they need. index.txt is the RSC payload the router
// fetches on a link click; without it, offline navigation waits forever.
// Not included: sw.js itself, the __next.* segment .txt files (prefetch
// only, and Next does not prefetch offline), the unused starter SVGs, and the
// curriculum lesson pages under roadmap/<phase>/<lesson>/.
const KEEP = [
  /\.html$/,
  /(^|\/)index\.txt$/,
  /^_next\/static\//,
  /^icons\//,
  /(^|\/)search-index\.json$/,
  /^manifest\.webmanifest$/,
  /^favicon\.ico$/,
  /^apple-icon\.png$/,
];
// The 1084 curriculum lesson pages would make the install download huge; they load online only.
const SKIP = [/^_not-found\//, /^(bn\/)?roadmap\/[^/]+\/[^/]+\//];

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  });
}

/** The files in outDir to save offline, as URLs relative to the site root. */
export function buildManifest(outDir) {
  return walk(outDir)
    .map((path) => ({ path, file: relative(outDir, path).split(sep).join("/") }))
    .filter(({ file }) => KEEP.some((re) => re.test(file)) && !SKIP.some((re) => re.test(file)))
    .map(({ path, file }) => ({
      // trailingSlash: true serves "topics/x/index.html" at "topics/x/".
      url: file.replace(/(^|\/)index\.html$/, "$1"),
      rev: createHash("md5").update(readFileSync(path)).digest("hex").slice(0, 12),
    }))
    .sort((a, b) => a.url.localeCompare(b.url));
}

export function injectManifest(swSource, manifest) {
  if (!swSource.includes(PLACEHOLDER)) throw new Error(`sw.js has no ${PLACEHOLDER}`);
  return swSource.replace(PLACEHOLDER, JSON.stringify(manifest));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const outDir = fileURLToPath(new URL("../out/", import.meta.url));
  const manifest = buildManifest(outDir);
  const swPath = join(outDir, "sw.js");
  writeFileSync(swPath, injectManifest(readFileSync(swPath, "utf8"), manifest));
  console.log(`sw.js: ${manifest.length} files saved for offline use`);
}
