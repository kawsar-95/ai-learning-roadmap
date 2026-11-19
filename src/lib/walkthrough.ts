// Layout and text helpers for the walk-through player. No React here, so
// `node --test` can load it.

import type { Lang } from "./i18n.ts";
import type { Bilingual, WalkNodeKind, WalkStep, Walkthrough } from "./content-schema.ts";

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

/** What a box is, which picks its color: people, your services, fast memory, data, queues, guards, models, measures, notes. */
export type WalkRole = "people" | "compute" | "memory" | "data" | "queue" | "guard" | "model" | "measure" | "note";

/**
 * The role of each kind of box. The record is exhaustive on purpose: a kind added to
 * WALK_NODE_KINDS does not compile until it is given a color here.
 */
export const NODE_ROLE: Record<WalkNodeKind, WalkRole> = {
  user: "people",
  browser: "people",
  dns: "compute",
  server: "compute",
  service: "compute",
  balancer: "compute",
  cache: "memory",
  cdn: "memory",
  database: "data",
  storage: "data",
  file: "data",
  queue: "queue",
  lock: "guard",
  key: "guard",
  shield: "guard",
  tool: "guard",
  model: "model",
  clock: "measure",
  chart: "measure",
  note: "note",
};

/**
 * What a whole walk-through draws, so the key under the diagram does not change from step
 * to step: whether a box or a line is ever in the warn state, and whether a line ever
 * sends a dot out or back.
 */
export function walkUses(w: Walkthrough): { warn: boolean; out: boolean; back: boolean } {
  const uses = { warn: false, out: false, back: false };
  for (const step of w.steps) {
    if (step.show.some((s) => s.state === "warn")) uses.warn = true;
    for (const link of step.links) {
      if (link.state === "warn") uses.warn = true;
      if (link.flow === "to" || link.flow === "both") uses.out = true;
      if (link.flow === "back" || link.flow === "both") uses.back = true;
    }
  }
  return uses;
}

/** A rounded rectangle as a path: the hard shadow of a box. A path and not a <rect>, so the first <rect> of a box stays the box itself. */
export function roundedRectPath(x: number, y: number, w: number, h: number, r: number): string {
  return `M${x + r} ${y}H${x + w - r}A${r} ${r} 0 0 1 ${x + w} ${y + r}V${y + h - r}A${r} ${r} 0 0 1 ${x + w - r} ${y + h}H${x + r}A${r} ${r} 0 0 1 ${x} ${y + h - r}V${y + r}A${r} ${r} 0 0 1 ${x + r} ${y}Z`;
}

/**
 * The padding left and right of a line label's pill: `base` units each side, less where a box
 * stands beside the label, so the pill stays `clear` units off every box. The text never moves;
 * only the pill gives way. `label` is the text's box (x, y, w, h) in diagram units.
 */
export function labelPads(label: { x: number; y: number; w: number; h: number }, boxes: Box[], base = 4, clear = 1.5): { left: number; right: number } {
  let left = base;
  let right = base;
  const top = label.y - 1;
  const bottom = label.y + label.h + 1;
  for (const b of boxes) {
    const l = b.x - b.w / 2 - clear;
    const r = b.x + b.w / 2 + clear;
    const t = b.y - b.h / 2 - clear;
    const u = b.y + b.h / 2 + clear;
    if (t >= bottom || u <= top) continue;
    if (l >= label.x + label.w) right = Math.max(0, Math.min(right, l - (label.x + label.w)));
    else if (r <= label.x) left = Math.max(0, Math.min(left, label.x - r));
  }
  return { left, right };
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

/** Where a section's walk-through is served from, as a path from the site root. The caller adds the basePath. */
export function walkthroughPath(slug: string, sectionId: string): string {
  return `/walkthroughs/${slug}/${sectionId}.json`;
}

type WithWalkthroughs = { slug: string; sections: readonly { id: string; walkthrough?: Walkthrough }[] };

/**
 * The static params of the walk-through route: one file for each section that
 * has a walk-through. `file` keeps the `.json` extension, so the export writes
 * `walkthroughs/<slug>/<id>.json` and a static host serves it as JSON.
 */
export function walkthroughParams(topics: readonly WithWalkthroughs[]): { slug: string; file: string }[] {
  return topics.flatMap((t) => t.sections.filter((s) => s.walkthrough).map((s) => ({ slug: t.slug, file: `${s.id}.json` })));
}

/** The walk-through that `walkthroughPath` points at, or undefined. */
export function findWalkthrough(topics: readonly WithWalkthroughs[], slug: string, file: string): Walkthrough | undefined {
  if (!file.endsWith(".json")) return undefined;
  const id = file.slice(0, -".json".length);
  return topics.find((t) => t.slug === slug)?.sections.find((s) => s.id === id)?.walkthrough;
}
