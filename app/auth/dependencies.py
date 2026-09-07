from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from app.database.client import supabase


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    client: Client = Depends(lambda: supabase)
):
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        response = client.auth.get_user(credentials.credentials.strip())
        if not response.user:
            raise ValueError("Supabase returned no user")
        return {
            "id": response.user.id,
            "email": response.user.email,
        }
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        