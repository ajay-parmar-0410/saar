"""Chat request/response schemas."""

from typing import Any

from pydantic import BaseModel, field_validator


class ChatSource(BaseModel):
    """A source citation in a chat response."""
    title: str
    url: str
    source: str


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        if len(v) > 2000:
            raise ValueError("Query must be under 2000 characters")
        return v


class ChatResponse(BaseModel):
    """Response from the chat engine."""
    response: str
    sources: list[ChatSource] = []


class ChatHistoryEntry(BaseModel):
    """A single chat history entry."""
    id: str
    user_id: str
    query: str
    response: str
    sources: list[dict[str, Any]] = []
    created_at: str | None = None


class ChatHistoryResponse(BaseModel):
    """Paginated chat history."""
    messages: list[ChatHistoryEntry]
    total: int
