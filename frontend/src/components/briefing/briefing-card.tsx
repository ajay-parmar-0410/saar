import type { BriefingItem } from "@/lib/types";
import { ImpactBadge } from "./impact-badge";
import { getSourceDisplay, formatTimeAgo } from "@/lib/source-utils";

interface BriefingCardProps {
  item: BriefingItem;
  featured?: boolean;
  generatedAt?: string;
}

export function BriefingCard({ item, featured = false, generatedAt }: BriefingCardProps) {
  const { label, dotColor } = getSourceDisplay(item.source);

  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`block rounded-xl border border-slate-100 bg-card transition-all hover:border-slate-200 hover:shadow-sm dark:border-slate-800 dark:hover:border-slate-700 ${
        featured ? "p-5" : "p-4"
      }`}
    >
      <ImpactBadge impact={item.impact} />

      <h3
        className={`mt-2 font-semibold leading-snug text-foreground ${
          featured ? "text-base" : "text-sm"
        }`}
      >
        {item.title}
      </h3>

      <p
        className={`mt-1 leading-relaxed text-muted-foreground ${
          featured ? "text-sm" : "text-xs"
        }`}
      >
        {item.summary}
      </p>

      <div className="mt-3 flex items-center gap-1.5 text-[11px] text-muted-foreground/70">
        <span className={`inline-block h-2 w-2 rounded-full ${dotColor}`} />
        <span className="font-semibold text-muted-foreground">{label}</span>
        {generatedAt && (
          <>
            <span>&bull;</span>
            <span>{formatTimeAgo(generatedAt)}</span>
          </>
        )}
      </div>
    </a>
  );
}
