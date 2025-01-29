# app/background_jobs/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .jobs import delete_old_pending_bookings  # Import the new function

scheduler = BackgroundScheduler()

def start_scheduler():
    # Add the job to delete old pending bookings
    scheduler.add_job(delete_old_pending_bookings, IntervalTrigger(hours=1))  # Run every hour
    print("Starting the scheduler...")
    # Start the scheduler
    scheduler.start()