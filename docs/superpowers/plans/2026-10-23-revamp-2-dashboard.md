# Revamp 2: Dashboard With Bookmarks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/dashboard` page (Continue card, 14 Part cards, bookmark list) and a per-section Bookmark button.

**Architecture:** One generic key-set store in `useProgress.ts` serves both progress and bookmarks, each with its own localStorage key. The dashboard page is a server component. Only the two blocks that read localStorage (Continue card, bookmark list) are client components. The pure logic (`resolveBookmarks`, `dashboardHref`) lives in files that `node --test` imports.

**Tech Stack:** Next.js 16.4 (read `node_modules/next/dist/docs/` before Next-specific code), React 19.3, Tailwind 4, `node --test`.

**Spec:** `docs/superpowers/specs/2026-10-23-revamp-2-dashboard-design.md`

## Global Constraints

- All new text goes into both `en` and `bn` dicts in `src/lib/i18n.ts` (`const bn: Dict = typeof en` makes `tsc` enforce matching keys). Numbers shown to the reader go through `fmtNum(lang, n)`.
- Bookmark key format: `<topic slug>/<section id>`, built with `progressKey`. localStorage key: `bookmarks`. It must differ from `progress`.
- The Bookmark button label is fixed (`UI.bookmark`). Only the icon changes. State is in `aria-pressed`.
- Storage blocked: nothing is saved and nothing throws.
- No new dependencies. No new CSS files. Use existing tokens.
- Page links end with a slash, as `contentsHref` does: `/dashboard/` and `/bn/dashboard/`.
- Work on branch `feat/revamp-2-dashboard`.

## Review Focus

- A stored bookmark for a section that no longer exists must not show on the dashboard (Task 1 test).
- The `bookmarks` and `progress` keys must never mix: bookmarking must not mark a section done, and marking done must not bookmark it (Task 1 test on the keys; Task 2 manual check).
- All sections done: the Continue card shows `UI.allDone`, not a broken link (Task 4 manual check with a full progress list).
- Corrupt `bookmarks` text in localStorage (not JSON, or JSON that is not a list): the dashboard shows the empty state. `parseProgress` already returns an empty set; Task 1 pins it for the bookmarks key.
- The language switch on `/dashboard/` must go to `/bn/dashboard/` and back (Task 1 test).
- A change in another tab must update this tab: each store listens to the `storage` event of its own key only (Task 2 manual check with two tabs).

---

### Task 1: Pure pieces (`resolveBookmarks`, bookmark key, `dashboardHref`)

**Files:**
- Modify: `src/lib/progress.ts`, `src/lib/i18n.ts`
- Test: `tests/progress.test.ts`, `tests/i18n.test.ts`

**Interfaces:**
- Produces: `BOOKMARKS_STORAGE_KEY: string` (`"bookmarks"`) in `src/lib/progress.ts`.
- Produces: `resolveBookmarks(stored: ReadonlySet<string>, order: readonly string[]): string[]` in `src/lib/progress.ts`. It returns the keys of `order`, in `order`, that are in `stored`.
- Produces: `dashboardHref(lang: Lang): string` in `src/lib/i18n.ts`: `"/dashboard/"` for `en`, `"/bn/dashboard/"` for `bn`.

- [ ] **Step 1: Write the failing tests.** In `tests/progress.test.ts` (add the two imports):

```ts
test("resolveBookmarks keeps reading order and drops unknown keys", () => {
  const stored = new Set(["rag/s2", "gone/s9", "inference/s1"]);
  assert.deepEqual(resolveBookmarks(stored, ["inference/s1", "rag/s1", "rag/s2"]), ["inference/s1", "rag/s2"]);
});

test("resolveBookmarks gives an empty list for no bookmarks", () => {
  assert.deepEqual(resolveBookmarks(new Set(), ["inference/s1"]), []);
});

test("the bookmarks and progress storage keys differ", () => {
  assert.equal(BOOKMARKS_STORAGE_KEY, "bookmarks");
  assert.notEqual(BOOKMARKS_STORAGE_KEY, PROGRESS_STORAGE_KEY);
});

test("parseProgress reads corrupt bookmark text as an empty set", () => {
  assert.equal(parseProgress("{not json").size, 0);
  assert.equal(parseProgress('{"a":1}').size, 0);
});
```

  In `tests/i18n.test.ts` (add `dashboardHref` to the import):

