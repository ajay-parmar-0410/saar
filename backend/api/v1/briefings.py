"""Briefings API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.middleware import get_current_user
from db.briefings import get_briefing, get_user_briefings, mark_as_read
from schemas.briefings import (
    BriefingDetail,
    BriefingListResponse,
    BriefingSummary,
    MarkReadResponse,
)

router = APIRouter(prefix="/api/v1/briefings", tags=["briefings"])


@router.get("", response_model=BriefingListResponse)
async def list_briefings(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
) -> BriefingListResponse:
    """List briefings for the current user, most recent first."""
    briefings = get_user_briefings(user["id"], limit=limit, offset=offset)

    summaries = [
        BriefingSummary(
            id=b["id"],
            user_id=b["user_id"],
            top_story=b.get("top_story", ""),
            item_count=b.get("item_count", 0),
            alert_count=b.get("alert_count", 0),
            read=b.get("read", False),
            generated_at=b.get("generated_at"),
        )
        for b in briefings
    ]

    return BriefingListResponse(
        briefings=summaries,
        total=len(summaries),
        limit=limit,
        offset=offset,
    )


@router.get("/{briefing_id}", response_model=BriefingDetail)
async def get_briefing_detail(
    briefing_id: str,
    user: dict = Depends(get_current_user),
) -> BriefingDetail:
    """Get a single briefing by ID."""
    briefing = get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found",
        )

    # Ensure the briefing belongs to the requesting user
    if briefing["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found",
        )

    return BriefingDetail(
        id=briefing["id"],
        user_id=briefing["user_id"],
        content=briefing.get("content", ""),
        sections=briefing.get("sections", []),
        top_story=briefing.get("top_story", ""),
        item_count=briefing.get("item_count", 0),
        alert_count=briefing.get("alert_count", 0),
        read=briefing.get("read", False),
        read_at=briefing.get("read_at"),
        generated_at=briefing.get("generated_at"),
    )


@router.put("/{briefing_id}/read", response_model=MarkReadResponse)
async def mark_briefing_read(
    briefing_id: str,
    user: dict = Depends(get_current_user),
) -> MarkReadResponse:
    """Mark a briefing as read."""
    briefing = get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found",
        )

    if briefing["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found",
        )

    updated = mark_as_read(briefing_id)
    return MarkReadResponse(
        id=updated["id"],
        read=updated.get("read", True),
        read_at=updated.get("read_at"),
    )
