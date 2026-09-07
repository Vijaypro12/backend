import logging

import httpx
from fastapi import APIRouter, HTTPException, Depends

from app.database.client import supabase
from app.auth.service import AuthService
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
)
from app.config import settings

from app.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

auth_service = AuthService(supabase)

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "user_id": user["id"],
        "email": user.get("email"),
    }


@router.post("/signup")
def signup(data: SignupRequest):

    try:
        response = auth_service.signup(
            data.email,
            data.password
        )

        if not response.user:
            raise HTTPException(
                status_code=400,
                detail="Signup failed"
            )

        return {
            "message": "Signup successful",
            "user_id": response.user.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(data: LoginRequest):

    try:
        response = auth_service.login(
            data.email,
            data.password
        )

        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Login did not return an active session. Check the credentials and confirm the email address."
            )

        return {
            "message": "Login successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id
        }


    except HTTPException:
        raise
    except httpx.TimeoutException:
        logger.exception("Supabase login timed out")
        raise HTTPException(
            status_code=503,
            detail="Authentication service timed out. Please try again."
        )
    except Exception:
        logger.exception("Supabase login failed")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    try:
        auth_service.request_password_reset(
            data.email,
            f"{settings.FRONTEND_URL.rstrip('/')}/reset-password"
        )
    except Exception:
        logger.exception("Supabase password reset request failed")

    return {
        "message": "If an account exists for that email, a password reset link has been sent."
    }


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    try:
        auth_service.update_password(
            data.access_token,
            data.password,
            data.refresh_token
        )
        return {"message": "Password updated successfully"}
    except Exception:
        logger.exception("Supabase password update failed")
        raise HTTPException(
            status_code=400,
            detail="This reset link is invalid or has expired. Request a new one and try again."
        )


@router.post("/logout")
def logout():

    try:
        auth_service.logout()

        return {
            "message": "Logout successful"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )