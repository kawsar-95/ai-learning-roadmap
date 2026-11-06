// Maps published YouTube titles to stored titles with the site's own storedTitle() (src/lib/video-check.ts),
// so the data and the TypeScript function cannot disagree.
//   echo '["MCP vs UTCP 🔀"]' | node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON stored_titles.mjs
import { readFileSync } from "node:fs";
import { storedTitle } from "../../src/lib/video-check.ts";

const titles = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(titles.map(storedTitle)));
