# app/utils/cloudinary.py

import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)