"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent, RefObject } from "react";
import type { WalkLink, WalkNode, WalkNodeKind, WalkShow, WalkStep, Walkthrough } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import {
  DIAGRAM_PAD,
  NODE_H,
  NODE_ROLE,
  changedValues,
  focusX,
  labelPads,
  linkEnds,
  localDigits,
  nodeWidths,
  roundedRectPath,
  valueText,
  walkUses,
} from "@/lib/walkthrough";
import type { Box } from "@/lib/walkthrough";
import { Inline } from "./Inline";

// The look of the diagram and of the card around it is in globals.css (`.wk-*` and the `--wk-*` colors).
const BOX_R = 14;
const NOTE_R = 10;
const DOT_R = 5.5;
const SIGN = { "+": "+", "-": "−", "~": "~" } as const;

/** A 20 × 20 line icon for each kind of box. */
function Icon({ kind }: { kind: WalkNodeKind }) {
  const line = {
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (kind) {
    case "user":
      return (
        <g {...line}>
          <circle cx="10" cy="6.5" r="3.5" />
          <path d="M3.5 18c0-3.9 2.9-6.2 6.5-6.2s6.5 2.3 6.5 6.2" />
        </g>
      );
    case "browser":
      return (
        <g {...line}>
          <rect x="2" y="3.5" width="16" height="13" rx="2" />
          <path d="M2 7.5h16M4.8 5.5h.01M7 5.5h.01" />
        </g>
      );
    case "dns":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M2.5 10h15M10 2.5c2.2 2.1 3.2 4.6 3.2 7.5s-1 5.4-3.2 7.5c-2.2-2.1-3.2-4.6-3.2-7.5s1-5.4 3.2-7.5z" />
        </g>
      );
    case "server":
      return (
        <g {...line}>
          <rect x="3" y="3" width="14" height="6" rx="1.5" />
          <rect x="3" y="11" width="14" height="6" rx="1.5" />
          <path d="M6 6h.01M6 14h.01" />
        </g>
      );
    case "database":
      return (
        <g {...line}>
          <ellipse cx="10" cy="4.8" rx="6.5" ry="2.3" />
          <path d="M3.5 4.8v10.4c0 1.3 2.9 2.3 6.5 2.3s6.5-1 6.5-2.3V4.8M3.5 10c0 1.3 2.9 2.3 6.5 2.3s6.5-1 6.5-2.3" />
        </g>
      );
    case "cache":
      return (
        <g {...line}>
          <path d="M11 2.5 4.5 11h5l-1 6.5L15.5 9h-5z" />
        </g>
      );
    case "cdn":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M2.5 10h15M10 2.5v15" />
          <circle cx="10" cy="10" r="2.2" />
        </g>
      );
    case "balancer":
      return (
        <g {...line}>
          <path d="M2.5 10h5l4-5h5M7.5 10l4 5h5M14.5 3l2.5 2-2.5 2M14.5 13l2.5 2-2.5 2" />
        </g>
      );
    case "queue":
      return (
        <g {...line}>
          <rect x="2.5" y="6" width="4" height="8" rx="1" />
          <rect x="8" y="6" width="4" height="8" rx="1" />
          <rect x="13.5" y="6" width="4" height="8" rx="1" />
        </g>
      );
    case "storage":
      return (
        <g {...line}>
          <rect x="2.5" y="4" width="15" height="4" rx="1" />
          <path d="M3.5 8v7.5h13V8M8 11h4" />
        </g>
      );
    case "service":
      return (
        <g {...line}>
          <rect x="3" y="3" width="14" height="14" rx="3.5" />
          <circle cx="10" cy="10" r="3" />
        </g>
      );
    case "lock":
      return (
        <g {...line}>
          <rect x="4.5" y="9" width="11" height="8" rx="2" />
          <path d="M6.8 9V6.6a3.2 3.2 0 0 1 6.4 0V9M10 12.2v2" />
        </g>
      );
    case "key":
      return (
        <g {...line}>
          <circle cx="6.5" cy="13.5" r="3.5" />
          <path d="M9 11 17 3M14 6l2.5 2.5M11.8 8.2l2 2" />
        </g>
      );
    case "shield":
      return (
        <g {...line}>
          <path d="M10 2.5 4 5v4.6c0 4 2.6 6.8 6 7.9 3.4-1.1 6-3.9 6-7.9V5z" />
          <path d="m7.3 10 2.1 2.1 3.5-3.9" />
        </g>
      );
    case "clock":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M10 5.5V10l3 2" />
        </g>
      );
    case "chart":
      return (
        <g {...line}>
          <path d="M3 3v14h14" />
          <path d="m6 13 3-4 3 2 4-6" />
        </g>
      );
    case "file":
      return (
        <g {...line}>
          <path d="M5 2.5h6.5L15 6v11.5H5z" />
          <path d="M11.5 2.5V6H15M7.5 10h5M7.5 13h5" />
        </g>
      );
    case "model":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="2.4" />
          <circle cx="3.8" cy="4.5" r="1.8" />
          <circle cx="16.2" cy="4.5" r="1.8" />
          <circle cx="3.8" cy="15.5" r="1.8" />
          <circle cx="16.2" cy="15.5" r="1.8" />
          <path d="M5.3 5.6l3 2.7M14.7 5.6l-3 2.7M5.3 14.4l3-2.7M14.7 14.4l-3-2.7" />
        </g>
      );
    case "tool":
      return (
        <g {...line}>
          <path d="M7.6 3.2c-1.8 0-2.6.9-2.6 2.6v1.7c0 1.1-.7 2-1.9 2.5 1.2.5 1.9 1.4 1.9 2.5v1.7c0 1.7.8 2.6 2.6 2.6M12.4 3.2c1.8 0 2.6.9 2.6 2.6v1.7c0 1.1.7 2 1.9 2.5-1.2.5-1.9 1.4-1.9 2.5v1.7c0 1.7-.8 2.6-2.6 2.6" />
        </g>
      );
    case "note":
      return null;
  }
}

