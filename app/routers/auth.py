from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import (
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    DetailResponse,
    RefreshResponse,
    RefreshToken
)
from app.models import (
    User
)
from app.utils import (
    logger,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from app.database import get_db

# Create an instance of APIRouter to handle authentication routes
auth_router = APIRouter()

# Register route to create a new user account
@auth_router.post("/register", response_model=RegisterResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Attempt to register with an existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password before storing
    password = hash_password(user.password)
    new_user = User(
        first_name = user.username,
        email = user.email, 
        password = password
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered successfully: '{new_user.username}' ({new_user.email}).")
    return {
        "first_name": new_user.username,
        "email": new_user.email,
        "message": "Registered successfully"
    }

# Login route for user authentication and token generation
@auth_router.post("/user/login", response_model=LoginResponse)
async def user_login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in a user by verifying the email and password, and returning a JWT access token.
    """
    # Query the database for the user and verify password
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        logger.warning(f"Failed login attempt for email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    logger.info(f"User '{db_user.id}' logged in successfully.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username,
    }

# Protected route example requiring authentication
@auth_router.get("/protected-route", response_model=DetailResponse)
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    A protected route that can only be accessed by authenticated users.
    """
    return {
        "detail": f"Hello, {current_user.username}! You have access to this protected route."
    }

@auth_router.post("/user/refresh-token", response_model=RefreshResponse)
async def get_refresh_token(token: RefreshToken, db: Session = Depends(get_db)):
    """
    Generate a new access token using a valid refresh token.
    """
    payload = verify_refresh_token(token.refresh_token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    # Verify user existence
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Generate new access token
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

# Login route for user authentication and token generation
@auth_router.post("/login", include_in_schema=False)
async def login_for_oauth_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    # Create and return the JWT access token
    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
