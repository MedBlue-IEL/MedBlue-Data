from datetime import datetime
from enum import StrEnum

from pydantic import field_validator
from sqlalchemy import DateTime, func, UniqueConstraint
from typing import List
from sqlmodel import Field, SQLModel, Column, Enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code

class EventType(StrEnum):
    SAMPLING = "Muestreo"
    TRANSECT = "Transecto"
    OBSERVATION = "Observación"
    COMPILATION = "Compilación"

# Shared fields
class SamplingEventBase(SQLModel):
    sampling_code: str = Field(index=True, unique=False, max_length=255)
    campaign_id: int = Field(default=None, index=True, foreign_key="campaign_event.id")
    habitat_id: int | None = Field(default=None, index=True, foreign_key="habitat.id")
    station_geometry_id: int | None = Field(default=None, index=True, foreign_key="station_geometry.id")
    event_type: EventType | None = Field(
        sa_column=Column(
            Enum(EventType),
            default=None,
            nullable=True,
            index=False
        )
    )
    sampling_protocol: str = Field(index=False, unique=False, max_length=255)
    sample_size_value: float = Field(index=False, unique=False, max_length=255)
    sample_size_unit: str = Field(index=False, unique=False, max_length=255)
    start_date: datetime | None  = Field(default=None, index=False)
    end_date: datetime | None  = Field(default=None, index=False)
    sampling_remarks: str | None  = Field(default=None, index=False)

    # Use __table_args__ to cleanly declare a complex GIN index
    __table_args__ = (
        UniqueConstraint('sampling_code', 'campaign_id', name='unique_sampling_code_campaign_id', deferrable=True, initially='DEFERRED'),
    )

    @field_validator("sampling_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class SamplingEvent(SamplingEventBase, table=True):
    __tablename__ = "sampling_event"
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
class SamplingEventCreate(SamplingEventBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class SamplingEventUpdate(SQLModel):
    sampling_code: str | None = None
    campaign_id: int | None = None
    habitat_id: int | None = None
    station_geometry_id: int | None = None
    event_type: EventType | None = None
    sampling_protocol: str | None = None
    sample_size_value: float | None = None
    sample_size_unit: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    sampling_remarks: str | None = None


