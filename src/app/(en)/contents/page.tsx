import type { Metadata } from "next";
import { ContentsPage } from "@/components/pages/ContentsPage";
import { UI } from "@/lib/i18n";

export const metadata: Metadata = { title: UI.en.contentsTitle };

export default function Contents() {
  return <ContentsPage lang="en" />;
}
