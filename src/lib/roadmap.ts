// Server-only access to the roadmap. Never import this module from a
// "use client" file; pass the data down as props.
//
// The two JSON files go through buildRoadmap at module load, so bad content
// fails `next build`.

import { buildRoadmap } from "@/lib/roadmap-schema";
import type { Phase } from "@/lib/roadmap-schema";
import lessonsFile from "@/data/roadmap-lessons.json";
import phasesFile from "@/data/roadmap-phases.json";

export const STAGES = buildRoadmap(lessonsFile, phasesFile);
export const PHASES: Phase[] = STAGES.flatMap((stage) => stage.phases);
