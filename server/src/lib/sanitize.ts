const HTML_TAG = /<[^>]*>/g;
const SCRIPT_PATTERN = /javascript:|on\w+\s*=/gi;
const MAX_INPUT_LENGTH = 2000;

export function sanitizeInput(input: string): string {
  if (typeof input !== "string") return "";

  return input
    .replace(HTML_TAG, "")
    .replace(SCRIPT_PATTERN, "")
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "")
    .trim()
    .slice(0, MAX_INPUT_LENGTH);
}

export function isValidInput(input: string): boolean {
  return input.length >= 3 && input.length <= MAX_INPUT_LENGTH;
}

export const MAX_INPUT = MAX_INPUT_LENGTH;
