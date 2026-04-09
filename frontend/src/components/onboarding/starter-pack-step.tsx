"use client";

import { Button } from "@/components/ui/button";

interface StarterPackStepProps {
  userTypes: string[];
  topics: string[];
  sources: string[];
  onUpdate: (topics: string[], sources: string[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const ALL_TOPICS = [
  "ai_ml",
  "web_dev",
  "mobile",
  "devops",
  "security",
  "data_science",
  "blockchain",
  "cloud",
  "startups",
  "finance",
  "markets",
  "economy",
  "world_news",
  "india",
  "science",
  "health",
];

const ALL_SOURCES = [
  "hackernews",
  "reddit",
  "github",
  "arxiv",
  "producthunt",
  "newsapi",
  "google_news",
  "yahoo_finance",
  "economic_times",
  "weatherapi",
];

function formatLabel(id: string): string {
  return id
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function StarterPackStep({
  userTypes,
  topics,
  sources,
  onUpdate,
  onNext,
  onBack,
}: StarterPackStepProps) {
  // No pre-selection — user picks their own topics and sources from scratch

  const toggleTopic = (topic: string) => {
    const updated = topics.includes(topic)
      ? topics.filter((t) => t !== topic)
      : [...topics, topic];
    onUpdate(updated, sources);
  };

  const toggleSource = (source: string) => {
    const updated = sources.includes(source)
      ? sources.filter((s) => s !== source)
      : [...sources, source];
    onUpdate(topics, updated);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Your Starter Pack</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Pick topics and sources for your briefing.
        </p>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Topics
        </h3>
        <div className="flex flex-wrap gap-2">
          {ALL_TOPICS.map((topic) => {
            const isActive = topics.includes(topic);
            return (
              <button
                key={topic}
                onClick={() => toggleTopic(topic)}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {formatLabel(topic)}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Sources
        </h3>
        <div className="flex flex-wrap gap-2">
          {ALL_SOURCES.map((source) => {
            const isActive = sources.includes(source);
            return (
              <button
                key={source}
                onClick={() => toggleSource(source)}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {formatLabel(source)}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={onBack}>
          Back
        </Button>
        <Button
          className="flex-1"
          onClick={onNext}
          disabled={topics.length === 0 || sources.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
