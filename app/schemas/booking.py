# app/schemas/booking.py

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class BookingCreate(BaseModel):
    """Schema for creating a new booking request."""

    space_id: UUID = Field(..., description="ID of the space to book")
    start_time: datetime = Field(..., description="Start time of the booking")
    end_time: datetime = Field(..., description="End time of the booking")
    purpose: str = Field(..., max_length=500, description="Purpose of the booking")

    @field_validator("end_time")
    @classmethod
    def check_range(cls, end_time, start_time):
        start_time = start_time.data["start_time"]
        if start_time >= end_time:
            raise ValueError("End time must be greater than start time")
        return end_time


class BookingUpdate(BaseModel):
    """Schema for updating an existing booking."""

    start_time: Optional[datetime] = Field(None, description="Updated start time")
    end_time: Optional[datetime] = Field(None, description="Updated end time")
    purpose: Optional[str] = Field(None, description="Updated purpose")
    status: Optional[str] = Field(None, description="Updated status")


class BookingResponse(BaseModel):
    """Response schema for booking information."""

    id: UUID = Field(..., description="Unique booking ID")
    space_id: UUID = Field(..., description="ID of the booked space")
    start_time: datetime = Field(..., description="Booking start time")
    end_time: datetime = Field(..., description="Booking end time")
    purpose: str = Field(..., description="Purpose of the booking")
    status: str = Field(..., description="Current booking status")
    total_cost: float = Field(..., description="Total cost of the booking")
    created_at: datetime = Field(..., description="Booking creation timestamp")

    class Config:
        from_attributes = True


class AdminBookingResponse(BookingResponse):
    """Extended response schema for admin booking views with additional user and space details."""

    user_id: UUID = Field(..., description="ID of the user who made the booking")
    username: str = Field(..., description="Username of the booking user")
    space_name: str = Field(..., description="Name of the booked space")
    receipt_id: Optional[str] = Field(None, description="Receipt ID if available")
    tx_ref: Optional[str] = Field(None, description="Transaction reference")
    transaction_id: Optional[int] = Field(None, description="Transaction ID")

    class Config:
        from_attributes = True


class Pagination(BaseModel):
    """Schema for pagination metadata."""

    current_page: int = Field(..., description="Current page number")
    next_page: int | None = Field(None, description="Next page number")
    prev_page: int | None = Field(None, description="Previous page number")
    total_pages: int = Field(..., description="Total number of pages")
    total_records: int = Field(..., description="Total number of records")
    next_request: str | None = Field(None, description="URL for next page")
    prev_request: str | None = Field(None, description="URL for previous page")


class AllBookingResponse(BaseModel):
    """Response schema for paginated list of bookings."""

    data: list[AdminBookingResponse] = Field(..., description="List of bookings")
    pagination: Pagination = Field(..., description="Pagination metadata")

    class Config:
        from_attributes = True


class TakenBookingResponse(BaseModel):
    """Response schema for unavailable time slots."""

    start_time: datetime = Field(..., description="Start time of unavailable slot")
    end_time: datetime = Field(..., description="End time of unavailable slot")

    class Config:
        from_attributes = True


class Customization(BaseModel):
    """Schema for payment customization details."""

    title: str = Field(..., description="Title for the payment")
    description: str = Field(..., description="Description for the payment")


class Customer(BaseModel):
    """Schema for customer information in payment."""

    email: EmailStr = Field(..., description="Customer's email address")
    name: str = Field(..., description="Customer's full name")
    phonenumber: str = Field(..., description="Customer's phone number")


class PaymentResponse(BaseModel):
    """Schema for payment initialization response."""

    tx_ref: str = Field(..., description="Transaction reference")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    customer: Customer = Field(..., description="Customer details")
    customizations: Customization = Field(..., description="Payment customization")


class ConfirmPayment(BaseModel):
    """Schema for confirming a payment."""

    tx_ref: str = Field(..., description="Transaction reference to confirm")
    transaction_id: int = Field(..., description="Transaction ID")


class BookingConfirmationResponse(BaseModel):
    """Response schema for booking confirmation."""

    message: str = Field(..., description="Confirmation message")
    booking_id: UUID = Field(..., description="ID of the confirmed booking")
    status: str = Field(..., description="Status of the booking")
    transaction_id: int = Field(..., description="Associated transaction ID")


class UserDetail(BaseModel):
    """Schema for user details in receipt."""

    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone_number: str = Field(..., description="User's phone number")


class SpaceDetail(BaseModel):
    """Schema for space details in receipt."""

    name: str = Field(..., description="Name of the space")
    location: str = Field(..., description="Location of the space")


class BookingDetail(BaseModel):
    """Schema for booking details in receipt."""

    date: str = Field(..., description="Date of the booking")
    time: str = Field(..., description="Time of the booking")
    duration: str = Field(..., description="Duration of the booking")
    purpose: str = Field(..., description="Purpose of the booking")


class PaymentDetail(BaseModel):
    """Schema for payment details in receipt."""

    amount: float = Field(..., description="Payment amount")
    status: str = Field(..., description="Payment status")
    transaction_id: int = Field(..., description="Transaction ID")
    payment_date: str = Field(..., description="Date of payment")


class ReceiptResponse(BaseModel):
    """Response schema for booking receipt."""

    receipt_no: str = Field(..., description="Receipt number")
    company_name: str = Field(..., description="Company name")
    user: UserDetail = Field(..., description="User details")
    space: SpaceDetail = Field(..., description="Space details")
    booking: BookingDetail = Field(..., description="Booking details")
    payment: PaymentDetail = Field(..., description="Payment details")
