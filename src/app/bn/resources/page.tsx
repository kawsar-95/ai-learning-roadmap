import type { Metadata } from "next";
import { ResourcesPage } from "@/components/pages/ResourcesPage";
import { UI } from "@/lib/i18n";

export const metadata: Metadata = { title: UI.bn.resourcesTitle };

export default function Resources() {
  return <ResourcesPage lang="bn" />;
}