/** A 20 × 20 line icon for each kind of callout. */
function NoteIcon({ kind }: { kind: "insight" | "tip" | "warn" }) {
  switch (kind) {
    case "insight":
      return (
        <svg viewBox="0 0 20 20" aria-hidden>
          <path d="M10 2.5a5.2 5.2 0 0 0-3 9.5c.6.5.9 1.1.9 1.8v.4h4.2v-.4c0-.7.3-1.3.9-1.8A5.2 5.2 0 0 0 10 2.5zM8 16.5h4M8.8 18.2h2.4" />
        </svg>
      );
    case "tip":
      return (
        <svg viewBox="0 0 20 20" aria-hidden>
          <circle cx="10" cy="10" r="7.5" />
          <path d="m6.6 10.3 2.3 2.3 4.5-4.9" />
        </svg>
      );
    case "warn":
      return (
        <svg viewBox="0 0 20 20" aria-hidden>
          <path d="M10 3 2.5 16.5h15z" />
          <path d="M10 8v4M10 14.2h.01" />
        </svg>
      );
  }
}

/**
 * One box. Every box is drawn in every step, so it can fade in, fade out and move. Its look is in
 * globals.css (`.wk-*`): the state and the role are data attributes. The first <rect> is the box
 * and the texts are direct children of the group, because the browser audits read them that way.
 */
