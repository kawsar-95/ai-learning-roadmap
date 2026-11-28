"use client";

import { useEffect, useRef, useState } from "react";
import type { Walkthrough } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { StepPlayer } from "./StepPlayer";
import { ISO_PARTS, isoScale } from "@/lib/walkthrough";

/** The scale of the isometric look for a walk-through, or undefined for the flat boxes. */
function isoLook(path: string, walk: Walkthrough): number | undefined {
  const slug = path.split("/")[2];
  if (!ISO_PARTS.has(slug)) return undefined;
  return isoScale(walk) ?? undefined;
}

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Each file is fetched once, however often its section mounts. A failed fetch is forgotten, so Try again asks the network again. */
const loads = new Map<string, Promise<Walkthrough>>();

function load(path: string): Promise<Walkthrough> {
  let pending = loads.get(path);
  if (!pending) {
    pending = fetch(BASE_PATH + path).then((response) => {
      if (!response.ok) throw new Error(`walk-through ${path}: ${response.status}`);
      return response.json() as Promise<Walkthrough>;
    });
    loads.set(path, pending);
    pending.catch(() => loads.delete(path));
  }
  return pending;
}

/**
 * The walk-through of a section, loaded from its own JSON file when the
 * section first comes into view. A Part shows one section at a time and keeps
 * the others hidden, so a hidden section loads nothing, and the Part's page
 * does not carry the walk-throughs of all its sections. The file holds both
 * languages, so switching the voice needs no second fetch.
 */
export function LazyStepPlayer({ path, sectionId, lang }: { path: string; sectionId: string; lang: Lang }) {
  const ui = UI[lang];
  const holder = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState(false);
  const [walkthrough, setWalkthrough] = useState<Walkthrough | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);

  // A hidden section has no box, so it never intersects: it starts when the pager shows it.
  useEffect(() => {
    const element = holder.current;
    if (!element) return;
    if (typeof IntersectionObserver === "undefined") {
      const timer = setTimeout(() => setSeen(true), 0);
      return () => clearTimeout(timer);
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setSeen(true);
          observer.disconnect();
        }
      },
      { rootMargin: "300px" },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!seen) return;
    let current = true;
    load(path).then(
      (data) => current && setWalkthrough(data),
      () => current && setFailed(true),
    );
    return () => {
      current = false;
    };
  }, [seen, path, attempt]);

  if (walkthrough) return <StepPlayer walkthrough={walkthrough} sectionId={sectionId} lang={lang} look={isoLook(path, walkthrough)} />;

  return (
    <div
      ref={holder}
      role="status"
      aria-busy={!failed}
      className="flex min-h-[28rem] flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-bg-raised px-4 py-10 text-center text-[14px] text-text-dim"
    >
      {failed ? (
        <>
          <p>{ui.walkLoadFailed}</p>
          <button
            type="button"
            onClick={() => {
              setFailed(false);
              setAttempt((n) => n + 1);
            }}
            className="inline-flex items-center rounded-lg border border-border-strong bg-bg px-3 py-1.5 text-[13px] font-medium text-text transition-colors hover:border-accent hover:text-accent"
          >
            {ui.walkRetry}
          </button>
        </>
      ) : (
        <p>{ui.walkLoading}</p>
      )}
    </div>
  );
}
