# Revamp 1 of 4: polish the look

Date: 2026-10-22. Status: design approved by the owner in chat. Spec waits
for review.

## Goal

Remove the last visible differences between this site and
https://www.systemdesignbangla.com/ on the header, the topic page, the
sidebar, and the sections. The 2026-10-21 editorial redesign already copied
the tokens, fonts, home page, and contents page. Copy the visual style
only, not that site's brand or text.

## The revamp has 4 sub-projects

Each sub-project gets its own spec, plan, and implementation.

| # | Sub-project | Depends on |
|---|---|---|
| 1 | Polish the look (this spec) | none |
| 2 | Dashboard page, with bookmarks | 1 |
| 3 | Quizzes per topic | 1 |
| 4 | Author section and interview page | 1 |

## Decisions

| Topic | Decision |
|---|---|
| Approach | Edit the existing components with the existing Tailwind tokens. No ported CSS file. |
| New pages | None. Nav links to Dashboard, Interview, and Author come with sub-projects 2 and 4. |
| Bookmark button | Comes with sub-project 2, where the dashboard lists the bookmarks. |
| "Go to quiz" button and quiz-count pill | Come with sub-project 3. |
| Floating support and coffee buttons | Out of scope. |
| Languages | All new text goes into `UI` in `src/lib/i18n.ts`, in English and Bangla. |

## 1. Header (`src/components/layout/SiteHeader.tsx`)

- Put the bar contents in a centered `max-w-6xl` container with the same
  side padding as the home page.
- Keep the nav links "Parts" and "Contents".
- Add a teal "Start reading" button at the right end. It links to
  `topicHref(TOPICS[0].slug, lang)`, as the home page button does. It uses
  the existing `UI.startReading` text. Below `sm` it is hidden, so the bar
  does not overflow at 375px.
- Search, language switch, install, and theme toggle stay as they are.

## 2. Topic header (`src/components/content/TopicHeader.tsx`)

- Remove the mono "PART 07" eyebrow. Put two pills in its place:
  - "Part 7 · Inference" (part number and topic title).
  - "📖 N min read".
- Pills use `bg-bg-raised-2`, `rounded-full`, `px-3 py-1`, 13px text.
- Remove the stats chip (`ui.topicMeta`).
- Title, tagline, and lede stay.
- Add an action bar below the lede, between two `border-border` rules, with
  one button: "✓ Mark as read". It sets every section of the topic to done.
  When all sections are done, the button shows "✓ Read" in the accent color.
  A second click sets them all to not done.

### Reading time

- New pure function `readingMinutes(blocks, strip)` in `src/lib/search.ts`,
  next to the existing `blockText` helper that it uses. (`node --test`
  cannot import `src/lib/topics.ts`, because that file uses `@/` aliases.)
- `TopicHeader` passes the blocks of the voice that the language shows
  first, for all sections: `bangla` for `bn`, `body` for `en`.
- Minutes = `max(1, round(words / 200))`. Words are runs of non-space
  characters.
- The page computes it at build time. No client code.

### Mark as read

- New pure function `setKeys(done, keys, value)` in `src/lib/progress.ts`,
  next to `toggleKey`. It returns a new set with all `keys` added (value
  true) or removed (value false).
- New function `setDone(keys, value)` in
  `src/components/progress/useProgress.ts`. It calls `write(setKeys(...))`,
  as `toggleDone` calls `write(toggleKey(...))`. One write, one change
  event.
- The button is a small client component next to `SectionDoneButton` in
  `src/components/progress/ProgressWidgets.tsx`. It gets the section keys
  as a prop.

## 3. Sidebar (`SidebarList.tsx`, `TopicPage.tsx`)

- Remove `border-r border-border` from the sidebar `aside` in `TopicPage`.
- The active item uses `bg-bg-raised-2` (was `bg-bg-raised`) with the
  existing teal left border.
- Hover uses `hover:bg-bg-raised-2/60`.

## 4. Sections (`src/components/content/SectionView.tsx`)

- Put a `border-t border-border` rule and top padding above each section
  except the first one.
- Remove the large section number ("01").
- In `TopicPage`, reduce the gap between sections to match the rule
  spacing.

## Out of scope

- Dashboard, bookmarks, quizzes, author, and interview (sub-projects 2-4).
- Token, font, home page, and contents page changes.
- Floating buttons and ads.

## Testing

- `tests/search.test.ts`: `readingMinutes` gives 1 for an empty or short
  block list, and 3 for 600 words.
- `tests/progress.test.ts`: `setKeys` adds all keys, removes all keys, and
  keeps the keys of other topics.
- `npm run lint`, `npm test`, and `npm run build` pass.
- Screenshots at 1440px and 375px of `/` and `/topics/inference/`, in light
  and dark mode, for the owner to compare with the reference.
