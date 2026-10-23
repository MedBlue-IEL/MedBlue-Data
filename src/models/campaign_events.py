from datetime import datetime

from pydantic import field_validator
from sqlalchemy import DateTime, func
from typing import List
from sqlmodel import Field, SQLModel, Column, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Integer
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code


# Shared fields
class CampaignEventBase(SQLModel):
    campaign_code: str = Field(index=True, unique=True, max_length=255)
    campaign_name: str = Field(index=False, unique=True, max_length=255)
    start_date: datetime | None  = Field(default=None, index=False)
    end_date: datetime | None  = Field(default=None, index=False)
    campaign_remarks: str | None  = Field(default=None, index=False)
    project_id: int | None = Field(default=None, index=True, foreign_key="project.id")
    habitat_ids: List[int] = Field(
        default=[],
        sa_column=Column(ARRAY(Integer), server_default="{}")
    )

    # Use __table_args__ to cleanly declare a complex GIN index
    __table_args__ = (
        Index(
            "idx_campaign_event_habitat_ids",  # Index Name
            "habitat_ids",                     # Column name string
            postgresql_using="gin"             # Index type
        ),
    )

    @field_validator("campaign_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class CampaignEvent(CampaignEventBase, table=True):
    __tablename__ = "campaign_event"
    id: int | None = Field(default=None, primary_key=True)
    created: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )
    modified: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )

# Exactly what shows up in Swagger POST documentation (No ID!)
class CampaignEventCreate(CampaignEventBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class CampaignEventUpdate(SQLModel):
    campaign_id: str | None = None
    campaign_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    campaign_remarks: str | None = None

