"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { useApi, useApiMutation } from "@/hooks/use-api";
import type { Briefing, BriefingItem } from "@/lib/types";
import { BriefingCard } from "@/components/briefing/briefing-card";
import { BriefingSkeleton } from "@/components/briefing/briefing-skeleton";
import { TopStoryCard } from "@/components/briefing/top-story-card";
import { SectionPills } from "@/components/briefing/section-pills";
import { RefreshCw, Sparkles, Sun } from "lucide-react";
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
  const [activeSection, setActiveSection] = useState("All");
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

  // Build section names for pills
  const sectionNames = useMemo(() => {
    if (!briefing?.sections) return ["All"];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const names = briefing.sections.map((s: any) =>
      (s.title || s.name || s.key || "Section") as string
    );
    return ["All", ...names];
  }, [briefing?.sections]);

  // Filter sections based on active pill
  const filteredSections = useMemo(() => {
    if (!briefing?.sections) return [];
    if (activeSection === "All") return briefing.sections;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return briefing.sections.filter((s: any) => {
      const name = (s.title || s.name || s.key || "Section") as string;
      return name === activeSection;
    });
  }, [briefing?.sections, activeSection]);

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  // Briefing generated timestamp
  const generatedAt = briefing?.created_at ?? undefined;

  if (loading && !refreshing) {
    return (
      <div>
        <div className="mb-4">
          <div className="flex gap-2">
            {["All", "Loading..."].map((p) => (
              <div key={p} className="h-9 w-20 animate-pulse rounded-full bg-muted" />
            ))}
          </div>
        </div>
        <p className="mb-4 text-xs text-muted-foreground">{today}</p>
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
          <Sun className="size-7 text-muted-foreground" />
        </div>
        <h2 className="text-lg font-semibold">No briefing yet</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Generate your first briefing now, or wait for your scheduled time.
        </p>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="mt-6 rounded-xl bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {generating ? "Generating..." : "Generate Now"}
        </button>
      </div>
    );
  }

  return (
    <div onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
      {/* Section filter pills */}
      <div className="mb-3">
        <SectionPills
          sections={sectionNames}
          activeSection={activeSection}
          onSelect={setActiveSection}
        />
      </div>

      {/* Date + generate + refresh */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{today}</p>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            <Sparkles className={`size-3.5 ${generating ? "animate-spin" : ""}`} />
            {generating ? "Generating..." : "Generate"}
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted"
          >
            <RefreshCw
              className={`size-3.5 ${refreshing ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      </div>

      {/* Top Story */}
      {activeSection === "All" && briefing.top_story && (
        <div className="mb-6">
          {typeof briefing.top_story === "string" ? (
            <TopStoryCard topStory={briefing.top_story} generatedAt={generatedAt} />
          ) : (
            <BriefingCard item={briefing.top_story} featured generatedAt={generatedAt} />
          )}
        </div>
      )}

      {/* Sections */}
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {filteredSections.map((section: any) => {
        const sectionName = (section.title || section.name || section.key || "Section") as string;
        const items = (section.items || []) as BriefingItem[];
        return (
          <div key={sectionName} className="mb-6">
            <h2 className="mb-3 text-base font-bold">{sectionName}</h2>
            <div className="space-y-2">
              {items.map((item) => (
                <BriefingCard key={item.title} item={item} generatedAt={generatedAt} />
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
