// The per-Part learning roadmaps: the data format and a checker. The data is in
// src/data/topic-roadmaps.json. This file has no React and no `@/` imports, so
// `node --test` can use it.
//
// A roadmap orders the sections of one Part into stages. It does not change the
// Part: a stage only points at section ids (or, for a one-section Part, at
// heading ids), so renaming nothing and no saved progress is affected.

import { z } from "zod";

export const ROADMAP_LEVELS = ["beginner", "intermediate", "advanced"] as const;
export type RoadmapLevel = (typeof ROADMAP_LEVELS)[number];

const Text = z.string().trim().min(1);
const StageText = z.strictObject({
  /** The name of the stage. */
  title: Text,
  /** What the reader can do after the stage. */
  goal: Text,
  /** One small thing to build to prove it. */
  build: Text,
});

const Stage = z.strictObject({
  level: z.enum(ROADMAP_LEVELS),
  en: StageText,
  bn: StageText,
  /** Section ids, or heading ids for a one-section Part, in the order to read. */
  targets: z.array(Text).min(1),
});

const Roadmap = z.strictObject({
  /** Parts to read first (slugs). */
  before: z.array(Text),
  /** Parts to read next (slugs). */
  after: z.array(Text),
  en: z.strictObject({ goal: Text }),
  bn: z.strictObject({ goal: Text }),
  stages: z.array(Stage).min(2),
});

/** One track of the path across all Parts: a name and the Parts to read, in order. */
const Track = z.strictObject({ en: Text, bn: Text, parts: z.array(Text).min(1) });

export const TopicRoadmapsSchema = z.strictObject({
  /** The order to read every Part in, in tracks. Each Part is in exactly one track. */
  path: z.array(Track).min(2),
  roadmaps: z.record(Text, Roadmap),
});

export type TopicRoadmap = z.infer<typeof Roadmap>;
export type PathTrack = z.infer<typeof Track>;
export type RoadmapStage = z.infer<typeof Stage>;
export type TopicRoadmapsFile = z.infer<typeof TopicRoadmapsSchema>;

/** What the checker needs to know about a Part. */
export type RoadmapPart = {
  slug: string;
  sectionIds: string[];
  /** The ids of the level 3 headings, for a one-section Part. */
  headingIds: string[];
};

const BANGLA = /[\u0980-\u09FF]/u;
// A Latin digit that is not part of a name such as "BM25".
const ASCII_DIGIT = /(?<![A-Za-z0-9])[0-9]/;
const TAG = /<\/?[a-zA-Z][^>]*>/;

/**
 * The problems of a roadmaps file, one message each. `parts` is every Part
 * with its ids. When `requireAll` is true, every Part must have a roadmap.
 * An empty list means the file is good.
 */
export function roadmapProblems(file: TopicRoadmapsFile, parts: RoadmapPart[], requireAll = false): string[] {
  const problems: string[] = [];
  const bySlug = new Map(parts.map((p) => [p.slug, p]));

  if (requireAll) {
    for (const part of parts) {
      if (!file.roadmaps[part.slug]) problems.push(`${part.slug}: has no roadmap`);
    }
  }

  // The path across Parts: every Part once, nothing unknown.
  const onPath = new Set<string>();
  for (const track of file.path) {
    for (const slug of track.parts) {
      if (!bySlug.has(slug)) problems.push(`path: unknown Part "${slug}"`);
      else if (onPath.has(slug)) problems.push(`path: "${slug}" is in two tracks`);
      onPath.add(slug);
    }
    if (!BANGLA.test(track.bn) || BANGLA.test(track.en)) problems.push(`path: wrong language in track "${track.en}"`);
  }
  if (requireAll) {
    for (const part of parts) {
      if (!onPath.has(part.slug)) problems.push(`path: "${part.slug}" is in no track`);
    }
  }

  for (const [slug, roadmap] of Object.entries(file.roadmaps)) {
    const part = bySlug.get(slug);
    if (!part) {
      problems.push(`${slug}: is not a Part`);
      continue;
    }

    for (const other of [...roadmap.before, ...roadmap.after]) {
      if (!bySlug.has(other)) problems.push(`${slug}: points at unknown Part "${other}"`);
      if (other === slug) problems.push(`${slug}: points at itself`);
    }

    // A one-section Part has nothing to point at but its headings.
    const single = part.sectionIds.length === 1;
    const valid = new Set(single ? part.headingIds : part.sectionIds);
    const seen = new Set<string>();
    for (const stage of roadmap.stages) {
      for (const target of stage.targets) {
        if (!valid.has(target)) problems.push(`${slug}: unknown target "${target}"`);
        else if (seen.has(target)) problems.push(`${slug}: "${target}" is in two stages`);
        seen.add(target);
      }
    }
    for (const id of valid) {
      if (!seen.has(id)) problems.push(`${slug}: "${id}" is in no stage`);
    }

    // Plain text, in the right language. Bangla numbers use Bangla digits, as the quizzes do.
    const texts: { lang: "en" | "bn"; text: string }[] = [
      { lang: "en", text: roadmap.en.goal },
      { lang: "bn", text: roadmap.bn.goal },
      ...roadmap.stages.flatMap((stage) =>
        (["en", "bn"] as const).flatMap((lang) =>
          [stage[lang].title, stage[lang].goal, stage[lang].build].map((text) => ({ lang, text })),
        ),
      ),
    ];
    for (const { lang, text } of texts) {
      if (TAG.test(text)) problems.push(`${slug}: plain text has a tag: "${text}"`);
      if (lang === "en" && BANGLA.test(text)) problems.push(`${slug}: English text has Bangla letters: "${text}"`);
      if (lang === "bn" && !BANGLA.test(text)) problems.push(`${slug}: Bangla text has no Bangla letters: "${text}"`);
      if (lang === "bn" && ASCII_DIGIT.test(text.replace(/`[^`]*`/g, ""))) {
        problems.push(`${slug}: Bangla text has Latin digits: "${text}"`);
      }
    }
  }

  return problems;
}
