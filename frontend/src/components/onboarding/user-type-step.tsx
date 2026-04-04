"use client";

import { Button } from "@/components/ui/button";

const USER_TYPES = [
  {
    id: "ai_tech",
    title: "AI / Tech",
    description: "AI breakthroughs, trending repos, dev tools, research papers",
  },
  {
    id: "general",
    title: "General",
    description: "Top headlines, weather, trending topics, quick catch-up",
  },
  {
    id: "trader",
    title: "Stock Trader",
    description: "Indian markets, Nifty/Sensex, watchlist, market news",
  },
] as const;

interface UserTypeStepProps {
  selected: string[];
  onSelect: (types: string[]) => void;
  onNext: () => void;
}

export function UserTypeStep({ selected, onSelect, onNext }: UserTypeStepProps) {
  const toggle = (id: string) => {
    const updated = selected.includes(id)
      ? selected.filter((t) => t !== id)
      : [...selected, id];
    onSelect(updated);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">What describes you best?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Pick one or more. We&apos;ll tailor your briefing.
        </p>
      </div>

      <div className="grid gap-3">
        {USER_TYPES.map((type) => {
          const isSelected = selected.includes(type.id);
          return (
            <button
              key={type.id}
              onClick={() => toggle(type.id)}
              className={`rounded-lg border-2 p-4 text-left transition-colors ${
                isSelected
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50"
              }`}
            >
              <div className="font-semibold">{type.title}</div>
              <div className="mt-1 text-sm text-muted-foreground">
                {type.description}
              </div>
            </button>
          );
        })}
      </div>

      <Button
        className="w-full"
        onClick={onNext}
        disabled={selected.length === 0}
      >
        Continue
      </Button>
    </div>
  );
}
