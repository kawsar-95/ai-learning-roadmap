# README screenshots

`take-screenshots.mjs` takes the images in [`screenshots/`](../../screenshots/)
that the [README](../../README.md) shows. It shoots the production build, so
the images have no development badge and match what GitHub Pages serves.

## Setup

- **Chrome or Chromium.** The default is `/usr/bin/google-chrome`. Set
  `CHROME=/path/to/chrome` for another one.
- **`playwright-core`, outside the repo.** It is not a dependency of the
  site. Install it in a work directory and point `SHOTS_WORK` at it. Run
  `npm init -y` first, or npm may install into a parent directory instead:

  ```bash
  export SHOTS_WORK=~/readme-screenshots    # default: <temp dir>/readme-screenshots
  mkdir -p "$SHOTS_WORK" && (cd "$SHOTS_WORK" && npm init -y && npm i playwright-core)
  ```

- **A network connection** for two shots: `videos` loads YouTube
  thumbnails, and `live-view` loads a page from another site.

## Taking the shots

```bash
npm run build                                          # without PAGES_BASE_PATH
node scripts/screenshots/take-screenshots.mjs          # every shot
node scripts/screenshots/take-screenshots.mjs quiz voices   # only these
```

The script serves `out/` itself on port 8017 (`SHOTS_PORT` changes it) and
stops the server when it is done. It prints each file and its size:

```text
screenshots/videos.png  316 KB
```

It stops with `out/ has no build` when there is no build. An unknown shot
name prints the list of known names.

## The shots

Desktop shots are 1440 × 900 at 1x in the light theme. Phone shots are
390 × 844 at 2x in the dark theme, with touch.

| Shot | Page | What it shows | README section |
| --- | --- | --- | --- |
| `home` | `/` | The hero, cropped below the counts | top |
| `topic-page` | `/topics/llm-fundamentals/` | The first screen of Part 1 | Read one section at a time |
| `voices` | `/topics/llm-fundamentals/` | Section 1 in each voice, three crops side by side | Three voices |
| `practice` | `/topics/llm-fundamentals/` | Section 1's practice panel, open, to the end of step 1 | Practice, videos, and a quiz |
| `videos` | `/topics/llm-fundamentals/` | Section 1's Watch list, open: three videos, then three Shorts | Practice, videos, and a quiz |
| `quiz` | `/topics/llm-fundamentals/#quiz` | The quiz answered with question 4 wrong, then checked: questions 4 and 5 and the score | Practice, videos, and a quiz |
| `search` | `/topics/llm-fundamentals/` | The search dialog with "kv cache" | Search everything |
| `roadmap` | `/roadmap/` | The title and the learning paths | A study roadmap |
| `lesson` | `/roadmap/07-transformers-deep-dive/02-self-attention-from-scratch/` | A lesson page | A study roadmap |
| `contents` | `/contents/` | Progress with the demo state | Progress that stays in your browser |
| `dashboard` | `/dashboard/` | Continue reading and three bookmarks | Progress that stays in your browser |
| `interview` | `/interview/` | The first question open | Interview questions and open-source repos |
| `resources` | `/resources/` | The first cards | Interview questions and open-source repos |
| `bangla-topic` | `/bn/topics/llm-fundamentals/` | Part 1 on the Bangla site | English and বাংলা |
| `themes` | `/topics/llm-fundamentals/` | The light and the dark theme, split on a diagonal | Light and dark |
| `mobile-topic` | `/topics/llm-fundamentals/` | Part 1 on a phone | Phones, install, and offline |
| `mobile-menu` | `/topics/llm-fundamentals/` | The menu drawer, open | Phones, install, and offline |
| `roadmap-progress` | `/roadmap/` | The progress card, the filter, and Phase 0 with its lessons open | More screenshots |
| `live-view` | `/topics/visual-learning-resources/` | The first live view, loaded, with its intro card closed | More screenshots |

## Demo state

Each shot opens in a new browser context with service workers blocked. The
script writes these `localStorage` keys before the first paint, so the
progress pages have something to show:

| Key | Demo value |
| --- | --- |
| `theme` | `light`, or `dark` for the phone and the dark half of `themes` |
| `progress` | every section of Part 1 and the first 3 of Part 2: 13 done |
| `bookmarks` | three sections, from Parts 2, 5, and 6 |
| `quiz-scores` | Part 1: 5 / 5, Part 2: 4 / 5 |
| `roadmap-progress` | lessons 1 to 6 of Phase 0 and 1 to 3 of Phase 1: 9 done |
| `voice` | `main`, `layman`, or `bangla`, for the three crops of `voices` |

The keys and their formats are in
[docs/architecture.md](../../docs/architecture.md#reader-state).

## After a run

- Look at every new image. Check for clipping, for a state that matches the
  README text (counts, the open panel, the selected voice), and for a
  half-loaded thumbnail or frame.
- Keep the `alt` text in the README true to the image. It is what a screen
  reader reads, and what shows when an image does not load.
- The script warns about page errors and thumbnails that did not load. A
  crop that matches a hidden element stops the run with
  `clip ... is too small`.
- Commit the images with the change that made them.
