"use client";

import { useSyncExternalStore } from "react";
import { PROGRESS_STORAGE_KEY, parseProgress, serializeProgress, toggleKey } from "@/lib/progress";

// The "storage" event fires only in other tabs. This event tells the
// components in this tab that the list changed.
const CHANGE_EVENT = "progress-change";
const EMPTY: ReadonlySet<string> = new Set();

function readRaw(): string | null {
  try {
    return localStorage.getItem(PROGRESS_STORAGE_KEY);
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
    if (event.key === PROGRESS_STORAGE_KEY || event.key === null) onChange();
  };
  window.addEventListener("storage", onStorage);
  window.addEventListener(CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onStorage);
    window.removeEventListener(CHANGE_EVENT, onChange);
  };
}

function write(done: ReadonlySet<string>) {
  try {
    if (done.size) localStorage.setItem(PROGRESS_STORAGE_KEY, serializeProgress(done));
    else localStorage.removeItem(PROGRESS_STORAGE_KEY);
  } catch {
    // Storage is blocked: progress is not saved.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function toggleDone(key: string) {
  write(toggleKey(getSnapshot(), key));
}

export function resetProgress() {
  write(EMPTY);
}

/**
 * The set of done section keys. The static HTML and the first client
 * render show nothing done; the stored list appears after hydration.
 */
export function useProgress(): ReadonlySet<string> {
  return useSyncExternalStore(subscribe, getSnapshot, () => EMPTY);
}
