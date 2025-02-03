# app/schemas/space.py

from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class SpaceCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the space")
    description: Optional[str] = Field(None, max_length=500, description="Description of the space")
    capacity: int = Field(..., gt=0, description="Maximum capacity of the space")
    is_available: bool = Field(default=True, description="Availability status of the space")
    location: str = Field(..., max_length=255, description="Location of the space (e.g., address or coordinates)")
    amenities: Optional[list[str]] = Field(None, max_length=500, description="List of amenities provided (e.g., WiFi, projector)")
    hourly_rate: float = Field(..., gt=0, description="Hourly rental rate for the space")


class SpaceResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the space")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the space")
    description: Optional[str] = Field(None, max_length=500, description="Description of the space")
    capacity: int = Field(..., gt=0, description="Maximum capacity of the space")
    is_available: bool = Field(default=True, description="Availability status of the space")
    location: str = Field(..., max_length=255, description="Location of the space (e.g., address or coordinates)")
    amenities: Optional[list[str]] = Field(None, max_length=500, description="List of amenities provided (e.g., WiFi, projector)")
    hourly_rate: float = Field(..., gt=0, description="Hourly rental rate for the space")
    images: list[str]

    class Config:
        from_attributes = True  # Enables Pydantic to work seamlessly with SQLAlchemy models


class SpaceUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated name of the space")
    description: Optional[str] = Field(None, max_length=500, description="Updated description of the space")
    capacity: Optional[int] = Field(None, gt=0, description="Updated maximum capacity of the space")
    is_available: Optional[bool] = Field(None, description="Updated availability status of the space")
    location: Optional[str] = Field(None, max_length=255, description="Updated location of the space")
    amenities: Optional[list[str]] = Field(None, max_length=500, description="Updated list of amenities provided")
    hourly_rate: Optional[float] = Field(None, gt=0, description="Updated hourly rental rate for the space")
