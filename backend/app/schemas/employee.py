from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.models import EmployeeStatus, UserRole


class EmployeeCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    temporary_password: str = Field(min_length=8, max_length=128)
    department_id: Optional[UUID] = None
    designation: Optional[str] = Field(default=None, max_length=255)
    joining_date: Optional[datetime] = None
    manager_id: Optional[UUID] = None
    status: EmployeeStatus = EmployeeStatus.ONBOARDING

    @field_validator("employee_id", "full_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    department_id: Optional[UUID] = None
    designation: Optional[str] = Field(default=None, max_length=255)
    joining_date: Optional[datetime] = None
    manager_id: Optional[UUID] = None
    status: Optional[EmployeeStatus] = None

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Full name cannot be blank")
        return value


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    user_id: str
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    organization_id: str
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[datetime] = None
    manager_id: Optional[UUID] = None
    status: EmployeeStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)
