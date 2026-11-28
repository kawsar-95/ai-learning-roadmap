import type { WalkNode, WalkShow } from "@/lib/content-schema";
import type { Lang } from "@/lib/i18n";
import type { Box } from "@/lib/walkthrough";
import { NODE_ROLE, isoPillY } from "@/lib/walkthrough";
import { Icon } from "./WalkIcon";

/**
 * The isometric look of a box: a solid object on a floor tile (a laptop, a hexagonal block, a
 * cylinder), a name under it, and a pill over it for the step's second line. The object is drawn
 * around the centre of the box, so the lines that already run to the box edges still meet it. Its
 * colors are the role colors (`--role`), shaded for the top and the two sides; its look is in
 * globals.css (`.iso-*`).
 */

const TILE = "M0 -21 42 0 0 21 -42 0z";
const TILE_L = "M-42 0 0 21V28L-42 7z";
const TILE_R = "M42 0 0 21V28L42 7z";

function Floor() {
  return (
    <g>
      <path className="iso-side-l" d={TILE_L} />
      <path className="iso-side-r" d={TILE_R} />
      <path className="iso-floor" d={TILE} />
    </g>
  );
}

/** A hexagonal block: the top, and three sides. `y` is the height of its top above the floor tile. */
function Hex({ y, h }: { y: number; h: number }) {
  const top = "M-22 0 -11 -9.5 11 -9.5 22 0 11 9.5 -11 9.5z";
  return (
    <g transform={`translate(0 ${y})`}>
      <path className="iso-side-l" d={`M-22 0 -11 9.5 -11 ${9.5 + h} -22 ${h}z`} />
      <path className="iso-side-m" d={`M-11 9.5 11 9.5 11 ${9.5 + h} -11 ${9.5 + h}z`} />
      <path className="iso-side-r" d={`M11 9.5 22 0 22 ${h} 11 ${9.5 + h}z`} />
      <path className="iso-top" d={top} />
    </g>
  );
}

function Object3d({ kind }: { kind: WalkNode["kind"] }) {
  switch (kind) {
    case "browser":
      // A laptop: a flat keyboard on the tile, and a screen standing at the back.
      return (
        <g>
          <path className="iso-side-l" d="M-26 4 0 17 0 21 -26 8z" />
          <path className="iso-side-r" d="M26 4 0 17 0 21 26 8z" />
          <path className="iso-top" d="M0 -9 26 4 0 17 -26 4z" />
          <path className="iso-screen" d="M-26 4 0 -9 0 -36 -26 -23z" />
          <path className="iso-screen-glow" d="M-22 2 -4 -7 -4 -30 -22 -21z" />
        </g>
      );
    case "database":
    case "storage":
    case "file":
      return (
        <g>
          <path className="iso-side-m" d="M-22 -2V16A22 9 0 0 0 22 16V-2z" />
          <path className="iso-side-r" d="M0 7.5A22 9 0 0 0 22 16V-2L0 -2z" opacity={0.5} />
          <ellipse className="iso-top" cx={0} cy={-2} rx={22} ry={9} />
          <path className="iso-band" d="M-22 5.5A22 9 0 0 0 22 5.5M-22 12A22 9 0 0 0 22 12" />
        </g>
      );
    case "dns":
      // A block with a globe on its top.
      return (
        <g>
          <Hex y={-8} h={22} />
          <g className="iso-mark" transform="translate(0 -8)">
            <ellipse cx={0} cy={0} rx={12} ry={5.5} />
            <ellipse cx={0} cy={0} rx={5} ry={5.5} />
            <path d="M-12 0H12" />
          </g>
        </g>
      );
    case "server":
      // A server: a block with two bays on its front.
      return (
        <g>
          <Hex y={-8} h={22} />
          <g className="iso-mark" transform="translate(0 -8)">
            <path d="M-8 -2.5 8 -2.5M-8 2.5 8 2.5" />
          </g>
          <path className="iso-led" d="M-6 21h.01M-2 21h.01" />
        </g>
      );
    default:
      // Every other kind: the same block with its own icon standing above it.
      return (
        <g>
          <Hex y={-4} h={20} />
          <g className="iso-badge" transform="translate(-10 -40)">
            <rect x={-3} y={-3} width={26} height={26} rx={7} />
            <Icon kind={kind} />
          </g>
        </g>
      );
  }
}

/** A name or a second line on a pill. */
function Pill({ x, y, text, kind }: { x: number; y: number; text: string; kind: "name" | "note" | "hot" | "warn" }) {
  const w = Math.max(34, [...text].length * 6.6 + 18);
  return (
    <g className="iso-pill" data-kind={kind} transform={`translate(${x} ${y})`}>
      <rect x={-w / 2} y={-10} width={w} height={20} rx={10} />
      <text y={4}>{text}</text>
    </g>
  );
}

export function IsoNode({ node, show, box, lang, scale = 1 }: { node: WalkNode; show: WalkShow | undefined; box: Box; lang: Lang; scale?: number }) {
  const pills = isoPillY(scale);
  const state = show?.state;
  const sub = show?.sub?.[lang];
  return (
    <g
      data-node={node.id}
      data-role={NODE_ROLE[node.kind]}
      data-state={show ? (state ?? "plain") : "off"}
      className="wk-node iso-node"
      style={{
        translate: `${box.x}px ${box.y}px`,
        opacity: show ? (state === "dim" ? 0.5 : 1) : 0,
      }}
    >
      <g transform={`translate(0 ${6 * scale}) scale(${scale})`}>
        <Floor />
        <Object3d kind={node.kind} />
      </g>
      <Pill x={0} y={pills.name} text={node.label[lang]} kind="name" />
      {sub && <Pill x={0} y={pills.sub} text={sub} kind={state === "warn" ? "warn" : state === "hot" ? "hot" : "note"} />}
    </g>
  );
}
