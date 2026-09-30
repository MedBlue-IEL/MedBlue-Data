from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: str = Field(index=True, max_length=255)
    project_name: str = Field(index=True, max_length=255)
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
