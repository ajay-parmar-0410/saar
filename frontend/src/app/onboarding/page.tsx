"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/auth-guard";
import { useAuth } from "@/context/auth-context";
import { apiFetch } from "@/lib/api";
import { UserTypeStep } from "@/components/onboarding/user-type-step";
import { StarterPackStep } from "@/components/onboarding/starter-pack-step";
import { WatchlistStep } from "@/components/onboarding/watchlist-step";
import { ScheduleStep } from "@/components/onboarding/schedule-step";

interface WatchlistItem {
  type: string;
  value: string;
}

interface OnboardingState {
  userTypes: string[];
  topics: string[];
  sources: string[];
  interests: WatchlistItem[];
  schedule: {
    times: string[];
    timezone: string;
    depth: string;
  };
}

const INITIAL_STATE: OnboardingState = {
  userTypes: [],
  topics: [],
  sources: [],
  interests: [],
  schedule: {
    times: ["07:00"],
    timezone: "Asia/Kolkata",
    depth: "detailed",
  },
};

function OnboardingWizard() {
  const [step, setStep] = useState(0);
  const [state, setState] = useState<OnboardingState>(INITIAL_STATE);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const { session } = useAuth();
  const router = useRouter();

  const handleSubmit = async () => {
    if (!session?.access_token) return;
    setSubmitting(true);
    setError("");

    try {
      await apiFetch("/api/v1/onboarding/complete", {
        method: "POST",
        token: session.access_token,
        body: JSON.stringify({
          user_types: state.userTypes,
          topics: state.topics,
          sources: state.sources,
          briefing_depth: state.schedule.depth,
          interests: state.interests,
          schedule: {
            times: state.schedule.times,
            timezone: state.schedule.timezone,
          },
        }),
      });
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  };

  const steps = ["Type", "Topics", "Watchlist", "Schedule"];

  return (
    <div className="flex min-h-screen flex-col bg-background px-4 py-8">
      <div className="mx-auto w-full max-w-md">
        {/* Progress indicator */}
        <div className="mb-8 flex items-center justify-center gap-2">
          {steps.map((label, i) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${
                  i <= step
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {i + 1}
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`h-0.5 w-6 ${
                    i < step ? "bg-primary" : "bg-muted"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </div>
        )}

        {step === 0 && (
          <UserTypeStep
            selected={state.userTypes}
            onSelect={(types) =>
              setState({ ...state, userTypes: types, topics: [], sources: [] })
            }
            onNext={() => setStep(1)}
          />
        )}

        {step === 1 && (
          <StarterPackStep
            userTypes={state.userTypes}
            topics={state.topics}
            sources={state.sources}
            onUpdate={(topics, sources) =>
              setState({ ...state, topics, sources })
            }
            onNext={() => setStep(2)}
            onBack={() => setStep(0)}
          />
        )}

        {step === 2 && (
          <WatchlistStep
            items={state.interests}
            onUpdate={(interests) => setState({ ...state, interests })}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
          />
        )}

        {step === 3 && (
          <ScheduleStep
            schedule={state.schedule}
            onUpdate={(schedule) => setState({ ...state, schedule })}
            onSubmit={handleSubmit}
            onBack={() => setStep(2)}
            submitting={submitting}
          />
        )}
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  return (
    <AuthGuard>
      <OnboardingWizard />
    </AuthGuard>
  );
}
