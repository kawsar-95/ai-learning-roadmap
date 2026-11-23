import type { CSSProperties } from "react";
import type { Block } from "@/lib/content-schema";
import { Inline } from "../Inline";

/**
 * The width the SVG may shrink to before its box scrolls sideways. Labels are
 * drawn for the viewBox width (about 12 px there), so below 90% of it they fall
 * under 11 px. The old fixed 640 px floor put a 1100 px
 * diagram at 58%, which is 7 px text.
 */
function minWidth(svg: string): number {
  const m = svg.match(/viewBox="\s*-?[\d.]+[\s,]+-?[\d.]+[\s,]+([\d.]+)[\s,]+[\d.]+/);
  const w = m ? Number(m[1]) : 0;
  return w > 0 ? Math.max(480, Math.round(w * 0.9)) : 640;
}

export function Diagram(block: Extract<Block, { type: "diagram" }>) {
  return (
    <figure className="my-5 rounded-lg border border-[var(--border)] bg-[var(--bg-raised)] p-4">
      <div
        style={{ "--diagram-min": `${minWidth(block.svg)}px` } as CSSProperties}
        className="diagram-svg overflow-x-auto [&>svg]:block [&>svg]:h-auto [&>svg]:w-full [&>svg]:min-w-[var(--diagram-min)]"
        dangerouslySetInnerHTML={{ __html: block.svg }}
      />
      {block.caption && (
        <figcaption className="mt-2.5 border-t border-dashed border-[var(--border-strong)] pt-2.5 text-[13px] italic text-[var(--text-dim)]">
          <Inline html={block.caption} />
        </figcaption>
      )}
      {block.captionBn && (
        <figcaption lang="bn" className="mt-1 text-[13px] text-[var(--text-faint)]">
          <Inline html={block.captionBn} />
        </figcaption>
      )}
    </figure>
  );
}
