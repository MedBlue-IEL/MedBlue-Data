from datetime import datetime
from enum import StrEnum

from pydantic import field_validator
from sqlalchemy import DateTime, func, UniqueConstraint
from sqlmodel import Field, SQLModel, Column, Enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code

class MeasurementType(StrEnum):
    DENSITY = "Densidad"
    LENGTH = "Longitud"
    COVERAGE = "Cobertura"
    WIDTH = "Anchura"

class ReefType(StrEnum):
    COASTAL_POOL = "Con charca litoral"
    LEDGE = "Cornisa"
    MICROATOLL = "Microatolón"
    MONOSTRATIFIED = "Monoestratificadas"
    DEAD = "Muertas"
    ABRASION_PLATFORM = "Sobre plataforma de abrasión"
    SUBMERGED = "Sumergidos"

class MeasurementUnitType(StrEnum):
    INDIVIDUALS_PER_CM2 = "individuos/25cm2"
    INDIVIDUALS_PER_C2 = "individuos/m2"
    BUNDLES_PER_M2 = "haces/m2"
    BUNDLES_PER_400CM2 = "haces/400cm2"
    CENTIMETERS = "cm"
    METERS = "m"
    PERCENTAGE = "porcentaje"
    PIXELS = "pixeles"

# Shared fields
class MeasurementBase(SQLModel):
    measurement_code: str = Field(index=True, unique=False, max_length=255)
    occurrence_id: int = Field(default=None, index=True, foreign_key="occurrence.id")
    reef_type: ReefType | None = Field(sa_column=Column(Enum(MeasurementType),
                                                                    default=None, nullable=True, index=False))
    measurement_type: MeasurementType = Field(sa_column=Column(Enum(MeasurementType),
                                                                    default=None, nullable=True, index=False))
    measurement_value: int = Field(default=None, index=False, max_length=255)
    measurement_unit: MeasurementUnitType = Field(sa_column=Column(Enum(MeasurementUnitType),
                                                                    default=None, nullable=True, index=False))
    measurement_determined_by: str | None = Field(default=None, index=False, max_length=255)
    start_date: datetime | None = Field(default=None, index=False)
    end_date: datetime | None = Field(default=None, index=False)
    measurement_remarks: str | None  = Field(default=None, index=False)
    reef_type_remarks: str | None  = Field(default=None, index=False)
    footprint_wtk: str | None  = Field(default=None, index=False)
    georeference_protocol: str | None  = Field(default=None, index=False)
    uuid: str | None  = Field(default=None, index=False)

    # Use __table_args__ to cleanly declare a complex GIN index
    __table_args__ = (
        UniqueConstraint('measurement_code', 'occurrence_id', name='unique_measurement_code_occurrence_id', deferrable=True, initially='DEFERRED'),
    )

    @field_validator("measurement_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class Measurement(MeasurementBase, table=True):
    __tablename__ = "measurement"
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
class MeasurementCreate(MeasurementBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class MeasurementUpdate(SQLModel):
    measurement_code: str | None = None
    occurrence_id: int | None = None
    reef_type: ReefType | None = None
    measurement_type: MeasurementType | None = None
    measurement_value: int | None = None
    measurement_unit: MeasurementUnitType  | None = None
    measurement_determined_by: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    measurement_remarks: str | None = None
    reef_type_remarks: str | None  = None
    footprint_wtk: str | None  = None
    georeference_protocol: str | None  = None
    uuid: str | None  = None
