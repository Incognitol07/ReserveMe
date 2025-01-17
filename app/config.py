# app/config.py

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ReserveMe API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # Default to 'development'
    DEBUG: bool = ENVIRONMENT == "development"

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # JWT and authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET")

    # Cloudinary
    CLOUDINARY_CLOUD: str = os.getenv("CLOUDINARY_CLOUD")
    CLOUDINARY_API_KEY: str= os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str= os.getenv("CLOUDINARY_API_SECRET")

    # Other security settings
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]  # Add frontend URL if applicable

# Instantiate settings
settings = Settings()
