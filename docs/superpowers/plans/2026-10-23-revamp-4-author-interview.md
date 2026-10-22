# Revamp 4: Author Section and Interview Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Author section to the home page and an Interview page with 42 questions (3 for each of the 14 Parts).

**Architecture:** Interview data is one JSON file checked by a zod schema and a pure `interviewProblems` function. The page is a server component. The Author block is a small server component on the home page.

**Tech Stack:** Next.js 16.4 (read `node_modules/next/dist/docs/` before Next-specific code), React 19.3, Tailwind 4, zod 4, `node --test`.

**Spec:** `docs/superpowers/specs/2026-10-23-revamp-4-author-interview-design.md`

## Global Constraints

- All new text goes into both `en` and `bn` in `src/lib/i18n.ts`.
- Interview text is plain text. Each answer is short (2 to 4 sentences) and must come from the section it links to. No facts that the section does not support.
- The Author block has the name "Nuruddin Kawsar" and the GitHub link only: no photo, no bio.
- Page links end with a slash: `/interview/` and `/bn/interview/`.
- No new dependencies. No new CSS files. Use existing tokens.
- Work on branch `feat/revamp-3-4`.

## Review Focus

- An interview answer that the linked section does not support (a wrong fact in new content) — the reviewer spot-checks at least 6 of the 42 against the section text (Task 4).
- A `section` id that does not exist in its topic must fail the test and the build (Task 1 test, Task 4 real-file test).
- A Part with 2 or 4 questions, or Parts out of order, must fail the test (Task 1 tests).
- The Bangla header with 4 links plus the Start button at 1024px to 1280px must not overflow or wrap (Task 6 check).
- `<details>` must work with the keyboard and have no JavaScript need (Task 5 check).

---

### Task 1: Interview schema and checker

**Files:**
- Create: `src/lib/interview.ts`
- Test: `tests/interview.test.ts`

**Interfaces:**
- Produces: `InterviewFileSchema` (zod), `type InterviewFile`, and `interviewProblems(file: InterviewFile, topics: { slug: string; sectionIds: string[] }[]): string[]` (`topics` in Part order).

- [ ] **Step 1: Write the failing tests** in `tests/interview.test.ts` with a sample of 2 topics (`a` with sections `s1`,`s2`; `b` with `s1`). A helper builds an item for a section. Names exact:
  - `interviewProblems is empty for a good file` (3 items for each of the 2 Parts).
  - `interviewProblems reports a missing Part`, `... a Part out of order`, `... a Part with 2 items`, `... a Part with 4 items`, `... an unknown section`, `... an unknown topic` — each asserts the list has exactly one message and that it contains the topic slug.
  - `InterviewFileSchema rejects an empty question` and `InterviewFileSchema rejects an unknown key`.
- [ ] **Step 2: Run** `npm test` — expected: FAIL, `../src/lib/interview.ts` not found.
- [ ] **Step 3: Implement** the schema (`strictObject`s, plain non-empty text like `PlainTextSchema` in `content-schema.ts`) and `interviewProblems` to spec section 2. No `@/` imports.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Commit** `feat: add the interview schema and checker`.

### Task 2: i18n keys and links

**Files:**
- Modify: `src/lib/i18n.ts`
- Test: `tests/i18n.test.ts`

**Interfaces:**
- Produces: `interviewHref(lang: Lang): string`, `AUTHOR_GITHUB_URL: string` (`"https://github.com/kawsar-95"`), and i18n keys (en / bn): `interview` "Interview" / "ইন্টারভিউ"; `interviewTitle` "Interview questions" / "ইন্টারভিউ প্রশ্ন"; `interviewIntro` "Three questions for each part, with a short answer. Open a question to see it, and follow the link to read the full section." / "প্রতিটি part-এর তিনটি প্রশ্ন, ছোট উত্তরসহ। প্রশ্ন খুললে উত্তর দেখা যাবে, পুরো section পড়তে link-এ যাও।"; `readSection` "Read the section →" / "Section পড়ো →"; `authorEyebrow` "Author" / "লেখক"; `authorBy` "Built and maintained by" / "যিনি বানিয়েছেন ও দেখভাল করেন"; `authorGithub` "GitHub ↗" / "GitHub ↗".

- [ ] **Step 1: Write the failing test** in `tests/i18n.test.ts`: `interviewHref and the language switch agree` (the same four assertions as `dashboardHref`, with `/interview/` and `/bn/interview/`).
- [ ] **Step 2: Run** `npm test` — expected: FAIL, `interviewHref` is not exported.
- [ ] **Step 3: Implement** `interviewHref` next to `dashboardHref`, `AUTHOR_GITHUB_URL` next to `REPO_URL`, and add the keys to both dicts.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Commit** `feat: add the interview link helper and the author and interview text`.

### Task 3: Author section

**Files:**
- Modify: `src/components/pages/HomePage.tsx`

**Interfaces:**
- Consumes: `AUTHOR_GITHUB_URL`, `UI.authorEyebrow`, `UI.authorBy`, `UI.authorGithub` (Task 2).

