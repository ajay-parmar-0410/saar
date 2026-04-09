"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">(
    "idle"
  );
  const [errorMessage, setErrorMessage] = useState("");
  const { user, loading, signInWithMagicLink, signInWithGoogle } = useAuth();
  const [googleLoading, setGoogleLoading] = useState(false);
  const router = useRouter();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (user) {
    router.replace("/briefing");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setStatus("sending");
    setErrorMessage("");

    const { error } = await signInWithMagicLink(email);

    if (error) {
      setStatus("error");
      setErrorMessage(error);
    } else {
      setStatus("sent");
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 dark:bg-slate-900">
      {/* Brand */}
      <h1 className="mb-8 text-3xl font-extrabold tracking-tight text-primary">
        Saar
      </h1>

      {/* Login card */}
      <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-800">
        <h2 className="text-center text-xl font-bold text-slate-900 dark:text-white">
          Welcome back!
        </h2>
        <p className="mt-1 text-center text-sm text-slate-500 dark:text-slate-400">
          Sign in to get your daily briefing
        </p>

        {/* Google Sign In */}
        <button
          disabled={googleLoading}
          onClick={async () => {
            setGoogleLoading(true);
            const { error } = await signInWithGoogle();
            if (error) {
              setStatus("error");
              setErrorMessage(error);
              setGoogleLoading(false);
            }
          }}
          className="mt-6 flex min-h-[48px] w-full items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-700 dark:text-white dark:hover:bg-slate-600"
        >
          <svg className="size-5" viewBox="0 0 24 24">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          {googleLoading ? "Redirecting..." : "Continue with Google"}
        </button>

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
          <span className="text-xs font-medium uppercase text-slate-400">or</span>
          <div className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
        </div>

        {/* Magic Link */}
        {status === "sent" ? (
          <div className="rounded-xl bg-primary/5 p-5 text-center dark:bg-primary/10">
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              Check your email
            </h3>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              We sent a magic link to <strong className="text-foreground">{email}</strong>.
            </p>
            <button
              className="mt-4 text-sm font-medium text-primary hover:underline"
              onClick={() => setStatus("idle")}
            >
              Use a different email
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-slate-700 dark:text-slate-300"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1.5 block min-h-[48px] w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm placeholder:text-slate-400 focus:border-primary focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-700 dark:placeholder:text-slate-500 dark:focus:bg-slate-600"
                disabled={status === "sending"}
              />
            </div>

            {status === "error" && (
              <p className="text-sm text-destructive">{errorMessage}</p>
            )}

            <button
              type="submit"
              disabled={status === "sending"}
              className="flex min-h-[48px] w-full items-center justify-center rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {status === "sending" ? "Sending..." : "Send Magic Link"}
            </button>
          </form>
        )}
      </div>

      {/* Footer */}
      <p className="mt-8 text-center text-xs text-slate-400">
        By signing in, you agree to our terms of service.
      </p>
    </div>
  );
}
