"""Chat Refinement Service for MemeGPT — Multi-turn conversational search.
Specification: 08_Features/Chat_Refinement.md
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal, Meme

logger = logging.getLogger("memegpt.services.chat_refinement")

# In-memory session store for conversation histories (session_id -> dict)
# Structure: {session_id: {"turns": [{"query": ..., "results": [...], "intent": {...}}], "last_active": float}}
_CHAT_SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_TTL_SECONDS = 3600  # 1 hour
MAX_SESSIONS = 500  # hard bound so anonymous traffic cannot exhaust memory
MAX_STORED_RESULTS = 5  # per turn; also bounds the referencable range


WORD_TO_INDEX = {
    "first": 1,
    "1st": 1,
    "one": 1,
    "1": 1,
    "second": 2,
    "2nd": 2,
    "two": 2,
    "2": 2,
    "third": 3,
    "3rd": 3,
    "three": 3,
    "3": 3,
    "fourth": 4,
    "4th": 4,
    "four": 4,
    "4": 4,
    "fifth": 5,
    "5th": 5,
    "five": 5,
    "5": 5,
}

# Matches an explicit pointer at a previous result. The first alternative needs a
# marker word so an incidental number ("3 AM", "5 minutes") is never mistaken
# for a selection.
_REFERENCE_PATTERN = re.compile(
    r"(?:(?:the|number|result|option)\s+|#)\s*(first|second|third|fourth|fifth|[1-5])\b"
    r"|\b(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th)\b"
)


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve turn history for a session."""
    session = _CHAT_SESSIONS.get(session_id)
    if not session:
        return []
    # Check TTL
    if time.time() - session.get("last_active", 0) > SESSION_TTL_SECONDS:
        del _CHAT_SESSIONS[session_id]
        return []
    return session.get("turns", [])


def add_session_turn(
    session_id: str,
    query: str,
    results: List[Dict[str, Any]],
    intent: Optional[Dict[str, Any]] = None,
) -> None:
    """Append a turn to the session history, capping at the last 10 turns."""
    now = time.time()
    if session_id not in _CHAT_SESSIONS:
        _CHAT_SESSIONS[session_id] = {"turns": [], "last_active": now}
    
    session = _CHAT_SESSIONS[session_id]
    session["last_active"] = now
    session["turns"].append({
        "query": query,
        "results": list(results or [])[:MAX_STORED_RESULTS],
        "intent": intent or {},
        "timestamp": now,
    })
    # Keep only the last 10 turns
    if len(session["turns"]) > 10:
        session["turns"] = session["turns"][-10:]


def clear_session_history(session_id: str) -> bool:
    """Clear conversation history for a given session."""
    if session_id in _CHAT_SESSIONS:
        del _CHAT_SESSIONS[session_id]
        return True
    return False


def _prune_sessions() -> None:
    """Evict expired sessions, then the oldest ones above ``MAX_SESSIONS``.

    The store is process-local and keyed by a client-controlled id; without
    pruning every abandoned conversation would live in RAM forever.
    """
    now = time.time()
    for sid in [s for s, v in _CHAT_SESSIONS.items() if now - v.get("last_active", 0) > SESSION_TTL_SECONDS]:
        _CHAT_SESSIONS.pop(sid, None)

    overflow = len(_CHAT_SESSIONS) - MAX_SESSIONS
    if overflow > 0:
        oldest = sorted(_CHAT_SESSIONS.items(), key=lambda kv: kv[1].get("last_active", 0))
        for sid, _ in oldest[:overflow]:
            _CHAT_SESSIONS.pop(sid, None)


