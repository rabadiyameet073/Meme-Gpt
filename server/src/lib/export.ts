import type { MemeSearchResult } from "./types.js";

export function exportAsTxt(result: MemeSearchResult, query: string): string {
  const lines = [
    "=== MemeGPT Result ===",
    "",
    `Situation: ${query}`,
    "",
    "--- Primary Meme ---",
    `Name: ${result.primary.name}`,
    `Category: ${result.primary.category}`,
    `Dialogue: ${result.primary.dialogue}`,
    `Confidence: ${Math.round(result.primary.confidence * 100)}%`,
    `Explanation: ${result.primary.explanation}`,
    result.primary.videoRef ? `Video: ${result.primary.videoRef}` : "",
    "",
    "--- Top 5 Memes ---",
    ...result.topFive.map(
      (m, i) =>
        `${i + 1}. ${m.name} (${Math.round(m.confidence * 100)}%) — "${m.dialogue}"`
    ),
    "",
    "--- Alternatives ---",
    ...result.alternatives.map(
      (m, i) =>
        `${i + 1}. ${m.name} (${Math.round(m.confidence * 100)}%) — "${m.dialogue}"`
    ),
    "",
    `Detected: ${result.detectedTags.join(", ")}`,
    `Latency: ${result.latencyMs}ms`,
  ];
  return lines.filter(Boolean).join("\n");
}

export function exportAsMarkdown(result: MemeSearchResult, query: string): string {
  return `# MemeGPT Result

## Situation
> ${query}

## Primary Meme
- **Name:** ${result.primary.name}
- **Category:** ${result.primary.category}
- **Dialogue:** "${result.primary.dialogue}"
- **Confidence:** ${Math.round(result.primary.confidence * 100)}%
- **Explanation:** ${result.primary.explanation}
${result.primary.videoRef ? `- **Video:** ${result.primary.videoRef}` : ""}

## Top 5 Memes
${result.topFive.map((m, i) => `${i + 1}. **${m.name}** (${Math.round(m.confidence * 100)}%) — "${m.dialogue}"`).join("\n")}

## Alternatives
${result.alternatives.map((m, i) => `${i + 1}. **${m.name}** (${Math.round(m.confidence * 100)}%) — "${m.dialogue}"`).join("\n")}

## Viral Suggestions
${result.viralSuggestions.map((m) => `- ${m.name}: "${m.dialogue}"`).join("\n")}

---
*Tags: ${result.detectedTags.join(", ")} | ${result.latencyMs}ms*
`;
}

export function exportAsJson(result: MemeSearchResult, query: string): string {
  return JSON.stringify({ query, ...result }, null, 2);
}
