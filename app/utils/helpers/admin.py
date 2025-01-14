from sqlalchemy.orm import Session
from app.models import User
from app.utils import hash_password, logger

def seed_admin(db: Session):
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Admin user created with email admin@example.com and password admin123")
    else:
        logger.info("Admin user already exists.")
