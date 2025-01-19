# app/routers/space.py

from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends,
    UploadFile
)
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import Space
from app.utils import (
    logger,
    admin_required,
    upload_image_to_cloudinary
)
from app.database import get_db
from app.schemas import (
    SpaceResponse,
    SpaceCreateSchema,
    SpaceUpdateSchema,
    DetailResponse,
    SpaceImageResponse
)

space_router = APIRouter(prefix="/spaces")

@space_router.get("/", response_model=list[SpaceResponse])
async def get_all_spaces(db: Session = Depends(get_db)):
    """
    Fetch all spaces. Open to all users.
    """
    try:
        spaces = db.query(Space).all()
        # Modify the response to include only the first image URL
        for space in spaces:
            if isinstance(space.images, list) and space.images:
                space.images = [space.images[0]]  # Keep only the first image URL

        return spaces
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching spaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching spaces"
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


@space_router.post("/", dependencies=[Depends(admin_required)], response_model=SpaceResponse)
async def create_space(
    space_data: SpaceCreateSchema,
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
        return new_space
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating space",
        )

@space_router.post("/{space_id}/upload-image", dependencies=[Depends(admin_required)], response_model=SpaceImageResponse)
async def upload_space_image(
    space_id: UUID, 
    file: UploadFile, 
    db: Session = Depends(get_db),
):
    """
    Upload an image for a specific space and save the URL to the database.
    """
    try:
        space = db.query(Space).filter(Space.id == space_id).first()
        if not space:
            logger.warning(f"Space not found for ID: {space_id}")
            raise HTTPException(status_code=404, detail="Space not found")

        # Save file to a temporary location
        import tempfile
        import shutil

        # Create a temporary file using tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            file_path = temp_file.name


        # Upload image to Cloudinary
        image_url = upload_image_to_cloudinary(file_path)

        # Append the image URL to the space's images
        if not isinstance(space.images, list):
            space.images = []
        space.images.append(image_url)
        db.commit()

        logger.info(f"Image uploaded for space ID {space_id}: {image_url}")
        return {"message": "Image uploaded successfully", "image_url": image_url}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while uploading image for space ID {space_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading image to the database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@space_router.put("/{space_id}", dependencies=[Depends(admin_required)], response_model=SpaceResponse)
async def update_space(
    space_id: UUID,
    update_data: SpaceUpdateSchema,
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
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(space, key, value)
        db.commit()
        db.refresh(space)
        logger.info(f"Space updated: {space.name}")
        return space
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating space",
        )


@space_router.delete("/{space_id}", dependencies=[Depends(admin_required)], response_model=DetailResponse)
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
        return {"detail": "Space deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting space",
        )
