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

export interface MemeRecord extends MemeMatch {
  keywords: string[];
  upvotes: number;
  downvotes: number;
}

export const CATEGORY_LABELS: Record<string, string> = {
  coding: "Coding",
  startup: "Startup",
  relationship: "Relationship",
  college: "College",
  office: "Office",
  funny: "Funny",
  motivation: "Motivation",
  unrealistic_goals: "Unrealistic Goals",
  ai: "AI",
  business: "Business",
  exam: "Exam",
  failure: "Failure",
  success: "Success",
  gaming: "Gaming",
  bollywood: "Bollywood",
  youtube: "YouTube",
};
