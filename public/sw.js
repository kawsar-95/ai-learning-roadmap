// The service worker. It makes the site offline first: at install it saves
// every page and the files they need, then it serves them from the device.
// src/components/layout/ServiceWorker.tsx registers it.
//
// - Saved files (the build list): cache first. A new build installs a new
//   worker, which downloads only the files that changed.
// - Other files (RSC segment .txt for prefetch): network first, then the
//   saved copy.
//
// scripts/precache.mjs replaces the placeholder below after `next build`.

const PRECACHE_MANIFEST = /* PRECACHE_MANIFEST */ [];

const PRECACHE = "precache-v1";
const RUNTIME = "runtime-v1";
const MAX_RUNTIME = 400;
const SCOPE = new URL(self.registration.scope).pathname;
const DOWNLOADS = 6;

// Site URL -> cache key. The key holds the revision, so a changed file gets a new key.
const KEYS = new Map(PRECACHE_MANIFEST.map((e) => [SCOPE + e.url, `${SCOPE}${e.url}?__rev=${e.rev}`]));

// The page for a URL that is not saved. It uses the site's colors, speaks the
// language of the URL, and links to what is saved: the home page, the Parts
// list on it, and the contents page.
const OFFLINE_TEXT = {
  en: {
    lang: "en",
    title: "Offline — AI Engineering",
    h1: "You are offline",
    body: "This page is not saved on this device. The Parts, the contents page, and the interview questions are; the roadmap lessons need a connection.",
    links: [["", "Home"], ["#parts", "Parts"], ["contents/", "Contents"]],
  },
  bn: {
    lang: "bn",
    title: "অফলাইন — AI Engineering",
    h1: "আপনি অফলাইনে আছেন",
    body: "এই পাতাটা এই ডিভাইসে সেভ করা নেই। পার্টগুলো, সূচিপত্র আর ইন্টারভিউ প্রশ্ন সেভ করা আছে; রোডম্যাপের লেসনের জন্য ইন্টারনেট লাগবে।",
    links: [["bn/", "হোম"], ["bn/#parts", "পার্টগুলো"], ["bn/contents/", "সূচিপত্র"]],
  },
};

function offlineHtml(url) {
  const bangla = new URL(url).pathname.startsWith(SCOPE + "bn/");
  const t = bangla ? OFFLINE_TEXT.bn : OFFLINE_TEXT.en;
  const links = t.links.map(([href, label]) => `<a href="${SCOPE}${href}">${label}</a>`).join(" · ");
  return `<!doctype html><html lang="${t.lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>${t.title}</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0e1115;color:#e6e6e6;font:16px/1.6 system-ui,sans-serif;padding:24px;text-align:center}
main{max-width:30rem}p{color:#b8bfc7}a{color:#2dd4bf;display:inline-block;padding:10px 6px}@media (prefers-color-scheme:light){body{background:#faf7f2;color:#1a1d1f}p{color:#4a5158}a{color:#0f766e}}</style></head>
<body><main><h1>${t.h1}</h1><p>${t.body}</p><p>${links}</p></main></body></html>`;
}

self.addEventListener("install", (event) => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys();
      await Promise.all(names.filter((n) => n !== PRECACHE && n !== RUNTIME).map((n) => caches.delete(n)));
      // Delete the files of old builds.
      const current = new Set([...KEYS.values()].map((k) => new URL(k, self.location.origin).href));
      const cache = await caches.open(PRECACHE);
      const keys = await cache.keys();
      await Promise.all(keys.filter((r) => !current.has(r.url)).map((r) => cache.delete(r)));
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith(SCOPE)) return;

  const key = precacheKey(url.pathname, request.mode === "navigate");
  event.respondWith(key ? cacheFirst(request, key) : networkFirst(request));
});

/** Downloads the files that are not in the cache yet. A failed install keeps what it saved. */
async function precache() {
  const cache = await caches.open(PRECACHE);
  const missing = [];
  for (const [url, key] of KEYS) if (!(await cache.match(key))) missing.push([url, key]);

  let next = 0;
  async function download() {
    while (next < missing.length) {
      const [url, key] = missing[next++];
      const response = await fetch(url, { cache: "reload" });
      if (!response.ok) throw new Error(`precache ${url}: ${response.status}`);
      await cache.put(key, clean(response));
    }
  }
  await Promise.all(Array.from({ length: DOWNLOADS }, download));
}

/** The cache key of a saved file. "topics/x" and "topics/x/index.html" also find "topics/x/". */
function precacheKey(pathname, navigate) {
  return (
    KEYS.get(pathname) ??
    KEYS.get(pathname.replace(/index\.html$/, "")) ??
    (navigate ? KEYS.get(pathname + "/") : undefined)
  );
}

async function cacheFirst(request, key) {
  const cached = await caches.match(key);
  if (cached) return cached;
  // Not saved yet (the install is still running): use the network.
  return networkFirst(request);
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME);
      await cache.put(request, response.clone());
      trim(cache);
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request, { ignoreSearch: true });
    if (cached) return cached;
    if (request.mode === "navigate") {
      return new Response(offlineHtml(request.url), { headers: { "Content-Type": "text/html; charset=utf-8" } });
    }
    // The router then loads the full page, which the cache has.
    throw error;
  }
}

/** A browser does not use a redirected response for a navigation. Copy it into a plain one. */
function clean(response) {
  if (!response.redirected) return response;
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers: response.headers });
}

/** Old builds leave old runtime files. Delete the oldest first. */
async function trim(cache) {
  const keys = await cache.keys();
  await Promise.all(keys.slice(0, Math.max(0, keys.length - MAX_RUNTIME)).map((k) => cache.delete(k)));
}
