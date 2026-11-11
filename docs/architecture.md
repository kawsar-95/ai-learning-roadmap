# Architecture

How the site is built: the routes, the build, the two languages, the three
voices, search, reader state, offline use, the theme, and the design rules.
The last part is a map of every file.

## Contents

- [Overview](#overview)
- [Routes](#routes)
- [The build](#the-build)
- [Server data and client components](#server-data-and-client-components)
- [Languages](#languages)
- [Voices](#voices)
- [The topic page](#the-topic-page)
- [Search](#search)
- [Reader state](#reader-state)
- [Offline use](#offline-use)
- [Theme](#theme)
- [Roadmap lessons](#roadmap-lessons)
- [Content from other sites](#content-from-other-sites)
- [Design rules](#design-rules)
- [Tests](#tests)
- [File layout](#file-layout)

## Overview

The site is a static export of a Next.js 16 App Router app. `next build`
writes every page as an HTML file into `out/`, and GitHub Pages serves that
folder. There is no server, no database, no account, and no analytics.

- **Content is data in the repo.** Each Part is one JSON file in
  `src/content/`. The roadmap is two JSON files in `src/data/` and 542
  Markdown lessons in `src/content/lessons/`.
- **The build checks the data.** Zod schemas parse every file when the build
  loads it. A bad file stops the build with the path of the bad field.
- **The reader's state stays in the browser.** Progress, bookmarks, quiz
  scores, and preferences are `localStorage` keys.

## Routes

English pages live at the site root. Bangla pages live under `/bn/`. Each
route file is a thin wrapper: it renders a page component from
`src/components/pages/` with `lang="en"` or `lang="bn"`. `(en)` is a route
group, so it adds nothing to the URL.

| English URL | Bangla URL | Page component | What it shows |
| --- | --- | --- | --- |
| `/` | `/bn/` | `HomePage` | The hero, the counts, the features, and the 17 Parts as a numbered index |
| `/topics/<slug>/` | `/bn/topics/<slug>/` | `TopicPage` | One Part (17 pages) |
| `/contents/` | `/bn/contents/` | `ContentsPage` | Every section with a check mark, overall progress, best quiz scores |
| `/dashboard/` | `/bn/dashboard/` | `DashboardPage` | Continue reading, and the bookmarks |
| `/interview/` | `/bn/interview/` | `InterviewPage` | Three questions for each Part |
| `/roadmap/` | `/bn/roadmap/` | `RoadmapPage` | Learning paths, then 7 stages of 20 phases with lesson lists |
| `/roadmap/<phase>/<lesson>/` | `/bn/roadmap/<phase>/<lesson>/` | `LessonPage` | One curriculum lesson (542 pages) |
| `/resources/` | `/bn/resources/` | `ResourcesPage` | 20 open-source repositories in 5 groups |
| `/search-index.json` | `/bn/search-index.json` | route handler | The search documents of one language |

The build also writes these files:

| File | Source | Note |
| --- | --- | --- |
| `404.html` | `src/app/not-found.tsx` | One page for both languages. GitHub Pages serves it for every unknown URL. |
| `manifest.webmanifest` | `src/app/manifest.ts` | The web app manifest. Its URLs are relative, so they work under any base path. |
| `favicon.ico`, `icon.svg`, `apple-icon.png` | `src/app/` | The tab and home screen icons |
| `sw.js`, `icons/` | `public/` | The service worker and the app icons |

Each language has 565 pages: the home page, 5 single pages, 17 Parts, and 542
lessons. That makes 1,130 pages, plus the 404 page.

Dynamic routes set `dynamicParams = false`, and `generateStaticParams` lists
every slug. A URL that is not in the list is a 404, not a page made on
demand.

## The build

`npm run build` runs two steps:

1. `next build` writes the site into `out/`.
2. `node scripts/precache.mjs` writes the offline file list into `out/sw.js`
   (see [Offline use](#offline-use)).

`next.config.ts` sets:

| Setting | Value | Why |
| --- | --- | --- |
| `output` | `"export"` | Write static files only. There is no server build, so `next start` does not work. |
| `trailingSlash` | `true` | `topics/x/` is written as `topics/x/index.html`, which GitHub Pages serves as a folder. |
| `basePath` | `PAGES_BASE_PATH`, or `""` | The deploy builds under `/ai-learning-roadmap`. A local build serves from `/`. |
| `env.NEXT_PUBLIC_BASE_PATH` | the same value | Client code needs the base path where `next/link` does not add it (see below). |
| `turbopack.rules` | `@tailwindcss/turbopack` for `*.css` | Tailwind CSS 4 runs as a Turbopack loader. |

`next/link` and `next/navigation` add the base path by themselves. These
places add it by hand from `NEXT_PUBLIC_BASE_PATH`:

- the fetch of the search index (`SearchPalette.tsx`)
- the service worker URL and scope (`ServiceWorker.tsx`)
- the language script in `<head>` and the language switch (`i18n.ts`,
  `LanguageSwitch.tsx`)
- links between roadmap lessons (`LessonPage.tsx`, `lesson-markdown.ts`)

The deploy and the base path are covered in
[deployment.md](deployment.md).

## Server data and client components

Two modules load the data, and only server code may import them:

| Module | Loads | Checks |
| --- | --- | --- |
| `src/lib/topics.ts` | the 17 Part files | `TopicFileSchema.parse` on each file. The `slug` in the file must match its place in `TOPIC_ORDER`. |
| `src/lib/roadmap.ts` | `roadmap-lessons.json`, `roadmap-phases.json` | `buildRoadmap`: both schemas, no gaps, no repeats, every phase in exactly one stage |

`InterviewPage.tsx` parses `src/content/interview.json` the same way. It
throws if a Part is missing, is out of order, does not have exactly 3
questions, or names a section that does not exist.

Page components are server components. They pass plain data to client
components as props. A `"use client"` file never imports `topics.ts` or
`roadmap.ts`. A client file that needs a type from them imports it with
`import type`, which is erased at build time.

Most of `src/lib/` has no server imports and no `@/` alias, so client code,
build code, and `node --test` can all load it. These files import each other
with relative paths that end in `.ts`, because Node runs the tests by
stripping the types and does not resolve the alias. For the same reason they
use no `enum`, no `namespace`, and no constructor parameter properties.

## Languages

`src/lib/i18n.ts` holds the language rules and every interface string.

- `langFromPath` and `localizedPath` map a path to its language and to the
  same page in the other language.
- `UI.en` and `UI.bn` are the two dictionaries. `UI.bn` has the type of
  `UI.en`, so a missing key is a type error, and a test checks that both have
  the same keys.
- `fmtNum` writes numbers in Bangla digits on the Bangla site.

The content has a Bangla title and intro for every Part (`bn.title`,
`bn.lede`) and every section (`bn.title`, `bn.sub`). The section text has a
Bangla voice. Practice tasks and quiz questions have an `en` and a `bn`
version.

**Choosing a language.** The header link (`LanguageSwitch.tsx`) opens the
same page in the other language, keeps the URL hash, and saves the choice in
`localStorage` key `lang`. A script in `<head>` (`langInitScript`) runs
before the first paint. It sets `<html lang>` from the path, and if the saved
language differs from the page's language, it replaces the URL with the same
page in the saved language.

**The 404 page** is prerendered once, so its path is not a page in either
language. It shows the English text with the Bangla text under it, and its
language switch opens the other home page.

## Voices

Each section has three block lists: `body` (Technical), `layman` (Layman's),
and `bangla` (বাংলা). `SectionView.tsx` shows one at a time.

- The voice switcher (`VoiceSwitcher.tsx`) lists the voices that have
  blocks. It shows only when a section has more than one. The Bangla site
  lists বাংলা first. Arrow keys, Home, and End move between the options.
- The choice is saved in `localStorage` key `voice`, and every section
  follows it. With no saved choice, a section shows the first voice in the
  list: Technical on the English site, বাংলা on the Bangla site.
- The Technical voice renders as plain prose. The other two render in a
  panel with a colored left border: violet for Layman's, green for বাংলা.
- A link to a heading in the Technical text (from "On this page", for
  example) switches that one section to Technical and scrolls to the heading.
  The saved choice does not change.
- Practice tasks follow the language: Bangla on the Bangla site, and Bangla
  on the English site when the voice is বাংলা (`practiceLang`).
- Videos follow the voice (`videosForVoice`). On the English site, Technical
  and Layman's show the English videos, and বাংলা shows the Bangla videos
  first, then the English ones. The Bangla site shows Bangla videos first in
  every voice.

## The topic page

`TopicPage.tsx` lays a Part out like a book chapter:

| Width | Parts | "On this page" |
| --- | --- | --- |
| below 1024 px (`lg`) | in the header's menu drawer | a closed list above the text |
| 1024 to 1279 px | a 240 px column on the left, sticky under the header | a closed list above the text |
| 1280 px (`xl`) and up | the same column | a 260 px column on the right that marks the heading in view |

The text column is at most 720 px wide.

- `TopicHeader.tsx` opens the page: the Part number, the reading time,
  **Mark as read**, **Go to quiz**, then the title, tagline, and intro.
  The reading time counts 200 words a minute over the voice each site shows
  first: Technical in English, বাংলা in Bangla. **Mark as read** marks every
  section of the Part as done, and a second click clears them.
- A Part with more than one section shows one section at a time
  (`SectionPager.tsx`): a step bar ("Section 1 of 10"), then the section,
  then **Previous** and **Next**. The quiz is the last step, followed by the
  sources and the links to the next Part. A URL hash, a click on an in-page
  link, or the Back button opens the step that holds the target.
- A Part with one section shows everything on one page, with a 3 px reading
  bar under the header (`ReadingBar.tsx`). Its "On this page" also lists the
  level 3 headings of the Technical text.
- Each section ends with **Bookmark** and **Mark as done**.

## Search

The build writes two static JSON files from route handlers with
`dynamic = "force-static"`:

- `/search-index.json`: one document per section, with the English titles
  and the Technical text.
- `/bn/search-index.json`: one document per section, with the Bangla titles,
  the বাংলা text, and the Technical text. An English term such as "token"
  still finds Bangla sections.

`SearchPalette.tsx` is the header button and the dialog. <kbd>Ctrl</kbd>+<kbd>K</kbd>
or <kbd>⌘</kbd>+<kbd>K</kbd> opens it from any page. On the first open it
fetches the index of the page's language and builds a
[MiniSearch](https://github.com/lucaong/minisearch) index in the browser.
The options are in `src/lib/search.ts`: prefix matching, fuzzy matching at
0.2, a boost of 3 for section titles and 1.5 for Part titles, and the top 8
hits. Arrow keys move the selection, Enter opens it, and Escape closes the
dialog.

## Reader state

Everything the site remembers is a `localStorage` key. There is no other
storage and no cookie.

| Key | Value | Written by |
| --- | --- | --- |
| `progress` | JSON array of `"<part slug>/<section id>"`, sorted | **Mark as done**, **Mark as read**, **Start over** |
| `bookmarks` | JSON array of `"<part slug>/<section id>"`, sorted | **Bookmark**, **Remove** on the dashboard |
| `quiz-scores` | JSON object `{ "<part slug>": { "best": n, "total": n } }` | **Check answers** |
| `roadmap-progress` | JSON array of `"<phase>/<lesson number>"`, sorted | the lesson toggles and **Mark as read** on the roadmap |
| `voice` | `main`, `layman`, or `bangla` | the voice switcher |
| `theme` | `light` or `dark` | the theme button |
| `lang` | `en` or `bn` | the language link |

- `src/lib/progress.ts` and `src/lib/quiz.ts` hold the pure logic: parse,
  serialize, toggle, count, and pick the first undone section. Bad or
  missing data reads as empty, so a corrupt value never breaks a page.
- `src/components/progress/createStore.ts` wraps one key in a React hook
  with `useSyncExternalStore`. A change in another tab arrives as a
  `storage` event. A change in the same tab sends a custom event, such as
  `progress-change`.
- The static HTML shows nothing done. The saved state appears after
  hydration.
- A key of a section that no longer exists stays in storage and does not
  count. This is why section ids must not change (see the
  [content guide](content-guide.md#keep-ids-stable)).
- A best quiz score counts only while the quiz keeps the same number of
  questions.

## Offline use

The site is an installable web app that works offline.

- `src/app/manifest.ts` is the manifest. It opens the site as a standalone
  app, with 192 px, 512 px, and maskable icons.
- `ServiceWorker.tsx` registers `sw.js` in production builds only. In
  development a worker would keep serving stale files. It also asks the
  browser not to evict the saved files (`navigator.storage.persist`).
- `InstallButton.tsx` shows an install button in the header when the browser
  offers one (Chromium browsers).

**The offline file list.** After `next build`, `scripts/precache.mjs` walks
`out/` and writes the list into `out/sw.js` in place of the placeholder
`/* PRECACHE_MANIFEST */ []`. Each entry has the URL and a 12-character hash
of the file. The build prints `sw.js: N files saved for offline use`.

| Saved | Left out |
| --- | --- |
| every HTML page, as its folder URL | the 1,084 roadmap lesson pages (both languages): the install would be too large |
| each page's `index.txt`, the RSC payload a link click fetches | the `__next.*` prefetch segments |
| `_next/static/` | `sw.js` itself |
| both search indexes, the manifest, the icons | the unused starter SVGs in `public/` |

**What the worker does** (`public/sw.js`):

- On install it downloads the files that are not saved yet, six at a time.
  A new build changes only the hashes of changed files, so an update
  downloads only those.
- A saved file is served from the cache first. Anything else goes to the
  network first and falls back to a saved copy. An unsaved page opened
  offline gets a small "You are offline" page.
- On activate it deletes the files of old builds and takes control of open
  tabs.

## Theme

`<html data-theme>` is the source of truth. The server writes `dark`.
`THEME_INIT_SCRIPT` in `src/lib/theme.ts` runs in `<head>` before the first
paint. It uses the saved `theme`, or the device setting when nothing is
saved, so the page does not flash. If storage is blocked, the page stays
dark. A test checks that the script and `resolveTheme` agree in every case.

The colors are CSS variables in `src/app/globals.css`, with one set for each
theme. `@theme inline` exposes them to Tailwind as `bg`, `text`,
`text-dim`, `accent`, `voice-layman`, `voice-bangla`, and so on.

| Token | Dark | Light |
| --- | --- | --- |
| `--bg` | `#0e1115` | `#faf7f2` (warm paper) |
| `--text` | `#e6e6e6` | `#1a1d1f` |
| `--accent` | `#2dd4bf` | `#0f766e` |
| `--voice-layman` | `#b9a3f0` | `#6a4bc0` |
| `--voice-bangla` | `#6fcf9f` | `#1b7a4c` |

The diagrams in the content were drawn for a dark page. In the light theme,
`globals.css` maps their dark fills and light strokes to light-theme colors,
one rule per color.

## Roadmap lessons

Each of the 542 lessons is a page made at build time from its copied
Markdown file. `src/lib/lesson-markdown.ts` renders it with
[marked](https://marked.js.org/) and [KaTeX](https://katex.org/):

- The first `# Title` line is dropped, because the page shows the title.
- Raw HTML in the Markdown is escaped. The text comes from another
  repository.
- `$...$` and `math` code blocks become KaTeX. A price such as "$5 and $10"
  stays text.
- A `figure` code block is an animation that only the curriculum site has.
  It becomes a link to the lesson there.
- `mermaid` code blocks stay as source code.
- A link to another lesson's `docs/en.md` opens that lesson on this site.
  Images load from `raw.githubusercontent.com`, and other files link to
  GitHub, both at the commit the copy came from.
- Every heading gets a GitHub-style id. A lesson with three or more level 2
  headings gets an "On this page" list.

Refreshing the lessons is covered in [roadmap.md](roadmap.md).

## Content from other sites

**Videos** (`VideoCard.tsx`). A video is a card with a thumbnail from
`i.ytimg.com`. Nothing plays and no player loads until the reader clicks.
Then the card becomes a `youtube-nocookie.com` player in place. A Short is a
9:16 card with a plain poster, because YouTube's thumbnail of a Short is 4:3
with black bars.

**Live views** (`EmbedFrame.tsx`). A live view is another site's page in a
frame, under the section intro. Only hosts in `FRAMEABLE_HOSTS` or
`LINK_ONLY_HOSTS` (`src/lib/content-schema.ts`) are allowed, over https.

- A frame loads when the reader clicks **Load live view**. A light page
  marked `autoload` loads when it comes within 300 px of the screen.
- The frame is sandboxed with these permissions:
  `allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-forms`.
- A page made for a wide screen sets `designWidth`. In a narrower column the
  frame keeps that width and scales down to fit. Below 55% it stops scaling
  and fills the column at full size.
- A host that refuses to be framed is a link card with **Open in a new tab**.

## Design rules

The look follows the calm editorial style of
[systemdesignbangla.com](https://www.systemdesignbangla.com/). The rules come
from the declutter pass
([spec](superpowers/specs/2026-11-07-declutter-design.md)):

1. Cards are flat: a border, no resting shadow, no lift on hover. Only the
   home page's cover card has a shadow.
2. Chrome has no emoji. A page header is a title and one line, with no label
   that repeats the navigation.
3. A list of many things is a ruled index, not a grid of boxes.
4. A reading page puts the text first: one meta line, then the title.
5. One accent color. Progress bars are flat teal.
6. Nothing is listed twice. The footer does not repeat the Parts.

**Type.** Crimson Pro for headings, Inter for text, JetBrains Mono for code
and labels, and Noto Sans Bengali for Bangla. `next/font/google` downloads
them at build time and serves them from the site.

**Layout.** The header is 64 px high and sticky. The breakpoints are
Tailwind's defaults: `sm` 640 px, `lg` 1024 px (the header links, the Parts
column), and `xl` 1280 px ("On this page").

**Accessibility.** A skip link opens each page. The voice switcher uses
roving focus. The search dialog and the menu drawer keep focus inside while
open, close on Escape, and return focus to their button. Motion is reduced
when the device asks for it.

## Tests

`npm test` runs every `tests/*.test.ts` file with Node's built-in test
runner. There is no test framework and no browser. Most tests load the
modules in `src/lib/` directly, and some read the real content files.

| File | Covers |
| --- | --- |
| `content-schema.test.ts` | The inline tag allowlist and `TopicFileSchema` |
| `embed.test.ts` | Live view hosts and the embed fields |
| `i18n.test.ts` | Paths in both languages, the language script, the dictionaries, Bangla digits, Bangla titles in the content |
| `icons.test.ts` | `icon.svg` colors and validity, `favicon.ico` sizes, icons in the offline list |
| `interview.test.ts` | The interview checker and the real `interview.json` |
| `lesson-markdown.test.ts` | Lesson rendering, escaping, math, links, and every real lesson |
| `practice.test.ts` | The practice task schema and `practiceLang` |
| `progress.test.ts` | Progress and bookmark keys and counts |
| `pwa.test.ts` | The manifest, the offline list, and the service worker (run against a fake cache) |
| `quiz.test.ts` | Scoring and the saved best scores |
| `quiz-content.test.ts` | Rules for the real quizzes: 5 questions, Bangla digits, answer positions |
| `roadmap.test.ts` | The roadmap files, lesson keys and links, durations |
| `search.test.ts` | Search documents in both languages, block text, reading time |
| `theme.test.ts` | `resolveTheme` and the theme script |
| `video-check.test.ts` | The title and channel matching of `npm run check:videos` |
| `video-curation-scripts.test.ts` | The two shell steps of the video curation |
| `video-data.test.ts` | Rules for the real videos: no repeats in a section, clean titles, Short lengths |
| `videos.test.ts` | The video schema, `videosForVoice`, and length formats |

## File layout

```text
.
├── .github/workflows/deploy-pages.yml   test, build, and publish to GitHub Pages on a push to main
├── AGENTS.md                            Next.js 16 notes for coding agents (written by `next dev`)
├── CONTRIBUTING.md                      how to make a change
├── LICENSE                              MIT
├── README.md
├── docs/
│   ├── architecture.md                  this file
│   ├── content-guide.md                 the Part file format
│   ├── deployment.md                    GitHub Pages, the base path, troubleshooting
│   ├── quizzes.md                       the quiz format
│   ├── roadmap.md                       the roadmap data and the curriculum lessons
│   ├── video-coverage.md                where the clips come from (generated)
│   ├── video-review-log.md              every clip added or left out, with the reason (generated)
│   └── superpowers/                     specs and plans of past redesigns (historical)
├── eslint.config.mjs                    Next.js core web vitals and TypeScript rules
├── next.config.ts                       static export, base path, Tailwind loader
├── package.json
├── public/
│   ├── icons/                           192 px, 512 px, and maskable app icons
│   ├── sw.js                            the service worker; the build fills in its file list
│   └── *.svg                            unused starter files from create-next-app
├── screenshots/                         the README images
├── scripts/
│   ├── build-roadmap.mjs                curriculum ROADMAP.md -> src/data/roadmap-lessons.json
│   ├── import-lessons.mjs               curriculum lessons -> src/content/lessons/
│   ├── precache.mjs                     writes the offline file list into out/sw.js
│   ├── check-videos.mjs                 `npm run check:videos`: asks YouTube about every listed video
│   ├── screenshots/                     takes the README screenshots (see its README)
│   └── video-curation/                  the scripts that found and verified the clips (see its README)
├── src/
│   ├── app/
│   │   ├── layout.tsx                   <html>, fonts, metadata, the theme and language scripts
│   │   ├── globals.css                  design tokens, both themes, prose and code styles
│   │   ├── not-found.tsx                the 404 page, both languages
│   │   ├── manifest.ts                  the web app manifest
│   │   ├── favicon.ico, icon.svg, apple-icon.png
│   │   ├── search-index.json/route.ts   the English search index
│   │   ├── (en)/                        English routes; layout.tsx wraps them in SiteShell
│   │   └── bn/                          Bangla routes, the same set, and bn/search-index.json
│   ├── components/
│   │   ├── content/
│   │   │   ├── SectionView.tsx          one section: intro, live views, voices, practice, videos, done
│   │   │   ├── SectionPager.tsx         one section at a time, with the step bar
│   │   │   ├── VoiceSwitcher.tsx        the voice tabs
│   │   │   ├── ProseBlocks.tsx          renders a block list, one component per block type
│   │   │   ├── Inline.tsx               the one place that renders inline HTML
│   │   │   ├── blocks/                  Paragraph, Heading, ListBlock, CodeBlock, Diagram, Callout,
│   │   │   │                            Analogy, PillGrid, Table, Panels, Divider, RawHtml
│   │   │   ├── TopicHeader.tsx          Part number, reading time, Mark as read, Go to quiz, title
│   │   │   ├── PracticeList.tsx         practice tasks, with CopyButton.tsx
│   │   │   ├── VideoList.tsx            the Watch list: videos, then Shorts, with VideoCard.tsx
│   │   │   ├── EmbedList.tsx            the Live view list, with EmbedFrame.tsx
│   │   │   ├── QuizSection.tsx          the quiz
│   │   │   ├── Sources.tsx              the numbered sources
│   │   │   └── PrevNext.tsx             previous and next Part or lesson
│   │   ├── layout/
│   │   │   ├── SiteShell.tsx            skip link, header, footer
│   │   │   ├── SiteHeader.tsx           the sticky header
│   │   │   ├── MobileNav.tsx            the menu drawer below `lg`
│   │   │   ├── Sidebar.tsx              the Parts column, with SidebarList.tsx
│   │   │   ├── PageHeader.tsx           the title and intro of a secondary page
│   │   │   ├── LanguageSwitch.tsx       the link to the same page in the other language
│   │   │   ├── ThemeToggle.tsx          the sun/moon button
│   │   │   ├── InstallButton.tsx        the install button (Chromium)
│   │   │   └── ServiceWorker.tsx        registers sw.js in production
│   │   ├── navigation/
│   │   │   ├── SearchPalette.tsx        the search button and the Ctrl/Cmd+K dialog
│   │   │   ├── SectionNav.tsx           the sticky "On this page" column
│   │   │   └── OutlineDetails.tsx       the closed "On this page" list on narrow screens
│   │   ├── pages/                       one component per page, shared by both languages
│   │   └── progress/
│   │       ├── createStore.ts           a localStorage key as a React hook
│   │       ├── useProgress.ts           the progress, bookmark, roadmap, and quiz score stores
│   │       ├── ProgressWidgets.tsx      Mark as done, Bookmark, Mark as read, Part counts
│   │       ├── DashboardWidgets.tsx     Continue reading, bookmarks, best scores
│   │       ├── RoadmapWidgets.tsx       lesson toggles, phase bars, the roadmap summary and filter
│   │       └── ReadingBar.tsx           the scroll bar under the header
│   ├── content/
│   │   ├── <slug>.json                  the 17 Parts
│   │   ├── interview.json               the interview questions
│   │   └── lessons/                     the copied curriculum lessons, LICENSE, source.json
│   ├── data/
│   │   ├── roadmap-lessons.json         every phase and lesson (generated)
│   │   └── roadmap-phases.json          stages, summaries, links to the Parts (by hand)
│   └── lib/
│       ├── content-schema.ts            block, section, Part, video, embed, practice, and quiz schemas
│       ├── topics.ts                    loads the Parts; TOPIC_ORDER (server only)
│       ├── roadmap.ts                   loads the roadmap (server only)
│       ├── roadmap-schema.ts            roadmap schemas, buildRoadmap, lesson URLs, durations
│       ├── lesson-markdown.ts           renders a lesson: marked, KaTeX, links, outline
│       ├── interview.ts                 the interview schema and checker
│       ├── i18n.ts                      languages, paths, the language script, every UI string
│       ├── search.ts                    search documents, the MiniSearch index, reading time
│       ├── progress.ts                  progress and bookmark logic and keys
│       ├── quiz.ts                      quiz scoring and best scores
│       ├── theme.ts                     the theme rule and the theme script
│       ├── practice.ts                  the language of the practice tasks
│       ├── videos.ts                    which videos a voice shows; length formats
│       └── video-check.ts               the pure helpers of `npm run check:videos`
├── tests/                               node:test suites (see Tests above)
└── tsconfig.json                        strict TypeScript; `@/*` maps to `src/*`
```
