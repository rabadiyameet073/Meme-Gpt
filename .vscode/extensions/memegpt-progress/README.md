# MemeGPT Progress Tracker — VS Code Extension

Shows **contextual completion/quality percentages** on every file and folder in the VS Code explorer.

## What It Does

Each file gets a percentage badge and color indicator based on its domain:

| File Domain | What % Measures |
|---|---|
| Test files (`test_*.py`) | Test pass rate (from actual pytest results) |
| API routes (`api/v1/*.py`) | Route implementation quality (validation, auth, error handling) |
| Services (`*_service.py`) | Service quality (error handling, logging, types, docs) |
| Models (`models/*.py`) | Schema completeness (columns, relationships, validators) |
| Components (`*.tsx`) | Component quality (props, a11y, loading states, memoization) |
| Hooks (`use*.ts`) | Hook implementation quality |
| Scripts (`scripts/*.py`) | Script completeness (main guard, args, error handling) |
| Config files | Configuration coverage vs expected keys |
| CI/CD workflows | Pipeline coverage (jobs, caching, tests, deploy) |
| Docker files | Docker best practices (multi-stage, health check, non-root) |
| Documentation (`.md`) | Content quality (sections, code examples, diagrams, tables) |
| Data files (`.json`) | Data population vs expected thresholds |

### Color Coding

| Badge Color | Range | Meaning |
|---|---|---|
| 🟩 Green | 90-100% | Excellent |
| 🟨 Yellow | 70-89% | Good |
| 🟧 Orange | 50-69% | Needs Work |
| 🟥 Red | 0-49% | Critical |

### Folder Percentages

Folders show the **average** of their children's percentages.

## Installation

The extension is auto-installed to your VS Code extensions directory. To reinstall:

```powershell
# From the project root
$dest = "$env:USERPROFILE\.vscode\extensions\memegpt.memegpt-progress-tracker-0.1.0"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force ".vscode\extensions\memegpt-progress" $dest
```

Then **reload VS Code** (Ctrl+Shift+P → "Developer: Reload Window").

## Commands

| Command | Description |
|---|---|
| `MemeGPT: Refresh Progress Percentages` | Re-analyze all files and update badges |
| `MemeGPT: Run Tests & Update Progress` | Run pytest and refresh test pass rates |

## Configuration

In `.vscode/settings.json`:

```json
{
  "memegpt-progress.enabled": true,
  "memegpt-progress.autoRefresh": true,
  "memegpt-progress.refreshOnSave": true
}
```

## Updating After Code Changes

1. Edit files in `.vscode/extensions/memegpt-progress/`
2. Re-run the install command above
3. Reload VS Code
