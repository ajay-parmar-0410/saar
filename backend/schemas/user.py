"""User-related request/response schemas."""

from pydantic import BaseModel


class UserProfile(BaseModel):
    """Response schema for user profile."""
    id: str
    email: str
    name: str | None = None
    user_type: list[str] | None = None
    onboarded: bool = False
    last_active_at: str | None = None
    created_at: str | None = None


class DeleteAccountResponse(BaseModel):
    """Response after account deletion."""
    message: str
