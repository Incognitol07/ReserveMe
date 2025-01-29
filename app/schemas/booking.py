# app/schemas/booking.py

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class BookingCreate(BaseModel):
    space_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str = Field(..., max_length=500, description="Purpose of the booking")

    @field_validator("end_time")
    @classmethod
    def check_range(cls, end_time, start_time):
        start_time = start_time.data["start_time"]
        if start_time>=end_time:
            raise ValueError("End time must be greater than start time")
        return end_time

class BookingUpdate(BaseModel):
    start_time: Optional[datetime]
    end_time: Optional[datetime] 
    purpose: Optional[str]
    status: Optional[str] 

class BookingResponse(BaseModel):
    id: UUID
    space_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    total_cost: float

    class Config:
        from_attributes = True

class AdminBookingResponse(BookingResponse):
    user_id: UUID

    class Config:
        from_attributes = True

class TakenBookingResponse(BaseModel):
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True

class Customization(BaseModel):
    title: str
    description: str

class Customer(BaseModel):
    email: EmailStr
    name: str

class PaymentResponse(BaseModel):
    tx_ref: str
    amount: float
    currency: str
    redirect_url: str
    customer: Customer
    customizations: Customization

class ConfirmPayment(BaseModel):
    tx_ref: str
    transaction_id: int