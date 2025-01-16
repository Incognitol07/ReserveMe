# app/utils/helpers/admin.py

from sqlalchemy.orm import Session
from app.models import User
from app.utils import hash_password, logger

def seed_admin(db: Session):
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("Admin123"),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Admin user created with email admin@example.com and password Admin123")
    else:
        logger.info("Admin user already exists.")

def seed_user(db: Session):
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = User(
            username="user",
            email="user@example.com",
            password=hash_password("User1234")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User created with email user@example.com and password User123")
    else:
        logger.info("User already exists.")