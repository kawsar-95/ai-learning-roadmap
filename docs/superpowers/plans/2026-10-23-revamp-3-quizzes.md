# Revamp 3: Quizzes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a quiz system to topic pages: schema, scoring, saved best score, quiz box, header pill and link, and a dashboard score. No real questions ship.

**Architecture:** Quiz data is an optional `quiz` list in each topic file, checked by the existing zod schema. Pure logic (`scoreQuiz`, `parseScores`, `recordBest`) lives in `src/lib/quiz.ts`. The progress store function is generalized so a third store (quiz scores) reuses it. One client component renders the quiz.

**Tech Stack:** Next.js 16.4 (read `node_modules/next/dist/docs/` before Next-specific code), React 19.3, Tailwind 4, zod 4, `node --test`.

**Spec:** `docs/superpowers/specs/2026-10-23-revamp-3-quizzes-design.md`

## Global Constraints

- All new text goes into both `en` and `bn` in `src/lib/i18n.ts`. Numbers shown to the reader go through `fmtNum(lang, n)`.
- Quiz text is plain text, no HTML. English and Bangla for every question.
- A topic without `quiz`: no quiz box, no pill, no "Go to quiz" link, no dashboard score.
- localStorage key for scores: `quiz-scores`. It must differ from `progress` and `bookmarks`.
- Storage blocked: nothing is saved and nothing throws.
- No real questions are committed. Sample questions are for local checks only and are removed before each commit.
- No new dependencies. No new CSS files. Use existing tokens.
- Work on branch `feat/revamp-3-4`.

## Review Focus

- A quiz with a wrong shape (answer index out of range, option counts differ between languages, repeated id, empty list) must fail the build with a clear zod error, not render a broken quiz (Task 1 tests).
- A saved score whose `total` no longer matches the quiz (the owner edited the quiz) must not show a wrong "best" (Task 2 test; Task 5 check).
- Corrupt `quiz-scores` text: no crash, no score shown (Task 2 test).
- "Check answers" must stay disabled until every question has an answer, and must not save a score twice for one check (Task 4 manual check).
- The store generalization must not change progress or bookmarks behavior (Task 3 manual check with the same Playwright script as part 2).
- A reader with the quiz open in two tabs: the lower score from the second tab must not replace the best (Task 2 `recordBest` test).

---

### Task 1: Quiz schema

**Files:**
- Modify: `src/lib/content-schema.ts`
- Test: `tests/content-schema.test.ts`

**Interfaces:**
- Produces: type `QuizQuestion` (spec section 1), `QuizQuestionSchema`, and `quiz?: QuizQuestion[]` on `TopicFile` and `TopicFileSchema`.

- [ ] **Step 1: Write the failing tests** in `tests/content-schema.test.ts`. A helper `topicWithQuiz(quiz: unknown)` builds the minimal valid topic used by the file's other tests with `quiz` added. Tests (names exact):
  - `TopicFileSchema accepts a topic with an mcq and a tf question`: one `mcq` (`options` of 3 in both languages, `answer: 1`) and one `tf` (`answer: true`) parse, and the parsed value equals the input.
  - `TopicFileSchema accepts a topic with no quiz`: the existing minimal topic parses.
  - `TopicFileSchema rejects a bad quiz`: each of these throws — an `mcq` with 1 option; with 7 options; with `answer: 3` for 3 options; with `en` 3 options and `bn` 2; two questions with the same `id`; `quiz: []`; a `tf` with `answer: 1`; a question with an unknown key; an empty `q`.
- [ ] **Step 2: Run** `npm test` — expected: FAIL (the accept test fails on the unknown `quiz` key).
- [ ] **Step 3: Implement** the types and `QuizQuestionSchema` (`z.discriminatedUnion("kind", [...])` of two `strictObject`s with `PlainTextSchema` for all text; the `mcq` refine for option count 2 to 6, equal counts, and index range). Add `quiz: z.array(QuizQuestionSchema).min(1).refine(unique ids).optional()` to `TopicFileSchema`.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Commit** `feat: add the quiz schema to topic files`.

### Task 2: Pure quiz code

**Files:**
- Create: `src/lib/quiz.ts`
- Test: `tests/quiz.test.ts`

**Interfaces:**
- Consumes: `QuizQuestion` (Task 1; `import type` with a relative `.ts` path, like `search.ts`).
- Produces: `QUIZ_SCORES_STORAGE_KEY: string`, `type QuizScores = Record<string, { best: number; total: number }>`, `type QuizAnswers = Record<string, number | boolean>`, `scoreQuiz(questions: QuizQuestion[], answers: QuizAnswers): { correct: number; total: number }`, `parseScores(raw: string | null): QuizScores`, `recordBest(scores: QuizScores, slug: string, correct: number, total: number): QuizScores`.

