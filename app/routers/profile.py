# app/routers/profile.py.py

from fastapi import (
    HTTPException,
    Query,
    APIRouter,
    status,
    Depends
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import User
from app.utils import logger, get_current_user
from app.database import get_db
from app.schemas import (
    DetailResponse
)

profile_router = APIRouter(prefix="/me")


@profile_router.delete("/account", response_model=DetailResponse)
def delete_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Deletes a user along with their associated data.
    """
    target_user = db.query(User).filter(User.id == user.id).first()

    if not target_user:
        logger.warning(
            f"Attempted deletion of account with ID: {user.id} by user '{user.username}'."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(target_user)
    db.commit()
    logger.info(f"User '{user.id}' deleted account (ID: {user.id}).")
    return {"detail": f"Deleted account of '{target_user.username}' successfully"}
