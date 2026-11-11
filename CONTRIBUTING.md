# Contributing

Fixes, new sections, better explanations, and translations are welcome.
This file covers the setup, the checks, the code conventions, and the
writing rules.

## Contents

- [Setup](#setup)
- [Making a change](#making-a-change)
- [Checks](#checks)
- [Code conventions](#code-conventions)
- [Writing rules](#writing-rules)
- [Screenshots](#screenshots)
- [Pull requests](#pull-requests)

## Setup

You need Node.js 22.18 or newer and npm. The tests run TypeScript files
directly, which needs Node 22.18 or newer. The deploy uses Node 24.

```bash
git clone https://github.com/kawsar-95/ai-learning-roadmap.git
cd ai-learning-roadmap
npm install
npm run dev        # http://localhost:3000
```

This is Next.js 16, and its APIs differ from older versions. Before you use
a Next.js API, read its page in `node_modules/next/dist/docs/`.
[AGENTS.md](AGENTS.md) says the same for coding agents.

Where things are:

| To change | Read |
| --- | --- |
| A Part, a section, a quiz, an interview question | [docs/content-guide.md](docs/content-guide.md), [docs/quizzes.md](docs/quizzes.md) |
| The roadmap, the lessons, the learning paths, the resources | [docs/roadmap.md](docs/roadmap.md) |
| Pages, components, search, progress, offline, theme | [docs/architecture.md](docs/architecture.md) |
| The deploy | [docs/deployment.md](docs/deployment.md) |
| Videos | [docs/content-guide.md](docs/content-guide.md#videos), [scripts/video-curation/README.md](scripts/video-curation/README.md) |

## Making a change

1. Branch from `main`. Name the branch after the kind of change:
   `feat/...`, `fix/...`, `docs/...`, or `ci/...`.
2. Make one change per branch. A content fix and a redesign are two pull
   requests.
3. Write the commit message in the
   [Conventional Commits](https://www.conventionalcommits.org/) style the
   history uses: `feat: add an "On this page" outline to roadmap lessons`,
   `fix: credit "Let's think step by step" to Kojima et al., not Wei et al.`
   The body says what changed, why, and how you checked it, with numbers
   where you have them.

## Checks

Run all three before you push. All three must pass.

| Command | What it checks |
| --- | --- |
| `npm test` | 158 tests in `tests/`: the libraries, and rules for the real content (quizzes, videos, interview questions, lessons) |
| `npm run lint` | ESLint with the Next.js core web vitals and TypeScript rules |
| `npm run build` | The type check, every content file against its schema, and every page in both languages |

Then check what the change touches:

- **A visible change:** open the page in the build (`npx serve@latest out`)
  in both languages, in both themes, and at phone width (390 px).
- **Videos:** run `npm run check:videos`. It needs the network.
- **Links, search, or the service worker:** preview the build under the
  GitHub Pages base path ([docs/deployment.md](docs/deployment.md#previewing-a-build)).

## Code conventions

- **Server data stays on the server.** Only server code imports
  `src/lib/topics.ts` and `src/lib/roadmap.ts`. Pages pass plain data to
  client components as props. A client file may `import type` from them.
- **Keep `src/lib/` loadable by the tests.** Files that a test or a script
  imports use relative imports ending in `.ts`, not the `@/` alias, and
  `import type` for types. They use no `enum`, no `namespace`, and no
  constructor parameter properties, because Node runs them by stripping the
  types.
- **Pure logic goes in `src/lib/` with a test.** Components stay thin.
  Logic that has to match an inline script, such as the theme and language
  scripts, gets a test that runs both.
- **Every interface string is in `src/lib/i18n.ts`, in both languages.** The
  type of `UI.bn` follows `UI.en`, so a missing Bangla string fails the type
  check.
- **Follow the design rules** in
  [docs/architecture.md](docs/architecture.md#design-rules): flat cards, no
  emoji in the interface, one accent color, text first.
- **Comments say why**, not what the next line does.
- **New dependencies need a reason.** The site has seven runtime
  dependencies. A tool used once (such as Shiki for code blocks, or
  Playwright for screenshots) is installed outside the repo.

## Writing rules

The site explains hard ideas to readers of many levels, in two languages.
These rules come from the readability passes in the history.

**Every voice**

- Write short sentences: about 13 to 18 words. Split a sentence over 25
  words where its clauses meet.
- Turn a long run of items into a list.
- Give a heading at most about 220 words. Past that, add a subheading.
- Spell out an abbreviation the first time a Part uses it: "key-value (KV)
  cache", "time to first token (TTFT)".
- Define a term once. Do not repeat a definition a few lines later.
- When you edit text, keep every name, number, citation, and link, unless
  the edit is to fix one.

**Technical**

- State the claim, then cite it with `<a class="cite" href="#srcN">[N]</a>`.
- Cite the primary source: the paper, the vendor's documentation, or the
  team's own post. Open the page and check that it supports the claim.
  Credit each method to the paper that introduced it.

**Layman's**

- Plain English and everyday analogies. No jargon. If a term must stay,
  explain it in the same sentence.
- Say the same things as the Technical voice. Do not add facts it does not
  have.

**বাংলা**

- Write natural Bangla sentences. Keep the common English technical words
  as they are: prompt, token, model, API.
- Do not translate word for word. Phrases that read as calques were removed
  in review, and the tests reject some of them in quizzes.
- In quizzes, write plain numbers in Bangla digits. Digits inside a name or
  a code word (GPT-4o, H100, `top_p`) stay Latin.

**Quizzes and interview questions**

- Quiz text is plain text. Write the `why` for the right answer.
- An interview answer is 2 to 4 sentences, and uses only facts from the
  section it links to.

**Ids**

- Never rename a section id or a heading id. Saved progress, bookmarks, and
  links depend on them. See
  [docs/content-guide.md](docs/content-guide.md#keep-ids-stable).

## Screenshots

If your change is visible in a README screenshot, retake it. The script and
its setup are in
[scripts/screenshots/README.md](scripts/screenshots/README.md). Look at
each new image before you commit it.

## Pull requests

- No workflow runs on pull requests, so GitHub shows no checks. Paste the
  results of `npm test`, `npm run lint`, and `npm run build`.
- For a visible change, add before and after screenshots.
- For a content change, list the sources you checked.
- Merging to `main` deploys the site
  ([docs/deployment.md](docs/deployment.md)).

The project is under the [MIT license](LICENSE). The copied curriculum
lessons keep their own MIT license in
[src/content/lessons/LICENSE](src/content/lessons/LICENSE).
