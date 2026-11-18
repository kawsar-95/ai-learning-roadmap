// Layout and text helpers for the walk-through player. No React here, so
// `node --test` can load it.

import type { Lang } from "./i18n.ts";
import type { Bilingual, WalkStep, Walkthrough } from "./content-schema.ts";

/** The height of a box in the diagram, in diagram units. */
export const NODE_H = 56;
/** Empty space kept left and right of the diagram, so a box at the edge does not touch the frame. */
export const DIAGRAM_PAD = 8;
const MIN_W = 112;
const MAX_W = 240;

const BN_DIGITS = "০১২৩৪৫৬৭৮৯";

/** The text with Bangla digits on the Bangla site, for readouts and badges. */
export function localDigits(text: string, lang: Lang): string {
  return lang === "bn" ? text.replace(/[0-9]/g, (d) => BN_DIGITS[Number(d)]) : text;
}

/** The text of a readout value in one language, or null for a dash. */
export function valueText(value: string | Bilingual | null | undefined, lang: Lang): string | null {
  if (value === null || value === undefined) return null;
  return typeof value === "string" ? localDigits(value, lang) : value[lang];
}

/** The width of a box that holds these lines of text. */
export function boxWidth(lines: string[]): number {
  const longest = Math.max(0, ...lines.map((line) => [...line].length));
  return Math.min(MAX_W, Math.max(MIN_W, Math.round(52 + longest * 7.2)));
}

/**
 * The width of every box in one language: wide enough for its label and for
 * every second line any step gives it, so a box keeps its size between steps.
 */
export function nodeWidths(w: Walkthrough, lang: Lang): Map<string, number> {
  const lines = new Map<string, string[]>(w.nodes.map((n) => [n.id, [n.label[lang]]]));
  for (const step of w.steps) {
    for (const s of step.show) {
      if (s.sub) lines.get(s.id)?.push(s.sub[lang]);
    }
  }
  return new Map([...lines].map(([id, l]) => [id, boxWidth(l)]));
}

export type Box = { x: number; y: number; w: number; h: number };

/** The point where a line from the centre of `box` towards (tx, ty) leaves the box. */
export function boxExit(box: Box, tx: number, ty: number): [number, number] {
  const dx = tx - box.x;
  const dy = ty - box.y;
  if (dx === 0 && dy === 0) return [box.x, box.y];
  const sx = dx === 0 ? Infinity : box.w / 2 / Math.abs(dx);
  const sy = dy === 0 ? Infinity : box.h / 2 / Math.abs(dy);
  const s = Math.min(sx, sy);
  return [box.x + dx * s, box.y + dy * s];
}

/** The ends of a line from the edge of `a` to the edge of `b`, `gap` units clear of each box. */
export function linkEnds(a: Box, b: Box, gap = 6): { x1: number; y1: number; x2: number; y2: number } {
  const [ax, ay] = boxExit(a, b.x, b.y);
  const [bx, by] = boxExit(b, a.x, a.y);
  const len = Math.hypot(bx - ax, by - ay);
  const r = (n: number) => Math.round(n * 10) / 10;
  if (len <= gap * 2) return { x1: r(ax), y1: r(ay), x2: r(bx), y2: r(by) };
  const ux = (bx - ax) / len;
  const uy = (by - ay) / len;
  return { x1: r(ax + ux * gap), y1: r(ay + uy * gap), x2: r(bx - ux * gap), y2: r(by - uy * gap) };
}

/**
 * The middle, in diagram units, of the boxes a step is about (hot or warn),
 * or null when it marks none. A narrow screen scrolls the diagram to it.
 */
export function focusX(w: Walkthrough, step: WalkStep): number | null {
  const xs = step.show
    .filter((s) => s.state === "hot" || s.state === "warn")
    .map((s) => s.x ?? w.nodes.find((n) => n.id === s.id)?.x)
    .filter((x): x is number => x !== undefined);
  if (!xs.length) return null;
  return (Math.min(...xs) + Math.max(...xs)) / 2;
}

/** For each readout, whether its text differs from the step before. The first step marks none. */
export function changedValues(
  prev: (string | Bilingual | null)[] | undefined,
  cur: (string | Bilingual | null)[] | undefined,
): boolean[] {
  if (!cur) return [];
  if (!prev) return cur.map(() => false);
  return cur.map((value, i) => valueText(value, "en") !== valueText(prev[i], "en"));
}
