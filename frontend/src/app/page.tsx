"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { Newspaper, Zap, MessageCircle } from "lucide-react";
import { useEffect } from "react";

const FEATURES = [
  {
    icon: Newspaper,
    title: "Personalized Briefings",
    description: "AI-curated news from 16+ sources, filtered to your interests.",
  },
  {
    icon: Zap,
    title: "Noise-Free",
    description: "Deduplication and relevance scoring — only what matters.",
  },
  {
    icon: MessageCircle,
    title: "Ask Follow-ups",
    description: "Chat with your briefing and get answers with sources.",
  },
] as const;

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.replace("/briefing");
    }
  }, [user, loading, router]);

  if (loading || user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-900">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-900 text-white">
      {/* Hero section */}
      <section className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-6 py-24 text-center">
        {/* Decorative gradient orbs */}
        <div className="absolute left-1/2 top-1/4 h-64 w-64 -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-48 w-48 rounded-full bg-primary/5 blur-3xl" />

        <h1 className="relative text-5xl font-extrabold tracking-tight sm:text-6xl">
          Saar
        </h1>
        <p className="relative mt-4 max-w-sm text-lg text-slate-400">
          Your daily briefing, distilled to what matters.
        </p>

        <Link
          href="/login"
          className="relative mt-10 inline-flex h-12 items-center rounded-xl bg-primary px-8 text-base font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Get Started
        </Link>
      </section>

      {/* Features */}
      <section className="border-t border-slate-800 bg-slate-900/80 px-6 py-16">
        <div className="mx-auto grid max-w-lg gap-8 sm:max-w-3xl sm:grid-cols-3">
          {FEATURES.map((feat) => {
            const Icon = feat.icon;
            return (
              <div key={feat.title} className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary">
                  <Icon className="size-6" />
                </div>
                <h3 className="mt-4 text-sm font-semibold text-white">
                  {feat.title}
                </h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">
                  {feat.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="border-t border-slate-800 px-6 py-8 text-center">
        <p className="text-sm text-slate-500">
          Pick your interests. Get your briefing. Stay informed.
        </p>
      </section>
    </div>
  );
}
