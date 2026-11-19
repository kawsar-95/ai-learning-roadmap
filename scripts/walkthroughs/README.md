# Walk-throughs of Parts 1 to 17

A walk-through is a diagram of one section that changes step by step. Its format is in the
[content guide](../../docs/content-guide.md#walk-throughs). Part 18 builds its 40 with its own generator
([scripts/system-design](../system-design/README.md)). Every other Part keeps each walk-through in a file of its own.
A Part can have one, four, or none, and adding one does not touch the Part's JSON.

Run every command from the repository root. The build needs Python 3.10 or newer and nothing else.

## Building

```bash
python3 scripts/walkthroughs/build.py            # checks every source, then writes the JSON and the index
python3 scripts/walkthroughs/build.py --check    # writes nothing; exits 1 if a file is not what its source builds
```

A build that finds a problem prints each one, with the section, the step and the language, and writes nothing. It never
deletes a file. A JSON file with no source is an error. `npm test` runs `--check`, so it fails when a JSON file and its
source disagree.

## What is where

| File | What it holds |
| --- | --- |
| `<Part>/<section>.py` | One walk-through. It defines `WALK`. `<Part>` is the Part's slug and `<section>` is the section id, as in `llm-fundamentals/s7.py` |
| `kit.py` | The helpers a source uses: `walk`, `node`, `sh`, `ln`, `st`. Every text is a pair, English then Bangla, so the two cannot drift apart. The format is in its docstring |
| `check.py` | The checks every walk-through passes, in any Part: the language rules, the layout, and the kinds of box the site draws. Part 18's generator uses the same file |
| `build.py` | The builder. It adds the size and room rules below, then writes the output |

The output is `src/content/walkthroughs/<Part>/<section>.json` and `src/content/walkthroughs/index.ts`. Do not edit
them by hand.

## The rules

The build holds each walk-through to these. A new kind of box is added in `WALK_NODE_KINDS` first
(`src/lib/content-schema.ts`).

- **Size.** 6 to 9 steps. At most 2 paragraphs in a step, 8 boxes shown in a step and 12 in all, and 4 readouts.
- **Language.** Every English text sits next to its Bangla text. Bangla text has Bangla digits and no Latin ones outside
  code. English text has no Bangla letters.
- **Layout.** Boxes fit in the diagram and keep 8px apart. No line runs through a third box. A line label has room.
- **Room.** A box is at least 10px from the left, right and bottom edge of the diagram, and 15px from the top. Every
  line shows at least 20px, so its arrow can be seen. Both languages are measured, because Bangla labels make a box
  wider and can close a gap that English leaves.
- **Content.** The section carries the citations. A walk-through says what the section says and adds no fact and no
  number of its own. By convention, the top of each source lists the words of the section that each step restates.

## Adding one

1. Read the section in all its voices: Technical, Layman's, বাংলা, and the Start here box.
2. Write `scripts/walkthroughs/<Part>/<section>.py`, then run the build until it prints no problem.
3. Run `npm test`, `npm run lint`, `npx tsc --noEmit` and `npm run build`.
4. Run the browser audits ([below](#audits)) and look at every step in both languages.

## How the site loads them

1. `attachWalkthroughs` (`src/lib/walkthrough-files.ts`, called from `src/lib/topics.ts`) puts each file on its section.
   A file must belong to a section of its Part. A section can have its walk-through in one place only. Each file goes
   through the same schema as Part 18's.
2. `TopicPage.tsx` hands the section a path and not the data, so the page of the Part does not carry the walk-throughs.
3. `/walkthroughs/<Part>/<section>.json` is a static route. `LazyStepPlayer.tsx` fetches it when the section is first
   shown, once for both languages.

## Audits

The browser audits in [`scripts/system-design/audit`](../system-design/README.md#audits) take `PART=<slug>`. Without it
they check Part 18.

```bash
PART=llm-fundamentals node scripts/system-design/audit/check-walk-dom.mjs http://127.0.0.1:8957
```
