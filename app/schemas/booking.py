from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    user_id: int = Field(..., description="The ID of the user making the booking")
    space_id: int = Field(..., description="The ID of the space being booked")
    start_time: datetime = Field(..., description="The start time of the booking")
    end_time: datetime = Field(..., description="The end time of the booking")
    purpose: str = Field(..., max_length=500, description="Purpose of the booking")
    total_cost: float = Field(..., ge=0, description="Total cost of the booking")

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = Field(None, description="The updated start time")
    end_time: Optional[datetime] = Field(None, description="The updated end time")
    purpose: Optional[str] = Field(None, max_length=500, description="Updated purpose of the booking")
    status: Optional[str] = Field(None, description="Updated status of the booking")
    total_cost: Optional[float] = Field(None, ge=0, description="Updated total cost")

class BookingResponse(BaseModel):
    id: UUID4
    user_id: int
    space_id: int
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    total_cost: float

    class Config:
        orm_mode = True
