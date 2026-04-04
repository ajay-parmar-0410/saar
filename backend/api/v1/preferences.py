"""Preferences API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.middleware import get_current_user
from db.preferences import get_preferences, update_preferences
from schemas.preferences import PreferencesResponse, UpdatePreferencesRequest

router = APIRouter(prefix="/api/v1/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesResponse)
async def get_user_preferences(
    user: dict = Depends(get_current_user),
) -> PreferencesResponse:
    """Get current user's preferences."""
    prefs = get_preferences(user["id"])
    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found. Complete onboarding first.",
        )
    return PreferencesResponse(
        user_id=prefs["user_id"],
        topics=prefs.get("topics", []),
        sources=prefs.get("sources", []),
        briefing_depth=prefs.get("briefing_depth", "detailed"),
        location=prefs.get("location", "Mumbai"),
        updated_at=prefs.get("updated_at"),
    )


@router.put("", response_model=PreferencesResponse)
async def update_user_preferences(
    body: UpdatePreferencesRequest,
    user: dict = Depends(get_current_user),
) -> PreferencesResponse:
    """Update user preferences. Only provided fields are changed.

    Changes are automatically logged to preference_history.
    """
    user_id = user["id"]

    # Verify preferences exist
    existing = get_preferences(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found. Complete onboarding first.",
        )

    # Build update dict from non-None fields
    updates = {
        k: v
        for k, v in body.model_dump().items()
        if v is not None
    }

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated = update_preferences(user_id, **updates)
    return PreferencesResponse(
        user_id=updated["user_id"],
        topics=updated.get("topics", []),
        sources=updated.get("sources", []),
        briefing_depth=updated.get("briefing_depth", "detailed"),
        location=updated.get("location", "Mumbai"),
        updated_at=updated.get("updated_at"),
    )
