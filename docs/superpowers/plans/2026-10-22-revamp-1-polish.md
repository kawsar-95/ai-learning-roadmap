# Revamp 1: Polish the Look Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the header, topic header, sidebar, and sections match systemdesignbangla.com.

**Architecture:** Edit existing components with the existing Tailwind tokens. Two new pure functions (`readingMinutes`, `setKeys`) carry the only new logic; both live in files that `node --test` already imports.

**Tech Stack:** Next.js 16.4 (read `node_modules/next/dist/docs/` before Next-specific code), React 19.3, Tailwind 4, `node --test`.

**Spec:** `docs/superpowers/specs/2026-10-22-revamp-1-polish-design.md`

## Global Constraints

- All new text goes into both `en` and `bn` dicts in `src/lib/i18n.ts`. Numbers shown to the reader go through `fmtNum(lang, n)`.
- No new dependencies. No new CSS files. Use existing tokens (`bg-bg-raised-2`, `border-border`, `text-accent`, ...).
- No Dashboard, Interview, Author, Bookmark, or quiz UI in this plan.
- The header must not overflow at 375px width.

## Review Focus

- A topic with no `bangla` blocks on `/bn/`: reading time must still show at least 1 min (Task 1 test: empty list gives 1).
- Mark as read when some sections are already done: one click marks all done, it must not toggle the done ones off (Task 2 test).
- Mark as read must not touch progress keys of other topics (Task 2 test).
- Storage blocked (private mode): the button must not throw; `write()` in `useProgress.ts` already catches. Keep `setDone` going through `write()`.
- Header at 375px with the new button: the button is `hidden sm:inline-flex` (Task 4 manual check).

---

### Task 1: `readingMinutes`

**Files:**
- Modify: `src/lib/search.ts` (add next to `blockText`)
- Test: `tests/search.test.ts`

**Interfaces:**
- Produces: `readingMinutes(blocks: Block[], strip: (html: string) => string): number`

