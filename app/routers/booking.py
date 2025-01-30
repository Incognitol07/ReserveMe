# app/routers/booking.py

from fastapi import HTTPException, Query, APIRouter, status, Depends
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import Booking, Space, User
from app.utils import (
    logger, 
    get_current_user, 
    admin_required, 
    create_random_key, 
    generate_and_store_receipt_id
    )
from app.config import settings
from app.database import get_db
from app.schemas import (
    BookingUpdate,
    BookingCreate,
    BookingResponse,
    AdminBookingResponse,
    TakenBookingResponse,
    DetailResponse,
    PaymentResponse,
    ConfirmPayment,
    BookingConfirmationResponse,
    ReceiptResponse
)

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])


@booking_router.get("/search", response_model=list[BookingResponse])
async def search_bookings(
    query: str = Query(
        ..., description="Search term for bookings (e.g., purpose or space name)"
    ),
    current_user: User = Depends(get_current_user),
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
                (Booking.purpose.ilike(f"%{query}%")) | (Space.name.ilike(f"%{query}%"))
            )
            .filter(Booking.user_id == current_user.id)
            .all()
        )
        return bookings
    except Exception as e:
        logger.error(f"Error searching bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )




@booking_router.get("/", response_model=list[BookingResponse])
async def get_all_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    current_user: User = Depends(get_current_user),
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=BookingResponse
)
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
        check_booking = (
            db.query(Booking)
            .filter(
                (Booking.start_time < booking.end_time)
                & (Booking.end_time > booking.start_time)
            )
            .first()
        )

        if check_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Booking conflict: Existing booking from {check_booking.start_time} to {check_booking.end_time}",
            )

        rate = db.query(Space).filter(Space.id == booking.space_id).first().hourly_rate
        total_cost = (booking.end_time - booking.start_time).seconds // 3600 * rate

        # Create the booking
        new_booking = Booking(
            **booking.model_dump(), user_id=current_user.id, total_cost=total_cost
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking

    except SQLAlchemyError as e:
        logger.error(f"Failed to create booking for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch a booking by ID.
    Accessible only to the owner of the booking or an admin.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or (
        booking.user_id != current_user.id and not current_user.is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this booking.",
        )
    return booking


@booking_router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: UUID,
    update_data: BookingUpdate,
    current_user: User = Depends(get_current_user),
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
            detail="You do not have permission to update this booking.",
        )

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(booking, key, value)

    try:
        db.commit()
        db.refresh(booking)
        return booking
    except SQLAlchemyError as e:
        logger.error(f"Error updating booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.delete("/{booking_id}", response_model=DetailResponse)
async def delete_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a booking by ID.
    Accessible only to the owner of the booking or an admin.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or (
        booking.user_id != current_user.id and not current_user.is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this booking.",
        )

    try:
        db.delete(booking)
        db.commit()
        return {"detail": "Booking deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Error deleting booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: UUID,
    status_sent: str = Query(
        ...,
        regex="^(pending|confirmed|canceled)$",
        description="New status for the booking",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the status of a booking.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    try:
        booking.status = status_sent
        db.commit()
        db.refresh(booking)
        return booking
    except SQLAlchemyError as e:
        logger.error(f"Error updating booking status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.get("/taken/{space_id}", response_model=list[TakenBookingResponse])
async def get_taken_bookings(
    space_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Fetch all taken bookings.
    """
    try:
        query = db.query(Booking).filter(
            Booking.end_time >= datetime.now(),
            Booking.status == "confirmed",
            Booking.space_id == space_id,
        )
        bookings = query.all()

        # Response formatting
        return [
            {"start_time": booking.start_time, "end_time": booking.end_time}
            for booking in bookings
        ]
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching taken bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@booking_router.get("/{booking_id}/payment", response_model=PaymentResponse)
async def pay_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Pay specified amount for a booking.
    """
    query = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.status == "pending",
        Booking.user_id == current_user.id,
    )
    booking = query.first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking with ID: {booking_id} not available for confirmation",
        )
    
    if not booking.tx_ref:
        tx_ref=create_random_key()
        booking.tx_ref = tx_ref
        db.commit()
        db.refresh(booking)

    return {
        "tx_ref": booking.tx_ref,
        "amount": booking.total_cost,
        "currency": "NGN",
        "customer": {
            "email": current_user.email, 
            "name": current_user.username,
            "phonenumber": current_user.phone_number
            },
        "customizations": {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
        }
    }

@booking_router.post("/{booking_id}/confirm", response_model=BookingConfirmationResponse)
async def confirm_booking_payment(
    booking_id: UUID,
    confirmation: ConfirmPayment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Confirm a booking payment and generate a receipt ID.
    """
    try:
        # Fetch and validate the booking
        query = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.status == "pending",
            Booking.user_id == current_user.id,
            Booking.tx_ref == confirmation.tx_ref
        )
        booking = query.first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with ID: {booking_id} and tx_ref {confirmation.tx_ref} not available for confirmation",
            )

        # Check for duplicate transactions
        existing_transaction = db.query(Booking).filter(
            Booking.transaction_id == confirmation.transaction_id
        ).first()
        if existing_transaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction ID already used",
            )

        # Update the booking status
        booking.status = "confirmed"
        booking.transaction_id = confirmation.transaction_id

        # Generate and store the receipt ID
        generate_and_store_receipt_id(db, booking)

        db.commit()
        db.refresh(booking)

        logger.info(f"Booking (ID: {booking_id}) confirmed with transaction ID: {confirmation.transaction_id}")

        return {
            "message": "Booking confirmed successfully",
            "booking_id": booking.id,
            "status": booking.status,
            "transaction_id": booking.transaction_id,
            "receipt_id": booking.receipt_id,  # Include the receipt ID in the response
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error confirming booking (ID: {booking_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@booking_router.get("/{booking_id}/receipt", response_model=ReceiptResponse)
async def get_booking_receipt(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch booking details for the receipt page.
    """
    try:
        # Fetch the booking with user and space details
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,  # Ensure the booking belongs to the user
        ).join(User).join(Space).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with ID: {booking_id} not found",
            )

        # Calculate duration
        duration = booking.end_time - booking.start_time
        duration_hours = duration.total_seconds() / 3600

        # Format the response
        response = {
            "receipt_no": booking.receipt_id,
            "company_name": "ReserveMe.com",
            "user": {
                "name": booking.user.username,
                "email": booking.user.email,
                "phone_number": booking.user.phone_number,
            },
            "space": {
                "name": booking.space.name,
                "location": booking.space.location,  # Assuming Space has an 'location' field
            },
            "booking": {
                "date": booking.start_time.strftime("%B %d, %Y"),  # Format: January 15, 2024
                "time": f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}",  # Format: 10:00 AM - 12:00 PM
                "duration": f"{duration_hours} hours",  # Format: 2 hours
                "purpose": booking.purpose,
            },
            "payment": {
                "amount": booking.total_cost,
                "status": booking.status,
                "transaction_id": booking.transaction_id,
                "payment_date": booking.created_at.strftime("%B %d, %Y %I:%M %p"),  # Format: January 15, 2024 10:05 AM
            },
            "footer": {
                "thank_you_message": "Thank you for booking with ReserveMe!",
                "support_email": "support@reserveme.com",
                "terms_and_conditions": "https://reserveme.com/terms",
            }
        }

        return response

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error fetching receipt for booking (ID: {booking_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

@booking_router.get("/admin/all", response_model=list[AdminBookingResponse])
async def admin_get_all_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """
    Fetch all bookings for admin review with pagination, including user and space details.
    """
    try:
        bookings = (
            db.query(Booking)
            .join(User, Booking.user_id == User.id)
            .join(Space, Booking.space_id == Space.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Map the results to the AdminBookingResponse schema
        return  [
            AdminBookingResponse(
                id=booking.id,
                receipt_id=booking.receipt_id,
                user_id=booking.user_id,
                username=booking.user.username,
                space_id=booking.space_id,
                space_name=booking.space.name,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status=booking.status,
                total_cost=booking.total_cost,
                purpose=booking.purpose,
                tx_ref=booking.tx_ref,
                transaction_id=booking.transaction_id,
                created_at=booking.created_at,
            )
            for booking in bookings
        ]
        
    except Exception as e:
        logger.error(f"Error fetching bookings for admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