```ts
test("dashboardHref and the language switch agree", () => {
  assert.equal(dashboardHref("en"), "/dashboard/");
  assert.equal(dashboardHref("bn"), "/bn/dashboard/");
  assert.equal(localizedPath(dashboardHref("en"), "bn"), dashboardHref("bn"));
  assert.equal(localizedPath(dashboardHref("bn"), "en"), dashboardHref("en"));
});
```

- [ ] **Step 2: Run** `npm test` — expected: FAIL, the new names are not exported.
- [ ] **Step 3: Implement** the three exports. `resolveBookmarks` is a filter of `order` by `stored.has`. `dashboardHref` sits next to `contentsHref`.
- [ ] **Step 4: Run** `npm test` — expected: PASS (existing tests plus the 5 new ones).
- [ ] **Step 5: Commit** `feat: add the bookmark key, resolveBookmarks, and dashboardHref`.

### Task 2: Generic key store

**Files:**
- Modify: `src/components/progress/useProgress.ts`

**Interfaces:**
- Consumes: `PROGRESS_STORAGE_KEY`, `BOOKMARKS_STORAGE_KEY`, `parseProgress`, `serializeProgress`, `setKeys`, `toggleKey` from `@/lib/progress`.
- Produces (new): `useBookmarks(): ReadonlySet<string>` and `toggleBookmark(key: string): void`.
- Produces (unchanged names and signatures): `useProgress`, `toggleDone`, `setDone(keys: string[], value: boolean)`, `resetProgress`.

This task changes no behavior of progress, so there is no failing test to write. The existing tests must stay green and Step 3 is a build and a manual check.

- [ ] **Step 1: Implement** a non-exported `createKeyStore(storageKey: string, eventName: string)` in `useProgress.ts`. It owns the cached raw text and set, `getSnapshot`, `subscribe` (the `storage` listener reacts only to `event.key === storageKey` or `null`), and `write` (same `try/catch`, then dispatches `eventName`). It returns `{ use, toggle, set, reset }`, where `use` wraps `useSyncExternalStore(subscribe, getSnapshot, () => EMPTY)`. Build the progress store with `("progress", "progress-change")` — keep the literal `PROGRESS_STORAGE_KEY` import, not a copy of the string — and the bookmark store with `(BOOKMARKS_STORAGE_KEY, "bookmarks-change")`. Re-export the five names above from the two stores. Keep the comments that explain the cache and the blocked storage.
- [ ] **Step 2: Run** `npm test`, `npm run lint`, and `npm run build` — expected: all pass; `grep -rn "useProgress\|toggleDone\|setDone\|resetProgress" src` shows no import that needs a change.
- [ ] **Step 3: Manual check** with `npm run dev`: open a topic, click "Mark as done" on a section, reload. Expected: it stays done, and `localStorage.progress` holds the key. (The Bookmark button comes in Task 3.)
- [ ] **Step 4: Commit** `refactor: share one key-set store between progress and bookmarks`.

### Task 3: Bookmark button

**Files:**
- Modify: `src/components/progress/ProgressWidgets.tsx`, `src/components/content/SectionView.tsx`, `src/lib/i18n.ts`

**Interfaces:**
- Consumes: `useBookmarks`, `toggleBookmark` (Task 2).
- Produces: `<BookmarkButton sectionKey={string} lang={Lang} />`.
- Produces i18n keys: `bookmark` ("Bookmark" / "বুকমার্ক").

