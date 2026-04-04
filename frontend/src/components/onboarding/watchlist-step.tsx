"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface WatchlistItem {
  type: string;
  value: string;
}

interface WatchlistStepProps {
  items: WatchlistItem[];
  onUpdate: (items: WatchlistItem[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const INTEREST_TYPES = [
  { id: "stock", label: "Stock", placeholder: "e.g. RELIANCE, TCS, INFY" },
  { id: "repo", label: "GitHub Repo", placeholder: "e.g. langchain-ai/langchain" },
  { id: "subreddit", label: "Subreddit", placeholder: "e.g. r/LocalLLaMA" },
  { id: "keyword", label: "Keyword", placeholder: "e.g. GPT-5, quantum computing" },
] as const;

export function WatchlistStep({
  items,
  onUpdate,
  onNext,
  onBack,
}: WatchlistStepProps) {
  const [activeType, setActiveType] = useState("stock");
  const [inputValue, setInputValue] = useState("");

  const addItem = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    const exists = items.some(
      (i) => i.type === activeType && i.value.toLowerCase() === trimmed.toLowerCase()
    );
    if (exists) return;
    onUpdate([...items, { type: activeType, value: trimmed }]);
    setInputValue("");
  };

  const removeItem = (index: number) => {
    onUpdate(items.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addItem();
    }
  };

  const activePlaceholder =
    INTEREST_TYPES.find((t) => t.id === activeType)?.placeholder || "";

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Your Watchlist</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Add specific items to track. You can skip this.
        </p>
      </div>

      <div className="flex gap-2 overflow-x-auto">
        {INTEREST_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setActiveType(type.id)}
            className={`whitespace-nowrap rounded-full px-3 py-1 text-sm font-medium transition-colors ${
              activeType === type.id
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={activePlaceholder}
          className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <Button onClick={addItem} disabled={!inputValue.trim()}>
          Add
        </Button>
      </div>

      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((item, index) => (
            <div
              key={`${item.type}-${item.value}`}
              className="flex items-center justify-between rounded-md border border-border px-3 py-2"
            >
              <div>
                <span className="text-xs font-medium uppercase text-muted-foreground">
                  {item.type}
                </span>
                <span className="ml-2 text-sm">{item.value}</span>
              </div>
              <button
                onClick={() => removeItem(index)}
                className="text-sm text-muted-foreground hover:text-destructive"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={onBack}>
          Back
        </Button>
        <Button className="flex-1" onClick={onNext}>
          {items.length === 0 ? "Skip" : "Continue"}
        </Button>
      </div>
    </div>
  );
}
