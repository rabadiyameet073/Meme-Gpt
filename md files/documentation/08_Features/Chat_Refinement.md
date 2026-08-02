# MemeGPT — Chat Refinement (Phase 2)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Specification for multi-turn conversational meme search — where users can refine results by saying things like "something more sarcastic" or "show me GIFs instead."

---

## Background

Phase 1 search is single-turn: query → results. Chat refinement adds **multi-turn context** so users can progressively narrow down to the perfect meme.

---

## User Flow

```
Turn 1: "Monday morning feeling"
→ 5 results (mix of sad/frustrated memes)

Turn 2: "Something more sarcastic"
→ 5 new results (sarcastic Monday memes, re-ranked)

Turn 3: "The second one but as a GIF"
→ Shows GIF version of result #2 from Turn 2
```

---

## Implementation Strategy

```python
async def search_with_context(
    query: str,
    conversation_history: list[dict],
    session_id: str
):
    # Build context from previous turns
    context = " | ".join([
        turn["query"] for turn in conversation_history[-3:]  # Last 3 turns
    ])
    enriched_query = f"{context} | Current: {query}"
    
    # LLM understands refinement
    intent = await parse_intent_with_context(enriched_query, conversation_history)
    
    # If user references previous results ("the second one")
    if intent.get("reference_index"):
        prev_results = conversation_history[-1].get("results", [])
        referenced_meme = prev_results[intent["reference_index"] - 1]
        return [referenced_meme]  # Return specific meme
    
    # Normal search with refined intent
    return await recommend_memes(enriched_query, **intent)
```

---

## Refinement Commands

| User Says | Intent | Action |
|---|---|---|
| "More sarcastic" | Tone refinement | Re-rank with `tone: sarcastic` boost |
| "Something sadder" | Emotion shift | Change `emotion: sadness` filter |
| "Show me GIFs" | Format change | Set `format_preference: gif` |
| "The third one" | Reference | Return result #3 from previous turn |
| "More like the first one" | Similar search | Use result #1 embedding as new query |
| "Try something different" | Reset | Clear context, search from scratch |

---

## Status: Phase 2 (Planned)

**Prerequisites:**
- [ ] Session state management (Redis)
- [ ] Conversation history storage
- [ ] LLM prompt for context understanding
- [ ] Frontend chat-style UI

---

> **Related Documents:**
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) — Core search feature
> - [05_AI_System/LLM_Workflow.md](../05_AI_System/LLM_Workflow.md) — LLM integration
