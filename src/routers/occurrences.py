from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.occurrences import Occurrence, OccurrenceCreate, OccurrenceUpdate

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


# CREATE a new occurrence
@router.post("/", response_model=Occurrence, status_code=status.HTTP_201_CREATED)
def create_occurrence(occurrence: OccurrenceCreate, session: Session = Depends(get_session)) -> Occurrence:
    # Convert the clean schema payload into the real DB Table format
    db_occurrence = Occurrence.model_validate(occurrence)
    try:
        session.add(db_occurrence)
        session.commit()
        session.refresh(db_occurrence)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_occurrence
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating occurrence: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all occurrences (with simple pagination limits)
@router.get("/", response_model=list[Occurrence])
def read_occurrences(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Occurrence).offset(offset).limit(limit)
    occurrences = session.exec(statement).all()
    return occurrences

# READ a single occurrence by ID
@router.get("/{occurrence_id}", response_model=Occurrence)
def read_occurrence(occurrence_id: int, session: Session = Depends(get_session)) -> Occurrence:
    occurrence = session.get(Occurrence, occurrence_id)
    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")
    return occurrence.first()

# READ a single occurrence by code
@router.get("/code/{occurrence_code}", response_model=Occurrence)
def read_occurrence_by_code(occurrence_code: str, session: Session = Depends(get_session)) -> Occurrence:

    clean_code = generate_clean_code(occurrence_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Occurrence]  = cast(
        SelectOfScalar[Occurrence],
        select(Occurrence).where(col(Occurrence.occurrence_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    occurrence = session.exec(statement).first()
    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")
    return occurrence

# GET multiple occurrence by sampling_id
@router.get("/sampling/{sampling_id}", response_model=list[Occurrence])
def read_occurrences_by_sampling_id(sampling_id: int, session: Session = Depends(get_session)) -> list[Occurrence]:

    # 1. Build the select statement filtering by the foreign key
    statement: SelectOfScalar[Occurrence] = cast(
        SelectOfScalar[Occurrence],
        select(Occurrence).where(col(Occurrence.sampling_id) == sampling_id)
    )

    # 2. Execute the statement and get the first result or None
    occurrences = session.exec(statement)
    if not occurrences:
        raise HTTPException(status_code=404, detail="Occurrences for Sampling Event Id not found")
    return list(occurrences)

# PATCH/UPDATE an existing occurrence
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{occurrence_id}", response_model=Occurrence)
def update_occurrence(occurrence_id: int, updated_data: OccurrenceUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_occurrence = session.get(Occurrence, occurrence_id)
    if not db_occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_occurrence, key, value)

    session.add(db_occurrence)
    session.commit()
    session.refresh(db_occurrence)
    return db_occurrence

# 5. DELETE a occurrence
@router.delete("/{occurrence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_occurrence(occurrence_id: int, session: Session = Depends(get_session)) -> None:
    occurrence = session.get(Occurrence, occurrence_id)
    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")

    session.delete(occurrence)
    session.commit()
