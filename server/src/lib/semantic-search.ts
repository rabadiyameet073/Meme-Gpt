import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import type { MemeRecord } from "./types.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EMBEDDINGS_PATH = path.resolve(__dirname, "../../data/embeddings.json");

interface EmbeddingEntry {
  id: string;
  vector: number[];
}

let cachedEmbeddings: Map<string, number[]> | null = null;

function loadEmbeddings(): Map<string, number[]> | null {
  if (cachedEmbeddings) return cachedEmbeddings;

  try {
    if (!fs.existsSync(EMBEDDINGS_PATH)) return null;
    const raw = JSON.parse(fs.readFileSync(EMBEDDINGS_PATH, "utf-8")) as EmbeddingEntry[];
    cachedEmbeddings = new Map(raw.map((e) => [e.id, e.vector]));
    return cachedEmbeddings;
  } catch {
    return null;
  }
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\w\s%]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 1);
}

function buildTfIdfVector(tokens: string[], idf: Map<string, number>, dim: number): number[] {
  const tf = new Map<string, number>();
  for (const t of tokens) {
    tf.set(t, (tf.get(t) ?? 0) + 1);
  }

  const vec = new Array(dim).fill(0);
  let idx = 0;
  for (const [term, count] of tf) {
    const idfVal = idf.get(term) ?? 0;
    const hash = hashTerm(term, dim);
    vec[hash] += (count / tokens.length) * idfVal;
    idx++;
  }

  return normalize(vec);
}

function hashTerm(term: string, dim: number): number {
  let h = 0;
  for (let i = 0; i < term.length; i++) {
    h = (h * 31 + term.charCodeAt(i)) >>> 0;
  }
  return h % dim;
}

function normalize(vec: number[]): number[] {
  const mag = Math.sqrt(vec.reduce((s, v) => s + v * v, 0)) || 1;
  return vec.map((v) => v / mag);
}

function cosineSimilarity(a: number[], b: number[]): number {
  const len = Math.min(a.length, b.length);
  let dot = 0;
  for (let i = 0; i < len; i++) {
    dot += a[i] * b[i];
  }
  return dot;
}

function buildIdf(corpus: string[][]): Map<string, number> {
  const df = new Map<string, number>();
  const n = corpus.length;

  for (const doc of corpus) {
    const unique = new Set(doc);
    for (const term of unique) {
      df.set(term, (df.get(term) ?? 0) + 1);
    }
  }

  const idf = new Map<string, number>();
  for (const [term, count] of df) {
    idf.set(term, Math.log((n + 1) / (count + 1)) + 1);
  }
  return idf;
}

const DIM = 384;

export function semanticSearch(
  query: string,
  memes: MemeRecord[],
  limit = 15
): Map<string, number> {
  const scores = new Map<string, number>();
  const queryTokens = tokenize(query);

  const corpus = memes.map((m) =>
    tokenize([m.name, m.dialogue, m.explanation, ...m.keywords].join(" "))
  );
  const idf = buildIdf(corpus);
  const queryVec = buildTfIdfVector(queryTokens, idf, DIM);

  const embeddings = loadEmbeddings();

  for (let i = 0; i < memes.length; i++) {
    const meme = memes[i];
    let score = 0;

    // TF-IDF cosine similarity
    const memeVec = buildTfIdfVector(corpus[i], idf, DIM);
    score += cosineSimilarity(queryVec, memeVec) * 0.4;

    // Keyword overlap (BM25-lite)
    const memeTerms = new Set(corpus[i]);
    let overlap = 0;
    for (const qt of queryTokens) {
      if (memeTerms.has(qt)) overlap++;
      for (const kw of meme.keywords) {
        if (qt.includes(kw.toLowerCase()) || kw.toLowerCase().includes(qt)) {
          overlap += 0.5;
        }
      }
    }
    score += (overlap / Math.max(queryTokens.length, 1)) * 0.35;

    // Precomputed sentence-transformer embeddings (when available)
    if (embeddings?.has(meme.id)) {
      const stored = embeddings.get(meme.id)!;
      // Approximate query embedding by averaging nearest keyword-matched meme vectors
      // For proper query embedding, run scripts/generate_embeddings.py with --query mode
      // Here we boost memes whose stored vectors align with TF-IDF proxy
      const proxySim = cosineSimilarity(queryVec.slice(0, stored.length), stored);
      score += proxySim * 0.25;
    }

    scores.set(meme.id, Math.min(score, 1));
  }

  return scores;
}

export function getTopSemanticMatches(
  query: string,
  memes: MemeRecord[],
  limit: number
): { id: string; score: number }[] {
  const scores = semanticSearch(query, memes, limit);
  return [...scores.entries()]
    .map(([id, score]) => ({ id, score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
