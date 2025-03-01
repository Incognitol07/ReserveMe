# app/schemas/auth.py

from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


# Base schema for user-related attributes
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: str
    phone_number: str
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    phone_number: str
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
    token_type: str
    user_id: UUID
    username: str
    role: str


class DetailResponse(BaseModel):
    detail: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
