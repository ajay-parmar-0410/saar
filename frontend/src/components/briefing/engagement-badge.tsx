import { Star, ArrowUp, Download, Heart, ThermometerSun, TrendingUp, TrendingDown } from "lucide-react";
import type { EngagementData } from "@/lib/types";

interface EngagementBadgeProps {
  engagement: EngagementData | null | undefined;
  source: string;
}

function formatCompact(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return String(value);
}

export function EngagementBadge({ engagement, source }: EngagementBadgeProps) {
  if (!engagement) return null;

  const { type } = engagement;

  if (type === "stars" && engagement.value != null) {
    return (
      <Badge icon={<Star className="h-3 w-3 fill-amber-500 text-amber-500" />}>
        {formatCompact(engagement.value)}
      </Badge>
    );
  }

  if (type === "points" && engagement.value != null) {
    return (
      <Badge icon={<ArrowUp className="h-3 w-3 text-orange-500" />}>
        {formatCompact(engagement.value)} pts
      </Badge>
    );
  }

  if (type === "upvotes" && engagement.value != null) {
    return (
      <Badge icon={<ArrowUp className="h-3 w-3 text-red-500" />}>
        {formatCompact(engagement.value)}
      </Badge>
    );
  }

  if (type === "model") {
    return (
      <div className="flex items-center gap-1.5">
        {engagement.downloads != null && (
          <Badge icon={<Download className="h-3 w-3 text-yellow-600" />}>
            {formatCompact(engagement.downloads)}
          </Badge>
        )}
        {engagement.likes != null && (
          <Badge icon={<Heart className="h-3 w-3 fill-red-400 text-red-400" />}>
            {formatCompact(engagement.likes)}
          </Badge>
        )}
      </div>
    );
  }

  if (type === "price_change" && engagement.value != null) {
    const isPositive = engagement.value >= 0;
    const Icon = isPositive ? TrendingUp : TrendingDown;
    const colorClass = isPositive
      ? "text-green-600 bg-green-50 dark:bg-green-500/20 dark:text-green-400"
      : "text-red-600 bg-red-50 dark:bg-red-500/20 dark:text-red-400";

    return (
      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${colorClass}`}>
        <Icon className="h-3 w-3" />
        {isPositive ? "+" : ""}{engagement.value.toFixed(2)}%
      </span>
    );
  }

  if (type === "temperature" && engagement.value != null) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-sky-50 px-2 py-0.5 text-[10px] font-semibold text-sky-600 dark:bg-sky-500/20 dark:text-sky-400">
        <ThermometerSun className="h-3 w-3" />
        {engagement.value}°C
      </span>
    );
  }

  return null;
}

function Badge({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
      {icon}
      {children}
    </span>
  );
}
