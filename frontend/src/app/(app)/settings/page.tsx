"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { useTheme } from "@/context/theme-context";
import { useApi, useApiMutation } from "@/hooks/use-api";
import { apiFetch } from "@/lib/api";
import type {
  UserProfile,
  UserPreferences,
  WatchlistItem,
  Schedule,
} from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  User,
  Palette,
  Bell,
  Trash2,
  Loader2,
  Sun,
  Moon,
  Monitor,
  Plus,
  X,
} from "lucide-react";

const TOPIC_OPTIONS = [
  "ai_ml",
  "web_dev",
  "mobile",
  "devops",
  "security",
  "data_science",
  "blockchain",
  "cloud",
  "startups",
  "finance",
  "markets",
  "economy",
  "world_news",
  "india",
  "science",
  "health",
];

const SOURCE_OPTIONS = [
  "hackernews",
  "reddit",
  "github",
  "arxiv",
  "producthunt",
  "newsapi",
  "google_news",
  "yahoo_finance",
  "economic_times",
  "weatherapi",
];

const TIME_OPTIONS = [
  "06:00", "06:30", "07:00", "07:30", "08:00", "08:30",
  "09:00", "12:00", "13:00", "17:00", "18:00", "19:00", "20:00", "21:00",
];

const TIMEZONE_OPTIONS = [
  { value: "Asia/Kolkata", label: "India (IST)" },
  { value: "America/New_York", label: "US Eastern (ET)" },
  { value: "America/Los_Angeles", label: "US Pacific (PT)" },
  { value: "Europe/London", label: "UK (GMT/BST)" },
  { value: "Asia/Singapore", label: "Singapore (SGT)" },
];