- [ ] **Step 1: Add the key** `bookmark` to both dicts.
- [ ] **Step 2: Implement `BookmarkButton`** next to `SectionDoneButton`. Props `{ sectionKey: string; lang: Lang }`. `on = useBookmarks().has(sectionKey)`. A `<button type="button" aria-pressed={on} onClick={() => toggleBookmark(sectionKey)}>` with the same size and border classes as `SectionDoneButton`; the on state uses `border-accent text-accent`. The visible text is always `ui.bookmark`; the icon is `🔖` in both states, at full opacity when on and `opacity-40` when off.
- [ ] **Step 3: In `SectionView.tsx`**, change the footer `div` (the one holding `SectionDoneButton`) to `mt-8 flex flex-wrap items-center justify-end gap-2 border-t border-border pt-5` and render `<BookmarkButton sectionKey={doneKey} lang={lang} />` before `SectionDoneButton`. The bookmark key equals the progress key (`doneKey`), by design.
- [ ] **Step 4: Run** `npm run lint` and `npm run build` — expected: pass. Check `out/topics/inference/index.html` contains `aria-pressed="false"` on the Bookmark button.
- [ ] **Step 5: Manual check** with `npm run dev`: bookmark a section, reload; it stays bookmarked, `localStorage.bookmarks` holds the key, and `localStorage.progress` is unchanged.
- [ ] **Step 6: Commit** `feat: add a bookmark button to every section`.

### Task 4: Dashboard page

**Files:**
- Create: `src/components/progress/DashboardWidgets.tsx` (`"use client"`), `src/components/pages/DashboardPage.tsx`, `src/app/(en)/dashboard/page.tsx`, `src/app/bn/dashboard/page.tsx`
- Modify: `src/lib/i18n.ts`

**Interfaces:**
- Consumes: `useProgress`, `useBookmarks`, `toggleBookmark` (Task 2); `resolveBookmarks`, `firstUndone`, `progressKey` from `@/lib/progress`; `dashboardHref` (Task 1); `PartProgress` and `SectionLink` from `ProgressWidgets.tsx`; `TOPICS`, `topicText`, `sectionText` from `@/lib/topics`.
- Produces: `ContinueCard({ sections, lang })` where `sections: { key: string; href: string; title: string; partTitle: string }[]` in reading order.
- Produces: `BookmarkList({ sections, lang })` with the same `sections` shape.
- Produces i18n keys (en / bn):
  - `dashboard`: "Dashboard" / "ড্যাশবোর্ড"
  - `dashboardTitle`: "Your dashboard" / "তোমার ড্যাশবোর্ড"
  - `dashboardIntro`: "Where you stopped, how far each part is, and the sections you saved." / "কোথায় থেমেছ, প্রতিটি part কতদূর, আর কোন section save করেছ।"
  - `bookmarksTitle`: "Bookmarks" / "বুকমার্ক"
  - `bookmarksEmpty`: "No bookmarks yet. Use the Bookmark button at the end of a section." / "এখনো কোনো বুকমার্ক নেই। কোনো section-এর শেষে Bookmark বোতাম চাপো।"
  - `removeBookmark`: "Remove" / "সরাও"
  - Existing keys reused: `continueReading`, `startReading`, `allDone`, `partsNav`, `contentsTitle`.

- [ ] **Step 1: Add the i18n keys** above to both dicts.
- [ ] **Step 2: Implement `DashboardWidgets.tsx`.**
  - `ContinueCard`: `next = firstUndone(useProgress(), sections.map(s => s.key))`. If `next` is null, show `ui.allDone` and a link to `contentsHref(lang)`. Otherwise show the section title, the Part title, and a teal button to its `href` (text `ui.startReading` when nothing is done, else `ui.continueReading`).
  - `BookmarkList`: `keys = resolveBookmarks(useBookmarks(), sections.map(s => s.key))`. If empty, show `ui.bookmarksEmpty`. Otherwise a `divide-y` list; each row links to the section and has a "Remove" button calling `toggleBookmark(key)`.
