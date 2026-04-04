from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.middleware import get_current_user
from auth.routes import router as auth_router
from api.v1.onboarding import router as onboarding_router

app = FastAPI(
    title="Saar API",
    description="Personalized daily briefing backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes (unprotected)
app.include_router(auth_router)

# API routes (protected)
app.include_router(onboarding_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/me")
async def get_me(user: dict = Depends(get_current_user)) -> dict:
    """Protected endpoint — returns current user info from JWT."""
    return user
