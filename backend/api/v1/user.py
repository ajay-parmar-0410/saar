"""User profile and account management routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.middleware import get_current_user
from db.users import get_user, delete_user
from db.preferences import get_preferences
from db.interests import get_interests
from db.chat import get_chat_history
from schemas.user import UserProfile, DeleteAccountResponse

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    user: dict = Depends(get_current_user),
) -> UserProfile:
    """Get the current user's profile."""
    user_data = get_user(user["id"])
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserProfile(
        id=user_data["id"],
        email=user_data.get("email", user["email"]),
        name=user_data.get("name"),
        user_type=user_data.get("user_type"),
        onboarded=user_data.get("onboarded", False),
        last_active_at=user_data.get("last_active_at"),
        created_at=user_data.get("created_at"),
    )


@router.delete("", response_model=DeleteAccountResponse)
async def delete_account(
    user: dict = Depends(get_current_user),
) -> DeleteAccountResponse:
    """Delete the current user's account and ALL associated data."""
    user_id = user["id"]

    # Verify user exists
    user_data = get_user(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete cascades through foreign keys in Supabase
    delete_user(user_id)

    return DeleteAccountResponse(message="Account deleted successfully")
