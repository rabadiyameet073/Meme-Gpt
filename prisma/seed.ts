import { prisma } from "../server/src/lib/database/prisma.js";
import { MEME_DATASET } from "../server/data/meme-dataset.js";

async function main() {
  console.log(`Seeding ${MEME_DATASET.length} memes...`);

  await prisma.memeVote.deleteMany();
  await prisma.memeUsage.deleteMany();
  await prisma.searchLog.deleteMany();
  await prisma.meme.deleteMany();

  for (const meme of MEME_DATASET) {
    await prisma.meme.create({
      data: {
        name: meme.name,
        category: meme.category,
        dialogue: meme.dialogue,
        explanation: meme.explanation,
        keywords: JSON.stringify(meme.keywords),
        videoRef: meme.video ?? null,
        gifRef: meme.gif ?? null,
        viralScore: meme.viralScore ?? Math.random() * 100,
        usageCount: Math.floor(Math.random() * 50),
        upvotes: Math.floor(Math.random() * 100),
        downvotes: Math.floor(Math.random() * 20),
      },
    });
  }

  const count = await prisma.meme.count();
  console.log(`Seeded ${count} memes successfully.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
