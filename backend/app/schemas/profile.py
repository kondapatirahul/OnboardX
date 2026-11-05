from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.models import EmployeeStatus, UserRole


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Email, role, department, manager and employment status remain HR-controlled.
    full_name: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Full name cannot be blank")
        return cleaned


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    user_id: UUID
    full_name: str
    email: str
    role: UserRole
    designation: str | None = None
    department_id: UUID | None = None
    department_name: str | None = None
    manager_id: UUID | None = None
    manager_name: str | None = None
    joining_date: datetime | None = None
    status: EmployeeStatus
    account_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
