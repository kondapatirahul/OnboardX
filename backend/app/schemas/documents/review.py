from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.documents.enums import ReviewDecision


class ReviewInput(BaseModel):
    decision: ReviewDecision
    comments: str | None = Field(default=None, max_length=4000)

    @field_validator("comments")
    @classmethod
    def normalize_comments(cls, value):
        if value is None:
            return None
        value = value.strip()
        return value or None


class ReviewOut(BaseModel):
    id: UUID
    document_id: UUID
    reviewed_by: UUID | None
    status: str
    comments: str | None
    decision: str | None
    previous_status: str | None
    reviewed_at: datetime

    class Config:
        from_attributes = True


class ReviewQueueItem(BaseModel):
    document: dict
    employee_name: str
    submitted_at: datetime
    latest_comment: str | None = None
