from typing import Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import get_session
from models.assets import Asset, AssetCreate, AssetUpdate

router = APIRouter(prefix="/assets", tags=["Assets"])


# CREATE a new asset
@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate, session: Session = Depends(get_session)) -> Asset:
    # Convert the clean schema payload into the real DB Table format
    db_asset = Asset.model_validate(asset)
    try:
        session.add(db_asset)
        session.commit()
        session.refresh(db_asset)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_asset
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating asset: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all assets (with simple pagination limits)
@router.get("/", response_model=list[Asset])
def read_assets(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Asset).offset(offset).limit(limit)
    assets = session.exec(statement).all()
    return assets


# READ a single asset by ID
@router.get("/{asset_id}", response_model=Asset)
def read_asset(asset_id: UUID, session: Session = Depends(get_session)) -> Type[Asset]:
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

# PATCH/UPDATE an existing asset
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{asset_id}", response_model=Asset)
def update_asset(asset_id: UUID, updated_data: AssetUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_asset = session.get(Asset, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_asset, key, value)

    session.add(db_asset)
    session.commit()
    session.refresh(db_asset)
    return db_asset

# 5. DELETE an asset
@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: UUID, session: Session = Depends(get_session)) -> None:
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    session.delete(asset)
    session.commit()
