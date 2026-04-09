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
import os

_allowed_origins = [
    "http://localhost:3000",
]
_frontend_url = os.environ.get("FRONTEND_URL", "").strip().rstrip("/")
if _frontend_url:
    _allowed_origins.append(_frontend_url)

import logging as _logging
_logging.getLogger(__name__).info("CORS allowed origins: %s", _allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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


@app.get("/health/sources")
async def source_health_check() -> dict:
    """Test all source fetchers and report status. For diagnostics only."""
    import time
    from sources.registry import SOURCE_REGISTRY
    from sources.types import SourceResult

    results = {}
    for name, (fn, kwargs) in SOURCE_REGISTRY.items():
        start = time.time()
        try:
            if name == "weatherapi":
                kwargs = {**kwargs, "location": "Mumbai"}
            elif name in ("reddit", "reddit_trending", "reddit_finance"):
                kwargs = {**kwargs, "user_type": "general"}

            result: SourceResult = await fn(**kwargs)
            elapsed = round(time.time() - start, 2)

            if result.error:
                results[name] = {"status": "error", "error": result.error, "time": elapsed}
            else:
                results[name] = {
                    "status": "ok",
                    "items": len(result.items),
                    "sample": result.items[0].title[:60] if result.items else "",
                    "time": elapsed,
                }
        except Exception as e:
            elapsed = round(time.time() - start, 2)
            results[name] = {"status": "exception", "error": str(e)[:100], "time": elapsed}

    ok = sum(1 for r in results.values() if r["status"] == "ok" and r.get("items", 0) > 0)
    total = len(results)
    return {"ok": ok, "total": total, "sources": results}
