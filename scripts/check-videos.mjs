// On-demand check of the YouTube videos in src/content/*.json: is each one still public and embeddable, does it
// still carry the stored title and channel, and is a Short still a Short?
//
//   npm run check:videos                          every video on the site
//   npm run check:videos -- --channel KodeKloud   only the videos of one channel
//
// It talks to YouTube, so `npm test` and CI never run it: a creator can delete, privatise or un-embed a video at
// any time, and that must not fail a deploy. Exit code: 0 all fine, 1 a video has a problem, 2 the check could
// not be done (offline, throttled, or YouTube answers 200 to every Short test). Requests are gentle: two at a
// time with a pause, no cookies, and a stop at the first HTTP 429.

import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { channelMatches, oembedProblem, titleMatches } from "../src/lib/video-check.ts";

const CONTENT = fileURLToPath(new URL("../src/content/", import.meta.url));
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
const CONTROL_ID = "dQw4w9WgXcQ"; // a long, stable video that is not a Short: its /shorts/ URL must redirect
const WORKERS = 2;
const PAUSE_MS = 600;

const flag = process.argv.indexOf("--channel");
const channelFilter = flag > -1 ? process.argv[flag + 1] : null;

// Every video of every topic file, with the section it sits in. interview.json has no `sections`.
const videos = [];
for (const file of readdirSync(CONTENT).filter((f) => f.endsWith(".json"))) {
  const topic = JSON.parse(readFileSync(CONTENT + file, "utf8"));
  for (const section of topic.sections ?? []) {
    for (const video of section.videos ?? []) {
      if (!channelFilter || video.channel === channelFilter) videos.push({ ...video, where: `${topic.slug}/${section.id}` });
    }
  }
}

class Throttled extends Error {}
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function get(url, redirect = "follow") {
  const response = await fetch(url, {
    headers: { "user-agent": UA, "accept-language": "en-US,en;q=0.9" },
    redirect,
    signal: AbortSignal.timeout(25_000),
  });
  if (response.status === 429) throw new Throttled();
  return response;
}

async function oembed(id) {
  const watch = encodeURIComponent(`https://www.youtube.com/watch?v=${id}`);
  const response = await get(`https://www.youtube.com/oembed?format=json&url=${watch}`);
  if (response.status !== 200) return { status: response.status };
  const data = await response.json();
  return { status: 200, title: data.title, author: data.author_name };
}

/** The status of /shorts/<id> without following redirects: 200 is a Short, a 3xx is a normal video. */
const shortsStatus = async (id) => (await get(`https://www.youtube.com/shorts/${id}`, "manual")).status;

async function problemOf(video) {
  const live = await oembed(video.id);
  const bad = oembedProblem(live.status);
  if (bad) return bad;
  if (!titleMatches(video.title, live.title)) return `the title changed: "${live.title}"`;
  if (!channelMatches(video.channel, live.author)) return `the channel changed: "${(live.author ?? "").trim()}"`;
  if (video.format === "short") {
    let status = await shortsStatus(video.id);
    if (status >= 300 && status < 400) {
      await sleep(3000); // YouTube can redirect a real Short for a moment: ask once more
      status = await shortsStatus(video.id);
    }
    if (status >= 300 && status < 400) return "it is a normal video now, not a Short";
    if (status !== 200) return `/shorts/ answered HTTP ${status}`;
  }
  return null;
}

async function main() {
  if (!videos.length) {
    console.log(channelFilter ? `No video of the channel "${channelFilter}".` : "No videos found.");
    return 0;
  }
  const control = await shortsStatus(CONTROL_ID);
  if (!(control >= 300 && control < 400)) {
    console.log(`CANNOT CHECK: the control video answered HTTP ${control}, so the Short test cannot tell a Short from a normal video right now.`);
    return 2;
  }

  let next = 0;
  let checked = 0;
  const failures = [];
  async function worker() {
    while (next < videos.length) {
      const video = videos[next++];
      const problem = await problemOf(video);
      checked++;
      if (problem) {
        failures.push(video);
        console.log(`FAIL ${video.where} ${video.id} (${video.title}): ${problem}`);
      }
      await sleep(PAUSE_MS);
    }
  }
  try {
    await Promise.all(Array.from({ length: WORKERS }, worker));
  } catch (error) {
    if (!(error instanceof Throttled)) throw error;
    console.log(`STOPPED: YouTube answered HTTP 429 after ${checked} of ${videos.length} videos. Wait a while before asking again.`);
    return 2;
  }
  console.log(failures.length ? `${failures.length} of ${checked} videos have a problem.` : `OK ${checked} videos checked, 0 problems`);
  return failures.length ? 1 : 0;
}

main().then(
  (code) => process.exit(code),
  (error) => {
    console.log(`CANNOT CHECK: ${error.message}`);
    process.exit(2);
  },
);
