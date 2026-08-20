import { useState, useCallback } from "react";
import { api, SearchResponse } from "../lib/api";

export function useSearch() {
  const [data, setData] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = useCallback(async (params: { query: string; format?: string; limit?: number }) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.search(params.query, {
        format: params.format,
        limit: params.limit || 5,
      });
      setData(res);
      return res;
    } catch (err: any) {
      const errorObj = err instanceof Error ? err : new Error(err?.message || "Search failed");
      setError(errorObj);
      throw errorObj;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    data,
    isLoading,
    error,
    mutate,
    reset: () => {
      setData(null);
      setError(null);
    },
  };
}
