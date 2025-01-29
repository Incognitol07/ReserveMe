# app/schemas/profile.py

from pydantic import BaseModel, EmailStr
from typing import Optional

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
