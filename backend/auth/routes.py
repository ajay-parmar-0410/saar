"""Authentication routes — Magic Link login, token refresh, logout."""

import os

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import create_client

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_client():
    """Get a Supabase client for auth operations (uses anon key)."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


class MagicLinkRequest(BaseModel):
    email: EmailStr


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    token: str


@router.post("/magic-link")
async def send_magic_link(body: MagicLinkRequest) -> dict:
    """Send a magic link to the user's email."""
    client = _get_auth_client()
    try:
        client.auth.sign_in_with_otp({"email": body.email})
        return {"message": "Magic link sent. Check your email."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send magic link: {str(e)}",
        )


@router.post("/verify-otp")
async def verify_otp(body: VerifyOtpRequest) -> dict:
    """Verify OTP token from magic link email."""
    client = _get_auth_client()
    try:
        response = client.auth.verify_otp({
            "email": body.email,
            "token": body.token,
            "type": "email",
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired OTP: {str(e)}",
        )


@router.post("/refresh")
async def refresh_token(body: TokenRefreshRequest) -> dict:
    """Refresh an expired access token using a refresh token."""
    client = _get_auth_client()
    try:
        response = client.auth.refresh_session(body.refresh_token)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to refresh token: {str(e)}",
        )


@router.post("/logout")
async def logout() -> dict:
    """Logout endpoint. Client-side should discard tokens."""
    return {"message": "Logged out successfully"}
