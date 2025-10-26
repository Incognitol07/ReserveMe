# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """Base schema containing common user attributes."""

    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a new user account."""

    username: str = Field(..., description="Desired username")
    phone_number: str = Field(..., description="User's phone number")
    password: str = Field(..., description="Password for the account")


class UserLogin(UserBase):
    """Schema for user login credentials."""

    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Response schema containing user information."""

    id: UUID = Field(..., description="Unique user ID")
    username: str = Field(..., description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    phone_number: str = Field(..., description="User's phone number")
    joined_at: datetime = Field(..., description="Account creation timestamp")
    last_login: datetime | None = Field(None, description="Last login timestamp")
    is_active: bool = Field(..., description="Account active status")

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    """Response schema for user registration confirmation."""

    username: str = Field(..., description="Registered username")
    email: EmailStr = Field(..., description="Registered email")
    message: str = Field(..., description="Confirmation message")


class LoginResponse(BaseModel):
    """Response schema containing authentication tokens and user info."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (e.g., Bearer)")
    user_id: UUID = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")


class DetailResponse(BaseModel):
    """Generic response schema for error or detail messages."""

    detail: str = Field(..., description="Detail message")


class RefreshResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str = Field(..., description="New access token")
    token_type: str = Field(..., description="Token type")
