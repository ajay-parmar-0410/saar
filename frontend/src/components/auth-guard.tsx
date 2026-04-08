"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { apiFetch } from "@/lib/api";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, session, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const isOnboardingPage = pathname === "/onboarding";
  const [checkingOnboarding, setCheckingOnboarding] = useState(!isOnboardingPage);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  // Check if user has completed onboarding (has sources configured)
  // Skip this check if already on the onboarding page
  useEffect(() => {
    if (isOnboardingPage || !session?.access_token || !user) {
      setCheckingOnboarding(false);
      return;
    }

    apiFetch<{ topics: string[]; sources: string[] }>(
      "/api/v1/preferences",
      { token: session.access_token }
    )
      .then((prefs) => {
        if (!prefs.sources || prefs.sources.length === 0) {
          router.replace("/onboarding");
        }
        setCheckingOnboarding(false);
      })
      .catch((err) => {
        // Only redirect to onboarding on 404 (no preferences exist)
        // For other errors (network, 401, 500), let the page handle it
        if (err instanceof Error && err.message.includes("not found")) {
          router.replace("/onboarding");
        }
        setCheckingOnboarding(false);
      });
  }, [session?.access_token, user, router, isOnboardingPage]);

  if (loading || checkingOnboarding) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
