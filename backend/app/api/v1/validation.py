"""Input Validation & Threat Sanitization API Router for MemeGPT.
Specification: 11_Security/Input_Validation.md
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.input_validation_service import (
    get_attack_vectors_and_defenses,
    get_validation_best_practices,
    sanitize_input,
    sanitize_search_payload,
    validate_and_parse_llm_json,
    detect_suspicious_patterns,
    evaluate_input_validation_health,
)

logger = logging.getLogger("memegpt.api.validation")
router = APIRouter(prefix="/validation", tags=["Input Validation & Threat Defense"])


class SanitizeTextRequest(BaseModel):
    text: str = Field(..., max_length=2000, description="Raw text to sanitize")


class ThreatInspectionRequest(BaseModel):
    text: str = Field(..., max_length=2000, description="Input string to inspect for attacks")


class ParseLLMJsonRequest(BaseModel):
    raw_response: str = Field(..., description="Raw text response from LLM to parse as JSON")


class SearchPayloadSanitizeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Search query string")
    format_preference: str = Field(default="gif", pattern="^(gif|image|video|any)$")
    limit: int = Field(default=5, ge=1, le=20)
    nsfw: bool = Field(default=False)


@router.get("/vectors", summary="Get 6 attack vectors and engineering defenses")
def get_vectors():
    """Retrieve the matrix of attack vectors (SQLi, XSS, Prompt Injection, ReDoS, Buffer Overflow, SSRF)."""
    return {
        "success": True,
        **get_attack_vectors_and_defenses(),
    }


@router.get("/practices", summary="Get 6 input validation best practices")
def get_practices():
    """Retrieve engineering best practices for input validation."""
    return {
        "success": True,
        **get_validation_best_practices(),
    }


@router.post("/sanitize", summary="Sanitize raw string input")
def sanitize_text_endpoint(body: SanitizeTextRequest):
    """Strip HTML tags, javascript: protocol, and null bytes from input string."""
    sanitized = sanitize_input(body.text)
    return {
        "success": True,
        "original_text": body.text,
        "sanitized_text": sanitized,
        "is_modified": sanitized != body.text,
    }


@router.post("/sanitize-payload", summary="Sanitize and bound full search payload")
def sanitize_search_payload_endpoint(body: SearchPayloadSanitizeRequest):
    """Sanitize and apply bounds to all fields of a SearchRequest."""
    res = sanitize_search_payload(
        query=body.query,
        format_pref=body.format_preference,
        limit=body.limit,
        nsfw=body.nsfw,
    )
    return {
        "success": True,
        **res,
    }


@router.post("/inspect-threats", summary="Detect attack signatures in input")
def inspect_threats_endpoint(body: ThreatInspectionRequest):
    """Inspect input for SQL injection, XSS script tags, prompt injection heuristics, and null bytes."""
    return {
        "success": True,
        **detect_suspicious_patterns(body.text),
    }


@router.post("/parse-llm-json", summary="Safe LLM JSON output parser with fallback")
def parse_llm_json_endpoint(body: ParseLLMJsonRequest):
    """Safely parse LLM output as data, never executing code and falling back on injection."""
    parsed = validate_and_parse_llm_json(body.raw_response)
    return {
        "success": True,
        **parsed,
    }


@router.get("/health", summary="Input validation system health check")
def get_validation_health():
    """Check sanitization, LLM JSON fallback, and Pydantic bounds health."""
    return {
        "success": True,
        **evaluate_input_validation_health(),
    }
