// The site's two languages. English pages live at the root ("/topics/x/"),
// Bangla pages under "/bn" ("/bn/topics/x/"). This file has no server-only
// imports, so client components and `node --test` can use it.

export type Lang = "en" | "bn";
export const LANGS: readonly Lang[] = ["en", "bn"];

/** The localStorage key that holds the reader's language choice. */
export const LANG_STORAGE_KEY = "lang";

/** The language of a path without the base path. */
export function langFromPath(path: string): Lang {
  return path === "/bn" || path.startsWith("/bn/") ? "bn" : "en";
}

/** The same page in `lang`. `path` has no base path. */
export function localizedPath(path: string, lang: Lang): string {
  const english = langFromPath(path) === "bn" ? path.slice(3) || "/" : path;
  if (lang === "en") return english;
  return english === "/" ? "/bn/" : `/bn${english}`;
}

/** The home page and a topic page in `lang`. */
export function homeHref(lang: Lang): string {
  return lang === "bn" ? "/bn/" : "/";
}
export function topicHref(slug: string, lang: Lang): string {
  return `${lang === "bn" ? "/bn" : ""}/topics/${slug}`;
}
export function contentsHref(lang: Lang): string {
  return lang === "bn" ? "/bn/contents/" : "/contents/";
}

/** The source code of the site. */
export const REPO_URL = "https://github.com/kawsar-95/ai-learning-roadmap";

/** A feature card on the home page. */
type Feature = { icon: string; title: string; text: string };

/** A number in the digits of `lang`. */
export function fmtNum(lang: Lang, n: number): string {
  return lang === "bn" ? new Intl.NumberFormat("bn-BD").format(n) : String(n);
}

/**
 * Runs in <head> before the first paint. It sets <html lang> from the path.
 * If the reader chose the other language before, it opens the same page in
 * that language. It must agree with langFromPath and localizedPath
 * (tests/i18n.test.ts checks this).
 */
export function langInitScript(basePath: string): string {
  return `(function(){try{var b=${JSON.stringify(basePath)},l=location,p=l.pathname;if(b&&p.indexOf(b)===0)p=p.slice(b.length)||"/";var bn=p==="/bn"||p.indexOf("/bn/")===0;document.documentElement.setAttribute("lang",bn?"bn":"en");var s=localStorage.getItem(${JSON.stringify(
    LANG_STORAGE_KEY,
  )});if((s==="bn"&&!bn)||(s==="en"&&bn)){var e=bn?p.slice(3)||"/":p,t=s==="en"?e:e==="/"?"/bn/":"/bn"+e;l.replace(b+t+l.search+l.hash)}}catch(x){}})()`;
}

