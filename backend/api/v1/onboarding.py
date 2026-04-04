"""Onboarding API — complete user setup in one call."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from auth.middleware import get_current_user
from config.starter_packs import (
    VALID_USER_TYPES,
    get_combined_starter_pack,
)
from db.preferences import update_preferences
from db.interests import add_interest
from db.schedules import update_schedule
from db.users import update_user

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


class InterestItem(BaseModel):
    type: str
    value: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = ("stock", "repo", "subreddit", "keyword", "team")
        if v not in valid:
            raise ValueError(f"Interest type must be one of {valid}")
        return v


class ScheduleConfig(BaseModel):
    times: list[str] = ["07:00"]
    timezone: str = "Asia/Kolkata"

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        import re
        for t in v:
            if not re.match(r"^\d{2}:\d{2}$", t):
                raise ValueError(f"Invalid time format: '{t}'. Use HH:MM")
        return v


class OnboardingRequest(BaseModel):
    user_types: list[str]
    topics: list[str] | None = None
    sources: list[str] | None = None
    briefing_depth: str = "detailed"
    location: str = "Mumbai"
    interests: list[InterestItem] = []
    schedule: ScheduleConfig = ScheduleConfig()

    @field_validator("user_types")
    @classmethod
    def validate_user_types(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one user type is required")
        for ut in v:
            if ut not in VALID_USER_TYPES:
                raise ValueError(
                    f"Invalid user type: '{ut}'. "
                    f"Valid types: {list(VALID_USER_TYPES)}"
                )
        return v

    @field_validator("briefing_depth")
    @classmethod
    def validate_depth(cls, v: str) -> str:
        if v not in ("headlines", "detailed"):
            raise ValueError("briefing_depth must be 'headlines' or 'detailed'")
        return v


class StarterPackResponse(BaseModel):
    topics: list[str]
    sources: list[str]


@router.get("/starter-pack")
async def get_starter_pack_for_types(
    user_types: str,
    _user: dict = Depends(get_current_user),
) -> StarterPackResponse:
    """Get the combined starter pack for given user types.

    Pass user_types as comma-separated: ?user_types=ai_tech,trader
    """
    types = [t.strip() for t in user_types.split(",") if t.strip()]
    for ut in types:
        if ut not in VALID_USER_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user type: '{ut}'. Valid: {list(VALID_USER_TYPES)}",
            )
    pack = get_combined_starter_pack(types)
    return StarterPackResponse(
        topics=list(pack.topics),
        sources=list(pack.sources),
    )


@router.post("/complete")
async def complete_onboarding(
    body: OnboardingRequest,
    user: dict = Depends(get_current_user),
) -> dict:
    """Complete onboarding — sets up all user preferences in one call."""
    user_id = user["id"]

    # 1. Update user type
    update_user(user_id, user_type=body.user_types)

    # 2. Determine topics and sources
    # If not provided, use starter pack defaults
    if body.topics is None or body.sources is None:
        pack = get_combined_starter_pack(body.user_types)
        topics = body.topics if body.topics is not None else list(pack.topics)
        sources = body.sources if body.sources is not None else list(pack.sources)
    else:
        topics = body.topics
        sources = body.sources

    # 3. Update preferences
    update_preferences(
        user_id,
        topics=topics,
        sources=sources,
        briefing_depth=body.briefing_depth,
        location=body.location,
    )

    # 4. Add watchlist interests
    for interest in body.interests:
        add_interest(user_id, interest.type, interest.value)

    # 5. Update schedule
    update_schedule(
        user_id,
        times=body.schedule.times,
        timezone=body.schedule.timezone,
        enabled=True,
    )

    return {
        "message": "Onboarding complete",
        "user_id": user_id,
        "user_types": body.user_types,
        "topics": topics,
        "sources": sources,
        "interests_count": len(body.interests),
        "schedule": {
            "times": body.schedule.times,
            "timezone": body.schedule.timezone,
        },
    }
