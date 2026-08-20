"""Chat Refinement API Router for MemeGPT — Multi-turn conversational meme search.
Specification: 08_Features/Chat_Refinement.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import AuthContext, optional_auth
from app.services.chat_refinement_service import (
    search_with_context,
    get_session_history,
    clear_session_history,
    parse_refinement_command,
)

logger = logging.getLogger("memegpt.api.chat")
router = APIRouter(prefix="/chat", tags=["Chat Refinement"])


class ChatRefinementRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User prompt or refinement command")
    session_id: str = Field(default="default_session", description="Conversation session identifier")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional client-managed history")
    format_preference: Optional[str] = Field(default=None, description="Format preference (gif, image, video, webp)")
    limit: int = Field(default=5, ge=1, le=20, description="Max results to return")


@router.post("/refine", summary="Multi-turn conversational search and refinement")
def refine_search(
    body: ChatRefinementRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(optional_auth),
):
    """Executes conversational search turn with multi-turn context (last 3 turns)."""
    return search_with_context(
        query=body.query,
        session_id=body.session_id,
        conversation_history=body.conversation_history,
        format_preference=body.format_preference,
        limit=body.limit,
        db=db,
    )


@router.post("/search", summary="Alias for conversational search turn")
def chat_search(
    body: ChatRefinementRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(optional_auth),
):
    """Alias for /chat/refine supporting conversational search."""
    return refine_search(body=body, db=db, auth=auth)


@router.get("/sessions/{session_id}", summary="Get conversation history for a session")
def get_session(session_id: str):
    """Retrieve all turns in conversation history for the given session ID."""
    history = get_session_history(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "turns_count": len(history),
        "history": history,
    }


@router.delete("/sessions/{session_id}", summary="Reset and clear session history")
def reset_session(session_id: str):
    """Clear conversation history and reset search context for a session."""
    cleared = clear_session_history(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "cleared": cleared,
        "message": "Session context reset successfully",
    }
