import { TOPICS } from "@/lib/topics";
import { findWalkthrough, walkthroughParams } from "@/lib/walkthrough";

// One static JSON file for each section that has a walk-through, at
// /walkthroughs/<Part>/<section>.json, with the English and the Bangla text in
// one file. The page loads it when the section is first shown, so the walk-
// throughs are not in the HTML and the RSC payload of the Part.
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  return walkthroughParams(TOPICS);
}

export async function GET(_request: Request, { params }: { params: Promise<{ slug: string; file: string }> }) {
  const { slug, file } = await params;
  const walkthrough = findWalkthrough(TOPICS, slug, file);
  if (!walkthrough) return new Response("Not found", { status: 404 });
  return Response.json(walkthrough);
}
