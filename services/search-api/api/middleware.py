"""
Middleware for Privacy Protection, Security, and Rate Limiting.
Guarantees:
1. Raw search queries are NEVER written to server access logs by default.
2. Lightweight client rate limiting to prevent abuse.
3. Security headers (X-Content-Type-Options, X-Frame-Options, etc.).
"""

import time
import logging
from typing import Dict, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings

logger = logging.getLogger("nya.access")


class PrivacyAndSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_rpm = max_requests_per_minute
        # In-memory sliding window per IP: ip -> list of timestamps
        self.request_history: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # 1. Rate limiting check
        timestamps = self.request_history.get(client_ip, [])
        # Expire timestamps older than 60 seconds
        valid_timestamps = [t for t in timestamps if now - t < 60]
        if len(valid_timestamps) >= self.max_rpm:
            return Response(
                content='{"detail": "Rate limit exceeded. Please wait a moment."}',
                status_code=429,
                media_type="application/json",
            )
        valid_timestamps.append(now)
        self.request_history[client_ip] = valid_timestamps

        # 2. Process request
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # 3. Privacy-safe access logging:
        # If path is /search, strip query params from log to prevent logging user search terms
        path = request.url.path
        if not settings.ENABLE_RAW_QUERY_LOGGING and "search" in path:
            logged_url = path  # exclude request.url.query
        else:
            logged_url = str(request.url)

        logger.info(
            f"{client_ip} - {request.method} {logged_url} -> {response.status_code} ({duration_ms}ms)"
        )

        # 4. Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
