import { Router, type Request, type Response, type NextFunction } from "express";
import { z } from "zod";
import { prisma } from "../lib/database/prisma.js";
import { sanitizeInput, isValidInput } from "../lib/sanitize.js";
import { matchMemes, buildExplanation } from "../lib/meme-matcher.js";
import { exportAsTxt, exportAsJson, exportAsMarkdown } from "../lib/export.js";
import type { MemeRecord } from "../lib/types.js";

export const apiRouter = Router();

function parseMeme(m: {
  id: string;
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  keywords: string;
  videoRef: string | null;
  gifRef: string | null;
  viralScore: number;
  usageCount: number;
  upvotes: number;
  downvotes: number;
}): MemeRecord {
  return {
    id: m.id,
    name: m.name,
    category: m.category,
    dialogue: m.dialogue,
    explanation: m.explanation,
    keywords: JSON.parse(m.keywords) as string[],
    videoRef: m.videoRef,
    gifRef: m.gifRef,
    viralScore: m.viralScore,
    usageCount: m.usageCount,
    upvotes: m.upvotes,
    downvotes: m.downvotes,
  };
}

async function getAllMemes(): Promise<MemeRecord[]> {
  const memes = await prisma.meme.findMany();
  return memes.map(parseMeme);
}

const analyzeSchema = z.object({
  query: z.string().min(3).max(2000),
  sessionId: z.string().optional(),
});

apiRouter.post("/analyze", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const parsed = analyzeSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Invalid input", details: parsed.error.flatten() });
      return;
    }

    const query = sanitizeInput(parsed.data.query);
    if (!isValidInput(query)) {
      res.status(400).json({ error: "Query must be 3-2000 characters" });
      return;
    }

    const memes = await getAllMemes();
    if (memes.length === 0) {
      res.status(503).json({ error: "Meme database empty. Run npm run db:setup" });
      return;
    }

    const result = matchMemes(query, memes);

    await prisma.meme.update({
      where: { id: result.primary.id },
      data: { usageCount: { increment: 1 } },
    });

    await prisma.memeUsage.create({
      data: {
        memeId: result.primary.id,
        query,
        score: result.primary.confidence,
      },
    });

    await prisma.searchLog.create({
      data: {
        query,
        resultCount: result.topFive.length,
        latencyMs: result.latencyMs,
      },
    });

    res.json({
      ...result,
      primary: {
        ...result.primary,
        explanation: buildExplanation(query, result.primary),
      },
    });
  } catch (err) {
    next(err);
  }
});

apiRouter.get("/memes", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { q, category, limit = "20" } = req.query;
    const take = Math.min(parseInt(String(limit), 10) || 20, 100);

    const where: Record<string, unknown> = {};
    if (category && typeof category === "string") {
      where.category = category;
    }

    let memes = await prisma.meme.findMany({
      where,
      take: category || !q ? take : undefined,
      orderBy: [{ usageCount: "desc" }, { viralScore: "desc" }],
    });

    if (q && typeof q === "string") {
      const search = sanitizeInput(q).toLowerCase();
      memes = memes.filter((m) => {
        const kws = JSON.parse(m.keywords) as string[];
        return (
          m.name.toLowerCase().includes(search) ||
          m.dialogue.toLowerCase().includes(search) ||
          m.category.toLowerCase().includes(search) ||
          kws.some((k) => k.toLowerCase().includes(search))
        );
      });
      memes = memes.slice(0, take);
    }

    res.json(memes.map(parseMeme));
  } catch (err) {
    next(err);
  }
});

apiRouter.get("/trending", async (_req: Request, res: Response, next: NextFunction) => {
  try {
    const memes = await prisma.meme.findMany({
      orderBy: [{ usageCount: "desc" }, { upvotes: "desc" }],
      take: 10,
    });
    res.json(memes.map(parseMeme));
  } catch (err) {
    next(err);
  }
});