function SceneNode({ node, show, box, lang }: { node: WalkNode; show: WalkShow | undefined; box: Box; lang: Lang }) {
  const state = show?.state;
  const sub = show?.sub?.[lang];
  const note = node.kind === "note";
  const textX = note ? 14 : 40;
  const badge = show?.badge ? localDigits(show.badge, lang) : null;
  const badgeW = badge ? 14 + [...badge].length * 7 : 0;
  return (
    <g
      data-node={node.id}
      data-role={NODE_ROLE[node.kind]}
      data-state={show ? (state ?? "plain") : "off"}
      className="wk-node"
      style={{
        translate: `${box.x - box.w / 2}px ${box.y - box.h / 2}px`,
        opacity: show ? (state === "dim" ? 0.5 : 1) : 0,
      }}
    >
      {!note && <path className="wk-shadow" d={roundedRectPath(3, 4, box.w, box.h, BOX_R)} />}
      <rect className="wk-box" width={box.w} height={box.h} rx={note ? NOTE_R : BOX_R} />
      {!note && (
        <>
          <g className="wk-tile" transform={`translate(22 ${box.h / 2 - 4})`} aria-hidden>
            <path className="wk-tile-left" d="M-15 0 0 9.5V15.5L-15 6z" />
            <path className="wk-tile-right" d="M15 0 0 9.5V15.5L15 6z" />
            <path className="wk-tile-top" d="M0-9.5 15 0 0 9.5-15 0z" />
            {/* The 20 × 20 icon is laid flat on the top face: scaled and sheared into the isometric plane. */}
            <g className="wk-icon" transform="matrix(0.69 0.4 -0.69 0.4 0 0) translate(-10 -10)">
              <Icon kind={node.kind} />
            </g>
          </g>
        </>
      )}
      <text className="wk-label" x={textX} y={sub ? 24 : 33}>
        {node.label[lang]}
      </text>
      {sub && (
        <text className="wk-sub" x={textX} y={42}>
          {sub}
        </text>
      )}
      {state === "warn" && !note && (
        <g className="wk-mark" transform="translate(5 1)">
          <circle r={9} />
          <text y={4.5}>!</text>
        </g>
      )}
      {badge && (
        <g className="wk-badge" transform={`translate(${box.w - badgeW + 6} -9)`}>
          <rect width={badgeW} height={18} rx={9} />
          <text x={badgeW / 2} y={12.5} textAnchor="middle">
            {badge}
          </text>
        </g>
      )}
    </g>
  );
}

/**
 * A dot that travels along `path` again and again, from the moment the diagram starts. A dot that
 * goes out is a circle and one that comes back is a square: the shape says it as well as the
 * color, because orange and green are the same lightness. Readers who ask for reduced motion see
 * no dots.
 */
function Dot({ path, ms, delay, back }: { path: string; ms: number; delay: number; back: boolean }) {
  const dur = `${ms / 1000}s`;
  const begin = `${delay / 1000}s`;
  const motion = (
    <>
      <animateMotion dur={dur} begin={begin} repeatCount="indefinite" path={path} />
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.88;1" dur={dur} begin={begin} repeatCount="indefinite" />
    </>
  );
  const half = DOT_R - 0.7;
  return back ? (
    <rect className="wk-dot wk-dot-back motion-reduce:hidden" x={-half} y={-half} width={2 * half} height={2 * half} rx={2.5} opacity={0}>
      {motion}
    </rect>
  ) : (
    <circle className="wk-dot motion-reduce:hidden" r={DOT_R} opacity={0}>
      {motion}
    </circle>
  );
}

/**
 * The text on a line, on a pill. The pill is sized from the text, so it is measured once the text is
 * drawn and again when its size changes (the web fonts arrive; a hidden player is shown). Where a box
 * stands beside the label the pill gives way, so it never touches a box. The text never moves.
 */
