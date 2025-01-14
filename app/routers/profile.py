# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.models import User
from app.utils import logger, get_current_user, hash_password, verify_password
from app.database import get_db
from app.schemas import UserResponse, DetailResponse

profile_router = APIRouter(prefix="/me")

@profile_router.get("/", response_model=UserResponse)
def get_profile(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Retrieve the currently authenticated user's profile.
    """
    return user


@profile_router.put("/update-password", response_model=DetailResponse)
def update_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Allows a user to update their password after verifying the current one.
    """
    if not verify_password(current_password, user.password):
        logger.warning(f"Password update failed for user ID {user.id}: Incorrect password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect."
        )

    user.password = hash_password(new_password)
    db.commit()
    logger.info(f"User ID {user.id} updated their password.")
    return {"detail": "Password updated successfully."}


@profile_router.put("/update-profile", response_model=UserResponse)
def update_profile(
    username: str | None = Body(None, embed=True),
    email: str | None = Body(None, embed=True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update the user's profile information.
    """
    if username:
        user.username = username
    if email:
        user.email = email

    db.commit()
    logger.info(f"User ID {user.id} updated their profile.")
    return user


@profile_router.put("/reactivate", response_model=DetailResponse)
def reactivate_account(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Reactivates a user's deactivated account.
    """
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Account is already active."
        )

    user.is_active = True
    db.commit()
    logger.info(f"User ID {user.id} reactivated their account.")
    return {"detail": f"Account '{user.username}' reactivated successfully."}