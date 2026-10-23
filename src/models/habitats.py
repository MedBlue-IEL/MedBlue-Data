from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel, text
from sqlalchemy import DateTime, func

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code


# Shared fields
class HabitatBase(SQLModel):
    habitat_code: str = Field(index=True, unique=True, max_length=255)
    habitat_name: str = Field(index=False, unique=True, max_length=255)

    @field_validator("habitat_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class Habitat(HabitatBase, table=True):
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
class HabitatCreate(HabitatBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class HabitatUpdate(SQLModel):
    habitat_id: str | None = None
    habitat_name: str | None = None
