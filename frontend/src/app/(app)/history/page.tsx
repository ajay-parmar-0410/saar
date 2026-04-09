"use client";

import { useState, useCallback, useEffect } from "react";
import { useApi } from "@/hooks/use-api";
import { useAuth } from "@/context/auth-context";
import { apiFetch } from "@/lib/api";
import type { Briefing, BriefingItem } from "@/lib/types";
import { BriefingCard } from "@/components/briefing/briefing-card";
import { TopStoryCard } from "@/components/briefing/top-story-card";
import { Clock, ChevronDown, Loader2, Inbox } from "lucide-react";

interface BriefingSummaryItem {
  id: string;
  top_story: string;
  item_count: number;
  alert_count: number;
  read: boolean;
  generated_at: string | null;
}

interface BriefingListResponse {
  briefings: BriefingSummaryItem[];
  total: number;
  limit: number;
  offset: number;
}

export default function HistoryPage() {
  const { session } = useAuth();
  const [page, setPage] = useState(1);
  const [allItems, setAllItems] = useState<BriefingSummaryItem[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedBriefing, setExpandedBriefing] = useState<Briefing | null>(
    null
  );
  const [loadingDetail, setLoadingDetail] = useState(false);

  const { data: initialData, loading, error } = useApi<BriefingListResponse>(
    "/api/v1/briefings?limit=10&offset=0"
  );

  useEffect(() => {
    if (initialData?.briefings && allItems.length === 0) {
      setAllItems(initialData.briefings);
      if (initialData.briefings.length < 10) setHasMore(false);
    }
  }, [initialData, allItems.length]);

  const loadMore = useCallback(async () => {
    if (!session?.access_token || loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const data = await apiFetch<BriefingListResponse>(
        `/api/v1/briefings?limit=10&offset=${page * 10}`,
        { token: session.access_token }
      );
      setAllItems((prev) => [...prev, ...data.briefings]);
      setPage((prev) => prev + 1);
      if (data.briefings.length < 10) setHasMore(false);
    } catch {
      // Silently fail load more
    } finally {
      setLoadingMore(false);
    }
  }, [session?.access_token, page, loadingMore, hasMore]);

  const toggleExpand = useCallback(
    async (id: string) => {
      if (expandedId === id) {
        setExpandedId(null);
        setExpandedBriefing(null);
        return;
      }

      if (!session?.access_token) return;
      setExpandedId(id);
      setLoadingDetail(true);
      try {
        const data = await apiFetch<Briefing>(`/api/v1/briefings/${id}`, {
          token: session.access_token,
        });
        setExpandedBriefing(data);
      } catch {
        setExpandedBriefing(null);
      } finally {
        setLoadingDetail(false);
      }
    },
    [expandedId, session?.access_token]
  );

  if (loading && allItems.length === 0) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center text-sm text-destructive">{error}</div>
    );
  }

  if (allItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <Inbox className="mb-3 size-10 text-muted-foreground/50" />
        <h2 className="text-lg font-semibold">No briefings yet</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Your briefing history will appear here once your first briefing is
          generated.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-lg font-bold">Briefing History</h1>

      <div className="space-y-3">
        {allItems.map((item) => {
          const date = item.generated_at ? new Date(item.generated_at) : new Date();
          const isExpanded = expandedId === item.id;

          return (
            <div key={item.id}>
              <button
                onClick={() => toggleExpand(item.id)}
                className="w-full rounded-lg border border-border bg-card p-4 text-left transition-colors hover:bg-accent/50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Clock className="size-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-semibold">
                        {date.toLocaleDateString("en-IN", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        })}
                      </div>
                      {item.top_story && (
                        <div className="mt-0.5 text-xs text-muted-foreground line-clamp-1">
                          {item.top_story}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right text-xs text-muted-foreground">
                      <div>{item.item_count} items</div>
                      {item.alert_count > 0 && (
                        <div className="text-destructive">
                          {item.alert_count} alerts
                        </div>
                      )}
                    </div>
                    <ChevronDown
                      className={`size-4 text-muted-foreground transition-transform ${
                        isExpanded ? "rotate-180" : ""
                      }`}
                    />
                  </div>
                </div>
              </button>

              {isExpanded && (
                <div className="mt-2 space-y-2 pl-2">
                  {loadingDetail ? (
                    <div className="flex justify-center py-4">
                      <Loader2 className="size-5 animate-spin text-muted-foreground" />
                    </div>
                  ) : expandedBriefing ? (
                    <>
                      {expandedBriefing.top_story && typeof expandedBriefing.top_story === "string" && (
                        <TopStoryCard
                          topStory={expandedBriefing.top_story}
                          generatedAt={expandedBriefing.created_at}
                        />
                      )}
                      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                      {expandedBriefing.sections.map((section: any) => {
                        const sectionTitle = (section.title || section.name || section.key || "Section") as string;
                        const items = (section.items || []) as BriefingItem[];
                        return (
                          <div key={sectionTitle}>
                            <h3 className="mb-2 mt-3 text-sm font-bold text-muted-foreground">{sectionTitle}</h3>
                            {items.map((si) => (
                              <div key={si.title} className="mb-2">
                                <BriefingCard item={si} generatedAt={expandedBriefing.created_at} />
                              </div>
                            ))}
                          </div>
                        );
                      })}
                    </>
                  ) : (
                    <p className="py-4 text-center text-sm text-muted-foreground">
                      Could not load briefing details.
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {hasMore && (
        <div className="mt-6 text-center">
          <button
            onClick={loadMore}
            disabled={loadingMore}
            className="text-sm font-medium text-primary hover:underline disabled:opacity-50"
          >
            {loadingMore ? "Loading..." : "Load more"}
          </button>
        </div>
      )}
    </div>
  );
}
