from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.stations import Station, StationCreate, StationUpdate

router = APIRouter(prefix="/stations", tags=["Stations"])


# CREATE a new station
@router.post("/", response_model=Station, status_code=status.HTTP_201_CREATED)
def create_station(station: StationCreate, session: Session = Depends(get_session)) -> Station:
    # Convert the clean schema payload into the real DB Table format
    db_station = Station.model_validate(station)
    try:
        session.add(db_station)
        session.commit()
        session.refresh(db_station)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_station
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating station: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all stations (with simple pagination limits)
@router.get("/", response_model=list[Station])
def read_stations(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Station).offset(offset).limit(limit)
    stations = session.exec(statement).all()
    return stations

# READ a single station by ID
@router.get("/{station_id}", response_model=Station)
def read_station(station_id: int, session: Session = Depends(get_session)) -> Station:
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station.first()

# READ a single station by code
@router.get("/code/{station_code}", response_model=Station)
def read_station_by_code(station_code: str, session: Session = Depends(get_session)) -> Station:

    clean_code = generate_clean_code(station_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Station]  = cast(
        SelectOfScalar[Station],
        select(Station).where(col(Station.station_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    station = session.exec(statement).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

# PATCH/UPDATE an existing station
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{station_id}", response_model=Station)
def update_station(station_id: int, updated_data: StationUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_station = session.get(Station, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_station, key, value)

    session.add(db_station)
    session.commit()
    session.refresh(db_station)
    return db_station

# 5. DELETE a station
@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(station_id: int, session: Session = Depends(get_session)) -> None:
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    session.delete(station)
    session.commit()
