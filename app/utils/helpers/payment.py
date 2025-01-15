# app/utils/helpers/payment.py

import requests
from app.config import settings
from fastapi import HTTPException, status

SECRET_KEY = settings.PAYSTACK_SECRET_KEY

BASE_URL = "https://api.paystack.co"


def initialize_transaction(email, amount, callback_url):
    """
    Initializes a Paystack payment transaction.
    """
    url = f"{BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": amount,  # Amount is in kobo
        "callback_url": callback_url,
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.json().get("message", "Failed to initialize payment"),
        )


def verify_transaction(reference):
    """
    Verifies the status of a transaction using Paystack.
    """
    url = f"{BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.json().get("message", "Failed to verify payment"),
        )


def get_transaction_details(transaction_id):
    """
    Retrieves details of a specific transaction by its ID.
    """
    url = f"{BASE_URL}/transaction/{transaction_id}"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.json().get("message", "Failed to fetch transaction details"),
        )


def list_transactions():
    """
    Lists all transactions on the Paystack account.
    """
    url = f"{BASE_URL}/transaction"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.json().get("message", "Failed to fetch transactions"),
        )
