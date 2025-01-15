from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class BookingCreate(BaseModel):
    space_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str = Field(..., max_length=500, description="Purpose of the booking")
    total_cost: float 

class BookingUpdate(BaseModel):
    start_time: Optional[datetime]
    end_time: Optional[datetime] 
    purpose: Optional[str]
    status: Optional[str] 
    total_cost: Optional[float]

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

class AdminBookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    space_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    total_cost: float

    class Config:
        from_attributes = True
