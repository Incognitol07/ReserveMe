# app/schemas/payment.py

from pydantic import BaseModel

class PaymentRequest(BaseModel):
    email: str
    amount: int  # Amount in kobo
    callback_url: str


class PaymentResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class PaymentVerificationRequest(BaseModel):
    reference: str
