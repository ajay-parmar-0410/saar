"""Interests/watchlist API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.middleware import get_current_user
from db.interests import get_interests, add_interest, remove_interest
from schemas.interests import InterestResponse, AddInterestRequest

router = APIRouter(prefix="/api/v1/interests", tags=["interests"])


@router.get("", response_model=list[InterestResponse])
async def list_interests(
    user: dict = Depends(get_current_user),
) -> list[InterestResponse]:
    """Get all watchlist items for the current user."""
    items = get_interests(user["id"])
    return [
        InterestResponse(
            id=item["id"],
            user_id=item["user_id"],
            type=item["type"],
            value=item["value"],
            added_at=item.get("added_at"),
        )
        for item in items
    ]


@router.post("", response_model=InterestResponse, status_code=status.HTTP_201_CREATED)
async def create_interest(
    body: AddInterestRequest,
    user: dict = Depends(get_current_user),
) -> InterestResponse:
    """Add a watchlist item. Automatically logged to preference_history."""
    item = add_interest(user["id"], body.type, body.value)
    return InterestResponse(
        id=item["id"],
        user_id=item["user_id"],
        type=item["type"],
        value=item["value"],
        added_at=item.get("added_at"),
    )


@router.delete("/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interest(
    interest_id: str,
    user: dict = Depends(get_current_user),
) -> None:
    """Remove a watchlist item. Automatically logged to preference_history."""
    # Verify the interest belongs to this user
    items = get_interests(user["id"])
    if not any(item["id"] == interest_id for item in items):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found",
        )
    remove_interest(user["id"], interest_id)
