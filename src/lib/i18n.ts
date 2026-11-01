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
export function dashboardHref(lang: Lang): string {
  return lang === "bn" ? "/bn/dashboard/" : "/dashboard/";
}
export function interviewHref(lang: Lang): string {
  return lang === "bn" ? "/bn/interview/" : "/interview/";
}
export function roadmapHref(lang: Lang): string {
  return lang === "bn" ? "/bn/roadmap/" : "/roadmap/";
}
export function resourcesHref(lang: Lang): string {
  return lang === "bn" ? "/bn/resources/" : "/resources/";
}

/** The source code of the site. */
export const REPO_URL = "https://github.com/kawsar-95/ai-learning-roadmap";

/** The GitHub profile of the author. */
export const AUTHOR_GITHUB_URL = "https://github.com/kawsar-95";

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
  siteName: "Learn AI",
  skipLink: "Skip to content",
  footer: "14 parts · citations verified against each publisher's metadata.",
  metaTitle: "Learn AI — All Necessary Topics",
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

  // Roadmap page.
  roadmap: "Roadmap",
  roadmapTitle: "AI engineering roadmap",
  roadmapIntro:
    "A study path through the open AI Engineering from Scratch curriculum: 20 phases, from setup and math to agents, production and capstone projects. Each lesson opens on the curriculum site. Tick the lessons you finish; your progress stays in this browser.",
  roadmapLessonsDone: "Lessons done",
  roadmapLessonsTotal: "Total lessons",
  roadmapTimeLeft: "Left to study",
  roadmapCoreOnly: "Show the suggested path only",
  roadmapCoreNote: "The suggested path skips the five optional phases (vision, speech, generative models, reinforcement learning, multimodal). Switch it off to see all 20.",
  roadmapPhase: (n: string) => `Phase ${n}`,
  roadmapCore: "Suggested",
  roadmapOptional: "Optional depth",
  roadmapLessons: (n: string) => `${n} lessons`,
  roadmapRelated: "Covered in the Parts",
  roadmapMarkLesson: (title: string) => `Mark done: ${title}`,
  roadmapUnmarkLesson: (title: string) => `Done, click to undo: ${title}`,
  roadmapResetConfirm: "Clear the progress of all roadmap lessons?",
  roadmapSource: "Source: the ROADMAP.md of the curriculum. Lesson titles stay in English.",
  pathsTitle: "Learning paths",
  pathsIntro: "Not sure where to start? Pick one path. Each path is a short list of lessons from the phases below, in a good order.",
  pathsStartHere: "Start here",
  pathsCore: "Core path",
  pathsFocused: "Focused path",
  pathsStart: "Start path",
  lessonPrev: "Previous lesson",
  lessonNext: "Next lesson",
  lessonNav: "Lesson navigation",
  resources: "Resources",
  resourcesTitle: "Open-source repos to learn from",
  resourcesIntro:
    "Twenty well-known GitHub repositories for AI engineers. Each card says what the repo is for and which roadmap phase it fits. The links open GitHub.",
  resourcesBangla: "Bangla translation ↗",
  resourcesNote: "Star counts change, so they are not shown. Check each repo's license before you reuse its code or text.",
  lessonCode: "Code and tests on GitHub ↗",
  lessonCredit: "Lesson text from AI Engineering from Scratch by Rohit Ghumare and contributors, under the",

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
  dashboard: "Dashboard",
  dashboardTitle: "Your dashboard",
  dashboardIntro: "Where you stopped, and the sections you saved.",
  bookmarksTitle: "Bookmarks",
  bookmarksEmpty: "No bookmarks yet. Use the Bookmark button at the end of a section.",
  removeBookmark: "Remove",
  doneMark: "Done",

  // Progress on a topic page.
  markDone: "Mark as done",
  markedDone: "Done · click to undo",
  markRead: "Mark as read",
  markedRead: "Read",
  bookmark: "Bookmark",
  interview: "Interview",
  interviewTitle: "Interview questions",
  interviewIntro:
    "Three questions for each part, with a short answer. Open a question to see it, and follow the link to read the full section.",
  readSection: "Read the section →",
  authorEyebrow: "Author",
  authorBy: "Built and maintained by",
  authorGithub: "GitHub ↗",
  quizTitle: "Quiz",
  quizIntro: (n: number) => `Check what you learned. ${n} ${n === 1 ? "question" : "questions"}.`,
  quizCheck: "Check answers",
  quizAnswerAll: "Answer every question to check.",
  quizRetry: "Try again",
  quizScore: (c: string, t: string) => `Score: ${c} / ${t}`,
  quizBest: (c: string, t: string) => `Best: ${c} / ${t}`,
  quizCorrect: "Correct",
  quizWrong: "Not quite",
  quizRightAnswer: "Right answer:",
  quizTrue: "True",
  quizFalse: "False",
  quizQuestions: (n: number) => `${n} ${n === 1 ? "question" : "questions"}`,
  goToQuiz: "Go to quiz",
  stepNav: "Sections of this Part",
  stepOf: (n: string, total: string) => `Section ${n} of ${total}`,
  stepPrev: "Previous",
  stepNext: "Next",
  sectionDone: "Section done",

  // Footer.
  footerSite: "Site",
  footerSource: "Source on GitHub",
  footerCopy: "Learn AI reference",

  // Topic page.
  minRead: (n: string) => `${n} min read`,
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
  siteName: "Learn AI",
  skipLink: "মূল লেখায় যান",
  footer: "১৪টি পার্ট · প্রতিটি সোর্স প্রকাশকের তথ্যের সাথে মিলিয়ে যাচাই করা।",
  metaTitle: "Learn AI — দরকারি সব বিষয়, বাংলায়",
  metaDescription:
    "অ্যাপ্লাইড AI ইঞ্জিনিয়ারের দরকারি সব বিষয় ১৪টি পার্টে: LLM-এর মূল ধারণা, প্রম্পট ইঞ্জিনিয়ারিং থেকে এজেন্ট, ইনফারেন্স, ইভ্যালুয়েশন, সেফটি আর AI অ্যাপ আর্কিটেকচার পর্যন্ত। প্রতিটি বিষয় সহজ বাংলা ব্যাখ্যা, প্র্যাকটিস টাস্ক আর ভিডিও সহ।",

  langSwitchText: "English",
  langSwitchLabel: "Read in English",
  themeToLight: "লাইট থিমে যান",
  themeToDark: "ডার্ক থিমে যান",
  themeGeneric: "থিম বদলান",
  installApp: "এই সাইটটা অ্যাপ হিসেবে ইনস্টল করুন",

  partsNav: "পার্টগুলো",
  part: (n: string) => `পার্ট ${n}`,
  openParts: "পার্টের তালিকা খুলুন",
  closeParts: "পার্টের তালিকা বন্ধ করুন",
  onThisPage: "এই পাতায়",
  prevNextNav: "আগের আর পরের পার্ট",

  search: "খুঁজুন",
  searchAll: "১৪টি পার্টে খুঁজুন",
  searchUnavailable: "এখন সার্চ কাজ করছে না।",
  searchType: "১৪টি পার্টে খুঁজতে লিখুন।",
  searchLoading: "লোড হচ্ছে…",
  searchNone: "কিছু পাওয়া যায়নি।",
  searchClose: "সার্চ বন্ধ করুন",
  searchResults: "সার্চের ফলাফল",

  homeEyebrow: (parts: string, sections: string) => `রেফারেন্স · ${parts}টি পার্ট · ${sections}টি সেকশন`,
  homeTitle: "AI Engineering-এর দরকারি সব বিষয়",
  homeIntro:
    "একজন AI ইঞ্জিনিয়ারের যা যা জানা দরকার, সব এক জায়গায়: টোকেন আর টুল ইউজ থেকে শুরু করে রিট্রিভাল, কনটেক্সট আর এজেন্ট লুপ পর্যন্ত। প্রতিটি বিষয়ে আছে সহজ <span class=\"text-voice-bangla\">বাংলা ব্যাখ্যা</span>, হাতে-কলমে প্র্যাকটিস টাস্ক আর ভিডিও। চাইলে টেকনিক্যাল English ভার্সন আর সহজ English ভার্সনও পড়তে পারেন।",
  contents: "সূচিপত্র",
  heroLine1: "AI Engineering-এর",
  heroLine2: "দরকারি সব বিষয়,",
  heroAccent: "সহজ বাংলায়",
  startReading: "পড়া শুরু করুন",
  seeContents: "পুরো সূচিপত্র দেখুন →",
  statParts: "পার্ট",
  statSections: "সেকশন",
  statSources: "সোর্স",
  statVoices: "ব্যাখ্যার ধরন",
  coverTag: "AI ENGINEERING · REFERENCE",
  coverTitle: ["Applied", "AI", "Engineering"],
  coverSub: "টোকেন থেকে এজেন্ট পর্যন্ত · বাংলা + English",
  coverLabel: "ভেতরে আছে",
  coverValue: (parts: string, sections: string) => `${parts}টি পার্ট · ${sections}টি সেকশন`,
  whyEyebrow: "বৈশিষ্ট্য",
  whyTitle: "কেন এই রেফারেন্স?",
  features: [
    {
      icon: "🗣️",
      title: "তিনভাবে ব্যাখ্যা",
      text: "প্রতিটি সেকশনে আছে কোড সহ টেকনিক্যাল ভার্সন, সহজ English ভার্সন আর সহজ বাংলা ব্যাখ্যা। যখন খুশি বদলান।",
    },
    {
      icon: "📚",
      title: "প্রতিটি তথ্যের সোর্স",
      text: "সাইটেশনগুলো মূল পেপার, ভেন্ডরের ডক্স আর টিম ব্লগে যায়। প্রতিটি প্রকাশকের তথ্যের সাথে মিলিয়ে দেখা।",
    },
    {
      icon: "🛠️",
      title: "প্র্যাকটিস টাস্ক",
      text: "সেকশনের শেষে হাতে-কলমে কাজ আছে, যাতে শুধু পড়া না, নিজে বানিয়ে শিখতে পারেন।",
    },
    {
      icon: "✅",
      title: "প্রগ্রেস ট্র্যাকিং",
      text: "প্রতিটি সেকশন শেষ হলে শেষ চিহ্ন দিন। প্রগ্রেস এই ব্রাউজারেই থাকে। অ্যাকাউন্ট বা লগইন লাগে না।",
    },
    {
      icon: "📴",
      title: "অফলাইনেও চলে",
      text: "সাইটটা অ্যাপ হিসেবে ইনস্টল করুন। সব পাতা সেভ হয়ে থাকে, তাই ইন্টারনেট ছাড়াও পড়া যায়।",
    },
    {
      icon: "🌗",
      title: "ডার্ক আর লাইট",
      text: "দিনের জন্য কাগজের মতো লাইট থিম, রাতের জন্য ডার্ক থিম। আপনার ডিভাইসের সেটিং মেনে চলে।",
    },
  ],
  partsEyebrow: "কাঠামো",
  partsTitle: "১৪টি পার্ট",
  partsIntro: "ক্রম অনুযায়ী পড়ুন, অথবা যে পার্ট দরকার সেখানে যান। প্রতিটি পার্ট নিজে নিজেই সম্পূর্ণ।",
  sectionCount: (n: number) => `${fmtNum("bn", n)}টি সেকশন`,

  roadmap: "রোডম্যাপ",
  roadmapTitle: "AI engineering রোডম্যাপ",
  roadmapIntro:
    "ওপেন সোর্স AI Engineering from Scratch কারিকুলামের ওপর একটি পড়ার পথ: সেটআপ আর ম্যাথ থেকে এজেন্ট, প্রোডাকশন আর ক্যাপস্টোন প্রজেক্ট পর্যন্ত ২০টি ফেজ। প্রতিটি লেসন কারিকুলামের সাইটে খোলে। যে লেসন শেষ করলেন তাতে টিক দিন; প্রগ্রেস এই ব্রাউজারেই থাকে।",
  roadmapLessonsDone: "শেষ করা লেসন",
  roadmapLessonsTotal: "মোট লেসন",
  roadmapTimeLeft: "পড়তে বাকি",
  roadmapCoreOnly: "শুধু প্রস্তাবিত পথ দেখান",
  roadmapCoreNote: "প্রস্তাবিত পথে পাঁচটি ঐচ্ছিক ফেজ (ভিশন, স্পিচ, জেনারেটিভ মডেল, reinforcement learning, multimodal) বাদ যায়। ২০টি ফেজই দেখতে এটি বন্ধ করুন।",
  roadmapPhase: (n: string) => `ফেজ ${n}`,
  roadmapCore: "প্রস্তাবিত",
  roadmapOptional: "ঐচ্ছিক গভীরতা",
  roadmapLessons: (n: string) => `${n}টি লেসন`,
  roadmapRelated: "যেসব পার্টে আছে",
  roadmapMarkLesson: (title: string) => `শেষ চিহ্ন দিন: ${title}`,
  roadmapUnmarkLesson: (title: string) => `শেষ, বাতিল করতে ক্লিক করুন: ${title}`,
  roadmapResetConfirm: "রোডম্যাপের সব লেসনের প্রগ্রেস মুছে ফেলবেন?",
  roadmapSource: "সোর্স: কারিকুলামের ROADMAP.md। লেসনের নাম English-এ থাকে।",
  pathsTitle: "লার্নিং পাথ",
  pathsIntro: "কোথা থেকে শুরু করবেন বুঝতে পারছেন না? একটি পাথ বেছে নিন। প্রতিটি পাথ নিচের ফেজগুলো থেকে বাছাই করা লেসনের একটি ছোট তালিকা, ঠিক ক্রমে সাজানো।",
  pathsStartHere: "এখান থেকে শুরু",
  pathsCore: "মূল পাথ",
  pathsFocused: "ফোকাসড পাথ",
  pathsStart: "পাথ শুরু করুন",
  lessonPrev: "আগের লেসন",
  lessonNext: "পরের লেসন",
  lessonNav: "লেসন নেভিগেশন",
  resources: "রিসোর্স",
  resourcesTitle: "শেখার জন্য ওপেন সোর্স রিপো",
  resourcesIntro:
    "AI ইঞ্জিনিয়ারদের জন্য বিশটি পরিচিত GitHub রিপো। প্রতিটি কার্ডে আছে রিপোটি কী কাজের, আর রোডম্যাপের কোন ফেজের সাথে মেলে। লিংক GitHub-এ খোলে।",
  resourcesBangla: "বাংলা অনুবাদ ↗",
  resourcesNote: "স্টারের সংখ্যা বদলায়, তাই দেখানো হয়নি। কোনো রিপোর কোড বা লেখা আবার ব্যবহার করার আগে তার লাইসেন্স দেখে নিন।",
  lessonCode: "GitHub-এ কোড আর টেস্ট ↗",
  lessonCredit: "লেসনের লেখা English-এ, AI Engineering from Scratch থেকে নেওয়া। লেখক Rohit Ghumare ও সহযোগীরা। লাইসেন্স:",

  contentsTitle: "সম্পূর্ণ সূচিপত্র",
  contentsIntro: "সব পার্ট আর সেকশন পড়ার ক্রমে। যে সেকশন শেষ করেছেন, তার পাশে টিক চিহ্ন থাকে।",
  doneLabel: "শেষ করা সেকশন",
  totalLabel: "মোট সেকশন",
  percentLabel: "সম্পূর্ণ",
  continueReading: "পড়া চালিয়ে যান →",
  startOver: "আবার শুরু করুন",
  startOverConfirm: "সব সেকশনের প্রগ্রেস মুছে ফেলবেন?",
  allDone: "আপনি সব সেকশন শেষ করেছেন।",
  dashboard: "ড্যাশবোর্ড",
  dashboardTitle: "আপনার ড্যাশবোর্ড",
  dashboardIntro: "কোথায় থেমেছেন, আর কোন সেকশন সেভ করেছেন।",
  bookmarksTitle: "বুকমার্ক",
  bookmarksEmpty: "এখনো কোনো বুকমার্ক নেই। কোনো সেকশনের শেষে বুকমার্ক বাটন চাপুন।",
  removeBookmark: "সরান",
  doneMark: "শেষ",

  markDone: "শেষ হয়েছে, চিহ্ন দিন",
  markedDone: "শেষ · বাতিল করতে ক্লিক করুন",
  markRead: "পড়া হয়েছে, চিহ্ন দিন",
  markedRead: "পড়া হয়েছে",
  bookmark: "বুকমার্ক",
  interview: "ইন্টারভিউ",
  interviewTitle: "ইন্টারভিউ প্রশ্ন",
  interviewIntro:
    "প্রতিটি পার্টের তিনটি প্রশ্ন, ছোট উত্তরসহ। প্রশ্ন খুললে উত্তর দেখা যাবে, পুরো সেকশন পড়তে লিংকে যান।",
  readSection: "সেকশন পড়ুন →",
  authorEyebrow: "লেখক",
  authorBy: "যিনি বানিয়েছেন ও দেখভাল করেন",
  authorGithub: "GitHub ↗",
  quizTitle: "কুইজ",
  quizIntro: (n: number) => `কী শিখলেন যাচাই করুন। ${fmtNum("bn", n)}টি প্রশ্ন।`,
  quizCheck: "উত্তর মেলান",
  quizAnswerAll: "মেলাতে সব প্রশ্নের উত্তর দিন।",
  quizRetry: "আবার চেষ্টা করুন",
  quizScore: (c: string, t: string) => `স্কোর: ${c} / ${t}`,
  quizBest: (c: string, t: string) => `সেরা: ${c} / ${t}`,
  quizCorrect: "সঠিক",
  quizWrong: "ঠিক হয়নি",
  quizRightAnswer: "সঠিক উত্তর:",
  quizTrue: "সত্য",
  quizFalse: "মিথ্যা",
  quizQuestions: (n: number) => `${fmtNum("bn", n)}টি প্রশ্ন`,
  goToQuiz: "কুইজে যান",
  stepNav: "এই পার্টের সেকশন",
  stepOf: (n: string, total: string) => `সেকশন ${n} / ${total}`,
  stepPrev: "আগের",
  stepNext: "পরের",
  sectionDone: "সেকশন শেষ",

  footerSite: "সাইট",
  footerSource: "GitHub-এ সোর্স কোড",
  footerCopy: "Learn AI রেফারেন্স",

  minRead: (n: string) => `${n} মিনিট পড়া`,
  references: "তথ্যসূত্র",
  sources: "সোর্স",
  sourcesNote:
    "সব সাইটেশন মূল পেপার (arXiv), ভেন্ডরের ডক্স (OpenAI, Anthropic, Google) বা অফিশিয়াল টিম ব্লগে যায়। প্রতিটি পাতা খুলে সাইটেশনের তথ্য যাচাই করা হয়েছে।",

  voiceGroup: "ব্যাখ্যার ধরন",
  voiceMain: "টেকনিক্যাল",
  voiceLayman: "সহজ English",
  voiceBangla: "বাংলা",
  voiceAll: "সবগুলো",
  laymanTitle: "লেম্যান'স ভার্সন",
  laymanNote: "সহজ English-এ, জার্গন ছাড়া",
  banglaTitle: "বাংলা ব্যাখ্যা",
  banglaNote: "সহজ ভাষায় বিস্তারিত",

  watch: (n: number) => `ভিডিও দেখুন · ${fmtNum("bn", n)}টি`,
  playVideo: (title: string) => `ভিডিও চালান: ${title}`,

  liveHeading: (n: number) => `সরাসরি দেখুন · ${fmtNum("bn", n)}টি পাতা`,
  liveLoad: "সরাসরি দেখুন",
  liveLoadHint: "ক্লিক করলে পাতাটি তার নিজের সাইট থেকে লোড হয়।",
  liveLoadLabel: (title: string) => `সরাসরি দেখুন: ${title}`,
  liveOpen: "নতুন ট্যাবে খুলুন",
  liveWide: "বড় স্ক্রিনে সবচেয়ে ভালো কাজ করে।",

  notFoundEyebrow: "এরর 404",
  notFoundTitle: "পাতাটি পাওয়া যায়নি",
  notFoundText: "এই পাতাটি নেই। হোম পেজে ১৪টি পার্টের তালিকা আছে।",
  notFoundBack: "← সব পার্টে ফিরে যান",
};

export const UI: Record<Lang, Dict> = { en, bn };
