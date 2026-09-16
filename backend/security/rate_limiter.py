import sys
from pathlib import Path

# Add backend directory to path so we can run this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from config import settings

# Create the limiter instance
# get_remote_address extracts the user's IP address from the request
limiter = Limiter(key_func=get_remote_address)

# Build the rate limit string from .env settings (e.g., "30/minute")
RATE_LIMIT = f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW_SECONDS} seconds"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom error response when a user exceeds the rate limit.
    Instead of a generic 429 error, we return a friendly JSON message.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate Limit Exceeded",
            "detail": f"Too many requests. You are limited to {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW_SECONDS} seconds.",
            "tip": "Please wait before trying again."
        }
    )
