"""Interest/watchlist request/response schemas."""

from pydantic import BaseModel, field_validator


VALID_INTEREST_TYPES = ("stock", "repo", "subreddit", "keyword", "team")


class InterestResponse(BaseModel):
    """Response schema for a single watchlist item."""
    id: str
    user_id: str
    type: str
    value: str
    added_at: str | None = None


class AddInterestRequest(BaseModel):
    """Request to add a watchlist item."""
    type: str
    value: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_INTEREST_TYPES:
            raise ValueError(
                f"Interest type must be one of {VALID_INTEREST_TYPES}"
            )
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Interest value cannot be empty")
        if len(v) > 200:
            raise ValueError("Interest value must be under 200 characters")
        return v
