# MemeGPT — Git Workflow

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Branch Strategy

```mermaid
gitgraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "base setup"
    branch feature/search-ui
    checkout feature/search-ui
    commit id: "search input"
    commit id: "results grid"
    checkout develop
    merge feature/search-ui id: "PR #12"
    branch feature/trending
    checkout feature/trending
    commit id: "trending API"
    commit id: "trending UI"
    checkout develop
    merge feature/trending id: "PR #15"
    checkout main
    merge develop id: "v1.0.0 release"
```

| Branch | Purpose | Deploys To | Merge Target |
|---|---|---|---|
| `main` | Production-ready code | Production (auto) | — |
| `develop` | Integration branch | Staging | → `main` |
| `feature/*` | Feature development | None | → `develop` |
| `fix/*` | Bug fixes | None | → `develop` |
| `hotfix/*` | Critical production fixes | Production (fast-track) | → `main` + `develop` |

---

## Commit Convention (Conventional Commits)

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

### Types

| Type | When | Example |
|---|---|---|
| `feat` | New feature | `feat(search): add emotion filtering` |
| `fix` | Bug fix | `fix(api): handle Groq timeout` |
| `docs` | Documentation | `docs(readme): update install steps` |
| `style` | Formatting (no logic) | `style(card): fix alignment` |
| `refactor` | Code restructure (no behavior change) | `refactor(backend): extract scoring` |
| `test` | Add/update tests | `test(api): add search integration` |
| `chore` | Tooling, deps, config | `chore(deps): update transformers` |
| `perf` | Performance improvement | `perf(search): add Redis caching` |
| `ci` | CI/CD changes | `ci: add deploy workflow` |

---

## Pull Request Process

1. **Branch** from `develop`: `git checkout -b feature/my-feature`
2. **Develop** with atomic commits
3. **Push**: `git push origin feature/my-feature`
4. **Open PR** → `develop` with:
   - Description of changes
   - Screenshots (for UI changes)
   - Test plan
   - Link to issue
5. **CI checks pass** (lint, build, tests)
6. **Code review** (1 approval required)
7. **Squash merge** to `develop`
8. **Delete** feature branch

---

## PR Template

```markdown
## What
Brief description of what this PR does.

## Why
Why is this change needed?

## How
How was it implemented?

## Screenshots
(for UI changes)

## Testing
- [ ] Unit tests pass
- [ ] Manual testing done
- [ ] Edge cases covered
```

---

> **Related Documents:**
> - [Coding_Standards.md](./Coding_Standards.md) · [12_Deployment/Deployment_Overview.md](../12_Deployment/Deployment_Overview.md)
