"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent, RefObject } from "react";
import type { WalkLink, WalkNode, WalkNodeKind, WalkShow, WalkStep, Walkthrough } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { DIAGRAM_PAD, NODE_H, changedValues, focusX, linkEnds, localDigits, nodeWidths, valueText } from "@/lib/walkthrough";
import type { Box } from "@/lib/walkthrough";
import { Inline } from "./Inline";

const STATE_COLOR = { hot: "var(--accent)", warn: "var(--warn)" } as const;
const NOTE_COLOR = { insight: "var(--accent)", tip: "var(--good)", warn: "var(--warn)" } as const;
const SIGN = {
  "+": { mark: "+", color: "var(--good)" },
  "-": { mark: "−", color: "var(--danger)" },
  "~": { mark: "~", color: "var(--warn)" },
} as const;

/** A 20 × 20 line icon for each kind of box. */
function Icon({ kind }: { kind: WalkNodeKind }) {
  const line = {
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
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
    case "note":
      return null;
  }
}

/** One box. Every box is drawn in every step, so it can fade in, fade out and move. */
function SceneNode({ node, show, box, lang }: { node: WalkNode; show: WalkShow | undefined; box: Box; lang: Lang }) {
  const state = show?.state;
  const color = state === "hot" || state === "warn" ? STATE_COLOR[state] : undefined;
  const sub = show?.sub?.[lang];
  const textX = node.kind === "note" ? 14 : 40;
  const badge = show?.badge ? localDigits(show.badge, lang) : null;
  const badgeW = badge ? 14 + [...badge].length * 7 : 0;
  return (
    <g
      data-node={node.id}
      className="transition-[transform,opacity] duration-[420ms] ease-[cubic-bezier(.2,.7,.2,1)] motion-reduce:transition-none"
      style={{
        transform: `translate(${box.x - box.w / 2}px, ${box.y - box.h / 2}px)`,
        opacity: show ? (state === "dim" ? 0.5 : 1) : 0,
      }}
    >
      <rect
        width={box.w}
        height={box.h}
        rx={10}
        strokeWidth={color ? 1.8 : 1.2}
        style={{
          fill: color ? `color-mix(in srgb, ${color} 12%, var(--bg-raised))` : "var(--bg-raised)",
          stroke: color ?? "var(--border-strong)",
        }}
      />
      {node.kind !== "note" && (
        <g transform={`translate(12 ${box.h / 2 - 10})`} style={{ color: color ?? "var(--text-dim)" }}>
          <Icon kind={node.kind} />
        </g>
      )}
      <text x={textX} y={sub ? 24 : 33} className="fill-text text-[13px] font-medium">
        {node.label[lang]}
      </text>
      {sub && (
        <text x={textX} y={42} className="fill-text-dim text-[11.5px]">
          {sub}
        </text>
      )}
      {badge && (
        <g transform={`translate(${box.w - badgeW + 6} -9)`}>
          <rect width={badgeW} height={18} rx={9} style={{ fill: color ?? "var(--accent)" }} />
          <text x={badgeW / 2} y={12.5} textAnchor="middle" className="fill-on-accent font-mono text-[11px] font-semibold">
            {badge}
          </text>
        </g>
      )}
    </g>
  );
}

/**
 * A dot that travels along `path` again and again, from the moment the
 * diagram starts. Readers who ask for reduced motion see no dots.
 */
function Dot({ path, ms, delay, color }: { path: string; ms: number; delay: number; color: string }) {
  const dur = `${ms / 1000}s`;
  const begin = `${delay / 1000}s`;
  return (
    <circle r={4.5} opacity={0} className="motion-reduce:hidden" style={{ fill: color }}>
      <animateMotion dur={dur} begin={begin} repeatCount="indefinite" path={path} />
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.88;1" dur={dur} begin={begin} repeatCount="indefinite" />
    </circle>
  );
}

