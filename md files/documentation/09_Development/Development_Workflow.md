# MemeGPT — Development Workflow

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete daily development workflow — from pulling code to pushing changes, including local testing, linting, and pre-commit checks.

---

## Daily Workflow

```mermaid
flowchart TD
    A["git pull origin main"] --> B["Create feature branch<br/>git checkout -b feat/xyz"]
    B --> C["Start dev servers<br/>npm run dev (frontend)<br/>uvicorn --reload (backend)"]
    C --> D["Write code + tests"]
    D --> E["Run tests locally<br/>pytest / npm test"]
    E --> F{"Tests pass?"}
    F -->|No| D
    F -->|Yes| G["git add + commit"]
    G --> H["git push origin feat/xyz"]
    H --> I["Create Pull Request"]
    I --> J["CI runs automatically<br/>(lint + build + test)"]
    J --> K{"CI passes?"}
    K -->|No| D
    K -->|Yes| L["Merge to main"]
    L --> M["Auto-deploy to production"]
```

---

## Local Development Commands

```bash
# Terminal 1: Backend
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd apps/web
npm install
npm run dev  # → http://localhost:5173

# Terminal 3: Local services (optional)
docker-compose up -d  # Redis + Qdrant
```

---

## Branch Strategy

| Branch | Purpose | Deploys To |
|---|---|---|
| `main` | Production-ready | Auto-deploy to prod |
| `feat/*` | New features | PR → main |
| `fix/*` | Bug fixes | PR → main |
| `docs/*` | Documentation | PR → main |

---

## Commit Convention

```
feat: add suggestion chips to search
fix: handle empty query validation
docs: update API Architecture docs
perf: cache trending results for 5 minutes
test: add emotion detection unit tests
chore: update dependencies
```

---

## Pre-Commit Checklist

- [ ] Code compiles without errors
- [ ] Tests pass locally (`pytest` / `npm test`)
- [ ] No hardcoded API keys or secrets
- [ ] Linter passes (ruff for Python, ESLint for TypeScript)
- [ ] New features have tests
- [ ] Documentation updated (if API changed)

---

> **Related Documents:**
> - [Git_Workflow.md](./Git_Workflow.md) — Branch and merge strategy
> - [Coding_Standards.md](./Coding_Standards.md) — Style guidelines
> - [Code_Review.md](./Code_Review.md) — Review process
