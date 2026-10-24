"use client";

import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

/** One step of a long Part: a section, or the quiz. `label` is the progress text, for example "Section 3 of 10". */
export type Step = { id: string; title: string; label: string; node: ReactNode };

const TOP = "top";
const BUTTON =
  "group flex-1 rounded-2xl border border-border bg-bg-raised px-5 py-3 text-left no-underline shadow-card transition hover:border-accent hover:shadow-card-hover motion-reduce:transition-none";

/** The element id that a hash points to, or null. */
function idFromHash(hash: string): string | null {
  if (!hash.startsWith("#") || hash.length < 2) return null;
  try {
    return decodeURIComponent(hash.slice(1));
  } catch {
    return hash.slice(1);
  }
}

/** The step that holds the element with this id, or -1. */
function stepOf(id: string): number {
  const step = document.getElementById(id)?.closest<HTMLElement>("[data-step]");
  return step ? Number(step.dataset.step) : -1;
}

/**
 * Shows one step of a long Part at a time, so the reader takes it in small
 * pieces. All steps stay in the page (the others have `hidden`), so every
 * `#id` link still has a target: a link to an element in another step opens
 * that step first. The first render shows step 1, as the static HTML does.
 */
export function SectionPager({ steps, lang }: { steps: Step[]; lang: Lang }) {
  const ui = UI[lang];
  const [index, setIndex] = useState(0);
  const indexRef = useRef(0);
  const top = useRef<HTMLDivElement>(null);
  // What to scroll to after the next render: an element id, or TOP.
  const pending = useRef<string | null>(null);

  function show(i: number, scrollTo: string) {
    pending.current = scrollTo;
    if (i !== indexRef.current) setIndex(i);
    else scrollToPending();
  }

  function scrollToPending() {
    const target = pending.current;
    pending.current = null;
    const el = target === TOP ? top.current : target ? document.getElementById(target) : null;
    if (!el) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }

  function go(i: number) {
    show(i, TOP);
    history.replaceState(null, "", `#${steps[i].id}`);
  }

  // After a step shows: scroll, and tell the "On this page" list.
  useEffect(() => {
    indexRef.current = index;
    requestAnimationFrame(() => {
      if (pending.current) scrollToPending();
      window.dispatchEvent(new Event("section-step"));
    });
  }, [index]);

  // A hash, a click on an in-page link, or the Back button opens the step that holds the target.
  useEffect(() => {
    const reveal = (hash: string) => {
      const id = idFromHash(hash);
      const i = id ? stepOf(id) : -1;
      if (id && i >= 0 && i !== indexRef.current) show(i, id);
    };
    const onClick = (event: MouseEvent) => {
      if (event.defaultPrevented || event.button !== 0) return;
      const link = (event.target as Element | null)?.closest?.('a[href^="#"]');
      if (link) reveal(link.getAttribute("href") ?? "");
    };
    const onHashChange = () => reveal(window.location.hash);
    reveal(window.location.hash);
    document.addEventListener("click", onClick);
    window.addEventListener("hashchange", onHashChange);
    return () => {
      document.removeEventListener("click", onClick);
      window.removeEventListener("hashchange", onHashChange);
    };
    // show() only reads refs and the stable setter.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const prev = steps[index - 1];
  const next = steps[index + 1];
  return (
    <div>
      <div ref={top} className="scroll-mt-24" />
      <div className="mb-8">
        <p className="m-0 font-mono text-xs font-medium uppercase tracking-[0.16em] text-text-faint">
          {steps[index].label}
        </p>
        <div aria-hidden="true" className="mt-2 h-1.5 overflow-hidden rounded-full bg-bg-raised-2">
          <div
            className="h-full rounded-full bg-linear-to-r from-accent to-accent-2 transition-[width] duration-300"
            style={{ width: `${((index + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      {steps.map((step, i) => (
        <div key={step.id} data-step={i} hidden={i !== index}>
          {step.node}
        </div>
      ))}

      <nav aria-label={ui.stepNav} className="mt-12 flex flex-col gap-3 sm:flex-row">
        {prev && (
          <button type="button" onClick={() => go(index - 1)} className={BUTTON}>
            <span className="block font-mono text-xs uppercase tracking-[0.14em] text-text-faint">
              ← {ui.stepPrev}
            </span>
            <span className="mt-1 block font-display text-lg leading-snug text-text transition-colors group-hover:text-accent">
              {prev.title}
            </span>
          </button>
        )}
        {next && (
          <button type="button" onClick={() => go(index + 1)} className={BUTTON + " sm:text-right"}>
            <span className="block font-mono text-xs uppercase tracking-[0.14em] text-text-faint">
              {ui.stepNext} →
            </span>
            <span className="mt-1 block font-display text-lg leading-snug text-text transition-colors group-hover:text-accent">
              {next.title}
            </span>
          </button>
        )}
      </nav>
    </div>
  );
}
