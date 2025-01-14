# app/routers/space.py

from fastapi import (
    HTTPException,
    Query,
    APIRouter,
    status,
    Depends
)
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import Space, User
from app.utils import logger, get_current_user, admin_required
from app.database import get_db

space_router = APIRouter(prefix="/spaces")


@space_router.get("/")
async def get_all_spaces(db:Session = Depends(get_db)):
    spaces = db.query(Space).all()
    return spaces

@space_router.post("/", dependencies=[Depends(admin_required)])
async def create_space(db: Session = Depends(get_db)):
    ...


@space_router.get("/{space_id}")
async def get_space(
    space_id: UUID,
    db:Session = Depends(get_db)
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )
    return space

@space_router.get("/{space_id}")
async def update_space(
    space_id: UUID,
    update_space,
    db:Session = Depends(get_db)
):
    space = db.query(Space).filter(Space.id == space_id).first()

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )

    for key, value in update_space.model_dump().items():
        setattr(space, key, value)

    db.commit()
    db.refresh(space)
    return 


@space_router.delete("/{space_id}")
async def delete_space(
    space_id: UUID,
    db:Session = Depends(get_db)
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )

    return space