"use client";

import { AuthGuard } from "@/components/auth-guard";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <AuthGuard>
      <HomePage />
    </AuthGuard>
  );
}

function HomePage() {
  const { user, signOut } = useAuth();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm space-y-6 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Saar</h1>
        <p className="text-sm text-muted-foreground">
          Welcome, {user?.email}
        </p>
        <p className="text-xs text-muted-foreground">
          Briefing, Chat, and Settings coming soon.
        </p>
        <Button variant="outline" onClick={signOut}>
          Sign Out
        </Button>
      </div>
    </div>
  );
}
