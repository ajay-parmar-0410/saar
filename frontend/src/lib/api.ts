// API calls use relative URLs — Next.js rewrites proxy them to the backend.
// This avoids CORS, CSP, and mobile network issues with cross-origin requests.

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, headers: extraHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(extraHeaders as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(path, {
    headers,
    ...rest,
  });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      // Stale or invalid session — sign out from Supabase and redirect
      const { createClient } = await import("@/lib/supabase");
      await createClient().auth.signOut();
      window.location.href = "/login";
      throw new Error("Session expired");
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
