"""Briefing request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class BriefingItemResponse(BaseModel):
    """A single item within a briefing section."""
    title: str
    summary: str
    url: str
    source: str
    impact: str
    relevance: int = 0


class BriefingSectionResponse(BaseModel):
    """A section within a briefing."""
    key: str
    title: str
    items: list[BriefingItemResponse] = []


class BriefingSummary(BaseModel):
    """Lightweight briefing for list views."""
    id: str
    user_id: str
    top_story: str = ""
    item_count: int = 0
    alert_count: int = 0
    read: bool = False
    generated_at: str | None = None


class BriefingDetail(BaseModel):
    """Full briefing detail."""
    id: str
    user_id: str
    content: str = ""
    sections: list[dict[str, Any]] = []
    top_story: str = ""
    item_count: int = 0
    alert_count: int = 0
    read: bool = False
    read_at: str | None = None
    generated_at: str | None = None


class BriefingListResponse(BaseModel):
    """Paginated list of briefings."""
    briefings: list[BriefingSummary]
    total: int
    limit: int
    offset: int


class MarkReadResponse(BaseModel):
    """Response after marking a briefing as read."""
    id: str
    read: bool = True
    read_at: str | None = None
