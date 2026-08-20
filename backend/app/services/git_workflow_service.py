"""Git Workflow Service for MemeGPT.
Specification: 09_Development/Git_Workflow.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.git_workflow")

GIT_BRANCHES = [
    {"branch": "main", "purpose": "Production-ready code", "deploys_to": "Production (auto)", "merge_target": "—"},
    {"branch": "develop", "purpose": "Integration branch", "deploys_to": "Staging", "merge_target": "→ main"},
    {"branch": "feature/*", "purpose": "Feature development", "deploys_to": "None", "merge_target": "→ develop"},
    {"branch": "fix/*", "purpose": "Bug fixes", "deploys_to": "None", "merge_target": "→ develop"},
    {"branch": "hotfix/*", "purpose": "Critical production fixes", "deploys_to": "Production (fast-track)", "merge_target": "→ main + develop"},
]

CONVENTIONAL_COMMIT_TYPES = [
    {"type": "feat", "when": "New feature", "example": "feat(search): add emotion filtering"},
    {"type": "fix", "when": "Bug fix", "example": "fix(api): handle Groq timeout"},
    {"type": "docs", "when": "Documentation", "example": "docs(readme): update install steps"},
    {"type": "style", "when": "Formatting (no logic change)", "example": "style(card): fix alignment"},
    {"type": "refactor", "when": "Code restructure (no behavior change)", "example": "refactor(backend): extract scoring"},
    {"type": "test", "when": "Add/update tests", "example": "test(api): add search integration"},
    {"type": "chore", "when": "Tooling, deps, config", "example": "chore(deps): update transformers"},
    {"type": "perf", "when": "Performance improvement", "example": "perf(search): add Redis caching"},
    {"type": "ci", "when": "CI/CD changes", "example": "ci: add deploy workflow"},
]

PR_LIFECYCLE_STEPS = [
    {"step": 1, "action": "Branch from develop", "command": "git checkout -b feature/my-feature"},
    {"step": 2, "action": "Develop with atomic commits", "command": "git commit -m \"feat(scope): msg\""},
    {"step": 3, "action": "Push to remote", "command": "git push origin feature/my-feature"},
    {"step": 4, "action": "Open PR targeting develop", "command": "Include description, screenshots, test plan"},
    {"step": 5, "action": "CI checks pass", "command": "Lint, build, and automated tests pass in GitHub Actions"},
    {"step": 6, "action": "Code review", "command": "At least 1 approval required"},
    {"step": 7, "action": "Squash merge", "command": "Squash and merge into develop"},
    {"step": 8, "action": "Delete branch", "command": "Delete feature branch post-merge"},
]

PR_TEMPLATE_MARKDOWN = """## What
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
"""

COMMIT_PATTERN = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|test|chore|perf|ci)(?:\((?P<scope>[a-zA-Z0-9_\-]+)\))?:\s+(?P<description>.+)$"
)


def get_git_branch_strategy() -> Dict[str, Any]:
    """Return Git branch topology and strategy."""
    return {
        "branches": GIT_BRANCHES,
        "default_integration_branch": "develop",
        "production_branch": "main",
    }


def get_conventional_commit_types() -> List[Dict[str, str]]:
    """Return catalog of Conventional Commit types."""
    return CONVENTIONAL_COMMIT_TYPES


def get_pr_lifecycle_steps() -> List[Dict[str, Any]]:
    """Return 8-step PR lifecycle process."""
    return PR_LIFECYCLE_STEPS


def get_pr_template_markdown() -> str:
    """Return markdown content of GitHub PR template."""
    return PR_TEMPLATE_MARKDOWN


def parse_and_validate_commit(commit_message: str) -> Dict[str, Any]:
    """Parse and validate a commit message against Conventional Commits."""
    msg = commit_message.strip()
    match = COMMIT_PATTERN.match(msg)
    if match:
        return {
            "is_valid": True,
            "commit_message": msg,
            "type": match.group("type"),
            "scope": match.group("scope"),
            "description": match.group("description"),
            "error": None,
        }
    else:
        return {
            "is_valid": False,
            "commit_message": msg,
            "type": None,
            "scope": None,
            "description": None,
            "error": "Message does not match '<type>(<scope>): <short description>' format. Allowed types: feat, fix, docs, style, refactor, test, chore, perf, ci",
        }


def validate_pr_submission(
    branch_name: str,
    target_branch: str = "develop",
    pr_body: str = "",
) -> Dict[str, Any]:
    """Validate PR branch, target branch, and template completeness."""
    errors = []

    # Valid branch naming
    is_feature_or_fix = (
        branch_name.startswith("feature/")
        or branch_name.startswith("feat/")
        or branch_name.startswith("fix/")
        or branch_name.startswith("docs/")
    )
    is_hotfix = branch_name.startswith("hotfix/")

    if is_hotfix:
        if target_branch not in ["main", "develop"]:
            errors.append(f"Hotfix branch '{branch_name}' must target 'main' or 'develop' (got '{target_branch}')")
    elif is_feature_or_fix:
        if target_branch != "develop":
            errors.append(f"Branch '{branch_name}' must target 'develop' branch (got '{target_branch}')")
    else:
        errors.append(f"Invalid branch name '{branch_name}'. Use 'feature/*', 'fix/*', 'docs/*', or 'hotfix/*'")

    # Template completeness checks
    required_sections = ["## What", "## Why", "## How", "## Testing"]
    missing_sections = [s for s in required_sections if s not in pr_body]
    if missing_sections:
        errors.append(f"PR body missing required sections: {', '.join(missing_sections)}")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "branch_name": branch_name,
        "target_branch": target_branch,
        "missing_sections": missing_sections,
        "errors": errors,
        "message": "PR submission is fully valid" if is_valid else f"Found {len(errors)} validation errors",
    }