function LineLabel({ text, x, y, obstacles }: { text: string; x: number; y: number; obstacles: Box[] }) {
  const textRef = useRef<SVGTextElement>(null);
  const pillRef = useRef<SVGRectElement>(null);
  const shadowRef = useRef<SVGRectElement>(null);
  useLayoutEffect(() => {
    const label = textRef.current;
    const pill = pillRef.current;
    const shadow = shadowRef.current;
    if (!label || !pill || !shadow) return;
    const fit = () => {
      let b: DOMRect;
      try {
        b = label.getBBox();
      } catch {
        return; // not rendered yet (Firefox throws for a hidden element); the observer calls this again
      }
      const { left, right } = labelPads({ x: b.x, y: b.y, w: b.width, h: b.height }, obstacles);
      const h = b.height + 2;
      for (const [el, dx, dy] of [[pill, 0, 0], [shadow, 1.5, 2]] as const) {
        el.setAttribute("x", String(b.x - left + dx));
        el.setAttribute("y", String(b.y - 1 + dy));
        el.setAttribute("width", String(b.width + left + right));
        el.setAttribute("height", String(h));
        el.setAttribute("rx", String(h / 2));
      }
    };
    fit();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(fit);
    observer.observe(label);
    return () => observer.disconnect();
  }, [text, x, y, obstacles]);
  return (
    <>
      <rect ref={shadowRef} className="wk-pill-shadow" />
      <rect ref={pillRef} className="wk-pill" />
      <text ref={textRef} className="wk-link-label" x={x} y={y} textAnchor="middle">
        {text}
      </text>
    </>
  );
}

function SceneLink({
  link,
  from,
  to,
  lang,
  markerId,
  obstacles,
}: {
  link: WalkLink;
  from: Box;
  to: Box;
  lang: Lang;
  markerId: (state: string) => string;
  obstacles: Box[];
}) {
  const { x1, y1, x2, y2 } = linkEnds(from, to);
  const forward = `M${x1} ${y1} L${x2} ${y2}`;
  const backward = `M${x2} ${y2} L${x1} ${y1}`;
  const state = link.state ?? "plain";
  const ms = link.ms ?? 1400;
  const flow = link.flow;
  const label = link.label?.[lang];
  return (
    <g data-link={`${link.from}>${link.to}`} data-state={state} className="wk-link">
      <g opacity={state === "dim" ? 0.45 : 1}>
        <path
          className="wk-line"
          d={forward}
          markerEnd={flow === "to" || flow === "both" ? `url(#${markerId(state)})` : undefined}
          markerStart={flow === "back" || flow === "both" ? `url(#${markerId(state)})` : undefined}
        />
        {(flow === "to" || flow === "both") && <Dot path={forward} ms={ms} delay={0} back={false} />}
        {(flow === "back" || flow === "both") && <Dot path={backward} ms={ms} delay={flow === "both" ? ms / 2 : 0} back />}
      </g>
      {label && <LineLabel text={label} x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 8} obstacles={obstacles} />}
    </g>
  );
}

