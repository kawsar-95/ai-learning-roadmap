// Real-browser check of the lazily loaded walk-throughs of one Part (PART=<slug>, default system-design), against a build
// served the way GitHub Pages serves it.
// Usage: [PART=<slug>] node scripts/system-design/audit/lazy-walk-check.mjs <base-url>   (see ../README.md)
//   A  only the visible section's file is fetched, and a section is fetched once
//   B  switching to the বাংলা voice on the English site shows Bangla step text without a second fetch
//   C  a failed fetch shows the error with Try again, and Try again loads the walk-through
//   D  after the service worker has saved the site, it has saved the walk-through files of every Part, and one opens with the network off
//   E  the Bangla site fetches the same single file and shows Bangla text
// The checks use the Part's 5th and 6th (A), 7th (B), 3rd (C), 2nd (E) and 9th (D) walk-through. A Part with fewer
// walk-throughs goes round to the start again; A3 and A4 need two different ones.
import { launch } from "./browser.mjs";
import { partWalks, siteWalkCount, slug } from "./part.mjs";

const [base] = process.argv.slice(2);
const walks = partWalks();
if (!walks.length) throw new Error(`PART=${slug} has no walk-through to check`);
const pick = (n) => walks[(n - 1) % walks.length].id;
const [secA, secA2, secB, secC, secE, secD] = [5, 6, 7, 3, 2, 9].map(pick);
const steps = (id) => walks.find((w) => w.id === id).walkthrough.steps.length;
const results = [];
const check = (pass, text) => results.push(`${pass ? "ok:  " : "FAIL:"} ${text}`);
const BANGLA = /[\u0980-\u09FF]/;
const page0 = `${base}/topics/${slug}/`;
const bnPage = `${base}/bn/topics/${slug}/`;
const browser = await launch();
const newCtx = (extra = {}) => browser.newContext({ viewport: { width: 1280, height: 1100 }, reducedMotion: "reduce", ...extra });
const watch = (page) => {
  const files = [];
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname.includes("/walkthroughs/")) files.push(u.pathname.split("/").pop());
  });
  return files;
};
const player = (page, id) => page.locator(`[aria-labelledby="${id}-walk"]`);

// A
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  const files = watch(page);
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`${page0}#${secA}`, { waitUntil: "load" });
  await player(page, secA).waitFor({ state: "visible", timeout: 15000 });
  await page.waitForTimeout(600);
  check(files.length === 1 && files[0] === `${secA}.json`, `A1 opening #${secA} fetches only ${secA}.json (fetched: ${files.join(", ") || "nothing"})`);
  check((await player(page, secA).locator("ol button").count()) === steps(secA), `A2 ${secA} shows its ${steps(secA)} steps`);
  if (secA2 === secA) {
    results.push(`skip: A3 and A4 need a second walk-through (PART=${slug} has one)`);
  } else {
    await page.evaluate((id) => (location.hash = `#${id}`), secA2);
    await player(page, secA2).waitFor({ state: "visible", timeout: 15000 });
    check(files.join() === `${secA}.json,${secA2}.json`, `A3 showing ${secA2} fetches ${secA2}.json next (fetched: ${files.join(", ")})`);
    await page.evaluate((id) => (location.hash = `#${id}`), secA);
    await page.waitForTimeout(700);
    check(files.length === 2, `A4 coming back to ${secA} fetches nothing new (fetched: ${files.length} files)`);
  }
  check(errors.length === 0, `A5 no page errors (${errors.join("; ") || "none"})`);
  await ctx.close();
}

// B
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  const files = watch(page);
  await page.goto(`${page0}#${secB}`, { waitUntil: "load" });
  await player(page, secB).waitFor({ state: "visible", timeout: 15000 });
  const before = await player(page, secB).locator("ol button").first().innerText();
  await page.locator(`section#${secB} [role="group"] button`, { hasText: "বাংলা" }).first().click();
  await page.waitForTimeout(800);
  const after = await player(page, secB).locator("ol button").first().innerText();
  check(!BANGLA.test(before) && BANGLA.test(after), `B1 the strip changes from English to Bangla (${JSON.stringify(before)} -> ${JSON.stringify(after)})`);
  check(files.length === 1, `B2 no second fetch for the other language (fetched: ${files.join(", ")})`);
  await ctx.close();
}

// C
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  let blocked = true;
  await page.route(`**/walkthroughs/${slug}/${secC}.json`, (route) => (blocked ? route.abort() : route.continue()));
  await page.goto(`${page0}#${secC}`, { waitUntil: "load" });
  await page.getByText("The walk-through did not load.").waitFor({ timeout: 15000 });
  const retry = page.getByRole("button", { name: "Try again" });
  check((await retry.count()) === 1, "C1 a failed fetch shows the message and a Try again button");
  blocked = false;
  await retry.click();
  await player(page, secC).waitFor({ state: "visible", timeout: 15000 });
  check((await player(page, secC).locator("ol button").count()) === steps(secC), "C2 Try again loads the walk-through");
  await ctx.close();
}

// E
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  const files = watch(page);
  await page.goto(`${bnPage}#${secE}`, { waitUntil: "load" });
  await player(page, secE).waitFor({ state: "visible", timeout: 15000 });
  const strip = await player(page, secE).locator("ol button").first().innerText();
  check(files.join() === `${secE}.json` && BANGLA.test(strip), `E1 the Bangla site fetches one file and shows Bangla (${files.join(", ")}; ${JSON.stringify(strip)})`);
  await ctx.close();
}

// D
{
  const ctx = await newCtx({ serviceWorkers: "allow" });
  const page = await ctx.newPage();
  await page.goto(page0, { waitUntil: "load" });
  const cacheCount = () =>
    page.evaluate(async () => {
      const cache = await caches.open("precache-v1");
      const keys = await cache.keys();
      return { all: keys.length, walks: keys.filter((k) => k.url.includes("/walkthroughs/")).length };
    });
  const total = siteWalkCount();
  let n = { all: 0, walks: 0 };
  for (let i = 0; i < 150; i++) {
    n = await cacheCount().catch(() => n);
    if (n.walks >= total) break;
    await page.waitForTimeout(1000);
  }
  check(n.walks === total, `D1 the service worker saved all ${total} walk-through files (${n.walks}) among ${n.all} files`);
  await page.waitForTimeout(1500);
  await ctx.setOffline(true);
  const failed = [];
  page.on("requestfailed", (r) => failed.push(r.url().split("/").slice(-2).join("/")));
  await page.goto(`${page0}#${secD}`, { waitUntil: "load" });
  await player(page, secD).waitFor({ state: "visible", timeout: 15000 });
  check((await player(page, secD).locator("ol button").count()) === steps(secD), `D2 offline, ${secD} opens with its ${steps(secD)} steps (failed requests: ${failed.length})`);
  await ctx.close();
}

await browser.close();
console.log(results.join("\n"));
process.exit(results.some((r) => r.startsWith("FAIL")) ? 1 : 0);
