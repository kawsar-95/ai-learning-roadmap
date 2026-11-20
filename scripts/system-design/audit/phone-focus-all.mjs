// Phone check of the walk-throughs of one Part (PART=<slug>, default system-design), every step, both languages: the diagram frame
// scrolls sideways, and on each step the middle of the boxes the step is about (hot or warn) must
// be at the middle of the visible frame, or at least inside it where the scroll is stopped at an end.
// A negative control shifts the frame by hand and expects the check to notice.
// Usage: [PART=<slug>] node scripts/system-design/audit/phone-focus-all.mjs <base-url> [sectionId ...]   (see ../README.md)
import { launch } from "./browser.mjs";
import { partWalks, slug } from "./part.mjs";

const [base, ...only] = process.argv.slice(2);
const walks = partWalks().filter((s) => !only.length || only.includes(s.id));

/** Runs in the page: where the hot boxes are, and where the frame is scrolled. */
function probe(root, ids) {
  const frame = root.querySelector("div.overflow-x-auto");
  const fr = frame.getBoundingClientRect();
  const centres = ids
    .map((id) => root.querySelector(`[data-node="${id}"] rect`)?.getBoundingClientRect())
    .filter(Boolean)
    .map((r) => r.left + r.width / 2);
  return { sl: frame.scrollLeft, max: frame.scrollWidth - frame.clientWidth, left: fr.left, width: fr.width, centres };
}

/** The verdict for one measurement: null when fine, otherwise a sentence. */
function verdict(m) {
  if (m.max <= 1 || !m.centres.length) return null; // nothing scrolls, or the step marks no box
  const mid = (Math.min(...m.centres) + Math.max(...m.centres)) / 2;
  const centre = m.left + m.width / 2;
  const stopped = m.sl <= 1 || m.sl >= m.max - 1;
  if (stopped) return mid >= m.left - 1 && mid <= m.left + m.width + 1 ? null : `focus ${Math.round(mid)}px is outside the frame ${Math.round(m.left)}..${Math.round(m.left + m.width)} (scroll ${Math.round(m.sl)}/${Math.round(m.max)})`;
  return Math.abs(mid - centre) <= 4 ? null : `focus is ${Math.round(mid - centre)}px off the middle (scroll ${Math.round(m.sl)}/${Math.round(m.max)})`;
}

const browser = await launch();
const problems = [];
let checked = 0;
let measured = 0;
for (const [prefix, lang] of [["", "en"], ["/bn", "bn"]]) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const p = await ctx.newPage();
  p.on("pageerror", (e) => problems.push(`[${lang}] pageerror: ${e.message}`));
  const page = `${base}${prefix}/topics/${slug}/`;
  await p.goto(page, { waitUntil: "networkidle" });
  let controlDone = lang !== "en";
  let controlTried = false;
  for (const s of walks) {
    await p.goto(`${page}#${s.id}`, { waitUntil: "load" });
    const player = p.locator(`[aria-labelledby="${s.id}-walk"]`);
    try {
      await player.waitFor({ state: "visible", timeout: 8000 });
    } catch {
      problems.push(`[${lang}] ${s.id}: the player is not visible`);
      continue;
    }
    const strip = player.locator("ol button");
    const steps = s.walkthrough.steps;
    for (let i = 0; i < steps.length; i++) {
      const ids = steps[i].show.filter((x) => x.state === "hot" || x.state === "warn").map((x) => x.id);
      await strip.nth(i).click();
      await p.waitForTimeout(60);
      const m = await player.evaluate(probe, ids);
      checked++;
      if (m.max > 1 && m.centres.length) measured++;
      const v = verdict(m);
      if (v) problems.push(`[${lang}] ${s.id} step ${i + 1}: ${v}`);
      if (!controlDone && m.max > 40 && m.centres.length && !v) {
        // Negative control: move the frame far from the focus and the verdict must change. A focus that spans the whole
        // diagram (a box at each end) stays in view wherever the frame stops, so the control tries each step until one
        // can show the defect, and fails only when none of them can.
        const moved = await player.evaluate((root) => {
          const f = root.querySelector("div.overflow-x-auto");
          f.scrollLeft = f.scrollLeft > f.scrollWidth / 4 ? 0 : f.scrollWidth;
          return null;
        }).then(() => player.evaluate(probe, ids));
        if (Math.abs(moved.sl - m.sl) > 20) {
          controlTried = true;
          if (verdict(moved) !== null) {
            console.log("self-test ok: a frame scrolled away from the focus is reported");
            controlDone = true;
          }
        }
      }
    }
  }
  if (controlTried && !controlDone) problems.push("SELF-TEST FAILED: a frame scrolled away from the focus was not reported on any step");
  await ctx.close();
}
await browser.close();
console.log(`checked ${checked} steps on a 390px phone (${measured} of them have a focus to measure; ${walks.length} walk-throughs x 2 languages)`);
console.log(problems.length ? `${problems.length} PROBLEMS:\n${problems.join("\n")}` : "no problems");
process.exit(problems.length ? 1 : 0);
