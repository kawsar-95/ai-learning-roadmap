#!/usr/bin/env bash
# Live verification, strictly serial: the oEmbed + /shorts/ lookups first, then (only if those were not throttled) the player probe.
# Needs verify_ids.txt and probe_ids.txt in $VIDEO_WORK (mk_verify.py writes them) and playwright-core in $VIDEO_WORK/node_modules.
# Writes lookups.json, lookup_run.log, probe.jsonl and probe_err.log into $VIDEO_WORK.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${VIDEO_WORK:-${TMPDIR:-/tmp}/video-curation}"
mkdir -p "$WORK" && cd "$WORK" || exit 3
python3 "$HERE/lookup.py" verify_ids.txt > lookup_run.log 2>&1
rc=$?
echo "lookup exit=$rc" >> lookup_run.log
if [ "$rc" -ne 0 ]; then
  echo "probe skipped because the lookup did not finish cleanly" >> lookup_run.log
  exit "$rc"
fi
PAUSE_MS=2000 node "$HERE/probe-player.mjs" --file probe_ids.txt > probe.jsonl 2> probe_err.log
echo "probe exit=$?" >> probe_err.log
cat lookup_run.log probe_err.log
