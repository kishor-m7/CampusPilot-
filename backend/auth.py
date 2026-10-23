from fastapi import Header, HTTPException, status
from typing import Optional
from backend.config import settings
import logging

logger = logging.getLogger("campuspilot.auth")

async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> str:
    """
    Extracts the authenticated student user ID.
    Supports:
    1. Direct X-User-Id header (for internal microservices / MCP / testing)
    2. Supabase Bearer token
    3. Development fallback to DEFAULT_DEV_USER_ID
    """
    # 1. Direct explicit user ID header
    if x_user_id:
        return x_user_id.strip()

    # 2. Bearer token check
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1].strip()
        # In a fully deployed Supabase project, decode JWT with SUPABASE_JWT_SECRET
        # For now, if mock or token provided, extract subject
        if token and token != "undefined" and token != "null":
            # For lightweight inspection:
            return token if "-" in token else settings.DEFAULT_DEV_USER_ID

    # 3. Development Fallback
    if settings.ENVIRONMENT == "development":
        return settings.DEFAULT_DEV_USER_ID

    # 4. Production Unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication token"
    )
