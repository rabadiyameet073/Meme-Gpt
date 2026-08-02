# MemeGPT — Coding Standards

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Code style guidelines for Python (backend) and TypeScript (frontend) — linting tools, naming conventions, file organization, and forbidden patterns.

---

## Python (Backend) Standards

### Linter: `ruff`

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E", "W", "F", "I", "N", "UP"]

[tool.ruff.isort]
known-first-party = ["app"]
```

### Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `recommendation.py` |
| Functions | `snake_case` | `recommend_memes()` |
| Classes | `PascalCase` | `SearchRequest` |
| Constants | `UPPER_SNAKE` | `MAX_QUERY_LENGTH` |
| Variables | `snake_case` | `query_embedding` |
| Private | `_prefix` | `_default_intent()` |

### Required Patterns

```python
# ✅ Always use type hints
async def recommend_memes(user_text: str, format_pref: str = "gif") -> list[dict]:
    ...

# ✅ Always use async/await for I/O
async def search(query_vector: list[float]) -> list:
    ...

# ✅ Always use Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)

# ❌ Never use bare except
try:
    result = await groq_call()
except:  # BAD — catches KeyboardInterrupt, SystemExit
    pass

# ✅ Catch specific exceptions
try:
    result = await groq_call()
except (httpx.TimeoutException, json.JSONDecodeError) as e:
    logger.warning(f"Groq failed: {e}")
```

---

## TypeScript (Frontend) Standards

### Linter: ESLint + Next.js config

```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "no-console": "warn",
    "prefer-const": "error",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

### Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Files (components) | `PascalCase.tsx` | `MemeCard.tsx` |
| Files (utils) | `camelCase.ts` | `formatScore.ts` |
| Components | `PascalCase` | `SearchInput` |
| Hooks | `useCamelCase` | `useSearch` |
| Functions | `camelCase` | `formatScore()` |
| Constants | `UPPER_SNAKE` | `API_BASE_URL` |
| Types/Interfaces | `PascalCase` | `MemeResult` |

### Required Patterns

```typescript
// ✅ Always use TypeScript interfaces
interface MemeResult {
  id: string;
  name: string;
  relevance_score: number;
}

// ✅ Always use 'use client' for interactive components
'use client'

// ✅ Always use const for components
export const MemeCard = ({ meme }: { meme: MemeResult }) => { ... }

// ❌ Never use any
const data: any = await fetch(...)  // BAD

// ✅ Use proper types
const data: SearchResponse = await fetch(...)
```

---

## Forbidden Patterns

| Pattern | Why | Alternative |
|---|---|---|
| `eval()` / `exec()` | Security risk | `json.loads()` |
| `import *` | Namespace pollution | Explicit imports |
| Bare `except:` | Catches system errors | `except Exception:` |
| `console.log` in production | Noise | Use logger |
| Hardcoded secrets | Security risk | Environment variables |
| `any` type in TypeScript | Defeats type safety | Proper interfaces |
| Raw SQL queries | Injection risk | Prisma ORM |

---

> **Related Documents:**
> - [Git_Workflow.md](./Git_Workflow.md) — Branch strategy
> - [Code_Review.md](./Code_Review.md) — Review process
> - [Contributing.md](./Contributing.md) — Contribution guidelines
