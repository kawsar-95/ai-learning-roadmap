// Reading progress: the sections the reader marked as done. The list lives
// in localStorage as a JSON array of "<topic slug>/<section id>" keys. This
// file has no React and no server imports, so client components and
// `node --test` can use it.

/** The localStorage key that holds the done sections. */
export const PROGRESS_STORAGE_KEY = "progress";

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
