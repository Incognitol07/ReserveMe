# app/utils/helpers/cloudinary.py
from app.utils import cloudinary  # This ensures the config is set

from cloudinary.uploader import upload

def upload_image_to_cloudinary(file_path: str) -> str:
    """
    Uploads an image to Cloudinary and returns the secure URL.
    """
    response = upload(file_path)
    return response["secure_url"]
