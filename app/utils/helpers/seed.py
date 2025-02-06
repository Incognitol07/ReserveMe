# app/utils/helpers/admin.py

from app.models import User
from app.utils import hash_password, logger
from app.database import get_db
from app.config import settings

def seed_admin():
    db = next(get_db())
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password=hash_password(settings.ADMIN_PASSWORD),
            phone_number = settings.ADMIN_PHONE,
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists.")
