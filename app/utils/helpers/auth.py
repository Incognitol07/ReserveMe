# app/utils/helpers/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import (
    User
)
from app.utils import (
    logger,
    verify_access_token
)
from app.database import get_db


# OAuth2 scheme to retrieve token from Authorization header
# The `tokenUrl` specifies the endpoint for obtaining a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependency to retrieve and verify the current user
# This will be used to secure routes that require user authentication
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieves the current authenticated user by verifying the provided token.

    Args: \n
        token (str): The authentication token passed in the Authorization header.
        db (Session): The database session to query user information.

    Raises:
        HTTPException: If token validation fails or the user cannot be found.

    Returns:
        User: The authenticated user object from the database.
    """
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Verify the token and retrieve user information
        payload = verify_access_token(token)
        if payload is None:
            logger.warning("Token validation failed for a request.")
            raise credentials_exception

        username: str = payload.get("sub")
        if username is None:
            logger.error("Invalid token payload: Missing 'sub' field.")
            raise credentials_exception

        # Query the user by username from the database
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            logger.warning(f"Unauthorized access attempt by unknown user '{username}'.")
            raise credentials_exception

        logger.info(f"User '{username}' authenticated successfully.")
        return db_user
    except Exception as e:
        logger.error(f"Error during user authentication: {e}")
        raise

async def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.is_admin == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return current_user