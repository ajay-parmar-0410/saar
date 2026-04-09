/** Source display info — maps raw backend source keys to friendly labels and dot colors. */

interface SourceDisplay {
  label: string;
  dotColor: string;
}

const SOURCE_MAP: Record<string, SourceDisplay> = {
  hackernews:      { label: "Hacker News",      dotColor: "bg-orange-500" },
  reddit:          { label: "Reddit",            dotColor: "bg-red-500" },
  reddit_trending: { label: "Reddit Trending",   dotColor: "bg-red-500" },
  reddit_finance:  { label: "Reddit Finance",    dotColor: "bg-red-500" },
  github:          { label: "GitHub",            dotColor: "bg-purple-600" },
  google_news:     { label: "Google News",       dotColor: "bg-blue-500" },
  arxiv:           { label: "arXiv",             dotColor: "bg-red-800" },
  producthunt:     { label: "Product Hunt",      dotColor: "bg-orange-600" },
  newsapi:         { label: "News",              dotColor: "bg-slate-500" },
  yahoo_finance:   { label: "Yahoo Finance",     dotColor: "bg-purple-700" },
  economic_times:  { label: "Economic Times",    dotColor: "bg-blue-700" },
  moneycontrol:    { label: "Moneycontrol",      dotColor: "bg-green-700" },
  techcrunch:      { label: "TechCrunch",        dotColor: "bg-green-600" },
  weatherapi:      { label: "Weather",           dotColor: "bg-sky-500" },
  huggingface:     { label: "Hugging Face",      dotColor: "bg-yellow-500" },
  exchangerate:    { label: "Exchange Rate",     dotColor: "bg-emerald-600" },
};

/** Returns display info for a source key. Unknown sources get a capitalized label and grey dot. */
export function getSourceDisplay(source: string): SourceDisplay {
  const entry = SOURCE_MAP[source];
  if (entry) return entry;

  const label = source
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
  return { label, dotColor: "bg-slate-400" };
}

/** Format an ISO timestamp as a relative time string (e.g., "2h ago", "3d ago"). */
export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  if (diffMs < 0) return "just now";

  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;

  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}
