# MemeGPT — Prompt Engineering

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete documentation of all LLM prompts used in MemeGPT — intent parsing, tag generation, blog content, and prompt design principles.

---

## Prompt Inventory

| Prompt | Model | When Used | Temperature | Max Tokens |
|---|---|---|---|---|
| Intent parsing | Groq Llama 3.1 8B | Every search (online) | 0.1 | 200 |
| Meme tag generation | Groq Llama 3.1 8B | Indexing (offline) | 0.2 | 300 |
| Alt text generation | Groq Llama 3.1 8B | Indexing (offline) | 0.3 | 100 |
| Blog post generation | Groq Llama 3.1 8B | Weekly cron | 0.7 | 2000 |

---

## Prompt 1: Intent Parsing (Online)

```python
INTENT_PROMPT = """You are a meme recommendation engine. Analyze the user's text and extract structured intent.

User text: "{user_text}"

Return ONLY valid JSON with these fields:
{{
  "emotion": "joy|sadness|anger|surprise|fear|disgust|neutral",
  "situation": "brief description of what's happening",
  "tone": "sarcastic|sincere|humorous|frustrated|excited|resigned",
  "keywords": ["5-8 search keywords for finding relevant memes"],
  "meme_format": "reaction|comparison|advice|relatable|wholesome"
}}

Rules:
- Return ONLY JSON, no markdown, no explanation
- Keywords should include synonyms and related concepts
- Emotion should be the dominant feeling
- Meme_format describes the type of meme that would fit best"""
```

### Design Decisions

| Decision | Reasoning |
|---|---|
| "Return ONLY valid JSON" | Prevents LLM from adding explanations |
| Enum values in prompt | Constrains output to valid values |
| 5-8 keywords | Enough for rich query building, not too many |
| Temperature 0.1 | Consistent, deterministic output |

---

## Prompt 2: Meme Tag Generation (Offline)

```python
TAG_PROMPT = """Analyze this meme and return ONLY valid JSON:

Meme name: {meme_name}
Text in image: {ocr_text}
Visual description: {caption}

Return:
{{
  "emotions": ["2-4 emotions this meme expresses"],
  "situations": ["3-5 situations where you'd send this meme"],
  "keywords": ["10 search keywords people would use to find this"],
  "tone": "sarcastic|sincere|humorous|frustrated|excited|relatable",
  "meme_type": "reaction|comparison|advice|relatable|wholesome",
  "alt_text": "Accessible image description for screen readers"
}}"""
```

---

## Prompt Design Principles

1. **Structured output only** — always request JSON, never free-form text
2. **Constrain with enums** — list valid values in the prompt
3. **Explicit format instructions** — "Return ONLY valid JSON, no markdown"
4. **Provide context** — give the LLM all relevant data (name + OCR + caption)
5. **Low temperature for structure** — 0.1-0.2 for JSON, 0.7 for creative content
6. **Validate output programmatically** — never trust LLM output without parsing

---

## Common Failure Modes

| Failure | Frequency | Mitigation |
|---|---|---|
| Markdown-wrapped JSON | ~5% | Strip \`\`\`json markers before parsing |
| Extra explanation text | ~3% | Extract first JSON block with regex |
| Missing required fields | ~2% | Merge with defaults |
| Invalid emotion value | ~1% | Map to nearest valid enum |
| Complete gibberish | <0.5% | Use fallback defaults entirely |

---

> **Related Documents:**
> - [LLM_Workflow.md](./LLM_Workflow.md) — Groq API integration
> - [AI_Pipeline.md](./AI_Pipeline.md) — Full pipeline
> - [Code_Generation.md](./Code_Generation.md) — Content generation
