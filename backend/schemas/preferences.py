"""Preferences request/response schemas."""

from pydantic import BaseModel, field_validator


class PreferencesResponse(BaseModel):
    """Response schema for user preferences."""
    user_id: str
    topics: list[str] = []
    sources: list[str] = []
    briefing_depth: str = "detailed"
    location: str = "Mumbai"
    updated_at: str | None = None


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences."""
    topics: list[str] | None = None
    sources: list[str] | None = None
    briefing_depth: str | None = None
    location: str | None = None

    @field_validator("briefing_depth")
    @classmethod
    def validate_depth(cls, v: str | None) -> str | None:
        if v is not None and v not in ("headlines", "detailed"):
            raise ValueError("briefing_depth must be 'headlines' or 'detailed'")
        return v
