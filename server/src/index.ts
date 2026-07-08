import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { apiRouter } from "./routes/api.js";

const app = express();
const PORT = process.env.PORT ?? 3001;

app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({ origin: ["http://localhost:5173", "http://127.0.0.1:5173"] }));
app.use(express.json({ limit: "16kb" }));

const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60,
  message: { error: "Too many requests. Please wait a minute." },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use("/api", limiter, apiRouter);

app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(PORT, () => {
  console.log(`MemeGPT API running at http://localhost:${PORT}`);
});
