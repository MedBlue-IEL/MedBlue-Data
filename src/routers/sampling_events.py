from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.sampling_events import SamplingEvent, SamplingEventCreate, SamplingEventUpdate

router = APIRouter(prefix="/sampling_events", tags=["Sampling Events"])


# CREATE a new sampling_event
@router.post("/", response_model=SamplingEvent, status_code=status.HTTP_201_CREATED)
def create_sampling_event(sampling_event: SamplingEventCreate, session: Session = Depends(get_session)) -> SamplingEvent:
    # Convert the clean schema payload into the real DB Table format
    db_sampling_event = SamplingEvent.model_validate(sampling_event)
    try:
        session.add(db_sampling_event)
        session.commit()
        session.refresh(db_sampling_event)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_sampling_event
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating sampling_event: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all sampling_events (with simple pagination limits)
@router.get("/", response_model=list[SamplingEvent])
def read_sampling_events(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(SamplingEvent).offset(offset).limit(limit)
    sampling_events = session.exec(statement).all()
    return sampling_events

# READ a single sampling_event by ID
@router.get("/{sampling_id}", response_model=SamplingEvent)
def read_sampling_event(sampling_id: int, session: Session = Depends(get_session)) -> SamplingEvent:
    sampling_event = session.get(SamplingEvent, sampling_id)
    if not sampling_event:
        raise HTTPException(status_code=404, detail="Sampling Event not found")
    return sampling_event.first()

# READ a single sampling_event by code
@router.get("/code/{sampling_code}", response_model=SamplingEvent)
def read_sampling_event_by_code(sampling_code: str, session: Session = Depends(get_session)) -> SamplingEvent:

    clean_code = generate_clean_code(sampling_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[SamplingEvent]  = cast(
        SelectOfScalar[SamplingEvent],
        select(SamplingEvent).where(col(SamplingEvent.sampling_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    sampling_event = session.exec(statement).first()
    if not sampling_event:
        raise HTTPException(status_code=404, detail="SamplingEvent not found")
    return sampling_event

# GET multiple sampling_event by campaign_id
@router.get("/campaign/{campaign_id}", response_model=list[SamplingEvent])
def read_sampling_events_by_campaign_id(campaign_id: int, session: Session = Depends(get_session)) -> list[SamplingEvent]:

    # 1. Build the select statement filtering by the foreign key
    statement: SelectOfScalar[SamplingEvent] = cast(
        SelectOfScalar[SamplingEvent],
        select(SamplingEvent).where(col(SamplingEvent.campaign_id) == campaign_id)
    )

    # 2. Execute the statement and get the first result or None
    sampling_events = session.exec(statement)
    if not sampling_events:
        raise HTTPException(status_code=404, detail="Sampling Events for Campaign Event Id not found")
    return list(sampling_events)

# PATCH/UPDATE an existing sampling_event
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("/{sampling_id}", response_model=SamplingEvent)
def update_sampling_event(sampling_id: int, updated_data: SamplingEventUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_sampling_event = session.get(SamplingEvent, sampling_id)
    if not db_sampling_event:
        raise HTTPException(status_code=404, detail="SamplingEvent not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_sampling_event, key, value)

    session.add(db_sampling_event)
    session.commit()
    session.refresh(db_sampling_event)
    return db_sampling_event

# 5. DELETE a sampling_event
@router.delete("/{sampling_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sampling_event(sampling_id: int, session: Session = Depends(get_session)) -> None:
    sampling_event = session.get(SamplingEvent, sampling_id)
    if not sampling_event:
        raise HTTPException(status_code=404, detail="SamplingEvent not found")

    session.delete(sampling_event)
    session.commit()
