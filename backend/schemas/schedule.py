"""Schedule request/response schemas."""

import re

from pydantic import BaseModel, field_validator


class ScheduleResponse(BaseModel):
    """Response schema for briefing schedule."""
    user_id: str
    times: list[str] = []
    timezone: str = "Asia/Kolkata"
    enabled: bool = True


class UpdateScheduleRequest(BaseModel):
    """Request to update briefing schedule."""
    times: list[str] | None = None
    timezone: str | None = None
    enabled: bool | None = None

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if not v:
            raise ValueError("At least one time is required")
        for t in v:
            if not re.match(r"^\d{2}:\d{2}$", t):
                raise ValueError(f"Invalid time format: '{t}'. Use HH:MM")
            hour, minute = int(t[:2]), int(t[3:])
            if hour > 23 or minute > 59:
                raise ValueError(f"Invalid time value: '{t}'")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(f"Invalid timezone: '{v}'")
        return v
