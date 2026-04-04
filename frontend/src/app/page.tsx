"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Newspaper, MessageCircle, Zap } from "lucide-react";
import { useEffect } from "react";

const VALUE_PROPS = [
  {
    icon: Newspaper,
    title: "Personalized Briefings",
    description:
      "AI-curated news from 12+ sources, filtered to match your interests and delivered on your schedule.",
  },
  {
    icon: Zap,
    title: "Noise-Free",
    description:
      "Deduplication, relevance scoring, and quality filters ensure you only see what matters.",
  },
  {
    icon: MessageCircle,
    title: "Ask Follow-ups",
    description:
      "Chat with your briefing. Ask deeper questions and get answers with source citations.",
  },
] as const;

const SAMPLE_ITEMS = [
  {
    impact: "HIGH",
    title: "Meta releases Llama 4 Scout — open-weight MoE model",
    summary:
      "Meta AI open-sourced Llama 4 Scout, a 109B-parameter mixture-of-experts model outperforming GPT-4o on several benchmarks.",
    source: "Hacker News",
  },
  {
    impact: "HIGH",
    title: "RBI holds repo rate at 6.5% for eighth straight meeting",
    summary:
      "The Reserve Bank of India maintained the benchmark rate, citing persistent food inflation despite improving growth outlook.",
    source: "Economic Times",
  },
  {
    impact: "MEDIUM",
    title: "GitHub Copilot now supports multi-file editing",
    summary:
      "Copilot Workspace enters GA, enabling developers to plan and implement changes across multiple files from a single prompt.",
    source: "GitHub Blog",
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
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Hero */}
      <section className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Saar
        </h1>
        <p className="mt-3 text-lg text-muted-foreground sm:text-xl">
          Your daily briefing, distilled to what matters.
        </p>
        <Link href="/login" className="mt-8">
          <Button size="lg" className="h-12 px-8 text-base">
            Get Started
          </Button>
        </Link>
      </section>

      {/* Value Props */}
      <section className="border-t border-border bg-muted/30 px-4 py-16">
        <div className="mx-auto grid max-w-lg gap-8 sm:max-w-3xl sm:grid-cols-3">
          {VALUE_PROPS.map((prop) => {
            const Icon = prop.icon;
            return (
              <div key={prop.title} className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="size-6" />
                </div>
                <h3 className="mt-4 text-base font-semibold">{prop.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  {prop.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Sample Briefing Preview */}
      <section className="px-4 py-16">
        <div className="mx-auto max-w-lg">
          <h2 className="mb-6 text-center text-2xl font-bold">
            Sample Briefing
          </h2>
          <div className="space-y-3">
            {SAMPLE_ITEMS.map((item) => (
              <div
                key={item.title}
                className="rounded-lg border border-border bg-card p-4"
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 inline-block rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                      item.impact === "HIGH"
                        ? "bg-destructive/15 text-destructive"
                        : "bg-yellow-500/15 text-yellow-600 dark:text-yellow-400"
                    }`}
                  >
                    {item.impact}
                  </span>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold leading-snug">
                      {item.title}
                    </h4>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {item.summary}
                    </p>
                    <p className="mt-2 text-[10px] font-medium text-muted-foreground/70">
                      {item.source}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="border-t border-border px-4 py-8 text-center">
        <p className="text-sm text-muted-foreground">
          Pick your interests. Get your briefing. Stay informed.
        </p>
        <Link href="/login" className="mt-4 inline-block">
          <Button>Get Started</Button>
        </Link>
      </section>
    </div>
  );
}
