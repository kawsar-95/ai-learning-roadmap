#!/usr/bin/env bash
# Serial, polite crawl of the KodeKloud channel tabs (flat listings only: ids, views, length, title).
# One YouTube-touching job at a time; no cookies, no login.
# Writes kk_shorts_fresh.tsv and kk_videos_fresh.tsv into $VIDEO_WORK (default: <temp dir>/video-curation).
# A tab whose crawl fails or comes back empty keeps its previous list, and the script then exits 1: the new listing goes to
# kk_<tab>_fresh.tsv.new and is moved into place only when yt-dlp succeeded and returned rows.
set -u
WORK="${VIDEO_WORK:-${TMPDIR:-/tmp}/video-curation}"
YT="${YT_DLP:-yt-dlp}"
mkdir -p "$WORK" && cd "$WORK" || exit 3
rm -f crawl.status
failed=0

# crawl <tab> <print format>: list one tab of the channel into kk_<tab>_fresh.tsv
crawl() {
  local tab="$1" fmt="$2" rc rows
  "$YT" "https://www.youtube.com/@KodeKloud/$tab" --flat-playlist --no-warnings --print "$fmt" > "kk_${tab}_fresh.tsv.new" 2> "kk_${tab}_fresh.err"
  rc=$?
  rows=$(wc -l < "kk_${tab}_fresh.tsv.new")
  if [ "$rc" -eq 0 ] && [ "$rows" -gt 0 ]; then
    mv "kk_${tab}_fresh.tsv.new" "kk_${tab}_fresh.tsv"
  else
    failed=1
  fi
  echo "${tab}_done rc=$rc rows=$rows" >> crawl.status
}

crawl shorts '%(id)s\t%(view_count)s\t%(title)s'
sleep 4
crawl videos '%(id)s\t%(view_count)s\t%(duration)s\t%(title)s'
cat crawl.status
if [ "$failed" -ne 0 ]; then
  echo "a crawl failed or listed nothing: its previous list was kept (see kk_*_fresh.err)" >&2
  exit 1
fi
