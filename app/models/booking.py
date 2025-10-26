# app/models/booking.py

from uuid import uuid4
from sqlalchemy import Column, Integer, String, UUID, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Booking(Base):
    """SQLAlchemy model representing a booking reservation."""

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True)
    receipt_id = Column(String, unique=True, nullable=True)  # Add this field
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        String, default="pending", nullable=False
    )  # Options: pending, confirmed, canceled
    total_cost = Column(Float, nullable=False)
    purpose = Column(Text, nullable=False)
    tx_ref = Column(String, nullable=True)
    transaction_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    user = relationship("User", back_populates="bookings")
    space = relationship("Space", back_populates="bookings")
