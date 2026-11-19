# System Design (Part 18): the generator

Part 18 is generated. [`src/content/system-design.json`](../../src/content/system-design.json) (about 3 MB) and the Part's three
entries in [`src/content/interview.json`](../../src/content/interview.json) are built from the Python files in this folder.
**Edit the files here, then run the build. A hand edit of the JSON is overwritten by the next build**, and `npm test` fails
until the two agree (see [Checking](#checking)).

The Part follows [Dilum Sanjaya's System Design course](https://designed-to-scale.vercel.app/) in its 40 lessons, their order and
their titles, and in the number and short names of the steps of each walk-through. The text, the sources, the Bangla, the
quiz and the walk-throughs themselves are written for this site. Nothing of the course's text, drawings, animations or code is
copied, and the build holds only what the course data is needed for in [`course-outline.json`](course-outline.json).

## Setup

- Python 3.10 or newer, **standard library only** for the build. It takes under a second.
- A code block that is not in [`code-cache.json`](code-cache.json) yet needs Shiki, to colour it the way the other Parts are
  coloured. It is not a dependency of the site, so install it in a work directory and point `SHIKI_WORK` at it. Run
  `npm init -y` first, or npm may install into a parent directory instead:

  ```bash
  export SHIKI_WORK=~/system-design-shiki     # default: <temp dir>/system-design-shiki
  mkdir -p "$SHIKI_WORK" && (cd "$SHIKI_WORK" && npm init -y && npm i shiki)
  ```

  Commit the new `code-cache.json` with the change. Without a new code block, nothing needs Shiki.
- For the source check only: `pip install requests`, and `pdftotext` (poppler-utils) for the sources that are PDFs.
- For the browser audits only: see [Audits](#audits).

Run every command from the repository root.

## Building

```bash
python3 scripts/system-design/build.py            # writes the two JSON files
python3 scripts/system-design/build.py --check    # writes nothing; exits 1 if the files on disk are not what the sources build
```

A build that finds any problem prints each one and writes nothing. After a change, also run `npm test`, `npm run lint`,
`npx tsc --noEmit` and `npm run build`.

## What is where

| File | What it holds |
| --- | --- |
| `m1.py` … `m9.py`, `m3b.py` | The 40 sections, in the course's order: title, intro, and the Technical, Layman's and বাংলা voices. One file for each course module (`m3` and `m3b` are the one *Data and storage* module) |
| `basics_a.py`, `basics_b.py` | The "Start here" box of each section, English and Bangla |
| `walks_m1.py`, `walks_l04.py` … `walks_l40.py` | The step-by-step walk-throughs: `walks_m1.py` has lessons 1 to 3, and each other file has one lesson. Built with `walkkit.py` |
| `part.py` | The Part's title, tagline, lede, the 5 quiz questions and the 3 interview questions |
| `sources.py`, `claims.py` | The cited sources, and the phrases each one is cited for |
| `dsl.py`, `walkkit.py` | Small helpers that return blocks and walk-through steps in the site's content schema |
| `course-outline.json` | The lessons' order, titles, lengths and step names (see below) |
| `build.py` | The build and every check |
| `check_sources.py` | Fetches every source and checks it still contains what it is cited for |
| `highlight.mjs`, `code-cache.json` | Shiki, and the coloured code it made |
| `review_packets.py` | Writes each section as plain text, both languages, for someone to proofread |
| `extract_outline.py` | Writes `course-outline.json` from the course's data |
| `audit/` | Browser checks of the built site |

The schema these files build to is [`src/lib/content-schema.ts`](../../src/lib/content-schema.ts), and the page and the player
that show it are `src/components/content/SectionView.tsx` and `StepPlayer.tsx`. The format of a section and of a walk-through is
in [`docs/content-guide.md`](../../docs/content-guide.md).

## What the build checks

- Citations: a source is cited in the text as `[[key]]`. The key must be in `sources.py`, and the build turns it into a numbered
  link, numbered in order of first use. Only the Technical voice, the English intro and the lede may cite; the Layman's voice,
  the বাংলা voice, the Bangla intro and the walk-throughs may not.
- Inline HTML stays within the allowed tags, heading ids are unique, no voice is empty, and code is highlighted.
- The lessons are in the course's order, with the course's titles, and each walk-through has the course's number of steps with
  the course's short step names.
- Each "Start here" box passes `check_basics`, and each section has one.
- Walk-through language: English text has no Bangla; Bangla text has no Latin digits (outside code) and does have Bangla; a step
  has no links; a step label is at most 24 characters and a box line at most 32; node ids match `[a-z][a-z0-9-]*`; a diagram has at
  most 6 readouts.
- Walk-through layout: boxes fit and keep apart, no line runs through a third box, and no line label sits on a box.
- The quiz has 5 questions with unique ids and answers that are not all at the same option, and there are exactly 3
  interview questions.

## Checking

- `npm test` runs `build.py --check` (when Python 3.10+ is installed), so the JSON cannot drift from these sources.
- `python3 scripts/system-design/check_sources.py` fetches each source and checks the phrases it is cited for. It caches the
  page text in `scripts/system-design/cache/` (not committed; delete a file to fetch it again). `python3
  scripts/system-design/claims.py` re-runs the claims against that cache. Both go to the network, so they are not part of the
  tests.
- `python3 scripts/system-design/review_packets.py` writes one text file for each section, with both languages and the whole
  walk-through, into `scripts/system-design/review-packets/` (not committed). It is what to hand to a proofreader.

## The course outline

`course-outline.json` holds the modules and the order of their lessons, and for each lesson its title, its length in minutes and the
short name of each step. The build uses it to give each section its place ("lesson 3 of 5"), to keep the Part's titles and
step counts the same as the course's, and to say on each link card how long the original lesson is. It is the same
information that the Part already shows. The course's own text, figures and code are not in it.

To refresh it after the course changes, save the course's lesson data and run `python3 scripts/system-design/extract_outline.py
<lessons.json>`. The build then names every lesson or step that no longer matches.

## Audits

Real-browser checks of a build of the site. They need Chrome or Chromium and `playwright-core`, which is not a dependency of the
site, so they look for it the way [`scripts/screenshots`](../screenshots/README.md) does:

```bash
export SHOTS_WORK=~/readme-screenshots     # where `npm init -y && npm i playwright-core` was run
export CHROME=/path/to/chrome              # default /usr/bin/google-chrome
PAGES_BASE_PATH=/ai-learning-roadmap npm run build
node scripts/system-design/audit/serve.mjs 8941 /ai-learning-roadmap &        # the site, as GitHub Pages serves it
node scripts/system-design/audit/check-walk-dom.mjs   http://127.0.0.1:8941/ai-learning-roadmap [s1 s7 ...]
node scripts/system-design/audit/phone-focus-all.mjs  http://127.0.0.1:8941/ai-learning-roadmap [s1 s7 ...]
node scripts/system-design/audit/lazy-walk-check.mjs  http://127.0.0.1:8941/ai-learning-roadmap
```

Each script takes `PART=<slug>` to check the walk-throughs of another Part, as in
`PART=llm-fundamentals node scripts/system-design/audit/check-walk-dom.mjs <base-url>`. Without it they check Part 18.
The offline check counts the walk-through files of every Part.

`npm run build` runs `next build` and then `scripts/precache.mjs`, which writes the offline list into `out/sw.js`. If
`next build` exits 1, the second step does not run, and the offline check then finds no files. Run `node scripts/precache.mjs`
after the build to get what a clean `npm run build` writes.

| Script | What it checks | Where it looks |
| --- | --- | --- |
| `check-walk-dom.mjs` | On every step of every walk-through, in both languages: text inside its box, boxes inside the diagram, no label on a box or on another label, no readout cut. It tests itself first with an over-long label | Desktop width |
| `phone-focus-all.mjs` | On every step, on a 390 px phone: the boxes the step is about are at the middle of the scrolling frame, or inside it where the scroll stops. It tests itself first by shifting the frame | Phone width |
| `lazy-walk-check.mjs` | Each walk-through is a file that is fetched when its section is shown (once, for both languages), a failed fetch shows Try again, and after the service worker has saved the site a walk-through opens with the network off | Chrome, with the service worker |

A script exits 1 and prints each problem it finds. Leave the server running between scripts, and stop it afterwards.
