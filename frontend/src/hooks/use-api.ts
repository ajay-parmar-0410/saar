"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/auth-context";
import { apiFetch } from "@/lib/api";

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(path: string, options?: { skip?: boolean }) {
  const { session } = useAuth();
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: !options?.skip,
    error: null,
  });

  const fetch = useCallback(async () => {
    if (!session?.access_token) return;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await apiFetch<T>(path, {
        token: session.access_token,
      });
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: err instanceof Error ? err.message : "Request failed",
      });
    }
  }, [path, session?.access_token]);

  useEffect(() => {
    if (options?.skip) return;
    fetch();
  }, [fetch, options?.skip]);

  return { ...state, refetch: fetch };
}

export function useApiMutation<TBody, TResponse = unknown>(
  path: string,
  method: string = "POST"
) {
  const { session } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(
    async (body?: TBody): Promise<TResponse | null> => {
      if (!session?.access_token) return null;
      setLoading(true);
      setError(null);
      try {
        const data = await apiFetch<TResponse>(path, {
          method,
          token: session.access_token,
          body: body !== undefined ? JSON.stringify(body) : undefined,
        });
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Request failed";
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [path, method, session?.access_token]
  );

  return { mutate, loading, error };
}
