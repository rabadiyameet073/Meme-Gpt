import { useState, useCallback } from "react";

export function useFormatPreference() {
  const [format, setFormatState] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("format_preference") || "gif";
    }
    return "gif";
  });

  const setFormat = useCallback((newFormat: string) => {
    setFormatState(newFormat);
    if (typeof window !== "undefined") {
      localStorage.setItem("format_preference", newFormat);
    }
  }, []);

  return [format, setFormat] as const;
}
