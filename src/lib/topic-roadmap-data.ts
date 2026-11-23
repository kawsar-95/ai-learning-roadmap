// Server-only access to the Part roadmaps. Never import this module from a
// "use client" file; pass the data down as props.
//
// The file goes through TopicRoadmapsSchema and roadmapProblems at module
// load, so a bad roadmap fails `next build`.

import { TopicRoadmapsSchema, roadmapProblems } from "@/lib/topic-roadmap";
import type { PathTrack, TopicRoadmap } from "@/lib/topic-roadmap";
import { TOPICS } from "@/lib/topics";
import file from "@/data/topic-roadmaps.json";

const parsed = TopicRoadmapsSchema.parse(file);

const problems = roadmapProblems(
  parsed,
  TOPICS.map((t) => ({
    slug: t.slug,
    sectionIds: t.sections.map((s) => s.id),
    headingIds: t.sections.flatMap((s) => s.body.flatMap((b) => (b.type === "heading" && b.level === 3 ? [b.id] : []))),
  })),
);
if (problems.length) throw new Error(`src/data/topic-roadmaps.json:\n${problems.join("\n")}`);

/** The tracks of the path across all Parts, in reading order. */
export const LEARNING_PATH: readonly PathTrack[] = parsed.path;

export function getTopicRoadmap(slug: string): TopicRoadmap | undefined {
  return parsed.roadmaps[slug];
}
