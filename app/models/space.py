# app/models/space.py

from uuid import uuid4
from sqlalchemy import Column, UUID, Integer,String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Space(Base):
    __tablename__ = "spaces"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    capacity = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    location = Column(String, nullable=False)
    amenities = Column(Text)
    hourly_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    bookings = relationship("Booking", back_populates="space")