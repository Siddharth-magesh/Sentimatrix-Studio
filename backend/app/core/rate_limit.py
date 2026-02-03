"""Rate limiting middleware and utilities."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings


@dataclass
class RateLimitInfo:
    """Rate limit tracking info for a client."""

    requests: list[float] = field(default_factory=list)
    blocked_until: float = 0


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_window: int = 100,
        window_seconds: int = 60,
        block_duration: int = 60,
    ):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.block_duration = block_duration
        self._clients: dict[str, RateLimitInfo] = defaultdict(RateLimitInfo)

    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _cleanup_old_requests(self, info: RateLimitInfo, now: float) -> None:
        """Remove requests outside the current window."""
        cutoff = now - self.window_seconds
        info.requests = [t for t in info.requests if t > cutoff]

    def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is allowed.

        Returns:
            Tuple of (allowed, headers_dict)
        """
        now = time.time()
        client_key = self._get_client_key(request)
        info = self._clients[client_key]

        # Check if client is blocked
        if info.blocked_until > now:
            retry_after = int(info.blocked_until - now)
            return False, {
                "X-RateLimit-Limit": str(self.requests_per_window),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(info.blocked_until)),
                "Retry-After": str(retry_after),
            }

        # Cleanup old requests
        self._cleanup_old_requests(info, now)

        # Check rate limit
        remaining = self.requests_per_window - len(info.requests)
        reset_time = int(now + self.window_seconds)

        headers = {
            "X-RateLimit-Limit": str(self.requests_per_window),
            "X-RateLimit-Remaining": str(max(0, remaining - 1)),
            "X-RateLimit-Reset": str(reset_time),
        }

        if remaining <= 0:
            # Block the client
            info.blocked_until = now + self.block_duration
            headers["Retry-After"] = str(self.block_duration)
            return False, headers

        # Record request
        info.requests.append(now)
        return True, headers

    def reset(self, request: Request) -> None:
        """Reset rate limit for a client."""
        client_key = self._get_client_key(request)
        if client_key in self._clients:
            del self._clients[client_key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(
        self,
        app,
        limiter: RateLimiter | None = None,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        settings = get_settings()
        self.limiter = limiter or RateLimiter(
            requests_per_window=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
        self.exclude_paths = exclude_paths or [
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        allowed, headers = self.limiter.is_allowed(request)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "retry_after": headers.get("Retry-After"),
                },
                headers=headers,
            )

        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


# Decorator for route-specific rate limiting
def rate_limit(
    requests: int = 10,
    window: int = 60,
    key_func: Callable[[Request], str] | None = None,
):
    """
    Decorator for route-specific rate limiting.

    Usage:
        @router.get("/expensive")
        @rate_limit(requests=5, window=60)
        async def expensive_endpoint():
            ...
    """
    limiters: dict[str, RateLimiter] = {}

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get or create limiter for this endpoint
            endpoint_key = f"{request.method}:{request.url.path}"
            if endpoint_key not in limiters:
                limiters[endpoint_key] = RateLimiter(
                    requests_per_window=requests,
                    window_seconds=window,
                )

            allowed, headers = limiters[endpoint_key].is_allowed(request)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for this endpoint",
                    headers=headers,
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


# Specialized limiters for different use cases
class AuthRateLimiter(RateLimiter):
    """Rate limiter for authentication endpoints with stricter limits."""

    def __init__(self):
        super().__init__(
            requests_per_window=5,  # 5 login attempts
            window_seconds=300,  # per 5 minutes
            block_duration=900,  # 15 minute block
        )


class ApiKeyRateLimiter(RateLimiter):
    """Rate limiter based on API key with higher limits."""

    def __init__(self):
        super().__init__(
            requests_per_window=1000,
            window_seconds=3600,  # per hour
            block_duration=300,
        )

    def _get_client_key(self, request: Request) -> str:
        """Get API key from request."""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key[:8]}"  # Use prefix for privacy
        return super()._get_client_key(request)
