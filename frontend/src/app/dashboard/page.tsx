"use client";

import { Header } from "@/shared/ui/header";
import { DashboardStashWidget } from "@/widgets/stash-table";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-surface-background p-6 md:p-10 flex flex-col items-center relative overflow-hidden">
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-brand-amber/10 rounded-full blur-[120px] pointer-events-none" />

      <Header />
      <DashboardStashWidget />
    </div>
  );
}
