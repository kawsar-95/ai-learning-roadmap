// Checks every walk-through of the System Design part in a real browser, in both
// languages and on every step: no text sticks out of its box, no box leaves the
// diagram, no line label sits on a box or on another label, no readout is cut.
// Reduced motion is on, so every box is at its final place when it is measured.
// Usage: node scripts/system-design/audit/check-walk-dom.mjs <base-url> [sectionId ...]   (see ../README.md)
import { launch } from "./browser.mjs";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const [base, ...only] = process.argv.slice(2);
const jsonPath = fileURLToPath(new URL("../../../src/content/system-design.json", import.meta.url));
const topic = JSON.parse(readFileSync(jsonPath, "utf8"));
const walks = topic.sections
  .filter((s) => s.walkthrough && (!only.length || only.includes(s.id)))
  .map((s) => ({ id: s.id, steps: s.walkthrough.steps.length }));

const browser = await launch();
const problems = [];
let checked = 0;

/** Runs in the page: returns a list of defects of the player that is showing one step. */
function measure(root) {
  const svg = root.querySelector("svg[role=img]");
  const sr = svg.getBoundingClientRect();
  const out = [];
  const overlap = (a, b, pad = 0) => a.left < b.right + pad && a.right > b.left - pad && a.top < b.bottom + pad && a.bottom > b.top - pad;
  const boxes = [...svg.querySelectorAll("[data-node]")]
    .filter((g) => Number(getComputedStyle(g).opacity) > 0.05)
    .map((g) => ({ id: g.dataset.node, g, r: g.querySelector("rect").getBoundingClientRect() }));
  for (const b of boxes) {
    for (const t of b.g.querySelectorAll(":scope > text")) {
      const tr = t.getBoundingClientRect();
      const over = tr.right - (b.r.right - 5);
      if (over > 0.5) out.push(`text "${t.textContent}" sticks out of ${b.id} by ${over.toFixed(1)}px`);
      if (tr.bottom > b.r.bottom + 1 || tr.top < b.r.top - 1) out.push(`text "${t.textContent}" leaves ${b.id} vertically`);
    }
    if (b.r.left < sr.left - 0.5 || b.r.right > sr.right + 0.5 || b.r.top < sr.top - 0.5 || b.r.bottom > sr.bottom + 0.5) {
      out.push(`${b.id} leaves the diagram`);
    }
  }
  const labels = [...svg.querySelectorAll("[data-link] > text")].map((t) => ({ text: t.textContent, r: t.getBoundingClientRect() }));
  labels.forEach((l, i) => {
    for (const b of boxes) if (overlap(l.r, b.r, 1)) out.push(`label "${l.text}" sits on ${b.id}`);
    if (l.r.left < sr.left || l.r.right > sr.right || l.r.top < sr.top) out.push(`label "${l.text}" leaves the diagram`);
    for (const m of labels.slice(i + 1)) if (overlap(l.r, m.r, 0)) out.push(`labels "${l.text}" and "${m.text}" overlap`);
  });
  for (const dt of root.querySelectorAll("dt")) if (dt.scrollWidth > dt.clientWidth + 1) out.push(`readout label "${dt.textContent}" is cut`);
  for (const dd of root.querySelectorAll("dd")) if (dd.scrollWidth > dd.clientWidth + 1) out.push(`readout value "${dd.textContent}" is cut`);
  return out;
}

for (const [prefix, lang] of [["", "en"], ["/bn", "bn"]]) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 1100 }, reducedMotion: "reduce" });
  const p = await ctx.newPage();
  p.on("pageerror", (e) => problems.push(`[${lang}] pageerror: ${e.message}`));
  p.on("console", (m) => m.type() === "error" && problems.push(`[${lang}] console: ${m.text()}`));
  const page = `${base}${prefix}/topics/system-design/`;
  await p.goto(page, { waitUntil: "networkidle" });
  if (lang === "en" && walks.length) {
    // Negative control: a label that is too long for its box must be reported, or this check proves nothing.
    await p.goto(`${page}#${walks[0].id}`, { waitUntil: "load" });
    const probe = p.locator(`[aria-labelledby="${walks[0].id}-walk"]`);
    await probe.waitFor({ state: "visible", timeout: 8000 });
    const flagged = await probe.evaluate((root, fn) => {
      const text = root.querySelector("[data-node] > text");
      const before = text.textContent;
      text.textContent = "a label that is far too long for its box ".repeat(2);
      const found = new Function(`return (${fn})`)()(root);
      text.textContent = before;
      return found;
    }, measure.toString());
    if (!flagged.some((f) => f.includes("sticks out"))) problems.push("SELF-TEST FAILED: an over-long label was not reported");
    else console.log("self-test ok: an over-long label is reported");
  }
  for (const w of walks) {
    await p.goto(`${page}#${w.id}`, { waitUntil: "load" });
    const player = p.locator(`[aria-labelledby="${w.id}-walk"]`);
    try {
      await player.waitFor({ state: "visible", timeout: 8000 });
    } catch {
      problems.push(`[${lang}] ${w.id}: the player is not visible`);
      continue;
    }
    const strip = player.locator("ol button");
    if ((await strip.count()) !== w.steps) problems.push(`[${lang}] ${w.id}: ${await strip.count()} strip buttons, ${w.steps} steps`);
    for (let i = 0; i < w.steps; i++) {
      await strip.nth(i).click();
      await p.waitForTimeout(50);
      for (const f of await player.evaluate(measure)) problems.push(`[${lang}] ${w.id} step ${i + 1}: ${f}`);
      checked++;
    }
  }
  await ctx.close();
}
await browser.close();
console.log(`checked ${checked} steps (${walks.length} walk-throughs x 2 languages)`);
console.log(problems.length ? `${problems.length} PROBLEMS:\n${problems.join("\n")}` : "no problems");
process.exit(problems.length ? 1 : 0);
