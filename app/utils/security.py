# app/utils/security.py

from jose import JWTError, jwt
from fastapi import HTTPException, status, HTTPException
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from pydantic import ValidationError
from app.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify a password against its hashed version
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"token_type": "access", "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for access",
            )
        return payload
    except JWTError as e:  # Unified JWTError handling
        error_msg = str(e).lower()
        if "expired" in error_msg:
            detail = "Token has expired"
        elif "invalid" in error_msg:
            detail = "Invalid token"
        else:
            detail = "Token verification failed"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Refresh token expiration time (e.g., 7 days)
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"token_type": "refresh", "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh",
            )
        return payload
    except JWTError as e:  # Unified JWTError handling
        error_msg = str(e).lower()
        if "expired" in error_msg:
            detail = "Refresh token has expired"
        else:
            detail = "Invalid refresh token"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# Password reset token expiration time (1 hour)
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 60


def create_password_reset_token(data: dict) -> str:
    """
    Create a password reset token with 1-hour expiration.

    Args:
        data: Dictionary containing user information (typically user_id)

    Returns:
        JWT token string for password reset
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"token_type": "password_reset", "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> dict:
    """
    Verify a password reset token and return the payload.

    Args:
        token: The password reset token to verify

    Returns:
        Dictionary containing the token payload

    Raises:
        HTTPException: If token is invalid, expired, or wrong type
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for password reset",
            )
        return payload
    except JWTError as e:  # Unified JWTError handling
        error_msg = str(e).lower()
        if "expired" in error_msg:
            detail = (
                "Password reset token has expired. Please request a new reset link."
            )
        elif "invalid" in error_msg:
            detail = "Invalid password reset token"
        else:
            detail = "Password reset token verification failed"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed password reset token",
        )