- [ ] **Step 1: Write the failing tests** in `tests/quiz.test.ts` with a 3-question sample (`mcq` answer 1, `tf` answer true, `mcq` answer 0). Names exact:
  - `scoreQuiz counts all right answers`: 3 of 3.
  - `scoreQuiz counts a missing answer as wrong`: 2 of 3.
  - `scoreQuiz treats a wrong type as wrong`: answering the `tf` with `1` is wrong.
  - `parseScores reads a valid entry`; `parseScores ignores bad JSON and wrong shapes` (`"{x"`, `"[]"`, `"null"`); `parseScores drops an entry with best above total, a fraction, or a negative`.
  - `recordBest stores a first score`; `recordBest keeps the higher best`; `recordBest raises the best`; `recordBest replaces the entry when the total changed`; `recordBest does not change its input`.
  - `the quiz-scores key differs from progress and bookmarks keys` (import the other two from `../src/lib/progress.ts`).
- [ ] **Step 2: Run** `npm test` — expected: FAIL, `../src/lib/quiz.ts` not found.
- [ ] **Step 3: Implement** the exports to the spec section 2 rules.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Commit** `feat: add quiz scoring and saved-score helpers`.

### Task 3: Generic store and the quiz-scores store

**Files:**
- Create: `src/components/progress/createStore.ts`
- Modify: `src/components/progress/useProgress.ts`

**Interfaces:**
- Consumes: `parseScores`, `QUIZ_SCORES_STORAGE_KEY`, `recordBest`, `QuizScores` (Task 2).
- Produces: `createStore<T>(opts: { storageKey: string; eventName: string; parse(raw: string | null): T; serialize(value: T): string; empty: T; isEmpty(value: T): boolean }): { use(): T; get(): T; write(value: T): void }`; and from `useProgress.ts`: `useQuizScores(): QuizScores` and `saveQuizScore(slug: string, correct: number, total: number): void`. All existing exports of `useProgress.ts` keep their names and signatures.

No new unit test: the store is client code that `node --test` cannot load. The existing tests and Step 3 prove no change for progress and bookmarks.

- [ ] **Step 1: Implement** `createStore.ts` by moving the body of `createKeyStore` out of `useProgress.ts`: cached raw text and value, `getSnapshot`, `subscribe` (storage listener filters on `storageKey` or `null`), `write` (removes the item when `isEmpty`, same `try/catch`, then dispatches `eventName`), and `use` (`useSyncExternalStore`, server snapshot `empty`). Mark the file `"use client"`.
- [ ] **Step 2: Rebuild `useProgress.ts`** on `createStore`: the progress and bookmark stores use `parseProgress`/`serializeProgress` with an empty `Set`; add the quiz store (`parseScores`, `JSON.stringify`, `{}` as empty, `isEmpty` is "no keys") and export `useQuizScores` and `saveQuizScore` (reads `get()`, calls `recordBest`, writes). Keep the exports `useProgress`, `toggleDone`, `setDone`, `resetProgress`, `useBookmarks`, `toggleBookmark` unchanged.
- [ ] **Step 3: Run** `npm test`, `npm run lint`, `npm run build` — expected: all pass. Then run the part 2 browser check with Playwright against `out/` served on port 4173: mark a section done, bookmark another, reload; both persist in `progress` and `bookmarks`, and `localStorage.getItem("quiz-scores")` is `null`.
- [ ] **Step 4: Commit** `refactor: generalize the key store and add the quiz-scores store`.

### Task 4: Quiz box

**Files:**
- Create: `src/components/content/QuizSection.tsx`
- Modify: `src/components/pages/TopicPage.tsx`, `src/lib/i18n.ts`

**Interfaces:**
- Consumes: `QuizQuestion` (Task 1), `scoreQuiz`, `QuizAnswers` (Task 2), `useQuizScores`, `saveQuizScore` (Task 3).
- Produces: `<QuizSection slug={string} questions={QuizQuestion[]} lang={Lang} />`; i18n keys per spec section 6. Texts (en / bn): `quizTitle` "Quiz" / "কুইজ"; `quizIntro(n)` "Check what you learned. {n} questions." / "কী শিখলে যাচাই করো। {n}টি প্রশ্ন।"; `quizCheck` "Check answers" / "উত্তর মেলাও"; `quizAnswerAll` "Answer every question to check." / "মেলাতে সব প্রশ্নের উত্তর দাও।"; `quizRetry` "Try again" / "আবার চেষ্টা করো"; `quizScore(c,t)` "Score: {c} / {t}" / "স্কোর: {c} / {t}"; `quizBest(c,t)` "Best: {c} / {t}" / "সেরা: {c} / {t}"; `quizCorrect` "Correct" / "সঠিক"; `quizWrong` "Not quite" / "ঠিক হয়নি"; `quizRightAnswer` "Right answer:" / "সঠিক উত্তর:"; `quizTrue` "True" / "সত্য"; `quizFalse` "False" / "মিথ্যা"; `quizQuestions(n)` "{n} questions" / "{n}টি প্রশ্ন"; `goToQuiz` "Go to quiz" / "কুইজে যাও".

