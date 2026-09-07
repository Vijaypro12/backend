from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    access_token: str
    password: str = Field(min_length=6)
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    user_id: str