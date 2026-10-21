# Editorial redesign (systemdesignbangla.com style)

Date: 2026-10-21. Status: approved by the owner ("do all, I approve all").

## Goal

Give the whole site the look of https://www.systemdesignbangla.com/: an
editorial, Bengali-first design with a cream paper ground and a deep teal
accent. Copy the visual style only. Do not copy that site's brand, text,
author section, or ads.

## Decisions

| Topic | Decision |
|---|---|
| Scope | Full match: tokens, fonts, shell, home page, topic pages, a new contents/progress page. |
| Default theme | Follow the OS (no change: `src/lib/theme.ts` already does this). |
| Approach | Change the existing token values and rebuild the pages with Tailwind. No ported CSS files. |
| Progress | Per section (63 sections). Key: `<topic slug>/<section id>`. Stored in localStorage. |

## 1. Visual system

Token names stay. Values change (`src/app/globals.css`):

| Token | Light | Dark |
|---|---|---|
| `--bg` | `#faf7f2` | `#0e1115` |
| `--bg-raised` | `#ffffff` | `#161b22` |
| `--bg-raised-2` | `#f3ede2` | `#1c2128` |
| `--border` / `--border-strong` | `#efeadc` / `#e6dfd0` | `#1f242b` / `#2a3038` |
| `--text` / `--text-dim` / `--text-faint` | `#1a1d1f` / `#4a5158` / `#656b72` | `#e6e6e6` / `#b8bfc7` / `#8a929e` |
| `--accent` | `#0f766e` | `#2dd4bf` |
| `--accent-2` (new) | `#9a4a07` | `#f59e0b` |

New: `--shadow-sm/md/lg`. Every text token has 4.5:1 contrast or more on
`--bg` (checked with a script). Crimson Pro replaces Fraunces as the display
font. Body text is 17px.

## 2. Shell

- Header: fixed height 64px, blurred page color, brand mark, nav links
  (Parts, Contents), search, language, install, theme.
- The left sidebar of Parts moves from `SiteShell` into `TopicPage`. The
  home and contents pages are full width.
- Footer: 3 columns (Parts 1–7, Parts 8–14, Site) and a copyright line.

## 3. Home page

1. Hero: grid and glow background, eyebrow, two-line title with an accent
   word, intro, two buttons (start reading, contents), 4 stats with a teal
   left rule, and a dark "cover card" tilted 2°.
2. "Why this reference": 6 cards (three voices, citations, practice tasks,
   progress, offline app, dark/light).
3. Parts: 14 numbered cards on a soft band, each with a section count and a
   progress bar.

## 4. Topic pages

- Grid: Parts sidebar 240px, reading column up to 720px, "On this page"
  280px (target `chapter-layout`).
- A 3px reading bar (accent to amber gradient) under the header.
- Each section ends with a "Mark as done" toggle.

## 5. Contents page (`/contents/`, `/bn/contents/`)

Progress summary (done, total, percent), a "continue reading" link to the
first section that is not done, a reset button, and all Parts with their
sections and check marks.

## Progress logic

`src/lib/progress.ts` has no React and no server imports. It parses and
writes the stored list, toggles a key, and counts only keys of sections
that exist. Unit tests in `tests/progress.test.ts`. A client hook reads it
with `useSyncExternalStore` and updates on the `storage` event, so all
tabs agree. The server snapshot is empty, so static HTML shows 0 done.

## Testing

`npm test`, `npm run lint`, `tsc`, `npm run build`, and screenshots of the
home, topic, and contents pages in both themes.
