from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class AccessGrantInput(BaseModel):
    user_id: UUID
    permission: str = Field(default="view", pattern="^(view|download|manage)$")
    expires_at: datetime | None = None


class AccessGrantOut(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    permission: str
    is_active: bool
    expires_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ShareInput(BaseModel):
    expires_in_hours: int = Field(default=72, ge=1, le=720)
    max_downloads: int | None = Field(default=None, ge=1, le=1000)


class ShareOut(BaseModel):
    id: UUID
    expires_at: datetime
    max_downloads: int | None
    created_at: datetime

    class Config:
        from_attributes = True
