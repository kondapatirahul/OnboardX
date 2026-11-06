from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, model_validator


class KeyResultInput(BaseModel):
    title: str = Field(min_length=2, max_length=240)
    metric: str | None = Field(default=None, max_length=80)
    start_value: float = 0
    target_value: float = 100
    current_value: float = 0
    weight: float = Field(default=1, gt=0, le=100)
    order_index: int = 0

    @model_validator(mode="after")
    def validate_target(self):
        if self.target_value == self.start_value:
            raise ValueError("Target and start values must be different")
        return self


class GoalCreate(BaseModel):
    owner_id: UUID
    title: str = Field(min_length=3, max_length=240)
    description: str | None = None
    goal_type: str = "individual"
    priority: str = "medium"
    start_date: datetime | None = None
    due_date: datetime | None = None
    key_results: list[KeyResultInput] = Field(default_factory=list, max_length=20)


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=240)
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    due_date: datetime | None = None


class KeyResultUpdate(BaseModel):
    current_value: float


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    title: str
    description: str | None
    goal_type: str
    status: str
    priority: str
    progress: int
    start_date: datetime | None
    due_date: datetime | None
    created_at: datetime


class CycleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    description: str | None = None
    cycle_type: str = "quarterly"
    starts_at: datetime
    ends_at: datetime
    self_review_deadline: datetime | None = None
    manager_review_deadline: datetime | None = None

    @model_validator(mode="after")
    def valid_window(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("Review cycle end must be after start")
        return self


class ReviewCreate(BaseModel):
    employee_id: UUID


class SelfReviewInput(BaseModel):
    self_rating: float = Field(ge=1, le=5)
    self_summary: str = Field(min_length=10, max_length=6000)


class ManagerReviewInput(BaseModel):
    manager_rating: float = Field(ge=1, le=5)
    manager_summary: str = Field(min_length=10, max_length=6000)
    strengths: str | None = Field(default=None, max_length=3000)
    growth_areas: str | None = Field(default=None, max_length=3000)


class FeedbackCreate(BaseModel):
    feedback_type: str = "peer"
    rating: float | None = Field(default=None, ge=1, le=5)
    strengths: str | None = Field(default=None, max_length=3000)
    suggestions: str | None = Field(default=None, max_length=3000)
    is_anonymous: bool = False


class ImprovementPlanCreate(BaseModel):
    employee_id: UUID
    review_id: UUID | None = None
    title: str = Field(min_length=3, max_length=200)
    objectives: str = Field(min_length=10)
    support_plan: str | None = None
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def valid_window(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("Plan end must be after start")
        return self
