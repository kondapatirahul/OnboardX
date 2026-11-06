from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class CommentInput(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    is_internal: bool = False
    parent_id: UUID | None = None

    @field_validator("body")
    @classmethod
    def clean_body(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Comment cannot be blank")
        return value


class CommentOut(BaseModel):
    id: UUID
    document_id: UUID
    author_id: UUID | None
    body: str
    is_internal: bool
    parent_id: UUID | None
    edited_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