def parse_refinement_command(query: str) -> Dict[str, Any]:
    """Parse refinement intent rules from query text matching Chat_Refinement.md specification."""
    q_lower = query.lower().strip()
    result: Dict[str, Any] = {
        "is_reset": False,
        "reference_index": None,
        "is_similar_search": False,
        "tone_shift": None,
        "emotion_shift": None,
        "format_preference": None,
    }

    # 1. Reset check: "Try something different", "reset", "start over"
    if any(phrase in q_lower for phrase in ["try something different", "reset", "start over", "clear context", "new search"]):
        result["is_reset"] = True
        return result

    # 2. Format shift: "Show me GIFs", "as a gif", "images only", "video version".
    # Word boundaries matter here: a bare substring test turns "gift" into "gif".
    if re.search(r"\bgifs?\b", q_lower):
        result["format_preference"] = "gif"
    elif re.search(r"\b(images?|jpg|jpeg|png)\b", q_lower):
        result["format_preference"] = "image"
    elif re.search(r"\b(videos?|mp4)\b", q_lower):
        result["format_preference"] = "video"
    elif re.search(r"\bwebp\b", q_lower):
        result["format_preference"] = "webp"

    # 3. Reference index: "the second one", "result #2", "more like the 3rd".
    # A reference *marker* is required — a bare "3" would otherwise make
    # "crashed at 3 AM" silently select the third previous result.
    ref_match = _REFERENCE_PATTERN.search(q_lower)
    if ref_match:
        matched_term = (ref_match.group(1) or ref_match.group(2) or "").strip()
        if matched_term in WORD_TO_INDEX:
            result["reference_index"] = WORD_TO_INDEX[matched_term]

    # 4. Similar search check: "more like the first one", "similar to #2"
    if "more like" in q_lower or "similar to" in q_lower or "like the" in q_lower:
        result["is_similar_search"] = True

    # 5. Tone refinement: "More sarcastic", "funnier", "darker", "wholesome"
    if "sarcastic" in q_lower or "sarcasm" in q_lower:
        result["tone_shift"] = "sarcastic"
    elif "funny" in q_lower or "funnier" in q_lower or "humorous" in q_lower:
        result["tone_shift"] = "humorous"
    elif "dark" in q_lower or "darker" in q_lower:
        result["tone_shift"] = "dark"
    elif "relatable" in q_lower:
        result["tone_shift"] = "relatable"

    # 6. Emotion shift: "Something sadder", "happier", "angrier", "more excited"
    if "sad" in q_lower or "sadder" in q_lower or "crying" in q_lower:
        result["emotion_shift"] = "sadness"
    elif "happy" in q_lower or "happier" in q_lower or "joy" in q_lower:
        result["emotion_shift"] = "joy"
    elif "angry" in q_lower or "angrier" in q_lower or "rage" in q_lower:
        result["emotion_shift"] = "anger"
    elif "frustrated" in q_lower or "frustration" in q_lower:
        result["emotion_shift"] = "frustration"
    elif "confused" in q_lower or "confusion" in q_lower:
        result["emotion_shift"] = "confusion"

    return result


from app.services.llm_service import _fallback_intent_parse

# Format preference → the key used by CDN ``formats`` dictionaries.
_FORMAT_KEYS = {
    "gif": "gif",
    "image": "image",
    "img": "image",
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "webp": "webp",
    "video": "mp4",
    "mp4": "mp4",
}


def parse_intent_with_context(
    enriched_query: str,
    conversation_history: List[Dict[str, Any]],
    current_query: str,
) -> Dict[str, Any]:
    """Parse intent taking into account multi-turn context and refinement commands.

    Keeps the pipeline's intent schema (keywords/categories/emotion/tone) so the
    re-ranker receives the same signals a direct ``/v1/search`` call would.
    """
    command_info = parse_refinement_command(current_query)
    base_intent = _fallback_intent_parse(enriched_query)

    return {
        "emotion": command_info["emotion_shift"] or base_intent.get("emotion", "relatable"),
        "emotion_hint": base_intent.get("emotion_hint"),
        "situation": base_intent.get("situation", current_query),
        "tone": command_info["tone_shift"] or base_intent.get("tone", "relatable"),
        "keywords": base_intent.get("keywords", []),
        "categories": base_intent.get("categories", []),
        "reference_index": command_info["reference_index"],
        "is_similar_search": command_info["is_similar_search"],
        "is_reset": command_info["is_reset"],
        "format_preference": command_info["format_preference"],
    }


def _memes_from_db(db: Session) -> List[Dict[str, Any]]:
    """Load searchable memes in the payload shape the pipeline expects."""
    memes: List[Dict[str, Any]] = []
    for row in db.query(Meme).filter(Meme.moderation_status != "removed").all():
        data = row.to_dict() if hasattr(row, "to_dict") else {"id": row.id, "name": row.name}
        data["videoRef"] = getattr(row, "video_ref", None)
        data["gifRef"] = getattr(row, "gif_ref", None)
        memes.append(data)
    return memes


def _apply_format_preference(item: Dict[str, Any], fmt_pref: Optional[str]) -> Dict[str, Any]:
    """Point ``preview_url`` at the requested format when the meme carries it."""
    formats = item.get("formats") if isinstance(item.get("formats"), dict) else {}
    key = _FORMAT_KEYS.get((fmt_pref or "").lower())

    if key and formats.get(key):
        item["preview_url"] = formats[key]
    elif not item.get("preview_url"):
        item["preview_url"] = (
            item.get("gif_url")
            or item.get("image_url")
            or item.get("thumb_url")
            or formats.get("gif")
            or formats.get("image")
            or ""
        )
    return item


