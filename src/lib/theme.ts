export type Theme = "light" | "dark";

/** The localStorage key that holds the reader's choice. */
export const THEME_STORAGE_KEY = "theme";

/** A saved choice wins. Without one, follow the device setting. */
export function resolveTheme(stored: string | null, prefersLight: boolean): Theme {
  if (stored === "light" || stored === "dark") return stored;
  return prefersLight ? "light" : "dark";
}

export function nextTheme(theme: Theme): Theme {
  return theme === "light" ? "dark" : "light";
}

/**
 * The code that sets data-theme on <html>, without a wrapper. The site runs
 * it in <head> before the first paint, together with the other two init
 * scripts (see src/lib/init-script.ts).
 * It must give the same result as resolveTheme (tests/theme.test.ts checks
 * this). If storage is blocked, the server default (dark) stays.
 */
export const THEME_INIT_BODY = `var s=localStorage.getItem(${JSON.stringify(
  THEME_STORAGE_KEY,
)});var t=s==="light"||s==="dark"?s:window.matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";document.documentElement.setAttribute("data-theme",t)`;

/**
 * Runs in <head> before the first paint and sets data-theme on <html>.
 * It must give the same result as resolveTheme (tests/theme.test.ts checks
 * this). If storage is blocked, the server default (dark) stays.
 */
export const THEME_INIT_SCRIPT = `(function(){try{${THEME_INIT_BODY}}catch(e){}})()`;