- [ ] **Step 1: Write the failing tests** in `tests/search.test.ts` (reuse the file's `strip`):

```ts
test("readingMinutes gives at least 1 minute", () => {
  assert.equal(readingMinutes([], strip), 1);
  assert.equal(readingMinutes([{ type: "paragraph", html: "<b>one</b> two" }], strip), 1);
});

test("readingMinutes counts 200 words per minute", () => {
  const html = Array(600).fill("word").join(" ");
  assert.equal(readingMinutes([{ type: "paragraph", html }], strip), 3);
});
```

- [ ] **Step 2: Run** `npm test` — expected: FAIL, `readingMinutes` is not exported.
- [ ] **Step 3: Implement** `readingMinutes`: join `blockText` of every block, count runs of non-space characters (`/\S+/g`), return `Math.max(1, Math.round(words / 200))`.
- [ ] **Step 4: Run** `npm test` — expected: PASS.
- [ ] **Step 5: Commit** `feat: add a reading-time helper`.

### Task 2: `setKeys`, `setDone`, and the Mark-as-read button

**Files:**
- Modify: `src/lib/progress.ts` (next to `toggleKey`)
- Modify: `src/components/progress/useProgress.ts` (next to `toggleDone`)
- Modify: `src/components/progress/ProgressWidgets.tsx` (next to `SectionDoneButton`)
- Modify: `src/lib/i18n.ts` (both dicts)
- Test: `tests/progress.test.ts`

**Interfaces:**
- Produces: `setKeys(done: ReadonlySet<string>, keys: string[], value: boolean): Set<string>`
- Produces: `setDone(keys: string[], value: boolean): void`
- Produces: `<TopicDoneButton keys={string[]} lang={Lang} />`
- Produces i18n keys: `markRead` ("Mark as read" / "পড়া হয়েছে, চিহ্ন দাও"), `markedRead` ("Read" / "পড়া হয়েছে").

- [ ] **Step 1: Write the failing tests** in `tests/progress.test.ts`:

```ts
test("setKeys adds every key and keeps other topics", () => {
  const next = setKeys(new Set(["rag/s1", "inference/s1"]), ["inference/s1", "inference/s2"], true);
  assert.deepEqual([...next].sort(), ["inference/s1", "inference/s2", "rag/s1"]);
});

test("setKeys removes every key and keeps other topics", () => {
  const next = setKeys(new Set(["rag/s1", "inference/s1", "inference/s2"]), ["inference/s1", "inference/s2"], false);
  assert.deepEqual([...next], ["rag/s1"]);
});
```

- [ ] **Step 2: Run** `npm test` — expected: FAIL, `setKeys` is not exported.
- [ ] **Step 3: Implement** `setKeys` (copy the set, add or delete each key). Add `setDone(keys, value)` that calls `write(setKeys(getSnapshot(), keys, value))`.
- [ ] **Step 4: Implement** `TopicDoneButton`: `allDone = keys.every(k => progress.has(k))`; `onClick={() => setDone(keys, !allDone)}`; `aria-pressed={allDone}`; label `✓ {allDone ? ui.markedRead : ui.markRead}`. Same classes as `SectionDoneButton`, except the done state is `border-accent text-accent bg-bg-raised` (accent text, not a filled button).
- [ ] **Step 5: Run** `npm test` and `npm run lint` — expected: PASS.
- [ ] **Step 6: Commit** `feat: mark a whole topic as read`.

### Task 3: Topic header pills and action bar

**Files:**
- Modify: `src/components/content/TopicHeader.tsx`
- Modify: `src/lib/i18n.ts` (both dicts)

**Interfaces:**
- Consumes: `readingMinutes` (Task 1), `stripTags` from `src/lib/topics.ts`, `TopicDoneButton` (Task 2), `progressKey` from `src/lib/progress.ts`.
- Produces i18n key: `minRead: (n: string) => string` — `` `${n} min read` `` / `` `${n} মিনিট পড়া` ``.

- [ ] **Step 1:** Replace the mono eyebrow with a flex row of two pills (`rounded-full bg-bg-raised-2 px-3 py-1 text-[13px] text-text-dim`):
  - `` `${ui.part(fmtNum(lang, topic.part))} · ${text.title}` ``
  - `📖 {ui.minRead(fmtNum(lang, minutes))}`, where `minutes = readingMinutes(topic.sections.flatMap(s => lang === "bn" ? s.bangla : s.body), stripTags)`.
- [ ] **Step 2:** Delete the `topicMeta` chip. Delete `topicMeta` from both dicts if nothing else uses it (`grep -rn topicMeta src`).
- [ ] **Step 3:** Below the lede add `<div className="mt-6 flex flex-wrap gap-2 border-y border-border py-4">` holding `<TopicDoneButton keys={topic.sections.map(s => progressKey(topic.slug, s.id))} lang={lang} />`.
- [ ] **Step 4: Run** `npm run lint` and `npm run build` — expected: PASS.
- [ ] **Step 5: Commit** `feat: show reading time and a mark-as-read bar on topic pages`.

### Task 4: Header

**Files:**
- Modify: `src/components/layout/SiteHeader.tsx`

**Interfaces:**
- Consumes: `TOPICS` from `src/lib/topics.ts`, `topicHref` and `UI.startReading` from `src/lib/i18n.ts`.

- [ ] **Step 1:** Change the inner `div` to `mx-auto flex h-full max-w-6xl items-center gap-2 px-4 sm:px-6` (same as the home page container).
- [ ] **Step 2:** After `<ThemeToggle>`, add a `Link` to `topicHref(TOPICS[0].slug, lang)` with text `UI[lang].startReading`, classes `ml-1 hidden items-center rounded-lg bg-accent px-4 py-2 text-[14px] font-semibold text-on-accent no-underline shadow-card transition hover:-translate-y-0.5 sm:inline-flex`.
- [ ] **Step 3: Run** `npm run build`, serve `out/` (`python3 -m http.server 4173 -d out`), and screenshot `/` at 1440px and 375px with `google-chrome --headless=new --window-size=375,900 --screenshot=...`. Expected: no horizontal scroll at 375px; the button shows at 1440px only.
- [ ] **Step 4: Commit** `feat: center the header and add a start-reading button`.

### Task 5: Sidebar and section rules

**Files:**
- Modify: `src/components/layout/SidebarList.tsx`
- Modify: `src/components/pages/TopicPage.tsx`
- Modify: `src/components/content/SectionView.tsx`

- [ ] **Step 1 (sidebar):** In `TopicPage`, remove `border-r border-border` from the left `aside`. In `SidebarList`, the active class becomes `border-accent bg-bg-raised-2`; the hover class becomes `hover:border-border-strong hover:bg-bg-raised-2/60`.
- [ ] **Step 2 (sections):** In `SectionView`, delete the `<p>` that shows `section.num`, and drop `mt-2` from the `h2`. In `TopicPage`, change the sections wrapper from `space-y-16 sm:space-y-20` to `divide-y divide-border [&>section]:py-12 sm:[&>section]:py-14 [&>section:first-child]:pt-0`. (One wrapper class gives the rule above every section except the first.)
- [ ] **Step 3: Run** `npm run lint`, `npm test`, `npm run build` — expected: all PASS.
- [ ] **Step 4: Commit** `feat: soften the sidebar and rule between sections`.

### Task 6: Visual check

- [ ] **Step 1:** Serve `out/`. Screenshot `/`, `/topics/inference/`, and `/bn/topics/inference/` at 1440px and 375px, in light and dark mode. For dark mode, add `--force-dark-mode` to the chrome command; with no saved choice the site follows the device.
- [ ] **Step 2:** Show the screenshots to the owner next to the reference screenshots. Fix what the owner rejects before the branch is finished.
