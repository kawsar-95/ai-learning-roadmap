# Learn AI — All Necessary Topics Related to AI Engineering

A citation-backed Next.js reference for the topics an applied AI engineer
needs. It has 16 parts, from LLM fundamentals to AI application
architecture, a part with ten visual and interactive learning resources,
and a part on Chip Huyen's *AI Engineering* book, nested by chapter. Each
topic has three voices: Technical (diagrams, code, cited sources),
Layman's (plain English with analogies), and বাংলা (Bangla explanation).

Live site: https://kawsar-95.github.io/ai-learning-roadmap/

## Stack

- **Next.js 16.4** (App Router, static export)
- **React 19**
- **TypeScript 5**
- **Tailwind CSS 4** (CSS-first config in `globals.css`)
- **Zod 4** (content validation at build time)
- **MiniSearch** (search in the browser)

## Running it

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # validates content, then writes the static site to out/
npm test         # runs the tests in tests/
npm run lint
npm run check:videos   # asks YouTube if every video still exists (not part of npm test)
npx serve out    # previews the static build at http://localhost:3000
```

`npm run start` does not work. The site is a static export, so `next start`
has no server build to serve.

## Hosting

The site runs on GitHub Pages. `.github/workflows/deploy-pages.yml` runs on
every push to `main`, and you can also start it from the Actions tab. It:

1. Installs dependencies and runs the tests.
2. Builds the static site with `PAGES_BASE_PATH` set to
   `/ai-learning-roadmap`.
3. Publishes `out/` to GitHub Pages.

A deploy takes about two minutes, and the publishing step a few seconds of
that. If the `deploy` job sits on `deployment_queued`, the workflow cancels
it after 3 minutes. A cancelled deployment cannot be run again for the same
commit (re-running the job answers "Deployment cancelled"), so push a new
commit.

`next.config.ts` reads `PAGES_BASE_PATH` as the `basePath`. Local builds do
not set it, so the site serves from `/`. Code that builds a URL by hand
(not through `next/link` or the router) must add
`process.env.NEXT_PUBLIC_BASE_PATH`, as the search palette does.

## Routes

| Route                       | What it is                                         |
| --------------------------- | -------------------------------------------------- |
| `/`                         | Landing page. An index of the 16 parts.            |
| `/topics/<slug>`            | One part, with prev/next links and an outline.     |
| `/contents/`                | Every section of every part, with reading progress. |
| `/dashboard/`               | Where to continue, bookmarks, and quiz scores.     |
| `/interview/`               | Interview questions and short answers, one set per part. |
| `/resources/`               | Curated open-source repos to learn from, grouped by topic. |
| `/roadmap/`                 | The study roadmap: 20 phases, 542 lessons, grouped into learning paths. |
| `/search-index.json`        | The search index. Built at build time.             |
| `/bn/`, `/bn/topics/<slug>`, `/bn/contents/`, `/bn/dashboard/`, `/bn/interview/`, `/bn/resources/`, `/bn/roadmap/` | The same pages in Bangla. See "Languages". |
| `/bn/search-index.json`     | The Bangla search index.                           |

The 16 parts, in order:

| Part | Route                                      |
| ---- | ------------------------------------------ |
| 1    | `/topics/llm-fundamentals`                 |
| 2    | `/topics/prompt-engineering`               |
| 3    | `/topics/fine-tuning-roadmap`              |
| 4    | `/topics/context-engineering`              |
| 5    | `/topics/rag-knowledge-systems`            |
| 6    | `/topics/agents-and-agentic-systems`       |
| 7    | `/topics/tool-use-and-integrations`        |
| 8    | `/topics/inference`                        |
| 9    | `/topics/llmops-and-observability`         |
| 10   | `/topics/evaluation-engineering`           |
| 11   | `/topics/cost-and-performance-optimization` |
| 12   | `/topics/safety-security-and-guardrails`   |
| 13   | `/topics/multimodal-engineering`           |
| 14   | `/topics/ai-application-architecture`      |
| 15   | `/topics/visual-learning-resources`        |
| 16   | `/topics/ai-engineering-book`              |

The order is set in one place: `TOPIC_ORDER` in `src/lib/topics.ts`.

Only these 16 slugs exist. Any other URL gets the 404 page.

## Content

Each part is one file: `src/content/<slug>.json`. To edit content, edit that
file. `npm run build` validates every file against the schema. A bad file
fails the build.

The schema is in [`src/lib/content-schema.ts`](src/lib/content-schema.ts).
A file has this shape:

```
{ slug, title, tagline?, lede, bn: { title, tagline?, lede }, sections: [...], sources: [...] }
```

Each section has `id`, `num`, `title`, `sub`, `bn: { title, sub }` (the
Bangla title and intro), three lists of blocks
(`body` for Technical, `layman`, and `bangla`), an optional `videos`
list, an optional `embeds` list, and an optional `practice` list.

An embed is a live page from another site, shown under the section intro:
`{ url, title, note, noteBn, frame?, autoload?, height?, designWidth? }`. The schema
accepts only an `https` URL on a host in `FRAMEABLE_HOSTS` or
`LINK_ONLY_HOSTS` (both in `src/lib/content-schema.ts`). A page loads in a
sandboxed frame when the reader clicks. `autoload: true` loads it when it
nears the screen, so use it only for light pages. A publisher that blocks
framing (it sends `frame-ancestors`, as Substack does) goes in
`LINK_ONLY_HOSTS`, and its embed needs `frame: false`. It then shows as a
link card. `designWidth` is for an app that needs a wide screen: the frame
keeps that width and shrinks to fit a narrower column. Before you add a host, open the page in a frame in a real
browser to check that it loads.

A block has a `type`. These are the block types:

| Type        | Purpose                                              |
| ----------- | ---------------------------------------------------- |
| `paragraph` | A paragraph of text.                                 |
| `heading`   | A level 3 or level 4 heading with an `id`.           |
| `list`      | An ordered or unordered list.                        |
| `code`      | A code sample. It stores the source and its highlighted HTML. |
| `diagram`   | An inline SVG with optional captions.                |
| `callout`   | A box with a variant: info, good, warn, danger, or pink. |
| `analogy`   | A box for an analogy.                                |
| `pillGrid`  | A grid of label and value pairs.                     |
| `table`     | A table with headers and rows.                       |
| `panels`    | Side-by-side panels, each with a heading and blocks. |
| `divider`   | A horizontal rule.                                   |
| `html`      | Raw HTML. Use it only when no other type fits.       |

Inline text (`html` fields on paragraphs, headings, list items, and so on)
allows only these tags: `strong`, `em`, `code`, `br`, `a` (a citation link
`<a class="cite" href="#srcN">` or an `http(s)` link). The schema rejects
any other tag.

`src/lib/topics.ts` loads and validates the 16 files, and it exposes the
parts in order. Only server code imports it. Client components get data as
props.

Only these components render raw HTML: `Inline.tsx`, `CodeBlock.tsx`,
`Diagram.tsx`, and `RawHtml.tsx`.

## Videos

Each section can list YouTube videos in `videos`:

```json
{ "id": "zduSFxRajkE", "title": "Let's build the GPT Tokenizer", "channel": "Andrej Karpathy", "lang": "en" }
{ "id": "p7U_98jWqWo", "title": "Claude Code Explained in 60 Seconds", "channel": "KodeKloud", "lang": "en", "format": "short", "seconds": 78 }
```

- `id` is the 11-character YouTube video ID. `lang` is `en` or `bn`.
- Copy `title` and `channel` from YouTube's oEmbed answer:
  `https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=<id>`.
  A 200 answer also confirms that the video is public and allows embedding.
  The stored title is the published one without hashtags and emoji.
- `format: "short"` marks a vertical YouTube Short (9:16, 180 seconds at most).
  `seconds` is the length in whole seconds, and the card shows it. Take it
  from the player (`getDuration()` in the IFrame API), not from a listing.
  Both fields are optional.
- Technical and Layman's show the English videos. বাংলা shows the Bangla
  videos first, then the English ones. All three shows all of them.
- A section shows its videos in a grid and its Shorts under them in a
  vertical grid. A Short has no thumbnail: YouTube's thumbnail for a Short
  is 4:3 with black bars.
- A card loads no player from YouTube until the reader clicks it. The
  thumbnail of a normal video comes from `i.ytimg.com` once its list is
  opened (the list starts closed); a Short loads nothing. After the click,
  the video plays in place through `youtube-nocookie.com`.
- Videos of one channel are other people's work. `npm run check:videos`
  asks YouTube if every video is still public, can still be embedded, and
  still has the stored title and channel, and if a Short is still a Short
  (`-- --channel KodeKloud` checks one channel). It prints one `FAIL` line
  for each problem. Run it by hand. `npm test` and the deploy never run it,
  because a creator can remove a video at any time.

The cards are `src/components/content/VideoList.tsx` and `VideoCard.tsx`.
The voice rule and the length format are in `src/lib/videos.ts`. The check
is `scripts/check-videos.mjs`, and its comparisons are in
`src/lib/video-check.ts`. The scripts that found, read and verified the clips,
and that write `docs/video-coverage.md` and `docs/video-review-log.md`, are in
`scripts/video-curation/` (see its README).

[Video coverage](docs/video-coverage.md) lists the channels the videos and
Shorts come from (KodeKloud, Cole Medin, AI Jason, Krish Naik, David Ondrej,
TechWorld with Nana, Lucas Soares | Automata Learning Lab, and DeepLearningAI),
the technical topics that the site does not cover yet with curated resources
for each, and how a clip is chosen. [Video review log](docs/video-review-log.md)
lists every clip that was added to a section, with what was noticed in it, and
the clips that were read and left out, each with the reason.

## Practice

Each section has a "Practice" panel with guided tasks. A reader does them
in any free AI chat (ChatGPT, Claude, or Gemini). No install, code, or API
key is necessary. In a part with several sections, each section has 1
task. A part with only 1 big section has 4 tasks.

Each task has an English and a Bangla version. The বাংলা voice shows the
Bangla version. The other voices show the English version. The Bangla
version keeps English technical words (prompt, token, model, and so on).

A task is one entry in the section's `practice` list:

```json
{
  "en": {
    "title": "See why the AI gives different answers",
    "why": "A chatbot can give a different answer to the same question.",
    "steps": [
      {
        "chat": "new",
        "do": "Copy this prompt, paste it, and press Enter.",
        "prompt": "Complete this sentence with one word only: Once upon a time, there was a little",
        "expect": "One word, for example <em>girl</em>.",
        "example": "girl"
      },
      { "chat": "new", "do": "Do step 1 two more times, each in a new chat.", "expect": "Often a different word." }
    ],
    "learned": "The AI picks each word partly by chance.",
    "done": "You have 3 story words.",
    "check": { "question": "Why does the word change?", "answer": "..." },
    "challenge": "Ask for the most common word. What changes?"
  },
  "bn": { "...": "the same fields, in Bangla" }
}
```

| Field | Shown as |
|---|---|
| `why` | Why this matters |
| `steps[].chat` | A NEW CHAT or SAME CHAT label. The first step is always `new`. |
| `steps[].do` | What to do in this step |
| `steps[].prompt` | A box with a Copy button, inside the step |
| `steps[].expect` | You should see: |
| `steps[].example` | Example answer, hidden until the reader opens it |
| `learned` | What just happened |
| `done` | You are done when |
| `check` | Check yourself, with a hidden answer |
| `challenge` | Try a harder version |

- `title`, `prompt`, and `example` are plain text. The other text fields
  allow the inline tags.
- A prompt must hold all the material that the task needs.
- The panel shows the chat links and a "How practice works" box one time,
  above the tasks. Do not repeat that text in a task.
- The schema checks that both versions exist and that the first step opens
  a new chat.

The panel is `src/components/content/PracticeList.tsx` and `CopyButton.tsx`.
The voice-to-language rule is `src/lib/practice.ts`.

## Languages

Every page exists in English and in Bangla (বাংলা).

| | English | Bangla |
|---|---|---|
| URL | `/`, `/topics/<slug>/` | `/bn/`, `/bn/topics/<slug>/` |
| Interface text | English | Bangla, from `UI.bn` in `src/lib/i18n.ts` |
| Part and section titles and intros | `title`, `tagline`, `lede`, `sub` | the `bn` fields of the content |
| A section opens in | Technical | বাংলা (listed first in the voice switcher) |
| Practice tasks | English (Bangla in the বাংলা voice) | Bangla in every voice |
| Videos | English (Bangla first in the বাংলা voice) | Bangla first, then English, in every voice |
| Technical and Layman's text, code, diagrams | English | English (one click away) |

- Bangla text keeps English technical words (prompt, token, model, and so
  on) where Bangla has no common word.
- The header button switches to the same page in the other language and
  keeps the section in view. It saves the choice in `localStorage` (key
  `lang`).
- An inline script in `<head>` (`langInitScript` in `src/lib/i18n.ts`)
  sets `<html lang>` from the URL before the first paint. If the reader
  chose the other language before, it opens the same page in that
  language. Without JavaScript, each URL shows its own language.
- The English pages are in the route group `src/app/(en)/` and the Bangla
  pages in `src/app/bn/`. Both render the same page components
  (`src/components/pages/`) with a `lang` prop. `SiteShell` draws the
  header, sidebar, and footer in that language.
- The 404 page shows its text in both languages.
- To add an interface string, add it to `en` in `src/lib/i18n.ts`. The
  type then requires it in `bn` too.

## Search

Press Ctrl+K (Cmd+K on macOS) to open the search palette.

1. At build time, `src/app/search-index.json/route.ts` makes one search
   document for each section. The text comes from the Technical voice.
2. On the first open, the palette fetches `search-index.json` under the
   base path.
3. The palette builds a MiniSearch index in the browser and searches as you
   type.
4. A result links to the section, for example `/topics/inference#<id>`.

