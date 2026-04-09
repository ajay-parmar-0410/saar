export function BriefingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {/* Hero card skeleton */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 p-6">
        <div className="h-4 w-20 rounded bg-slate-700" />
        <div className="mt-3 h-5 w-4/5 rounded bg-slate-700" />
        <div className="mt-2 h-4 w-full rounded bg-slate-700" />
        <div className="mt-2 h-4 w-2/3 rounded bg-slate-700" />
      </div>

      {/* Section skeletons */}
      {[1, 2].map((i) => (
        <div key={i} className="space-y-2">
          <div className="h-5 w-32 rounded bg-muted" />
          {[1, 2, 3].map((j) => (
            <div
              key={j}
              className="rounded-xl border border-slate-100 bg-card p-4 dark:border-slate-800"
            >
              <div className="h-3 w-12 rounded bg-muted" />
              <div className="mt-2 h-4 w-5/6 rounded bg-muted" />
              <div className="mt-1 h-3 w-full rounded bg-muted" />
              <div className="mt-3 flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-muted" />
                <div className="h-3 w-20 rounded bg-muted" />
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
