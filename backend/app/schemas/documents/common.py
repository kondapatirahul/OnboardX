from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.documents.constants import MAX_DESCRIPTION_LENGTH, MAX_TITLE_LENGTH, MAX_TAG_LENGTH
from app.documents.enums import DocumentVisibility


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    employee_id: UUID
    organization_id: UUID
    document_type: str
    file_name: str
    file_size: int | None = None
    mime_type: str | None = None
    status: str
    title: str | None = None
    description: str | None = None
    category: str | None = None
    lifecycle: str
    visibility: str
    checksum_sha256: str | None = None
    scan_status: str
    current_version: int
    expires_at: datetime | None = None
    uploaded_at: datetime
    updated_at: datetime


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)
    category: str | None = Field(default=None, max_length=80)
    visibility: DocumentVisibility | None = None
    expires_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Title cannot be blank")
        return value.strip() if value else value


class TagInput(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_TAG_LENGTH)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Tag cannot be blank")
        return value


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    created_at: datetime


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor_id: UUID | None
    event_type: str
    summary: str
    created_at: datetime


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    version_number: int
    file_name: str
    file_size: int
    mime_type: str
    checksum_sha256: str
    change_note: str | None
    uploaded_by: UUID | None
    created_at: datetime


class PageInfo(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class DocumentPage(BaseModel):
    items: list[DocumentOut]
    pagination: PageInfo
