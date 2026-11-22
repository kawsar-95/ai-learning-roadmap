// A topic page has two side columns: the Parts list on the left and "On this page" on the right. Each can be
// folded away to a thin rail, and the text then grows to use the room. The choice is kept in localStorage and
// put on <html> before the first paint, the way src/lib/theme.ts does for the theme.

export type Panel = "parts" | "toc";

export const PANELS: readonly Panel[] = ["parts", "toc"];

/** The value that is stored, and set on <html>, for a folded column. Any other value, or none, means open. */
export const COLLAPSED = "collapsed";

/** The localStorage key that holds whether a column is folded. */
export function panelStorageKey(panel: Panel): string {
  return `panel-${panel}`;
}

/** The attribute on <html> that globals.css reads: data-parts or data-toc. */
export function panelAttribute(panel: Panel): string {
  return `data-${panel}`;
}

export function isCollapsed(stored: string | null): boolean {
  return stored === COLLAPSED;
}

const CHECKS = PANELS.map(
  (panel) =>
    `if(localStorage.getItem(${JSON.stringify(panelStorageKey(panel))})===${JSON.stringify(COLLAPSED)})` +
    `d.setAttribute(${JSON.stringify(panelAttribute(panel))},${JSON.stringify(COLLAPSED)});`,
).join("");

/**
 * The code that sets data-parts and data-toc on <html> for each folded
 * column, without a wrapper. The site runs it in <head> before the first
 * paint, together with the other two init scripts (see
 * src/lib/init-script.ts).
 * It must give the same result as isCollapsed (tests/panels.test.ts checks
 * this). If storage is blocked, the columns stay open, as the server renders
 * them.
 */
export const PANEL_INIT_BODY = `var d=document.documentElement;${CHECKS}`;

/**
 * Runs in <head> before the first paint and sets data-parts and data-toc on <html> for each folded column.
 * It must give the same result as isCollapsed (tests/panels.test.ts checks this). If storage is blocked, the
 * columns stay open, as the server renders them.
 */
export const PANEL_INIT_SCRIPT = `(function(){try{${PANEL_INIT_BODY}}catch(e){}})()`;
