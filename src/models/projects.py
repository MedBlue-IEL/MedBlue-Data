from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel, text
from sqlalchemy import DateTime, func

from commons.util import generate_clean_code


# Shared fields
class ProjectBase(SQLModel):
    project_code: str = Field(index=True, unique=True, max_length=255)
    project_name: str = Field(index=False, unique=True, max_length=255)
    start_date: datetime | None  = Field(default=None, index=False)
    end_date: datetime | None  = Field(default=None, index=False)
    responsible_institution: str | None  = Field(default=None, index=False, max_length=255)
    project_manager: str | None  = Field(default=None, index=False, max_length=255)
    funding_source: str | None  = Field(default=None, index=False, max_length=255)
    rights_holder: str | None  = Field(default=None, index=False, max_length=255)
    project_remarks: str | None  = Field(default=None, index=False)

    @field_validator("project_code", mode="before")
    @classmethod
    def force_uppercase_clean_code(cls, value: str) -> str:
        return generate_clean_code(value)

# Includes database-specific logic and fields
class Project(ProjectBase, table=True):
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
class ProjectCreate(ProjectBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class ProjectUpdate(SQLModel):
    project_id: str | None = None
    project_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    responsible_institution: str | None = None
    project_manager: str | None = None
    funding_source: str | None = None
    rights_holder: str | None = None
    project_remarks: str | None = None

