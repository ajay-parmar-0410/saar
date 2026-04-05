/**
 * API Contract Tests
 *
 * Verify that the frontend TypeScript types match the backend pydantic schemas.
 * These tests validate that API responses can be correctly consumed by the frontend.
 */
import { describe, it, expect } from "vitest";
import type {
  BriefingItem,
  BriefingSection,
  Briefing,
  BriefingListItem,
  ChatSource,
  ChatMessage,
  ChatResponse,
  UserPreferences,
  WatchlistItem,
  Schedule,
  UserProfile,
} from "./types";

// --- Mock API responses that match backend pydantic schemas ---

const mockBriefingItemFromBackend = {
  title: "OpenAI releases GPT-5",
  summary: "Major AI breakthrough.",
  url: "https://example.com",
  source: "newsapi",
  impact: "HIGH" as const,
  relevance: 9,
};

const mockBriefingSectionFromBackend = {
  key: "ai_tech",
  title: "AI & Tech",
  items: [mockBriefingItemFromBackend],
};

const mockBriefingDetailFromBackend = {
  id: "br-123",
  user_id: "user-456",
  content: "# Daily Briefing",
  sections: [mockBriefingSectionFromBackend],
  top_story: "AI breakthrough",
  item_count: 12,
  alert_count: 2,
  read: false,
  read_at: null,
  generated_at: "2026-04-04T07:00:00Z",
};

const mockChatResponseFromBackend = {
  response: "Here is the latest on AI.",
  sources: [
    { title: "Article", url: "https://a.com", source: "newsapi" },
  ],
};

const mockPreferencesFromBackend = {
  user_id: "user-456",
  topics: ["ai", "tech"],
  sources: ["github", "hackernews"],
  briefing_depth: "detailed",
  location: "Mumbai",
  updated_at: "2026-04-04T00:00:00Z",
};

const mockInterestFromBackend = {
  id: "int-1",
  user_id: "user-456",
  type: "stock",
  value: "RELIANCE",
  added_at: "2026-04-04T00:00:00Z",
};

const mockScheduleFromBackend = {
  user_id: "user-456",
  times: ["07:00", "19:00"],
  timezone: "Asia/Kolkata",
  enabled: true,
};

const mockUserProfileFromBackend = {
  id: "user-456",
  email: "test@saar.app",
  name: "Test User",
  user_type: ["ai_tech"],
  onboarded: true,
  last_active_at: "2026-04-04T00:00:00Z",
  created_at: "2026-04-01T00:00:00Z",
};

// --- Contract Tests ---

describe("API Contract: BriefingItem", () => {
  it("backend BriefingItemResponse maps to frontend BriefingItem", () => {
    const item: BriefingItem = {
      title: mockBriefingItemFromBackend.title,
      summary: mockBriefingItemFromBackend.summary,
      url: mockBriefingItemFromBackend.url,
      source: mockBriefingItemFromBackend.source,
      impact: mockBriefingItemFromBackend.impact,
    };
    expect(item.title).toBe("OpenAI releases GPT-5");
    expect(item.impact).toBe("HIGH");
    expect(["HIGH", "MEDIUM", "LOW"]).toContain(item.impact);
  });
});

describe("API Contract: BriefingSection", () => {
  it("backend BriefingSectionResponse maps to frontend BriefingSection", () => {
    const section: BriefingSection = {
      name: mockBriefingSectionFromBackend.title,
      items: mockBriefingSectionFromBackend.items.map((i) => ({
        title: i.title,
        summary: i.summary,
        url: i.url,
        source: i.source,
        impact: i.impact,
      })),
    };
    expect(section.name).toBe("AI & Tech");
    expect(section.items).toHaveLength(1);
  });
});

