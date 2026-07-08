export type MemeCategory =
  | "coding"
  | "startup"
  | "relationship"
  | "college"
  | "office"
  | "funny"
  | "motivation"
  | "unrealistic_goals"
  | "ai"
  | "business"
  | "exam"
  | "failure"
  | "success"
  | "gaming"
  | "bollywood"
  | "youtube";

export interface MemeData {
  name: string;
  category: MemeCategory;
  keywords: string[];
  dialogue: string;
  explanation: string;
  video?: string;
  gif?: string;
  viralScore?: number;
}

export interface MemeRecord {
  id: string;
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  keywords: string[];
  videoRef?: string | null;
  gifRef?: string | null;
  viralScore: number;
  usageCount: number;
  upvotes: number;
  downvotes: number;
}

export interface MemeMatch {
  id: string;
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  confidence: number;
  videoRef?: string | null;
  gifRef?: string | null;
  viralScore: number;
  usageCount: number;
}

export interface MemeSearchResult {
  primary: MemeMatch;
  topFive: MemeMatch[];
  alternatives: MemeMatch[];
  detectedCategories: string[];
  detectedTags: string[];
  gifs: string[];
  viralSuggestions: MemeMatch[];
  latencyMs: number;
}

export const MEME_CATEGORIES: { value: MemeCategory; label: string }[] = [
  { value: "coding", label: "Coding" },
  { value: "startup", label: "Startup" },
  { value: "relationship", label: "Relationship" },
  { value: "college", label: "College" },
  { value: "office", label: "Office" },
  { value: "funny", label: "Funny" },
  { value: "motivation", label: "Motivation" },
  { value: "unrealistic_goals", label: "Unrealistic Goals" },
  { value: "ai", label: "AI" },
  { value: "business", label: "Business" },
  { value: "exam", label: "Exam" },
  { value: "failure", label: "Failure" },
  { value: "success", label: "Success" },
  { value: "gaming", label: "Gaming" },
  { value: "bollywood", label: "Bollywood" },
  { value: "youtube", label: "YouTube" },
];