function SceneLink({ link, from, to, lang, markerId }: { link: WalkLink; from: Box; to: Box; lang: Lang; markerId: (state: string) => string }) {
  const { x1, y1, x2, y2 } = linkEnds(from, to);
  const forward = `M${x1} ${y1} L${x2} ${y2}`;
  const backward = `M${x2} ${y2} L${x1} ${y1}`;
  const state = link.state ?? "plain";
  const strong = state === "hot" || state === "warn";
  const dotColor = strong ? STATE_COLOR[state] : "var(--accent)";
  const ms = link.ms ?? 1400;
  const flow = link.flow;
  const label = link.label?.[lang];
  return (
    <g data-link={`${link.from}>${link.to}`}>
      <g opacity={state === "dim" ? 0.45 : 1}>
        <path
          d={forward}
          fill="none"
          strokeWidth={state === "hot" ? 2 : 1.5}
          strokeDasharray={state === "dim" ? "5 5" : undefined}
          style={{ stroke: strong ? STATE_COLOR[state] : "var(--border-strong)" }}
          markerEnd={flow === "to" || flow === "both" ? `url(#${markerId(state)})` : undefined}
          markerStart={flow === "back" || flow === "both" ? `url(#${markerId(state)})` : undefined}
        />
        {(flow === "to" || flow === "both") && <Dot path={forward} ms={ms} delay={0} color={dotColor} />}
        {(flow === "back" || flow === "both") && <Dot path={backward} ms={ms} delay={flow === "both" ? ms / 2 : 0} color={dotColor} />}
      </g>
      {label && (
        <text
          x={(x1 + x2) / 2}
          y={(y1 + y2) / 2 - 8}
          textAnchor="middle"
          className="fill-text-dim text-[11.5px]"
          style={{ paintOrder: "stroke", stroke: "var(--bg)", strokeWidth: 5, strokeLinejoin: "round" }}
        >
          {label}
        </text>
      )}
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
  const shown = new Map(step.show.map((s) => [s.id, s]));
  const box = (node: WalkNode): Box => {
    const s = shown.get(node.id);
    return { x: s?.x ?? node.x, y: s?.y ?? node.y, w: widths.get(node.id) ?? 112, h: NODE_H };
  };
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
        <pattern id={`${idBase}-grid`} width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="1.5" cy="1.5" r="1" style={{ fill: "var(--border-strong)" }} />
        </pattern>
        {(["plain", "dim", "hot", "warn"] as const).map((state) => (
          <marker
            key={state}
            id={markerId(state)}
            viewBox="0 0 10 10"
            refX="8.5"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M0 1 9 5 0 9z" style={{ fill: state === "hot" || state === "warn" ? STATE_COLOR[state] : "var(--text-faint)" }} />
          </marker>
        ))}
      </defs>
      <rect x={-DIAGRAM_PAD} width={walk.width + 2 * DIAGRAM_PAD} height={walk.height} fill={`url(#${idBase}-grid)`} />
      {step.links.map((link, i) => {
        const from = byId.get(link.from);
        const to = byId.get(link.to);
        if (!from || !to) return null;
        return <SceneLink key={`${link.from}-${link.to}-${i}`} link={link} from={box(from)} to={box(to)} lang={lang} markerId={markerId} />;
      })}
      {walk.nodes.map((node) => (
        <SceneNode key={node.id} node={node} show={shown.get(node.id)} box={box(node)} lang={lang} />
      ))}
    </svg>
  );
}

