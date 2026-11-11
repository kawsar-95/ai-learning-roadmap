# Deployment

The site deploys to GitHub Pages from GitHub Actions on every push to
`main`. This file covers the workflow, the base path, previewing a build,
stalled deploys, and common problems.

**Live site:** <https://kawsar-95.github.io/ai-learning-roadmap/>

## Contents

- [The workflow](#the-workflow)
- [The base path](#the-base-path)
- [Setting up a fork](#setting-up-a-fork)
- [Previewing a build](#previewing-a-build)
- [Stalled deploys](#stalled-deploys)
- [Troubleshooting](#troubleshooting)

## The workflow

`.github/workflows/deploy-pages.yml` runs on a push to `main`, and by hand
from the Actions tab (`workflow_dispatch`).

| Job | Steps |
| --- | --- |
| `build` | checkout, Node 24 with the npm cache, `actions/configure-pages`, `npm ci --no-audit`, `npm test`, `npm run build` with `PAGES_BASE_PATH`, upload `out/` as the Pages artifact |
| `deploy` | `actions/deploy-pages`, in the `github-pages` environment |

- Both jobs run on `ubuntu-24.04`, not `ubuntu-latest`. When
  `ubuntu-latest` moved to 26.04, the first two deploys on it stalled in the
  Pages queue.
- Each job stops after 15 minutes. The deploy step waits up to 600,000 ms
  (10 minutes), which is GitHub's own limit for a Pages deployment. A
  shorter wait can cancel a deployment that would still finish.
- `concurrency: pages` with `cancel-in-progress: false`: a new push waits
  for the deploy before it instead of cancelling it.
- `--no-audit` skips the one network request a warm `npm ci` makes, which
  nothing uses.

**No workflow runs on pull requests.** A pull request gets no checks from
GitHub, and the deploy does not run `npm run lint`. Run `npm test`,
`npm run lint`, and `npm run build` before you push, and paste the results
in the pull request.

## The base path

A project site on GitHub Pages lives under the repository name:
`https://kawsar-95.github.io/ai-learning-roadmap/`. Every URL in the build
must start with `/ai-learning-roadmap`.

- `actions/configure-pages` outputs that path as `base_path`. The workflow
  passes it to the build as `PAGES_BASE_PATH`.
- `next.config.ts` uses it as `basePath`, and copies it into
  `NEXT_PUBLIC_BASE_PATH` for client code.
- A local `npm run build` has no `PAGES_BASE_PATH`, so it serves from `/`.
- The web app manifest uses relative URLs, so it works under any path.

`next/link` adds the base path by itself. A plain `fetch`, `<a href>`, or
`location` change does not: read `NEXT_PUBLIC_BASE_PATH` there. The places
that already do are listed in
[architecture.md](architecture.md#the-build).

## Setting up a fork

1. Fork the repository.
2. In the fork, open **Settings → Pages**, and under **Build and
   deployment** set **Source** to **GitHub Actions**.
3. Push to `main`, or run the workflow from the **Actions** tab.

The base path follows the fork's name, so nothing in the code needs to
change. A custom domain or a `<user>.github.io` repository serves from `/`,
and `configure-pages` then outputs an empty base path.

The **Source on GitHub** link in the footer and the author link on the home
page come from `REPO_URL` and `AUTHOR_GITHUB_URL` in `src/lib/i18n.ts`.

## Previewing a build

**At the site root.** This is what `npm run build` makes by default.

```bash
npm run build
npx serve@latest out      # http://localhost:3000
```

`npm run start` does not work, because a static export has no server build.
`next start` stops with this error:

```text
Error: "next start" does not work with "output: export" configuration. Use "npx serve@latest out" instead.
```

**Under the GitHub Pages base path.** Use this to test a change to links,
the search index fetch, or the service worker.

```bash
PAGES_BASE_PATH=/ai-learning-roadmap npm run build
rm -rf /tmp/pages && mkdir -p /tmp/pages && cp -r out /tmp/pages/ai-learning-roadmap
python3 -m http.server 3000 -d /tmp/pages   # http://localhost:3000/ai-learning-roadmap/
```

Build again without `PAGES_BASE_PATH` before you run the screenshot script:
it serves `out/` from `/`.

**The service worker** registers only in a production build, so a preview
installs it. It then serves saved pages from its cache. To see a new build,
reload twice, or open DevTools → **Application** → **Service workers** and
click **Unregister**. A private window starts clean.

## Stalled deploys

The `deploy` job prints `Current status: <phase>` every 5 seconds. A healthy
deploy moves through `deployment_queued`, `deployment_in_progress`,
`syncing_files`, and `updating_pages` in under a minute. Sometimes the Pages
service stalls in one phase until the 10-minute limit cancels the
deployment. The site then keeps serving the previous build.

Do not re-run the failed job. GitHub keys a Pages deployment by commit, and
a cancelled deployment cannot be deployed again for the same commit: a
re-run ends with `Deployment cancelled` after a few seconds. The fix is a
new commit on `main`. An empty one is enough:

```bash
git switch main && git pull
git commit --allow-empty -m "ci: redeploy after a stalled Pages deployment"
git push
```

Check which build is live before and after:

```bash
curl -sI https://kawsar-95.github.io/ai-learning-roadmap/ | grep -i last-modified
gh run list --workflow deploy-pages.yml --limit 5
```

A run that shows as queued is usually waiting for the deploy before it
(`concurrency: pages`), not slow itself.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| The build stops with a Zod error: a list of issues, each with a `path` such as `["sections", 1, "body", 2, "html"]` and a `message` | A content file breaks the schema | Fix that field. The rules are in the [content guide](content-guide.md). |
| `Inline html uses a tag or attribute outside the allowlist` | A tag other than `strong`, `em`, `code`, `br`, or a plain or citation link | Remove the tag, or write `&lt;` for a literal `<` |
| `Topic file for "x" has slug "y"` | The `slug` in a Part file does not match `TOPIC_ORDER` | Make them the same |
| `src/content/interview.json: ...` | A Part's questions are missing, out of order, not 3, or name an unknown section | Fix `interview.json` |
| `npm test` cannot load the `.ts` test files | Node is older than 22.18, which runs TypeScript by stripping types | Use Node 22.18 or newer. The deploy uses Node 24. |
| The deployed site has no styles, or its links lead to 404 | The build had the wrong base path | Check the `PAGES_BASE_PATH` the build step printed. Code that builds a URL by hand must add `NEXT_PUBLIC_BASE_PATH`. |
| Search says "Search is unavailable." | The index fetch failed: offline before the index was saved, or a base path mismatch | Open `<base path>/search-index.json` in the browser |
| A deploy finished, but the old content shows | The service worker served the saved build | Reload twice. The new worker installs in the background, then takes over. |
| The deploy is cancelled after 10 minutes | A stalled Pages deployment | See [Stalled deploys](#stalled-deploys) |
| `npm run check:videos` exits with 2 | It could not check: offline, throttled by YouTube (HTTP 429), or the Short test failed its control video | Wait and run it again. It is not part of the deploy. |
