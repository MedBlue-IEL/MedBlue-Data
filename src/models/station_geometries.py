from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func

import os
import sys
import uuid
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path


# Shared fields
class StationGeometryBase(SQLModel):
    station_id: int | None = Field(default=None, index=True, foreign_key="station.id")
    uuid: uuid.UUID = Field(default=None, index=True, unique=True)
    remarks: str = Field(index=False, unique=False, max_length=255)

# Includes database-specific logic and fields
class StationGeometry(StationGeometryBase, table=True):
    __tablename__ = "station_geometry"
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
class StationGeometryCreate(StationGeometryBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class StationGeometryUpdate(SQLModel):
    station_id: int | None = None
    uuid: uuid.UUID | None = None
    remarks: str | None = None
