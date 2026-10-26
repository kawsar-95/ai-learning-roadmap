import type { Metadata } from "next";
import { RoadmapPage } from "@/components/pages/RoadmapPage";
import { UI } from "@/lib/i18n";

export const metadata: Metadata = { title: UI.bn.roadmapTitle };

export default function Roadmap() {
  return <RoadmapPage lang="bn" />;
}
