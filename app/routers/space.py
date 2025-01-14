# app/routers/space.py

from fastapi import (
    HTTPException,
    Query,
    APIRouter,
    status,
    Depends,
    Body,
)
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import Space
from app.utils import logger, get_current_user, admin_required
from app.database import get_db
from app.schemas import (
    SpaceResponse,
    SpaceCreateSchema,
    SpaceUpdateSchema
)

space_router = APIRouter(prefix="/spaces")


@space_router.get("/", response_model=list[SpaceResponse])
async def get_all_spaces(db: Session = Depends(get_db)):
    """
    Fetch all spaces. Open to all users.
    """
    try:
        spaces = db.query(Space).all()
        return spaces
    except SQLAlchemyError as e:
        logger.error(f"Error fetching spaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching spaces",
        )


@space_router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(space_id: UUID, db: Session = Depends(get_db)):
    """
    Fetch a specific space by ID. Open to all users.
    """
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )
    return space


@space_router.post("/", dependencies=[Depends(admin_required)])
async def create_space(
    space_data: SpaceCreateSchema = Body(...),
    db: Session = Depends(get_db),
):
    """
    Create a new space. Admin only.
    """
    try:
        new_space = Space(**space_data.model_dump())
        db.add(new_space)
        db.commit()
        db.refresh(new_space)
        logger.info(f"Space created: {new_space.name}")
        return {"message": "Space created successfully", "space": new_space}
    except SQLAlchemyError as e:
        logger.error(f"Error creating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating space",
        )


@space_router.put("/{space_id}", dependencies=[Depends(admin_required)])
async def update_space(
    space_id: UUID,
    update_data: SpaceUpdateSchema = Body(...),
    db: Session = Depends(get_db),
):
    """
    Update an existing space. Admin only.
    """
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )
    try:
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(space, key, value)
        db.commit()
        db.refresh(space)
        logger.info(f"Space updated: {space.name}")
        return {"message": "Space updated successfully", "space": space}
    except SQLAlchemyError as e:
        logger.error(f"Error updating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating space",
        )


@space_router.delete("/{space_id}", dependencies=[Depends(admin_required)])
async def delete_space(space_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a space by ID. Admin only.
    """
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Space not found"
        )
    try:
        db.delete(space)
        db.commit()
        logger.info(f"Space deleted: {space.name}")
        return {"message": "Space deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Error deleting space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting space",
        )
