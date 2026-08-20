import { useState, useCallback } from "react";

export interface ValidationErrorItem {
  field: string;
  message: string;
}

export function useSearchValidation() {
  const [errors, setErrors] = useState<ValidationErrorItem[]>([]);

  const validate = useCallback((query: string): boolean => {
    const newErrors: ValidationErrorItem[] = [];

    const trimmed = query.trim();
    if (!trimmed) {
      newErrors.push({ field: "query", message: "Please enter something to search for" });
    } else if (trimmed.length > 2000) {
      newErrors.push({ field: "query", message: "Query must be under 2000 characters" });
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  }, []);

  const clearErrors = useCallback(() => setErrors([]), []);

  const getFieldError = useCallback(
    (field: string): string | undefined => {
      return errors.find((e) => e.field === field)?.message;
    },
    [errors]
  );

  return {
    errors,
    validate,
    clearErrors,
    getFieldError,
    hasErrors: errors.length > 0,
  };
}
