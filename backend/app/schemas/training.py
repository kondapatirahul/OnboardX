from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class TrainingLessonInput(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1200)
    content: str | None = Field(default=None, max_length=30000)
    resource_url: str | None = Field(default=None, max_length=1000)
    duration_minutes: int = Field(default=10, ge=1, le=600)
    order_index: int = Field(default=0, ge=0)
    is_preview: bool = False

    @field_validator("title")
    @classmethod
    def clean_title(cls, value):
        return " ".join(value.split())


class TrainingCourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    category: str = Field(default="General", min_length=2, max_length=80)
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    duration_minutes: int = Field(default=30, ge=1, le=10000)
    content_url: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=1000)
    is_mandatory: bool = False
    published: bool = False
    lessons: list[TrainingLessonInput] = Field(default_factory=list, max_length=100)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value):
        return " ".join(value.split())


class TrainingCourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    level: str | None = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    duration_minutes: int | None = Field(default=None, ge=1, le=10000)
    content_url: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=1000)
    is_mandatory: bool | None = None
    published: bool | None = None


class TrainingAssignmentCreate(BaseModel):
    employee_ids: list[UUID] = Field(min_length=1, max_length=500)
    due_date: datetime | None = None


class TrainingLessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None = None
    content: str | None = None
    resource_url: str | None = None
    duration_minutes: int
    order_index: int
    is_preview: bool


class TrainingCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None = None
    category: str | None = None
    level: str
    duration_minutes: int | None = None
    content_url: str | None = None
    thumbnail_url: str | None = None
    is_mandatory: bool
    published: bool
    lessons: list[TrainingLessonResponse] = Field(default_factory=list)
    created_at: datetime


class TrainingProgressUpdate(BaseModel):
    completed: bool = True


class TrainingAssignmentResponse(BaseModel):
    id: UUID
    course_id: UUID
    course_title: str
    employee_id: UUID
    employee_name: str
    status: str
    progress_percentage: float
    due_date: datetime | None = None
    completed_at: datetime | None = None
    certificate_code: str | None = None
    lessons_completed: int = 0
    lessons_total: int = 0


class TrainingCertificateResponse(BaseModel):
    id: UUID
    course_title: str
    certificate_code: str
    issued_at: datetime