const en = {
  siteName: "AI Engineering",
  skipLink: "Skip to content",
  footer: "14 parts · citations verified against each publisher's metadata.",
  metaTitle: "AI Engineering — All Necessary Topics",
  metaDescription:
    "Fourteen reference parts covering every topic an applied AI engineer needs, from LLM fundamentals and prompt engineering to agents, inference, evaluation, safety, and AI application architecture. Each topic in three voices: technical, layman, and বাংলা.",

  // Language and theme switches.
  langSwitchText: "বাংলা",
  langSwitchLabel: "বাংলায় পড়ো",
  themeToLight: "Switch to light theme",
  themeToDark: "Switch to dark theme",
  themeGeneric: "Switch color theme",
  installApp: "Install this site as an app",

  // Navigation.
  partsNav: "Parts",
  part: (n: string) => `Part ${n}`,
  openParts: "Open the list of parts",
  closeParts: "Close the list of parts",
  onThisPage: "On this page",
  prevNextNav: "Previous and next Part",

  // Search.
  search: "Search",
  searchAll: "Search all 14 parts",
  searchUnavailable: "Search is unavailable.",
  searchType: "Type to search 14 parts.",
  searchLoading: "Loading…",
  searchNone: "No results.",
  searchClose: "Close search",
  searchResults: "Search results",

  // Home page.
  homeEyebrow: (parts: string, sections: string) => `Reference · ${parts} parts · ${sections} sections`,
  homeTitle: "All necessary topics related to AI Engineering",
  homeIntro:
    "A dense, citation-backed reference for the fundamentals every applied AI engineer needs — from tokens and tool use to retrieval, context, and agent loops. Each topic ships in three voices: the engineer's version (with code and diagrams), the layman's version (plain English with analogies), and <span lang=\"bn\" class=\"text-voice-bangla\">বাংলা ব্যাখ্যা</span>.",
  contents: "Contents",
  heroLine1: "All necessary topics",
  heroLine2: "of AI engineering,",
  heroAccent: "in three voices",
  startReading: "Start reading",
  seeContents: "See all contents →",
  statParts: "Parts",
  statSections: "Sections",
  statSources: "Sources",
  statVoices: "Voices",
  coverTag: "AI ENGINEERING · REFERENCE",
  coverTitle: ["Applied", "AI", "Engineering"] as [string, string, string],
  coverSub: "From tokens to agents · English + বাংলা",
  coverLabel: "INSIDE",
  coverValue: (parts: string, sections: string) => `${parts} parts · ${sections} sections`,
  whyEyebrow: "Features",
  whyTitle: "Why this reference?",
  features: [
    {
      icon: "🗣️",
      title: "Three voices",
      text: "Each section has a technical version with code, a plain-English version, and a বাংলা ব্যাখ্যা. Switch any time.",
    },
    {
      icon: "📚",
      title: "Every claim cited",
      text: "Citations go to the primary papers, vendor docs, and team blogs. Each one was checked against the publisher.",
    },
    {
      icon: "🛠️",
      title: "Practice tasks",
      text: "Sections end with hands-on tasks, so you build the idea instead of only reading about it.",
    },
    {
      icon: "✅",
      title: "Progress tracking",
      text: "Mark each section as done. Your progress stays in this browser. No account, no login.",
    },
    {
      icon: "📴",
      title: "Works offline",
      text: "Install the site as an app. It saves every page, so you can read on a train or a plane.",
    },
    {
      icon: "🌗",
      title: "Dark and light",
      text: "A warm paper theme for the day and a dark theme for the night. It follows your device.",
    },
  ] as Feature[],
  partsEyebrow: "Structure",
  partsTitle: "The 14 parts",
  partsIntro: "Read in order, or jump to the part you need. Each part stands on its own.",
  sectionCount: (n: number) => `${n} ${n === 1 ? "section" : "sections"}`,

  // Contents page.
  contentsTitle: "All contents",
  contentsIntro: "Every part and section in reading order. A check mark shows a section you marked as done.",
  doneLabel: "Sections done",
  totalLabel: "Total sections",
  percentLabel: "Complete",
  continueReading: "Continue reading →",
  startOver: "Start over",
  startOverConfirm: "Clear the progress of all sections?",
  allDone: "You finished every section.",
  doneMark: "Done",

  // Progress on a topic page.
  markDone: "Mark as done",
  markedDone: "Done · click to undo",
  markRead: "Mark as read",
  markedRead: "Read",
  sectionDone: "Section done",

  // Footer.
  footerSite: "Site",
  footerSource: "Source on GitHub",
  footerCopy: "AI Engineering reference",

  // Topic page.
  topicMeta: (sections: number, sources: number) =>
    `${sections} ${sections === 1 ? "section" : "sections"} · ${sources} ${sources === 1 ? "source" : "sources"} · three voices`,
  references: "References",
  sources: "Sources",
  sourcesNote:
    "All citations resolve to primary papers (arXiv), vendor docs (OpenAI, Anthropic, Google), or official team blogs. IDs were verified by fetching each page and extracting the citation metadata.",

  // Voices.
  voiceGroup: "Voice",
  voiceMain: "Technical",
  voiceLayman: "Layman's",
  voiceBangla: "বাংলা",
  voiceAll: "All three",
  laymanTitle: "Layman's version",
  laymanNote: "plain English, no jargon",
  banglaTitle: "বাংলা ব্যাখ্যা",
  banglaNote: "সহজ ভাষায় বিস্তারিত",

  // Videos.
  watch: (n: number) => `Watch · ${n} ${n === 1 ? "video" : "videos"}`,
  playVideo: (title: string) => `Play video: ${title}`,

  // Live views: pages from other sites, shown in a frame.
  liveHeading: (n: number) => `Live view · ${n} ${n === 1 ? "page" : "pages"}`,
  liveLoad: "Load live view",
  liveLoadHint: "The page loads from its own site when you click.",
  liveLoadLabel: (title: string) => `Load live view: ${title}`,
  liveOpen: "Open in a new tab",
  liveWide: "Works best on a wide screen.",

  // 404.
  notFoundEyebrow: "Error 404",
  notFoundTitle: "Page not found",
  notFoundText: "That page does not exist. All 14 parts are listed on the home page.",
  notFoundBack: "← Back to all parts",
};

