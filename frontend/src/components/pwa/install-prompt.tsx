"use client";

import { useState, useEffect } from "react";
import { X, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Show after 2nd visit
    const visitCount = Number(localStorage.getItem("saar-visits") || "0") + 1;
    localStorage.setItem("saar-visits", String(visitCount));
    const dismissed = localStorage.getItem("saar-install-dismissed");

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      if (visitCount >= 2 && !dismissed) {
        setShow(true);
      }
    };

    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setShow(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShow(false);
    localStorage.setItem("saar-install-dismissed", "true");
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 mx-auto max-w-lg animate-in slide-in-from-bottom-4">
      <div className="flex items-center gap-3 rounded-xl border border-border bg-card p-4 shadow-lg">
        <Download className="size-5 shrink-0 text-primary" />
        <div className="flex-1">
          <p className="text-sm font-medium">Add Saar to Home Screen</p>
          <p className="text-xs text-muted-foreground">
            Quick access to your briefings
          </p>
        </div>
        <Button size="sm" onClick={handleInstall}>
          Install
        </Button>
        <button
          onClick={handleDismiss}
          className="rounded p-1 text-muted-foreground hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>
    </div>
  );
}
