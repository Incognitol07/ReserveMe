# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
import re


# Base schema for user-related attributes
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one digit")
        return password


class UserLogin(UserBase):
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    joined_at: datetime
    last_login: datetime | None
    is_active: bool

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    username: str
    email: EmailStr
    message: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    username: str
    user_id: UUID


class DetailResponse(BaseModel):
    detail: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str 
