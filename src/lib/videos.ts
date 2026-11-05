import type { Video } from "./content-schema.ts";
import { fmtNum } from "./i18n.ts";
import type { Lang } from "./i18n.ts";

type Voice = "main" | "layman" | "bangla" | "all";

/** A length for a card, as m:ss or h:mm:ss, in the digits of `lang`. */
export function formatClock(seconds: number, lang: Lang = "en"): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const two = (n: number) => fmtNum(lang, Math.floor(n / 10)) + fmtNum(lang, n % 10);
  return h > 0 ? `${fmtNum(lang, h)}:${two(m)}:${two(s)}` : `${fmtNum(lang, m)}:${two(s)}`;
}

/** The ISO 8601 duration for a <time> element: 65 gives "PT1M5S". */
export function isoDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `PT${h ? `${h}H` : ""}${m ? `${m}M` : ""}${s || (!h && !m) ? `${s}S` : ""}`;
}

/**
 * The videos a section shows. The Bangla site shows Bangla videos first,
 * then English, in every voice. On the English site, Technical and Layman's
 * show the English videos, বাংলা shows Bangla first then English (so a section
 * without a Bangla video still has something to watch), and All three shows
 * all of them.
 */
export function videosForVoice(videos: Video[] | undefined, voice: Voice, siteLang: Lang = "en"): Video[] {
  const english = (videos ?? []).filter((v) => v.lang === "en");
  const bangla = (videos ?? []).filter((v) => v.lang === "bn");
  if (siteLang === "bn") return [...bangla, ...english];
  switch (voice) {
    case "main":
    case "layman":
      return english;
    case "bangla":
      return [...bangla, ...english];
    case "all":
      return [...english, ...bangla];
  }
}
