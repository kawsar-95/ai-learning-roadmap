import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildManifest } from "../scripts/precache.mjs";

const appDir = fileURLToPath(new URL("../src/app/", import.meta.url));
const css = readFileSync(appDir + "globals.css", "utf8");
const svg = readFileSync(appDir + "icon.svg", "utf8");

/** The --accent and --on-accent colors in the globals.css block that `selector` matches. */
function themeColors(selector: RegExp) {
  const block = css.match(selector)?.[1] ?? "";
  const color = (name: string) => block.match(new RegExp(`--${name}:\\s*(#[0-9a-f]{6})`, "i"))?.[1].toLowerCase();
  return { tile: color("accent"), mark: color("on-accent") };
}

/** The .tile and .mark fill colors in a piece of the icon's <style>. */
function iconColors(style: string) {
  const fill = (name: string) => style.match(new RegExp(`\\.${name}\\s*\\{\\s*fill:\\s*(#[0-9a-f]{6})`, "i"))?.[1].toLowerCase();
  return { tile: fill("tile"), mark: fill("mark") };
}

// The icon is the header logo (bg-accent, text-on-accent) in a file. Its colors must follow the theme.
const style = svg.match(/<style>([\s\S]*?)<\/style>/)?.[1] ?? "";
const [darkStyle, lightStyle = ""] = style.split(/@media \(prefers-color-scheme: light\)/);

test("icon.svg: the logo colors are the site's accent colors, dark by default and light when preferred", () => {
  for (const [theme, iconStyle] of [["dark", darkStyle], ["light", lightStyle]] as const) {
    const want = themeColors(new RegExp(`:root\\[data-theme="${theme}"\\]\\s*\\{([^}]*)\\}`));
    assert.match(want.tile ?? "", /^#[0-9a-f]{6}$/, `--accent of the ${theme} theme in globals.css`);
    assert.match(want.mark ?? "", /^#[0-9a-f]{6}$/, `--on-accent of the ${theme} theme in globals.css`);
    assert.deepEqual(iconColors(iconStyle), want, `${theme} colors of icon.svg`);
  }
});

test("icon.svg: no comment holds a double hyphen (that makes the XML invalid, and browsers draw nothing)", () => {
  for (const [, body] of svg.matchAll(/<!--([\s\S]*?)-->/g)) assert.ok(!body.includes("--"), `comment: ${body.trim().slice(0, 40)}`);
});

test("favicon.ico: is a valid icon file with the tab sizes (16 and 32 px)", () => {
  const ico = readFileSync(appDir + "favicon.ico");
  assert.deepEqual([ico.readUInt16LE(0), ico.readUInt16LE(2)], [0, 1]); // reserved, type 1 = icon
  const sizes: number[] = [];
  for (let i = 0; i < ico.readUInt16LE(4); i++) {
    const entry = 6 + 16 * i;
    const width = ico[entry] || 256; // 0 means 256
    const bytes = ico.readUInt32LE(entry + 8);
    const offset = ico.readUInt32LE(entry + 12);
    assert.ok(bytes > 0 && offset + bytes <= ico.length, `the ${width} px frame lies inside the file`);
    sizes.push(width);
  }
  assert.ok(sizes.includes(16) && sizes.includes(32), `sizes: ${sizes}`);
});

test("precache: saves the tab icons, so they also show offline", () => {
  const dir = mkdtempSync(join(tmpdir(), "out-"));
  for (const file of ["favicon.ico", "icon.svg", "apple-icon.png"]) writeFileSync(join(dir, file), file);
  assert.deepEqual(buildManifest(dir).map((e: { url: string }) => e.url), ["apple-icon.png", "favicon.ico", "icon.svg"]);
});
