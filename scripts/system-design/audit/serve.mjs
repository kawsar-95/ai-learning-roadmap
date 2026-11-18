// Serves out/ the way GitHub Pages serves the site, for the audits in this folder.
// Usage: node scripts/system-design/audit/serve.mjs [port] [basePath]
// The Pages build sets PAGES_BASE_PATH=/ai-learning-roadmap, and then the site is at
// http://127.0.0.1:<port>/ai-learning-roadmap/. Without a base path it is at the root.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const out = fileURLToPath(new URL("../../../out/", import.meta.url));
const port = Number(process.argv[2] || 8941);
const base = (process.argv[3] || "").replace(/\/$/, "");
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".txt": "text/plain; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".webmanifest": "application/manifest+json",
  ".woff2": "font/woff2",
};

function notFound(res) {
  res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("Not found");
}

http
  .createServer((req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    let rel = decodeURIComponent(url.pathname);
    if (base && rel !== base && !rel.startsWith(base + "/")) return notFound(res);
    rel = rel.slice(base.length) || "/";
    let file = path.join(out, rel);
    if (!file.startsWith(out)) return notFound(res);
    if (rel.endsWith("/")) file = path.join(file, "index.html");
    else if (!path.extname(file) && fs.existsSync(path.join(file, "index.html"))) {
      res.writeHead(301, { Location: url.pathname + "/" });
      return res.end();
    }
    fs.readFile(file, (error, data) => {
      if (error) return notFound(res);
      res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] ?? "application/octet-stream" });
      res.end(data);
    });
  })
  .listen(port, "127.0.0.1", () => console.log(`serving ${out} at http://127.0.0.1:${port}${base}/`));
