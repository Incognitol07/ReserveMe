# app/background_jobs/jobs.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Booking

def delete_old_pending_bookings():
    """
    Delete bookings that have been in a pending status for more than 24 hours.
    """
    db: Session = next(get_db())  # Get a database session
    try:
        # Calculate the cutoff time (24 hours ago)
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Query for pending bookings older than 24 hours
        old_pending_bookings = db.query(Booking).filter(
            Booking.status == "pending",
            Booking.created_at <= cutoff_time
        ).all()

        # Delete the old pending bookings
        for booking in old_pending_bookings:
            db.delete(booking)

        # Commit the changes
        db.commit()
        print(f"Deleted {len(old_pending_bookings)} old pending bookings.")

    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        print(f"Error deleting old pending bookings: {e}")

    finally:
        # Close the database session
        db.close()