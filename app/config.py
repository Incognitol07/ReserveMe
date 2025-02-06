# app/config.py

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str
    APP_DESCRIPTION: str= "ReserveMe simplifies the process of booking and managing spaces, such as meeting rooms, event halls, or workspaces."
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    DEBUG: bool = ENVIRONMENT == "development"

    DATABASE_URL: str

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_PHONE: str

    ADMIN_NAME: str

    # JWT and authentication settings
    JWT_SECRET_KEY: str

    # Other security settings
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]  # Add frontend URL if applicable

    class Config:
        env_file =".env"

# Instantiate settings
settings = Settings()
