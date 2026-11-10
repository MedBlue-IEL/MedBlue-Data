from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.municipalities import Municipality, MunicipalityCreate, MunicipalityUpdate

router = APIRouter(prefix="/municipalities", tags=["Municipalities"])


# CREATE a new municipality
@router.post("/", response_model=Municipality, status_code=status.HTTP_201_CREATED)
def create_municipality(municipality: MunicipalityCreate, session: Session = Depends(get_session)) -> Municipality:
    # Convert the clean schema payload into the real DB Table format
    db_municipality = Municipality.model_validate(municipality)
    try:
        session.add(db_municipality)
        session.commit()
        session.refresh(db_municipality)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_municipality
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating municipality: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all municipalities (with simple pagination limits)
@router.get("/", response_model=list[Municipality])
def read_municipalities(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Municipality).offset(offset).limit(limit)
    municipalities = session.exec(statement).all()
    return municipalities

# READ a single municipality by ID
@router.get("/{municipality_id}", response_model=Municipality)
def read_municipality(municipality_id: int, session: Session = Depends(get_session)) -> Municipality:
    municipality = session.get(Municipality, municipality_id)
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return municipality.first()

# READ a single municipality by code
@router.get("/code/{municipality_code}", response_model=Municipality)
def read_municipality_by_code(municipality_code: str, session: Session = Depends(get_session)) -> Municipality:

    clean_code = generate_clean_code(municipality_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Municipality]  = cast(
        SelectOfScalar[Municipality],
        select(Municipality).where(col(Municipality.municipality_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    municipality = session.exec(statement).first()
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return municipality

# PATCH/UPDATE an existing municipality
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{municipality_id}", response_model=Municipality)
def update_municipality(municipality_id: int, updated_data: MunicipalityUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_municipality = session.get(Municipality, municipality_id)
    if not db_municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_municipality, key, value)

    session.add(db_municipality)
    session.commit()
    session.refresh(db_municipality)
    return db_municipality

# 5. DELETE a municipality
@router.delete("/{municipality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_municipality(municipality_id: int, session: Session = Depends(get_session)) -> None:
    municipality = session.get(Municipality, municipality_id)
    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")

    session.delete(municipality)
    session.commit()
