"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import { apiFetch } from "@/lib/api";

interface StarterPackStepProps {
  userTypes: string[];
  topics: string[];
  sources: string[];
  onUpdate: (topics: string[], sources: string[]) => void;
  onNext: () => void;
  onBack: () => void;
}

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
  const { session } = useAuth();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (topics.length > 0 && sources.length > 0) return;

    const fetchPack = async () => {
      if (!session?.access_token) return;
      setLoading(true);
      try {
        const data = await apiFetch<{ topics: string[]; sources: string[] }>(
          `/api/v1/onboarding/starter-pack?user_types=${userTypes.join(",")}`,
          { token: session.access_token }
        );
        onUpdate(data.topics, data.sources);
      } catch {
        // Fallback — will use empty arrays
      } finally {
        setLoading(false);
      }
    };
    fetchPack();
  }, [userTypes.join(",")]); // eslint-disable-line react-hooks/exhaustive-deps

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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Your Starter Pack</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Toggle topics and sources on or off.
        </p>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Topics
        </h3>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <button
              key={topic}
              onClick={() => toggleTopic(topic)}
              className="rounded-full border border-primary bg-primary/10 px-3 py-1 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
            >
              {formatLabel(topic)} ×
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Sources
        </h3>
        <div className="flex flex-wrap gap-2">
          {sources.map((source) => (
            <button
              key={source}
              onClick={() => toggleSource(source)}
              className="rounded-full border border-primary bg-primary/10 px-3 py-1 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
            >
              {formatLabel(source)} ×
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={onBack}>
          Back
        </Button>
        <Button
          className="flex-1"
          onClick={onNext}
          disabled={topics.length === 0 && sources.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
