# app/main.py

from fastapi import (
    FastAPI,
    Request
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.config import settings
from app.utils import logger
from app.routers import (
    auth_router,
    space_router,
    booking_router
)


# Create the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    print("Starting up the application...")
    # Initialize database (create tables if they don't exist)
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        print("Shutting down the application...")

app = FastAPI(
    title=settings.APP_NAME,
    description="An API",
    version="1.0.0",
    debug=settings.DEBUG,  # Enable debug mode if in development
    lifespan=lifespan,
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(space_router, tags=["Spaces"])
app.include_router(booking_router, tags=["Bookings"])


# Middleware to log route endpoints
@app.middleware("http")
async def log_requests(request: Request, call_next):
    endpoint = request.url.path
    method = request.method
    client_ip = request.client.host

    logger.info(f"Request: {method} {endpoint} from {client_ip}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {method} {endpoint} returned {response.status_code}")
    return response



# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": f"{settings.APP_NAME} is running"}
