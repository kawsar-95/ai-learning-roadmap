import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

// The shell steps in scripts/video-curation talk to YouTube. These tests put stand-ins for the tools first on PATH, so
// nothing here touches the network: they check only what each script does with the status and the output of its step.
const script = (name: string) => fileURLToPath(new URL(`../scripts/video-curation/${name}`, import.meta.url));
const skip = process.platform === "win32" ? "the scripts need bash" : false;

/** Runs a script in a fresh work directory with stand-in tools (name -> bash body) first on PATH. Returns the exit status and every file left in the work directory. */
function run(name: string, tools: Record<string, string>, files: Record<string, string>, env: Record<string, string> = {}) {
  const dir = mkdtempSync(join(tmpdir(), "video-curation-"));
  try {
    const bin = join(dir, "bin");
    const work = join(dir, "work");
    mkdirSync(bin);
    mkdirSync(work);
    for (const [tool, body] of Object.entries(tools)) {
      writeFileSync(join(bin, tool), `#!/usr/bin/env bash\n${body}\n`);
      chmodSync(join(bin, tool), 0o755);
    }
    for (const [file, text] of Object.entries(files)) writeFileSync(join(work, file), text);
    const r = spawnSync("bash", [script(name)], {
      env: { ...process.env, PATH: `${bin}:${process.env.PATH}`, VIDEO_WORK: work, ...env },
      encoding: "utf8",
      timeout: 30_000,
    });
    const left: Record<string, string> = {};
    for (const file of readdirSync(work)) left[file] = readFileSync(join(work, file), "utf8");
    return { status: r.status, left };
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

const OLD_PROBE = '{"id":"old","duration":10,"playing":true}\n';
const NEW_PROBE = '{"id":"new","duration":20,"playing":true}\n';
const verifyFiles = { "probe.jsonl": OLD_PROBE, "verify_ids.txt": "", "probe_ids.txt": "abc\n" };

test("verify_run.sh: a probe that fails fails the script and leaves the earlier probe.jsonl alone", { skip }, () => {
  const r = run("verify_run.sh", { python3: "exit 0", node: "echo partial; echo 'Cannot find module playwright-core' >&2; exit 1" }, verifyFiles);
  assert.equal(r.status, 1);
  assert.equal(r.left["probe.jsonl"], OLD_PROBE);
  assert.match(r.left["probe_err.log"] ?? "", /probe exit=1/);
});

test("verify_run.sh: a probe that finishes replaces probe.jsonl and the script succeeds", { skip }, () => {
  const r = run("verify_run.sh", { python3: "exit 0", node: `echo '${NEW_PROBE.trim()}'` }, verifyFiles);
  assert.equal(r.status, 0);
  assert.equal(r.left["probe.jsonl"], NEW_PROBE);
  assert.equal("probe.jsonl.new" in r.left, false);
});

test("verify_run.sh: a lookup that fails stops before the probe and passes its status on", { skip }, () => {
  const r = run("verify_run.sh", { python3: "exit 3", node: "echo the probe must not run; exit 0" }, verifyFiles);
  assert.equal(r.status, 3);
  assert.equal(r.left["probe.jsonl"], OLD_PROBE);
  assert.match(r.left["lookup_run.log"] ?? "", /probe skipped/);
});

const OLD_SHORTS = "old-short\t1\told\n";
const OLD_VIDEOS = "old-video\t1\t60\told\n";
const crawlFiles = { "kk_shorts_fresh.tsv": OLD_SHORTS, "kk_videos_fresh.tsv": OLD_VIDEOS };
const crawlEnv = { YT_DLP: "yt" };

test("crawl_kodekloud.sh: two good crawls replace both lists and the script succeeds", { skip }, () => {
  const r = run("crawl_kodekloud.sh", { yt: `printf 'new\\t5\\tnew title\\n'`, sleep: "exit 0" }, crawlFiles, crawlEnv);
  assert.equal(r.status, 0);
  assert.equal(r.left["kk_shorts_fresh.tsv"], "new\t5\tnew title\n");
  assert.equal(r.left["kk_videos_fresh.tsv"], "new\t5\tnew title\n");
  assert.equal(r.left["crawl.status"], "shorts_done rc=0 rows=1\nvideos_done rc=0 rows=1\n");
});

test("crawl_kodekloud.sh: a crawl that fails keeps that list, the other tab still updates, and the script fails", { skip }, () => {
  const yt = `case "$1" in *shorts*) echo 'HTTP Error 429' >&2; exit 1;; *) printf 'new\\t5\\t60\\tnew title\\n';; esac`;
  const r = run("crawl_kodekloud.sh", { yt, sleep: "exit 0" }, crawlFiles, crawlEnv);
  assert.equal(r.status, 1);
  assert.equal(r.left["kk_shorts_fresh.tsv"], OLD_SHORTS);
  assert.equal(r.left["kk_videos_fresh.tsv"], "new\t5\t60\tnew title\n");
  assert.equal(r.left["crawl.status"], "shorts_done rc=1 rows=0\nvideos_done rc=0 rows=1\n");
  assert.match(r.left["kk_shorts_fresh.err"] ?? "", /429/);
});

test("crawl_kodekloud.sh: a crawl that succeeds but lists nothing counts as failed and keeps the old lists", { skip }, () => {
  const r = run("crawl_kodekloud.sh", { yt: "exit 0", sleep: "exit 0" }, crawlFiles, crawlEnv);
  assert.equal(r.status, 1);
  assert.equal(r.left["kk_shorts_fresh.tsv"], OLD_SHORTS);
  assert.equal(r.left["kk_videos_fresh.tsv"], OLD_VIDEOS);
});
