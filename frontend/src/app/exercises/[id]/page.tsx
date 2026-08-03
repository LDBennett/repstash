"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Header } from "@/shared/ui/header";
import { ExerciseDetailWidget } from "@/widgets/exercise-detail";

export default function ExercisePage() {
  const params = useParams();
  const id = parseInt(params.id as string, 10);

  return (
    <div className="min-h-screen bg-surface-background p-6 md:p-10 flex flex-col items-center relative overflow-hidden">
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-brand-amber/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Since Header is shared, we can inject a back link right below or above it for navigation */}
      <div className="w-full max-w-4xl mx-auto flex items-center justify-between mb-8 relative z-10">
        <Link href="/dashboard" className="flex items-center gap-2 text-text-muted hover:text-text-primary transition-colors font-medium">
          <ArrowLeft className="w-5 h-5" />
          Back to Stash
        </Link>
      </div>
      
      {/* We can still use the shared header, or just skip it if we want the back button to dominate. But Header brings the Logo and UserButton. */}
      {/* Let's wrap it nicely */}
      <div className="w-full max-w-4xl mx-auto -mt-6">
         <Header />
      </div>

      <ExerciseDetailWidget id={id} />
    </div>
  );
}
