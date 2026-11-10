from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

import uuid
from database import get_session
from models.station_geometries import StationGeometry, StationGeometryCreate, StationGeometryUpdate

router = APIRouter(prefix="/station_geometries", tags=["StationGeometries"])


# CREATE a new station_geometry
@router.post("/", response_model=StationGeometry, status_code=status.HTTP_201_CREATED)
def create_station_geometry(station_geometry: StationGeometryCreate, session: Session = Depends(get_session)) -> StationGeometry:
    # Convert the clean schema payload into the real DB Table format
    db_station_geometry = StationGeometry.model_validate(station_geometry)
    try:
        session.add(db_station_geometry)
        session.commit()
        session.refresh(db_station_geometry)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_station_geometry
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating station_geometry: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all station_geometries (with simple pagination limits)
@router.get("/", response_model=list[StationGeometry])
def read_station_geometries(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(StationGeometry).offset(offset).limit(limit)
    station_geometries = session.exec(statement).all()
    return station_geometries

# READ a single station_geometry by ID
@router.get("/{station_geometry_id}", response_model=StationGeometry)
def read_station_geometry(station_geometry_id: int, session: Session = Depends(get_session)) -> StationGeometry:
    station_geometry = session.get(StationGeometry, station_geometry_id)
    if not station_geometry:
        raise HTTPException(status_code=404, detail="StationGeometry not found")
    return station_geometry.first()

# READ a single station_geometry by uuid
@router.get("/code/{station_geometry_uuid}", response_model=StationGeometry)
def read_station_geometry_by_uuid(station_geometry_uuid: uuid.UUID, session: Session = Depends(get_session)) -> StationGeometry:

    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[StationGeometry]  = cast(
        SelectOfScalar[StationGeometry],
        select(StationGeometry).where(col(StationGeometry.uuid) == station_geometry_uuid)
    )

    # 2. Execute the statement and get the first result or None
    station_geometry = session.exec(statement).first()
    if not station_geometry:
        raise HTTPException(status_code=404, detail="StationGeometry not found")
    return station_geometry

# PATCH/UPDATE an existing station_geometry
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{station_geometry_id}", response_model=StationGeometry)
def update_station_geometry(station_geometry_id: int, updated_data: StationGeometryUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_station_geometry = session.get(StationGeometry, station_geometry_id)
    if not db_station_geometry:
        raise HTTPException(status_code=404, detail="StationGeometry not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_station_geometry, key, value)

    session.add(db_station_geometry)
    session.commit()
    session.refresh(db_station_geometry)
    return db_station_geometry

# 5. DELETE a station_geometry
@router.delete("/{station_geometry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station_geometry(station_geometry_id: int, session: Session = Depends(get_session)) -> None:
    station_geometry = session.get(StationGeometry, station_geometry_id)
    if not station_geometry:
        raise HTTPException(status_code=404, detail="StationGeometry not found")

    session.delete(station_geometry)
    session.commit()
