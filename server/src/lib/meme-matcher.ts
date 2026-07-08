import type { MemeRecord, MemeMatch, MemeSearchResult } from "./types.js";
import { runRuleEngine } from "./rule-engine.js";
import { getTopSemanticMatches } from "./semantic-search.js";

function toMatch(meme: MemeRecord, confidence: number): MemeMatch {
  return {
    id: meme.id,
    name: meme.name,
    category: meme.category,
    dialogue: meme.dialogue,
    explanation: meme.explanation,
    confidence: Math.round(confidence * 100) / 100,
    videoRef: meme.videoRef,
    gifRef: meme.gifRef,
    viralScore: meme.viralScore,
    usageCount: meme.usageCount,
  };
}

export function matchMemes(query: string, memes: MemeRecord[]): MemeSearchResult {
  const start = performance.now();
  const rules = runRuleEngine(query);
  const semantic = getTopSemanticMatches(query, memes, 20);

  const scored = memes.map((meme) => {
    let score = 0;

    const sem = semantic.find((s) => s.id === meme.id);
    if (sem) score += sem.score * 0.45;

    if (rules.categories.includes(meme.category)) {
      score += (rules.scores[meme.category] ?? 0) * 0.35;
    }

    for (const kw of meme.keywords) {
      if (query.toLowerCase().includes(kw.toLowerCase())) {
        score += 0.08;
      }
      for (const tag of rules.tags) {
        if (kw.toLowerCase().includes(tag.replace(/_/g, " "))) {
          score += 0.05;
        }
      }
    }

    score += Math.min(meme.viralScore / 100, 0.1);
    score += Math.min(meme.usageCount / 1000, 0.05);

    return { meme, score: Math.min(score, 0.99) };
  });

  scored.sort((a, b) => b.score - a.score);

  const ranked = scored.filter((s) => s.score > 0.05);
  const top = ranked.length > 0 ? ranked : scored;

  const primary = toMatch(top[0].meme, top[0].score);
  const topFive = top.slice(0, 5).map((s) => toMatch(s.meme, s.score));
  const alternatives = top.slice(1, 11).map((s) => toMatch(s.meme, s.score));

  const viralSuggestions = [...memes]
    .sort((a, b) => b.viralScore + b.usageCount * 0.1 - (a.viralScore + a.usageCount * 0.1))
    .slice(0, 5)
    .map((m) => toMatch(m, 0.75));

  const gifs = top
    .slice(0, 5)
    .map((s) => s.meme.gifRef)
    .filter((g): g is string => !!g);

  return {
    primary,
    topFive,
    alternatives,
    detectedCategories: rules.categories,
    detectedTags: rules.tags,
    gifs,
    viralSuggestions,
    latencyMs: Math.round(performance.now() - start),
  };
}

export function buildExplanation(query: string, match: MemeMatch): string {
  return `${match.explanation} This meme fits because your situation "${query.slice(0, 80)}${query.length > 80 ? "..." : ""}" aligns with the ${match.category.replace(/_/g, " ")} theme.`;
}
