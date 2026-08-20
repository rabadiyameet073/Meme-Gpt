import { useState, useEffect, useCallback } from "react";
import { api, TrendingResponse } from "../lib/api";

export function useTrending(category: string = "all", limit: number = 20) {
  const [data, setData] = useState<TrendingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTrending = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getTrending({ category, limit });
      setData(res);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error(err?.message || "Failed to fetch trending memes"));
    } finally {
      setIsLoading(false);
    }
  }, [category, limit]);

  useEffect(() => {
    fetchTrending();
  }, [fetchTrending]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchTrending,
  };
}
