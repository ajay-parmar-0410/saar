"use client";

import { AuthGuard } from "@/components/auth-guard";
import { TopBar } from "@/components/layout/top-bar";
import { BottomNav } from "@/components/layout/bottom-nav";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen flex-col">
        <TopBar />
        <main className="mx-auto w-full max-w-lg flex-1 px-4 pb-20 pt-4">
          {children}
        </main>
        <BottomNav />
      </div>
    </AuthGuard>
  );
}
