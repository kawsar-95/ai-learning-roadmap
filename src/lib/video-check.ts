// Pure helpers for scripts/check-videos.mjs, the on-demand check of the YouTube videos in src/content/*.json.
// No network here, so `node --test` can load this file. The script does the requests.

/** The answer of YouTube's oEmbed endpoint, as the check reads it. */
export type Oembed = { status: number; title?: string; author?: string };

/** What an oEmbed status means for a stored video. Null means the video is public and can be embedded. */
export function oembedProblem(status: number): string | null {
  if (status === 200) return null;
  if (status === 401 || status === 403) return "embedding is turned off";
  if (status === 404) return "the video is gone or private";
  return `oEmbed answered HTTP ${status}`;
}

/**
 * A hashtag starts with a letter or an underscore. "#2" in "Tutorial #2: Prompt Templates" is an episode number,
 * not a hashtag (YouTube does not accept a hashtag made of digits only), so it stays in the title.
 */
const HASHTAG = /#[\p{L}_][\p{L}\p{N}_]*/gu;

/**
 * A title reduced to what must still match. The stored title is the published one without hashtags and emoji,
 * so the live title is normalised the same way and must contain it. NFKC makes two Unicode spellings of one
 * Bangla letter equal. The joiners and variation selectors go first: an emoji leaves U+FE0F behind, it counts
 * as a mark, and the title would stop matching.
 */
export function normalizeTitle(title: string): string {
  return title
    .normalize("NFKC")
    .replace(/[\uFE00-\uFE0F\u200B-\u200D\u2060]/g, "")
    .replace(HASHTAG, " ")
    .replace(/[^\p{L}\p{N}\p{M}]+/gu, " ")
    .trim()
    .toLowerCase();
}

export function titleMatches(stored: string, live: string): boolean {
  return normalizeTitle(live).includes(normalizeTitle(stored));
}

/** The channel must still be the stored one. YouTube's own name can carry a trailing space, so outer space does not count. */
export function channelMatches(stored: string, live: string | undefined): boolean {
  return (live ?? "").trim() === stored.trim();
}

/** The title as stored: hashtags and emoji removed, nothing else changed. */
export function storedTitle(published: string): string {
  return published
    .replace(HASHTAG, "")
    .replace(/[\p{Extended_Pictographic}\uFE0F\u200D]/gu, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}
