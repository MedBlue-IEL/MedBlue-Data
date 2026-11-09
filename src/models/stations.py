from enum import StrEnum
from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func, Column, Enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code

class StationType(StrEnum):
    POINT = "Punto"
    TRANSECT = "Transecto"
    SEGMENT = "Segmento"
    CELL = "Celda"
    POLYGON = "Polígono"
    SECTOR = "Sector"
    STRETCH = "Tramo"
    OTHER = "Otro"

# Shared fields
class StationBase(SQLModel):
    station_code: str = Field(index=True, unique=True, max_length=255)
    station_name: str = Field(index=False, unique=True, max_length=255)
    station_type: StationType = Field(
        sa_column=Column(
            Enum(StationType),
            default=None,
            nullable=True,
            index=False
        )
    )
    municipality_id: int | None = Field(default=None, index=True, foreign_key="municipality.id")
    locality: str = Field(index=False, unique=False, max_length=255)
    location_remarks: str = Field(index=False, unique=False, max_length=255)
    minimum_elevation_in_meters: float = Field(index=False, unique=False, max_length=255)
    maximum_elevation_in_meters: float = Field(index=False, unique=False, max_length=255)
    vertical_datum: str = Field(index=False, unique=False, max_length=255)
    minimum_depth_in_meters: float = Field(index=False, unique=False, max_length=255)
    maximum_depth_in_meters: float = Field(index=False, unique=False, max_length=255)
    verbatim_coordinates: str = Field(index=False, unique=False, max_length=255)
    verbatim_coordinate_system: str = Field(index=False, unique=False, max_length=255)
    verbatim_srs: str = Field(index=False, unique=False, max_length=255)
    decimal_latitude: float = Field(index=False, unique=False, max_length=255)
    decimal_longitude: float = Field(index=False, unique=False, max_length=255)
    geodetic_datum: str = Field(index=False, unique=False, max_length=255)
    coordinate_uncertainty_in_meters: float = Field(index=False, unique=False, max_length=255)
    coordinate_precision: float = Field(index=False, unique=False, max_length=255)
    footprint_wtk: str = Field(index=False, unique=False, max_length=255)
    utm10x10km: str = Field(index=False, unique=False, max_length=255)
    utm1x1km: str = Field(index=False, unique=False, max_length=255)
    footprint_srs: str = Field(index=False, unique=False, max_length=255)
    georeferenced_by: str = Field(index=False, unique=False, max_length=255)
    georeferenced_date: datetime | None = Field(default=None, index=False)
    georeference_protocol: str = Field(index=False, unique=False, max_length=255)
    georeference_sources: str = Field(index=False, unique=False, max_length=255)
    georeference_remarks: str = Field(index=False, unique=False, max_length=255)

    @field_validator("station_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class Station(StationBase, table=True):
    __tablename__ = "station"
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
class StationCreate(StationBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class StationUpdate(SQLModel):
    station_code: str | None = None
    station_name: str | None = None
    station_type: StationType | None = None
    municipality_id: int | None = None
    locality: str | None = None
    location_remarks: str | None = None
    minimum_elevation_in_meters: float | None = None
    maximum_elevation_in_meters: float | None = None
    vertical_datum: str | None = None
    minimum_depth_in_meters: float | None = None
    maximum_depth_in_meters: float | None = None
    verbatim_coordinates: str | None = None
    verbatim_coordinate_system: str | None = None
    verbatim_srs: str | None = None
    decimal_latitude: float | None = None
    decimal_longitude: float | None = None
    geodetic_datum: str | None = None
    coordinate_uncertainty_in_meters: float | None = None
    coordinate_precision: float | None = None
    footprint_wtk: str | None = None
    utm10x10km: str | None = None
    utm1x1km: str | None = None
    footprint_srs: str | None = None
    georeferenced_by: str | None = None
    georeferenced_date: datetime | None = None
    georeference_protocol: str | None = None
    georeference_sources: str | None = None
    georeference_remarks: str | None = None
