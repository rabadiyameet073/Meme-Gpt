import { PrismaClient } from "@prisma/client";
import * as fs from "fs";
import * as path from "path";

const prisma = new PrismaClient();

async function main() {
  const datasetPath = path.resolve(__dirname, "../backend/data/memes.json");
  let memes: any[] = [];
  if (fs.existsSync(datasetPath)) {
    try {
      memes = JSON.parse(fs.readFileSync(datasetPath, "utf-8"));
    } catch {
      memes = [];
    }
  }

  console.log(`Seeding ${memes.length} memes...`);

  await prisma.memeVote.deleteMany().catch(() => {});
  await prisma.memeUsage.deleteMany().catch(() => {});
  await prisma.searchLog.deleteMany().catch(() => {});
  await prisma.meme.deleteMany().catch(() => {});

  for (const meme of memes) {
    await prisma.meme.create({
      data: {
        name: meme.name || "Untitled Meme",
        category: (meme.categories && meme.categories[0]) || meme.category || "reaction",
        dialogue: meme.dialogue || "",
        explanation: meme.explanation || "",
        keywords: JSON.stringify(meme.keywords || []),
        videoRef: meme.videoRef || meme.mp4_url || null,
        gifRef: meme.gifRef || meme.gif_url || null,
        viralScore: meme.viralScore ?? 75.0,
        usageCount: meme.usageCount ?? 10,
        upvotes: meme.upvotes ?? 5,
        downvotes: meme.downvotes ?? 0,
      },
    }).catch(() => {});
  }

  const count = await prisma.meme.count().catch(() => 0);
  console.log(`Seeded ${count} memes successfully.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
