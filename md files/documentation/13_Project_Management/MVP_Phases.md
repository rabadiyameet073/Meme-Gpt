# MemeGPT — MVP Phases (Detailed Sprint Planning)

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Sprint Breakdown

### Sprint 1 (Weeks 1–2): Backend Foundation

| Task | Status | Owner | Deliverable |
|---|---|---|---|
| FastAPI app scaffold | ✅ Done | Backend | `main.py`, `config.py` |
| Database schema (Prisma) | ✅ Done | Backend | `schema.prisma` |
| Meme seeder script | ✅ Done | Backend | `seed_memes.py` |
| Health endpoint | ✅ Done | Backend | `GET /health` |
| Search endpoint | ✅ Done | Backend | `POST /search` |
| Meme CRUD endpoints | ✅ Done | Backend | `GET /memes`, `GET /memes/{id}` |
| Rule engine scoring | ✅ Done | Backend | `rule_engine.py` |
| CORS + basic middleware | ✅ Done | Backend | Middleware stack |

### Sprint 2 (Weeks 3–4): AI Integration

| Task | Status | Owner | Deliverable |
|---|---|---|---|
| MiniLM embedding generation | ✅ Done | ML | `semantic_search.py` |
| Semantic search implementation | ✅ Done | ML | Cosine similarity search |
| Groq LLM intent parsing | ✅ Done | ML | Intent JSON extraction |
| Emotion detection | ✅ Done | ML | DistilRoBERTa pipeline |
| Combined scoring pipeline | ✅ Done | ML | `meme_matcher.py` |
| Offline indexing scripts | ✅ Done | ML | `scripts/` directory |

### Sprint 3 (Weeks 5–6): Frontend + Deploy

| Task | Status | Owner | Deliverable |
|---|---|---|---|
| React app scaffold (Vite) | ✅ Done | Frontend | Project structure |
| Search input component | ✅ Done | Frontend | `SearchInput.tsx` |
| Results grid + MemeCard | ✅ Done | Frontend | `ResultsGrid.tsx`, `MemeCard.tsx` |
| Copy/download functionality | ✅ Done | Frontend | Clipboard + download |
| Dark mode design system | ✅ Done | Frontend | CSS design tokens |
| Format selector (GIF/PNG/MP4) | ✅ Done | Frontend | `FormatSelector.tsx` |
| Vercel deployment | ✅ Done | DevOps | `memegpt.com` live |
| Render/Railway deployment | ✅ Done | DevOps | `api.memegpt.com` live |

### Sprint 4 (Weeks 7–8): Polish + Feedback

| Task | Status | Owner | Deliverable |
|---|---|---|---|
| Trending endpoint + UI | ☐ | Fullstack | `/trending` page |
| Favorites (localStorage) | ☐ | Frontend | Save/remove memes |
| Feedback voting (👍/👎) | ☐ | Fullstack | Vote UI + API |
| Loading states + skeletons | ☐ | Frontend | Shimmer animations |
| Error states + fallbacks | ☐ | Frontend | Error boundaries |
| UptimeRobot monitoring | ☐ | DevOps | Health pings |
| Sentry error tracking | ☐ | DevOps | Exception capture |
| Documentation v1 | ☐ | Docs | This knowledge base |

---

## Definition of Done (DoD)

A sprint item is "Done" when:
- [ ] Code is merged to `develop`
- [ ] All tests pass (lint + build + unit)
- [ ] No critical bugs
- [ ] Code reviewed by at least 1 person
- [ ] Documentation updated if needed
- [ ] Deployed to staging and manually verified

---

> **Related Documents:**
> - [Roadmap.md](./Roadmap.md) · [00_Project_Overview/Goals.md](../00_Project_Overview/Goals.md)
