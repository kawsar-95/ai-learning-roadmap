// Takes the README screenshots from the production build and writes them to screenshots/.
//
//   npm run build                                       # without PAGES_BASE_PATH, so paths start at /
//   node scripts/screenshots/take-screenshots.mjs        # every shot
//   node scripts/screenshots/take-screenshots.mjs quiz   # only the named shots
//
// Needs playwright-core inside $SHOTS_WORK (default <temp dir>/readme-screenshots; it is not a dependency of
// the site): `npm init -y && npm i playwright-core` there, or npm may install into a parent directory. Also
// Chrome or Chromium (CHROME=/path/to/chrome, default /usr/bin/google-chrome). See README.md next to this file.
// It serves out/ from inside the script, so nothing is left running. The "videos" and "live-view" shots
// load YouTube thumbnails and a third-party page, so they need a network connection.
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const work = process.env.SHOTS_WORK || path.join(os.tmpdir(), "readme-screenshots");
const { chromium } = createRequire(path.join(work, "noop.js"))("playwright-core");

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const OUT = path.join(ROOT, "out");
const DEST = path.join(ROOT, "screenshots");
const PORT = Number(process.env.SHOTS_PORT ?? 8017);
const BASE = `http://127.0.0.1:${PORT}`;
const ONLY = new Set(process.argv.slice(2));

if (!fs.existsSync(path.join(OUT, "index.html"))) {
  console.error("out/ has no build. Run `npm run build` first.");
  process.exit(1);
}
fs.mkdirSync(DEST, { recursive: true });

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json",
};

