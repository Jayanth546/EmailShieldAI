import time
from collections import defaultdict, deque
from typing import ClassVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# ============================================================
# Configuration
# ============================================================

MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1 MB

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_REQUESTS = 120

LOGIN_FAILURE_WINDOW = 60  # seconds
LOGIN_FAILURE_LIMIT = 5


# ============================================================
# General API rate limiter
# ============================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic in-memory rate limiter.

    Limits requests by client IP.

    Suitable for a single-process development/small deployment.
    For multiple workers or servers, use a shared store such as Redis.
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        now = time.monotonic()
        window_start = now - RATE_LIMIT_WINDOW

        request_times = self.requests[client_ip]

        while request_times and request_times[0] < window_start:
            request_times.popleft()

        if len(request_times) >= RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
                headers={
                    "Retry-After": str(RATE_LIMIT_WINDOW),
                },
            )

        request_times.append(now)

        return await call_next(request)


# ============================================================
# Request size protection
# ============================================================

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Reject requests larger than MAX_REQUEST_SIZE.
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                content_length = int(content_length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Invalid Content-Length header."
                    },
                )

            if content_length > MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Request body is too large."
                    },
                )

        return await call_next(request)


# ============================================================
# Security headers
# ============================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security-related HTTP response headers.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        if request.url.path.startswith(
            ("/auth", "/analyze", "/reports")
        ):
            response.headers["Cache-Control"] = "no-store"

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


# ============================================================
# Login brute-force protection
# ============================================================

class LoginBruteForceMiddleware(BaseHTTPMiddleware):
    """
    Protect /auth/login against repeated failed login attempts.

    Rules:
    - First 5 failed attempts: normal 401 response.
    - 6th attempt within the window: 429 response.
    - Successful login clears the failure counter.
    - Failed attempts are tracked per client IP.
    """

    failed_attempts: ClassVar[defaultdict] = defaultdict(deque)

    def __init__(self, app):
        super().__init__(app)

    @classmethod
    def _cleanup(cls, client_ip: str) -> deque:
        """Remove expired failed-login attempts."""
        now = time.monotonic()
        window_start = now - LOGIN_FAILURE_WINDOW

        attempts = cls.failed_attempts[client_ip]

        while attempts and attempts[0] < window_start:
            attempts.popleft()

        return attempts

    @classmethod
    def is_blocked(cls, client_ip: str) -> bool:
        """Return True when the IP has exceeded the failure limit."""
        attempts = cls._cleanup(client_ip)

        return len(attempts) >= LOGIN_FAILURE_LIMIT

    @classmethod
    def record_failure(cls, client_ip: str) -> None:
        """Record one failed login attempt."""
        attempts = cls._cleanup(client_ip)
        attempts.append(time.monotonic())

    @classmethod
    def clear_failures(cls, client_ip: str) -> None:
        """Clear failed-login attempts after successful login."""
        cls.failed_attempts.pop(client_ip, None)

    async def dispatch(self, request: Request, call_next):
        # Only protect the login endpoint.
        if request.url.path != "/auth/login":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # Check whether this IP is already blocked.
        if self.is_blocked(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many failed login attempts. "
                        "Please try again later."
                    )
                },
                headers={
                    "Retry-After": str(LOGIN_FAILURE_WINDOW),
                },
            )

        response = await call_next(request)

        return response
