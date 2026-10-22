import type { Metadata } from "next";
import { InterviewPage } from "@/components/pages/InterviewPage";
import { UI } from "@/lib/i18n";

export const metadata: Metadata = { title: UI.bn.interviewTitle };

export default function Interview() {
  return <InterviewPage lang="bn" />;
}