/** Serves the static export the way GitHub Pages does: a folder URL gets its index.html, a miss gets 404.html. */
function serve(dir, port) {
  const server = http.createServer((req, res) => {
    let file = path.join(dir, decodeURIComponent(new URL(req.url, BASE).pathname));
    try {
      if (fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
      fs.accessSync(file);
      res.writeHead(200, { "content-type": MIME[path.extname(file)] ?? "application/octet-stream" });
      fs.createReadStream(file).pipe(res);
    } catch {
      res.writeHead(404, { "content-type": MIME[".html"] });
      fs.createReadStream(path.join(dir, "404.html")).pipe(res);
    }
  });
  return new Promise((resolve) => server.listen(port, "127.0.0.1", () => resolve(server)));
}

const topic = (slug) => JSON.parse(fs.readFileSync(path.join(ROOT, "src/content", `${slug}.json`), "utf8"));
const part1 = topic("llm-fundamentals");
const part2 = topic("prompt-engineering");
const part5 = topic("rag-knowledge-systems");
const part6 = topic("agents-and-agentic-systems");
const FIRST = part1.sections[0].id;
const key = (slug, section) => `${slug}/${section.id}`;

// Demo state for the progress pages, in the site's own localStorage keys.
const DEMO = {
  progress: JSON.stringify(
    [...part1.sections.map((s) => key("llm-fundamentals", s)), ...part2.sections.slice(0, 3).map((s) => key("prompt-engineering", s))].sort(),
  ),
  bookmarks: JSON.stringify(
    [key("prompt-engineering", part2.sections[4]), key("rag-knowledge-systems", part5.sections[2]), key("agents-and-agentic-systems", part6.sections[1])].sort(),
  ),
  "quiz-scores": JSON.stringify({ "llm-fundamentals": { best: 5, total: 5 }, "prompt-engineering": { best: 4, total: 5 } }),
  "roadmap-progress": JSON.stringify(["0/1", "0/2", "0/3", "0/4", "0/5", "0/6", "1/1", "1/2", "1/3"]),
};

const DESKTOP = { w: 1440, h: 900, dpr: 1 };
const PHONE = { w: 390, h: 844, dpr: 2, touch: true, theme: "dark" };

const browser = await chromium.launch({ executablePath: process.env.CHROME || "/usr/bin/google-chrome", args: ["--no-sandbox"] });

/**
 * Opens `url` in a fresh context and returns a PNG buffer. `theme` and `seed` go into localStorage before the
 * first paint (the site reads them in a head script). `act(page)` may return a clip in page coordinates.
 */
async function capture(url, { theme = "light", w, h, dpr, touch = false, seed = {}, act } = {}) {
  const ctx = await browser.newContext({
    viewport: { width: w, height: h },
    deviceScaleFactor: dpr,
    colorScheme: theme,
    hasTouch: touch,
    isMobile: touch,
    serviceWorkers: "block",
  });
  await ctx.addInitScript(
    ({ origin, prefs }) => {
      try {
        // Runs in every frame. Seed once per tab, so a reload keeps what the page saved.
        if (location.origin !== origin || sessionStorage.getItem("__seeded")) return;
        for (const [k, v] of Object.entries(prefs)) localStorage.setItem(k, v);
        sessionStorage.setItem("__seeded", "1");
      } catch {
        // A data: frame inside an embedded app has no storage.
      }
    },
    { origin: BASE, prefs: { theme, ...seed } },
  );
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(BASE + url, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  const clip = act ? await act(page) : null;
  // A selector that matched a hidden element gives a clip of padding only: fail loudly instead.
  if (clip && (clip.width < 100 || clip.height < 100)) throw new Error(`${url}: clip ${JSON.stringify(clip)} is too small`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  // With fullPage the clip is in page coordinates; without it Playwright clips the viewport image.
  const png = clip ? await page.screenshot({ clip, fullPage: true }) : await page.screenshot();
  if (errors.length) console.warn(`  ${url}: ${errors.join(" | ")}`);
  await ctx.close();
  return png;
}

/** Stops the sticky header from being painted over a crop further down the page. */
const unstickHeader = (page) => page.addStyleTag({ content: "header.sticky{position:relative!important}" });

/** The box of an element in page coordinates. */
const box = (locator) =>
  locator.evaluate((el) => {
    const r = el.getBoundingClientRect();
    return { x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height, bottom: r.bottom + scrollY };
  });

/** A clip from `top` to `bottom` (page y), as wide as `around` plus `pad` on each side. */
function clipBetween(around, top, bottom, pad = 24) {
  return { x: Math.max(0, around.x - pad), y: Math.max(0, top), width: around.width + pad * 2, height: bottom - top };
}

/** Lays out `html` in a blank page and screenshots `#frame`: the composites are plain HTML and CSS. */
async function compose(html, width) {
  const page = await browser.newPage({ viewport: { width, height: 800 }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><body style="margin:0">${html}</body>`, { waitUntil: "load" });
  const png = await page.locator("#frame").screenshot();
  await page.close();
  return png;
}

const dataUrl = (png) => `data:image/png;base64,${png.toString("base64")}`;

/** The shots, in README order. Each returns a PNG buffer. */
const SHOTS = {
  // The home page hero.
  home: () =>
    capture("/", {
      ...DESKTOP,
      act: async (page) => {
        const hero = await box(page.locator("main section").first());
        return { x: 0, y: 0, width: DESKTOP.w, height: hero.bottom };
      },
    }),

  // A topic page: the Parts, the section pager and voice switcher, "On this page".
  "topic-page": () => capture("/topics/llm-fundamentals/", DESKTOP),

  // One section in the three voices, side by side. The saved voice is localStorage "voice".
  voices: async () => {
    const panels = [];
    for (const voice of ["main", "layman", "bangla"]) {
      panels.push(
        await capture("/topics/llm-fundamentals/", {
          ...DESKTOP,
          seed: { voice },
          act: async (page) => {
            await unstickHeader(page);
            const section = page.locator(`section#${FIRST}`);
            await section.scrollIntoViewIfNeeded();
            const b = await box(section);
            return clipBetween(b, b.y - 8, b.y + 616);
          },
        }),
      );
    }
    const imgs = panels
      .map((p) => `<img src="${dataUrl(p)}" style="display:block;-webkit-mask-image:linear-gradient(#000 calc(100% - 90px),transparent)">`)
      .join("");
    return compose(`<div id="frame" style="display:inline-flex;gap:28px;background:#faf7f2">${imgs}</div>`, 2400);
  },

  // The practice panel of section 1, open, down to the end of its first step.
  practice: () =>
    capture("/topics/llm-fundamentals/", {
      ...DESKTOP,
      act: async (page) => {
        await unstickHeader(page);
        const details = page.locator(`details:has(#${FIRST}-practice)`);
        await details.locator("summary").first().click();
        await page.waitForTimeout(300);
        const all = await box(details);
        const head = await box(details.locator("summary").first());
        const step = await box(details.locator("article ol > li").first());
        // The step's box ends where step 2 starts; its bottom padding is the margin.
        return clipBetween(all, head.y - 20, step.bottom - 2);
      },
    }),

  // The "Watch" list of section 1, open: the video cards with their thumbnails, then the Shorts row.
  videos: () =>
    capture("/topics/llm-fundamentals/", {
      ...DESKTOP,
      act: async (page) => {
        await unstickHeader(page);
        const details = page.locator(`details:has(#${FIRST}-videos)`);
        await details.locator("summary").first().click();
        const grid = details.locator("ul").first();
        await grid.scrollIntoViewIfNeeded();
        await page
          .waitForFunction((sel) => [...document.querySelectorAll(sel)].every((img) => img.complete && img.naturalWidth > 0), `details:has(#${FIRST}-videos) ul img`, {
            timeout: 20000,
          })
          .catch(() => console.warn("  videos: some thumbnails did not load"));
        const all = await box(details);
        const head = await box(details.locator("summary").first());
        // The last list is the Shorts grid when the section has Shorts, else the video grid.
        const last = await box(details.locator("ul").last());
        return clipBetween(all, head.y - 20, last.bottom + 20);
      },
    }),

  // The quiz, answered with question 4 wrong, then checked: questions 4 and 5 and the score.
  quiz: () =>
    capture("/topics/llm-fundamentals/#quiz", {
      ...DESKTOP,
      act: async (page) => {
        await unstickHeader(page);
        const quiz = page.locator("section#quiz");
        await quiz.waitFor({ state: "visible" });
        const WRONG = 3;
        for (const [i, q] of part1.quiz.entries()) {
          const wrong = i === WRONG;
          const index = q.kind === "mcq" ? (wrong ? (q.answer + 1) % q.en.options.length : q.answer) : (wrong ? !q.answer : q.answer) ? 0 : 1;
          await quiz.locator("[role=radiogroup]").nth(i).locator("input[type=radio]").nth(index).check();
        }
        await quiz.getByRole("button", { name: "Check answers" }).click();
        await page.waitForTimeout(400);
        const all = await box(quiz);
        const from = await box(quiz.locator("[role=radiogroup]").nth(WRONG));
        return clipBetween(all, from.y - 16, all.bottom + 24);
      },
    }),

  // The search palette (Ctrl+K) with results.
  search: () =>
    capture("/topics/llm-fundamentals/", {
      ...DESKTOP,
      act: async (page) => {
        await page.keyboard.press("Control+k");
        const input = page.locator("[role=dialog] input").first();
        await input.waitFor();
        await input.pressSequentially("kv cache", { delay: 40 });
        await page.waitForTimeout(800);
        return null;
      },
    }),

  // The roadmap: title and learning paths.
  roadmap: () => capture("/roadmap/", { ...DESKTOP, seed: DEMO }),

  // The roadmap progress card, the filter, and Phase 0 with its lessons open.
  "roadmap-progress": () =>
    capture("/roadmap/", {
      ...DESKTOP,
      seed: DEMO,
      act: async (page) => {
        await unstickHeader(page);
        await page.locator("#phase-0 details summary").click();
        await page.waitForTimeout(300);
        const card = await page.locator("[role=progressbar]").first().evaluate((el) => {
          const r = el.closest(".rounded-2xl").getBoundingClientRect();
          return { x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height };
        });
        const row = await box(page.locator("#phase-0 details ol > li").nth(5));
        return clipBetween(card, card.y - 24, row.bottom + 4);
      },
    }),

  // A curriculum lesson rendered on the site (KaTeX, "On this page").
  lesson: () => capture("/roadmap/07-transformers-deep-dive/02-self-attention-from-scratch/", { ...DESKTOP, seed: DEMO }),

  // Progress pages with the demo state.
  contents: () => capture("/contents/", { ...DESKTOP, seed: DEMO }),
  dashboard: () => capture("/dashboard/", { ...DESKTOP, seed: DEMO }),

  // Interview questions, the first one open.
  interview: () =>
    capture("/interview/", {
      ...DESKTOP,
      act: async (page) => {
        await page.locator("details summary").first().click();
        await page.waitForTimeout(300);
        return null;
      },
    }),

  resources: () => capture("/resources/", DESKTOP),

  // The Bangla site: বাংলা voice first, Bangla interface.
  "bangla-topic": () => capture("/bn/topics/llm-fundamentals/", DESKTOP),

  // One page in both themes, split on a diagonal.
  themes: async () => {
    const light = await capture("/topics/llm-fundamentals/", DESKTOP);
    const dark = await capture("/topics/llm-fundamentals/", { ...DESKTOP, theme: "dark" });
    const { w, h } = DESKTOP;
    const [top, bottom] = [Math.round(w * 0.6), Math.round(w * 0.44)];
    return compose(
      `<div id="frame" style="position:relative;width:${w}px;height:${h}px">
        <img src="${dataUrl(light)}" style="position:absolute;inset:0">
        <img src="${dataUrl(dark)}" style="position:absolute;inset:0;clip-path:polygon(${top}px 0,100% 0,100% 100%,${bottom}px 100%)">
        <svg width="${w}" height="${h}" style="position:absolute;inset:0"><line x1="${top}" y1="0" x2="${bottom}" y2="${h}" stroke="#2dd4bf" stroke-width="3"/></svg>
      </div>`,
      w,
    );
  },

  // Phone, dark: a topic page, and the menu drawer.
  "mobile-topic": () => capture("/topics/llm-fundamentals/", PHONE),
  "mobile-menu": () =>
    capture("/topics/llm-fundamentals/", {
      ...PHONE,
      act: async (page) => {
        await page.getByRole("button", { name: "Open the list of parts" }).click();
        await page.waitForTimeout(500);
        return null;
      },
    }),

  // A live view (Part 15): the first embedded page, loaded and with its intro card closed.
  "live-view": () =>
    capture("/topics/visual-learning-resources/", {
      ...DESKTOP,
      h: 1100,
      act: async (page) => {
        await unstickHeader(page);
        const first = page.locator("figure", { has: page.locator("button[aria-label^='Load live view']") }).first();
        // Pin the figure: once loaded it has no button, and the filter above would match the next one.
        await first.evaluate((el) => el.setAttribute("data-shot", ""));
        const figure = page.locator("figure[data-shot]");
        await figure.scrollIntoViewIfNeeded();
        await figure.locator("button[aria-label^='Load live view']").click();
        await page.waitForTimeout(9000);
        const frame = figure.frameLocator("iframe");
        // The embedded app opens with its own intro card. Its close button is a bare "×".
        await frame
          .getByRole("button", { name: /close|×|✕/i })
          .first()
          .click({ timeout: 3000 })
          .catch(() => frame.locator("button:has-text('×'), button:has-text('✕')").first().click({ timeout: 3000 }))
          .catch(() => console.warn("  live-view: no intro card to close"));
        await page.waitForTimeout(1200);
        const b = await box(figure);
        return clipBetween(b, b.y - 16, b.bottom + 16, 16);
      },
    }),
};

const unknown = [...ONLY].filter((name) => !(name in SHOTS));
if (unknown.length) {
  console.error(`Unknown shot: ${unknown.join(", ")}. Known: ${Object.keys(SHOTS).join(", ")}`);
  process.exit(1);
}

const server = await serve(OUT, PORT);
try {
  for (const [name, take] of Object.entries(SHOTS)) {
    if (ONLY.size && !ONLY.has(name)) continue;
    const file = path.join(DEST, `${name}.png`);
    fs.writeFileSync(file, await take());
    console.log(`screenshots/${name}.png  ${Math.round(fs.statSync(file).size / 1024)} KB`);
  }
} finally {
  server.close();
  await browser.close();
}
