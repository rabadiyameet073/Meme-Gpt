# MemeGPT — Input Validation Security

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete input validation and sanitization strategy — preventing XSS, injection attacks, and malicious input across all API endpoints.

---

## Attack Vectors and Defenses

| Attack | Vector | Defense |
|---|---|---|
| **SQL Injection** | Malicious query string | Prisma ORM (parameterized queries) |
| **XSS (Cross-Site Scripting)** | Script tags in query | HTML stripping + React auto-escaping |
| **Prompt Injection** | LLM manipulation | Structured JSON output parsing only |
| **ReDoS** | Pathological regex | No user-controlled regex patterns |
| **Buffer Overflow** | Extremely long input | `max_length=2000` Pydantic validation |
| **SSRF** | Malicious URLs in input | No URL fetching from user input |

---

## Pydantic Validation (First Line of Defense)

```python
class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,     # No empty strings
        max_length=2000,  # Prevent memory exhaustion
    )
    format_preference: str = Field(
        default="gif",
        pattern="^(gif|image|video|any)$"  # Strict enum
    )
    limit: int = Field(default=5, ge=1, le=20)  # Bounded integer
    nsfw: bool = Field(default=False)             # Boolean only
```

---

## HTML Sanitization

```python
import re

def sanitize_input(text: str) -> str:
    """Remove HTML/script tags from user input."""
    text = re.sub(r'<[^>]+>', '', text)          # Strip HTML tags
    text = re.sub(r'javascript:', '', text, flags=re.I)  # Remove JS protocol
    text = text.replace('\x00', '')               # Remove null bytes
    return text.strip()
```

---

## Prompt Injection Defense

```python
# The LLM output is ALWAYS parsed as JSON — never executed
response = groq_client.chat.completions.create(...)
try:
    intent = json.loads(response.choices[0].message.content)
    # Validate expected structure
    assert "emotion" in intent
    assert isinstance(intent.get("keywords"), list)
except (json.JSONDecodeError, AssertionError):
    intent = {"emotion": "neutral", "keywords": []}  # Safe fallback
```

> **Key principle:** LLM output is data, never code. It's JSON-parsed and schema-validated, making prompt injection harmless.

---

## Best Practices

1. **Validate at the Pydantic layer** — reject bad input before it reaches business logic
2. **Never use raw SQL** — always use Prisma ORM with parameterized queries
3. **Strip HTML from all text inputs** — prevent XSS via stored content
4. **Parse LLM output as JSON only** — never `eval()` or `exec()` LLM responses
5. **Bound all numeric inputs** — `ge=1, le=20` prevents absurd values
6. **Log validation failures** — track attack attempts for security monitoring

---

> **Related Documents:**
> - [Security_Overview.md](./Security_Overview.md) — Security architecture
> - [Rate_Limiting_Security.md](./Rate_Limiting_Security.md) — DDoS protection
> - [03_Backend/Error_Handling.md](../03_Backend/Error_Handling.md) — Error responses
