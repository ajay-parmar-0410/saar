"""Common response schemas used across endpoints."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    error: str
    detail: str
    status: int


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
