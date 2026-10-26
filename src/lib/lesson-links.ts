// Turns the relative links and image paths of a lesson into addresses on this
// site or on GitHub. A lesson's markdown sits in phases/<phase>/<lesson>/docs/,
// so "../assets/x.svg" means phases/<phase>/<lesson>/assets/x.svg. This file
// has no server imports, so `node --test` can load it.

import { posix } from "node:path";

/** Where lesson files that are not lessons (code, outputs) are shown. */
export const UPSTREAM_REPO_URL = "https://github.com/rohitg00/ai-engineering-from-scratch";
export const UPSTREAM_BLOB_URL = `${UPSTREAM_REPO_URL}/blob/HEAD/phases/`;

const ABSOLUTE = /^([a-z][a-z0-9+.-]*:|\/\/)/i;

/** The path of `target` under phases/, or null when it points outside. */
function underPhases(target: string, folder: string, dir: string): string | null {
  const path = posix.normalize(posix.join(folder, dir, "docs", target));
  return path.startsWith("../") || path === ".." ? null : path;
}

export type ResolvedLink = { href: string; external: boolean };

/**
 * `known` holds "<phase folder>/<lesson folder>" for every lesson on the site.
 * A link to one of those becomes a page of this site; any other relative link
 * goes to the file on GitHub.
 */
export function resolveLessonHref(href: string, folder: string, dir: string, known: ReadonlySet<string>): ResolvedLink {
  if (href.startsWith("#")) return { href, external: false };
  if (ABSOLUTE.test(href)) return { href, external: true };

  const [target, hash = ""] = href.split("#");
  const path = target === "" ? null : underPhases(target, folder, dir);
  if (!path) return { href: UPSTREAM_REPO_URL, external: true };

  const lesson = path.match(/^([^/]+\/[^/]+)(?:\/(?:docs\/en\.md)?)?$/);
  if (lesson && known.has(lesson[1])) {
    return { href: `/roadmap/${lesson[1]}/${hash ? `#${hash}` : ""}`, external: false };
  }
  return { href: UPSTREAM_BLOB_URL + path.replace(/\/$/, ""), external: true };
}

/** The address of an image. Copied assets live in public/lesson-assets/. */
export function resolveLessonImage(src: string, folder: string, dir: string, basePath: string): string {
  if (ABSOLUTE.test(src)) return src;
  const path = underPhases(src, folder, dir);
  return path ? `${basePath}/lesson-assets/${path}` : "";
}