The Bangla site uses `/bn/search-index.json`. Its documents hold the
Bangla titles, the বাংলা voice, and the Technical text, so English terms
such as "token" find results too. Results link to `/bn/` pages.

The shared helpers are in `src/lib/search.ts`.

## Source quality

All citations resolve to:

- **arXiv papers** for the foundational techniques (BPE, SentencePiece, CoT,
  ReAct, Reflexion, MemGPT, LLMLingua, Lost-in-the-Middle, and others).
- **Vendor documentation** for production patterns (Anthropic prompt
  caching, OpenAI prompt caching, Gemini caching, OpenAI Structured Outputs,
  Anthropic tool use).
- **Anthropic engineering blog** for the context-engineering playbook.

## File layout

```
.
├── src/
│   ├── app/
│   │   ├── layout.tsx                  root layout: fonts, head scripts
│   │   ├── (en)/                       English pages: layout, home, topics/[slug]
│   │   ├── bn/                         Bangla pages: layout, home, topics/[slug], search index
│   │   ├── not-found.tsx               404 (both languages)
│   │   ├── globals.css                 design tokens and prose styles
│   │   └── search-index.json/route.ts  English search index (static)
│   ├── components/
│   │   ├── content/                    topic header, sections, voice switcher,
│   │   │   └── blocks/                 sources, prev/next, one file per block type
│   │   ├── layout/                     site shell, header, sidebar, mobile nav,
│   │   │                               language and theme switches
│   │   ├── navigation/                 search palette, outline (TOC)
│   │   └── pages/                      home and topic pages, shared by both languages
│   ├── content/                        16 topic JSON files (source of truth)
│   └── lib/
│       ├── content-schema.ts           block types and Zod schema
│       ├── topics.ts                   loads and validates content; order, outline, nav
│       ├── search.ts                   search index helpers
│       ├── videos.ts                   which videos each voice shows; clip length format
│       ├── video-check.ts              title, channel and status comparisons for check:videos
│       ├── practice.ts                 which practice language each voice shows
│       ├── theme.ts                    theme choice and the inline head script
│       └── i18n.ts                     languages, URLs, interface text, the lang head script
├── tests/                              content-schema, search, video, practice, theme, PWA, and language tests
├── docs/                               design spec and plan, video coverage and review log
├── .github/workflows/deploy-pages.yml  GitHub Pages deploy
├── next.config.ts                      static export and base path
└── LICENSE
```

