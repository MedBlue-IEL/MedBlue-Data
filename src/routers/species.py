from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.species import Species, SpeciesCreate, SpeciesUpdate

router = APIRouter(prefix="/species", tags=["Species"])


# CREATE a new species
@router.post("/", response_model=Species, status_code=status.HTTP_201_CREATED)
def create_species(species: SpeciesCreate, session: Session = Depends(get_session)) -> Species:
    # Convert the clean schema payload into the real DB Table format
    db_species = Species.model_validate(species)
    try:
        session.add(db_species)
        session.commit()
        session.refresh(db_species)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_species
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating species: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all species (with simple pagination limits)
@router.get("/", response_model=list[Species])
def read_species(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Species).offset(offset).limit(limit)
    species = session.exec(statement).all()
    return species

# READ a single species by ID
@router.get("/{species_id}", response_model=Species)
def read_species(species_id: int, session: Session = Depends(get_session)) -> Species:
    species = session.get(Species, species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return species.first()

# READ a single species by name
@router.get("/name/{scientific_name}", response_model=Species)
def read_species_by_name(scientific_name: str, session: Session = Depends(get_session)) -> Species:

    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Species]  = cast(
        SelectOfScalar[Species],
        select(Species).where(col(Species.scientific_name) == scientific_name)
    )

    # 2. Execute the statement and get the first result or None
    species = session.exec(statement).first()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return species

# PATCH/UPDATE an existing species
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{species_id}", response_model=Species)
def update_species(species_id: int, updated_data: SpeciesUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_species = session.get(Species, species_id)
    if not db_species:
        raise HTTPException(status_code=404, detail="Species not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_species, key, value)

    session.add(db_species)
    session.commit()
    session.refresh(db_species)
    return db_species

# 5. DELETE a species
@router.delete("/{species_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_species(species_id: int, session: Session = Depends(get_session)) -> None:
    species = session.get(Species, species_id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")

    session.delete(species)
    session.commit()
