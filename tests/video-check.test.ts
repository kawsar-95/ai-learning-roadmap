import { test } from "node:test";
import assert from "node:assert/strict";
import { channelMatches, normalizeTitle, oembedProblem, storedTitle, titleMatches } from "../src/lib/video-check.ts";

test("oembedProblem: 200 is fine, 401/403 is embedding off, 404 is gone, anything else is reported", () => {
  assert.equal(oembedProblem(200), null);
  assert.equal(oembedProblem(401), "embedding is turned off");
  assert.equal(oembedProblem(403), "embedding is turned off");
  assert.equal(oembedProblem(404), "the video is gone or private");
  assert.equal(oembedProblem(429), "oEmbed answered HTTP 429");
  assert.equal(oembedProblem(500), "oEmbed answered HTTP 500");
});

test("storedTitle removes hashtags and emoji and changes nothing else", () => {
  assert.equal(storedTitle("Why We Need MCP When APIs Already Exist 🤔"), "Why We Need MCP When APIs Already Exist");
  assert.equal(storedTitle("MCP vs UTCP 🔀"), "MCP vs UTCP");
  assert.equal(storedTitle("Everyone's Quitting MCP… Here's What They're Using Instead #shorts"), "Everyone's Quitting MCP… Here's What They're Using Instead");
  assert.equal(storedTitle("How Google's A2A Protocol Works? #aiagent #google #ai"), "How Google's A2A Protocol Works?");
  assert.equal(storedTitle("What Are AI Guardrails and How Do They Work!🤖"), "What Are AI Guardrails and How Do They Work!");
  assert.equal(storedTitle("Plain title (Part 1/3)"), "Plain title (Part 1/3)");
  assert.equal(storedTitle("LangChain Tutorial (Python) #2: Prompt Templates and Chains"), "LangChain Tutorial (Python) #2: Prompt Templates and Chains", "an episode number is not a hashtag");
  assert.equal(storedTitle("SSE Deep Dive #realtimecommunication"), "SSE Deep Dive");
  assert.equal(storedTitle("Top #1 Tips #ai2026"), "Top #1 Tips");
});

test("titleMatches: the live title must contain the stored one, ignoring case, punctuation, hashtags and emoji", () => {
  assert.equal(titleMatches("MCP vs UTCP", "MCP vs UTCP 🔀"), true);
  assert.equal(titleMatches("Why Context Engineering Is the Future of AI?", "why context engineering is the future of ai? #shorts"), true);
  assert.equal(titleMatches("What Is a Context Window?", "What Is a Context Window? (updated)"), true);
  assert.equal(titleMatches("What Is a Context Window?", "What is a token?"), false, "a renamed video must fail");
});

test("channelMatches: a renamed channel fails, outer space does not count", () => {
  assert.equal(channelMatches("Dan Cleary", "Dan Cleary "), true, "YouTube returns this channel name with a trailing space");
  assert.equal(channelMatches("Dan Cleary ", "Dan Cleary"), true);
  assert.equal(channelMatches("PromptHub", "Dan Cleary"), false, "a renamed channel must fail");
  assert.equal(channelMatches("KodeKloud", undefined), false, "an answer without a channel must fail");
});

test("normalizeTitle drops the variation selector that an emoji leaves behind", () => {
  // U+2699 (gear) plus U+FE0F is "⚙️": the selector is a mark, so it would otherwise survive the cleanup.
  const live = "Tune the \u2699\uFE0F settings";
  assert.equal(normalizeTitle(live), "tune the settings");
  assert.equal(titleMatches("Tune the settings", live), true);
});

test("normalizeTitle makes two Unicode spellings of one Bangla letter equal", () => {
  // U+09DF (য়) against U+09AF followed by U+09BC: one from YouTube's player, one from its oEmbed answer.
  const precomposed = "\u09DF";
  const decomposed = "\u09AF\u09BC";
  assert.notEqual(precomposed, decomposed, "the test needs two different spellings, or it proves nothing");
  assert.equal(normalizeTitle(`ব${precomposed}`), normalizeTitle(`ব${decomposed}`));
  assert.equal(titleMatches(`ব${precomposed}`, `ব${decomposed} ভিডিও`), true);
});
