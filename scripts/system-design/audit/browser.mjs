// The browser for the audits in this folder, the way scripts/screenshots does it: `playwright-core` is not a
// dependency of the site, so it is looked up in SHOTS_WORK (default <temp dir>/readme-screenshots).
//   SHOTS_WORK  a directory where `npm init -y && npm i playwright-core` has been run
//   CHROME      the Chrome or Chromium binary (default /usr/bin/google-chrome)
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";

const work = process.env.SHOTS_WORK || path.join(os.tmpdir(), "readme-screenshots");
const { chromium } = createRequire(path.join(work, "noop.js"))("playwright-core");

export const launch = () => chromium.launch({ executablePath: process.env.CHROME || "/usr/bin/google-chrome", args: ["--no-sandbox"] });
