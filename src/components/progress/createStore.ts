"use client";

import { useSyncExternalStore } from "react";

type StoreOptions<T> = {
  storageKey: string;
  /** Tells the components in this tab that the value changed; the "storage" event fires only in other tabs. */
  eventName: string;
  parse(raw: string | null): T;
  serialize(value: T): string;
  /** The value when nothing is stored, and on the server. Must be the same object each time. */
  empty: T;
  /** An empty value removes the item from storage. */
  isEmpty(value: T): boolean;
};

/** A value kept in localStorage under `storageKey`, with a React hook that follows it. */
export function createStore<T>({ storageKey, eventName, parse, serialize, empty, isEmpty }: StoreOptions<T>) {
  function readRaw(): string | null {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  }

  // useSyncExternalStore needs the same object while the stored text is the
  // same, so the parsed value is cached by its source text.
  let cachedRaw: string | null = null;
  let cachedValue: T = empty;

  function get(): T {
    const raw = readRaw();
    if (raw !== cachedRaw) {
      cachedRaw = raw;
      cachedValue = parse(raw);
    }
    return cachedValue;
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

  function write(value: T) {
    try {
      if (isEmpty(value)) localStorage.removeItem(storageKey);
      else localStorage.setItem(storageKey, serialize(value));
    } catch {
      // Storage is blocked: the value is not saved.
    }
    window.dispatchEvent(new Event(eventName));
  }

  return { use: () => useSyncExternalStore(subscribe, get, () => empty), get, write };
}
