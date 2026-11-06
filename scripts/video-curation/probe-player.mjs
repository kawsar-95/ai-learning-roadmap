// Probes YouTube videos through the official IFrame Player API in a real browser: the true length, the title
// YouTube reports, and whether the embed loads and starts to play (muted).
//
//   node probe-player.mjs <id> [<id> ...]      or      node probe-player.mjs --file ids.txt
//
// Needs `npm i playwright-core` inside $VIDEO_WORK (no browser download; it is not a dependency of the site) and Chrome or
// Chromium (CHROME=/path/to/chrome, default /usr/bin/google-chrome).
// Prints one JSON line per id: {id, duration, title, playing, state}, or {id, error}.
// error 100, 101, or 150 = the video is missing or not embeddable. `author` comes back empty: take it from oEmbed.
// Sequential on purpose: one video at a time with a pause (PAUSE_MS, default 1500), like a person watching.
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";

const work = process.env.VIDEO_WORK || path.join(os.tmpdir(), "video-curation");
const { chromium } = createRequire(path.join(work, "noop.js"))("playwright-core");

const args = process.argv.slice(2);
const ids = args[0] === "--file" ? fs.readFileSync(args[1], "utf8").split(/\s+/).filter(Boolean) : args;
const PAUSE = Number(process.env.PAUSE_MS ?? 1500);

// The harness page is served from a local http origin rather than opened from file://.
const html = `<!doctype html><meta charset="utf-8"><body style="margin:0">
<div id="host"></div>
<script src="https://www.youtube.com/iframe_api"></script>
<script>
window.__ready = new Promise((r) => { window.onYouTubeIframeAPIReady = r; });
window.probe = async (id) => {
  await window.__ready;
  document.getElementById("host").innerHTML = '<div id="p"></div>';
  return new Promise((resolve) => {
    const out = { id };
    let player; let done = false;
    const safe = (f) => { try { return f(); } catch (e) { return null; } };
    const finish = (extra) => { if (done) return; done = true; Object.assign(out, extra); try { player.destroy(); } catch (e) {} resolve(out); };
    const t = setTimeout(() => finish({ timeout: true, state: safe(() => player.getPlayerState()) }), 20000);
    player = new YT.Player("p", {
      videoId: id, width: 360, height: 640, host: "https://www.youtube-nocookie.com",
      playerVars: { playsinline: 1, rel: 0 },
      events: {
        onError: (e) => { clearTimeout(t); finish({ error: e.data }); },
        onReady: async () => {
          let duration = 0;
          for (let i = 0; i < 20 && !duration; i++) { duration = player.getDuration(); if (!duration) await new Promise((r) => setTimeout(r, 250)); }
          const data = safe(() => player.getVideoData()) || {};
          out.duration = duration; out.title = data.title; out.author = data.author;
          player.mute(); player.playVideo();
          for (let i = 0; i < 24; i++) {
            await new Promise((r) => setTimeout(r, 250));
            if (safe(() => player.getPlayerState()) === 1) { out.playing = true; break; }
          }
          out.state = safe(() => player.getPlayerState());
          // Some clips report no length until they play: read it again, now that playback has started.
          for (let i = 0; i < 20 && !out.duration; i++) {
            out.duration = safe(() => player.getDuration()) || 0;
            if (!out.duration) await new Promise((r) => setTimeout(r, 250));
          }
          if (!out.title) out.title = (safe(() => player.getVideoData()) || {}).title;
          clearTimeout(t); finish({});
        },
      },
    });
  });
};
</script>`;

const server = http.createServer((req, res) => { res.setHeader("content-type", "text/html"); res.end(html); });
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const origin = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch({ executablePath: process.env.CHROME ?? "/usr/bin/google-chrome", headless: true, args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required"] });
const page = await browser.newPage({ viewport: { width: 400, height: 700 } });
await page.goto(origin);
for (const id of ids) {
  let r;
  try { r = await page.evaluate((i) => window.probe(i), id); } catch (e) { r = { id, exception: String(e).slice(0, 120) }; }
  console.log(JSON.stringify(r));
  await new Promise((res) => setTimeout(res, PAUSE));
}
await browser.close();
server.close();
