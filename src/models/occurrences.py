from datetime import datetime
from enum import StrEnum

from pydantic import field_validator
from sqlalchemy import DateTime, func, UniqueConstraint
from sqlmodel import Field, SQLModel, Column, Enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code

class OccurrenceType(StrEnum):
    SPECIES = "Especie"
    CARLIT = "CARLIT"

class BasisOfRecordType(StrEnum):
    PRESERVED_SPECIMEN = "PreservedSpecimen"
    LIVING_SPECIMEN = "LivingSpecimen"
    HUMAN_OBSERVATION = "HumanObservation"
    MACHINE_OBSERVATION = "MachineObservation"
    MATERIAL_SAMPLE = "MaterialSample"
    FOSSIL_SPECIMEN = "FossilSpecimen"

class OccurrenceStatusType(StrEnum):
    PRESENT = "Present"
    ABSENT = "Absent"

# Shared fields
class OccurrenceBase(SQLModel):
    occurrence_code: str = Field(index=True, unique=False, max_length=255)
    sampling_id: int = Field(default=None, index=True, foreign_key="sampling_event.id")
    occurrence_type: OccurrenceType | None = Field(sa_column=Column(Enum(OccurrenceType),
                                                                    default=None, nullable=True, index=False))
    basis_of_record: BasisOfRecordType | None = Field(sa_column=Column(Enum(BasisOfRecordType),
                                                                    default=None, nullable=True, index=False))
    occurrence_status: OccurrenceStatusType | None = Field(sa_column=Column(Enum(OccurrenceStatusType),
                                                                    default=None, nullable=True, index=False))
    institution_code: str | None = Field(default=None, index=False, max_length=255)
    institution_id: str | None = Field(default=None, index=False, max_length=255)
    license: str | None = Field(default=None, index=False, max_length=255)
    rights_holder: str | None = Field(default=None, index=False, max_length=255)
    access_rights: str | None = Field(default=None, index=False, max_length=255)
    recorded_by: str | None = Field(default=None, index=False, max_length=255)
    recorded_by_id: str | None = Field(default=None, index=False, max_length=255)
    species_id: int | None = Field(default=None, index=False, foreign_key="species.id")
    identified_by: str | None = Field(default=None, index=False, max_length=255)
    date_identified: datetime | None = Field(default=None, index=False)
    carlit_id: int | None = Field(default=None, index=False, foreign_key="carlit.id")
    carlit_report: str | None = Field(default=None, index=False, max_length=255)
    occurrence_remarks: str | None  = Field(default=None, index=False)

    # Use __table_args__ to cleanly declare a complex GIN index
    __table_args__ = (
        UniqueConstraint('occurrence_code', 'sampling_id', name='unique_occurrence_code_sampling_event_id', deferrable=True, initially='DEFERRED'),
    )

    @field_validator("occurrence_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class Occurrence(OccurrenceBase, table=True):
    __tablename__ = "occurrence"
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
class OccurrenceCreate(OccurrenceBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class OccurrenceUpdate(SQLModel):
    occurrence_code: str | None = None
    sampling_id: int | None = None
    occurrence_type: OccurrenceType | None = None
    basis_of_record: BasisOfRecordType | None = None
    occurrence_status: OccurrenceStatusType | None = None
    institution_code: str | None = None
    institution_id: str | None = None
    license: str | None = None
    rights_holder: str | None = None
    access_rights: str | None = None
    recorded_by: str | None = None
    recorded_by_id: str | None = None
    species_id: int | None = None
    date_identified: datetime | None = None
    identified_by: str | None = None
    carlit_id: int | None = None
    carlit_report: str | None = None
    occurrence_remarks: str | None = None

