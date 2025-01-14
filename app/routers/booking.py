# app/routers/booking.py

from fastapi import (
    HTTPException,
    Query,
    APIRouter,
    status,
    Depends
)
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import booking, Booking, User
from app.utils import logger
from app.database import get_db

booking_router = APIRouter(prefix="/bookings")

@booking_router.get("/")
async def get_all_bookings(db:Session = Depends(get_db)):
    bookings = db.query(booking).all()
    return bookings

@booking_router.post("/")
async def create_booking(db: Session = Depends(get_db)):
    ...


@booking_router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    db:Session = Depends(get_db)
):
    booking = db.query(booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    return booking

@booking_router.get("/{booking_id}")
async def update_booking(
    booking_id: UUID,
    update_booking,
    db:Session = Depends(get_db)
):
    booking = db.query(booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    for key, value in update_booking.model_dump().items():
        setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return 


@booking_router.delete("/{booking_id}")
async def delete_booking(
    booking_id: UUID,
    db:Session = Depends(get_db)
):
    booking = db.query(booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    return booking