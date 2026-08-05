"use client";

import { motion } from "framer-motion";
import { SignInButton, UserButton, useAuth } from "@clerk/nextjs";
import { ArrowRight, Link as LinkIcon, Dumbbell, Zap } from "lucide-react";
import Link from "next/link";
import { Button } from "@/shared/ui/button";

export default function Home() {
  const { isSignedIn } = useAuth();

  return (
    <div className="flex flex-col min-h-screen bg-surface-background overflow-hidden relative">
      {/* Decorative background glow */}
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-amber/20 rounded-full blur-[120px] pointer-events-none" />

      <header className="w-full flex items-center justify-between p-6 max-w-7xl mx-auto relative z-10">
        <div className="flex items-center gap-2 text-text-primary">
          <Dumbbell className="w-6 h-6 text-brand-amber" />
          <span className="font-bold text-xl tracking-tight">RepStash</span>
        </div>
        <nav className="flex items-center gap-4">
          {!isSignedIn ? (
            <>
              <SignInButton mode="modal">
                <Button variant="ghost" size="none" className="text-sm font-medium text-text-muted hover:text-text-primary">
                  Sign In
                </Button>
              </SignInButton>
              <SignInButton mode="modal">
                <Button variant="outline" size="sm" className="bg-surface-card hover:border-brand-amber/50">
                  Get Started
                </Button>
              </SignInButton>
            </>
          ) : (
            <>
              <Link 
                href="/dashboard"
                className="text-sm font-semibold bg-brand-amber text-white px-5 py-2 rounded-full hover:bg-brand-hover transition-colors"
              >
                Go to Dashboard
              </Link>
              <UserButton />
            </>
          )}
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center z-10 relative mt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-muted border border-brand-amber/20 text-brand-amber text-sm font-medium mb-8"
        >
          <Zap className="w-4 h-4" />
          <span>Powered by Gemini 2.5 Flash</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="text-5xl sm:text-7xl font-extrabold tracking-tight text-text-primary max-w-4xl leading-tight"
        >
          Paste a link. <br />
          <span className="text-brand-amber">Get a structured workout.</span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          className="mt-6 text-lg sm:text-xl text-text-muted max-w-2xl"
        >
          RepStash is your personal &quot;Paprika for Exercise Moves&quot;. Drop an Instagram Reel, TikTok, or YouTube Short, and our AI instantly extracts the sets, reps, and form into a clean exercise card.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
          className="mt-10 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto"
        >
          {!isSignedIn ? (
            <SignInButton mode="modal">
              <Button variant="primary" size="xl" className="w-full sm:w-auto group hover:scale-105 active:scale-95 shadow-[0_0_40px_-10px_rgba(255,90,0,0.5)]">
                Start Stashing
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </SignInButton>
          ) : (
            <Link 
              href="/dashboard"
              className="w-full sm:w-auto group flex items-center justify-center gap-2 bg-brand-amber hover:bg-brand-hover text-white px-8 py-4 rounded-full font-semibold text-lg transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_-10px_rgba(255,90,0,0.5)]"
            >
              Open Dashboard
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          )}
          
          <div className="w-full sm:w-auto flex items-center gap-2 px-6 py-4 rounded-full bg-surface-card border border-surface-border text-text-muted">
            <LinkIcon className="w-5 h-5" />
            <span className="font-mono text-sm">https://instagram.com/reel/xyz</span>
          </div>
        </motion.div>
      </main>

      {/* Decorative Bottom gradient */}
      <div className="fixed bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-background to-transparent pointer-events-none" />
    </div>
  );
}