function Scene({
  walk,
  step,
  lang,
  svgRef,
  idBase,
  label,
}: {
  walk: Walkthrough;
  step: WalkStep;
  lang: Lang;
  svgRef: RefObject<SVGSVGElement | null>;
  idBase: string;
  label: string;
}) {
  const widths = useMemo(() => nodeWidths(walk, lang), [walk, lang]);
  const shown = useMemo(() => new Map(step.show.map((s) => [s.id, s])), [step]);
  const boxes = useMemo(
    () =>
      new Map<string, Box>(
        walk.nodes.map((n) => {
          const s = shown.get(n.id);
          return [n.id, { x: s?.x ?? n.x, y: s?.y ?? n.y, w: widths.get(n.id) ?? 112, h: NODE_H }];
        }),
      ),
    [walk, shown, widths],
  );
  // The boxes a line label has to keep clear of: the ones this step shows.
  const obstacles = useMemo(
    () =>
      walk.nodes.flatMap((n) => {
        const b = boxes.get(n.id);
        return b && shown.has(n.id) ? [b] : [];
      }),
    [walk, boxes, shown],
  );
  const at = (id: string): Box => boxes.get(id) ?? { x: 0, y: 0, w: 112, h: NODE_H };
  const byId = new Map(walk.nodes.map((n) => [n.id, n]));
  const markerId = (state: string) => `${idBase}-arrow-${state}`;
  return (
    <svg
      ref={svgRef}
      viewBox={`${-DIAGRAM_PAD} 0 ${walk.width + 2 * DIAGRAM_PAD} ${walk.height}`}
      role="img"
      aria-label={label}
      className="block h-auto w-full min-w-[540px]"
    >
      <defs>
        <pattern id={`${idBase}-lattice`} width="48" height="24" patternUnits="userSpaceOnUse">
          <path className="wk-lattice" d="M0 0L48 24M0 24L48 0" />
        </pattern>
        {(["plain", "dim", "hot", "warn"] as const).map((state) => (
          <marker
            key={state}
            id={markerId(state)}
            className={`wk-arrow wk-arrow-${state}`}
            viewBox="0 0 10 10"
            refX="8.5"
            refY="5"
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M0 1 9 5 0 9z" />
          </marker>
        ))}
      </defs>
      <rect x={-DIAGRAM_PAD} width={walk.width + 2 * DIAGRAM_PAD} height={walk.height} fill={`url(#${idBase}-lattice)`} />
      {step.links.map((link, i) => {
        if (!byId.has(link.from) || !byId.has(link.to)) return null;
        return <SceneLink key={`${link.from}-${link.to}-${i}`} link={link} from={at(link.from)} to={at(link.to)} lang={lang} markerId={markerId} obstacles={obstacles} />;
      })}
      {walk.nodes.map((node) => (
        <SceneNode key={node.id} node={node} show={shown.get(node.id)} box={at(node.id)} lang={lang} />
      ))}
    </svg>
  );
}

/**
 * A step-by-step walk-through of a section: readouts, a diagram that changes
 * with each step (dots show requests moving), and the words of the step.
 * Back and Next, the numbered steps, and the Left and Right keys move between
 * steps. Pause stops the dots. Readers who ask for reduced motion get the
 * same steps without dots or sliding boxes.
 */
