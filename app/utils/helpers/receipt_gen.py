# app/utils/helpers/receipt_gen.py

from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Booking


def generate_receipt_id(booking_id: UUID, created_at: datetime, sequence_number: int):
    return f"ORD-{created_at.year}-{sequence_number:03d}"


def generate_and_store_receipt_id(db: Session, booking: Booking):
    # Fetch the latest sequence number for the year
    latest_sequence = db.query(func.max(Booking.receipt_id)).filter(
        func.extract("year", Booking.created_at) == booking.created_at.year
    ).scalar()

    if latest_sequence:
        sequence_number = int(latest_sequence.split("-")[-1]) + 1
    else:
        sequence_number = 1

    # Generate the receipt ID
    booking.receipt_id = generate_receipt_id(booking.id, booking.created_at, sequence_number)
    db.commit()