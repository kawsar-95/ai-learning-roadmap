# Revamp 4 of 4: author section and interview page

Date: 2026-10-23. Status: design approved by the owner in chat ("yes").

## Goal

Add an Author section to the home page and an Interview page of 42
questions, like the author block and the interview page at
https://www.systemdesignbangla.com/. Copy the idea only, not that site's
text or brand.

## Decisions

| Topic | Decision |
|---|---|
| Author content | Name "Nuruddin Kawsar" and a GitHub link (`https://github.com/kawsar-95`). No photo and no bio. The name is the same in both languages. |
| Interview content | 3 questions for each of the 14 Parts, 42 in total, written from the topic text. |
| Interview answers | Short, English and Bangla, plain text. Each links to the section it comes from. |
| Routes | `/interview/` and `/bn/interview/`. |

## 1. Author section (`src/components/pages/HomePage.tsx`)

- A new `Author({ lang })` block at the end of `HomePage`, after `Parts`.
- Same container as the other sections (`max-w-6xl`, `px-4 sm:px-6`).
- Content: eyebrow `UI.authorEyebrow` ("Author" / "লেখক"), the name as a
  heading, a line `UI.authorBy` ("Built and maintained by" / "যিনি বানিয়েছেন ও
  দেখভাল করেন"), and a link `UI.authorGithub` ("GitHub ↗") with
  `target="_blank" rel="noopener noreferrer"`.
- The GitHub URL is a constant `AUTHOR_GITHUB_URL` in `src/lib/i18n.ts`
  next to `REPO_URL`.

## 2. Interview data (`src/content/interview.json`, `src/lib/interview.ts`)

```json
{ "parts": [ { "topic": "<slug>", "items": [
  { "section": "<section id>",
    "en": { "q": "...", "a": "..." },
    "bn": { "q": "...", "a": "..." } } ] } ] }
```

`src/lib/interview.ts` (no React, no `@/` imports) exports:
- `InterviewFileSchema` (zod, `strictObject`, plain text, non-empty).
- `interviewProblems(file, topics): string[]` where
  `topics: { slug: string; sectionIds: string[] }[]` is in Part order. It
  returns one message for each problem: a Part missing, repeated, or out of
  order; a Part without exactly 3 items; a `section` that is not in that
  topic. An empty list means the file is good.

## 3. Interview page

- New `src/components/pages/InterviewPage.tsx` (server component) and
  routes `src/app/(en)/interview/page.tsx`, `src/app/bn/interview/page.tsx`
  with `metadata.title` from `UI[lang].interviewTitle`.
- `interviewHref(lang)` in `src/lib/i18n.ts`: `/interview/` and
  `/bn/interview/` (trailing slash, like `contentsHref`).
- Header (eyebrow, title, intro) like the Contents page.
- One block for each Part, in Part order: Part number, Part title (links to
  the topic), then its 3 questions. Each question is a `<details>` with the
  question in `<summary>`; the opened part shows the answer and a link
  "Read the section →" to `${topicHref(slug, lang)}/#${section}`.
- The page parses the file with `InterviewFileSchema` at build time and calls
  `interviewProblems`; a problem fails the build with the messages.

## 4. Navigation

- "Interview" link in the header (after "Dashboard"), the mobile menu, and
  the footer site list. Texts: `UI.interview` ("Interview" / "ইন্টারভিউ").
- Check the Bangla header at 1024px to 1280px. If the links crowd the bar,
  show the "Interview" link from 1280px (`xl`) and keep the mobile menu link.

## Out of scope

- Author photo, bio, and other links; an About page.
- Interview search, filters, and progress.

## Testing

- `tests/interview.test.ts`:
  - `interviewProblems` is empty for a good sample and reports each of:
    missing Part, wrong order, 2 items, 4 items, unknown section.
  - `InterviewFileSchema` rejects an empty `q` and an unknown key.
  - The real `src/content/interview.json` (read with `fs`, with the slugs
    and section ids read from the 14 topic files in the order of
    `TOPIC_ORDER`) has no problems.
- `tests/i18n.test.ts`: `interviewHref` for both languages, and the language
  switch maps one to the other.
- `npm run lint`, `npm test`, `npm run build` pass. The build output has
  `out/interview/index.html` and `out/bn/interview/index.html`, each with 42
  `<details>`.
- Screenshots of the home page Author section and the interview page in
  light and dark, 1440px and 375px, English and Bangla. The Bangla header is
  checked at 1024px, 1100px, and 1280px.
- Owner review (in the PR): the 42 questions and answers, because they are
  new content. Each names its section, so a reader can check the answer.
