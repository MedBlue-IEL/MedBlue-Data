import uuid
from enum import StrEnum
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import DateTime, func, Column, Enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

from commons.util import generate_clean_code

class AssetType(StrEnum):
    STILL_IMAGE = "StillImage"
    MOVING_IMAGE = "MovingImage"
    AUDIO = "Audio"
    DOCUMENT = "Document"
    SPREADSHEET = "Spreadsheet"
    GIS_DATASET = "GISDataset"
    RASTER = "Raster"
    ORTHOMOSAIC = "Orthomosaic"
    POINT_CLOUD = "PointCloud"
    SONOGRAM = "Sonogram"
    MESH_3D = "Mesh3D"
    SCRIPT = "Script"
    PUBLICATION = "Publication"
    WEB_RESOURCE = "WebResource"
    OTHER = "Other"

class AssetFormat(StrEnum):
    IMAGE_JPG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    APPLICATION_PDF = "application/pdf"
    DOCUMENT_DOC = "document/doc"
    TABLE_XLS = "table/xls"
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"

# Shared fields
class AssetBase(SQLModel):
    file_name: str = Field(index=False, unique=True, max_length=255)
    asset_type: AssetType = Field(
        sa_column=Column(
            Enum(AssetType),
            default=None,
            nullable=True,
            index=False
        )
    )
    asset_format: AssetFormat = Field(
        sa_column=Column(
            Enum(AssetFormat),
            default=None,
            nullable=True,
            index=False
        )
    )
    project_id: int | None = Field(default=None, index=True, foreign_key="project.id")
    campaign_id: int | None = Field(default=None, index=True, foreign_key="campaign_event.id")
    sampling_event_id: int | None = Field(default=None, index=True, foreign_key="sampling_event.id")
    occurrence_id: int | None = Field(default=None, index=True, foreign_key="occurrence.id")
    measurement_id: int | None = Field(default=None, index=True, foreign_key="measurement.id")
    identifier: str | None = Field(index=False, unique=False, max_length=255)
    asset_remarks: str | None = Field(index=False, unique=False, max_length=255)

# Includes database-specific logic and fields
class Asset(AssetBase, table=True):
    __tablename__ = "asset"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
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
class AssetCreate(AssetBase):
    pass

# For incoming PATCH/PUT payloads (All fields optional, No ID)
class AssetUpdate(SQLModel):
    file_name: str | None = None
    asset_type: AssetType | None = None
    asset_format: AssetFormat | None = None
    project_id: int | None = None
    campaign_id: int | None = None
    sampling_event_id: int | None = None
    occurrence_id: int | None = None
    measurement_id: int | None = None
    identifier: str | None = None
    asset_remarks: str | None = None
