"""
auth.py
--------
Reusable authentication dependency for protected routes.

HTTPBearer automatically:
- reads the Authorization header
- checks it's formatted as "Bearer <token>"
- returns 403 automatically if the header is missing entirely

get_current_user() then verifies the token itself against Supabase.
Any route that adds `user = Depends(get_current_user)` to its signature
is now a protected route -- FastAPI runs this function first, and the
route body only runs if it doesn't raise an exception.

This also makes Swagger UI show a padlock icon next to protected routes
and adds the "Authorize" button (Stage 5), since FastAPI auto-detects
HTTPBearer as a security scheme.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"user": result.user, "token": token}
