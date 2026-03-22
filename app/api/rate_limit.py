"""
Simple in-memory rate limiter middleware.

Uses a sliding window approach per client IP. No external dependencies.
Configurable via RATE_LIMIT_RPM env var (requests per minute, default 60).
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter based on client IP with sliding window."""

    def __init__(self, app, requests_per_minute: int | None = None):
        super().__init__(app)
        self.rpm = requests_per_minute or settings.rate_limit_rpm
        self.window = 60.0  # seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, respecting X-Forwarded-For for proxies."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup(self, timestamps: list[float], now: float) -> list[float]:
        """Remove timestamps outside the current window."""
        cutoff = now - self.window
        return [t for t in timestamps if t > cutoff]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for health endpoints
        if request.url.path.endswith("/health"):
            return await call_next(request)

        # Skip if rate limiting is disabled (rpm=0)
        if self.rpm <= 0:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        # Clean old entries
        self._requests[client_ip] = self._cleanup(
            self._requests[client_ip], now
        )

        if len(self._requests[client_ip]) >= self.rpm:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.rpm} requests per minute.",
            )

        self._requests[client_ip].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.rpm - len(self._requests[client_ip]))
        )
        return response
