import type { BriefingItem } from "@/lib/types";
import { ImpactBadge } from "./impact-badge";
import { ExternalLink } from "lucide-react";

interface BriefingCardProps {
  item: BriefingItem;
  featured?: boolean;
}

export function BriefingCard({ item, featured = false }: BriefingCardProps) {
  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`block rounded-lg border border-border bg-card transition-colors hover:bg-accent/50 ${
        featured ? "p-5" : "p-4"
      }`}
    >
      <div className="flex items-start gap-3">
        <ImpactBadge impact={item.impact} />
        <div className="flex-1 min-w-0">
          <h3
            className={`font-semibold leading-snug ${
              featured ? "text-base" : "text-sm"
            }`}
          >
            {item.title}
          </h3>
          <p
            className={`mt-1 text-muted-foreground ${
              featured ? "text-sm" : "text-xs"
            }`}
          >
            {item.summary}
          </p>
          <div className="mt-2 flex items-center gap-2 text-[10px] font-medium text-muted-foreground/70">
            <span>{item.source}</span>
            <ExternalLink className="size-3" />
          </div>
        </div>
      </div>
    </a>
  );
}
