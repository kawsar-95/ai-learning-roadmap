import type { Metadata } from "next";
import { DashboardPage } from "@/components/pages/DashboardPage";
import { UI } from "@/lib/i18n";

export const metadata: Metadata = { title: UI.bn.dashboardTitle };

export default function Dashboard() {
  return <DashboardPage lang="bn" />;
}
