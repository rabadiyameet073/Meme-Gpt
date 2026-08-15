"""MemeGPT — Error Taxonomy & Custom Exceptions.
Provides standard error definitions matching Error_Handling.md.
"""
from typing import Optional, Any, Dict, List
from fastapi import HTTPException


class MemeGPTException(HTTPException):
    """Base exception for all MemeGPT API errors."""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Any] = None,
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.error_code = error_code
        self.message = message
        self.details = details
        self.retry_after = retry_after


class InvalidRequestError(MemeGPTException):
    def __init__(self, message: str = "Invalid request format", details: Optional[Any] = None):
        super().__init__(status_code=400, error_code="invalid_request", message=message, details=details)


class QueryTooLongError(MemeGPTException):
    def __init__(self, message: str = "Query exceeds maximum limit of 2000 characters"):
        super().__init__(status_code=400, error_code="query_too_long", message=message)


class InvalidFormatError(MemeGPTException):
    def __init__(self, message: str = "Invalid format preference"):
        super().__init__(status_code=400, error_code="invalid_format", message=message)


class MemeNotFoundError(MemeGPTException):
    def __init__(self, message: str = "Meme not found"):
        super().__init__(status_code=404, error_code="meme_not_found", message=message)


class RateLimitExceededError(MemeGPTException):
    def __init__(self, retry_after: int = 60, limit: int = 60):
        headers = {"Retry-After": str(retry_after), "X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"}
        super().__init__(
            status_code=429,
            error_code="rate_limit_exceeded",
            message=f"Too many requests. Limit is {limit} requests per minute. Retry after {retry_after} seconds.",
            retry_after=retry_after,
            headers=headers
        )


class UpstreamServiceError(MemeGPTException):
    def __init__(self, message: str = "External service returned an error"):
        super().__init__(status_code=502, error_code="upstream_error", message=message)


class ServiceUnavailableError(MemeGPTException):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(status_code=503, error_code="service_unavailable", message=message)
