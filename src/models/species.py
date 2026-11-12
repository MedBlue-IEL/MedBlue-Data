from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

# Shared fields
class SpeciesBase(SQLModel):
    scientific_name: str = Field(index=True, unique=True, max_length=255)
    scientific_name_id: str = Field(index=False, unique=True, max_length=255)
    taxon_id: str | None = Field(index=False, unique=True, max_length=255)
    scientific_name_authorship: str | None = Field(index=False, unique=False, max_length=255)
    kingdom: str | None = Field(index=False, unique=False, max_length=255)
    phylum: str | None = Field(index=False, unique=False, max_length=255)
    species_class: str | None = Field(index=False, unique=False, max_length=255)
    order: str | None = Field(index=False, unique=False, max_length=255)
    family: str | None = Field(index=False, unique=False, max_length=255)
    genus: str | None = Field(index=False, unique=False, max_length=255)
    specific_epithet: str | None = Field(index=False, unique=False, max_length=255)
    infraspecific_epithet: str | None = Field(index=False, unique=False, max_length=255)
    taxon_rank: str | None = Field(index=False, unique=False, max_length=255)
    taxon_remarks: str | None = Field(index=False, unique=False, max_length=255)


# Includes database-specific logic and fields
class Species(SpeciesBase, table=True):
    __tablename__ = "species"
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
class SpeciesCreate(SpeciesBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class SpeciesUpdate(SQLModel):
    scientific_name: str | None = None
    scientific_name_id: str | None = None
    taxon_id: str | None = None
    scientific_name_authorship: str | None = None
    kingdom: str | None = None
    phylum: str | None = None
    species_class: str | None = None
    order: str | None = None
    family: str | None = None
    genus: str | None = None
    specific_epithet: str | None = None
    infraspecific_epithet: str | None = None
    taxon_rank: str | None = None
    taxon_remarks: str | None = None