"use client";

import { useEffect, useRef } from "react";

/**
 * The 3px bar under the header that fills as the reader scrolls the page.
 * It writes the width straight to the DOM, so a scroll does not re-render
 * React.
 */
export function ReadingBar() {
  const fill = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? Math.min(1, window.scrollY / max) : 0;
      if (fill.current) fill.current.style.transform = `scaleX(${ratio})`;
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-x-0 top-16 z-30 h-[3px]">
      <div
        ref={fill}
        style={{ transform: "scaleX(0)" }}
        className="h-full origin-left bg-linear-to-r from-accent to-accent-2"
      />
    </div>
  );
}
