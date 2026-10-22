# Revamp 2 of 4: dashboard page with bookmarks

Date: 2026-10-23. Status: design approved by the owner in chat. Spec waits
for review.

## Goal

Add a Dashboard page that does not repeat the Contents page. The Contents
page already shows the totals, the percent, the progress bar, the
"Continue reading" link, the reset button, and the progress of each Part.
The Dashboard adds a "Continue" card, one card for each Part, and a list of
bookmarked sections.

Part of the revamp (see `2026-10-22-revamp-1-polish-design.md`). Sub-project
1 is merged. Sub-project 3 (quizzes) later adds a quiz card to this page.

## Decisions

| Topic | Decision |
|---|---|
| Page content | Continue card, 14 Part cards, bookmark list. The Contents page stays as it is. |
| Bookmark unit | A section, key `<topic slug>/<section id>` (same as progress). |
| Bookmark storage | localStorage key `bookmarks`, a JSON array of keys. Same format as progress. |
| Code reuse | The progress store logic moves into one function that takes the storage key and the event name. Progress and bookmarks both use it. Progress behavior does not change. |
| Languages | All new text goes into `en` and `bn` in `src/lib/i18n.ts`. Numbers go through `fmtNum`. |
| Routes | `/dashboard` and `/bn/dashboard`, static pages. The data comes from localStorage after hydration. |

## 1. Bookmark store

- `src/lib/progress.ts`: add `BOOKMARKS_STORAGE_KEY = "bookmarks"`. The pure
  helpers `parseProgress`, `serializeProgress`, `toggleKey`, and `setKeys`
  already work on any key list and stay as they are.
- `src/components/progress/useProgress.ts`: replace the module-level store
  with `createKeyStore(storageKey: string, eventName: string)`. It returns
  `{ use, toggle, set, reset }`. The cache by source text, the `storage`
  event handler, and the blocked-storage `try/catch` move into it without
  change. The file then exports:
  - `useProgress`, `toggleDone`, `setDone`, `resetProgress` (same names and
    signatures as now, built on `createKeyStore("progress", "progress-change")`).
  - `useBookmarks`, `toggleBookmark` (built on
    `createKeyStore(BOOKMARKS_STORAGE_KEY, "bookmarks-change")`).
- If storage is blocked, nothing is saved and nothing throws.

## 2. Bookmark button (`ProgressWidgets.tsx`, `SectionView.tsx`)

- New client component `BookmarkButton({ sectionKey, lang })`.
- It sits next to `SectionDoneButton` at the end of each section.
- The label is fixed: `UI.bookmark` ("Bookmark" / "বুকমার্ক"). Only the icon
  changes: 🔖 outline when off, filled when on. The state is in
  `aria-pressed`. A label that does not change keeps screen readers correct.
- Same size and border classes as `SectionDoneButton`. The on state uses
  `border-accent text-accent`.

## 3. Dashboard page

New files:
- `src/components/pages/DashboardPage.tsx` (server component, `lang` prop).
- `src/app/(en)/dashboard/page.tsx` and `src/app/bn/dashboard/page.tsx`,
  each with `metadata.title` from `UI[lang].dashboardTitle`, like the
  Contents routes.
- `dashboardHref(lang)` in `src/lib/i18n.ts`, next to `contentsHref`.

The page has a header (eyebrow, title, intro) and three blocks in this order.
The blocks that read localStorage are client components in
`src/components/progress/DashboardWidgets.tsx`.

**3a. Continue card** (`ContinueCard`)
- Props: the ordered list of `SectionLink` (key, href) for all sections, and
  the title of each section by key.
- Shows the first section that is not done (`firstUndone`), its title and
  Part, and a teal "Continue reading" button that links to it.
- If all sections are done, it shows `UI.allDone` and a link to the Contents
  page. If none is done, the button text is `UI.startReading`.

**3b. Part cards** (`PartCards`)
- A grid: 1 column below `sm`, 2 columns from `sm`, 3 from `lg`.
- One card for each of the 14 Parts. It shows the Part number, the title,
  the existing `PartProgress` bar, and "done / total sections". The whole
  card links to the topic page.
- Card style: `rounded-2xl border border-border bg-bg-raised p-5 shadow-card`,
  the same as the Contents page cards.

**3c. Bookmarks** (`BookmarkList`)
- Props: a lookup of every section by key: `{ href, title, partTitle }`.
- `resolveBookmarks(keys, order)` (pure, in `src/lib/progress.ts`) returns the
  stored keys that exist in `order`, in reading order. Unknown keys are
  dropped. Duplicates cannot occur (the store is a set).
- Each row: section title, Part title, link to `/<topic>/#<section id>`, and
  a "Remove" button that calls `toggleBookmark`.
- Empty state: `UI.bookmarksEmpty` ("No bookmarks yet. Use the Bookmark
  button at the end of a section.").

## 4. Navigation

- Add the "Dashboard" link to the header links (`SiteHeader.tsx`, after
  "Contents"), the mobile menu (`MobileNav.tsx`), and the footer site list
  (`SiteShell.tsx`).

## Out of scope

- Sync between devices, notes on bookmarks, and export of bookmarks.
- Quiz scores (sub-project 3 adds a card).
- Changes to the Contents page.

## Testing

- `tests/progress.test.ts`: `resolveBookmarks` drops unknown keys and keeps
  reading order; an empty list gives an empty list.
- `tests/progress.test.ts`: `BOOKMARKS_STORAGE_KEY` differs from
  `PROGRESS_STORAGE_KEY` (a bookmark must never write to the progress key).
- `tests/i18n.test.ts`: `dashboardHref("en")` is `/dashboard` and
  `dashboardHref("bn")` is `/bn/dashboard`.
- Existing progress tests stay green after the store refactor. Manual check
  in the browser: mark a section done, bookmark it, reload; both persist
  and neither changes the other.
- `npm run lint`, `npm test`, and `npm run build` pass. The build output
  has `out/dashboard/index.html` and `out/bn/dashboard/index.html`.
- Screenshots at 1440px and 375px of `/dashboard/` and `/bn/dashboard/`, in
  light and dark mode, with no progress and with some progress and bookmarks.
