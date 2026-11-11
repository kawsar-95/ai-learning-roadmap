# Content guide

How the content files are built, what the build checks, and how to add or
change a Part without breaking a reader's saved progress.

## Contents

- [Where content lives](#where-content-lives)
- [What checks the content](#what-checks-the-content)
- [The Part file](#the-part-file)
- [Sections](#sections)
- [Keep ids stable](#keep-ids-stable)
- [Inline HTML](#inline-html)
- [Block types](#block-types)
- [Code blocks](#code-blocks)
- [Diagrams](#diagrams)
- [Citations and sources](#citations-and-sources)
- [Videos](#videos)
- [Live views](#live-views)
- [Practice tasks](#practice-tasks)
- [Quizzes](#quizzes)
- [Interview questions](#interview-questions)
- [Adding a Part](#adding-a-part)

## Where content lives

| Path | What | Edit by hand? |
| --- | --- | --- |
| `src/content/<slug>.json` | One Part: its sections in three voices, sources, quiz | Yes |
| `src/content/interview.json` | Three interview questions for each Part | Yes |
| `src/data/roadmap-phases.json` | Roadmap stages and phase summaries | Yes ([roadmap.md](roadmap.md)) |
| `src/data/roadmap-lessons.json` | Every roadmap phase and lesson | No, generated |
| `src/content/lessons/` | The copied curriculum lessons | No, copied |

The writing rules for every voice are in
[CONTRIBUTING.md](../CONTRIBUTING.md#writing-rules).

## What checks the content

- **The build.** `src/lib/topics.ts` parses each Part with
  `TopicFileSchema` (`src/lib/content-schema.ts`). Every object is strict:
  a missing field, a wrong type, or an unknown key stops `npm run build`.
  The error lists each problem with its `path`, for example
  `["sections", 1, "body", 2, "html"]`. `InterviewPage.tsx` checks
  `interview.json` the same way.
- **The tests.** `npm test` reads the real files too:
  - every Part has a quiz of 5 questions that follows the
    [quiz rules](#quizzes);
  - every Part and section has its Bangla title and intro;
  - every video follows the [video rules](#videos);
  - `interview.json` has 3 questions per Part, in Part order, each tied to a
    real section.

Run both after a content change. The schema is the reference: if this guide
and `content-schema.ts` disagree, the schema wins.

## The Part file

```json
{
  "slug": "inference",
  "title": "Inference",
  "tagline": "optional, shown in italics under the title",
  "lede": "The intro under the title. Inline HTML.",
  "bn": {
    "title": "ইনফারেন্স (মডেল চালানো)",
    "tagline": "optional",
    "lede": "Bangla intro. Inline HTML."
  },
  "sections": [],
  "sources": [],
  "quiz": []
}
```

| Key | Type | Notes |
| --- | --- | --- |
| `slug` | string | Must equal the file name and its entry in `TOPIC_ORDER`. It is the URL: `/topics/<slug>/`. |
| `title`, `tagline` | plain text | `tagline` is optional. |
| `lede` | [inline HTML](#inline-html) | One or two sentences. |
| `bn` | object | `title` and `lede` are required, `tagline` is optional. |
| `sections` | array | See [Sections](#sections). |
| `sources` | array | See [Citations and sources](#citations-and-sources). |
| `quiz` | array | Optional in the schema. The tests require 5 questions. |

The Part number is not in the file. It is the slug's position in
`TOPIC_ORDER` in `src/lib/topics.ts`.

## Sections

```json
{
  "id": "s1",
  "num": "01",
  "title": "Tokens, tokenization & context cost",
  "sub": "The section intro. Inline HTML.",
  "bn": { "title": "টোকেন, টোকেনাইজেশন আর কনটেক্সটের খরচ", "sub": "Bangla intro." },
  "body": [],
  "layman": [],
  "bangla": [],
  "videos": [],
  "embeds": [],
  "practice": []
}
```

| Key | Notes |
| --- | --- |
| `id` | The section's address (`#s1`) and its progress key. Never change it: see [Keep ids stable](#keep-ids-stable). |
| `num` | The number readers see, two digits, in reading order: `"01"`, `"02"`. It may differ from the id. |
| `title`, `sub`, `bn` | The title and intro in each language. `bn.title` must not be empty. |
| `body` | The Technical voice: a list of [blocks](#block-types). |
| `layman` | The Layman's voice: plain English, analogies, no jargon. |
| `bangla` | The বাংলা voice. |
| `videos` | Optional. See [Videos](#videos). |
| `embeds` | Optional. See [Live views](#live-views). |
| `practice` | Optional, at least one task when present. See [Practice tasks](#practice-tasks). |

A voice with an empty list has no tab. The voice switcher shows only when a
section has two or more voices.

## Keep ids stable

Readers' progress and bookmarks are saved as `"<part slug>/<section id>"`,
and links point at section and heading ids. So:

- Do not rename a section `id` or a heading `id`.
- To split a long section, keep the original id on the first half and give
  the second half a new id. Renumber `num` to keep the reading order. A done
  mark, a bookmark, or a link to the old id still works, and a link to a
  heading that moved opens the half that holds it.
- Removing a section is safe for the site: its saved key stays in the
  browser and stops counting. Update `interview.json` if a question pointed
  at it.

## Inline HTML

Fields marked "inline HTML" (`lede`, `sub`, paragraphs, list items, table
cells, captions, notes) allow only these tags:

| Tag | Use |
| --- | --- |
| `<strong>`, `<em>`, `<code>` | Emphasis and code words. No attributes. |
| `<br>` | A line break. |
| `<a class="cite" href="#src12">[12]</a>` | A citation of source 12. |
| `<a href="https://...">text</a>` | A link out. No other attributes. |

Any other tag or attribute fails the build. To show a literal `<` or `>`,
write `&lt;` and `&gt;`. Text inside JSON is escaped JSON, so a quote is `\"`.

## Block types

`body`, `layman`, and `bangla` are lists of blocks. Each block has a `type`.

| `type` | Fields | Renders as |
| --- | --- | --- |
| `paragraph` | `html` | A paragraph. |
| `heading` | `level` (3 or 4), `id`, `html` | A subheading. Only level 3 headings of a one-section Part appear in "On this page". |
| `list` | `ordered`, `items` | A bulleted or numbered list. |
| `code` | `lang`, `code`, `html` | A highlighted code block. See [Code blocks](#code-blocks). |
| `diagram` | `svg`, `caption?`, `captionBn?` | An SVG figure. See [Diagrams](#diagrams). |
| `callout` | `variant`, `blocks` | A tinted box. `variant` is `info`, `good`, `warn`, `danger`, or `pink`. |
| `analogy` | `blocks` | An analogy box. |
| `pillGrid` | `items` (each `label`, `value`) | A grid of short label and value pairs. |
| `table` | `headers`, `rows` | A table. Cells are inline HTML. |
| `panels` | `panels` (each `heading`, `blocks`) | Side-by-side panels. |
| `divider` | none | A rule. |
| `html` | `html` | Raw HTML with no allowlist. No Part uses it. Prefer the other types. |

`callout`, `analogy`, and `panels` hold blocks, so they can nest.

**Heading ids** are written as `<section id>-<words of the heading>`, for
example `s1-what-is-a-token`. An id must be unique in its Part, because all
sections of a Part are on one page.

```json
{ "type": "heading", "level": 3, "id": "s1-what-is-a-token", "html": "What is a token?" }
{ "type": "callout", "variant": "warn", "blocks": [
  { "type": "paragraph", "html": "<strong>Watch out:</strong> long context is not free." }
] }
{ "type": "table", "headers": ["Model", "Best for"], "rows": [["Reasoning", "Math and proofs"]] }
```

## Code blocks

```json
{
  "type": "code",
  "lang": "python",
  "code": "print(\"hello\")",
  "html": "<pre class=\"shiki github-dark-dimmed\" ...>...</pre>"
}
```

- `code` is the plain source. Search reads it.
- `lang` is the label in the corner of the block. `"text"` shows no label.
- `html` is the highlighted HTML that [Shiki](https://shiki.style/) returns
  for `codeToHtml(code, { lang, theme: "github-dark-dimmed" })`. Shiki is
  not a dependency of the site, so make the HTML once, outside the repo:

  ```bash
  mkdir -p ~/shiki && cd ~/shiki && npm init -y && npm i shiki
  # Put the code in snippet.txt, then (python is the language):
  node --input-type=module -e '
    import { codeToHtml } from "shiki";
    import { readFileSync } from "node:fs";
    const code = readFileSync(process.argv[1], "utf8").replace(/\n$/, "");
    console.log(JSON.stringify(await codeToHtml(code, { lang: process.argv[2], theme: "github-dark-dimmed" })));
  ' snippet.txt python
  ```

  Paste the printed string as `html`, and the same code (without the
  trailing newline) as `code`. If Shiki does not know the language, make the
  HTML with `text` and keep the real name in `lang`, as the `promql` block in
  Part 17 does.

## Diagrams

```json
{
  "type": "diagram",
  "svg": "<svg viewBox=\"0 0 1100 280\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\" aria-label=\"Tokenization of a sample sentence\">...</svg>",
  "caption": "What the diagram shows. Inline HTML.",
  "captionBn": "The same in Bangla."
}
```

- The SVG goes into the page as it is. Give it a `viewBox`, `role="img"`,
  and an `aria-label`. It scales to the column and scrolls sideways below
  640 px.
- Ids inside an SVG (arrow markers, gradients) share the page with every
  other diagram of the Part. Make them unique, for example `arr1`, `arr2`.
- Draw for a dark ground with the palette below. The light theme maps each
  of these colors to a darker or lighter one (`src/app/globals.css`). Other
  solid colors stay as they are in both themes.

| Use | Colors the light theme maps |
| --- | --- |
| Box fills | `#0b0f17`, `#0f172a`, `#111827` |
| Text | `#cfd8e6`, `#e2e8f0` (main), `#a8b5c8`, `#94a3b8` (secondary) |
| Borders and arrows (stroke) | `#334155`, `#1f2937`, `#94a3b8` |
| Accents (fill or stroke) | `#22d3ee`, `#34d399`, `#a78bfa`, `#fbbf24`, `#fb7185`, `#f472b6` |

Low-alpha `rgba()` tints work on both grounds and stay as they are.

## Citations and sources

```json
"sources": [
  { "n": 1, "url": "https://arxiv.org/abs/2005.14165", "text": "Brown et al., \"Language Models are Few-Shot Learners\" — GPT-3 (NeurIPS 2020)" }
]
```

- Cite with `<a class="cite" href="#src1">[1]</a>` in any inline field. The
  link jumps to the source list at the end of the Part.
- `n` is the number readers see. Keep it unique in the Part, and give a new
  source the next free number. The list shows in file order.
- Cite the primary source: the paper, the vendor's documentation, or the
  team's own post. Open the page and check that it says what you cite it
  for.

## Videos

```json
"videos": [
  { "id": "zduSFxRajkE", "title": "Let's build the GPT Tokenizer", "channel": "Andrej Karpathy", "lang": "en" },
  { "id": "P-mv2hQc43E", "title": "What Actually is an AI Token? (Simply Explained)", "channel": "KodeKloud", "lang": "en", "format": "short", "seconds": 174 }
]
```

| Field | Rule |
| --- | --- |
| `id` | The 11-character YouTube id. |
| `title` | The published title without hashtags and emoji, otherwise unchanged (`storedTitle()` in `src/lib/video-check.ts`). |
| `channel` | The channel name as YouTube's oEmbed gives it (`author_name`), with no outer spaces. |
| `lang` | `en` or `bn`: the language spoken. |
| `format` | `"short"` for a vertical YouTube Short. Leave it out for a normal video. |
| `seconds` | The length. Required for a Short, and at most 180. A normal video, when given, is at least 10. |

- A section lists a video once. The same video may appear in two sections
  (Part 16 lists some clips of earlier Parts on purpose).
- The English site shows English videos with Technical and Layman's, and
  Bangla videos first with বাংলা. The Bangla site shows Bangla videos first
  in every voice.
- `npm run check:videos` asks YouTube whether each video is still public,
  embeddable, under the same title and channel, and (for a Short) still a
  Short. `npm run check:videos -- --channel KodeKloud` checks one channel.
  It exits 0 when all is well, 1 when a video has a problem, and 2 when it
  could not check. It needs the network, so the tests and the deploy do not
  run it.
- How the current clips were found, read, and verified is in
  [scripts/video-curation/README.md](../scripts/video-curation/README.md).
  Every clip added or left out is in
  [video-review-log.md](video-review-log.md).

## Live views

A live view shows another site's interactive page in a frame, under the
section intro. Part 15 uses them.

```json
"embeds": [
  {
    "url": "https://poloclub.github.io/transformer-explainer/",
    "title": "Transformer Explainer",
    "note": "What to try in the page. Inline HTML.",
    "noteBn": "The same in Bangla.",
    "height": 720
  }
]
```

| Field | Rule |
| --- | --- |
| `url` | https, on a host in `FRAMEABLE_HOSTS` or `LINK_ONLY_HOSTS` in `src/lib/content-schema.ts`. |
| `title`, `note`, `noteBn` | Required and not empty. |
| `frame` | `false` for a host that refuses framing: the site shows a link card. Required for `LINK_ONLY_HOSTS`. |
| `autoload` | Load when the frame nears the screen, not on click. Only for light pages, and never with `frame: false`. |
| `height` | Frame height, 320 to 1000 px. The default is 640. |
| `designWidth` | For a page made for a wide screen: its width, 600 to 1600 px. |

**A new host.** Check that the page may be framed before you add its host
to `FRAMEABLE_HOSTS`:

```bash
curl -sIL https://example.org/page | grep -iE 'x-frame-options|content-security-policy'
```

An `X-Frame-Options` header, or a `frame-ancestors` rule that leaves out
other sites, blocks the frame. For example, the two Substack hosts in
`LINK_ONLY_HOSTS` answer with this header:

```text
content-security-policy: frame-ancestors 'self' https://*.substack.com https://substack.com
```

Such a host goes in `LINK_ONLY_HOSTS`, and its embeds set `"frame": false`.
Load the page in the built site as well.

## Practice tasks

A practice task is done in any free AI chat (ChatGPT, Claude, or Gemini),
with no install and no API key. Each task has an English and a Bangla
version with the same steps.

```json
"practice": [
  {
    "en": {
      "title": "Cut the prompt, keep the answer",
      "why": "Why the reader should care. Inline HTML.",
      "steps": [
        {
          "chat": "new",
          "do": "Copy this long prompt, paste it, and press Enter. Write down the answer.",
          "prompt": "Plain text to copy.",
          "expect": "One word, most likely <em>defect</em>.",
          "example": "A sample answer. Plain text."
        },
        { "chat": "same", "do": "The next step. Inline HTML.", "expect": "What the reader should see." }
      ],
      "learned": "What just happened.",
      "done": "You are done when ...",
      "check": { "question": "A question to check yourself.", "answer": "Its answer." },
      "challenge": "A harder version."
    },
    "bn": { "title": "...", "why": "...", "steps": [], "learned": "...", "done": "...", "check": { "question": "...", "answer": "..." }, "challenge": "..." }
  }
]
```

- `chat` is `new` (open a new chat) or `same` (keep typing in the open one).
  The first step must be `new`.
- `title` is plain text. `prompt` and `example` are plain text and optional.
  The other fields are inline HTML. No field may be empty.
- Use made-up data. A task must never ask the reader to paste private
  information.

## Quizzes

The quiz format is in [quizzes.md](quizzes.md). The tests add these rules:

- Every Part has exactly 5 questions.
- Bangla text writes plain numbers in Bangla digits. Digits inside a name or
  a code word (GPT-4o, H100, `top_p`) stay Latin.
- Bangla text says "এই Part", never "Topic" or "Text".
- The right answers of a Part are not all at the same option.
- Across the Parts with two true or false questions, at most half put
  false before true.

## Interview questions

`src/content/interview.json` has one entry per Part, in Part order:

```json
{
  "parts": [
    {
      "topic": "llm-fundamentals",
      "items": [
        {
          "section": "s1",
          "en": { "q": "Why do engineers count tokens, and how does the length of a prompt change cost and latency?", "a": "Two to four sentences." },
          "bn": { "q": "...", "a": "..." }
        }
      ]
    }
  ]
}
```

- Exactly 3 items per Part. `section` must be a section id of that Part.
- The text is plain text. Each answer is 2 to 4 sentences and uses only
  facts the linked section states.

## Adding a Part

1. Write `src/content/<slug>.json`, with sections in all three voices,
   sources, and a 5-question quiz.
2. In `src/lib/topics.ts`, import the file, add it to `FILES`, and put the
   slug in `TOPIC_ORDER` where it belongs. The position sets the Part
   number.
3. Add its 3 questions to `src/content/interview.json`, at the same
   position.
4. Link it from the roadmap phases that cover the same ground: the `topics`
   list of each phase in `src/data/roadmap-phases.json`.
5. Update the places that state the Part count or list the Parts:
   - `src/lib/i18n.ts`, in both dictionaries: `footer`, `metaDescription`,
     `searchAll`, `searchType`, `partsTitle`, `notFoundText`;
   - the `description` in `src/app/layout.tsx` and in
     `src/app/manifest.ts`;
   - `tests/roadmap.test.ts` (the Part count) and `tests/interview.test.ts`
     (`PART_ORDER`);
   - the counts and the Parts table in `README.md`.
6. Run `npm test`, `npm run lint`, and `npm run build`, then read the new
   Part in both languages and both themes.
7. Retake the README screenshots that show the list of Parts
   ([scripts/screenshots/README.md](../scripts/screenshots/README.md)).
