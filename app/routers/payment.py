# app/routers/payment.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models import User
from app.utils import (
    initialize_transaction,
    verify_transaction,
    get_transaction_details,
    list_transactions,
)
from app.schemas import (
    PaymentRequest, 
    PaymentResponse, 
    PaymentVerificationRequest
)
from app.database import get_db
from app.utils import logger

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post("/initialize", response_model=PaymentResponse)
def initialize_payment(payment_request: PaymentRequest, db: Session = Depends(get_db)):
    """
    Initializes a Paystack payment transaction.
    """
    try:
        response = initialize_transaction(
            email=payment_request.email,
            amount=payment_request.amount,
            callback_url=payment_request.callback_url,
        )
        return response["data"]
    except Exception as e:
        logger.error(f"Payment initialization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing payment.",
        )


@payment_router.post("/verify", response_model=dict)
def verify_payment(verification_request: PaymentVerificationRequest, db: Session = Depends(get_db)):
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


@payment_router.get("/details/{transaction_id}", response_model=dict)
def fetch_transaction_details(transaction_id: str, db: Session = Depends(get_db)):
    """
    Fetches details of a specific transaction by its ID.
    """
    try:
        response = get_transaction_details(transaction_id)
        return response["data"]
    except Exception as e:
        logger.error(f"Error fetching transaction details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching transaction details.",
        )


@payment_router.get("/list", response_model=list)
def list_all_transactions(db: Session = Depends(get_db)):
    """
    Lists all transactions.
    """
    try:
        response = list_transactions()
        return response["data"]
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing transactions.",
        )
