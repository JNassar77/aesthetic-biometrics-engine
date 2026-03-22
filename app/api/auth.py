"""
API Key authentication middleware.

Validates X-API-Key header against configured API_KEYS environment variable.
Keys are comma-separated in the env var. If no keys are configured, auth is disabled
(development mode).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_valid_keys() -> set[str]:
    """Parse configured API keys from settings."""
    raw = settings.api_keys.strip()
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}


async def require_api_key(
    api_key: str | None = Security(_api_key_header),
) -> str:
    """Dependency that enforces API key authentication.

    If API_KEYS env var is empty, authentication is bypassed (dev mode).
    Returns the validated API key string.
    """
    valid_keys = _get_valid_keys()

    # Dev mode: no keys configured → bypass auth
    if not valid_keys:
        return "dev-mode"

    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header.",
        )

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )

    return api_key
