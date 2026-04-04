// ---- Briefing ----

export interface BriefingItem {
  title: string;
  summary: string;
  url: string;
  source: string;
  impact: "HIGH" | "MEDIUM" | "LOW";
}

export interface BriefingSection {
  name: string;
  items: BriefingItem[];
}

export interface Briefing {
  id: string;
  user_id: string;
  sections: BriefingSection[];
  top_story: BriefingItem | null;
  item_count: number;
  alert_count: number;
  briefing_depth: string;
  is_read: boolean;
  created_at: string;
}

export interface BriefingListItem {
  id: string;
  top_story_title: string | null;
  item_count: number;
  alert_count: number;
  is_read: boolean;
  created_at: string;
}

// ---- Chat ----

export interface ChatSource {
  title: string;
  url: string;
  source: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[];
  created_at: string;
}

export interface ChatResponse {
  response: string;
  sources: ChatSource[];
}

// ---- Preferences ----

export interface UserPreferences {
  user_types: string[];
  topics: string[];
  sources: string[];
  briefing_depth: string;
  location: string | null;
}

// ---- Interests ----

export interface WatchlistItem {
  id: string;
  type: string;
  value: string;
  created_at: string;
}

// ---- Schedule ----

export interface Schedule {
  id: string;
  times: string[];
  timezone: string;
  enabled: boolean;
}

// ---- User ----

export interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  onboarded: boolean;
  created_at: string;
}
