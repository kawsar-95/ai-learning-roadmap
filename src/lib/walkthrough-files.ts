// Gives a Part's sections the walk-throughs that have files of their own. Part 18 keeps its walk-throughs inline in
// its Part file; the other Parts keep theirs in src/content/walkthroughs/<Part>/<section>.json, which
// scripts/walkthroughs/build.py writes from its sources. Server only: it imports the zod schema, so a client file
// must not import it. It has no "@/" imports, so `node --test` can load it.

import { WalkthroughSchema } from "./content-schema.ts";
import type { Section, TopicFile, Walkthrough } from "./content-schema.ts";

/** The walk-through files of one Part, by section id. Each is parsed here, so it is `unknown` until then. */
export type WalkthroughFiles = Record<string, unknown>;

/**
 * The Part with each file's walk-through on its section. A file must belong to a section of the Part, and a section
 * has its walk-through in one place only: its Part file or its own file. Every file goes through WalkthroughSchema,
 * so a bad one fails `next build` and names the file.
 */
export function attachWalkthroughs(topic: TopicFile, files: WalkthroughFiles | undefined): TopicFile {
  if (!files) return topic;
  const ids = new Set(topic.sections.map((section) => section.id));
  for (const id of Object.keys(files)) {
    if (!ids.has(id)) throw new Error(`walkthroughs/${topic.slug}/${id}.json: ${topic.slug} has no section "${id}"`);
  }
  return {
    ...topic,
    sections: topic.sections.map((section): Section => {
      if (!(section.id in files)) return section;
      const where = `walkthroughs/${topic.slug}/${section.id}.json`;
      if (section.walkthrough) {
        throw new Error(`${topic.slug} section "${section.id}" has a walk-through in its Part file and in ${where}`);
      }
      const parsed = WalkthroughSchema.safeParse(files[section.id]);
      if (!parsed.success) throw new Error(`${where}: ${parsed.error.message}`);
      return { ...section, walkthrough: parsed.data as Walkthrough };
    }),
  };
}