## Design notes

- The site has a light and a dark theme. Design tokens are CSS variables in
  `globals.css`, one set for each theme. Each extra voice has its own color:
  Layman's is violet, বাংলা is green. Every text color has 4.5:1 contrast
  or more on the page and card backgrounds.
- The sun/moon button in the header switches the theme. On the first visit
  the site follows the device setting. After a click, `localStorage`
  (key `theme`) keeps the choice. An inline script in `<head>`
  (`THEME_INIT_SCRIPT` in `src/lib/theme.ts`) sets `data-theme` on `<html>`
  before the first paint, so the page does not flash. Without JavaScript
  the site shows the dark theme.
- Code blocks stay dark in both themes. Their Shiki colors are inline in
  the content HTML.
- Diagram SVGs use fixed colors made for a dark ground. In the light
  theme, `globals.css` maps each solid diagram color to a darker or lighter
  one. If you add a diagram with a new solid color, add it to that map.
- Fraunces (headings), Inter, JetBrains Mono, and Noto Sans Bengali load
  through `next/font/google` with `display: swap`.
- The sidebar lists the 16 parts. Below the `lg` breakpoint, a menu button
  opens the same list.
- The voice switcher works for one section at a time. Its options are
  Technical, Layman's, বাংলা, and All three. A section shows only the
  voices that have content.
- Topic pages show an outline (TOC) on wide screens. It uses
  `IntersectionObserver` to mark the section in view. Heading links in the
  outline work in every voice.
- Content is static. `next build` writes every route to `out/` as HTML.

## License

[MIT](LICENSE)

## Roadmap

`/roadmap/` (and `/bn/roadmap/`) is a study path through the open
[AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
curriculum. It groups the 20 phases into 7 stages, marks five phases as
optional depth, links each phase to the Parts of this site that cover the same
ground, and lets you tick lessons off. It also lists a few focused learning
paths (for example, an Agents/LLMs/MCP under-the-hood path) that point
readers through an existing subset of phases. Progress is saved in the
browser under its own `roadmap-progress` key, separate from the Part
progress. Each lesson opens on the curriculum site.

- `src/data/roadmap-lessons.json` is generated from the curriculum's
  `ROADMAP.md`. Refresh it with
  `node scripts/build-roadmap.mjs <path to the curriculum repo>`.
- `src/data/roadmap-phases.json` is written by hand: the stages, a one-line
  summary of each phase (English and Bangla), which phases are optional, and
  the related Parts.
- `npm run build` and `npm test` check that the two files agree: every phase
  has a summary and a stage, lesson numbers do not repeat, and every related
  Part exists.