const createMemeSchema = z.object({
  name: z.string().min(1).max(200),
  category: z.string().min(1),
  dialogue: z.string().min(1).max(500),
  explanation: z.string().min(1).max(1000),
  keywords: z.array(z.string()).min(1),
  videoRef: z.string().optional(),
  gifRef: z.string().optional(),
});

apiRouter.post("/admin/memes", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const parsed = createMemeSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Invalid meme data", details: parsed.error.flatten() });
      return;
    }

    const data = parsed.data;
    const meme = await prisma.meme.create({
      data: {
        name: sanitizeInput(data.name),
        category: data.category,
        dialogue: sanitizeInput(data.dialogue),
        explanation: sanitizeInput(data.explanation),
        keywords: JSON.stringify(data.keywords.map(sanitizeInput)),
        videoRef: data.videoRef ?? null,
        gifRef: data.gifRef ?? null,
      },
    });

    res.status(201).json(parseMeme(meme));
  } catch (err) {
    next(err);
  }
});

apiRouter.delete("/admin/memes/:id", async (req: Request, res: Response, next: NextFunction) => {
  try {
    await prisma.meme.delete({ where: { id: req.params.id } });
    res.json({ success: true });
  } catch (err) {
    next(err);
  }
});

const voteSchema = z.object({
  memeId: z.string(),
  vote: z.union([z.literal(1), z.literal(-1)]),
  sessionId: z.string().min(1),
});

apiRouter.post("/vote", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const parsed = voteSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Invalid vote" });
      return;
    }

    const { memeId, vote, sessionId } = parsed.data;

    const existing = await prisma.memeVote.findUnique({
      where: { memeId_sessionId: { memeId, sessionId } },
    });

    if (existing) {
      if (existing.vote !== vote) {
        await prisma.$transaction([
          prisma.memeVote.update({
            where: { id: existing.id },
            data: { vote },
          }),
          prisma.meme.update({
            where: { id: memeId },
            data: {
              upvotes: { increment: vote === 1 ? 1 : -1 },
              downvotes: { increment: vote === -1 ? 1 : -1 },
            },
          }),
        ]);
      }
    } else {
      await prisma.$transaction([
        prisma.memeVote.create({ data: { memeId, vote, sessionId } }),
        prisma.meme.update({
          where: { id: memeId },
          data: {
            upvotes: vote === 1 ? { increment: 1 } : undefined,
            downvotes: vote === -1 ? { increment: 1 } : undefined,
          },
        }),
      ]);
    }

    res.json({ success: true });
  } catch (err) {
    next(err);
  }
});

apiRouter.post("/export", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { query, format, result } = req.body as {
      query: string;
      format: "txt" | "json" | "markdown";
      result: Parameters<typeof exportAsTxt>[0];
    };

    if (!query || !format || !result) {
      res.status(400).json({ error: "Missing query, format, or result" });
      return;
    }

    let content: string;
    let contentType: string;

    switch (format) {
      case "txt":
        content = exportAsTxt(result, query);
        contentType = "text/plain";
        break;
      case "markdown":
        content = exportAsMarkdown(result, query);
        contentType = "text/markdown";
        break;
      case "json":
        content = exportAsJson(result, query);
        contentType = "application/json";
        break;
      default:
        res.status(400).json({ error: "Invalid format" });
        return;
    }

    res.json({ content, contentType, filename: `memegpt-result.${format === "markdown" ? "md" : format}` });
  } catch (err) {
    next(err);
  }
});

apiRouter.get("/categories", (_req: Request, res: Response) => {
  res.json([
    "coding", "startup", "relationship", "college", "office", "funny",
    "motivation", "unrealistic_goals", "ai", "business", "exam", "failure",
    "success", "gaming", "bollywood", "youtube",
  ]);
});

apiRouter.get("/health", async (_req: Request, res: Response) => {
  const count = await prisma.meme.count();
  res.json({ status: "ok", memeCount: count });
});
