import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import manifest from "../src/app/manifest.ts";
import { PLACEHOLDER, buildManifest, injectManifest } from "../scripts/precache.mjs";

const publicDir = fileURLToPath(new URL("../public/", import.meta.url));

test("manifest: URLs are relative, so they work under the GitHub Pages base path", () => {
  const m = manifest();
  assert.equal(m.start_url, "./");
  assert.equal(m.scope, "./");
  for (const icon of m.icons ?? []) assert.doesNotMatch(icon.src, /^\//);
});

test("manifest: has the 192 px and 512 px icons that install needs, and a maskable icon", () => {
  const icons = manifest().icons ?? [];
  assert.ok(icons.some((i) => i.sizes === "192x192"));
  assert.ok(icons.some((i) => i.sizes === "512x512" && i.purpose === "any"));
  assert.ok(icons.some((i) => i.purpose === "maskable"));
  for (const icon of icons) assert.ok(existsSync(publicDir + icon.src), `missing public/${icon.src}`);
});

test("manifest: opens as a standalone app", () => {
  assert.equal(manifest().display, "standalone");
});

// --- Offline first: scripts/precache.mjs and public/sw.js ---

const swSource = readFileSync(publicDir + "sw.js", "utf8");

function makeOut() {
  const dir = mkdtempSync(join(tmpdir(), "out-"));
  const files: Record<string, string> = {
    "index.html": "home",
    "topics/inference/index.html": "inference",
    "topics/inference/index.txt": "rsc",
    "_next/static/chunks/app.js": "js",
    "search-index.json": "{}",
    "sw.js": swSource,
    "next.svg": "<svg/>",
    "_not-found/index.html": "nf",
    "roadmap/index.html": "roadmap",
    "roadmap/11-llm-engineering/01-prompt-engineering/index.html": "lesson",
    "roadmap/11-llm-engineering/01-prompt-engineering/index.txt": "rsc",
  };
  for (const [file, text] of Object.entries(files)) {
    mkdirSync(dirname(join(dir, file)), { recursive: true });
    writeFileSync(join(dir, file), text);
  }
  return dir;
}

test("precache: lists pages as their folder URL, but not the lesson pages,, their RSC index.txt and the files they need, not sw.js", () => {
  const urls = buildManifest(makeOut()).map((e: { url: string }) => e.url);
  assert.deepEqual(urls, ["", "_next/static/chunks/app.js", "roadmap/", "search-index.json", "topics/inference/", "topics/inference/index.txt"]);
});

test("precache: the revision changes only when the file changes", () => {
  const dir = makeOut();
  const before = buildManifest(dir);
  writeFileSync(join(dir, "topics/inference/index.html"), "inference v2");
  const after = buildManifest(dir);
  const rev = (m: { url: string; rev: string }[], url: string) => m.find((e) => e.url === url)?.rev;
  assert.equal(rev(before, ""), rev(after, ""));
  assert.notEqual(rev(before, "topics/inference/"), rev(after, "topics/inference/"));
});

test("precache: public/sw.js has the placeholder that the build replaces", () => {
  assert.ok(swSource.includes(PLACEHOLDER));
  assert.throws(() => injectManifest("no placeholder", []));
});

/** Runs sw.js with a fake browser. `online` controls fetch(). */
function loadWorker(manifest: { url: string; rev: string }[]) {
  const stores = new Map<string, Map<string, Response>>();
  const href = (r: string | Request) => new URL(typeof r === "string" ? r : r.url, "https://x.test").href;
  const strip = (u: string) => u.split("?")[0];
  const open = async (name: string) => {
    if (!stores.has(name)) stores.set(name, new Map());
    const store = stores.get(name)!;
    return {
      match: async (r: string | Request, o?: { ignoreSearch?: boolean }) => {
        const want = href(r);
        for (const [k, v] of store) if (k === want || (o?.ignoreSearch && strip(k) === strip(want))) return v.clone();
      },
      put: async (r: string | Request, res: Response) => void store.set(href(r), res),
      keys: async () => [...store.keys()].map((url) => ({ url })),
      delete: async (r: { url: string }) => store.delete(r.url),
    };
  };
  const caches = {
    open,
    keys: async () => [...stores.keys()],
    delete: async (n: string) => stores.delete(n),
    match: async (r: string | Request, o?: { ignoreSearch?: boolean }) => {
      for (const name of stores.keys()) {
        const hit = await (await open(name)).match(r, o);
        if (hit) return hit;
      }
    },
  };
  const state = { online: true, fetched: [] as string[] };
  const listeners: Record<string, (e: unknown) => void> = {};
  const self = {
    registration: { scope: "https://x.test/repo/" },
    location: { origin: "https://x.test" },
    addEventListener: (type: string, fn: (e: unknown) => void) => (listeners[type] = fn),
    skipWaiting: async () => {},
    clients: { claim: async () => {} },
  };
  const fetch = async (r: string | Request) => {
    if (!state.online) throw new TypeError("offline");
    state.fetched.push(href(r));
    return new Response(`body of ${new URL(href(r)).pathname}`);
  };
  vm.runInNewContext(injectManifest(swSource, manifest), { self, caches, fetch, Response, URL, Map, Set, Promise, Array });

  const run = async (type: string, extra: object = {}) => {
    let done: Promise<unknown> = Promise.resolve();
    let response: Promise<Response> | undefined;
    listeners[type]({ ...extra, waitUntil: (p: Promise<unknown>) => (done = p), respondWith: (p: Promise<Response>) => (response = p) });
    await done;
    return response;
  };
  const get = (path: string, mode = "navigate") =>
    run("fetch", { request: { method: "GET", url: "https://x.test" + path, mode } }) as Promise<Response>;
  return { state, stores, run, get };
}

const MANIFEST = [
  { url: "", rev: "a" },
  { url: "topics/inference/", rev: "b" },
];

test("sw: install saves every page, and pages then open offline", async () => {
  const sw = loadWorker(MANIFEST);
  await sw.run("install");
  assert.deepEqual(sw.state.fetched.sort(), ["https://x.test/repo/", "https://x.test/repo/topics/inference/"]);
  await sw.run("activate");

  sw.state.online = false;
  assert.equal(await (await sw.get("/repo/topics/inference/")).text(), "body of /repo/topics/inference/");
  assert.equal(await (await sw.get("/repo/topics/inference")).text(), "body of /repo/topics/inference/");
  assert.equal(await (await sw.get("/repo/?q=1")).text(), "body of /repo/");
  assert.match(await (await sw.get("/repo/topics/unknown/")).text(), /You are offline/);
});

test("sw: saved pages come from the cache even online", async () => {
  const sw = loadWorker(MANIFEST);
  await sw.run("install");
  sw.state.fetched = [];
  await sw.get("/repo/topics/inference/");
  assert.deepEqual(sw.state.fetched, []);
});

test("sw: a new build downloads only changed files and deletes old ones", async () => {
  const old = loadWorker(MANIFEST);
  await old.run("install");
  // Same caches, new worker with one changed page.
  const sw = loadWorker([{ url: "", rev: "a" }, { url: "topics/inference/", rev: "c" }]);
  sw.stores.clear();
  for (const [name, store] of old.stores) sw.stores.set(name, store);
  await sw.run("install");
  assert.deepEqual(sw.state.fetched, ["https://x.test/repo/topics/inference/"]);
  await sw.run("activate");
  const keys = [...sw.stores.get("precache-v1")!.keys()].sort();
  assert.deepEqual(keys, ["https://x.test/repo/?__rev=a", "https://x.test/repo/topics/inference/?__rev=c"]);
});
