# app/routers/payment.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models import User
from app.utils import (
    logger, 
    get_current_user,
    initialize_transaction,
    verify_transaction
)
from app.schemas import (
    PaymentRequest, 
    PaymentResponse, 
    PaymentVerificationRequest
)
from app.database import get_db
from app.config import settings

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post("/initialize", response_model=PaymentResponse)
def initialize_payment(
    payment_request: PaymentRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Initializes a Paystack payment transaction.
    """
    try:
        response = initialize_transaction(
            email=current_user.email,
            amount=payment_request.amount,
            callback_url=settings.PAYMENT_CALLBACK_URL,
        )
        return response["data"]
    except Exception as e:
        logger.error(f"Payment initialization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing payment.",
        )


@payment_router.post("/verify", response_model=dict)
def verify_payment(
    verification_request: PaymentVerificationRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Verifies a Paystack payment transaction.
    """
    try:
        response = verify_transaction(verification_request.reference)
        return response["data"]
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying payment.",
        )
