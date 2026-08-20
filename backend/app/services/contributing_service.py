"""Contributing Service for MemeGPT.
Specification: 09_Development/Contributing.md
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.contributing")

CONTRIBUTION_TYPES = [
    {"type": "bug_reports", "label": "🐛 Bug reports", "difficulty": "Easy", "impact": "High"},
    {"type": "documentation", "label": "📖 Documentation improvements", "difficulty": "Easy", "impact": "Medium"},
    {"type": "tests", "label": "🧪 Adding tests", "difficulty": "Medium", "impact": "High"},
    {"type": "features", "label": "✨ New features", "difficulty": "Medium–Hard", "impact": "High"},
    {"type": "ui_ux", "label": "🎨 UI/UX improvements", "difficulty": "Medium", "impact": "Medium"},
    {"type": "ai_models", "label": "🤖 AI model improvements", "difficulty": "Hard", "impact": "Very High"},
]

FIRST_CONTRIBUTION_STEPS = [
    {"step": 1, "action": "Fork the repository"},
    {"step": 2, "action": "Clone your fork: git clone https://github.com/YOUR_USER/memegpt.git"},
    {"step": 3, "action": "Create a branch: git checkout -b fix/my-fix"},
    {"step": 4, "action": "Follow Development Setup"},
    {"step": 5, "action": "Make your changes"},
    {"step": 6, "action": "Run tests: npm test and cd backend && python -m pytest"},
    {"step": 7, "action": "Commit: git commit -m \"fix(component): description\""},
    {"step": 8, "action": "Push: git push origin fix/my-fix"},
    {"step": 9, "action": "Open a Pull Request to develop"},
]

GOOD_FIRST_ISSUES = [
    "Add a new meme category",
    "Fix a typo in documentation",
    "Add a unit test for an untested function",
    "Improve error messages",
    "Add accessibility attributes to UI components",
]

CODE_OF_CONDUCT = [
    "Be respectful and inclusive",
    "Give constructive feedback",
    "Help new contributors feel welcome",
    "No NSFW content in code, comments, or documentation",
]

VALID_BRANCH_PREFIXES = ["feat/", "fix/", "docs/", "test/", "refactor/", "chore/", "perf/"]
CONVENTIONAL_COMMIT_REGEX = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_\-]+\))?:\s+.+$")


def get_contributing_guide() -> Dict[str, Any]:
    """Return the structured contributing guide."""
    return {
        "welcome_message": "Thank you for your interest in contributing to MemeGPT!",
        "ways_to_contribute": CONTRIBUTION_TYPES,
        "first_contribution_checklist": FIRST_CONTRIBUTION_STEPS,
        "good_first_issues": GOOD_FIRST_ISSUES,
        "code_of_conduct": CODE_OF_CONDUCT,
        "target_branch": "develop",
    }


def validate_contribution_pr(
    branch_name: str,
    commit_message: str,
    target_branch: str = "develop",
) -> Dict[str, Any]:
    """Validate PR metadata against contributing standards."""
    errors = []

    # Check branch name prefix
    has_valid_branch = any(branch_name.startswith(p) for p in VALID_BRANCH_PREFIXES)
    if not has_valid_branch:
        errors.append(f"Branch '{branch_name}' should start with one of: {', '.join(VALID_BRANCH_PREFIXES)}")

    # Check conventional commit message
    if not CONVENTIONAL_COMMIT_REGEX.match(commit_message.strip()):
        errors.append(f"Commit message '{commit_message}' does not follow Conventional Commits (e.g. 'fix(auth): handle token expiry')")

    # Check PR target branch
    if target_branch.lower() != "develop":
        errors.append(f"Pull Requests must target the 'develop' branch (received '{target_branch}')")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "branch_name": branch_name,
        "commit_message": commit_message,
        "target_branch": target_branch,
        "errors": errors,
        "message": "PR passes all contribution standards" if is_valid else f"Found {len(errors)} contribution validation issues",
    }
