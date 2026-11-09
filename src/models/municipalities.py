from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path


# Shared fields
class MunicipalityBase(SQLModel):
    municipality_code: str = Field(index=True, unique=True, max_length=255)
    municipality_name: str = Field(index=False, unique=True, max_length=255)
    continent: str = Field(index=False, unique=False, max_length=255)
    water_body: str = Field(index=False, unique=False, max_length=255)
    country: str = Field(index=False, unique=False, max_length=255)
    country_code: str = Field(index=False, unique=False, max_length=255)
    state_province: str = Field(index=False, unique=False, max_length=255)
    county: str = Field(index=False, unique=False, max_length=255)
    inspireid: str = Field(index=False, unique=True, max_length=255)
    natlevel: str = Field(index=False, unique=False, max_length=255)
    netcode: str = Field(index=False, unique=False, max_length=255)
    codnut1: str = Field(index=False, unique=False, max_length=255)
    codnut2: str = Field(index=False, unique=False, max_length=255)
    codnut3: str = Field(index=False, unique=False, max_length=255)

# Includes database-specific logic and fields
class Municipality(MunicipalityBase, table=True):
    __tablename__ = "municipality"
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
class MunicipalityCreate(MunicipalityBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class MunicipalityUpdate(SQLModel):
    municipality_code: str | None = None
    municipality_name: str | None = None
    continent: str | None = None
    water_body: str | None = None
    country: str | None = None
    country_code: str | None = None
    state_province: str | None = None
    county: str | None = None
    inspireid: str | None = None
    natlevel: str | None = None
    netcode: str | None = None
    codnut1: str | None = None
    codnut2: str | None = None
