from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base, get_db
from app.config import settings
from app.utils import logger, seed_admin
from app.routers import (
    auth_router, 
    space_router, 
    booking_router,
    profile_router
)
from app.background_tasks import scheduler, start_scheduler
import time


# Create the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    logger.info("Starting up the application...")
    Base.metadata.create_all(bind=engine)  # Initialize database (create tables if they don't exist)
    start_scheduler()
    # Seed the users
    seed_admin()  # Call the function to seed admin
    try:
        yield
    finally:
        scheduler.shutdown()
        logger.info("Shutting down the application...")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version="1.0.0",
    debug=settings.DEBUG,  # Enable debug mode if in development
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)


# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Strictly enforce trusted origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],  # Limit allowed headers
)


# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(space_router, tags=["Spaces"])
app.include_router(booking_router, tags=["Bookings"])

# Middleware to log route endpoints with client IP
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Extract real client IP
    client_ip = request.headers.get("X-Forwarded-For") or request.headers.get("X-Real-IP") or request.client.host
    endpoint = request.url.path
    method = request.method
    
    logger.info(f"Request: {method} {endpoint} from {client_ip}")
    
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"Response: {method} {endpoint} from {client_ip} returned {response.status_code} in {duration:.2f}s"
    )
    return response


# Root endpoint for health check
@app.get("/", tags=["Health"])
def read_root():
    return {"message": f"{settings.APP_NAME} is running"}