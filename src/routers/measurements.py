from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.measurements import Measurement, MeasurementCreate, MeasurementUpdate

router = APIRouter(prefix="/measurements", tags=["Measurements"])


# CREATE a new measurement
@router.post("/", response_model=Measurement, status_code=status.HTTP_201_CREATED)
def create_measurement(measurement: MeasurementCreate, session: Session = Depends(get_session)) -> Measurement:
    # Convert the clean schema payload into the real DB Table format
    db_measurement = Measurement.model_validate(measurement)
    try:
        session.add(db_measurement)
        session.commit()
        session.refresh(db_measurement)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_measurement
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating measurement: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all measurements (with simple pagination limits)
@router.get("/", response_model=list[Measurement])
def read_measurements(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Measurement).offset(offset).limit(limit)
    measurements = session.exec(statement).all()
    return measurements

# READ a single measurement by ID
@router.get("/{measurement_id}", response_model=Measurement)
def read_measurement(measurement_id: int, session: Session = Depends(get_session)) -> Measurement:
    measurement = session.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement.first()

# GET multiple measurement by occurrence_id
@router.get("/occurrence/{occurrence_id}", response_model=list[Measurement])
def read_measurements_by_occurrence_id(occurrence_id: int, session: Session = Depends(get_session)) -> list[Measurement]:

    # 1. Build the select statement filtering by the foreign key
    statement: SelectOfScalar[Measurement] = cast(
        SelectOfScalar[Measurement],
        select(Measurement).where(col(Measurement.occurrence_id) == occurrence_id)
    )

    # 2. Execute the statement and get the first result or None
    measurements = session.exec(statement)
    if not measurements:
        raise HTTPException(status_code=404, detail="Measurements for Occurrence Id not found")
    return list(measurements)

# PATCH/UPDATE an existing measurement
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{measurement_id}", response_model=Measurement)
def update_measurement(measurement_id: int, updated_data: MeasurementUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_measurement = session.get(Measurement, measurement_id)
    if not db_measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_measurement, key, value)

    session.add(db_measurement)
    session.commit()
    session.refresh(db_measurement)
    return db_measurement

# 5. DELETE a measurement
@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(measurement_id: int, session: Session = Depends(get_session)) -> None:
    measurement = session.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")

    session.delete(measurement)
    session.commit()
