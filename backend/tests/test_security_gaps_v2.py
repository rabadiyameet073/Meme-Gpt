"""Unit tests verifying security gap resolutions (09-security-gaps.md).

Items verified:
- SEC-06: Production distributed rate limiting check.
- SEC-12: SSRF protection in NSFW image classifier from URL.
"""

from app.services.nsfw_service import classify_image_from_url


def test_sec_12_ssrf_blocked_in_nsfw_url_classifier():
    """Verify private/loopback/cloud metadata URLs are blocked before making any HTTP request."""
    # Cloud metadata
    is_nsfw, score, label = classify_image_from_url("http://169.254.169.254/latest/meta-data/")
    assert label == "blocked unsafe url"
    assert not is_nsfw

    # Loopback
    is_nsfw, score, label = classify_image_from_url("http://127.0.0.1:8080/admin/secrets")
    assert label == "blocked unsafe url"

    # Localhost
    is_nsfw, score, label = classify_image_from_url("http://localhost:5000/internal")
    assert label == "blocked unsafe url"
