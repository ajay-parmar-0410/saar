import { getSourceDisplay, formatTimeAgo } from "@/lib/source-utils";

interface TopStoryCardProps {
  topStory: string;
  generatedAt?: string;
}

/**
 * Parse backend top_story string format: "title: extended_summary"
 * Falls back to using full string as title if no colon-space separator found.
 */
function parseTopStory(raw: string): { title: string; summary: string } {
  const separatorIndex = raw.indexOf(": ");
  if (separatorIndex === -1 || separatorIndex > 120) {
    return { title: raw, summary: "" };
  }
  return {
    title: raw.slice(0, separatorIndex),
    summary: raw.slice(separatorIndex + 2),
  };
}

export function TopStoryCard({ topStory, generatedAt }: TopStoryCardProps) {
  if (!topStory) return null;

  const { title, summary } = parseTopStory(topStory);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-6 text-white dark:from-slate-700 dark:to-slate-800">
      {/* Decorative circle */}
      <div className="absolute -right-5 -top-5 h-28 w-28 rounded-full bg-primary/15" />

      <span className="inline-block rounded-md bg-red-500/20 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-red-300">
        Top Story
      </span>

      <h2 className="mt-3 text-lg font-bold leading-snug">{title}</h2>

      {summary && (
        <p className="mt-2 text-sm leading-relaxed text-slate-400">{summary}</p>
      )}

      {generatedAt && (
        <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
          <span>{formatTimeAgo(generatedAt)}</span>
        </div>
      )}
    </div>
  );
}

export { parseTopStory };
