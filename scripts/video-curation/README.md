# Video curation

The scripts that found, read, verified and wrote the clips in the Parts' video lists, and that generate [`docs/video-coverage.md`](../../docs/video-coverage.md) and [`docs/video-review-log.md`](../../docs/video-review-log.md).

They talk to YouTube, so nothing here runs in `npm test`, the build or the deploy. To check that the listed videos still exist, use `npm run check:videos` instead.

## Setup

- Python 3 (standard library only), the Node version the site already needs, [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), and Chrome or Chromium for the player probe.
- `export VIDEO_WORK=~/video-work`: an empty directory for crawl lists, caches and lookups. The default is `<temp dir>/video-curation`. Nothing in it is committed, and every step can be re-run. Export it in every shell that runs these scripts, `node` included: the player probe finds `playwright-core` through it.
- `export YT_DLP=/path/to/yt-dlp` when `yt-dlp` is not on your `PATH`.
- For the player probe: `cd "$VIDEO_WORK" && npm i playwright-core`. It is not a dependency of the site. `CHROME=/path/to/chrome` replaces the default `/usr/bin/google-chrome`.
- Run every command from the repository root. A file name argument (such as `pool_ids.txt`) is read from `$VIDEO_WORK`.

## Be gentle with YouTube

- One YouTube-touching job at a time, serial, with a pause between requests. No cookies and no login.
- Stop at the first HTTP 429 or "Sign in to confirm you're not a bot", and wait. Do not retry harder.
- Ask for the `en-orig` captions only. Every extra caption language is another request per clip, and asking for two drew HTTP 429.
- oEmbed and the `/shorts/<id>` redirect kept answering when the metadata calls were throttled, so titles and statuses come from them.

## Steps

All paths below are in `scripts/video-curation/`. The last column is what the step writes into `$VIDEO_WORK`.

| # | Step | Command | Writes |
| --- | --- | --- | --- |
| 1 | List the channels' tabs | `crawl_kodekloud.sh`, `python3 crawl_channels.py [creator ...]` | `kk_*_fresh.tsv`, `ch_<creator>_{videos,shorts}.tsv`, `channels_resolved.json` |
| 2 | Catalogue the site's sections and videos | `python3 catalog.py` | `catalog.json` |
| 3 | Turn needles into candidate ids | `python3 candidates_kodekloud.py`, `python3 candidates_creators.py`, `python3 gap_pick.py` | `pool_ids.txt`, `pool2_ids.txt`, `draft*_resolved.json`, `gap*_resolved.json` |
| 4 | Fetch length and captions of the candidates | `python3 fetch_details.py pool_ids.txt` | `deep/<id>.json` |
| 5 | Read them | `python3 read_transcript.py <id> ...`, `python3 search_transcript.py <id> <regex>` | |
| 6 | Decide | edit `picks.py`, then `python3 picks.py` and `python3 check_sections.py` | `final_picks.json` |
| 7 | Verify live | `python3 mk_verify.py`, `verify_run.sh`, `python3 lookup_summary.py` | `lookups.json`, `probe.jsonl` |
| 8 | Write the data | `python3 build_content.py` (dry run), then `--write` | `src/content/*.json` |
| 9 | Write the docs | `python3 gaps.py`, `python3 build_docs.py` | `gaps.json`, `docs/video-*.md` |

`build_docs.py` reads the crawl lists, the lookups and the probe results, so run steps 1 to 7 on the same `$VIDEO_WORK` first.

Do not re-run `gaps.py` now that Part 17 exists: it counts keyword hits in the Parts, and Part 17 is made of those keywords. `docs/video-coverage.md` keeps the counts taken before Part 17 was added. To verify only a few new picks, write their ids to a file and run `PAUSE_MS=2000 node probe-player.mjs --file new_ids.txt >> probe.jsonl` from `$VIDEO_WORK`, after `python3 lookup.py <file>` (it extends `lookups.json` and skips ids it already has).

## Needles

An id is never typed. A clip is named by a needle, and a script resolves it against the crawled lists:

```text
S:what is context engineering          a Short of KodeKloud (the Shorts tab), a lower-case part of its published title
V:rag explained@35000                  a video; @35000 keeps only the clip with exactly 35,000 views
colemedin/V:rag 2.0                    the same, for another creator (crawl_channels.py spells the creator names)
```

A needle must match exactly one clip. A typo or a tie fails loudly, and a tie is settled with `@views`.

## Reading

Step 5 is the editorial step. For every candidate read the opening, a sample of the middle and the ending of the transcript, and check that the section's own text names the concept. A title is not evidence. Watch for errors of fact, hype, product launches that are already dated, and enrolment or course pitches. `picks.py` keeps the reason for every clip that was left out, and `docs/video-review-log.md` prints them.

## What the write step refuses

`build_content.py --write` writes nothing if any pick fails. A pick passes only if:

- oEmbed answers 200 (public and embeddable), and the IFrame player reports no error and starts;
- a Short is a Short (`/shorts/<id>` answers 200) and is at most 180 seconds;
- its stored title is the published title through the site's own `storedTitle()` (`stored_titles.mjs` calls it, so the data and the TypeScript cannot disagree), and its channel is the oEmbed `author_name`;
- it is not already listed.

`picks.py` also enforces the per-section limits: at most 5 KodeKloud clips, at most 4 clips from the other creators together and 3 from one creator, and at most 2 videos over 30 minutes.

## Adding clips later

Add the creator to `CREATORS` in `crawl_channels.py` when the channel is new, and crawl it. Put the needles into `picks.py` (KodeKloud) or `candidates_creators.py` (the others), then run steps 4 to 9.

Six sections were split in two after their clips were picked (5.02, 5.05, 5.06, 5.07, 5.09 and 8.01). `picks.py` and the `candidates_*.py` files still use the original ids, which now stand for the first half. Three groups of picked clips sit in a second half: one in `rag-knowledge-systems/s11` (was `s2`), two in `rag-knowledge-systems/s12` (was `s5`) and three in `inference/s4` (was `inference/s3`). `docs/video-review-log.md` was edited by hand to list them under the new ids, and a regenerated log would put them back under the old ones. Use the section ids that `src/content/*.json` has today.

A second round split thirteen more (5.01, 5.03, 5.05, 7.01, 8.01, 15.06 and the Part 16 chapters 2, 3, 5, 6, 7, 9 and 10, numbered as before that round). Two groups of picked clips now sit in a second half: one in `rag-knowledge-systems/s18` (was `s1`) and eight in `tool-use-and-integrations/s3` (was `s2`). The other clips that moved were added outside `picks.py`.

## What is not here

The helpers used to shortlist (per-channel keyword rankings, topic sweeps, printouts of candidates) were one-off and are left out. Their result is what is committed: the needles in `candidates_*.py`, the decisions and reasons in `picks.py`, and the log in `docs/video-review-log.md`.
