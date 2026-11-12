from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.carlit import Carlit, CarlitCreate, CarlitUpdate

router = APIRouter(prefix="/carlit", tags=["Carlit"])


# CREATE a new carlit
@router.post("/", response_model=Carlit, status_code=status.HTTP_201_CREATED)
def create_carlit(carlit: CarlitCreate, session: Session = Depends(get_session)) -> Carlit:
    # Convert the clean schema payload into the real DB Table format
    db_carlit = Carlit.model_validate(carlit)
    try:
        session.add(db_carlit)
        session.commit()
        session.refresh(db_carlit)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_carlit
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating carlit: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all carlit (with simple pagination limits)
@router.get("/", response_model=list[Carlit])
def read_carlit(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Carlit).offset(offset).limit(limit)
    carlit = session.exec(statement).all()
    return carlit

# READ a single carlit by ID
@router.get("/{carlit_id}", response_model=Carlit)
def read_carlit(carlit_id: int, session: Session = Depends(get_session)) -> Carlit:
    carlit = session.get(Carlit, carlit_id)
    if not carlit:
        raise HTTPException(status_code=404, detail="Carlit not found")
    return carlit.first()

# READ a single carlit by name
@router.get("/name/{carlit_name}", response_model=Carlit)
def read_carlit_by_name(carlit_name: str, session: Session = Depends(get_session)) -> Carlit:

    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[Carlit]  = cast(
        SelectOfScalar[Carlit],
        select(Carlit).where(col(Carlit.carlit_name) == carlit_name)
    )

    # 2. Execute the statement and get the first result or None
    carlit = session.exec(statement).first()
    if not carlit:
        raise HTTPException(status_code=404, detail="Carlit not found")
    return carlit

# PATCH/UPDATE an existing carlit
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{carlit_id}", response_model=Carlit)
def update_carlit(carlit_id: int, updated_data: CarlitUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_carlit = session.get(Carlit, carlit_id)
    if not db_carlit:
        raise HTTPException(status_code=404, detail="Carlit not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_carlit, key, value)

    session.add(db_carlit)
    session.commit()
    session.refresh(db_carlit)
    return db_carlit

# 5. DELETE a carlit
@router.delete("/{carlit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_carlit(carlit_id: int, session: Session = Depends(get_session)) -> None:
    carlit = session.get(Carlit, carlit_id)
    if not carlit:
        raise HTTPException(status_code=404, detail="Carlit not found")

    session.delete(carlit)
    session.commit()