def _build_turn_response(
    session_id: str,
    query: str,
    enriched_query: str,
    turn_number: int,
    intent: Dict[str, Any],
    results: List[Dict[str, Any]],
    is_reference_selection: bool,
    latency_ms: int,
    cached: bool = False,
    emotion: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Shape a turn so it is a drop-in replacement for a ``/v1/search`` payload."""
    return {
        "success": True,
        "session_id": session_id,
        "query": query,
        "enriched_query": enriched_query,
        "turn": turn_number,
        "intent_parsed": intent,
        "is_reference_selection": is_reference_selection,
        "results": results,
        "primary": results[0] if results else None,
        "topFive": results[:5],
        "alternatives": results[1:],
        "gifs": [
            url for url in (
                r.get("gif_url") or r.get("gifRef") or (r.get("formats") or {}).get("gif")
                for r in results[:5]
            ) if url
        ],
        "detectedCategories": intent.get("categories") or [],
        "detectedTags": intent.get("keywords") or [],
        "emotion": emotion or {"primary": intent.get("emotion", "neutral"), "confidence": 0.0},
        "total": len(results),
        "latencyMs": latency_ms,
        "cached": cached,
    }


async def search_with_context(
    query: str,
    session_id: str = "default_session",
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    format_preference: Optional[str] = None,
    limit: int = 5,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Multi-turn conversational search, executed by the production pipeline.

    Every retrieval turn (initial, refined or "more like this") goes through the
    same LLM-intent → emotion → embedding → vector-search → re-rank chain used by
    ``/v1/search``. The previous implementation scored memes with an ad-hoc
    keyword counter that ignored the vector index entirely, so conversational
    results were unrelated to the prompt (AUDIT-REPORT AI-2).
    """
    started = time.perf_counter()
    _prune_sessions()

    sid = (session_id or "default_session").strip()[:128] or "default_session"
    limit = max(1, min(int(limit or 5), 20))

    # 1. Resolve history
    history = (
        list(conversation_history)
        if conversation_history is not None
        else list(get_session_history(sid))
    )

    # Reset wipes the server-side context so the next turn starts clean.
    command_info = parse_refinement_command(query)
    if command_info["is_reset"]:
        clear_session_history(sid)
        history = []

    turn_number = len(history) + 1

    # 2. Build context from the previous three turns
    recent_turns = history[-3:]
    if recent_turns:
        context = " | ".join(t.get("query", "") for t in recent_turns if t.get("query"))
        enriched_query = f"{context} | Current: {query}"
    else:
        enriched_query = query

    # 3. Parse contextual intent
    intent = parse_intent_with_context(
        enriched_query=enriched_query,
        conversation_history=history,
        current_query=query,
    )

    fmt_pref = (format_preference or intent.get("format_preference") or "").lower() or None

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        previous_results = recent_turns[-1].get("results", []) if recent_turns else []

        # 4. Direct reference to a previous result ("the second one, but as a GIF")
        ref_idx = (intent.get("reference_index") or 0) - 1
        references_previous = 0 <= ref_idx < len(previous_results)
        if references_previous and not intent.get("is_similar_search"):
            results = [_apply_format_preference(dict(previous_results[ref_idx]), fmt_pref)]
            add_session_turn(sid, query, results, intent)
            return _build_turn_response(
                session_id=sid,
                query=query,
                enriched_query=enriched_query,
                turn_number=turn_number,
                intent=intent,
                results=results,
                is_reference_selection=True,
                latency_ms=max(int((time.perf_counter() - started) * 1000), 1),
            )

        # 5. Choose the text handed to the retrieval pipeline
        search_text = query
        if intent.get("is_similar_search") and references_previous:
            seed = previous_results[ref_idx]
            seed_categories = seed.get("categories") or ([seed.get("category")] if seed.get("category") else [])
            search_text = " ".join(
                part for part in (
                    str(seed.get("name") or ""),
                    " ".join(str(c) for c in seed_categories if c),
                    str(intent.get("emotion") or ""),
                ) if part
            ).strip() or query
        elif recent_turns:
            search_text = enriched_query

        # Explicit refinement commands bias retrieval, and because the bias is
        # part of the text it reaches intent parsing, emotion detection, the
        # embedding and the re-ranker alike.
        if command_info["emotion_shift"]:
            search_text = f"{search_text} feeling {command_info['emotion_shift']}"
        if command_info["tone_shift"]:
            search_text = f"{search_text} {command_info['tone_shift']} tone"

        # 6. Execute the production pipeline (live media off: chat must stay fast)
        from app.services.recommendation_service import recommend

        payload = await recommend(
            user_text=search_text,
            format_pref=fmt_pref or "gif",
            session_id=sid,
            memes_from_db=_memes_from_db(db),
            include_live_media=False,
        )

        results: List[Dict[str, Any]] = []
        for rank, item in enumerate((payload.get("results") or payload.get("topFive") or [])[:limit], 1):
            entry = _apply_format_preference(dict(item), fmt_pref)
            entry["relevance_score"] = round(float(entry.get("confidence") or 0.0), 3)
            entry["rank"] = rank
            results.append(entry)

        add_session_turn(sid, query, results, intent)

        return _build_turn_response(
            session_id=sid,
            query=query,
            enriched_query=enriched_query,
            turn_number=turn_number,
            intent={**intent, "retrieval_text": search_text},
            results=results,
            is_reference_selection=False,
            latency_ms=max(int((time.perf_counter() - started) * 1000), 1),
            cached=bool(payload.get("cached")),
            emotion=payload.get("emotion"),
        )

    finally:
        if close_db:
            db.close()
