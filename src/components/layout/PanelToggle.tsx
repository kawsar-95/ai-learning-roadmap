"use client";

import { useLayoutEffect, useSyncExternalStore } from "react";
import { COLLAPSED, isCollapsed, panelAttribute, panelStorageKey } from "@/lib/panels";
import type { Panel } from "@/lib/panels";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";

function readStored(panel: Panel): string | null {
  try {
    return localStorage.getItem(panelStorageKey(panel));
  } catch {
    return null;
  }
}

function setFolded(panel: Panel, folded: boolean) {
  const root = document.documentElement;
  if (folded) root.setAttribute(panelAttribute(panel), COLLAPSED);
  else root.removeAttribute(panelAttribute(panel));
}

/** data-parts and data-toc on <html> are the source of truth, as data-theme is for the theme. */
function subscribeTo(panel: Panel) {
  return (onChange: () => void) => {
    const observer = new MutationObserver(onChange);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: [panelAttribute(panel)] });
    return () => observer.disconnect();
  };
}

function snapshotOf(panel: Panel) {
  return () => document.documentElement.getAttribute(panelAttribute(panel)) === COLLAPSED;
}

// useSyncExternalStore needs the same functions on every render, so each column gets its own pair once.
const SUBSCRIBE = { parts: subscribeTo("parts"), toc: subscribeTo("toc") };
const SNAPSHOT = { parts: snapshotOf("parts"), toc: snapshotOf("toc") };

// The arrow points the way the column moves: away when it is open, back when it is folded. The turn comes
// from CSS, so it is right before hydration too. The class names are spelled out for Tailwind to find them.
const ARROW: Record<Panel, string> = {
  parts: "parts-collapsed:rotate-180",
  toc: "rotate-180 toc-collapsed:rotate-0",
};

/**
 * The button that folds a side column to a rail and opens it again. The inline script from src/lib/panels.ts
 * sets the saved state on <html> before the first paint; this button changes it and saves the choice.
 * `controls` is the id of the column's content.
 */
export function PanelToggle({
  panel,
  lang,
  controls,
  className = "",
}: {
  panel: Panel;
  lang: Lang;
  controls: string;
  className?: string;
}) {
  const ui = UI[lang];
  const collapsed = useSyncExternalStore(SUBSCRIBE[panel], SNAPSHOT[panel], () => null);

  // Same guard as ThemeToggle: if a development remount clears the attribute on <html>, fold again before
  // paint. It only folds: opening a column also removes it from storage, so there is nothing to undo here.
  // When the attribute is already set, it changes nothing.
  useLayoutEffect(() => {
    if (isCollapsed(readStored(panel))) setFolded(panel, true);
  }, [panel]);

  const toggle = () => {
    const next = !SNAPSHOT[panel]();
    setFolded(panel, next);
    try {
      if (next) localStorage.setItem(panelStorageKey(panel), COLLAPSED);
      else localStorage.removeItem(panelStorageKey(panel));
    } catch {
      // Storage is blocked: the column still folds for this page.
    }
  };

  const text =
    panel === "parts"
      ? { name: ui.partsNav, hide: ui.partsHide, show: ui.partsShow }
      : { name: ui.onThisPage, hide: ui.tocHide, show: ui.tocShow };
  // Before hydration the state is not known: name the column, and say what the button does once it is.
  const label = collapsed === null ? text.name : collapsed ? text.show : text.hide;

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={label}
      title={label}
      aria-expanded={collapsed === null ? undefined : !collapsed}
      aria-controls={controls}
      className={
        "grid size-8 shrink-0 place-items-center rounded-md text-text-dim transition-colors hover:bg-bg-raised-2 hover:text-text " +
        className
      }
    >
      <svg viewBox="0 0 20 20" className={"size-[18px] " + ARROW[panel]} fill="none" aria-hidden="true">
        <path d="M12.5 4.5 7 10l5.5 5.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}
