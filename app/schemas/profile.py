# app/schemas/profile.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UpdatePasswordRequest(BaseModel):
    """Schema for updating user password."""

    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., description="New password to set")


class UpdateProfileRequest(BaseModel):
    """Schema for updating user profile information."""

    username: Optional[str] = Field(None, description="Updated username")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    phone_number: Optional[str] = Field(None, description="Updated phone number")