function formatLabel(id: string): string {
  return id
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function SettingsPage() {
  const { session, signOut } = useAuth();
  const { theme, setTheme } = useTheme();
  const router = useRouter();

  const { data: profile } = useApi<UserProfile>("/api/v1/user/profile");
  const { data: prefs, refetch: refetchPrefs } =
    useApi<UserPreferences>("/api/v1/preferences");
  const { data: interests, refetch: refetchInterests } =
    useApi<WatchlistItem[]>("/api/v1/interests");
  const { data: schedule, refetch: refetchSchedule } =
    useApi<Schedule>("/api/v1/schedule");

  const [localPrefs, setLocalPrefs] = useState<UserPreferences | null>(null);
  const [localSchedule, setLocalSchedule] = useState<Schedule | null>(null);
  const [savingPrefs, setSavingPrefs] = useState(false);
  const [savingSchedule, setSavingSchedule] = useState(false);
  const [newInterest, setNewInterest] = useState({ type: "stock", value: "" });
  const [addingInterest, setAddingInterest] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (prefs && !localPrefs) setLocalPrefs(prefs);
  }, [prefs, localPrefs]);

  useEffect(() => {
    if (schedule && !localSchedule) setLocalSchedule(schedule);
  }, [schedule, localSchedule]);

  // --- Preferences ---
  const toggleTopic = (topic: string) => {
    if (!localPrefs) return;
    const topics = localPrefs.topics.includes(topic)
      ? localPrefs.topics.filter((t) => t !== topic)
      : [...localPrefs.topics, topic];
    setLocalPrefs({ ...localPrefs, topics });
  };

  const toggleSource = (source: string) => {
    if (!localPrefs) return;
    const sources = localPrefs.sources.includes(source)
      ? localPrefs.sources.filter((s) => s !== source)
      : [...localPrefs.sources, source];
    setLocalPrefs({ ...localPrefs, sources });
  };

  const savePrefs = useCallback(async () => {
    if (!localPrefs || !session?.access_token) return;
    setSavingPrefs(true);
    try {
      await apiFetch("/api/v1/preferences", {
        method: "PUT",
        token: session.access_token,
        body: JSON.stringify(localPrefs),
      });
      await refetchPrefs();
    } catch {
      // Revert
      if (prefs) setLocalPrefs(prefs);
    } finally {
      setSavingPrefs(false);
    }
  }, [localPrefs, session?.access_token, refetchPrefs, prefs]);

  // --- Schedule ---
  const toggleTime = (time: string) => {
    if (!localSchedule) return;
    const times = localSchedule.times.includes(time)
      ? localSchedule.times.filter((t) => t !== time)
      : [...localSchedule.times, time].sort();
    setLocalSchedule({ ...localSchedule, times });
  };

  const saveSchedule = useCallback(async () => {
    if (!localSchedule || !session?.access_token) return;
    setSavingSchedule(true);
    try {
      await apiFetch("/api/v1/schedule", {
        method: "PUT",
        token: session.access_token,
        body: JSON.stringify({
          times: localSchedule.times,
          timezone: localSchedule.timezone,
          enabled: localSchedule.enabled,
        }),
      });
      await refetchSchedule();
    } catch {
      if (schedule) setLocalSchedule(schedule);
    } finally {
      setSavingSchedule(false);
    }
  }, [localSchedule, session?.access_token, refetchSchedule, schedule]);

  // --- Interests ---
  const addInterest = useCallback(async () => {
    if (!newInterest.value.trim() || !session?.access_token) return;
    setAddingInterest(true);
    try {
      await apiFetch("/api/v1/interests", {
        method: "POST",
        token: session.access_token,
        body: JSON.stringify(newInterest),
      });
      setNewInterest({ type: "stock", value: "" });
      await refetchInterests();
    } catch {
      // Silent
    } finally {
      setAddingInterest(false);
    }
  }, [newInterest, session?.access_token, refetchInterests]);

  const removeInterest = useCallback(
    async (id: string) => {
      if (!session?.access_token) return;
      try {
        await apiFetch(`/api/v1/interests/${id}`, {
          method: "DELETE",
          token: session.access_token,
        });
        await refetchInterests();
      } catch {
        // Silent
      }
    },
    [session?.access_token, refetchInterests]
  );

  // --- Delete Account ---
  const handleDelete = useCallback(async () => {
    if (!session?.access_token) return;
    setDeleting(true);
    try {
      await apiFetch("/api/v1/user", {
        method: "DELETE",
        token: session.access_token,
      });
      await signOut();
      router.push("/");
    } catch {
      setDeleting(false);
      setDeleteConfirm(false);
    }
  }, [session?.access_token, signOut, router]);

  return (
    <div className="space-y-8 pb-8">
      <h1 className="text-lg font-bold">Settings</h1>

      {/* Profile */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase text-muted-foreground">
          <User className="size-4" />
          Profile
        </div>
        {profile && (
          <div className="rounded-lg border border-border bg-card p-4">
            <div className="text-sm font-medium">
              {profile.display_name || profile.email}
            </div>
            <div className="text-xs text-muted-foreground">{profile.email}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              Member since{" "}
              {new Date(profile.created_at).toLocaleDateString("en-IN", {
                month: "short",
                year: "numeric",
              })}
            </div>
          </div>
        )}
      </section>

      {/* Appearance */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase text-muted-foreground">
          <Palette className="size-4" />
          Appearance
        </div>
        <div className="flex gap-2">
          {(
            [
              { value: "light", icon: Sun, label: "Light" },
              { value: "dark", icon: Moon, label: "Dark" },
              { value: "system", icon: Monitor, label: "System" },
            ] as const
          ).map(({ value, icon: Icon, label }) => (
            <button
              key={value}
              onClick={() => setTheme(value)}
              className={`flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-lg border-2 px-3 py-2 text-sm font-medium transition-colors ${
                theme === value
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50"
              }`}
            >
              <Icon className="size-4" />
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* Topics & Sources */}
      {localPrefs && (
        <section className="space-y-3">
          <div className="text-sm font-semibold uppercase text-muted-foreground">
            Topics
          </div>
          <div className="flex flex-wrap gap-2">
            {TOPIC_OPTIONS.map((topic) => {
              const isActive = localPrefs.topics.includes(topic);
              return (
                <button
                  key={topic}
                  onClick={() => toggleTopic(topic)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  {formatLabel(topic)}
                </button>
              );
            })}
          </div>

          <div className="text-sm font-semibold uppercase text-muted-foreground">
            Sources
          </div>
          <div className="flex flex-wrap gap-2">
            {SOURCE_OPTIONS.map((source) => {
              const isActive = localPrefs.sources.includes(source);
              return (
                <button
                  key={source}
                  onClick={() => toggleSource(source)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  {formatLabel(source)}
                </button>
              );
            })}
          </div>

          <Button
            onClick={savePrefs}
            disabled={savingPrefs}
            size="sm"
          >
            {savingPrefs ? "Saving..." : "Save Preferences"}
          </Button>
        </section>
      )}

      {/* Watchlist */}
      <section className="space-y-3">
        <div className="text-sm font-semibold uppercase text-muted-foreground">
          Watchlist
        </div>

        <div className="flex gap-2">
          <select
            value={newInterest.type}
            onChange={(e) =>
              setNewInterest({ ...newInterest, type: e.target.value })
            }
            className="rounded-md border border-input bg-background px-2 py-2 text-sm"
          >
            <option value="stock">Stock</option>
            <option value="repo">Repo</option>
            <option value="subreddit">Subreddit</option>
            <option value="keyword">Keyword</option>
          </select>
          <input
            type="text"
            value={newInterest.value}
            onChange={(e) =>
              setNewInterest({ ...newInterest, value: e.target.value })
            }
            onKeyDown={(e) => e.key === "Enter" && addInterest()}
            placeholder="Add item..."
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <button
            onClick={addInterest}
            disabled={!newInterest.value.trim() || addingInterest}
            className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground disabled:opacity-50"
          >
            <Plus className="size-4" />
          </button>
        </div>

        {interests && interests.length > 0 && (
          <div className="space-y-1">
            {interests.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-md border border-border px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase text-muted-foreground">
                    {item.type}
                  </span>
                  <span className="text-sm">{item.value}</span>
                </div>
                <button
                  onClick={() => removeInterest(item.id)}
                  className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                >
                  <X className="size-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Schedule */}
      {localSchedule && (
        <section className="space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold uppercase text-muted-foreground">
            <Bell className="size-4" />
            Schedule
          </div>

          <div className="flex flex-wrap gap-2">
            {TIME_OPTIONS.map((time) => {
              const isActive = localSchedule.times.includes(time);
              return (
                <button
                  key={time}
                  onClick={() => toggleTime(time)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  {time}
                </button>
              );
            })}
          </div>

          <select
            value={localSchedule.timezone}
            onChange={(e) =>
              setLocalSchedule({ ...localSchedule, timezone: e.target.value })
            }
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {TIMEZONE_OPTIONS.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label}
              </option>
            ))}
          </select>

          <Button
            onClick={saveSchedule}
            disabled={savingSchedule}
            size="sm"
          >
            {savingSchedule ? "Saving..." : "Save Schedule"}
          </Button>
        </section>
      )}

      {/* Sign Out */}
      <section className="border-t border-border pt-6">
        <Button variant="outline" onClick={signOut} className="w-full">
          Sign Out
        </Button>
      </section>

      {/* Delete Account */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase text-destructive">
          <Trash2 className="size-4" />
          Danger Zone
        </div>
        {!deleteConfirm ? (
          <Button
            variant="destructive"
            onClick={() => setDeleteConfirm(true)}
            className="w-full"
          >
            Delete Account
          </Button>
        ) : (
          <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
            <p className="mb-3 text-sm">
              This will permanently delete your account and all data. This
              action cannot be undone.
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setDeleteConfirm(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                className="flex-1"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  "Confirm Delete"
                )}
              </Button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
