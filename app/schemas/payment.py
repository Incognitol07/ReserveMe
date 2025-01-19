# app/schemas/payment.py

from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: int


class PaymentResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class PaymentVerificationRequest(BaseModel):
    reference: str