- [ ] **Step 1: Implement** `Author({ lang })` (non-exported) in `HomePage.tsx` per spec section 1, and render it after `<Parts lang={lang} />`. Section: `aria-labelledby`, `border-t border-border`, container like `Features`. Name in `font-display` heading; link `rel="noopener noreferrer" target="_blank"`.
- [ ] **Step 2: Run** `npm run lint` and `npm run build` — expected: pass; `grep -c 'github.com/kawsar-95"' out/index.html out/bn/index.html` shows 1 or more in each (the repo link is a different URL).
- [ ] **Step 3: Commit** `feat: add the author section to the home page`.

### Task 4: Interview content (42 questions)

**Files:**
- Create: `src/content/interview.json`
- Test: `tests/interview.test.ts`

**Interfaces:**
- Consumes: `InterviewFileSchema`, `interviewProblems` (Task 1).

- [ ] **Step 1: Write the failing real-file test** in `tests/interview.test.ts`: `the real interview file has no problems` reads `src/content/interview.json` with `fs`, parses it with `InterviewFileSchema`, builds `topics` by reading the 14 topic files in this order — `llm-fundamentals`, `prompt-engineering`, `context-engineering`, `rag-knowledge-systems`, `agents-and-agentic-systems`, `tool-use-and-integrations`, `inference`, `llmops-and-observability`, `evaluation-engineering`, `cost-and-performance-optimization`, `safety-security-and-guardrails`, `multimodal-engineering`, `ai-application-architecture`, `visual-learning-resources` — (slug and `sections[].id`), and asserts `interviewProblems(...)` is `[]`.
- [ ] **Step 2: Run** `npm test` — expected: FAIL, the file does not exist.
- [ ] **Step 3: Write `interview.json`.** For each Part, read the topic file's section text (title, `body`, `layman`, `bangla` blocks) and write 3 questions that an interviewer could ask about that Part, each tied to one `section` id. Answer in 2 to 4 sentences, in English and in Bangla, using only facts the section states. Match the Bangla style of the site (Bangla sentences with English technical terms). Several topics may be drafted in parallel by helper agents; each helper returns only its Part entries, and the whole file is assembled in Part order.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Spot-check** at least 6 answers against their sections (a mix of Parts and both languages). Fix any answer that the section does not support.
- [ ] **Step 6: Commit** `feat: add 42 interview questions with English and Bangla answers`.

### Task 5: Interview page and routes

**Files:**
- Create: `src/components/pages/InterviewPage.tsx`, `src/app/(en)/interview/page.tsx`, `src/app/bn/interview/page.tsx`

**Interfaces:**
- Consumes: `InterviewFileSchema`, `interviewProblems` (Task 1), `src/content/interview.json` (Task 4), `TOPICS`, `topicText` from `@/lib/topics`, `topicHref`, `fmtNum`, `UI` keys (Task 2).

- [ ] **Step 1: Implement `InterviewPage({ lang })`** to spec section 3. At module load or in the render, parse the JSON with `InterviewFileSchema` and run `interviewProblems` against `TOPICS` (`slug`, section ids); throw an `Error` joining the messages if any. Layout: the Contents page header style, `max-w-4xl`; one card for each Part (`rounded-2xl border border-border bg-bg-raised p-6 shadow-card`) with the Part number and linked title; each question a `<details>` with a styled `<summary>` (`cursor-pointer`, visible focus ring), the answer paragraph, and the `readSection` link.
- [ ] **Step 2: Add the two route files** like `src/app/(en)/dashboard/page.tsx` with `metadata.title` from `UI[lang].interviewTitle`.
- [ ] **Step 3: Run** `npm run lint`, `npm test`, `npm run build` — expected: pass; `grep -o '<details' out/interview/index.html | wc -l` and the same for `out/bn/interview/index.html` print 42.
- [ ] **Step 4: Browser check** with Playwright: click a question, the answer shows; press Enter on a focused summary, it toggles; the "Read the section" link goes to an existing section anchor (`/topics/<slug>/#<id>` loads and the id exists in the page).
- [ ] **Step 5: Commit** `feat: add the interview page`.

### Task 6: Navigation links

**Files:**
- Modify: `src/components/layout/SiteHeader.tsx`, `src/components/layout/MobileNav.tsx`, `src/components/layout/SiteShell.tsx`

**Interfaces:**
- Consumes: `interviewHref`, `UI.interview` (Task 2).

- [ ] **Step 1:** Add the "Interview" link after "Dashboard" in the header `nav`, in the mobile menu (same style as the Dashboard link, `mt-2`), and in the footer site list.
- [ ] **Step 2: Run** `npm run lint` and `npm run build`; take header screenshots of `/bn/` at 1024, 1100, 1280, and 1440px and `/` at 1024px; check for overflow (`document.documentElement.scrollWidth > innerWidth`) and wrapped text. If the links crowd the bar, show the header "Interview" link from `xl` only (`hidden xl:inline-flex`) and keep the mobile and footer links; repeat the check.
- [ ] **Step 3: Commit** `feat: link the interview page from the header, menu, and footer`.

### Task 7: Visual check

- [ ] **Step 1:** `npm run build`, serve `out/`, and take screenshots with Playwright: the home page Author section and the interview page (one question opened); light and dark, 1440px and 375px, English and Bangla. Read them. Fix what looks wrong.
- [ ] **Step 2:** Show the screenshots to the owner in the PR. Ask the owner to review the 42 questions and answers.
