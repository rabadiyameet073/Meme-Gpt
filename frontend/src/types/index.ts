export interface MemeMatch {
  id: string;
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  confidence?: number;
  videoRef?: string | null;
  gifRef?: string | null;
  viralScore?: number;
  usageCount?: number;
  formats?: {
    image?: string;
    gif?: string;
    video?: string;
    webp?: string;
  };
  imageRef?: string | null;
  preview_url?: string | null;
  slug?: string;
  description?: string;
  tags?: string[];
}

export interface MemeSearchResult {
  primary?: MemeMatch;
  topFive?: MemeMatch[];
  alternatives?: MemeMatch[];
  detectedCategories?: string[];
  detectedTags?: string[];
  gifs?: string[];
  viralSuggestions?: MemeMatch[];
  latencyMs?: number;
  query_id?: string;
  queryId?: string;
}

export interface MemeRecord extends MemeMatch {
  keywords?: string[];
  upvotes?: number;
  downvotes?: number;
}

export interface Meme extends MemeMatch {
  slug?: string;
  description?: string;
  tags?: string[];
}

export interface StatsResponse {
  totalMemes?: number;
  totalSearches?: number;
  totalUsage?: number;
  totalVotes?: number;
  avgLatencyMs?: number;
  [key: string]: any;
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

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  plan?: string;
  preferences?: Record<string, any>;
  preferred_format?: string;
  theme?: string;
  nsfw_enabled?: boolean;
  favourite_categories?: string[];
  oauth_provider?: string;
  is_admin?: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

