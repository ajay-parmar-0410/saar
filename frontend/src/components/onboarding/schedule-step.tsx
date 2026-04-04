"use client";

import { Button } from "@/components/ui/button";

interface ScheduleConfig {
  times: string[];
  timezone: string;
  depth: string;
}

interface ScheduleStepProps {
  schedule: ScheduleConfig;
  onUpdate: (schedule: ScheduleConfig) => void;
  onSubmit: () => void;
  onBack: () => void;
  submitting: boolean;
}

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

export function ScheduleStep({
  schedule,
  onUpdate,
  onSubmit,
  onBack,
  submitting,
}: ScheduleStepProps) {
  const toggleTime = (time: string) => {
    const updated = schedule.times.includes(time)
      ? schedule.times.filter((t) => t !== time)
      : [...schedule.times, time].sort();
    onUpdate({ ...schedule, times: updated });
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Set Your Schedule</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          When should we prepare your briefing?
        </p>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Briefing Time(s)
        </h3>
        <div className="flex flex-wrap gap-2">
          {TIME_OPTIONS.map((time) => {
            const isSelected = schedule.times.includes(time);
            return (
              <button
                key={time}
                onClick={() => toggleTime(time)}
                className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
                  isSelected
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {time}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Timezone
        </h3>
        <select
          value={schedule.timezone}
          onChange={(e) => onUpdate({ ...schedule, timezone: e.target.value })}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        >
          {TIMEZONE_OPTIONS.map((tz) => (
            <option key={tz.value} value={tz.value}>
              {tz.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold uppercase text-muted-foreground">
          Briefing Depth
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { id: "headlines", title: "Headlines", desc: "Quick 1-min scan" },
            { id: "detailed", title: "Detailed", desc: "Full 3-min read" },
          ].map((option) => (
            <button
              key={option.id}
              onClick={() => onUpdate({ ...schedule, depth: option.id })}
              className={`rounded-lg border-2 p-3 text-left transition-colors ${
                schedule.depth === option.id
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50"
              }`}
            >
              <div className="text-sm font-semibold">{option.title}</div>
              <div className="text-xs text-muted-foreground">{option.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={onBack}>
          Back
        </Button>
        <Button
          className="flex-1"
          onClick={onSubmit}
          disabled={schedule.times.length === 0 || submitting}
        >
          {submitting ? "Setting up..." : "Complete Setup"}
        </Button>
      </div>
    </div>
  );
}
