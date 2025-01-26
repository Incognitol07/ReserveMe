# app/config.py

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ReserveMe API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    DEBUG: bool = ENVIRONMENT == "development"

    DATABASE_URL: str

    # JWT and authentication settings
    JWT_SECRET_KEY: str

    # Cloudinary
    CLOUDINARY_CLOUD: str 
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str    

    # Other security settings
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]  # Add frontend URL if applicable

    class Config:
        env_file =".env"

# Instantiate settings
settings = Settings()
