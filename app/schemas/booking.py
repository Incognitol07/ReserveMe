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
    created_at: datetime

    class Config:
        from_attributes = True

class AdminBookingResponse(BookingResponse):
    user_id: UUID
    username: str
    space_name: str
    receipt_id: Optional[str] = None  # Optional field
    tx_ref: Optional[str] = None  # Optional field
    transaction_id: Optional[int] = None  # Optional field

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
    phonenumber: str

class PaymentResponse(BaseModel):
    tx_ref: str
    amount: float
    currency: str
    customer: Customer
    customizations: Customization

class ConfirmPayment(BaseModel):
    tx_ref: str
    transaction_id: int

class BookingConfirmationResponse(BaseModel):
    message: str
    booking_id: UUID
    status: str
    transaction_id: int

class UserDetail(BaseModel):
    name: str
    email: EmailStr
    phone_number: str

class SpaceDetail(BaseModel):
    name: str
    location: str

class BookingDetail(BaseModel):
    date: str
    time: str
    duration: str
    purpose: str

class PaymentDetail(BaseModel):
    amount: float
    status: str
    transaction_id: int
    payment_date: str

class Footer(BaseModel):
    thank_you_message: str
    support_email: str
    terms_and_conditions: str

class ReceiptResponse(BaseModel):
    receipt_no: str
    company_name: str
    user: UserDetail
    space: SpaceDetail
    booking: BookingDetail
    payment: PaymentDetail
    footer: Footer
