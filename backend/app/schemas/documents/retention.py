from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class RetentionPolicyInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    retention_days: int = Field(ge=1, le=36500)
    action: str = Field(default="review", pattern="^(archive|delete|review)$")
    is_active: bool = True


class RetentionPolicyOut(BaseModel):
    id: UUID
    name: str
    category: str | None
    retention_days: int
    action: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RetentionPolicyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    retention_days: int | None = Field(default=None, ge=1, le=36500)
    action: str | None = Field(default=None, pattern="^(archive|delete|review)$")
    is_active: bool | None = None
