"use client";

import { useSyncExternalStore } from "react";
import {
  BOOKMARKS_STORAGE_KEY,
  PROGRESS_STORAGE_KEY,
  parseProgress,
  serializeProgress,
  setKeys,
  toggleKey,
} from "@/lib/progress";

const EMPTY: ReadonlySet<string> = new Set();

/**
 * A set of section keys kept in localStorage under `storageKey`. Progress
 * and bookmarks each have one. `eventName` tells the components in this tab
 * that the list changed, because the "storage" event fires only in other tabs.
 */
function createKeyStore(storageKey: string, eventName: string) {
  function readRaw(): string | null {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  }

  // useSyncExternalStore needs the same object while the stored text is the
  // same, so the parsed set is cached by its source text.
  let cachedRaw: string | null = null;
  let cachedSet: ReadonlySet<string> = EMPTY;

  function getSnapshot(): ReadonlySet<string> {
    const raw = readRaw();
    if (raw !== cachedRaw) {
      cachedRaw = raw;
      cachedSet = parseProgress(raw);
    }
    return cachedSet;
  }

  function subscribe(onChange: () => void) {
    const onStorage = (event: StorageEvent) => {
      if (event.key === storageKey || event.key === null) onChange();
    };
    window.addEventListener("storage", onStorage);
    window.addEventListener(eventName, onChange);
    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener(eventName, onChange);
    };
  }

  function write(keys: ReadonlySet<string>) {
    try {
      if (keys.size) localStorage.setItem(storageKey, serializeProgress(keys));
      else localStorage.removeItem(storageKey);
    } catch {
      // Storage is blocked: the list is not saved.
    }
    window.dispatchEvent(new Event(eventName));
  }

  return {
    use: () => useSyncExternalStore(subscribe, getSnapshot, () => EMPTY),
    toggle: (key: string) => write(toggleKey(getSnapshot(), key)),
    set: (keys: string[], value: boolean) => write(setKeys(getSnapshot(), keys, value)),
    reset: () => write(EMPTY),
  };
}

const progress = createKeyStore(PROGRESS_STORAGE_KEY, "progress-change");
const bookmarks = createKeyStore(BOOKMARKS_STORAGE_KEY, "bookmarks-change");

export const toggleDone = progress.toggle;
export const setDone = progress.set;
export const resetProgress = progress.reset;
export const toggleBookmark = bookmarks.toggle;

/**
 * The set of done section keys. The static HTML and the first client
 * render show nothing done; the stored list appears after hydration.
 */
export const useProgress = progress.use;

/** The set of bookmarked section keys. Same first-render rule as `useProgress`. */
export const useBookmarks = bookmarks.use;
