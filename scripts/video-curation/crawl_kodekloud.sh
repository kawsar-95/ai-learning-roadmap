#!/usr/bin/env bash
# Serial, polite crawl of the KodeKloud channel tabs (flat listings only: ids, views, length, title).
# One YouTube-touching job at a time; no cookies, no login.
# Writes kk_shorts_fresh.tsv and kk_videos_fresh.tsv into $VIDEO_WORK (default: <temp dir>/video-curation).
set -u
WORK="${VIDEO_WORK:-${TMPDIR:-/tmp}/video-curation}"
YT="${YT_DLP:-yt-dlp}"
mkdir -p "$WORK" && cd "$WORK" || exit 3
rm -f crawl.status
"$YT" 'https://www.youtube.com/@KodeKloud/shorts' --flat-playlist --no-warnings \
  --print '%(id)s\t%(view_count)s\t%(title)s' > kk_shorts_fresh.tsv 2> kk_shorts_fresh.err
echo "shorts_done rc=$? rows=$(wc -l < kk_shorts_fresh.tsv)" >> crawl.status
sleep 4
"$YT" 'https://www.youtube.com/@KodeKloud/videos' --flat-playlist --no-warnings \
  --print '%(id)s\t%(view_count)s\t%(duration)s\t%(title)s' > kk_videos_fresh.tsv 2> kk_videos_fresh.err
echo "videos_done rc=$? rows=$(wc -l < kk_videos_fresh.tsv)" >> crawl.status
cat crawl.status
