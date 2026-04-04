"""Rate limiting middleware using in-memory token bucket per user."""

import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


@dataclass
class TokenBucket:
    """Simple token bucket for rate limiting."""
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)

    def consume(self) -> bool:
        """Try to consume a token. Returns True if allowed."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )
        self.last_refill = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-user rate limiting.

    - General endpoints: 60 requests/minute
    - Chat endpoint: 20 requests/minute
    """

    GENERAL_CAPACITY = 60
    GENERAL_RATE = 60.0 / 60.0  # 1 token/sec

    CHAT_CAPACITY = 20
    CHAT_RATE = 20.0 / 60.0  # ~0.33 tokens/sec

    def __init__(self, app: object) -> None:
        super().__init__(app)
        self._general_buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=self.GENERAL_CAPACITY,
                refill_rate=self.GENERAL_RATE,
            )
        )
        self._chat_buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=self.CHAT_CAPACITY,
                refill_rate=self.CHAT_RATE,
            )
        )

    def _get_user_key(self, request: Request) -> str:
        """Extract user identifier from request."""
        # Try JWT sub from auth header
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            # Use token hash as key (avoids decoding JWT in middleware)
            return f"token:{hash(auth)}"
        # Fallback to IP
        client = request.client
        return f"ip:{client.host if client else 'unknown'}"

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Skip rate limiting for health check and auth routes
        path = request.url.path
        if path == "/health" or path.startswith("/auth/"):
            return await call_next(request)

        user_key = self._get_user_key(request)

        # Check chat-specific limit
        is_chat = path.startswith("/api/v1/chat") and request.method == "POST"
        if is_chat:
            if not self._chat_buckets[user_key].consume():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Chat rate limit exceeded. Max 20 requests per minute.",
                )

        # Check general limit
        if not self._general_buckets[user_key].consume():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Max 60 requests per minute.",
            )

        return await call_next(request)
