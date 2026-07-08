import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { runRuleEngine } from "../src/lib/rule-engine.js";
import { matchMemes } from "../src/lib/meme-matcher.js";
import { sanitizeInput, isValidInput } from "../src/lib/sanitize.js";
import type { MemeRecord } from "../src/lib/types.js";

const sampleMemes: MemeRecord[] = [
  {
    id: "1",
    name: "Khwab Dekho Raat Bhar",
    category: "unrealistic_goals",
    dialogue: "Khwab Dekho Raat Bhar",
    explanation: "Unrealistic expectations.",
    keywords: ["100%", "accuracy", "impossible", "dream"],
    viralScore: 90,
    usageCount: 10,
    upvotes: 5,
    downvotes: 0,
  },
  {
    id: "2",
    name: "Aukat Me Reh",
    category: "unrealistic_goals",
    dialogue: "Khwab To Dekho Magar Aukat Ke Hisab Se",
    explanation: "Stay within limits.",
    keywords: ["aukat", "impossible", "100%"],
    viralScore: 95,
    usageCount: 20,
    upvotes: 10,
    downvotes: 1,
  },
];

describe("sanitize", () => {
  it("strips HTML tags", () => {
    assert.equal(sanitizeInput("<script>alert(1)</script>hello"), "hello");
  });

  it("validates length", () => {
    assert.equal(isValidInput("hi"), false);
    assert.equal(isValidInput("valid input here"), true);
  });
});

describe("rule engine", () => {
  it("detects unrealistic expectations", () => {
    const result = runRuleEngine("Can you make accuracy 100% by tomorrow?");
    assert.ok(result.tags.includes("unrealistic_expectation"));
    assert.ok(result.categories.includes("unrealistic_goals"));
  });

  it("detects coding issues", () => {
    const result = runRuleEngine("Production bug after deploy");
    assert.ok(result.tags.includes("coding"));
  });
});

describe("meme matcher", () => {
  it("matches accuracy query to unrealistic meme", () => {
    const result = matchMemes(
      "I worked 3 months and accuracy is only 12%. Can you make it 100%?",
      sampleMemes
    );
    assert.ok(result.primary.confidence > 0);
    assert.ok(result.topFive.length >= 1);
    assert.ok(result.latencyMs < 1000);
  });
});
