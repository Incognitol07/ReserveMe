# app/routers/booking.py

from fastapi import (
    HTTPException,
    Query,
    APIRouter,
    status,
    Depends
)
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import Booking, Space, User
from app.utils import logger, get_current_user, admin_required
from app.database import get_db
from app.schemas import (
    BookingUpdate,
    BookingCreate,
    BookingResponse,
    AdminBookingResponse
)

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])

@booking_router.get("/search", response_model=list[BookingResponse])
async def search_bookings(
    query: str = Query(..., description="Search term for bookings (e.g., purpose or space name)"),
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search bookings by purpose or related space name.
    Only accessible to authenticated users.
    """
    try:
        bookings = (
            db.query(Booking)
            .join(Space, Booking.space_id == Space.id)
            .filter(
                (Booking.purpose.ilike(f"%{query}%")) |
                (Space.name.ilike(f"%{query}%"))
            )
            .filter(Booking.user_id == current_user.id)
            .all()
        )
        return bookings
    except Exception as e:
        logger.error(f"Error searching bookings: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@booking_router.get("/taken")
async def get_taken_bookings(
    db: Session = Depends(get_db),
):
    """
    Fetch all taken bookings.
    """
    try:
        bookings = db.query(Booking).filter(
            Booking.end_time>=datetime.now(), 
            Booking.status=="confirmed"
        ).all()
        if not bookings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Taken bookings not found"
            )
        return [
            {
                "space_name": db.query(Space).filter(Space.id ==booking.space_id).first().name,
                "start_time": booking.start_time,
                "end_time": booking.end_time
            }
            for booking in bookings
            ]
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching available spaces: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@booking_router.get("/admin/all", response_model=list[AdminBookingResponse])
async def admin_get_all_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User =Depends(admin_required),
    db: Session = Depends(get_db),
):
    """
    Fetch all bookings for admin review with pagination.
    """
    try:
        bookings = db.query(Booking).offset(skip).limit(limit).all()
        return bookings
    except Exception as e:
        logger.error(f"Error fetching bookings for admin: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@booking_router.get("/", response_model=list[BookingResponse])
async def get_all_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch all bookings with pagination.
    Only accessible to authenticated users.
    """
    try:
        bookings = (
            db.query(Booking)
            .filter(Booking.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return bookings
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@booking_router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new booking.
    Requires authentication.
    """
    try:
        # Check for booking conflicts
        check_booking = db.query(Booking).filter(
            (Booking.start_time < booking.end_time) & 
            (Booking.end_time > booking.start_time)
        ).first()
        
        if check_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Booking conflict: Existing booking from {check_booking.start_time} to {check_booking.end_time}"
            )

        # Create the booking
        new_booking = Booking(**booking.model_dump(), user_id=current_user.id)
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create booking for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@booking_router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a booking by ID.
    Accessible only to the owner of the booking or an admin.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or (booking.user_id != current_user.id and not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this booking."
        )
    return booking


@booking_router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: UUID,
    update_data: BookingUpdate,
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a booking by ID.
    Accessible only to the owner of the booking.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this booking."
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(booking, key, value)

    try:
        db.commit()
        db.refresh(booking)
        return booking
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@booking_router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a booking by ID.
    Accessible only to the owner of the booking or an admin.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or (booking.user_id != current_user.id and not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this booking."
        )

    try:
        db.delete(booking)
        db.commit()
        return {"message": "Booking deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@booking_router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: UUID,
    status_sent: str = Query(..., regex="^(pending|confirmed|canceled)$", description="New status for the booking"),
    current_user: User =Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the status of a booking.
    Only accessible to admins.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update booking status."
        )

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    try:
        booking.status = status_sent
        db.commit()
        db.refresh(booking)
        return booking
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating booking status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
