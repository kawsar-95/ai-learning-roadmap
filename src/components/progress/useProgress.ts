"use client";

import {
  BOOKMARKS_STORAGE_KEY,
  PROGRESS_STORAGE_KEY,
  parseProgress,
  serializeProgress,
  setKeys,
  toggleKey,
} from "@/lib/progress";
import { QUIZ_SCORES_STORAGE_KEY, parseScores, recordBest } from "@/lib/quiz";
import type { QuizScores } from "@/lib/quiz";
import { createStore } from "./createStore";

const EMPTY: ReadonlySet<string> = new Set();
const NO_SCORES: QuizScores = {};

/** A set of section keys. Progress and bookmarks each have one. */
function createKeyStore(storageKey: string, eventName: string) {
  const store = createStore<ReadonlySet<string>>({
    storageKey,
    eventName,
    parse: parseProgress,
    serialize: serializeProgress,
    empty: EMPTY,
    isEmpty: (keys) => keys.size === 0,
  });
  return {
    use: store.use,
    toggle: (key: string) => store.write(toggleKey(store.get(), key)),
    set: (keys: string[], value: boolean) => store.write(setKeys(store.get(), keys, value)),
    reset: () => store.write(EMPTY),
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

const quizScores = createStore<QuizScores>({
  storageKey: QUIZ_SCORES_STORAGE_KEY,
  eventName: "quiz-scores-change",
  parse: parseScores,
  serialize: JSON.stringify,
  empty: NO_SCORES,
  isEmpty: (scores) => Object.keys(scores).length === 0,
});

/** The best quiz score of each topic. Same first-render rule as `useProgress`. */
export const useQuizScores = quizScores.use;

/** Records one quiz attempt. The best score stays unless this one is higher. */
export function saveQuizScore(slug: string, correct: number, total: number) {
  quizScores.write(recordBest(quizScores.get(), slug, correct, total));
}
