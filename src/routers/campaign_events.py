from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar, col  # Import the type wrapper

from commons.util import generate_clean_code
from database import get_session
from models.campaign_events import CampaignEvent, CampaignEventCreate, CampaignEventUpdate

router = APIRouter(prefix="/campaign_events", tags=["Campaign Events"])


# CREATE a new campaign_event
@router.post("/", response_model=CampaignEvent, status_code=status.HTTP_201_CREATED)
def create_campaign_event(campaign_event: CampaignEventCreate, session: Session = Depends(get_session)) -> CampaignEvent:
    # Convert the clean schema payload into the real DB Table format
    db_campaign_event = CampaignEvent.model_validate(campaign_event)
    try:
        session.add(db_campaign_event)
        session.commit()
        session.refresh(db_campaign_event)

        # Returns the created hero, which now safely includes the database-generated ID
        return db_campaign_event
    except IntegrityError as e:
        session.rollback()
        print(f"Error creating campaign_event: {e}")
        raise HTTPException(status_code=500, detail=f"Foreign Key error: {e.orig}")

# READ all campaign_events (with simple pagination limits)
@router.get("/", response_model=list[CampaignEvent])
def read_campaign_events(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(CampaignEvent).offset(offset).limit(limit)
    campaign_events = session.exec(statement).all()
    return campaign_events

# READ a single campaign_event by ID
@router.get("/{campaign_event_id}", response_model=CampaignEvent)
def read_campaign_event(campaign_event_id: int, session: Session = Depends(get_session)) -> CampaignEvent:
    campaign_event = session.get(CampaignEvent, campaign_event_id)
    if not campaign_event:
        raise HTTPException(status_code=404, detail="Campaign Event not found")
    return campaign_event.first()

# READ a single campaign_event by code
@router.get("/code/{campaign_event_code}", response_model=CampaignEvent)
def read_campaign_event_by_code(campaign_event_code: str, session: Session = Depends(get_session)) -> CampaignEvent:

    clean_code = generate_clean_code(campaign_event_code)
    # 1. Build the select statement filtering by the unique field
    statement: SelectOfScalar[CampaignEvent]  = cast(
        SelectOfScalar[CampaignEvent],
        select(CampaignEvent).where(col(CampaignEvent.campaign_event_code) == clean_code)
    )

    # 2. Execute the statement and get the first result or None
    campaign_event = session.exec(statement).first()
    if not campaign_event:
        raise HTTPException(status_code=404, detail="CampaignEvent not found")
    return campaign_event

# GET a multiple campaign_event by project_id
@router.get("/project/{project_id}", response_model=list[CampaignEvent])
def read_campaign_event_by_code(project_id: int, session: Session = Depends(get_session)) -> list[CampaignEvent]:

    # 1. Build the select statement filtering by the foreign key
    statement: SelectOfScalar[CampaignEvent] = cast(
        SelectOfScalar[CampaignEvent],
        select(CampaignEvent).where(col(CampaignEvent.project_id) == project_id)
    )

    # 2. Execute the statement and get the first result or None
    campaign_events = session.exec(statement)
    if not campaign_events:
        raise HTTPException(status_code=404, detail="CampaignEvents for Project Id not found")
    return list(campaign_events)

# PATCH/UPDATE an existing campaign_event
# Swagger UI will display a dynamic payload with NO ID field included.
@router.patch("{campaign_event_id}", response_model=CampaignEvent)
def update_campaign_event(campaign_event_id: int, updated_data: CampaignEventUpdate, session: Session = Depends(get_session)):
    # Look up the existing record in Postgres
    db_campaign_event = session.get(CampaignEvent, campaign_event_id)
    if not db_campaign_event:
        raise HTTPException(status_code=404, detail="CampaignEvent not found")

    # Extract only the data sent by the client, ignoring empty/unset values
    update_data = updated_data.model_dump(exclude_unset=True)

    # Merge the updated attributes onto our existing database record object
    for key, value in update_data.items():
        setattr(db_campaign_event, key, value)

    session.add(db_campaign_event)
    session.commit()
    session.refresh(db_campaign_event)
    return db_campaign_event

# 5. DELETE a campaign_event
@router.delete("/{campaign_event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign_event(campaign_event_id: int, session: Session = Depends(get_session)) -> None:
    campaign_event = session.get(CampaignEvent, campaign_event_id)
    if not campaign_event:
        raise HTTPException(status_code=404, detail="CampaignEvent not found")

    session.delete(campaign_event)
    session.commit()