export type Dict = typeof en;

const bn: Dict = {
  siteName: "AI Engineering",
  skipLink: "মূল লেখায় যাও",
  footer: "১৪টি part · প্রতিটি source প্রকাশকের তথ্যের সাথে মিলিয়ে যাচাই করা।",
  metaTitle: "AI Engineering — দরকারি সব বিষয়, বাংলায়",
  metaDescription:
    "Applied AI engineer-এর দরকারি সব বিষয় ১৪টি part-এ: LLM-এর মূল ধারণা, prompt engineering থেকে agent, inference, evaluation, safety আর AI app architecture পর্যন্ত। প্রতিটি বিষয় সহজ বাংলা ব্যাখ্যা, practice task আর video সহ।",

  langSwitchText: "English",
  langSwitchLabel: "Read in English",
  themeToLight: "Light theme-এ যাও",
  themeToDark: "Dark theme-এ যাও",
  themeGeneric: "Theme বদলাও",
  installApp: "এই site-টা app হিসেবে install করো",

  partsNav: "Part-গুলো",
  part: (n: string) => `Part ${n}`,
  openParts: "Part-এর তালিকা খোলো",
  closeParts: "Part-এর তালিকা বন্ধ করো",
  onThisPage: "এই পাতায়",
  prevNextNav: "আগের আর পরের Part",

  search: "খোঁজো",
  searchAll: "১৪টি part-এ খোঁজো",
  searchUnavailable: "এখন search কাজ করছে না।",
  searchType: "১৪টি part-এ খুঁজতে লেখো।",
  searchLoading: "Load হচ্ছে…",
  searchNone: "কিছু পাওয়া যায়নি।",
  searchClose: "Search বন্ধ করো",
  searchResults: "Search-এর ফলাফল",

  homeEyebrow: (parts: string, sections: string) => `Reference · ${parts}টি part · ${sections}টি section`,
  homeTitle: "AI Engineering-এর দরকারি সব বিষয়",
  homeIntro:
    "একজন AI engineer-এর যা যা জানা দরকার, সব এক জায়গায়: token আর tool use থেকে শুরু করে retrieval, context আর agent loop পর্যন্ত। প্রতিটি বিষয়ে আছে সহজ <span class=\"text-voice-bangla\">বাংলা ব্যাখ্যা</span>, হাতে-কলমে practice task আর video। চাইলে technical English version আর সহজ English version-ও পড়তে পারো।",
  contents: "সূচিপত্র",
  heroLine1: "AI Engineering-এর",
  heroLine2: "দরকারি সব বিষয়,",
  heroAccent: "সহজ বাংলায়",
  startReading: "পড়া শুরু করো",
  seeContents: "পুরো সূচিপত্র দেখো →",
  statParts: "Part",
  statSections: "Section",
  statSources: "Source",
  statVoices: "ব্যাখ্যার ধরন",
  coverTag: "AI ENGINEERING · REFERENCE",
  coverTitle: ["Applied", "AI", "Engineering"],
  coverSub: "Token থেকে agent পর্যন্ত · বাংলা + English",
  coverLabel: "ভেতরে আছে",
  coverValue: (parts: string, sections: string) => `${parts}টি part · ${sections}টি section`,
  whyEyebrow: "বৈশিষ্ট্য",
  whyTitle: "কেন এই reference?",
  features: [
    {
      icon: "🗣️",
      title: "তিনভাবে ব্যাখ্যা",
      text: "প্রতিটি section-এ আছে code সহ technical version, সহজ English version আর সহজ বাংলা ব্যাখ্যা। যখন খুশি বদলাও।",
    },
    {
      icon: "📚",
      title: "প্রতিটি তথ্যের source",
      text: "Citation-গুলো মূল paper, vendor docs আর team blog-এ যায়। প্রতিটি প্রকাশকের তথ্যের সাথে মিলিয়ে দেখা।",
    },
    {
      icon: "🛠️",
      title: "Practice task",
      text: "Section-এর শেষে হাতে-কলমে কাজ আছে, যাতে শুধু পড়া না, নিজে বানিয়ে শেখো।",
    },
    {
      icon: "✅",
      title: "Progress tracking",
      text: "প্রতিটি section শেষ হলে done চিহ্ন দাও। Progress এই browser-এই থাকে। Account বা login লাগে না।",
    },
    {
      icon: "📴",
      title: "Offline-এও চলে",
      text: "Site-টা app হিসেবে install করো। সব পাতা save হয়ে থাকে, তাই internet ছাড়াও পড়া যায়।",
    },
    {
      icon: "🌗",
      title: "Dark আর light",
      text: "দিনের জন্য কাগজের মতো light theme, রাতের জন্য dark theme। তোমার device-এর setting মেনে চলে।",
    },
  ],
  partsEyebrow: "কাঠামো",
  partsTitle: "১৪টি part",
  partsIntro: "ক্রম অনুযায়ী পড়ো, অথবা যে part দরকার সেখানে যাও। প্রতিটি part নিজে নিজেই সম্পূর্ণ।",
  sectionCount: (n: number) => `${fmtNum("bn", n)}টি section`,

  contentsTitle: "সম্পূর্ণ সূচিপত্র",
  contentsIntro: "সব part আর section পড়ার ক্রমে। যে section done করেছ, তার পাশে টিক চিহ্ন থাকে।",
  doneLabel: "শেষ করা section",
  totalLabel: "মোট section",
  percentLabel: "সম্পূর্ণ",
  continueReading: "পড়া চালিয়ে যাও →",
  startOver: "আবার শুরু করো",
  startOverConfirm: "সব section-এর progress মুছে ফেলবে?",
  allDone: "তুমি সব section শেষ করেছ।",
  doneMark: "শেষ",

  markDone: "শেষ হয়েছে, চিহ্ন দাও",
  markedDone: "শেষ · বাতিল করতে click করো",
  markRead: "পড়া হয়েছে, চিহ্ন দাও",
  markedRead: "পড়া হয়েছে",
  sectionDone: "Section শেষ",

  footerSite: "Site",
  footerSource: "GitHub-এ source code",
  footerCopy: "AI Engineering reference",

  topicMeta: (sections: number, sources: number) =>
    `${fmtNum("bn", sections)}টি section · ${fmtNum("bn", sources)}টি source · তিনভাবে ব্যাখ্যা`,
  references: "তথ্যসূত্র",
  sources: "Sources",
  sourcesNote:
    "সব citation মূল paper (arXiv), vendor-এর docs (OpenAI, Anthropic, Google) বা official team blog-এ যায়। প্রতিটি পাতা খুলে citation-এর তথ্য যাচাই করা হয়েছে।",

  voiceGroup: "ব্যাখ্যার ধরন",
  voiceMain: "Technical",
  voiceLayman: "সহজ English",
  voiceBangla: "বাংলা",
  voiceAll: "সবগুলো",
  laymanTitle: "Layman's version",
  laymanNote: "সহজ English-এ, jargon ছাড়া",
  banglaTitle: "বাংলা ব্যাখ্যা",
  banglaNote: "সহজ ভাষায় বিস্তারিত",

  watch: (n: number) => `ভিডিও দেখো · ${fmtNum("bn", n)}টি`,
  playVideo: (title: string) => `Video চালাও: ${title}`,

  liveHeading: (n: number) => `সরাসরি দেখো · ${fmtNum("bn", n)}টি পাতা`,
  liveLoad: "সরাসরি দেখো",
  liveLoadHint: "Click করলে পাতাটি তার নিজের সাইট থেকে load হয়।",
  liveLoadLabel: (title: string) => `সরাসরি দেখো: ${title}`,
  liveOpen: "নতুন tab-এ খোলো",
  liveWide: "বড় screen-এ সবচেয়ে ভালো কাজ করে।",

  notFoundEyebrow: "Error 404",
  notFoundTitle: "পাতাটি পাওয়া যায়নি",
  notFoundText: "এই পাতাটি নেই। Home page-এ ১৪টি part-এর তালিকা আছে।",
  notFoundBack: "← সব part-এ ফিরে যাও",
};

export const UI: Record<Lang, Dict> = { en, bn };
