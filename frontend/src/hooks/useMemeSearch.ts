import { useState, useCallback } from "react";
import { api, MemeResult } from "../lib/api";

export function useMemeSearch() {
  const [results, setResults] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.search(query);
      setResults(res?.results || []);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error(err?.message || "Search failed"));
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    results,
    loading,
    error,
    search,
  };
}
