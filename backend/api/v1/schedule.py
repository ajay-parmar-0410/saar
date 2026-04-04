"""Schedule API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.middleware import get_current_user
from db.schedules import get_schedule, update_schedule
from schemas.schedule import ScheduleResponse, UpdateScheduleRequest

router = APIRouter(prefix="/api/v1/schedule", tags=["schedule"])


@router.get("", response_model=ScheduleResponse)
async def get_user_schedule(
    user: dict = Depends(get_current_user),
) -> ScheduleResponse:
    """Get the current user's briefing schedule."""
    schedule = get_schedule(user["id"])
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found. Complete onboarding first.",
        )
    return ScheduleResponse(
        user_id=schedule["user_id"],
        times=schedule.get("times", []),
        timezone=schedule.get("timezone", "Asia/Kolkata"),
        enabled=schedule.get("enabled", True),
    )


@router.put("", response_model=ScheduleResponse)
async def update_user_schedule(
    body: UpdateScheduleRequest,
    user: dict = Depends(get_current_user),
) -> ScheduleResponse:
    """Update the briefing schedule."""
    user_id = user["id"]

    existing = get_schedule(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found. Complete onboarding first.",
        )

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

    updated = update_schedule(user_id, **updates)

    # Reschedule the APScheduler jobs
    _reschedule_jobs(user_id, updated)

    return ScheduleResponse(
        user_id=updated["user_id"],
        times=updated.get("times", []),
        timezone=updated.get("timezone", "Asia/Kolkata"),
        enabled=updated.get("enabled", True),
    )


def _reschedule_jobs(user_id: str, schedule: dict) -> None:
    """Update APScheduler jobs after a schedule change."""
    from briefing.scheduler import (
        get_scheduler,
        remove_user_jobs,
        schedule_user_briefing,
    )
    from db.preferences import get_preferences
    from db.interests import get_interests

    scheduler = get_scheduler()
    remove_user_jobs(scheduler, user_id)

    if not schedule.get("enabled", False):
        return

    preferences = get_preferences(user_id)
    if not preferences:
        return

    interests = get_interests(user_id)
    interest_values = [i["value"] for i in interests]

    schedule_user_briefing(
        scheduler=scheduler,
        user_id=user_id,
        schedule=schedule,
        preferences=preferences,
        interest_values=interest_values,
    )
