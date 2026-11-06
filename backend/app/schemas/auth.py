from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.models import UserRole


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.EMPLOYEE
    organization_name: Optional[str] = Field(default=None, max_length=255)
    organization_code: Optional[str] = Field(default=None, max_length=120)

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Full name must contain at least 2 characters")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("organization_name", "organization_code")
    @classmethod
    def clean_organization_fields(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value else None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    organization_id: Optional[str] = None

    class Config:
        from_attributes = True


LoginResponse.model_rebuild()
