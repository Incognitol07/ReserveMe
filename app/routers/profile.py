# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import User
from app.utils import (
    logger, 
    get_current_user, 
    hash_password, 
    verify_password
)
from app.database import get_db
from app.schemas import (
    UserResponse, 
    DetailResponse, 
    UpdatePasswordRequest, 
    UpdateProfileRequest,
    UserLogin
)

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

@profile_router.delete("/", response_model=DetailResponse)
def delete_account(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Soft delete the currently authenticated user's account.
    """
    try:
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already deleted."
            )

        user.is_deleted = True
        user.is_active = False  # Mark the account inactive as well
        db.commit()
        logger.info(f"User ID {user.id} soft deleted their account.")
        return {"detail": "Account deleted successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user ID: {user.id} : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@profile_router.put("/update-password", response_model=DetailResponse)
def update_password(
    payload: UpdatePasswordRequest,  # Schema for request body
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Allows a user to update their password after verifying the current one.
    """
    try:
        if not verify_password(payload.current_password, user.password):
            logger.warning(f"Password update failed for user ID {user.id}: Incorrect password.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect."
            )

        user.password = hash_password(payload.new_password)
        db.commit()
        logger.info(f"User ID {user.id} updated their password.")
        return {"detail": "Password updated successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating password for user ID: {user.id} : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@profile_router.put("/update-profile", response_model=UserResponse)
def update_profile(
    payload: UpdateProfileRequest,  # Schema for request body
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update the user's profile information.
    """
    try:
        if payload.username and payload.username != user.username:
            db_user = db.query(User).filter(User.username == payload.username).first()
            if db_user:
                logger.warning(f"Attempt to register with an existing username: {db_user.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                    )
            user.username = payload.username
        if payload.email and payload.email != user.email:
            db_user = db.query(User).filter(User.email == payload.email).first()
            if db_user:
                logger.warning(f"Attempt to register with an existing email: {db_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            user.email = payload.email

        db.commit()
        logger.info(f"User ID {user.id} updated their profile.")
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating user ID: {user.id} : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@profile_router.post("/reactivate", response_model=DetailResponse)
def reactivate_account_with_password(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Reactivates a soft-deleted account using username and password verification.
    """
    try:
        # Fetch the user by username or email
        user = db.query(User).filter(User.email == user.email, User.is_deleted == True).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or account is not deactivated."
            )

        # Verify the provided password
        if not verify_password(user.password, hash_password(user.password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )

        # Reactivate the account
        user.is_deleted = False
        user.is_active = True
        db.commit()

        logger.info(f"User ID {user.id} reactivated their account.")
        return {"detail": f"Account for '{user.username}' has been reactivated successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error reactivating user ID: {user.id} : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")