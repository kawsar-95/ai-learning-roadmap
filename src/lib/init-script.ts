// The one script that runs in <head> before the first paint.
//
// It does three things: it sets the theme, it folds the side columns a reader
// had folded, and it opens a later visit in the language the reader chose.
// Each of the three was its own <script> tag. Three inline scripts are three
// render-blocking tags for the parser to walk, and the browser cannot paint
// until it has read all of them. One script that does the same work is one
// tag, and the same amount of parsing.
//
// The three pieces keep their own modules and their own tests
// (src/lib/theme.ts, src/lib/panels.ts, src/lib/i18n.ts). This file only
// joins their bodies: each module exports the code without a wrapper, and
// this puts the three together inside one try/catch, so a failure in one
// does not stop the others.

// Relative imports with an extension, like the other lib files that tests load.
import { THEME_INIT_BODY } from "./theme.ts";
import { PANEL_INIT_BODY } from "./panels.ts";
import { langInitBody } from "./i18n.ts";

/**
 * One script for the theme, the side columns, and the language.
 * The site sends it in <head>, so all three are set before the first paint.
 */
export function initScript(basePath: string): string {
  // Each body gets its own try/catch, as it had as a script of its own: with
  // storage blocked the theme read throws, and the language still has to be
  // set from the path. A ";" ends a body that has none.
  const bodies = [THEME_INIT_BODY, PANEL_INIT_BODY, langInitBody(basePath)];
  return `(function(){${bodies.map((body) => `try{${body};}catch(e){}`).join("")}})()`;
}
