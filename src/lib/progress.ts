// Reading progress: the sections the reader marked as done. The list lives
// in localStorage as a JSON array of "<topic slug>/<section id>" keys. This
// file has no React and no server imports, so client components and
// `node --test` can use it.

/** The localStorage key that holds the done sections. */
export const PROGRESS_STORAGE_KEY = "progress";

/** The localStorage key of the bookmarked sections. Same key format as progress. */
export const BOOKMARKS_STORAGE_KEY = "bookmarks";

/** The localStorage key of the roadmap lessons marked as done. Keys come from lessonKey in roadmap-schema.ts. */
export const ROADMAP_STORAGE_KEY = "roadmap-progress";

export type ProgressSummary = { done: number; total: number; percent: number };

export function progressKey(slug: string, sectionId: string): string {
  return `${slug}/${sectionId}`;
}

/** The stored value as a set. Missing or bad data gives an empty set. */
export function parseProgress(raw: string | null): Set<string> {
  if (!raw) return new Set();
  try {
    const value: unknown = JSON.parse(raw);
    if (!Array.isArray(value)) return new Set();
    return new Set(value.filter((item): item is string => typeof item === "string"));
  } catch {
    return new Set();
  }
}

export function serializeProgress(done: ReadonlySet<string>): string {
  return JSON.stringify([...done].sort());
}

/** A new set with `key` added if it was missing, or removed if it was there. */
export function toggleKey(done: ReadonlySet<string>, key: string): Set<string> {
  const next = new Set(done);
  if (next.has(key)) next.delete(key);
  else next.add(key);
  return next;
}

/** A new set with every key in `keys` added (value true) or removed (value false). */
export function setKeys(done: ReadonlySet<string>, keys: string[], value: boolean): Set<string> {
  const next = new Set(done);
  for (const key of keys) {
    if (value) next.add(key);
    else next.delete(key);
  }
  return next;
}

/**
 * Counts the keys in `all` that are done. Keys of sections that no longer
 * exist stay in storage but do not count.
 */
export function summarize(done: ReadonlySet<string>, all: readonly string[]): ProgressSummary {
  const count = all.filter((key) => done.has(key)).length;
  return {
    done: count,
    total: all.length,
    percent: all.length ? Math.round((count / all.length) * 100) : 0,
  };
}

/** The first key of `all`, in reading order, that is not done. */
export function firstUndone(done: ReadonlySet<string>, all: readonly string[]): string | null {
  return all.find((key) => !done.has(key)) ?? null;
}

/** The keys of `order`, in reading order, that are bookmarked. Unknown stored keys are dropped. */
export function resolveBookmarks(stored: ReadonlySet<string>, order: readonly string[]): string[] {
  return order.filter((key) => stored.has(key));
}
