from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.middleware import get_current_user
from auth.routes import router as auth_router
from api.v1.onboarding import router as onboarding_router
from api.v1.user import router as user_router
from api.v1.preferences import router as preferences_router
from api.v1.interests import router as interests_router
from api.v1.schedule import router as schedule_router
from api.v1.briefings import router as briefings_router
from api.v1.chat import router as chat_router
from middleware.error_handler import register_error_handlers
from middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown lifecycle — load scheduler jobs on startup."""
    from briefing.scheduler import get_scheduler, load_all_schedules

    scheduler = get_scheduler()
    await load_all_schedules(scheduler)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Saar API",
    description="Personalized daily briefing backend",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Middleware (order matters: last added = first executed) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# --- Error handlers ---
register_error_handlers(app)

# --- Auth routes (unprotected) ---
app.include_router(auth_router)

# --- API routes (protected) ---
app.include_router(onboarding_router)
app.include_router(user_router)
app.include_router(preferences_router)
app.include_router(interests_router)
app.include_router(schedule_router)
app.include_router(briefings_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
