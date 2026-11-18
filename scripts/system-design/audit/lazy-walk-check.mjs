// Real-browser check of the lazily loaded walk-throughs, against a build served the way GitHub Pages serves it.
// Usage: node scripts/system-design/audit/lazy-walk-check.mjs <base-url>   (see ../README.md)
//   A  only the visible section's file is fetched, and a section is fetched once
//   B  switching to the বাংলা voice on the English site shows Bangla step text without a second fetch
//   C  a failed fetch shows the error with Try again, and Try again loads the walk-through
//   D  after the service worker has saved the site, the walk-through opens with the network off
//   E  the Bangla site fetches the same single file and shows Bangla text
import { launch } from "./browser.mjs";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const [base] = process.argv.slice(2);
const jsonPath = fileURLToPath(new URL("../../../src/content/system-design.json", import.meta.url));
const topic = JSON.parse(readFileSync(jsonPath, "utf8"));
const steps = (id) => topic.sections.find((s) => s.id === id).walkthrough.steps.length;
const results = [];
const check = (pass, text) => results.push(`${pass ? "ok:  " : "FAIL:"} ${text}`);
const BANGLA = /[\u0980-\u09FF]/;
const page0 = `${base}/topics/system-design/`;
const bnPage = `${base}/bn/topics/system-design/`;
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
  await page.goto(`${page0}#s5`, { waitUntil: "load" });
  await player(page, "s5").waitFor({ state: "visible", timeout: 15000 });
  await page.waitForTimeout(600);
  check(files.length === 1 && files[0] === "s5.json", `A1 opening #s5 fetches only s5.json (fetched: ${files.join(", ") || "nothing"})`);
  check((await player(page, "s5").locator("ol button").count()) === steps("s5"), `A2 s5 shows its ${steps("s5")} steps`);
  await page.evaluate(() => (location.hash = "#s6"));
  await player(page, "s6").waitFor({ state: "visible", timeout: 15000 });
  check(files.join() === "s5.json,s6.json", `A3 showing s6 fetches s6.json next (fetched: ${files.join(", ")})`);
  await page.evaluate(() => (location.hash = "#s5"));
  await page.waitForTimeout(700);
  check(files.length === 2, `A4 coming back to s5 fetches nothing new (fetched: ${files.length} files)`);
  check(errors.length === 0, `A5 no page errors (${errors.join("; ") || "none"})`);
  await ctx.close();
}

// B
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  const files = watch(page);
  await page.goto(`${page0}#s7`, { waitUntil: "load" });
  await player(page, "s7").waitFor({ state: "visible", timeout: 15000 });
  const before = await player(page, "s7").locator("ol button").first().innerText();
  await page.locator('section#s7 [role="group"] button', { hasText: "বাংলা" }).first().click();
  await page.waitForTimeout(800);
  const after = await player(page, "s7").locator("ol button").first().innerText();
  check(!BANGLA.test(before) && BANGLA.test(after), `B1 the strip changes from English to Bangla (${JSON.stringify(before)} -> ${JSON.stringify(after)})`);
  check(files.length === 1, `B2 no second fetch for the other language (fetched: ${files.join(", ")})`);
  await ctx.close();
}

// C
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  let blocked = true;
  await page.route("**/walkthroughs/system-design/s3.json", (route) => (blocked ? route.abort() : route.continue()));
  await page.goto(`${page0}#s3`, { waitUntil: "load" });
  await page.getByText("The walk-through did not load.").waitFor({ timeout: 15000 });
  const retry = page.getByRole("button", { name: "Try again" });
  check((await retry.count()) === 1, "C1 a failed fetch shows the message and a Try again button");
  blocked = false;
  await retry.click();
  await player(page, "s3").waitFor({ state: "visible", timeout: 15000 });
  check((await player(page, "s3").locator("ol button").count()) === steps("s3"), "C2 Try again loads the walk-through");
  await ctx.close();
}

// E
{
  const ctx = await newCtx({ serviceWorkers: "block" });
  const page = await ctx.newPage();
  const files = watch(page);
  await page.goto(`${bnPage}#s2`, { waitUntil: "load" });
  await player(page, "s2").waitFor({ state: "visible", timeout: 15000 });
  const strip = await player(page, "s2").locator("ol button").first().innerText();
  check(files.join() === "s2.json" && BANGLA.test(strip), `E1 the Bangla site fetches one file and shows Bangla (${files.join(", ")}; ${JSON.stringify(strip)})`);
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
  let n = { all: 0, walks: 0 };
  for (let i = 0; i < 150; i++) {
    n = await cacheCount().catch(() => n);
    if (n.walks >= 40) break;
    await page.waitForTimeout(1000);
  }
  check(n.walks === 40, `D1 the service worker saved all 40 walk-through files (${n.walks}) among ${n.all} files`);
  await page.waitForTimeout(1500);
  await ctx.setOffline(true);
  const failed = [];
  page.on("requestfailed", (r) => failed.push(r.url().split("/").slice(-2).join("/")));
  await page.goto(`${page0}#s9`, { waitUntil: "load" });
  await player(page, "s9").waitFor({ state: "visible", timeout: 15000 });
  check((await player(page, "s9").locator("ol button").count()) === steps("s9"), `D2 offline, s9 opens with its ${steps("s9")} steps (failed requests: ${failed.length})`);
  await ctx.close();
}

await browser.close();
console.log(results.join("\n"));
process.exit(results.some((r) => r.startsWith("FAIL")) ? 1 : 0);
