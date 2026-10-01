from datetime import datetime
from sqlmodel import Field, SQLModel, text
from sqlalchemy import func

# Shared fields
class ProjectBase(SQLModel):
    project_id: str = Field(index=True, max_length=255)
    project_name: str = Field(index=False, max_length=255)
    start_date: datetime = Field(index=False)
    end_date: datetime = Field(index=False)
    responsible_institution: str = Field(index=False, max_length=255)
    project_manager: str = Field(index=False, max_length=255)
    funding_source: str = Field(index=False, max_length=255)
    rights_holder: str = Field(index=False, max_length=255)
    project_remarks: str = Field(index=False)

# Includes database-specific logic and fields
class Project(ProjectBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created: datetime = Field(
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )
    modified: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now() # SQLAlchemy hook to update on edits
        }
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

