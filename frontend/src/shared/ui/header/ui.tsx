import { UserButton } from "@clerk/nextjs";
import { Dumbbell } from "lucide-react";
import Link from "next/link";

export function Header() {
  return (
    <header className="w-full max-w-7xl mx-auto flex items-center justify-between mb-12 relative z-10">
      <Link href="/" className="flex items-center gap-2 text-text-primary hover:opacity-80 transition-opacity">
        <Dumbbell className="w-7 h-7 text-brand-amber" />
        <span className="font-bold text-2xl tracking-tight">RepStash</span>
      </Link>
      <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: "w-10 h-10" } }} />
    </header>
  );
}
