"""Chat API routes."""

import logging

from fastapi import APIRouter, Depends, Query

from auth.middleware import get_current_user
from chat.engine import generate_chat_response
from db.chat import create_chat_entry, get_chat_history, get_recent_context
from db.preferences import get_preferences
from db.interests import get_interests
from db.briefings import get_latest_briefing
from schemas.chat import (
    ChatHistoryEntry,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatSource,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    body: ChatRequest,
    user: dict = Depends(get_current_user),
) -> ChatResponse:
    """Send a chat message and get an AI response with source citations."""
    user_id = user["id"]

    # Gather context
    preferences = get_preferences(user_id)
    interests = get_interests(user_id)
    latest_briefing = get_latest_briefing(user_id)
    recent = get_recent_context(user_id, limit=5)

    # Generate response via chat engine
    result = await generate_chat_response(
        query=body.query,
        user_id=user_id,
        preferences=preferences,
        interests=interests,
        latest_briefing=latest_briefing,
        recent_context=recent,
    )

    # Persist to chat history
    sources_dicts = [
        {"title": s.title, "url": s.url, "source": s.source}
        for s in result.sources
    ]
    create_chat_entry(
        user_id=user_id,
        query=body.query,
        response=result.response,
        sources=sources_dicts,
    )

    return ChatResponse(
        response=result.response,
        sources=[
            ChatSource(title=s.title, url=s.url, source=s.source)
            for s in result.sources
        ],
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def list_chat_history(
    limit: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user),
) -> ChatHistoryResponse:
    """Get chat history for the current user."""
    messages = get_chat_history(user["id"], limit=limit)

    entries = [
        ChatHistoryEntry(
            id=msg["id"],
            user_id=msg["user_id"],
            query=msg["query"],
            response=msg["response"],
            sources=msg.get("sources", []),
            created_at=msg.get("created_at"),
        )
        for msg in messages
    ]

    return ChatHistoryResponse(
        messages=entries,
        total=len(entries),
    )