- [ ] **Step 1: Add the i18n keys** to both dicts.
- [ ] **Step 2: Implement `QuizSection`** to spec section 4. State: `answers: QuizAnswers`, `checked: boolean`. "Check answers" is disabled until `Object.keys(answers).length === questions.length`. On click: set `checked`, compute `scoreQuiz`, call `saveQuizScore` once. "Try again" clears both. Use `fieldset`/`legend`, radio inputs with the question id in `name`, labels wrapped around inputs. After the check each question shows ✓ Correct or ✗ Not quite, the right answer text, and `why`. The right option gets `border-accent`; a wrong choice gets `border-danger` (check the token name in `globals.css`).
- [ ] **Step 3: Render it** in `TopicPage.tsx` between the sections block and the `Sources` block, only when `topic.quiz` is set: `<QuizSection slug={topic.slug} questions={topic.quiz} lang={lang} />`.
- [ ] **Step 4: Run** `npm run lint`, `npm test`, `npm run build` — expected: pass; `grep -c 'id="quiz"' out/topics/inference/index.html` is 0 (no quiz yet).
- [ ] **Step 5: Manual check with a temporary sample.** Add a 3-question `quiz` to `src/content/inference.json` (do not commit), `npm run build`, serve `out/`, and with Playwright: the check button is disabled at first; after answering all, it enables; checking shows the score and `why`; reload keeps "Best"; "Try again" clears the answers; a second, lower attempt keeps the best. Then `git checkout src/content/inference.json`.
- [ ] **Step 6: Commit** `feat: add the quiz box to topic pages` (only source and i18n files).

### Task 5: Header pill, link, and dashboard score

**Files:**
- Modify: `src/components/content/TopicHeader.tsx`, `src/components/pages/DashboardPage.tsx`, `src/components/progress/DashboardWidgets.tsx`

**Interfaces:**
- Consumes: `useQuizScores` (Task 3), i18n keys `quizQuestions`, `goToQuiz`, `quizBest` (Task 4).
- Produces: `<QuizBest slug={string} total={number} lang={Lang} />` in `DashboardWidgets.tsx`.

- [ ] **Step 1:** In `TopicHeader`, when `topic.quiz` exists add a pill `📝 {ui.quizQuestions(fmtNum(lang, n))}` (same `PILL` class) and, in the action bar, an `<a href="#quiz">` styled like `TopicDoneButton` with text `ui.goToQuiz`.
- [ ] **Step 2:** `QuizBest` reads `useQuizScores()[slug]`; it renders `ui.quizBest(fmtNum(lang, best), fmtNum(lang, total))` in a small `font-mono text-[12px] text-text-faint` line only when an entry exists and `entry.total === total`; otherwise `null`.
- [ ] **Step 3:** In `DashboardPage`, inside each Part card under `PartProgress`, render `<QuizBest>` only when `topic.quiz` exists.
- [ ] **Step 4: Run** `npm run lint`, `npm test`, `npm run build` — expected: pass.
- [ ] **Step 5: Manual check** with the temporary sample from Task 4 (not committed): the inference page shows the pill and the link; after a check, `/dashboard/` shows "Best: 2 / 3" on the Part 7 card; edit the sample to 4 questions, rebuild: the dashboard shows nothing for Part 7 (changed total). Then `git checkout src/content/inference.json`.
- [ ] **Step 6: Commit** `feat: show the quiz in the topic header and on the dashboard`.

### Task 6: Owner guide and visual check

**Files:**
- Create: `docs/quizzes.md`

- [ ] **Step 1: Write `docs/quizzes.md`**: where to put `quiz` in a topic file, the format with one `mcq` and one `tf` example, the schema rules (spec section 1), the target of 5 questions for each topic, and the note that the build fails with a zod error on a bad quiz.
- [ ] **Step 2:** With the temporary sample on `inference.json` (and `llm-fundamentals.json` for a second Part), take screenshots with Playwright: the topic page quiz box (unanswered, checked with wrong answers, checked all right), header pill and link, and the dashboard Part card; light and dark, 1440px and 375px, English and Bangla. Read them. Fix what looks wrong. Then `git checkout src/content`.
- [ ] **Step 3:** Confirm `git status` shows no change in `src/content/`. Commit `docs: add the quiz guide for the owner`.
