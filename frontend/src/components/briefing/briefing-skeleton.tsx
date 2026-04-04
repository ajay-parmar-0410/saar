export function BriefingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {/* Top story skeleton */}
      <div className="rounded-lg border border-border bg-card p-5">
        <div className="flex items-start gap-3">
          <div className="h-4 w-10 rounded bg-muted" />
          <div className="flex-1 space-y-2">
            <div className="h-5 w-3/4 rounded bg-muted" />
            <div className="h-3 w-full rounded bg-muted" />
            <div className="h-3 w-2/3 rounded bg-muted" />
          </div>
        </div>
      </div>

      {/* Section skeletons */}
      {[1, 2].map((i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 w-32 rounded bg-muted" />
          {[1, 2, 3].map((j) => (
            <div
              key={j}
              className="rounded-lg border border-border bg-card p-4"
            >
              <div className="flex items-start gap-3">
                <div className="h-4 w-10 rounded bg-muted" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-5/6 rounded bg-muted" />
                  <div className="h-3 w-full rounded bg-muted" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
