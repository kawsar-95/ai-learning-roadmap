# Revamp 3 of 4: quizzes for each topic

Date: 2026-10-23. Status: design approved by the owner in chat ("yes").

## Goal

Add a quiz system to the topic pages, like the quizzes at
https://www.systemdesignbangla.com/. The owner writes the questions. This
work ships the system and no questions. A topic without a quiz looks as it
does now.

Part of the revamp. Sub-projects 1 and 2 are merged.

## Decisions

| Topic | Decision |
|---|---|
| Who writes questions | The owner. This work ships no questions. |
| Target size | 5 questions for each topic (a guide, not a rule in code). |
| Question types | `mcq` (one right answer) and `tf` (true or false). |
| Where the data lives | An optional `quiz` list in each topic file in `src/content/`. |
| Text | Plain text only (no HTML). English and Bangla for every question. |
| Saved score | Best score for each topic, localStorage key `quiz-scores`. |
| Topic without `quiz` | No quiz box, no pill, no link, no score on the dashboard. |

## 1. Data (`src/lib/content-schema.ts`)

```ts
export type QuizQuestion =
  | { id: string; kind: "mcq"; answer: number; en: McqText; bn: McqText }
  | { id: string; kind: "tf"; answer: boolean; en: TfText; bn: TfText };
type McqText = { q: string; options: string[]; why: string };
type TfText = { q: string; why: string };
```

`TopicFile` gets `quiz?: QuizQuestion[]`. The schema (`strictObject`, plain
text with `PlainTextSchema`) rejects:
- an `mcq` with fewer than 2 or more than 6 options;
- an `mcq` whose `en` and `bn` have different option counts;
- an `mcq` whose `answer` is not an index of its options;
- two questions with the same `id` in one topic;
- an empty `quiz` list (omit the key instead).

## 2. Pure code (`src/lib/quiz.ts`, no React, no `@/` imports)

- `QUIZ_SCORES_STORAGE_KEY = "quiz-scores"`.
- `type QuizScores = Record<string, { best: number; total: number }>`.
- `scoreQuiz(questions, answers): { correct: number; total: number }`.
  `answers` maps a question id to the chosen option index (`mcq`) or
  boolean (`tf`). A missing answer is wrong.
- `parseScores(raw: string | null): QuizScores`. Bad text, a non-object, or
  an entry that is not `{ best, total }` of whole numbers with
  `0 <= best <= total` gives no entry for it.
- `recordBest(scores, slug, correct, total): QuizScores`. It returns a new
  object. It sets the entry when there is none, when `total` changed (the
  owner edited the quiz), or when `correct` is higher than `best`.
  Otherwise it keeps the old entry.

## 3. Store (`src/components/progress/`)

`createKeyStore` in `useProgress.ts` is generalized to
`createStore<T>({ storageKey, eventName, parse, serialize, empty, isEmpty })`
in a new file `createStore.ts`. It keeps the same cache by raw text, the same
`storage` event rule, and the same blocked-storage handling. `useProgress.ts`
builds the progress and bookmark stores from it with no change of behavior.
A third store holds the quiz scores. New exports: `useQuizScores()` and
`saveQuizScore(slug, correct, total)`.

## 4. Quiz box (`src/components/content/QuizSection.tsx`, client)

- Props: `{ slug: string; questions: QuizQuestion[]; lang: Lang }`.
- It renders on the topic page between the sections and the Sources, only
  when `topic.quiz` exists. Its root has `id="quiz"` and a heading.
- One `fieldset` with a `legend` for each question. Radio buttons for
  options. For `tf` the options are `UI.quizTrue` and `UI.quizFalse`.
- "Check answers" is disabled until every question has an answer. A hint
  says so.
- After the check: radios are disabled; each question shows "Correct" or
  "Not quite", the right answer, and the `why` text; the box shows the score
  "4 / 5" and the best score; the score is saved with `saveQuizScore`.
- "Try again" clears the answers and the check, keeps the best score.
- Result text is not color alone: it has a word and a mark (✓ or ✗).

## 5. Topic header and dashboard

- `TopicHeader`: when the topic has a quiz, add a pill "📝 5 questions" and
  a "Go to quiz" link (to `#quiz`) in the action bar, next to "Mark as read".
- Dashboard Part card: a new client leaf `QuizBest({ slug, total, lang })`
  shows "Quiz best: 4/5" when a saved score for `slug` has the same `total`.
  The Part card passes it only for topics that have a quiz.

## 6. i18n (both languages, `src/lib/i18n.ts`)

`quizTitle`, `quizIntro(n)`, `quizCheck`, `quizAnswerAll`, `quizRetry`,
`quizScore(correct, total)`, `quizBest(correct, total)`, `quizCorrect`,
`quizWrong`, `quizRightAnswer`, `quizTrue`, `quizFalse`, `quizQuestions(n)`,
`goToQuiz`. Numbers go through `fmtNum`.

## 7. Owner guide (`docs/quizzes.md`)

The format with one `mcq` and one `tf` example, the schema rules, and where
to put the list in a topic file. No questions for a real topic.

## Out of scope

- Real questions (the owner writes them).
- A quiz for the interview page, timers, a leaderboard, and sync between
  devices.

## Testing

- `tests/quiz.test.ts`: `scoreQuiz` (all right, all wrong, a missing answer,
  a boolean answer); `parseScores` (bad JSON, wrong shape, `best > total`,
  a valid entry); `recordBest` (first score, higher score, lower score keeps
  the best, changed `total` replaces the entry, input is not changed).
- `tests/content-schema.test.ts`: a topic with a valid quiz parses; each
  rejection in section 1 throws.
- Existing tests stay green after the store change. A browser check shows
  that progress and bookmarks still persist.
- With a temporary sample quiz (not committed): answer, check, score, retry,
  reload keeps the best; dashboard shows "Quiz best". A topic without a quiz
  shows no quiz UI.
- `npm run lint`, `npm test`, `npm run build` pass. Screenshots in light and
  dark, 1440px and 375px, English and Bangla.
