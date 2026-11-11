# Roadmap and resources

The roadmap is a study path through the open
[AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
curriculum by Rohit Ghumare and contributors (MIT license). This file covers
its data, its pages, how to refresh the copied lessons, the learning paths,
and the resources page.

## Contents

- [At a glance](#at-a-glance)
- [Data files](#data-files)
- [What checks the data](#what-checks-the-data)
- [The roadmap page](#the-roadmap-page)
- [Lesson pages](#lesson-pages)
- [Progress](#progress)
- [Refreshing the curriculum](#refreshing-the-curriculum)
- [Learning paths](#learning-paths)
- [The resources page](#the-resources-page)

## At a glance

| What | Count |
| --- | --- |
| Stages | 7 |
| Phases | 20, numbered 0 to 19 |
| Suggested phases | 15 |
| Optional phases | 5: Computer Vision (4), Speech & Audio (6), Generative AI (8), Reinforcement Learning (9), Multimodal AI (12) |
| Lessons | 542, each a page in both languages |
| Learning paths | 8 |
| Copied from | commit `3f9715c` of the curriculum (`src/content/lessons/source.json`) |

| Stage | Phases |
| --- | --- |
| Foundations | 0 to 3 |
| Vision, language and speech | 4 to 6 |
| Transformers and LLMs | 7 to 10 |
| Building with LLMs | 11 to 13 |
| Agents | 14 to 16 |
| Production and safety | 17, 18 |
| Capstone | 19 |

## Data files

| File | Made by | Holds |
| --- | --- | --- |
| `src/data/roadmap-lessons.json` | `scripts/build-roadmap.mjs` | Every phase and lesson, in order |
| `src/data/roadmap-phases.json` | hand | The stages, and for each phase: suggested or optional, a summary in both languages, the related Parts |
| `src/content/lessons/<phase folder>/<lesson dir>.md` | `scripts/import-lessons.mjs` | The English text of each lesson |
| `src/content/lessons/LICENSE` | `scripts/import-lessons.mjs` | The curriculum's MIT license |
| `src/content/lessons/source.json` | `scripts/import-lessons.mjs` | The repository and commit of the copy |

Do not edit the generated files by hand. Run the scripts again (see
[Refreshing the curriculum](#refreshing-the-curriculum)).

**roadmap-lessons.json**

```json
{
  "phases": [
    {
      "phase": 0,
      "folder": "00-setup-and-tooling",
      "title": "Setup & Tooling",
      "hours": 16,
      "lessons": [
        { "n": 1, "title": "Dev Environment", "dir": "01-dev-environment", "minutes": 75 }
      ]
    }
  ]
}
```

`hours` is the estimate the curriculum states for the phase. The site shows
the sum of the lesson `minutes` instead, so the two can differ (15.5 h
against 16 for Phase 0).

**roadmap-phases.json**

```json
{
  "stages": [
    {
      "id": "foundations",
      "phases": [0, 1, 2, 3],
      "title": "Foundations",
      "summary": "Tooling, math, classical ML and deep learning. Everything later stands on this.",
      "bn": { "title": "ভিত্তি", "summary": "..." }
    }
  ],
  "phases": [
    {
      "phase": 0,
      "core": true,
      "topics": ["deploying-and-operating-ai-systems"],
      "summary": "Set up Python, Git, Docker, GPUs and API keys so every later lesson runs.",
      "bn": "..."
    }
  ]
}
```

- `core: true` puts the phase on the suggested path. `false` marks it as
  optional depth.
- `topics` lists the slugs of the Parts that cover the same ground. The
  phase card links to them under "Covered in the Parts".
- Lesson titles stay in English on both sites. Stage titles and summaries,
  and phase summaries, have a Bangla version.

## What checks the data

`src/lib/roadmap.ts` runs `buildRoadmap` (`src/lib/roadmap-schema.ts`) when
the build loads it. It parses both files with strict schemas and stops the
build if:

- a phase in one file has no entry in the other;
- a phase is listed twice, or has two lessons with the same number;
- a stage names a phase that does not exist, a phase is in two stages, or a
  phase is in no stage.

`npm test` adds these checks (`tests/roadmap.test.ts`,
`tests/lesson-markdown.test.ts`):

- there are 20 phases, numbered 0 to 19 in stage order, with 542 lessons;
- every phase and stage has its Bangla text;
- every related Part exists;
- lesson keys are unique;
- every lesson has its copied text, renders, and links only to lessons that
  exist.

## The roadmap page

`/roadmap/` (`src/components/pages/RoadmapPage.tsx`), from top to bottom:

1. The title and intro.
2. **Learning paths**: eight cards. The first, "New to AI engineering", is
   marked **Start here**. See [Learning paths](#learning-paths).
3. A link to the resources page.
4. **Progress**: lessons done, total lessons, and time left to study (the
   sum of the minutes of the lessons not done). **Continue reading** opens
   the first lesson not done, and **Start over** clears the roadmap
   progress after a confirmation.
5. **Show the suggested path only**: a switch that hides the five optional
   phases. It does not change the counts, and it is not saved.
6. The 7 stages. Each phase is a card: its number, **Suggested** or
   **Optional depth**, the title and summary, the lesson count and length,
   the related Parts, a progress bar with **Mark as read**, and a closed
   list of its lessons. Each lesson row has a done toggle, its number, its
   title (a link to the lesson page), and its length.
7. The source line, with a link to the curriculum on GitHub.

A phase card has the id `phase-<n>`, so `/roadmap/#phase-7` opens Phase 7.

## Lesson pages

`/roadmap/<phase folder>/<lesson dir>/`
(`src/components/pages/LessonPage.tsx`) shows one lesson:

- a meta line: **Roadmap** (a link back to the phase), the phase number and
  title, and the lesson length;
- the done toggle, and **Code and tests on GitHub**, which opens the lesson
  folder at the copied commit;
- the title, then the lesson text;
- "On this page" when the lesson has three or more level 2 headings: a
  column on the right from 1280 px, a closed list above the text below that;
- links to the previous and next lesson, across phases;
- a credit line with a link to the curriculum's MIT license.

How the Markdown becomes HTML (math, links, escaping) is in
[architecture.md](architecture.md#roadmap-lessons). Lesson pages are not
saved for offline use. 1,084 pages would make the install too large.

## Progress

The done lessons are saved in `localStorage` key `roadmap-progress`, as a
JSON array of `"<phase>/<lesson number>"`, for example `"7/2"`. The key
uses the lesson number, not its folder name. If the curriculum renumbers the
lessons of a phase, saved ticks point at other lessons.

## Refreshing the curriculum

Run this when the curriculum adds or changes lessons. Both scripts take the
path of a local clone.

```bash
git clone https://github.com/rohitg00/ai-engineering-from-scratch.git ../ai-engineering-from-scratch
node scripts/build-roadmap.mjs ../ai-engineering-from-scratch
node scripts/import-lessons.mjs ../ai-engineering-from-scratch
```

1. `build-roadmap.mjs` reads the curriculum's `ROADMAP.md` and rewrites
   `src/data/roadmap-lessons.json`. It reads each phase heading, such as
   `## Phase N: Title — ... (~H hours)`, and each lesson row, such as
   `| n | [Title](link) | ... | ~75 min |`. A row without a link (Phase 0)
   is matched to its folder by number. It stops with an error if a folder
   is missing, and prints `Wrote 20 phases and 542 lessons to ...`.
2. `import-lessons.mjs` deletes `src/content/lessons/`, then copies each
   lesson's `docs/en.md`, the license, and the commit hash. It prints
   `Copied 542 lessons from commit 3f9715c to ...`.
3. If the phases changed, update `src/data/roadmap-phases.json`: stages,
   summaries in both languages, and related Parts.
4. If the counts changed, update the tests that pin them
   (`tests/roadmap.test.ts`), the interface strings that say "20 phases"
   (`roadmapIntro` and `roadmapCoreNote` in both dictionaries of
   `src/lib/i18n.ts`), and the counts in `README.md` and this file.
5. Run `npm test` and `npm run build`. The lesson test renders every lesson
   and fails on a link to a lesson that does not exist.
6. Commit the JSON, the lessons, `LICENSE`, and `source.json` together.

To check that the copy is untouched, check out the commit in `source.json`
and run both scripts: `git status` shows no change.

```bash
git -C ../ai-engineering-from-scratch checkout 3f9715c62a3bedcffb68a260f1a65ee2dd9cc10a
```

## Learning paths

The eight paths are written in `PATHS` at the top of
`src/components/pages/RoadmapPage.tsx`:

| Kind | Label | Paths |
| --- | --- | --- |
| `start` | Start here | New to AI engineering |
| `core` | Core path | Build and ship AI apps; Software engineering basics; Work with coding agents; Product judgment |
| `focused` | Focused path | Model Context Protocol (MCP); Agent skills; Agents, LLMs and MCP under the hood |

Each path has an `id`, a `kind`, the first `lesson` (as
`<phase folder>/<lesson dir>`), a `github` link to the path in the
curriculum, and a title and summary in English and Bangla. **Start path**
opens the first lesson on this site. **GitHub** opens the path's file in the
curriculum's `learning-paths/` folder, or the lesson folder for the start
and focused paths. A path's `lesson` must be a lesson in
`roadmap-lessons.json`. No test checks this, so open each **Start path**
link after a refresh.

## The resources page

`/resources/` (`src/components/pages/ResourcesPage.tsx`) lists 20
well-known GitHub repositories in 5 groups. They are written in `GROUPS` at
the top of the file.

| Group | Repositories |
| --- | --- |
| Courses | 4 |
| Cookbooks | 2 |
| Models and training | 5 |
| LLM apps and agents | 6 |
| Serving and running models | 3 |

Each repository has:

- `repo`: `owner/name` on GitHub;
- `phase`: the roadmap phase it fits, shown as a link to that phase;
- `about`: one sentence in English and in Bangla;
- `bangla: true` when the repository has a Bangla translation. The card then
  links to `translations/bn/README.md` in that repository.

Star counts change, so the page does not show them.
