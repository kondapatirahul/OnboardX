from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.models import OnboardingStatus, TaskStatus


class OnboardingStageInput(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    order_index: int = Field(default=0, ge=0)
    duration_days: int | None = Field(default=None, ge=1, le=3650)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Stage name must contain at least 2 characters")
        return value


class OnboardingTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    stages: list[OnboardingStageInput] = Field(default_factory=list, max_length=50)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Template name must contain at least 2 characters")
        return value


class OnboardingTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class OnboardingStageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str | None = None
    order_index: int
    duration_days: int | None = None


class OnboardingTemplateResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    stages: list[OnboardingStageResponse] = Field(default_factory=list)
    created_at: datetime


class OnboardingTemplateListResponse(BaseModel):
    items: list[OnboardingTemplateResponse]
    total: int


class OnboardingAssignmentCreate(BaseModel):
    employee_id: UUID
    template_id: UUID


class OnboardingTaskResponse(BaseModel):
    id: UUID
    title: str
    status: TaskStatus
    stage_id: UUID | None = None
    due_date: datetime | None = None


class OnboardingInstanceResponse(BaseModel):
    id: UUID
    employee_id: UUID
    template_id: UUID | None = None
    status: OnboardingStatus
    progress_percentage: float
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tasks: list[OnboardingTaskResponse] = Field(default_factory=list)


class OnboardingStatusUpdate(BaseModel):
    status: OnboardingStatus


class OnboardingTaskStatusUpdate(BaseModel):
    status: TaskStatus