- [ ] **Step 3: Implement `DashboardPage({ lang })`** as a server component with the Contents page header style and `max-w-4xl` container. It builds the `sections` array from `TOPICS` (key `progressKey(topic.slug, section.id)`, href `` `${topicHref(topic.slug, lang)}/#${section.id}` ``, titles via `sectionText` and `topicText`). Blocks in order: `ContinueCard`; a grid (`grid gap-4 sm:grid-cols-2 lg:grid-cols-3`) of 14 `<Link>` cards with the Part number, the Part title, and `<PartProgress keys={...} lang={lang} />`; then a `bookmarksTitle` heading and `BookmarkList`. Card class: `rounded-2xl border border-border bg-bg-raised p-5 shadow-card`.
- [ ] **Step 4: Add the two route files** like `src/app/(en)/contents/page.tsx`: `metadata = { title: UI.<lang>.dashboardTitle }` and a default export that renders `<DashboardPage lang="<lang>" />`.
- [ ] **Step 5: Run** `npm run lint`, `npm test`, `npm run build` — expected: all pass, and `out/dashboard/index.html` and `out/bn/dashboard/index.html` exist.
- [ ] **Step 6: Manual check** with `npm run dev` at `/dashboard/`: with no data, the Continue button says "Start reading" and the bookmark list shows the empty state. Bookmark two sections: both rows appear in reading order, and "Remove" removes one. Set `localStorage.bookmarks = "{bad"` and reload: the empty state shows. Mark all sections done from the Contents page: the Continue card shows `allDone`.
- [ ] **Step 7: Commit** `feat: add the dashboard page`.

### Task 5: Navigation links

**Files:**
- Modify: `src/components/layout/SiteHeader.tsx`, `src/components/layout/MobileNav.tsx`, `src/components/layout/SiteShell.tsx`

**Interfaces:**
- Consumes: `dashboardHref`, `UI.dashboard` (Tasks 1 and 4).

- [ ] **Step 1: Header.** After the "Contents" `Link` in the `nav`, add a `Link` to `dashboardHref(lang)` with `className={NAV_LINK}` and text `UI[lang].dashboard`.
- [ ] **Step 2: Mobile menu.** Next to the existing Contents link block in `MobileNav.tsx`, add the same style of link to `dashboardHref(lang)` (text `ui.dashboard`) that closes the menu on click.
- [ ] **Step 3: Footer.** In the site list of `SiteFooter` (`SiteShell.tsx`), add an `li` with a `Link` (`FOOTER_LINK`) to `dashboardHref(lang)`, between Contents and the source link.
- [ ] **Step 4: Run** `npm run lint` and `npm run build` — expected: pass. `grep -c 'href="/dashboard/"' out/index.html` is 2 or more (header and footer).
- [ ] **Step 5: Commit** `feat: link the dashboard from the header, menu, and footer`.

### Task 6: Visual check

- [ ] **Step 1:** `npm run build`, serve `out/` (`python3 -m http.server 4173 -d out`). Screenshot `/dashboard/` and `/bn/dashboard/` at 1440px and 375px, light and dark (`--force-dark-mode`), with no data and with some progress and 2 bookmarks. Headless Chrome cannot set `localStorage` from the command line, so for the "with data" shots use Playwright (installed in `/home/nuruddin-kawsar/Documents/hris-web-automation/node_modules`): `page.addInitScript` sets `progress` and `bookmarks` before the page loads.
- [ ] **Step 2:** Check the header at 640px and 768px in both languages (the "Dashboard" link must not wrap or push the Start button out; "ড্যাশবোর্ড" is the long one). Fix before finishing.
- [ ] **Step 3:** Show the screenshots to the owner. Fix what the owner rejects before the branch is finished.