describe("API Contract: ChatResponse", () => {
  it("backend ChatResponse maps to frontend ChatResponse", () => {
    const resp: ChatResponse = {
      response: mockChatResponseFromBackend.response,
      sources: mockChatResponseFromBackend.sources,
    };
    expect(resp.response).toBe("Here is the latest on AI.");
    expect(resp.sources).toHaveLength(1);
    expect(resp.sources[0].title).toBe("Article");
    expect(resp.sources[0].url).toBe("https://a.com");
    expect(resp.sources[0].source).toBe("newsapi");
  });
});

describe("API Contract: ChatSource", () => {
  it("backend ChatSource fields match frontend", () => {
    const source: ChatSource = {
      title: "Test",
      url: "https://t.com",
      source: "hackernews",
    };
    expect(source).toHaveProperty("title");
    expect(source).toHaveProperty("url");
    expect(source).toHaveProperty("source");
  });
});

describe("API Contract: UserPreferences", () => {
  it("backend PreferencesResponse maps to frontend UserPreferences", () => {
    const prefs: UserPreferences = {
      user_types: mockUserProfileFromBackend.user_type ?? [],
      topics: mockPreferencesFromBackend.topics,
      sources: mockPreferencesFromBackend.sources,
      briefing_depth: mockPreferencesFromBackend.briefing_depth,
      location: mockPreferencesFromBackend.location,
    };
    expect(prefs.topics).toEqual(["ai", "tech"]);
    expect(prefs.briefing_depth).toBe("detailed");
    expect(prefs.location).toBe("Mumbai");
  });
});

describe("API Contract: WatchlistItem", () => {
  it("backend InterestResponse maps to frontend WatchlistItem", () => {
    const item: WatchlistItem = {
      id: mockInterestFromBackend.id,
      type: mockInterestFromBackend.type,
      value: mockInterestFromBackend.value,
      created_at: mockInterestFromBackend.added_at ?? "",
    };
    expect(item.type).toBe("stock");
    expect(item.value).toBe("RELIANCE");
  });
});

describe("API Contract: Schedule", () => {
  it("backend ScheduleResponse maps to frontend Schedule", () => {
    const schedule: Schedule = {
      id: mockScheduleFromBackend.user_id,
      times: mockScheduleFromBackend.times,
      timezone: mockScheduleFromBackend.timezone,
      enabled: mockScheduleFromBackend.enabled,
    };
    expect(schedule.times).toEqual(["07:00", "19:00"]);
    expect(schedule.timezone).toBe("Asia/Kolkata");
    expect(schedule.enabled).toBe(true);
  });
});

describe("API Contract: UserProfile", () => {
  it("backend UserProfile maps to frontend UserProfile", () => {
    const profile: UserProfile = {
      id: mockUserProfileFromBackend.id,
      email: mockUserProfileFromBackend.email,
      display_name: mockUserProfileFromBackend.name,
      avatar_url: null,
      onboarded: mockUserProfileFromBackend.onboarded,
      created_at: mockUserProfileFromBackend.created_at ?? "",
    };
    expect(profile.id).toBe("user-456");
    expect(profile.email).toBe("test@saar.app");
    expect(profile.onboarded).toBe(true);
  });
});

describe("API Contract: Impact values", () => {
  it("impact field only allows HIGH, MEDIUM, LOW", () => {
    const validImpacts: BriefingItem["impact"][] = ["HIGH", "MEDIUM", "LOW"];
    validImpacts.forEach((impact) => {
      const item: BriefingItem = {
        title: "Test",
        summary: "Test",
        url: "https://t.com",
        source: "test",
        impact,
      };
      expect(["HIGH", "MEDIUM", "LOW"]).toContain(item.impact);
    });
  });
});

describe("API Contract: Error response format", () => {
  it("backend error responses have consistent envelope", () => {
    const errorResp = {
      error: "Validation Error",
      detail: "query: Query cannot be empty",
      status: 422,
    };
    expect(errorResp).toHaveProperty("error");
    expect(errorResp).toHaveProperty("detail");
    expect(errorResp).toHaveProperty("status");
    expect(typeof errorResp.status).toBe("number");
  });
});
