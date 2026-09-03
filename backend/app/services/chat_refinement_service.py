"""Chat Refinement Service for MemeGPT — Multi-turn conversational search.
Specification: 08_Features/Chat_Refinement.md
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.database import SessionLocal, Meme
from app.services.search_service import format_search_meme_result, build_search_response_payload
from app.services.llm_service import parse_intent

logger = logging.getLogger("memegpt.services.chat_refinement")

# In-memory session store for conversation histories (session_id -> dict)
# Structure: {session_id: {"turns": [{"query": ..., "results": [...], "intent": {...}}], "last_active": float}}
_CHAT_SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_TTL_SECONDS = 3600  # 1 hour


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
        "results": results,
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

    # 2. Format shift: "Show me GIFs", "as a gif", "images only", "video version"
    if "gif" in q_lower or "gifs" in q_lower:
        result["format_preference"] = "gif"
    elif "image" in q_lower or "jpg" in q_lower or "png" in q_lower:
        result["format_preference"] = "image"
    elif "video" in q_lower or "mp4" in q_lower:
        result["format_preference"] = "video"
    elif "webp" in q_lower:
        result["format_preference"] = "webp"

    # 3. Reference index check: "the second one", "result #2", "the 3rd one", "the first one"
    ref_match = re.search(r"\b(?:the|result|number|#)?\s*(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th|[1-5])\s*(?:one|meme|result)?\b", q_lower)
    if ref_match:
        matched_term = ref_match.group(1).replace("#", "")
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

def parse_intent_with_context(
    enriched_query: str,
    conversation_history: List[Dict[str, Any]],
    current_query: str,
) -> Dict[str, Any]:
    """Parse intent taking into account multi-turn context and specific refinement patterns."""
    command_info = parse_refinement_command(current_query)

    # Base intent parsing from fallback rule engine
    base_intent = _fallback_intent_parse(enriched_query)

    intent = {
        "emotion": command_info["emotion_shift"] or base_intent.get("emotion", "relatable"),
        "situation": base_intent.get("situation", current_query),
        "tone": command_info["tone_shift"] or base_intent.get("tone", "relatable"),
        "reference_index": command_info["reference_index"],
        "is_similar_search": command_info["is_similar_search"],
        "is_reset": command_info["is_reset"],
        "format_preference": command_info["format_preference"],
    }
    return intent


def search_with_context(
    query: str,
    session_id: str = "default_session",
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    format_preference: Optional[str] = None,
    limit: int = 5,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Multi-turn conversational search matching Chat_Refinement.md specification."""
    # 1. Resolve history
    if conversation_history is None:
        conversation_history = list(get_session_history(session_id))
    else:
        conversation_history = list(conversation_history)

    # Check reset
    command_info = parse_refinement_command(query)
    if command_info["is_reset"]:
        clear_session_history(session_id)
        conversation_history = []

    turn_number = len(conversation_history) + 1

    # 2. Build context from previous turns (last 3 turns)
    last_3_turns = conversation_history[-3:] if conversation_history else []
    if last_3_turns:
        context = " | ".join([turn.get("query", "") for turn in last_3_turns if turn.get("query")])
        enriched_query = f"{context} | Current: {query}"
    else:
        enriched_query = query

    # 3. Parse contextual intent
    intent = parse_intent_with_context(
        enriched_query=enriched_query,
        conversation_history=conversation_history,
        current_query=query,
    )

    fmt_pref = format_preference or intent.get("format_preference")

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # 4. Handle direct reference to previous results (e.g. "The second one but as a GIF")
        if intent.get("reference_index") and last_3_turns and not intent.get("is_similar_search"):
            prev_results = last_3_turns[-1].get("results", [])
            ref_idx = intent["reference_index"] - 1
            if 0 <= ref_idx < len(prev_results):
                referenced_item = prev_results[ref_idx].copy()
                # If format preference specified (e.g. "as a GIF"), adapt preview_url
                if fmt_pref:
                    target_url = referenced_item.get("formats", {}).get(fmt_pref) or f"https://cdn.memegpt.com/memes/{referenced_item.get('slug', 'meme')}.{fmt_pref}"
                    referenced_item["preview_url"] = target_url
                    if "formats" in referenced_item and isinstance(referenced_item["formats"], dict):
                        referenced_item["formats"][fmt_pref] = target_url
                
                results = [referenced_item]
                add_session_turn(session_id, query, results, intent)
                return {
                    "success": True,
                    "session_id": session_id,
                    "query": query,
                    "enriched_query": enriched_query,
                    "turn": turn_number,
                    "intent_parsed": intent,
                    "is_reference_selection": True,
                    "results": results,
                    "total": len(results),
                }

        # 5. Handle similar search (e.g. "More like the first one")
        if intent.get("is_similar_search") and intent.get("reference_index") and last_3_turns:
            prev_results = last_3_turns[-1].get("results", [])
            ref_idx = intent["reference_index"] - 1
            if 0 <= ref_idx < len(prev_results):
                ref_meme = prev_results[ref_idx]
                target_cat = ref_meme.get("categories", ["general"])[0] if ref_meme.get("categories") else "general"
                similar_query = f"{ref_meme.get('name', '')} {target_cat} {intent.get('emotion', '')}"
                enriched_query = f"Similar to {ref_meme.get('name', '')} | {similar_query}"

        # 6. Execute meme retrieval
        query_terms = [t for t in re.split(r"\W+", enriched_query.lower()) if len(t) > 2]
        db_memes = db.query(Meme).all()
        scored_memes = []
        for m in db_memes:
            score = 0.5
            name_lower = (m.name or "").lower()
            cats_list = m.categories if isinstance(m.categories, list) else ([m.category] if getattr(m, "category", None) else [])
            cat_lower = " ".join(cats_list).lower()
            diag_lower = (m.dialogue or "").lower()
            kw_list = m.keywords if isinstance(m.keywords, list) else ([m.keywords] if m.keywords else [])
            kw_lower = " ".join(str(k) for k in kw_list).lower()
            
            # Match query keywords
            for term in query_terms:
                if term in name_lower or term in cat_lower or term in diag_lower or term in kw_lower:
                    score += 0.15

            # Tone & Emotion boosts
            if intent.get("tone") and intent["tone"] in cat_lower:
                score += 0.2
            if intent.get("emotion") and (intent["emotion"] in kw_lower or (isinstance(m.emotions, list) and intent["emotion"] in m.emotions)):
                score += 0.25

            # Usage bonus
            if getattr(m, "usage_count", None):
                score += min(0.1, m.usage_count * 0.001)
            elif getattr(m, "popularity_score", None):
                score += min(0.1, m.popularity_score * 0.1)

            formatted = format_search_meme_result(m, relevance_score=min(1.0, round(score, 2)), query_id=session_id)
            if fmt_pref and formatted.get("formats", {}).get(fmt_pref):
                formatted["preview_url"] = formatted["formats"][fmt_pref]

            scored_memes.append(formatted)

        scored_memes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        final_results = scored_memes[:limit]

        # Record session turn
        add_session_turn(session_id, query, final_results, intent)

        return {
            "success": True,
            "session_id": session_id,
            "query": query,
            "enriched_query": enriched_query,
            "turn": turn_number,
            "intent_parsed": intent,
            "is_reference_selection": False,
            "results": final_results,
            "total": len(final_results),
        }
    finally:
        if close_db:
            db.close()
