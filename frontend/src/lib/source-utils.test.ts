import { describe, it, expect } from "vitest";
import { getSourceDisplay, formatTimeAgo } from "./source-utils";

describe("getSourceDisplay", () => {
  it("returns correct label and color for known sources", () => {
    expect(getSourceDisplay("hackernews")).toEqual({
      label: "Hacker News",
      dotColor: "bg-orange-500",
    });
    expect(getSourceDisplay("reddit")).toEqual({
      label: "Reddit",
      dotColor: "bg-red-500",
    });
    expect(getSourceDisplay("github")).toEqual({
      label: "GitHub",
      dotColor: "bg-purple-600",
    });
    expect(getSourceDisplay("arxiv")).toEqual({
      label: "arXiv",
      dotColor: "bg-red-800",
    });
    expect(getSourceDisplay("yahoo_finance")).toEqual({
      label: "Yahoo Finance",
      dotColor: "bg-purple-700",
    });
    expect(getSourceDisplay("economic_times")).toEqual({
      label: "Economic Times",
      dotColor: "bg-blue-700",
    });
    expect(getSourceDisplay("google_news")).toEqual({
      label: "Google News",
      dotColor: "bg-blue-500",
    });
    expect(getSourceDisplay("weatherapi")).toEqual({
      label: "Weather",
      dotColor: "bg-sky-500",
    });
  });

  it("returns capitalized fallback for unknown sources", () => {
    const result = getSourceDisplay("some_unknown_source");
    expect(result.label).toBe("Some Unknown Source");
    expect(result.dotColor).toBe("bg-slate-400");
  });

  it("handles single-word unknown source", () => {
    const result = getSourceDisplay("custom");
    expect(result.label).toBe("Custom");
    expect(result.dotColor).toBe("bg-slate-400");
  });
});

describe("formatTimeAgo", () => {
  it("returns 'just now' for very recent times", () => {
    const now = new Date().toISOString();
    expect(formatTimeAgo(now)).toBe("just now");
  });

  it("returns minutes for times less than 1 hour ago", () => {
    const date = new Date(Date.now() - 15 * 60_000).toISOString();
    expect(formatTimeAgo(date)).toBe("15m ago");
  });

  it("returns hours for times less than 24 hours ago", () => {
    const date = new Date(Date.now() - 3 * 3600_000).toISOString();
    expect(formatTimeAgo(date)).toBe("3h ago");
  });

  it("returns days for times less than 30 days ago", () => {
    const date = new Date(Date.now() - 5 * 86400_000).toISOString();
    expect(formatTimeAgo(date)).toBe("5d ago");
  });

  it("returns months for older times", () => {
    const date = new Date(Date.now() - 60 * 86400_000).toISOString();
    expect(formatTimeAgo(date)).toBe("2mo ago");
  });

  it("returns 'just now' for future dates", () => {
    const date = new Date(Date.now() + 3600_000).toISOString();
    expect(formatTimeAgo(date)).toBe("just now");
  });
});