export function StepPlayer({ walkthrough, sectionId, lang }: { walkthrough: Walkthrough; sectionId: string; lang: Lang }) {
  const ui = UI[lang];
  const steps = walkthrough.steps;
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);
  const frameRef = useRef<HTMLDivElement>(null);
  const stripRef = useRef<HTMLOListElement>(null);
  const step = steps[index];
  const text = step[lang];
  const changed = changedValues(index > 0 ? steps[index - 1].values : undefined, step.values);
  const uses = useMemo(() => walkUses(walkthrough), [walkthrough]);
  const headingId = `${sectionId}-walk`;
  const bangla = lang === "bn";
  const label = bangla ? "text-[14px] font-semibold" : "font-mono text-xs font-medium";
  const first = index === 0;
  const last = index === steps.length - 1;
  const nextShort = last ? null : steps[index + 1][lang].short;

  const go = (i: number) => setIndex(Math.max(0, Math.min(steps.length - 1, i)));

  // Pause and Play stop and start every dot of the diagram.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || typeof svg.pauseAnimations !== "function") return;
    if (paused) svg.pauseAnimations();
    else svg.unpauseAnimations();
  }, [paused]);

  // Keep the current step visible in the numbered steps, without scrolling the page.
  // On a narrow screen the diagram scrolls sideways too: bring the boxes the
  // step is about into view.
  useEffect(() => {
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    const strip = stripRef.current;
    const current = strip?.querySelector<HTMLElement>('[aria-current="step"]')?.closest("li");
    if (strip && current) {
      const left = current.offsetLeft;
      const right = left + current.offsetWidth;
      if (left < strip.scrollLeft || right > strip.scrollLeft + strip.clientWidth) {
        strip.scrollTo({ left: left - (strip.clientWidth - current.offsetWidth) / 2, behavior });
      }
    }
    const frame = frameRef.current;
    const svg = svgRef.current;
    const x = focusX(walkthrough, steps[index]);
    const focus = (how: ScrollBehavior) => {
      if (frame && svg && x !== null && frame.scrollWidth > frame.clientWidth) {
        const scale = svg.clientWidth / (walkthrough.width + 2 * DIAGRAM_PAD);
        frame.scrollTo({ left: (x + DIAGRAM_PAD) * scale - frame.clientWidth / 2, behavior: how });
      }
    };
    focus(behavior);

    // The topic page shows one section at a time, so this player can mount
    // hidden, with no width, and the scroll above did nothing. Do it once the
    // diagram is shown.
    let observer: ResizeObserver | undefined;
    if (frame && frame.clientWidth === 0 && typeof ResizeObserver !== "undefined") {
      observer = new ResizeObserver(() => {
        if (frame.clientWidth === 0) return;
        focus("auto");
        observer?.disconnect();
      });
      observer.observe(frame);
    }
    return () => observer?.disconnect();
  }, [index, steps, walkthrough]);

  const replay = () => {
    svgRef.current?.setCurrentTime(0);
    setPaused(false);
  };

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    let next: number;
    if (event.key === "ArrowRight") next = index + 1;
    else if (event.key === "ArrowLeft") next = index - 1;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = steps.length - 1;
    else return;
    event.preventDefault();
    go(next);
  }

  const navButton = "wk-btn inline-flex min-w-0 items-center gap-1.5 px-3 py-1.5 text-[13px]";
  const toolButton = "wk-btn inline-flex items-center gap-1.5 px-2.5 py-1 text-[13px]";

  return (
    <div
      role="group"
      aria-labelledby={headingId}
      onKeyDown={onKeyDown}
      lang={lang}
      className={"wk-card rounded-2xl bg-bg-raised px-4 py-4 sm:px-5 sm:py-5 " + (bangla ? "font-bengali" : "")}
    >
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <div className="flex flex-wrap items-center gap-x-2">
          <h3 id={headingId} className={`${label} text-accent`}>
            {ui.walkTitle}
          </h3>
          <span className={`wk-stepchip ${label}`}>{ui.walkStepOf(index + 1, steps.length)}</span>
        </div>
        <div className="flex gap-1.5 motion-reduce:hidden">
          <button type="button" onClick={replay} className={toolButton}>
            <svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
              <path d="M4 10a6 6 0 1 0 2-4.5M4 3.5V6h2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            {ui.walkReplay}
          </button>
          <button type="button" onClick={() => setPaused((p) => !p)} aria-pressed={paused} className={toolButton}>
            <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor" aria-hidden>
              {paused ? <path d="M6 4.5v11l9-5.5z" /> : <path d="M5.5 4.5h3v11h-3zM11.5 4.5h3v11h-3z" />}
            </svg>
            {paused ? ui.walkPlay : ui.walkPause}
          </button>
        </div>
      </div>

      {walkthrough.metrics.length > 0 && (
        <dl className="mt-3 grid grid-cols-[repeat(auto-fit,minmax(7.5rem,1fr))] gap-2">
          {walkthrough.metrics.map((metric, i) => {
            const value = valueText(step.values?.[i], lang);
            const fresh = changed[i] && value !== null;
            return (
              <div key={i} className="wk-metric min-w-0 px-3 py-2" data-fresh={fresh ? "" : undefined}>
                <dt className="truncate text-[12px] text-text-faint">{metric[lang]}</dt>
                <dd className={"m-0 font-mono text-[16px] font-bold tabular-nums " + (fresh ? "text-accent" : value ? "text-text" : "text-text-faint")}>
                  {value ?? "—"}
                </dd>
              </div>
            );
          })}
        </dl>
      )}
      {walkthrough.caption && <p className="mt-1.5 text-[12px] text-text-faint">{walkthrough.caption[lang]}</p>}

      <div ref={frameRef} className="wk-frame mt-3 overflow-x-auto rounded-lg">
        <Scene walk={walkthrough} step={step} lang={lang} svgRef={svgRef} idBase={headingId} label={ui.walkDiagram(text.title)} />
      </div>
      <p className="wk-key mt-2.5 flex flex-wrap gap-x-4 gap-y-1 text-[12px] text-text-dim">
        <span>
          <i aria-hidden className="wk-key-focus" />
          {ui.walkKeyFocus}
        </span>
        <span>
          <i aria-hidden className="wk-key-plain" />
          {ui.walkKeyOther}
        </span>
        {uses.warn && (
          <span>
            <i aria-hidden className="wk-key-red" />
            {ui.walkKeyBad}
          </span>
        )}
        {uses.out && (
          <span>
            <i aria-hidden className="wk-key-out" />
            {ui.walkKeyOut}
          </span>
        )}
        {uses.back && (
          <span>
            <i aria-hidden className="wk-key-back" />
            {ui.walkKeyBack}
          </span>
        )}
      </p>

      <p aria-live="polite" className="sr-only">
        {ui.walkStepOf(index + 1, steps.length)}: {text.title}
      </p>
      <div key={index} className="voice-fade mt-4">
        <h4 className="font-display text-[20px] font-semibold leading-snug text-text">{text.title}</h4>
        {text.body.map((html, i) => (
          <Inline key={i} as="p" html={html} className="mt-2 text-[16px] leading-[1.75] text-pretty text-text-dim" />
        ))}
        {text.points && (
          <ul className="mt-3 list-disc space-y-1.5 pl-5 text-[16px] leading-relaxed text-text marker:text-accent">
            {text.points.map((html, i) => (
              <Inline key={i} as="li" html={html} />
            ))}
          </ul>
        )}
        {text.note && (
          <div className="wk-note mt-4 text-[15px] leading-relaxed" data-kind={text.note.kind}>
            <span className="wk-note-icon">
              <NoteIcon kind={text.note.kind} />
            </span>
            <div>
              <b className="wk-note-tag">{ui.walkNote[text.note.kind]}</b> <Inline html={text.note.html} />
            </div>
          </div>
        )}
        {text.changes && (
          <div className="mt-4">
            <p className={`${label} text-text-faint`}>{ui.walkChanges}</p>
            <ul className="mt-1.5 space-y-1 text-[15px] leading-relaxed text-text-dim">
              {text.changes.map((change, i) => (
                <li key={i} className="wk-change flex gap-2.5" data-sign={change.sign}>
                  <span aria-hidden className="wk-sign">
                    {SIGN[change.sign]}
                  </span>
                  <Inline html={change.html} />
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="wk-nav mt-5 pt-4">
        <ol ref={stripRef} aria-label={ui.walkSteps} className="wk-track">
          {steps.map((s, i) => (
            <li key={i} className="wk-tk" data-state={i === index ? "on" : i < index ? "done" : "todo"}>
              <button type="button" onClick={() => go(i)} aria-current={i === index ? "step" : undefined} title={s[lang].title}>
                <span className="wk-tkc">{localDigits(String(i + 1), lang)}</span>
                <span className="wk-tkl">{s[lang].short}</span>
              </button>
            </li>
          ))}
        </ol>
        <div className="mt-3.5 flex items-center justify-between gap-2">
          <button type="button" onClick={() => go(index - 1)} aria-disabled={first} className={navButton}>
            <span aria-hidden>←</span>
            <span className="truncate">{ui.walkBack}</span>
          </button>
          <button type="button" onClick={() => go(index + 1)} aria-disabled={last} className={navButton + " wk-next"}>
            <span className="truncate">{nextShort ? `${ui.walkNext}: ${nextShort}` : ui.walkNext}</span>
            <span aria-hidden>→</span>
          </button>
        </div>
      </div>
      <p className="mt-2 hidden text-[12px] text-text-faint sm:block">{ui.walkKeys}</p>
    </div>
  );
}