/**
 * A step-by-step walk-through of a section: readouts, a diagram that changes
 * with each step (dots show requests moving), and the words of the step.
 * Back and Next, the step strip, and the Left and Right keys move between
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
  const headingId = `${sectionId}-walk`;
  const bangla = lang === "bn";
  const label = bangla ? "text-[14px] font-semibold" : "font-mono text-xs font-medium uppercase tracking-[0.16em]";
  const first = index === 0;
  const last = index === steps.length - 1;

  const go = (i: number) => setIndex(Math.max(0, Math.min(steps.length - 1, i)));

  // Pause and Play stop and start every dot of the diagram.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || typeof svg.pauseAnimations !== "function") return;
    if (paused) svg.pauseAnimations();
    else svg.unpauseAnimations();
  }, [paused]);

  // Keep the current step visible in the strip, without scrolling the page.
  // On a narrow screen the diagram scrolls sideways too: bring the boxes the
  // step is about into view.
  useEffect(() => {
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    const strip = stripRef.current;
    const current = strip?.querySelector<HTMLElement>('[aria-current="step"]');
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

  const navButton =
    "inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-border-strong bg-bg px-3 py-1.5 text-[13px] font-medium text-text transition-colors hover:border-accent hover:text-accent aria-disabled:cursor-not-allowed aria-disabled:opacity-40 aria-disabled:hover:border-border-strong aria-disabled:hover:text-text";
  const toolButton =
    "inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1 text-[12.5px] text-text-dim transition-colors hover:border-accent hover:text-accent";

  return (
    <div
      role="group"
      aria-labelledby={headingId}
      onKeyDown={onKeyDown}
      lang={lang}
      className={"rounded-2xl border border-border bg-bg-raised px-4 py-4 sm:px-5 sm:py-5 " + (bangla ? "font-bengali" : "")}
    >
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <div className="flex flex-wrap items-baseline gap-x-2">
          <h3 id={headingId} className={`${label} text-accent`}>
            {ui.walkTitle}
          </h3>
          <span className={`${label} text-text-faint`}>· {ui.walkStepOf(index + 1, steps.length)}</span>
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
              <div
                key={i}
                className="min-w-0 rounded-lg border border-border bg-bg px-3 py-2 transition-colors"
                style={fresh ? { borderColor: "color-mix(in srgb, var(--accent) 60%, var(--border))" } : undefined}
              >
                <dt className="truncate text-[12px] text-text-faint">{metric[lang]}</dt>
                <dd className={"m-0 font-mono text-[15px] tabular-nums " + (fresh ? "text-accent" : value ? "text-text" : "text-text-faint")}>
                  {value ?? "—"}
                </dd>
              </div>
            );
          })}
        </dl>
      )}
      {walkthrough.caption && <p className="mt-1.5 text-[12px] text-text-faint">{walkthrough.caption[lang]}</p>}

      <div ref={frameRef} className="mt-3 overflow-x-auto rounded-xl border border-border bg-bg">
        <Scene walk={walkthrough} step={step} lang={lang} svgRef={svgRef} idBase={headingId} label={ui.walkDiagram(text.title)} />
      </div>

      <p aria-live="polite" className="sr-only">
        {ui.walkStepOf(index + 1, steps.length)}: {text.title}
      </p>
      <div key={index} className="voice-fade mt-4">
        <h4 className="font-display text-[1.3rem] font-semibold leading-snug text-text">{text.title}</h4>
        {text.body.map((html, i) => (
          <Inline key={i} as="p" html={html} className="mt-2 text-[16px] leading-[1.75] text-pretty text-text-dim" />
        ))}
        {text.points && (
          <ul className="mt-3 list-disc space-y-1.5 pl-5 text-[15.5px] leading-relaxed text-text marker:text-accent">
            {text.points.map((html, i) => (
              <Inline key={i} as="li" html={html} />
            ))}
          </ul>
        )}
        {text.note && (
          <div
            className="mt-4 rounded-[10px] border-l-[3px] px-4 py-3 text-[15px] leading-relaxed text-text"
            style={{
              borderLeftColor: NOTE_COLOR[text.note.kind],
              backgroundColor: `color-mix(in srgb, ${NOTE_COLOR[text.note.kind]} 8%, transparent)`,
            }}
          >
            <span className="mr-2 font-semibold" style={{ color: NOTE_COLOR[text.note.kind] }}>
              {ui.walkNote[text.note.kind]}
            </span>
            <Inline html={text.note.html} />
          </div>
        )}
        {text.changes && (
          <div className="mt-4">
            <p className={`${label} text-text-faint`}>{ui.walkChanges}</p>
            <ul className="mt-1.5 space-y-1 text-[15px] leading-relaxed text-text-dim">
              {text.changes.map((change, i) => (
                <li key={i} className="flex gap-2.5">
                  <span aria-hidden className="w-3 shrink-0 text-center font-mono font-semibold" style={{ color: SIGN[change.sign].color }}>
                    {SIGN[change.sign].mark}
                  </span>
                  <Inline html={change.html} />
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="mt-5 flex items-center gap-2 border-t border-border pt-4">
        <button type="button" onClick={() => go(index - 1)} aria-disabled={first} className={navButton}>
          <span aria-hidden>←</span>
          <span className="sr-only sm:not-sr-only">{ui.walkBack}</span>
        </button>
        <ol ref={stripRef} aria-label={ui.walkSteps} className="relative flex min-w-0 flex-1 gap-1 overflow-x-auto px-0.5 py-1">
          {steps.map((s, i) => {
            const active = i === index;
            return (
              <li key={i} className="shrink-0">
                <button
                  type="button"
                  onClick={() => go(i)}
                  aria-current={active ? "step" : undefined}
                  title={s[lang].title}
                  className={
                    "flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-1 text-[12.5px] transition-colors " +
                    (active
                      ? "border-accent bg-accent text-on-accent"
                      : i < index
                        ? "border-border-strong text-text-dim hover:text-text"
                        : "border-border text-text-faint hover:text-text")
                  }
                >
                  <span className="font-mono text-[11px]">{localDigits(String(i + 1).padStart(2, "0"), lang)}</span>
                  <span>{s[lang].short}</span>
                </button>
              </li>
            );
          })}
        </ol>
        <button type="button" onClick={() => go(index + 1)} aria-disabled={last} className={navButton}>
          <span className="sr-only sm:not-sr-only">{ui.walkNext}</span>
          <span aria-hidden>→</span>
        </button>
      </div>
      <p className="mt-2 hidden text-[12px] text-text-faint sm:block">{ui.walkKeys}</p>
    </div>
  );
}
