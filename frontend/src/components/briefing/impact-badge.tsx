interface ImpactBadgeProps {
  impact: "HIGH" | "MEDIUM" | "LOW";
}

const STYLES: Record<string, string> = {
  HIGH: "bg-red-50 text-red-600 dark:bg-red-500/20 dark:text-red-400",
  MEDIUM: "bg-amber-50 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400",
  LOW: "bg-green-50 text-green-600 dark:bg-green-500/20 dark:text-green-400",
};

export function ImpactBadge({ impact }: ImpactBadgeProps) {
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wider ${STYLES[impact] ?? STYLES.LOW}`}
    >
      {impact}
    </span>
  );
}
