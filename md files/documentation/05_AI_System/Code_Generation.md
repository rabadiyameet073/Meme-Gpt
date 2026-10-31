# MemeGPT — Code Generation (AI System Context)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Documents how AI-generated code is used within MemeGPT — LLM-generated blog content, auto-generated SEO metadata, Groq-generated meme tags, and automated test data generation. MemeGPT does **not** offer code generation as a user feature, but uses AI code/text generation internally.

---

## AI Generation Use Cases

| Use Case | Model | Output | Frequency |
|---|---|---|---|
| Meme tag generation | Groq Llama 3.1 8B | JSON tags, emotions, situations | Indexing (offline) |
| SEO blog posts | Groq Llama 3.1 8B | Markdown blog content | Weekly (cron) |
| Alt text generation | BLIP + Groq | Image alt descriptions | Indexing (offline) |
| Test data generation | Groq / local | Mock meme datasets | Development |
| Meme metadata enrichment | Groq | Enhanced descriptions | Indexing (offline) |

---

## Meme Tag Generation (Primary)

```python
def generate_meme_tags(meme_name: str, ocr_text: str, caption: str) -> dict:
    """Use Groq LLM to generate rich tags for a meme."""
    prompt = f"""Analyze this meme and return ONLY valid JSON:
    
Meme name: {meme_name}
Text in image: {ocr_text}
Visual description: {caption}

Return:
{{
  "emotions": ["list of 2-4 emotions this meme expresses"],
  "situations": ["3-5 situations where you'd send this meme"],
  "keywords": ["10 search keywords people would use to find this"],
  "tone": "sarcastic|sincere|humorous|frustrated|excited|relatable",
  "meme_type": "reaction|comparison|advice|relatable|wholesome",
  "alt_text": "Accessible description for screen readers"
}}"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )
    return json.loads(response.choices[0].message.content)
```

---

## SEO Blog Post Generation

```python
def generate_weekly_blog_post(topic: str, memes: list) -> str:
    prompt = f"""Write an SEO-optimized blog post:
Title: "Top 20 {topic} Memes of This Week"

Include:
- 300-word intro (natural, conversational)
- 20 meme sections with: name, why it's funny, when to use it
- Conclusion with CTA to try MemeGPT

Target keyword: "{topic.lower()} memes"
Tone: funny, relatable, internet-native"""

    return groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    ).choices[0].message.content
```

---

## Best Practices

1. **Always parse LLM output as JSON** — wrap in try/except, validate schema
2. **Set temperature low (0.1–0.2) for structured output** — consistency matters
3. **Set temperature higher (0.7) for creative content** — blog posts, descriptions
4. **Validate generated tags** — check emotion values against known enum
5. **Cache generated tags** — never re-generate for the same meme
6. **Human review for published content** — auto-generated blogs need editorial review

---

> **Related Documents:**
> - [LLM_Workflow.md](./LLM_Workflow.md) — Groq API integration
> - [Prompt_Engineering.md](./Prompt_Engineering.md) — Prompt design
> - [AI_Pipeline.md](./AI_Pipeline.md) — Full pipeline
