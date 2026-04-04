interface ImpactBadgeProps {
  impact: "HIGH" | "MEDIUM" | "LOW";
}

const STYLES: Record<string, string> = {
  HIGH: "bg-destructive/15 text-destructive",
  MEDIUM: "bg-yellow-500/15 text-yellow-600 dark:text-yellow-400",
  LOW: "bg-muted text-muted-foreground",
};

export function ImpactBadge({ impact }: ImpactBadgeProps) {
  return (
    <span
      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${STYLES[impact] ?? STYLES.LOW}`}
    >
      {impact}
    </span>
  );
}
