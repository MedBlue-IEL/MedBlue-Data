from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.habitats import Habitat, HabitatCreate, HabitatUpdate

router = APIRouter(prefix="/habitats", tags=["Habitats"])


# CREATE a new habitat
@router.post("/", response_model=Habitat, status_code=status.HTTP_201_CREATED)
def create_habitat(habitat: HabitatCreate, session: Session = Depends(get_session)) -> Habitat:
    # Convert the clean schema payload into the real DB Table format
    db_habitat = Habitat.model_validate(habitat)
    try:
        session.add(db_habitat)
        session.commit()
        session.refresh(db_habitat)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_habitat
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating habitat: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all habitats (with simple pagination limits)
@router.get("/", response_model=list[Habitat])
def read_habitats(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Habitat).offset(offset).limit(limit)
    habitats = session.exec(statement).all()
    return habitats

# READ a single habitat by ID
@router.get("/{habitat_id}", response_model=Habitat)
def read_habitat(habitat_id: int, session: Session = Depends(get_session)) -> Habitat:
    habitat = session.get(Habitat, habitat_id)
    if not habitat:
        raise HTTPException(status_code=404, detail="Habitat not found")
    return habitat.first()

# READ a single habitat by code
@router.get("/code/{habitat_code}", response_model=Habitat)
def read_habitat_by_code(habitat_code: str, session: Session = Depends(get_session)) -> Habitat:

    clean_code = generate_clean_code(habitat_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Habitat]  = cast(
        SelectOfScalar[Habitat],
        select(Habitat).where(col(Habitat.habitat_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    habitat = session.exec(statement).first()
    if not habitat:
        raise HTTPException(status_code=404, detail="Habitat not found")
    return habitat

# PATCH/UPDATE an existing habitat
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("{habitat_id}", response_model=Habitat)
def update_habitat(habitat_id: int, updated_data: HabitatUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_habitat = session.get(Habitat, habitat_id)
    if not db_habitat:
        raise HTTPException(status_code=404, detail="Habitat not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_habitat, key, value)

    session.add(db_habitat)
    session.commit()
    session.refresh(db_habitat)
    return db_habitat

# 5. DELETE a habitat
@router.delete("/{habitat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habitat(habitat_id: int, session: Session = Depends(get_session)) -> None:
    habitat = session.get(Habitat, habitat_id)
    if not habitat:
        raise HTTPException(status_code=404, detail="Habitat not found")

    session.delete(habitat)
    session.commit()
