from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

# Shared fields
class CarlitBase(SQLModel):
    carlit_name: str = Field(index=True, unique=True, max_length=255)
    remarks: str | None = Field(index=False, unique=False, max_length=255)
    sensitivity_level: int | None = Field(index=False, unique=False)

# Includes database-specific logic and fields
class Carlit(CarlitBase, table=True):
    __tablename__ = "carlit"
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
class CarlitCreate(CarlitBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class CarlitUpdate(SQLModel):
    carlit_name: str | None = None
    remarks: str | None = None
    sensitivity_level: int | None = None
