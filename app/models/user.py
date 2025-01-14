# app/models/user.py

from uuid import uuid4
from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.now)

    bookings = relationship("Booking", back_populates="user")