"use client";

import { useCallback, useRef, useState } from "react";
import { useApi, useApiMutation } from "@/hooks/use-api";
import type { Briefing, BriefingItem } from "@/lib/types";
import { BriefingCard } from "@/components/briefing/briefing-card";
import { BriefingSkeleton } from "@/components/briefing/briefing-skeleton";
import { RefreshCw } from "lucide-react";
import Link from "next/link";

interface BriefingListResponse {
  briefings: { id: string }[];
  total: number;
}

export default function BriefingPage() {
  const { data: listData, loading: listLoading, error: listError, refetch: refetchList } = useApi<BriefingListResponse>(
    "/api/v1/briefings?limit=1"
  );

  const latestId = listData?.briefings?.[0]?.id ?? null;

  const { data: briefing, loading: detailLoading, error: detailError, refetch: refetchDetail } = useApi<Briefing>(
    `/api/v1/briefings/${latestId}`,
    { skip: !latestId }
  );

  const loading = listLoading || detailLoading;
  const error = listError || detailError;

  const [refreshing, setRefreshing] = useState(false);
  const touchStartY = useRef(0);
  const { mutate: generateBriefing, loading: generating } = useApiMutation<void, Briefing>(
    "/api/v1/briefings/generate",
    "POST"
  );

  const handleGenerate = useCallback(async () => {
    const result = await generateBriefing();
    if (result) {
      await refetchList();
    }
  }, [generateBriefing, refetchList]);

  const refetch = useCallback(async () => {
    await refetchList();
    if (latestId) await refetchDetail();
  }, [refetchList, refetchDetail, latestId]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  }, [refetch]);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  }, []);

  const handleTouchEnd = useCallback(
    (e: React.TouchEvent) => {
      const deltaY = e.changedTouches[0].clientY - touchStartY.current;
      if (deltaY > 80 && window.scrollY === 0) {
        handleRefresh();
      }
    },
    [handleRefresh]
  );

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  if (loading && !refreshing) {
    return (
      <div>
        <h1 className="mb-1 text-lg font-bold">Today&apos;s Briefing</h1>
        <p className="mb-6 text-xs text-muted-foreground">{today}</p>
        <BriefingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <p className="text-sm text-destructive">{error}</p>
        <button
          onClick={handleRefresh}
          className="mt-4 text-sm font-medium text-primary hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!briefing) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
          <RefreshCw className="size-7 text-muted-foreground" />
        </div>
        <h2 className="text-lg font-semibold">
          No briefing yet
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Generate your first briefing now, or wait for your scheduled time.
        </p>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="mt-4 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {generating ? "Generating..." : "Generate Now"}
        </button>
      </div>
    );
  }

  return (
    <div onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
      {/* Header */}
      <div className="mb-1 flex items-center justify-between">
        <h1 className="text-lg font-bold">Today&apos;s Briefing</h1>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="rounded-md p-2 text-muted-foreground hover:bg-muted"
        >
          <RefreshCw
            className={`size-4 ${refreshing ? "animate-spin" : ""}`}
          />
        </button>
      </div>
      <p className="mb-6 text-xs text-muted-foreground">{today}</p>

      {/* Top Story */}
      {briefing.top_story && typeof briefing.top_story === "string" && (
        <div className="mb-6">
          <h2 className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
            Top Story
          </h2>
          <div className="rounded-lg border border-border bg-card p-4">
            <p className="text-sm">{briefing.top_story}</p>
          </div>
        </div>
      )}
      {briefing.top_story && typeof briefing.top_story === "object" && (
        <div className="mb-6">
          <h2 className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
            Top Story
          </h2>
          <BriefingCard item={briefing.top_story} featured />
        </div>
      )}

      {/* Sections */}
      {briefing.sections.map((section: Record<string, unknown>) => {
        const sectionName = (section.title || section.name || section.key || "Section") as string;
        const items = (section.items || []) as BriefingItem[];
        return (
          <div key={sectionName} className="mb-6">
            <h2 className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
              {sectionName}
            </h2>
            <div className="space-y-2">
              {items.map((item) => (
                <BriefingCard key={item.title} item={item} />
              ))}
            </div>
          </div>
        );
      })}

      {/* Link to history */}
      <div className="border-t border-border pt-4 text-center">
        <Link
          href="/history"
          className="text-sm font-medium text-primary hover:underline"
        >
          View previous briefings
        </Link>
      </div>
    </div>
  );
}
