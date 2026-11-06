# Declutter pass (the calm systemdesignbangla.com way)

Date: 2026-11-07. Status: built on `feat/declutter-revamp`, not merged.

## Goal

The site already has the look of https://www.systemdesignbangla.com/ (see the
2026-10-21 editorial redesign: palette, fonts, hero). Since then it grew
busier than that site: more controls, more boxes, the same text repeated.
This pass changes density and structure only. It does not change the palette,
the fonts, the content files, the routes, or the schema.

## Diagnosis

Measured on the production build, light theme, 1440 and 390 px wide:

| What | Found |
| --- | --- |
| Topic page, first real paragraph | y = 863 to 1150 on a 900 px screen; y = 1030 to 1643 on a phone (nothing to read on the first screen) |
| Footer | 572 px high (1300 px on a phone) with 24 links; it listed all 17 Parts again |
| Home | 17 boxed cards, each with six pieces of data, 4220 px tall (8121 px on a phone) |
| Contents | 17 boxes of ruled rows, 8747 px tall |
| Header | 10 controls: a wide search box with a key hint, and a solid "Start reading" button that the home hero already offers |
| Topic header | two pills, an emoji, two bordered buttons between two rules, a 6 px gradient bar, then two intros (the Part lede and the section intro) |
| A layout bug | `[&>section]:pt-0` lost to `sm:[&>section]:py-10`, so every section had 40 px of extra top padding from 640 px up |

## Rules

1. Cards are flat: a border, no resting shadow, no lift on hover. Only the home
   cover card keeps a shadow.
2. Chrome has no emoji, and a page header is a title and one line, with no
   label that repeats the nav.
3. A list of many things is a ruled index, not a grid of boxes.
4. A reading page puts the text first: one meta line, then the title.
5. One accent. Progress bars are flat teal, not teal to amber.
6. Nothing is listed twice: the footer does not repeat the Parts.

## Changes

| Area | Change |
| --- | --- |
| `globals.css` | `--shadow-card` and `--shadow-card-hover` are a transparent shadow |
| Header | CTA removed; search, language, theme, and install are quiet icon buttons |
| Footer | brand, one line, site links in one row, copyright |
| `PageHeader` (new) | one header for Contents, Dashboard, Interview, Roadmap, Resources |
| Home | no eyebrow; the 17 Parts are a numbered, two-column index with a section count, or `3/10` once started; the author block is smaller |
| Topic header | meta line (Part, time) with the Part actions on the right; "Go to quiz" is a link |
| Topic body | thin step bar, smaller section heading, voice switcher as underline tabs, flat action buttons, the sidebar is one line per Part, the 40 px padding bug is fixed |
| Contents, Interview | ruled headings; Contents lists sections in two columns |
| `i18n.ts` | `homeEyebrow`, `partsEyebrow`, `authorEyebrow` removed from both languages |

## Result

Page height (`scrollHeight`) at 1440x900 and 390x844, light theme, production
build served from the site root:

| | Before | After |
| --- | --- | --- |
| Home, desktop / phone | 4220 / 8121 px | 2234 / 2942 px |
| Contents, desktop / phone | 8747 / 10703 px | 4461 / 6458 px |
| Footer, desktop / phone | 572 / 1300 px, 24 links | 226 / 328 px, 7 links |
| Header controls, desktop | 10 | 9 |
| First paragraph, Part 6 | y 863 (desktop), 1030 (phone) | y 651 (desktop), 860 (phone) |

On a phone the voice tabs now fit on the first screen (they end at y = 796 of
844 px) and the first body text starts just below the fold (y = 860). Going
further would mean cutting the Part intro or the section intro, which is
content.

## Left alone on purpose

Content files, routes, the progress logic, the search palette, the voice
panels, the roadmap and resources cards (they only lose the shadow and the
label above the title), the home cover card, and the mobile menu.

## Checks

`npm test` (152 pass), `npm run lint`, `tsc --noEmit`, and `npm run build` pass.
Screenshots at 1440 and 390 px (11 pages in light, two of them Bangla, and
3 pages in dark) show no horizontal overflow and no console errors. A browser
run (39 checks) covered the voice tabs with the keyboard, mark as done,
bookmark, the pager, the progress counts on Home and Contents, search (click
and Ctrl+K), the language and theme switches, focus rings, hit sizes (24 px or
more), and the mobile menu. The measuring scripts are throwaway files outside
the repo.
