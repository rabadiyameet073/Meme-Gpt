"""Development API Router for MemeGPT.
Specification: 09_Development/Code_Review.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.code_review_service import (
    get_code_review_checklist,
    evaluate_code_compliance,
)
from app.services.coding_standards_service import (
    get_coding_standards_spec,
    get_linter_configurations,
    validate_source_code_standards,
)
from app.services.contributing_service import (
    get_contributing_guide,
    validate_contribution_pr,
)
from app.services.debugging_service import (
    get_debugging_matrix,
    get_quick_debug_commands,
    get_debugging_best_practices,
    diagnose_issue,
)
from app.services.development_workflow_service import (
    get_daily_workflow_overview,
    get_pre_commit_checklist_items,
    verify_pre_commit_status,
)
from app.services.git_workflow_service import (
    get_git_branch_strategy,
    get_conventional_commit_types,
    get_pr_lifecycle_steps,
    get_pr_template_markdown,
    parse_and_validate_commit,
    validate_pr_submission,
)
from app.services.dev_manifest_service import (
    get_development_section_manifest,
    verify_development_system_health,
)

logger = logging.getLogger("memegpt.api.development")
router = APIRouter(prefix="/dev", tags=["Development & Code Review"])


class CodeAuditRequest(BaseModel):
    code_snippet: str = Field(..., description="Code snippet to audit")
    filename: str = Field(default="code.py", description="Filename to infer language rules")


class StandardsValidationRequest(BaseModel):
    code_snippet: str = Field(..., description="Code snippet to validate")
    filename: str = Field(default="code.py", description="Filename to infer language rules")


class PRValidationRequest(BaseModel):
    branch_name: str = Field(..., description="Git branch name e.g. 'feat/social-cards'")
    commit_message: str = Field(..., description="Commit message e.g. 'feat(share): add opengraph tags'")
    target_branch: str = Field(default="develop", description="Target PR branch e.g. 'develop'")


class DiagnosisRequest(BaseModel):
    symptom_text: str = Field(..., description="Error message, stack trace snippet, or symptom description")


class PreCommitVerifyRequest(BaseModel):
    checks_completed: Dict[str, bool] = Field(..., description="Dictionary mapping check IDs (e.g. compiles, tests_pass, no_secrets, linter_passes, has_tests) to booleans")


class CommitValidationRequest(BaseModel):
    commit_message: str = Field(..., description="Commit message to validate against Conventional Commits")


class PRSubmissionValidationRequest(BaseModel):
    branch_name: str = Field(..., description="Git branch name e.g. 'feature/search-chips'")
    target_branch: str = Field(default="develop", description="Target branch e.g. 'develop'")
    pr_body: str = Field(..., description="PR description body markdown")


@router.get("/code-review/checklist", summary="Get 6-pillar code review checklist")
def get_checklist():
    """Retrieve standard code review checklist for Functionality, Quality, Performance, Security, Testing, Documentation."""
    return {
        "success": True,
        **get_code_review_checklist(),
    }


@router.post("/code-review/audit", summary="Audit code snippet against review standards")
def audit_code(body: CodeAuditRequest):
    """Scan code snippet for common review violations (raw print/console.log, hardcoded keys, typing issues, XSS)."""
    result = evaluate_code_compliance(code_snippet=body.code_snippet, filename=body.filename)
    return {
        "success": True,
        **result,
    }


@router.get("/coding-standards/spec", summary="Get coding standards specification")
def get_standards_spec():
    """Retrieve Python & TypeScript coding standards specification."""
    return {
        "success": True,
        **get_coding_standards_spec(),
    }


@router.get("/coding-standards/linters", summary="Get linter configurations (ruff & eslint)")
def get_linters():
    """Retrieve ruff and ESLint configuration dictionaries."""
    return {
        "success": True,
        "linters": get_linter_configurations(),
    }


@router.post("/coding-standards/validate", summary="Validate source code against forbidden patterns")
def validate_standards(body: StandardsValidationRequest):
    """Validate source code against forbidden patterns (eval/exec, wildcard imports, bare except, any in TS, raw SQL)."""
    res = validate_source_code_standards(code_snippet=body.code_snippet, filename=body.filename)
    return {
        "success": True,
        **res,
    }


@router.get("/contributing/guide", summary="Get contributor onboarding guide")
def get_guide():
    """Retrieve ways to contribute, 9-step first PR checklist, and code of conduct."""
    return {
        "success": True,
        **get_contributing_guide(),
    }


@router.post("/contributing/validate-pr", summary="Validate PR compliance for contributors")
def validate_pr(body: PRValidationRequest):
    """Check branch naming convention, conventional commit message format, and target branch."""
    res = validate_contribution_pr(
        branch_name=body.branch_name,
        commit_message=body.commit_message,
        target_branch=body.target_branch,
    )
    return {
        "success": True,
        **res,
    }


@router.get("/debugging/matrix", summary="Get troubleshooting matrix by service")
def get_matrix(category: Optional[str] = None):
    """Retrieve problem/diagnosis/fix troubleshooting matrix for backend, frontend, ai_pipeline, or database."""
    return {
        "success": True,
        **get_debugging_matrix(category=category),
    }


@router.get("/debugging/commands", summary="Get quick diagnostic commands")
def get_commands():
    """Retrieve quick curl and CLI debug inspection commands."""
    return {
        "success": True,
        "commands": get_quick_debug_commands(),
        "best_practices": get_debugging_best_practices(),
    }


@router.post("/debugging/diagnose", summary="Auto-diagnose error message or symptom")
def diagnose_error(body: DiagnosisRequest):
    """Match symptom or error against known failure patterns and return actionable fixes."""
    res = diagnose_issue(symptom_text=body.symptom_text)
    return {
        "success": True,
        **res,
    }


@router.get("/workflow/overview", summary="Get daily development workflow overview")
def get_workflow():
    """Retrieve daily workflow steps, local dev commands, branch strategy, and commit conventions."""
    return {
        "success": True,
        **get_daily_workflow_overview(),
    }


@router.get("/workflow/pre-commit-checklist", summary="Get pre-commit checklist")
def get_pre_commit():
    """Retrieve list of pre-commit checklist requirements."""
    return {
        "success": True,
        "checklist": get_pre_commit_checklist_items(),
    }


@router.post("/workflow/verify-pre-commit", summary="Verify pre-commit readiness")
def verify_pre_commit(body: PreCommitVerifyRequest):
    """Verify if staged changes satisfy all required pre-commit checks."""
    res = verify_pre_commit_status(checks_completed=body.checks_completed)
    return {
        "success": True,
        **res,
    }


@router.get("/git/strategy", summary="Get Git branch topology and commit conventions")
def get_git_strategy():
    """Retrieve Git branches, conventional commit types, and 8-step PR lifecycle."""
    return {
        "success": True,
        **get_git_branch_strategy(),
        "commit_types": get_conventional_commit_types(),
        "pr_lifecycle": get_pr_lifecycle_steps(),
    }


@router.get("/git/pr-template", summary="Get GitHub Pull Request template markdown")
def get_pr_template():
    """Retrieve standard GitHub PR template."""
    return {
        "success": True,
        "template": get_pr_template_markdown(),
    }


@router.post("/git/validate-commit", summary="Validate Conventional Commit message")
def validate_commit(body: CommitValidationRequest):
    """Parse and validate commit message format '<type>(<scope>): <description>'."""
    res = parse_and_validate_commit(commit_message=body.commit_message)
    return {
        "success": True,
        **res,
    }


@router.post("/git/validate-pr-submission", summary="Validate PR branch and description template")
def validate_pr_submission_endpoint(body: PRSubmissionValidationRequest):
    """Validate PR branch naming, merge target, and required description sections."""
    res = validate_pr_submission(
        branch_name=body.branch_name,
        target_branch=body.target_branch,
        pr_body=body.pr_body,
    )
    return {
        "success": True,
        **res,
    }


@router.get("/manifest", summary="Get Section 09 Development master manifest")
def get_manifest():
    """Retrieve full manifest of Section 09 development practices and standards."""
    return {
        "success": True,
        **get_development_section_manifest(),
    }


@router.get("/health", summary="Check Section 09 development system health")
def get_dev_health():
    """Perform diagnostics across all Section 09 services."""
    return {
        "success": True,
        **verify_development_system_health(),
    }





